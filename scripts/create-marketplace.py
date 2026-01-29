#!/usr/bin/env python3
"""
Migrate Claude Code skills to native plugin marketplace format.

This script:
1. Scans all existing skills in category directories
2. Extracts metadata from SKILL.md frontmatter
3. Creates .claude-plugin/plugin.json for each skill
4. Generates .claude-plugin/marketplace.json registry
5. Reorganizes skills into plugins/ directory (optional)
"""

import json
import os
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Repository root
REPO_ROOT = Path(__file__).parent.parent
SKILLS_CATEGORIES = ["academic", "development", "formatting", "office"]

# Category mappings for plugin metadata
CATEGORY_MAP = {
    "academic": "productivity",
    "development": "developer-tools",
    "formatting": "productivity",
    "office": "productivity",
}

# Keyword mappings
KEYWORD_MAP = {
    "academic": ["academic", "writing", "ml-research", "paper"],
    "development": ["python", "development", "automation"],
    "formatting": ["formatting", "latex", "visualization"],
    "office": ["office", "documents", "presentation"],
}


def extract_frontmatter(skill_md_path: Path) -> Optional[Dict[str, Any]]:
    """Extract YAML frontmatter from SKILL.md file."""
    content = skill_md_path.read_text()

    # Match YAML frontmatter
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        print(f"Warning: No frontmatter found in {skill_md_path}")
        return None

    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        print(f"Error parsing frontmatter in {skill_md_path}: {e}")
        return None


def create_plugin_json(
    skill_name: str,
    skill_category: str,
    frontmatter: Dict[str, Any],
    version: str = "1.0.0"
) -> Dict[str, Any]:
    """Create plugin.json metadata from SKILL.md frontmatter."""

    # Extract description (remove trigger phrases part)
    description = frontmatter.get("description", "").strip()
    # Remove "Use when asked to..." part
    description = re.sub(r'\s*Use when asked to.*$', '', description, flags=re.DOTALL)
    description = description.strip()

    plugin_json = {
        "name": skill_name,
        "version": version,
        "description": description,
        "author": {
            "name": "rpatrik96",
            "email": "[email protected]"
        },
        "homepage": "https://github.com/rpatrik96/claude-skills",
        "repository": "https://github.com/rpatrik96/claude-skills",
        "license": "MIT",
        "keywords": KEYWORD_MAP.get(skill_category, []) + [skill_name],
    }

    return plugin_json


def scan_skills() -> List[Dict[str, Any]]:
    """Scan all skill directories and extract metadata."""
    skills = []

    for category in SKILLS_CATEGORIES:
        category_dir = REPO_ROOT / category
        if not category_dir.exists():
            print(f"Warning: Category directory {category} not found")
            continue

        for skill_dir in category_dir.iterdir():
            if not skill_dir.is_dir():
                continue

            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                print(f"Warning: No SKILL.md in {skill_dir}")
                continue

            frontmatter = extract_frontmatter(skill_md)
            if not frontmatter:
                continue

            skill_name = frontmatter.get("name", skill_dir.name)

            skills.append({
                "name": skill_name,
                "category": category,
                "path": skill_dir,
                "frontmatter": frontmatter,
            })

    return skills


def create_plugin_structure(skill: Dict[str, Any], reorganize: bool = True) -> Path:
    """Create .claude-plugin directory and plugin.json for a skill."""

    if reorganize:
        # Move to plugins/ directory
        new_path = REPO_ROOT / "plugins" / skill["name"]
        new_path.mkdir(parents=True, exist_ok=True)

        # Copy skill contents
        for item in skill["path"].iterdir():
            if item.is_dir():
                shutil.copytree(item, new_path / item.name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, new_path / item.name)

        skill_path = new_path
    else:
        # Keep in current location
        skill_path = skill["path"]

    # Create .claude-plugin directory
    plugin_dir = skill_path / ".claude-plugin"
    plugin_dir.mkdir(exist_ok=True)

    # Create plugin.json
    plugin_json = create_plugin_json(
        skill["name"],
        skill["category"],
        skill["frontmatter"]
    )

    plugin_json_path = plugin_dir / "plugin.json"
    plugin_json_path.write_text(json.dumps(plugin_json, indent=2) + "\n")

    print(f"Created plugin.json for {skill['name']}")

    return skill_path


def create_marketplace_json(skills: List[Dict[str, Any]], reorganize: bool = True) -> None:
    """Create marketplace.json registry."""

    plugins = []
    for skill in sorted(skills, key=lambda s: s["name"]):
        # Extract description
        description = skill["frontmatter"].get("description", "").strip()
        description = re.sub(r'\s*Use when asked to.*$', '', description, flags=re.DOTALL)
        description = description.strip()

        plugin_entry = {
            "name": skill["name"],
            "source": skill["name"] if reorganize else f"./{skill['category']}/{skill['name']}",
            "description": description,
            "version": "1.0.0",
            "author": {"name": "rpatrik96"},
            "category": skill["category"],
            "keywords": KEYWORD_MAP.get(skill["category"], []) + [skill["name"]],
        }
        plugins.append(plugin_entry)

    marketplace = {
        "name": "research-agora",
        "owner": {
            "name": "Patrik Reizinger",
            "email": "[email protected]"
        },
        "metadata": {
            "description": "Research Agora - A plugin marketplace for Claude Code focused on ML research, academic writing, and development automation",
            "version": "1.0.0",
        }
    }

    if reorganize:
        marketplace["metadata"]["pluginRoot"] = "./plugins"

    marketplace["plugins"] = plugins

    # Create .claude-plugin directory at root
    plugin_dir = REPO_ROOT / ".claude-plugin"
    plugin_dir.mkdir(exist_ok=True)

    # Write marketplace.json
    marketplace_json_path = plugin_dir / "marketplace.json"
    marketplace_json_path.write_text(json.dumps(marketplace, indent=2) + "\n")

    print(f"\nCreated marketplace.json with {len(plugins)} plugins")


def main():
    """Main migration script."""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate skills to Claude Code marketplace format")
    parser.add_argument(
        "--reorganize",
        action="store_true",
        help="Reorganize skills into plugins/ directory (default: keep in place)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )

    args = parser.parse_args()

    print("Scanning existing skills...")
    skills = scan_skills()
    print(f"Found {len(skills)} skills\n")

    if args.dry_run:
        print("Dry run - no changes will be made\n")
        for skill in skills:
            print(f"  {skill['category']}/{skill['name']}")
        return

    if args.reorganize:
        print("Reorganizing skills into plugins/ directory...")
        plugins_dir = REPO_ROOT / "plugins"
        plugins_dir.mkdir(exist_ok=True)

    # Create plugin structure for each skill
    for skill in skills:
        create_plugin_structure(skill, reorganize=args.reorganize)

    # Create marketplace.json
    create_marketplace_json(skills, reorganize=args.reorganize)

    print("\n✓ Marketplace structure created!")
    print("\nNext steps:")
    print("  1. Review generated .claude-plugin/ directories")
    print("  2. Run: /plugin validate .")
    print("  3. Test: /plugin marketplace add ./")
    print("  4. Commit and push to GitHub")


if __name__ == "__main__":
    main()
