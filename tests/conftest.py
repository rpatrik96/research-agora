"""
Pytest fixtures for claude-skills marketplace testing.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

import pytest
import yaml

# Skip synthetic test directory when playwright is not installed
try:
    import playwright  # noqa: F401
except ImportError:
    collect_ignore_glob = ["synthetic/**"]

# Repository root
REPO_ROOT = Path(__file__).parent.parent


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Return the repository root path."""
    return REPO_ROOT


@pytest.fixture(scope="session")
def marketplace_path(repo_root: Path) -> Path:
    """Return the path to marketplace.json."""
    return repo_root / ".claude-plugin" / "marketplace.json"


@pytest.fixture(scope="session")
def marketplace_data(marketplace_path: Path) -> dict[str, Any]:
    """Load and return marketplace.json data."""
    with open(marketplace_path) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def plugins_dir(repo_root: Path) -> Path:
    """Return the plugins directory path."""
    return repo_root / "plugins"


@pytest.fixture(scope="session")
def agents_dir(repo_root: Path) -> Path:
    """Return the research-agents agents directory path."""
    return repo_root / "plugins" / "research-agents" / "agents"


@pytest.fixture(scope="session")
def all_command_files(plugins_dir: Path) -> list[Path]:
    """Return all command .md files from plugins/*/commands/ directories."""
    command_files = []
    for plugin_dir in plugins_dir.iterdir():
        if plugin_dir.is_dir() and not plugin_dir.name.startswith("."):
            commands_dir = plugin_dir / "commands"
            if commands_dir.exists():
                for cmd_file in commands_dir.iterdir():
                    if cmd_file.suffix == ".md" and not cmd_file.name.startswith(".") and not cmd_file.stem.isupper():
                        command_files.append(cmd_file)
    return sorted(command_files)


@pytest.fixture(scope="session")
def all_plugin_dirs(plugins_dir: Path) -> list[Path]:
    """Return all plugin directories (those with .claude-plugin/plugin.json)."""
    plugin_dirs = []
    for plugin_dir in plugins_dir.iterdir():
        if plugin_dir.is_dir() and not plugin_dir.name.startswith("."):
            if (plugin_dir / ".claude-plugin" / "plugin.json").exists():
                plugin_dirs.append(plugin_dir)
    return sorted(plugin_dirs)


@pytest.fixture(scope="session")
def all_agent_files(agents_dir: Path) -> list[Path]:
    """Return all agent .md files from plugins/research-agents/agents/."""
    if not agents_dir.exists():
        return []
    return sorted([
        f for f in agents_dir.iterdir()
        if f.suffix == ".md" and not f.name.startswith(".") and not f.stem.isupper()
    ])


@pytest.fixture(scope="session")
def marketplace_plugins(marketplace_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the plugins list from marketplace.json."""
    return marketplace_data.get("plugins", [])


@pytest.fixture(scope="session")
def command_plugins(marketplace_plugins: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return plugins that contain commands (not research-agents)."""
    return [p for p in marketplace_plugins if p.get("name") != "research-agents"]


@pytest.fixture(scope="session")
def agent_plugins(marketplace_plugins: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return only the research-agents plugin."""
    return [p for p in marketplace_plugins if p.get("name") == "research-agents"]


def parse_yaml_frontmatter(file_path: Path) -> Optional[dict[str, Any]]:
    """Parse YAML frontmatter from a markdown file.

    Returns None if no frontmatter found.
    """
    content = file_path.read_text()

    # Match YAML frontmatter between --- markers
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None

    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


@pytest.fixture(scope="session")
def valid_categories() -> list[str]:
    """Return the list of valid plugin categories."""
    return ["academic", "development", "editorial", "formatting", "office", "research"]


@pytest.fixture(scope="session")
def required_marketplace_fields() -> list[str]:
    """Return required top-level fields for marketplace.json."""
    return ["name", "owner", "metadata", "plugins"]


@pytest.fixture(scope="session")
def required_plugin_fields() -> list[str]:
    """Return required fields for plugin entries in marketplace.json."""
    return ["name", "source", "description", "version", "author", "category"]


@pytest.fixture(scope="session")
def required_plugin_json_fields() -> list[str]:
    """Return required fields for .claude-plugin/plugin.json files."""
    return ["name", "version", "description", "author", "license"]


@pytest.fixture(scope="session")
def required_command_frontmatter_fields() -> list[str]:
    """Return required fields for command .md frontmatter."""
    return ["name", "description"]


@pytest.fixture(scope="session")
def required_agent_frontmatter_fields() -> list[str]:
    """Return required fields for agent .md frontmatter."""
    return ["name", "description"]
