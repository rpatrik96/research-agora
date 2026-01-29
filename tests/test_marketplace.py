"""
Tests for marketplace.json structure and validity.
"""

import json
from pathlib import Path
from typing import Any

import pytest


class TestMarketplaceStructure:
    """Tests for marketplace.json file structure."""

    def test_marketplace_exists(self, marketplace_path: Path) -> None:
        """Marketplace.json file must exist."""
        assert marketplace_path.exists(), f"marketplace.json not found at {marketplace_path}"

    def test_marketplace_is_valid_json(self, marketplace_path: Path) -> None:
        """Marketplace.json must be valid JSON."""
        try:
            with open(marketplace_path) as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"marketplace.json is not valid JSON: {e}")

    def test_marketplace_has_required_fields(
        self, marketplace_data: dict[str, Any], required_marketplace_fields: list[str]
    ) -> None:
        """Marketplace.json must have all required top-level fields."""
        for field in required_marketplace_fields:
            assert field in marketplace_data, f"Missing required field: {field}"

    def test_marketplace_name_is_string(self, marketplace_data: dict[str, Any]) -> None:
        """Marketplace name must be a non-empty string."""
        name = marketplace_data.get("name")
        assert isinstance(name, str), "Marketplace name must be a string"
        assert len(name) > 0, "Marketplace name cannot be empty"

    def test_marketplace_owner_structure(self, marketplace_data: dict[str, Any]) -> None:
        """Owner must have name and email fields."""
        owner = marketplace_data.get("owner", {})
        assert "name" in owner, "Owner must have 'name' field"
        assert "email" in owner, "Owner must have 'email' field"
        assert isinstance(owner["name"], str), "Owner name must be a string"
        assert isinstance(owner["email"], str), "Owner email must be a string"

    def test_marketplace_metadata_structure(self, marketplace_data: dict[str, Any]) -> None:
        """Metadata must have description and version fields."""
        metadata = marketplace_data.get("metadata", {})
        assert "description" in metadata, "Metadata must have 'description' field"
        assert "version" in metadata, "Metadata must have 'version' field"

    def test_marketplace_plugins_is_array(self, marketplace_data: dict[str, Any]) -> None:
        """Plugins must be a non-empty array."""
        plugins = marketplace_data.get("plugins")
        assert isinstance(plugins, list), "Plugins must be an array"
        assert len(plugins) > 0, "Plugins array cannot be empty"


class TestPluginEntries:
    """Tests for individual plugin entries in marketplace.json."""

    def test_all_plugins_have_required_fields(
        self, marketplace_plugins: list[dict[str, Any]], required_plugin_fields: list[str]
    ) -> None:
        """Each plugin must have all required fields."""
        for plugin in marketplace_plugins:
            plugin_name = plugin.get("name", "<unknown>")
            for field in required_plugin_fields:
                assert (
                    field in plugin
                ), f"Plugin '{plugin_name}' missing required field: {field}"

    def test_plugin_names_are_kebab_case(
        self, marketplace_plugins: list[dict[str, Any]]
    ) -> None:
        """Plugin names must be kebab-case."""
        import re

        kebab_pattern = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
        for plugin in marketplace_plugins:
            name = plugin.get("name", "")
            assert kebab_pattern.match(
                name
            ), f"Plugin name '{name}' is not kebab-case"

    def test_plugin_sources_exist(
        self, marketplace_plugins: list[dict[str, Any]], repo_root: Path
    ) -> None:
        """Plugin source directories must exist."""
        for plugin in marketplace_plugins:
            source = plugin.get("source", "")
            plugin_name = plugin.get("name", "<unknown>")
            if source.startswith("./"):
                source_path = repo_root / source[2:]
            else:
                source_path = repo_root / source
            assert source_path.exists(), f"Plugin '{plugin_name}' source not found: {source_path}"

    def test_plugin_categories_are_valid(
        self, marketplace_plugins: list[dict[str, Any]], valid_categories: list[str]
    ) -> None:
        """Plugin categories must be from the valid set."""
        for plugin in marketplace_plugins:
            category = plugin.get("category", "")
            plugin_name = plugin.get("name", "<unknown>")
            assert (
                category in valid_categories
            ), f"Plugin '{plugin_name}' has invalid category '{category}'. Valid: {valid_categories}"

    def test_plugin_versions_are_semver(
        self, marketplace_plugins: list[dict[str, Any]]
    ) -> None:
        """Plugin versions should follow semver format."""
        import re

        semver_pattern = re.compile(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$")
        for plugin in marketplace_plugins:
            version = plugin.get("version", "")
            plugin_name = plugin.get("name", "<unknown>")
            assert semver_pattern.match(
                version
            ), f"Plugin '{plugin_name}' version '{version}' is not semver format"

    def test_plugin_authors_have_name(
        self, marketplace_plugins: list[dict[str, Any]]
    ) -> None:
        """Plugin authors must have a name."""
        for plugin in marketplace_plugins:
            author = plugin.get("author", {})
            plugin_name = plugin.get("name", "<unknown>")
            assert "name" in author, f"Plugin '{plugin_name}' author missing 'name'"
            assert isinstance(
                author["name"], str
            ), f"Plugin '{plugin_name}' author name must be string"
            assert len(author["name"]) > 0, f"Plugin '{plugin_name}' author name is empty"

    def test_plugin_keywords_are_arrays(
        self, marketplace_plugins: list[dict[str, Any]]
    ) -> None:
        """Plugin keywords, if present, must be arrays of strings."""
        for plugin in marketplace_plugins:
            if "keywords" in plugin:
                keywords = plugin["keywords"]
                plugin_name = plugin.get("name", "<unknown>")
                assert isinstance(
                    keywords, list
                ), f"Plugin '{plugin_name}' keywords must be an array"
                for kw in keywords:
                    assert isinstance(
                        kw, str
                    ), f"Plugin '{plugin_name}' keywords must be strings"


class TestPluginUniqueness:
    """Tests for uniqueness constraints in marketplace.json."""

    def test_plugin_names_are_unique(
        self, marketplace_plugins: list[dict[str, Any]]
    ) -> None:
        """Plugin names must be unique."""
        names = [p.get("name", "") for p in marketplace_plugins]
        duplicates = [name for name in names if names.count(name) > 1]
        assert len(duplicates) == 0, f"Duplicate plugin names found: {set(duplicates)}"

    def test_plugin_sources_are_unique(
        self, marketplace_plugins: list[dict[str, Any]]
    ) -> None:
        """Plugin sources must be unique (no two plugins from same directory)."""
        sources = [p.get("source", "") for p in marketplace_plugins]
        duplicates = [src for src in sources if sources.count(src) > 1]
        assert len(duplicates) == 0, f"Duplicate plugin sources found: {set(duplicates)}"
