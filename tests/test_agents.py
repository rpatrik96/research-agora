"""
Tests for agent validation - markdown files with YAML frontmatter.
"""

import re
from pathlib import Path
from typing import Any

import pytest
from conftest import parse_yaml_frontmatter


class TestAgentDirectoryStructure:
    """Tests for agent directory structure."""

    def test_agents_directory_exists(self, agents_dir: Path) -> None:
        """Agents directory must exist."""
        assert agents_dir.exists(), f"Agents directory not found at {agents_dir}"

    def test_agents_directory_has_files(self, all_agent_files: list[Path]) -> None:
        """Agents directory should contain markdown files."""
        assert len(all_agent_files) > 0, "No agent files found in agents directory"

    def test_agent_files_are_markdown(self, all_agent_files: list[Path]) -> None:
        """All agent files must be markdown files."""
        for agent_file in all_agent_files:
            assert agent_file.suffix == ".md", f"Agent file must be .md: {agent_file.name}"


class TestAgentFrontmatter:
    """Tests for agent YAML frontmatter."""

    def test_agents_have_frontmatter(self, all_agent_files: list[Path]) -> None:
        """Each agent file must have YAML frontmatter."""
        for agent_file in all_agent_files:
            frontmatter = parse_yaml_frontmatter(agent_file)
            assert (
                frontmatter is not None
            ), f"{agent_file.name} missing YAML frontmatter"

    def test_agents_have_required_fields(
        self, all_agent_files: list[Path], required_agent_frontmatter_fields: list[str]
    ) -> None:
        """Agent frontmatter must have required fields."""
        for agent_file in all_agent_files:
            frontmatter = parse_yaml_frontmatter(agent_file)

            if frontmatter is None:
                pytest.fail(f"{agent_file.name} has no frontmatter")

            for field in required_agent_frontmatter_fields:
                assert (
                    field in frontmatter
                ), f"{agent_file.name} frontmatter missing: {field}"

    def test_agent_name_matches_filename(self, all_agent_files: list[Path]) -> None:
        """Agent frontmatter name must match filename (without .md)."""
        for agent_file in all_agent_files:
            frontmatter = parse_yaml_frontmatter(agent_file)

            if frontmatter is None:
                continue

            expected_name = agent_file.stem  # filename without .md
            actual_name = frontmatter.get("name", "")
            assert (
                actual_name == expected_name
            ), f"Name mismatch in {agent_file.name}: frontmatter says '{actual_name}', expected '{expected_name}'"

    def test_agent_name_is_kebab_case(self, all_agent_files: list[Path]) -> None:
        """Agent names must be kebab-case."""
        kebab_pattern = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

        for agent_file in all_agent_files:
            frontmatter = parse_yaml_frontmatter(agent_file)

            if frontmatter is None:
                continue

            name = frontmatter.get("name", "")
            assert kebab_pattern.match(
                name
            ), f"Agent name '{name}' in {agent_file.name} is not kebab-case"

    def test_agent_description_not_empty(self, all_agent_files: list[Path]) -> None:
        """Agent frontmatter description must not be empty."""
        for agent_file in all_agent_files:
            frontmatter = parse_yaml_frontmatter(agent_file)

            if frontmatter is None:
                continue

            description = frontmatter.get("description", "")
            assert (
                len(str(description).strip()) > 0
            ), f"{agent_file.name} has empty description"

    def test_agent_model_if_present_is_valid(self, all_agent_files: list[Path]) -> None:
        """If model is specified, it must be a valid model name."""
        valid_models = ["haiku", "sonnet", "opus"]

        for agent_file in all_agent_files:
            frontmatter = parse_yaml_frontmatter(agent_file)

            if frontmatter is None:
                continue

            if "model" in frontmatter:
                model = frontmatter["model"]
                assert (
                    model in valid_models
                ), f"{agent_file.name} has invalid model '{model}'. Valid: {valid_models}"


class TestAgentContent:
    """Tests for agent file content."""

    def test_agents_have_content_beyond_frontmatter(
        self, all_agent_files: list[Path]
    ) -> None:
        """Agent files must have content beyond just frontmatter."""
        for agent_file in all_agent_files:
            content = agent_file.read_text()

            # Remove frontmatter
            content_without_frontmatter = re.sub(
                r"^---\s*\n.*?\n---\s*\n", "", content, flags=re.DOTALL
            )

            assert (
                len(content_without_frontmatter.strip()) > 50
            ), f"{agent_file.name} has insufficient content beyond frontmatter"

    def test_agents_are_not_too_short(self, all_agent_files: list[Path]) -> None:
        """Agent files should have substantial content (at least 20 lines)."""
        min_lines = 20

        for agent_file in all_agent_files:
            content = agent_file.read_text()
            lines = content.strip().split("\n")
            assert len(lines) >= min_lines, (
                f"{agent_file.name} is too short ({len(lines)} lines). "
                f"Agents should have at least {min_lines} lines."
            )


class TestAgentMarketplaceConsistency:
    """Tests for consistency between agents and marketplace."""

    def test_research_agents_plugin_exists(
        self, agent_plugins: list[dict[str, Any]]
    ) -> None:
        """research-agents plugin should exist in marketplace."""
        assert len(agent_plugins) == 1, "Expected exactly one research-agents plugin"
        assert agent_plugins[0].get("name") == "research-agents"

    def test_research_agents_has_research_category(
        self, agent_plugins: list[dict[str, Any]]
    ) -> None:
        """research-agents plugin should have 'research' category."""
        for plugin in agent_plugins:
            category = plugin.get("category", "")
            assert category == "research", (
                f"research-agents plugin has category '{category}'. "
                f"Expected 'research'."
            )

    def test_research_agents_has_agents_keyword(
        self, agent_plugins: list[dict[str, Any]]
    ) -> None:
        """research-agents plugin should have 'agents' in keywords."""
        for plugin in agent_plugins:
            keywords = plugin.get("keywords", [])
            assert "agents" in keywords, (
                "research-agents plugin should have 'agents' keyword"
            )
