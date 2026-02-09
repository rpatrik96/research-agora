#!/usr/bin/env python3
"""
Convert Research Agora skills to other AI agent formats.

Supports:
- cursor: Generates .cursor/rules/{skill-name}.md
- gemini: Generates .gemini/agents/{skill-name}.md
- copilot: Appends to .github/copilot-instructions.md
- agentskills: Generates SKILL.md in AgentSkills.io format

Usage:
    python scripts/convert-skill.py --format cursor --skill paper-references
    python scripts/convert-skill.py --format gemini --all --output /path/to/project
    python scripts/convert-skill.py --format agentskills --plugin academic
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


def parse_yaml_frontmatter(file_path: Path) -> tuple[dict, str]:
    """Parse YAML frontmatter and body from a markdown file."""
    content = file_path.read_text()
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
    if not match:
        return {}, content
    try:
        fm = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        fm = {}
    return fm, match.group(2)


def find_skill_file(skill_name: str) -> Path | None:
    """Find a skill file by name across all plugins."""
    for plugin_dir in PLUGINS_DIR.iterdir():
        if not plugin_dir.is_dir() or plugin_dir.name.startswith("."):
            continue
        # Check commands/
        commands_dir = plugin_dir / "commands"
        if commands_dir.exists():
            candidate = commands_dir / f"{skill_name}.md"
            if candidate.exists():
                return candidate
        # Check sub-plugins
        for sub_dir in plugin_dir.iterdir():
            if sub_dir.is_dir() and not sub_dir.name.startswith("."):
                sub_commands = sub_dir / "commands"
                if sub_commands.exists():
                    candidate = sub_commands / f"{skill_name}.md"
                    if candidate.exists():
                        return candidate
        # Check agents/
        if plugin_dir.name == "research-agents":
            for subdir in ["agents", "micro-skills", "orchestrators", "helpers"]:
                candidate = plugin_dir / subdir / f"{skill_name}.md"
                if candidate.exists():
                    return candidate
    return None


def collect_all_skills() -> list[Path]:
    """Collect all skill files."""
    files = []
    for plugin_dir in sorted(PLUGINS_DIR.iterdir()):
        if not plugin_dir.is_dir() or plugin_dir.name.startswith("."):
            continue
        if plugin_dir.name == "research-agents":
            for subdir in ["agents", "micro-skills", "orchestrators", "helpers"]:
                d = plugin_dir / subdir
                if d.exists():
                    files.extend(
                        sorted(
                            f
                            for f in d.iterdir()
                            if f.suffix == ".md" and not f.name.startswith((".", "_"))
                        )
                    )
        else:
            commands_dir = plugin_dir / "commands"
            if commands_dir.exists():
                files.extend(
                    sorted(
                        f
                        for f in commands_dir.iterdir()
                        if f.suffix == ".md" and not f.name.startswith((".", "_"))
                    )
                )
            for sub_dir in sorted(plugin_dir.iterdir()):
                if sub_dir.is_dir() and not sub_dir.name.startswith("."):
                    sub_commands = sub_dir / "commands"
                    if sub_commands.exists():
                        files.extend(
                            sorted(
                                f
                                for f in sub_commands.iterdir()
                                if f.suffix == ".md" and not f.name.startswith((".", "_"))
                            )
                        )
    return files


def collect_plugin_skills(plugin_name: str) -> list[Path]:
    """Collect skills for a specific plugin."""
    plugin_dir = PLUGINS_DIR / plugin_name
    if not plugin_dir.exists():
        return []
    files = []
    if plugin_name == "research-agents":
        for subdir in ["agents", "micro-skills", "orchestrators", "helpers"]:
            d = plugin_dir / subdir
            if d.exists():
                files.extend(sorted(f for f in d.iterdir() if f.suffix == ".md" and not f.name.startswith((".", "_"))))
    else:
        commands_dir = plugin_dir / "commands"
        if commands_dir.exists():
            files.extend(
                sorted(
                    f
                    for f in commands_dir.iterdir()
                    if f.suffix == ".md" and not f.name.startswith((".", "_"))
                )
            )
    return files


def to_cursor(fm: dict, body: str, skill_name: str) -> str:
    """Convert to Cursor rules format."""
    desc = fm.get("description", "")
    if isinstance(desc, str):
        desc = desc.strip()
    return f"""---
description: {desc}
globs:
alwaysApply: false
---

{body.strip()}
"""


def to_gemini(fm: dict, body: str, skill_name: str) -> str:
    """Convert to Gemini CLI agent format."""
    desc = fm.get("description", "")
    if isinstance(desc, str):
        desc = desc.strip()
    return f"""# {skill_name}

{desc}

{body.strip()}
"""


def to_copilot(fm: dict, body: str, skill_name: str) -> str:
    """Convert to GitHub Copilot instructions section."""
    desc = fm.get("description", "")
    if isinstance(desc, str):
        desc = desc.strip()
    return f"""## {skill_name}

{desc}

{body.strip()}
"""


def to_agentskills(fm: dict, body: str, skill_name: str) -> str:
    """Convert to AgentSkills.io SKILL.md format."""
    desc = fm.get("description", "")
    if isinstance(desc, str):
        desc = desc.strip()
    metadata = fm.get("metadata", {})
    model = fm.get("model", "sonnet")
    return f"""---
name: {skill_name}
version: "1.0.0"
description: |
  {desc}
author: Research Agora
license: MIT
model: {model}
tags:
  - {metadata.get('research-domain', 'general')}
  - {metadata.get('task-type', 'writing')}
  - {metadata.get('research-phase', 'paper-writing')}
platforms:
  - claude-code
  - cursor
  - gemini-cli
---

{body.strip()}
"""


CONVERTERS = {
    "cursor": (to_cursor, ".cursor/rules", ".mdc"),
    "gemini": (to_gemini, ".gemini/agents", ".md"),
    "copilot": (to_copilot, ".github", ".md"),
    "agentskills": (to_agentskills, ".", ".md"),
}


def convert_skill(skill_path: Path, fmt: str, output_dir: Path) -> Path:
    """Convert a single skill and write to output directory."""
    fm, body = parse_yaml_frontmatter(skill_path)
    skill_name = fm.get("name", skill_path.stem)

    converter, subdir, ext = CONVERTERS[fmt]
    converted = converter(fm, body, skill_name)

    if fmt == "copilot":
        # Copilot appends to a single file
        out_path = output_dir / subdir / f"copilot-instructions{ext}"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "a") as f:
            f.write(converted + "\n\n")
        return out_path
    else:
        out_path = output_dir / subdir / f"{skill_name}{ext}"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(converted)
        return out_path


def main():
    parser = argparse.ArgumentParser(description="Convert Research Agora skills to other agent formats")
    parser.add_argument("--format", required=True, choices=list(CONVERTERS.keys()),
                        help="Target format")
    parser.add_argument("--skill", help="Convert a single skill by name")
    parser.add_argument("--plugin", help="Convert all skills in a plugin")
    parser.add_argument("--all", action="store_true", help="Convert all skills")
    parser.add_argument("--output", default=".", help="Output directory (default: current dir)")

    args = parser.parse_args()
    output_dir = Path(args.output)

    if args.skill:
        skill_path = find_skill_file(args.skill)
        if not skill_path:
            print(f"Error: Skill '{args.skill}' not found")
            sys.exit(1)
        out = convert_skill(skill_path, args.format, output_dir)
        print(f"Converted {args.skill} → {out}")

    elif args.plugin:
        skills = collect_plugin_skills(args.plugin)
        if not skills:
            print(f"Error: No skills found in plugin '{args.plugin}'")
            sys.exit(1)
        for skill_path in skills:
            out = convert_skill(skill_path, args.format, output_dir)
            print(f"  {skill_path.stem} → {out}")
        print(f"\nConverted {len(skills)} skills to {args.format} format")

    elif args.all:
        skills = collect_all_skills()
        for skill_path in skills:
            out = convert_skill(skill_path, args.format, output_dir)
            print(f"  {skill_path.stem} → {out.relative_to(output_dir)}")
        print(f"\nConverted {len(skills)} skills to {args.format} format")

    else:
        print("Error: Specify --skill, --plugin, or --all")
        sys.exit(1)


if __name__ == "__main__":
    main()
