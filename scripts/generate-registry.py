#!/usr/bin/env python3
"""
Generate registry/index.json from skill files.

Scans all plugins/*/commands/*.md and plugins/research-agents/{agents,micro-skills,orchestrators,helpers}/*.md,
extracts YAML frontmatter, and generates a machine-readable registry index.
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: pyyaml required. Install with: pip install pyyaml")
    sys.exit(1)

REPO_ROOT = Path(__file__).parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"
REGISTRY_DIR = REPO_ROOT / "registry"
# The feedback client ships inside the development plugin, where the registry
# is out of reach in the plugin-cache layout; it filters capture against this
# copy of the names instead (RFC-0001 §6).
SKILL_NAMES_PATH = PLUGINS_DIR / "toolkit" / "scripts" / "skill-names.json"
# Capture attributes an invocation to the Agora by its plugin prefix, so the
# client needs the plugin names in that layout too.
MARKETPLACE_PATH = REPO_ROOT / ".claude-plugin" / "marketplace.json"
PLUGIN_NAMES_PATH = PLUGINS_DIR / "toolkit" / "scripts" / "plugin-names.json"


def parse_yaml_frontmatter(file_path: Path) -> dict:
    """Parse YAML frontmatter from a markdown file."""
    content = file_path.read_text()
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}


def determine_skill_type(file_path: Path) -> str:
    """Determine the skill type based on file location."""
    parts = file_path.relative_to(PLUGINS_DIR).parts
    if "agents" in parts:
        return "agent"
    elif "micro-skills" in parts:
        return "micro-skill"
    elif "orchestrators" in parts:
        return "orchestrator"
    elif "helpers" in parts:
        return "helper"
    else:
        return "command"


def determine_plugin(file_path: Path) -> str:
    """Determine the plugin name based on file location."""
    parts = file_path.relative_to(PLUGINS_DIR).parts
    return parts[0]  # First directory under plugins/


def collect_skill_files() -> list[Path]:
    """Collect every skill file from every plugin.

    Skill type comes from the containing directory, so each plugin may hold any
    of commands/, agents/, micro-skills/ and orchestrators/. This used to
    special-case a single `research-agents` plugin as the only home for agents;
    RFC-0002 split the catalog by research phase instead, so verification agents
    live in `verify` and figure tooling in `toolkit`, and the collector cannot
    assume where a type lives.
    """
    files = []
    subdirs = ["commands", "agents", "micro-skills", "orchestrators", "helpers"]

    for plugin_dir in sorted(PLUGINS_DIR.iterdir()):
        if not plugin_dir.is_dir() or plugin_dir.name.startswith("."):
            continue
        for subdir_name in subdirs:
            subdir = plugin_dir / subdir_name
            if not subdir.exists():
                continue
            for f in sorted(subdir.iterdir()):
                if f.suffix == ".md" and not f.name.startswith((".", "_")):
                    files.append(f)

    return files


# Tools a skill actually invokes, counted only at invocation sites: inside a
# bash/python fence, an mcp__ call, or a named scripts/*.py delegate. A tool
# mentioned in prose, in a routing table, or inside a config snippet the skill
# merely recommends is not an invocation — navigator names matplotlib in a
# routing row without running it.
TOOL_PATTERNS = [
    (r"bibtex-check|bibtexupdater|bibtex-updater", "bibtexupdater"),
    (r"limpid_bridge\.py|\blimpid\b", "limpid"),
    (r"latexmk|build_latex\.py", "latexmk"),
    (r"latex-code-sync", "latex-code-sync"),
    (r"\bvulture\b", "vulture"),
    (r"\bradon\b", "radon"),
    (r"\bpylint\b", "pylint"),
    (r"\bflake8\b", "flake8"),
    (r"condor_\w+", "HTCondor"),
    (r"writing_verify\.py", "writing_verify.py"),
    (r"parse_latex\.py", "parse_latex.py"),
    (r"onboard\.py", "onboard.py"),
    (r"agora_feedback\.py", "agora_feedback.py"),
    (r"cache_manager\.py", "cache_manager.py"),
    (r"matplotlib|seaborn", "matplotlib"),
]

_FENCE_RE = re.compile(r"```(?:bash|sh|shell|console|python)\n(.*?)```", re.S)
_MCP_RE = re.compile(r"mcp__(\w+)__\w+")


# Claude Code reads and globs natively, so a skill naming an mcp__filesystem__
# tool is carrying a stale reference, not reaching a server. Never report it.
_MCP_IGNORE = {"filesystem"}

# A skill may delegate to a repo script outside a fence, as onboard.md does:
# "Run `python3 scripts/onboard.py --detect ...` via Bash". That is an
# invocation even though no fence surrounds it.
_DELEGATE_RE = re.compile(r"(?:python3?\s+|\$\{CLAUDE_PLUGIN_ROOT\}/)[\w/]*?(\w+\.py)")


def detect_tools(text: str) -> list:
    """Return the tools a skill invokes, from invocation sites only."""
    sites = "\n".join(_FENCE_RE.findall(text))
    found = {name for pat, name in TOOL_PATTERNS if re.search(pat, sites)}
    for script in _DELEGATE_RE.findall(text):
        for pat, name in TOOL_PATTERNS:
            if re.fullmatch(pat.replace("\\.", "."), script) or name == script:
                found.add(name)
    for server in _MCP_RE.findall(text):
        if server not in _MCP_IGNORE:
            found.add(f"{server} MCP")
    return sorted(found)


def build_skill_entry(file_path: Path) -> dict | None:
    """Build a registry entry from a skill file."""
    frontmatter = parse_yaml_frontmatter(file_path)
    if not frontmatter:
        print(f"  Warning: No frontmatter in {file_path.relative_to(REPO_ROOT)}")
        return None

    name = frontmatter.get("name", file_path.stem)
    description = frontmatter.get("description", "")
    if isinstance(description, str):
        description = description.strip()

    metadata = frontmatter.get("metadata", {})

    entry = {
        "name": name,
        "plugin": determine_plugin(file_path),
        "type": determine_skill_type(file_path),
        "description": description,
        "model": frontmatter.get("model", "sonnet"),
        "path": str(file_path.relative_to(REPO_ROOT)),
        "research-domain": metadata.get("research-domain", "general"),
        "task-type": metadata.get("task-type", ""),
        "research-phase": metadata.get("research-phase", ""),
        "verification-level": metadata.get("verification-level", "none"),
        "visibility": metadata.get("visibility", "public"),
    }

    tools = detect_tools(file_path.read_text())
    if tools:
        entry["tools"] = tools

    # Deprecation is optional and only appears on skills that carry it, so that
    # a live skill's entry is byte-identical to what it was before the field
    # existed. superseded_by names what to reach for instead; a deprecated
    # skill without one leaves the user nowhere to go.
    if metadata.get("deprecated"):
        entry["deprecated"] = True
        entry["superseded-by"] = metadata.get("superseded-by", "")
        entry["deprecated-in"] = metadata.get("deprecated-in", "")

    return entry


def validate_against_categories(skills: list[dict]) -> list[str]:
    """Validate skill metadata against categories.json."""
    categories_path = REGISTRY_DIR / "categories.json"
    if not categories_path.exists():
        return ["categories.json not found"]

    with open(categories_path) as f:
        categories = json.load(f)

    warnings = []
    for skill in skills:
        domain = skill.get("research-domain", "")
        if domain and domain not in categories["research-domains"]:
            warnings.append(f"{skill['name']}: invalid research-domain '{domain}'")

        task_type = skill.get("task-type", "")
        if task_type and task_type not in categories["task-types"]:
            warnings.append(f"{skill['name']}: invalid task-type '{task_type}'")

        phase = skill.get("research-phase", "")
        if phase and phase not in categories["research-phases"]:
            warnings.append(f"{skill['name']}: invalid research-phase '{phase}'")

        level = skill.get("verification-level", "")
        if level and level not in categories["verification-levels"]:
            warnings.append(f"{skill['name']}: invalid verification-level '{level}'")

    return warnings


def main():
    print("Generating registry/index.json...")

    files = collect_skill_files()
    print(f"Found {len(files)} skill files")

    skills = []
    for f in files:
        entry = build_skill_entry(f)
        if entry:
            skills.append(entry)

    print(f"Generated {len(skills)} registry entries")

    # Validate
    warnings = validate_against_categories(skills)
    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")

    # Build index
    index = {
        "version": "1.0.0",
        "generated": date.today().isoformat(),
        "stats": {
            "total_skills": len(skills),
            "public_skills": sum(
                1 for s in skills if s.get("visibility", "public") == "public"
            ),
            "deprecated_skills": sum(1 for s in skills if s.get("deprecated")),
            # What the marketplace advertises: public and not deprecated. The
            # badge and every "<N> skills" claim in the docs use this, since a
            # deprecated skill is not something to recommend to a new user.
            "active_public_skills": sum(
                1
                for s in skills
                if s.get("visibility", "public") == "public" and not s.get("deprecated")
            ),
            "commands": sum(1 for s in skills if s["type"] == "command"),
            "agents": sum(1 for s in skills if s["type"] == "agent"),
            "micro_skills": sum(1 for s in skills if s["type"] == "micro-skill"),
            "orchestrators": sum(1 for s in skills if s["type"] == "orchestrator"),
            "helpers": sum(1 for s in skills if s["type"] == "helper"),
            "plugins": len(set(s["plugin"] for s in skills)),
        },
        "repos": [
            {
                "repo": "rpatrik96/research-agora",
                "description": "Research Agora - ML research skills marketplace",
                "homepage": "https://rpatrik96.github.io/research-agora",
                "skills": skills,
            }
        ],
    }

    # Write
    REGISTRY_DIR.mkdir(exist_ok=True)
    output_path = REGISTRY_DIR / "index.json"
    with open(output_path, "w") as f:
        json.dump(index, f, indent=2)
        # Match end-of-file-fixer, or the hook rewrites this file after every run.
        f.write("\n")
    print(f"\nWrote {output_path.relative_to(REPO_ROOT)}")

    names = {
        "generated": index["generated"],
        "names": sorted({s["name"] for s in skills}),
    }
    with open(SKILL_NAMES_PATH, "w") as f:
        json.dump(names, f, indent=2)
        f.write("\n")
    print(f"Wrote {SKILL_NAMES_PATH.relative_to(REPO_ROOT)}")

    with open(MARKETPLACE_PATH) as f:
        marketplace = json.load(f)
    plugin_names = {
        "generated": index["generated"],
        "names": sorted(p["name"] for p in marketplace.get("plugins", [])),
    }
    with open(PLUGIN_NAMES_PATH, "w") as f:
        json.dump(plugin_names, f, indent=2)
        f.write("\n")
    print(f"Wrote {PLUGIN_NAMES_PATH.relative_to(REPO_ROOT)}")

    # Summary
    print("\nRegistry summary:")
    print(f"  Commands:      {index['stats']['commands']}")
    print(f"  Agents:        {index['stats']['agents']}")
    print(f"  Micro-skills:  {index['stats']['micro_skills']}")
    print(f"  Orchestrators: {index['stats']['orchestrators']}")
    print(f"  Helpers:       {index['stats']['helpers']}")
    print(f"  Total:         {index['stats']['total_skills']}")


if __name__ == "__main__":
    main()
