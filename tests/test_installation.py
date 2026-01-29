"""
Tests for installation simulation and marketplace configuration.

Note: Global configuration files (global-settings.json, install.sh, CLAUDE.md)
are in the separate claude-config repository, not in research-agora.
"""

import json
import re
from pathlib import Path
from typing import Any

import pytest


class TestValidationScript:
    """Tests for the validation script."""

    @pytest.fixture
    def validate_script_path(self, repo_root: Path) -> Path:
        """Return path to validate-marketplace.py."""
        return repo_root / "scripts" / "validate-marketplace.py"

    def test_validation_script_exists(self, validate_script_path: Path) -> None:
        """Validation script must exist."""
        assert validate_script_path.exists(), "validate-marketplace.py not found"

    def test_validation_script_is_python(self, validate_script_path: Path) -> None:
        """Validation script should be valid Python syntax."""
        content = validate_script_path.read_text()
        try:
            compile(content, validate_script_path, "exec")
        except SyntaxError as e:
            pytest.fail(f"validate-marketplace.py has syntax error: {e}")


class TestInstallableComponents:
    """Tests simulating installation requirements."""

    def test_all_plugin_sources_are_relative(
        self, marketplace_plugins: list[dict[str, Any]]
    ) -> None:
        """All plugin sources should use relative paths starting with ./"""
        for plugin in marketplace_plugins:
            source = plugin.get("source", "")
            plugin_name = plugin.get("name", "<unknown>")
            assert source.startswith("./"), (
                f"Plugin '{plugin_name}' source '{source}' should start with ./. "
                f"Relative paths are required for local installation."
            )

    def test_no_external_dependencies_in_sources(
        self, marketplace_plugins: list[dict[str, Any]]
    ) -> None:
        """Plugin sources should not contain URLs or external references."""
        for plugin in marketplace_plugins:
            source = plugin.get("source", "")
            plugin_name = plugin.get("name", "<unknown>")
            assert not source.startswith("http"), (
                f"Plugin '{plugin_name}' source should not be a URL"
            )
            assert not source.startswith("git@"), (
                f"Plugin '{plugin_name}' source should not be a git URL"
            )

    def test_plugin_json_files_are_self_contained(
        self, all_plugin_dirs: list[Path]
    ) -> None:
        """Plugin.json files should not reference external resources."""
        for plugin_dir in all_plugin_dirs:
            plugin_json_path = plugin_dir / ".claude-plugin" / "plugin.json"
            with open(plugin_json_path) as f:
                data = json.load(f)

            # Check no external dependencies field requires remote fetch
            deps = data.get("dependencies", {})
            if deps:
                # Python dependencies in SKILL.md frontmatter are ok
                # but plugin.json shouldn't have complex external deps
                assert not isinstance(deps, str) or not deps.startswith("http"), (
                    f"{plugin_dir.name}/plugin.json has external dependency URL"
                )


class TestDirectoryConventions:
    """Tests for directory and file naming conventions."""

    def test_plugin_directories_are_kebab_case(
        self, all_plugin_dirs: list[Path]
    ) -> None:
        """Plugin directory names must be kebab-case."""
        kebab_pattern = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

        for plugin_dir in all_plugin_dirs:
            assert kebab_pattern.match(plugin_dir.name), (
                f"Plugin directory '{plugin_dir.name}' is not kebab-case"
            )

    def test_command_files_are_kebab_case(self, all_command_files: list[Path]) -> None:
        """Command file names must be kebab-case."""
        kebab_pattern = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

        for cmd_file in all_command_files:
            # Check the stem (filename without extension)
            assert kebab_pattern.match(cmd_file.stem), (
                f"Command file '{cmd_file.name}' is not kebab-case"
            )

    def test_agent_files_are_kebab_case(self, all_agent_files: list[Path]) -> None:
        """Agent file names must be kebab-case."""
        kebab_pattern = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

        for agent_file in all_agent_files:
            # Check the stem (filename without extension)
            assert kebab_pattern.match(agent_file.stem), (
                f"Agent file '{agent_file.name}' is not kebab-case"
            )

    def test_no_hidden_files_in_plugins(self, all_plugin_dirs: list[Path]) -> None:
        """Plugins shouldn't have hidden files except .claude-plugin."""
        for plugin_dir in all_plugin_dirs:
            hidden_files = [
                f for f in plugin_dir.iterdir()
                if f.name.startswith(".") and f.name != ".claude-plugin"
            ]
            assert len(hidden_files) == 0, (
                f"Plugin '{plugin_dir.name}' has unexpected hidden files: "
                f"{[f.name for f in hidden_files]}"
            )


class TestNoHardcodedPaths:
    """Tests to ensure no hardcoded personal paths exist."""

    def _is_grep_example(self, line: str) -> bool:
        """Check if line is a grep example showing what to search for."""
        return "grep" in line.lower() and ("\\|" in line or "-rn" in line)

    def test_no_hardcoded_home_paths_in_skills(
        self, all_command_files: list[Path]
    ) -> None:
        """Skills should not contain hardcoded home directory paths."""
        forbidden_patterns = [
            "~/Documents/GitHub/",
        ]

        for cmd_file in all_command_files:
            content = cmd_file.read_text()
            for pattern in forbidden_patterns:
                assert pattern not in content, (
                    f"Skill '{cmd_file.name}' contains hardcoded path '{pattern}'"
                )

    def test_no_hardcoded_home_paths_in_agents(
        self, all_agent_files: list[Path]
    ) -> None:
        """Agents should not contain hardcoded home directory paths."""
        forbidden_patterns = [
            "~/Documents/GitHub/",
        ]

        for agent_file in all_agent_files:
            content = agent_file.read_text()
            for pattern in forbidden_patterns:
                assert pattern not in content, (
                    f"Agent '{agent_file.name}' contains hardcoded path '{pattern}'"
                )
