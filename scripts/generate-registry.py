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
    """Collect all skill/agent .md files from the plugins directory."""
    files = []

    # Command files from plugins/*/commands/*.md
    for plugin_dir in sorted(PLUGINS_DIR.iterdir()):
        if not plugin_dir.is_dir() or plugin_dir.name.startswith("."):
            continue
        if plugin_dir.name == "research-agents":
            continue  # Handle separately
        commands_dir = plugin_dir / "commands"
        if commands_dir.exists():
            for f in sorted(commands_dir.iterdir()):
                if f.suffix == ".md" and not f.name.startswith((".", "_")):
                    files.append(f)
        # Also check sub-plugins like latex-code-sync
        for sub_dir in sorted(plugin_dir.iterdir()):
            if sub_dir.is_dir() and not sub_dir.name.startswith("."):
                sub_commands = sub_dir / "commands"
                if sub_commands.exists():
                    for f in sorted(sub_commands.iterdir()):
                        if f.suffix == ".md" and not f.name.startswith((".", "_")):
                            files.append(f)

    # Research agents: agents, micro-skills, orchestrators, helpers
    ra_dir = PLUGINS_DIR / "research-agents"
    for subdir_name in ["agents", "micro-skills", "orchestrators", "helpers"]:
        subdir = ra_dir / subdir_name
        if subdir.exists():
            for f in sorted(subdir.iterdir()):
                if f.suffix == ".md" and not f.name.startswith((".", "_")):
                    files.append(f)

    return files


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
    }

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
                "homepage": "https://research-agora.github.io",
                "skills": skills,
            }
        ],
    }

    # Write
    REGISTRY_DIR.mkdir(exist_ok=True)
    output_path = REGISTRY_DIR / "index.json"
    with open(output_path, "w") as f:
        json.dump(index, f, indent=2)
    print(f"\nWrote {output_path.relative_to(REPO_ROOT)}")

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
