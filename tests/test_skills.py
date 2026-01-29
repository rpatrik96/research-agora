"""
Tests for plugin and command validation.
"""

import json
import re
from pathlib import Path
from typing import Any

import pytest
from conftest import parse_yaml_frontmatter


class TestPluginDirectoryStructure:
    """Tests for plugin directory structure."""

    def test_plugins_directory_exists(self, plugins_dir: Path) -> None:
        """Plugins directory must exist."""
        assert plugins_dir.exists(), f"Plugins directory not found at {plugins_dir}"

    def test_plugin_categories_exist(
        self, plugins_dir: Path, valid_categories: list[str]
    ) -> None:
        """Expected category plugin directories should exist."""
        plugin_categories = ["academic", "development", "formatting", "office", "research-agents"]
        for category in plugin_categories:
            category_path = plugins_dir / category
            assert category_path.exists(), f"Plugin directory missing: {category}"
            assert category_path.is_dir(), f"Plugin must be a directory: {category}"

    def test_all_plugins_have_claude_plugin_dir(self, all_plugin_dirs: list[Path]) -> None:
        """Each plugin must have a .claude-plugin directory."""
        for plugin_dir in all_plugin_dirs:
            claude_plugin = plugin_dir / ".claude-plugin"
            assert (
                claude_plugin.exists()
            ), f"Missing .claude-plugin directory in {plugin_dir.name}"

    def test_all_plugins_have_plugin_json(self, all_plugin_dirs: list[Path]) -> None:
        """Each plugin must have .claude-plugin/plugin.json."""
        for plugin_dir in all_plugin_dirs:
            plugin_json = plugin_dir / ".claude-plugin" / "plugin.json"
            assert (
                plugin_json.exists()
            ), f"Missing plugin.json in {plugin_dir.name}/.claude-plugin/"

    def test_command_plugins_have_commands_dir(self, all_plugin_dirs: list[Path]) -> None:
        """Command-based plugins must have a commands/ directory."""
        for plugin_dir in all_plugin_dirs:
            if plugin_dir.name != "research-agents":
                commands_dir = plugin_dir / "commands"
                assert (
                    commands_dir.exists()
                ), f"Missing commands/ directory in {plugin_dir.name}"


class TestPluginJson:
    """Tests for .claude-plugin/plugin.json files."""

    def test_plugin_json_is_valid_json(self, all_plugin_dirs: list[Path]) -> None:
        """Each plugin.json must be valid JSON."""
        for plugin_dir in all_plugin_dirs:
            plugin_json_path = plugin_dir / ".claude-plugin" / "plugin.json"
            try:
                with open(plugin_json_path) as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON in {plugin_dir.name}/plugin.json: {e}")

    def test_plugin_json_has_required_fields(
        self, all_plugin_dirs: list[Path], required_plugin_json_fields: list[str]
    ) -> None:
        """Each plugin.json must have required fields."""
        for plugin_dir in all_plugin_dirs:
            plugin_json_path = plugin_dir / ".claude-plugin" / "plugin.json"
            with open(plugin_json_path) as f:
                data = json.load(f)

            for field in required_plugin_json_fields:
                assert (
                    field in data
                ), f"{plugin_dir.name}/plugin.json missing required field: {field}"

    def test_plugin_json_name_matches_directory(
        self, all_plugin_dirs: list[Path]
    ) -> None:
        """Plugin.json name must match directory name."""
        for plugin_dir in all_plugin_dirs:
            plugin_json_path = plugin_dir / ".claude-plugin" / "plugin.json"
            with open(plugin_json_path) as f:
                data = json.load(f)

            expected_name = plugin_dir.name
            actual_name = data.get("name", "")
            assert (
                actual_name == expected_name
            ), f"Name mismatch in {plugin_dir.name}: plugin.json says '{actual_name}'"

    def test_plugin_json_author_structure(self, all_plugin_dirs: list[Path]) -> None:
        """Plugin.json author must have at least a name."""
        for plugin_dir in all_plugin_dirs:
            plugin_json_path = plugin_dir / ".claude-plugin" / "plugin.json"
            with open(plugin_json_path) as f:
                data = json.load(f)

            author = data.get("author", {})
            assert isinstance(
                author, dict
            ), f"{plugin_dir.name}/plugin.json: author must be an object"
            assert "name" in author, f"{plugin_dir.name}/plugin.json: author missing 'name'"

    def test_plugin_json_has_license(self, all_plugin_dirs: list[Path]) -> None:
        """Plugin.json should have a license field."""
        for plugin_dir in all_plugin_dirs:
            plugin_json_path = plugin_dir / ".claude-plugin" / "plugin.json"
            with open(plugin_json_path) as f:
                data = json.load(f)

            assert "license" in data, f"{plugin_dir.name}/plugin.json missing 'license'"
            assert (
                len(data["license"]) > 0
            ), f"{plugin_dir.name}/plugin.json has empty license"


class TestCommandMarkdown:
    """Tests for command .md files in commands/ directories."""

    def test_command_files_have_frontmatter(self, all_command_files: list[Path]) -> None:
        """Each command .md file must have YAML frontmatter."""
        for cmd_file in all_command_files:
            frontmatter = parse_yaml_frontmatter(cmd_file)
            assert (
                frontmatter is not None
            ), f"{cmd_file.name} missing YAML frontmatter"

    def test_command_files_have_required_fields(
        self, all_command_files: list[Path], required_command_frontmatter_fields: list[str]
    ) -> None:
        """Command frontmatter must have required fields."""
        for cmd_file in all_command_files:
            frontmatter = parse_yaml_frontmatter(cmd_file)

            if frontmatter is None:
                pytest.fail(f"{cmd_file.name} has no frontmatter")

            for field in required_command_frontmatter_fields:
                assert (
                    field in frontmatter
                ), f"{cmd_file.name} frontmatter missing: {field}"

    def test_command_name_matches_filename(self, all_command_files: list[Path]) -> None:
        """Command frontmatter name must match filename (without .md)."""
        for cmd_file in all_command_files:
            frontmatter = parse_yaml_frontmatter(cmd_file)

            if frontmatter is None:
                continue

            expected_name = cmd_file.stem  # filename without .md
            actual_name = frontmatter.get("name", "")
            assert (
                actual_name == expected_name
            ), f"Name mismatch in {cmd_file.name}: frontmatter says '{actual_name}', expected '{expected_name}'"

    def test_command_description_not_empty(self, all_command_files: list[Path]) -> None:
        """Command frontmatter description must not be empty."""
        for cmd_file in all_command_files:
            frontmatter = parse_yaml_frontmatter(cmd_file)

            if frontmatter is None:
                continue

            description = frontmatter.get("description", "")
            assert (
                len(str(description).strip()) > 0
            ), f"{cmd_file.name} has empty description"

    def test_command_has_content_beyond_frontmatter(
        self, all_command_files: list[Path]
    ) -> None:
        """Command files must have content beyond just frontmatter."""
        for cmd_file in all_command_files:
            content = cmd_file.read_text()

            # Remove frontmatter
            content_without_frontmatter = re.sub(
                r"^---\s*\n.*?\n---\s*\n", "", content, flags=re.DOTALL
            )

            assert (
                len(content_without_frontmatter.strip()) > 50
            ), f"{cmd_file.name} has insufficient content"


class TestPluginConsistency:
    """Tests for consistency between marketplace and plugin directories."""

    def test_marketplace_plugins_exist_on_disk(
        self, marketplace_plugins: list[dict[str, Any]], repo_root: Path
    ) -> None:
        """All plugins in marketplace must exist on disk."""
        for plugin in marketplace_plugins:
            source = plugin.get("source", "")
            plugin_name = plugin.get("name", "<unknown>")

            if source.startswith("./"):
                plugin_path = repo_root / source[2:]
            else:
                plugin_path = repo_root / source

            assert (
                plugin_path.exists()
            ), f"Marketplace plugin '{plugin_name}' not found at {plugin_path}"

    def test_marketplace_plugin_names_match_plugin_json(
        self, marketplace_plugins: list[dict[str, Any]], repo_root: Path
    ) -> None:
        """Marketplace plugin names must match their plugin.json names."""
        for plugin in marketplace_plugins:
            source = plugin.get("source", "")
            marketplace_name = plugin.get("name", "")

            if source.startswith("./"):
                plugin_path = repo_root / source[2:]
            else:
                plugin_path = repo_root / source

            plugin_json_path = plugin_path / ".claude-plugin" / "plugin.json"
            if not plugin_json_path.exists():
                continue

            with open(plugin_json_path) as f:
                plugin_json_data = json.load(f)

            plugin_json_name = plugin_json_data.get("name", "")
            assert (
                marketplace_name == plugin_json_name
            ), f"Name mismatch for '{marketplace_name}': plugin.json says '{plugin_json_name}'"

    def test_disk_plugins_listed_in_marketplace(
        self, all_plugin_dirs: list[Path], marketplace_plugins: list[dict[str, Any]], repo_root: Path
    ) -> None:
        """All plugins on disk should be listed in marketplace."""
        # Get plugin names from marketplace
        marketplace_sources = set()
        for plugin in marketplace_plugins:
            source = plugin.get("source", "")
            if source.startswith("./"):
                marketplace_sources.add(str(repo_root / source[2:]))
            else:
                marketplace_sources.add(str(repo_root / source))

        # Check each disk plugin
        missing = []
        for plugin_dir in all_plugin_dirs:
            if str(plugin_dir) not in marketplace_sources:
                missing.append(plugin_dir.name)

        assert len(missing) == 0, f"Plugins on disk but not in marketplace: {missing}"
