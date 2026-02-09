#!/usr/bin/env python3
"""
Add research metadata to skill file frontmatter.

Scans all skill .md files and adds a metadata block with:
- research-domain
- task-type
- research-phase
- verification-level

Values are inferred from file location and description. Run with --dry-run
to preview changes without writing.
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: pyyaml required. Install with: pip install pyyaml")
    sys.exit(1)

REPO_ROOT = Path(__file__).parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"

# Inference rules: maps keywords in name/description to metadata values

DOMAIN_RULES = {
    "general": [],  # default
}

TASK_TYPE_RULES = {
    "writing": [
        "write", "introduction", "abstract", "discussion",
        "literature", "rebuttal", "title",
    ],
    "verification": [
        "verify", "check", "validate", "audit", "fact-check", "proof",
    ],
    "analysis": [
        "analyz", "synthesiz", "evidence", "claim", "perspective",
        "devil", "counterexample", "intuition", "connect", "bounds",
    ],
    "formatting": [
        "format", "latex", "tikz", "figure",
        "publication-figure", "consistency",
    ],
    "automation": [
        "commit", "pr-", "cicd", "ci/cd", "htcondor",
        "scaffold", "sync", "annotate",
    ],
    "dissemination": ["slide", "poster", "twitter", "presentation"],
    "review": ["review", "audience", "clarity", "readability"],
}

PHASE_RULES = {
    "literature-review": [
        "literature", "synthesiz", "related work", "benchmark-scout",
    ],
    "experiment-design": [
        "experiment-tracker", "experiment design", "benchmark-scout",
    ],
    "implementation": [
        "code", "commit", "pr-", "cicd", "htcondor", "simplify",
        "python-docs", "sync-setup", "sync-annotate", "sync-verify",
    ],
    "paper-writing": [
        "paper-", "abstract", "introduction", "discussion",
        "experiment", "references", "verify-experiment",
        "title", "latex", "tikz", "figure", "openreview",
    ],
    "submission": ["openreview", "submission", "artifact", "packag"],
    "rebuttal": ["rebuttal", "reviewer-response", "response"],
    "dissemination": ["slide", "poster", "twitter", "presentation"],
}

VERIFICATION_RULES = {
    "formal": [
        "verify citation", "fact-check", "bibtexupdater", "doi",
        "verify-experiment", "statistical-validator", "sync-verify",
    ],
    "heuristic": [
        "check", "lint", "consistency", "notation", "format",
    ],
    "layered": [
        "evidence", "claim", "audit", "proof", "review", "analyz",
    ],
    "none": [],  # default
}


def infer_metadata(
    name: str, description: str, plugin: str, skill_type: str,
) -> dict:
    """Infer metadata values from name, description, and location."""
    text = f"{name} {description}".lower()

    # Research domain — almost all are general for now
    domain = "general"

    # Task type
    task_type = "writing"  # default for academic
    if plugin == "development":
        task_type = "automation"
    elif plugin == "formatting":
        task_type = "formatting"
    elif plugin == "office":
        task_type = "automation"
    elif plugin == "research-agents":
        task_type = "analysis"  # default for agents

    for ttype, keywords in TASK_TYPE_RULES.items():
        if any(kw in text for kw in keywords):
            task_type = ttype
            break

    # Research phase
    phase = "paper-writing"  # default
    if plugin == "development":
        phase = "implementation"
    elif plugin == "office":
        phase = "dissemination"

    for ph, keywords in PHASE_RULES.items():
        if any(kw in text for kw in keywords):
            phase = ph
            break

    # Verification level
    vlevel = "none"  # default
    for level, keywords in VERIFICATION_RULES.items():
        if any(kw in text for kw in keywords):
            vlevel = level
            break

    return {
        "research-domain": domain,
        "task-type": task_type,
        "research-phase": phase,
        "verification-level": vlevel,
    }


def collect_skill_files() -> list[Path]:
    """Collect all skill .md files."""
    files = []

    for plugin_dir in sorted(PLUGINS_DIR.iterdir()):
        if not plugin_dir.is_dir() or plugin_dir.name.startswith("."):
            continue
        if plugin_dir.name == "research-agents":
            continue
        commands_dir = plugin_dir / "commands"
        if commands_dir.exists():
            for f in sorted(commands_dir.iterdir()):
                if f.suffix == ".md" and not f.name.startswith((".", "_")):
                    files.append(f)
        for sub_dir in sorted(plugin_dir.iterdir()):
            if sub_dir.is_dir() and not sub_dir.name.startswith("."):
                sub_commands = sub_dir / "commands"
                if sub_commands.exists():
                    for f in sorted(sub_commands.iterdir()):
                        if f.suffix == ".md" and not f.name.startswith((".", "_")):
                            files.append(f)

    ra_dir = PLUGINS_DIR / "research-agents"
    for subdir_name in ["agents", "micro-skills", "orchestrators", "helpers"]:
        subdir = ra_dir / subdir_name
        if subdir.exists():
            for f in sorted(subdir.iterdir()):
                if f.suffix == ".md" and not f.name.startswith((".", "_")):
                    files.append(f)

    return files


def add_metadata_to_file(
    file_path: Path, dry_run: bool = False,
) -> tuple[bool, str]:
    """Add metadata block to a skill file's frontmatter.

    Returns (changed, message).
    """
    content = file_path.read_text()

    # Parse frontmatter
    match = re.match(r"^(---\s*\n)(.*?)(\n---\s*\n)", content, re.DOTALL)
    if not match:
        return False, "no frontmatter found"

    prefix = match.group(1)
    fm_text = match.group(2)
    suffix = match.group(3)
    body = content[match.end():]

    try:
        frontmatter = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError:
        return False, "invalid YAML frontmatter"

    # Check if metadata already exists
    if "metadata" in frontmatter and frontmatter["metadata"]:
        return False, "metadata already exists"

    # Determine plugin from path
    rel = file_path.relative_to(PLUGINS_DIR)
    plugin = rel.parts[0]

    # Determine skill type
    parts = rel.parts
    if "agents" in parts:
        skill_type = "agent"
    elif "micro-skills" in parts:
        skill_type = "micro-skill"
    elif "orchestrators" in parts:
        skill_type = "orchestrator"
    elif "helpers" in parts:
        skill_type = "helper"
    else:
        skill_type = "command"

    name = frontmatter.get("name", file_path.stem)
    description = frontmatter.get("description", "")
    if isinstance(description, str):
        description = description.strip()

    metadata = infer_metadata(name, description, plugin, skill_type)

    # Add metadata to frontmatter YAML text
    metadata_yaml = yaml.dump(
        {"metadata": metadata}, default_flow_style=False,
    ).strip()
    new_fm_text = fm_text.rstrip() + "\n" + metadata_yaml

    new_content = prefix + new_fm_text + suffix + body

    if not dry_run:
        file_path.write_text(new_content)

    domain = metadata["research-domain"]
    task = metadata["task-type"]
    phase = metadata["research-phase"]
    verify = metadata["verification-level"]
    return (
        True,
        f"added metadata: domain={domain}, type={task}, "
        f"phase={phase}, verify={verify}",
    )


def main():
    parser = argparse.ArgumentParser(
        description="Add research metadata to skill files",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview changes without writing",
    )
    parser.add_argument(
        "--file", type=str,
        help="Process a single file instead of all",
    )
    args = parser.parse_args()

    if args.file:
        files = [Path(args.file)]
    else:
        files = collect_skill_files()

    dry_label = "(dry run)" if args.dry_run else ""
    print(f"Processing {len(files)} skill files {dry_label}...")
    print()

    changed = 0
    skipped = 0
    errors = 0

    for f in files:
        rel = f.relative_to(REPO_ROOT)
        try:
            was_changed, msg = add_metadata_to_file(
                f, dry_run=args.dry_run,
            )
            if was_changed:
                print(f"  + {rel}: {msg}")
                changed += 1
            else:
                print(f"  - {rel}: {msg}")
                skipped += 1
        except Exception as e:
            print(f"  ! {rel}: error - {e}")
            errors += 1

    print()
    print(f"Done: {changed} changed, {skipped} skipped, {errors} errors")
    if args.dry_run:
        print("(dry run — no files were modified)")


if __name__ == "__main__":
    main()
