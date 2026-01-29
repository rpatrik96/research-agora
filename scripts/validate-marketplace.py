#!/usr/bin/env python3
"""
Validate Claude Code marketplace structure.

Checks:
- marketplace.json exists and is valid JSON
- All plugins listed in marketplace.json exist
- Skills have valid .claude-plugin/plugin.json and SKILL.md
- Agents have valid .md files with YAML frontmatter
- Required fields are present in all manifests
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).parent.parent

# Required fields in marketplace.json
MARKETPLACE_REQUIRED = ["name", "owner", "metadata", "plugins"]
MARKETPLACE_OWNER_REQUIRED = ["name", "email"]
MARKETPLACE_METADATA_REQUIRED = ["description", "version"]

# Required fields in plugin.json
PLUGIN_REQUIRED = ["name", "version", "description", "author", "license"]
PLUGIN_AUTHOR_REQUIRED = ["name"]

# Required fields in agent frontmatter
AGENT_FRONTMATTER_REQUIRED = ["name", "description"]


def parse_yaml_frontmatter(file_path: Path) -> Dict:
    """Parse YAML frontmatter from a markdown file."""
    try:
        import yaml
    except ImportError:
        # Fallback to basic parsing if yaml not installed
        content = file_path.read_text()
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if not match:
            return {}
        # Basic key: value parsing
        result = {}
        for line in match.group(1).split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                result[key.strip()] = value.strip()
        return result

    content = file_path.read_text()
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return {}

    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}


def validate_marketplace_json() -> Tuple[bool, List[str]]:
    """Validate marketplace.json file."""
    errors = []
    marketplace_path = REPO_ROOT / ".claude-plugin" / "marketplace.json"

    if not marketplace_path.exists():
        return False, [f"marketplace.json not found at {marketplace_path}"]

    try:
        with open(marketplace_path) as f:
            marketplace = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON in marketplace.json: {e}"]

    # Check required top-level fields
    for field in MARKETPLACE_REQUIRED:
        if field not in marketplace:
            errors.append(f"Missing required field in marketplace.json: {field}")

    # Check owner fields
    if "owner" in marketplace:
        for field in MARKETPLACE_OWNER_REQUIRED:
            if field not in marketplace["owner"]:
                errors.append(f"Missing required field in marketplace.json owner: {field}")

    # Check metadata fields
    if "metadata" in marketplace:
        for field in MARKETPLACE_METADATA_REQUIRED:
            if field not in marketplace["metadata"]:
                errors.append(f"Missing required field in marketplace.json metadata: {field}")

    # Check plugins array
    if "plugins" not in marketplace:
        errors.append("marketplace.json missing 'plugins' array")
    elif not isinstance(marketplace["plugins"], list):
        errors.append("marketplace.json 'plugins' must be an array")
    elif len(marketplace["plugins"]) == 0:
        errors.append("marketplace.json 'plugins' array is empty")

    return len(errors) == 0, errors


def validate_skill(plugin_name: str, plugin_entry: Dict) -> Tuple[bool, List[str]]:
    """Validate a skill plugin (has .claude-plugin/plugin.json and SKILL.md)."""
    errors = []

    source = plugin_entry.get("source", "")
    if source.startswith("./"):
        plugin_dir = REPO_ROOT / source[2:]
    else:
        plugin_dir = REPO_ROOT / source

    # Check plugin directory exists
    if not plugin_dir.exists():
        errors.append(f"Plugin directory not found: {plugin_dir}")
        return False, errors

    # Check .claude-plugin directory
    claude_plugin_dir = plugin_dir / ".claude-plugin"
    if not claude_plugin_dir.exists():
        errors.append(f"Missing .claude-plugin directory in {plugin_dir}")
        return False, errors

    # Check plugin.json
    plugin_json_path = claude_plugin_dir / "plugin.json"
    if not plugin_json_path.exists():
        errors.append(f"Missing plugin.json in {claude_plugin_dir}")
        return False, errors

    try:
        with open(plugin_json_path) as f:
            plugin_json = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in {plugin_json_path}: {e}")
        return False, errors

    # Check required fields
    for field in PLUGIN_REQUIRED:
        if field not in plugin_json:
            errors.append(f"Missing required field in {plugin_name}/plugin.json: {field}")

    # Check author fields
    if "author" in plugin_json:
        if not isinstance(plugin_json["author"], dict):
            errors.append(f"'author' must be an object in {plugin_name}/plugin.json")
        else:
            for field in PLUGIN_AUTHOR_REQUIRED:
                if field not in plugin_json["author"]:
                    errors.append(f"Missing required field in {plugin_name}/plugin.json author: {field}")

    # Check name matches
    if "name" in plugin_json and plugin_json["name"] != plugin_name:
        errors.append(f"Plugin name mismatch: marketplace says '{plugin_name}', plugin.json says '{plugin_json['name']}'")

    # Check SKILL.md exists
    skill_md = plugin_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append(f"Missing SKILL.md in {plugin_dir}")

    return len(errors) == 0, errors


def validate_agent(plugin_name: str, plugin_entry: Dict) -> Tuple[bool, List[str]]:
    """Validate an agent plugin (has .md file with YAML frontmatter in agents/)."""
    errors = []

    agents_dir = REPO_ROOT / "agents"
    if not agents_dir.exists():
        errors.append(f"Agents directory not found: {agents_dir}")
        return False, errors

    # For agent plugins, we check if there are valid .md files in the agents directory
    # The plugin_name should correspond to an agent file or be a collection name
    agent_files = list(agents_dir.glob("*.md"))

    if not agent_files:
        errors.append(f"No agent .md files found in {agents_dir}")
        return False, errors

    # Validate each agent file has proper frontmatter
    for agent_file in agent_files:
        frontmatter = parse_yaml_frontmatter(agent_file)
        if not frontmatter:
            errors.append(f"Agent {agent_file.name} missing YAML frontmatter")
            continue

        for field in AGENT_FRONTMATTER_REQUIRED:
            if field not in frontmatter:
                errors.append(f"Agent {agent_file.name} missing frontmatter field: {field}")

    return len(errors) == 0, errors


def is_agent_plugin(plugin_entry: Dict) -> bool:
    """Check if a plugin entry is an agent (source is ./agents)."""
    return plugin_entry.get("source") == "./agents"


def main():
    """Run all validations."""
    print("Validating Claude Code marketplace structure...")
    print()

    all_valid = True
    total_errors = []

    # Validate marketplace.json
    print("Checking marketplace.json...")
    valid, errors = validate_marketplace_json()
    if valid:
        print("  ✓ marketplace.json is valid")
    else:
        print("  ✗ marketplace.json has errors:")
        for error in errors:
            print(f"    - {error}")
        all_valid = False
        total_errors.extend(errors)
    print()

    # Load marketplace.json to validate plugins
    marketplace_path = REPO_ROOT / ".claude-plugin" / "marketplace.json"
    if not marketplace_path.exists():
        print("Cannot validate plugins: marketplace.json not found")
        sys.exit(1)

    with open(marketplace_path) as f:
        marketplace = json.load(f)

    plugins = marketplace.get("plugins", [])

    # Separate skills and agents
    skill_plugins = [p for p in plugins if not is_agent_plugin(p)]
    agent_plugins = [p for p in plugins if is_agent_plugin(p)]

    # Validate skills
    print(f"Validating {len(skill_plugins)} skills...")
    print()

    for plugin_entry in skill_plugins:
        plugin_name = plugin_entry.get("name", "unknown")
        valid, errors = validate_skill(plugin_name, plugin_entry)

        if valid:
            print(f"  ✓ {plugin_name}")
        else:
            print(f"  ✗ {plugin_name}")
            for error in errors:
                print(f"    - {error}")
            all_valid = False
            total_errors.extend(errors)

    print()

    # Validate agents (only once, since they all point to same directory)
    if agent_plugins:
        print(f"Validating agents ({len(agent_plugins)} entries in marketplace)...")
        print()

        # Validate the agents directory once
        valid, errors = validate_agent("agents", agent_plugins[0])

        if valid:
            print("  ✓ agents directory valid")
            for plugin_entry in agent_plugins:
                print(f"    - {plugin_entry.get('name', 'unknown')}")
        else:
            print("  ✗ agents directory has errors:")
            for error in errors:
                print(f"    - {error}")
            all_valid = False
            total_errors.extend(errors)

        print()

    print("═" * 70)
    if all_valid:
        print("✓ All validations passed!")
        print()
        print("Next steps:")
        print("  1. Commit changes: git add . && git commit -m 'feat: convert to native marketplace'")
        print("  2. Push to GitHub: git push")
        print("  3. Add marketplace: /plugin marketplace add rpatrik96/claude-skills")
        print("  4. Install plugins: /plugin install paper-introduction@research-agora")
        sys.exit(0)
    else:
        print(f"✗ Found {len(total_errors)} errors")
        print()
        print("Please fix the errors above before publishing the marketplace.")
        sys.exit(1)


if __name__ == "__main__":
    main()
