"""
Tests for registry index and categories validation.
"""

import json
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).parent.parent
REGISTRY_DIR = REPO_ROOT / "registry"


@pytest.fixture(scope="session")
def categories_data() -> dict[str, Any]:
    """Load registry/categories.json."""
    cat_path = REGISTRY_DIR / "categories.json"
    if not cat_path.exists():
        pytest.skip("registry/categories.json not found")
    with open(cat_path) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def registry_data() -> dict[str, Any]:
    """Load registry/index.json."""
    index_path = REGISTRY_DIR / "index.json"
    if not index_path.exists():
        pytest.skip("registry/index.json not found — run scripts/generate-registry.py first")
    with open(index_path) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def registry_skills(registry_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract all skills from the registry index."""
    skills = []
    for repo in registry_data.get("repos", []):
        skills.extend(repo.get("skills", []))
    return skills


class TestCategoriesJson:
    """Tests for registry/categories.json schema."""

    def test_categories_file_exists(self) -> None:
        """categories.json must exist."""
        assert (REGISTRY_DIR / "categories.json").exists()

    def test_categories_is_valid_json(self) -> None:
        """categories.json must be valid JSON."""
        with open(REGISTRY_DIR / "categories.json") as f:
            json.load(f)

    def test_categories_has_required_keys(self, categories_data: dict) -> None:
        """categories.json must have all taxonomy dimensions."""
        required = ["research-domains", "task-types", "research-phases", "verification-levels"]
        for key in required:
            assert key in categories_data, f"Missing key in categories.json: {key}"

    def test_categories_values_are_lists(self, categories_data: dict) -> None:
        """All category values must be non-empty lists."""
        for key, values in categories_data.items():
            assert isinstance(values, list), f"{key} must be a list"
            assert len(values) > 0, f"{key} must not be empty"

    def test_categories_values_are_strings(self, categories_data: dict) -> None:
        """All category list items must be strings."""
        for key, values in categories_data.items():
            for v in values:
                assert isinstance(v, str), f"{key} contains non-string: {v}"

    def test_categories_no_duplicates(self, categories_data: dict) -> None:
        """Category values must not have duplicates."""
        for key, values in categories_data.items():
            assert len(values) == len(set(values)), f"Duplicates in {key}"

    def test_verification_levels_complete(self, categories_data: dict) -> None:
        """Verification levels must include the four standard levels."""
        expected = {"formal", "heuristic", "layered", "none"}
        actual = set(categories_data.get("verification-levels", []))
        assert expected == actual, f"Expected {expected}, got {actual}"


class TestRegistryIndex:
    """Tests for registry/index.json schema."""

    def test_registry_has_version(self, registry_data: dict) -> None:
        """Registry must have a version field."""
        assert "version" in registry_data

    def test_registry_has_generated_date(self, registry_data: dict) -> None:
        """Registry must have a generated date."""
        assert "generated" in registry_data

    def test_registry_has_stats(self, registry_data: dict) -> None:
        """Registry must have stats."""
        assert "stats" in registry_data
        stats = registry_data["stats"]
        assert "total_skills" in stats
        assert stats["total_skills"] > 0

    def test_registry_has_repos(self, registry_data: dict) -> None:
        """Registry must have repos array."""
        assert "repos" in registry_data
        assert isinstance(registry_data["repos"], list)
        assert len(registry_data["repos"]) > 0

    def test_registry_repo_has_required_fields(self, registry_data: dict) -> None:
        """Each repo entry must have required fields."""
        for repo in registry_data["repos"]:
            assert "repo" in repo, "Repo entry missing 'repo' field"
            assert "description" in repo, "Repo entry missing 'description'"
            assert "skills" in repo, "Repo entry missing 'skills'"

    def test_registry_skill_count_matches_stats(
        self, registry_data: dict, registry_skills: list
    ) -> None:
        """Stats total must match actual skill count."""
        assert registry_data["stats"]["total_skills"] == len(registry_skills)


class TestRegistrySkills:
    """Tests for individual skill entries in the registry."""

    def test_skills_have_required_fields(self, registry_skills: list) -> None:
        """Each skill must have required fields."""
        required = ["name", "plugin", "type", "description", "model", "path"]
        for skill in registry_skills:
            for field in required:
                assert field in skill, f"Skill '{skill.get('name', '?')}' missing '{field}'"

    def test_skill_names_are_unique(self, registry_skills: list) -> None:
        """Skill names should be unique within a plugin."""
        seen = set()
        duplicates = []
        for skill in registry_skills:
            key = f"{skill['plugin']}/{skill['name']}"
            if key in seen:
                duplicates.append(key)
            seen.add(key)
        assert len(duplicates) == 0, f"Duplicate skills: {duplicates}"

    def test_skill_paths_exist(self, registry_skills: list) -> None:
        """Skill paths in the registry must point to actual files."""
        for skill in registry_skills:
            path = REPO_ROOT / skill["path"]
            assert path.exists(), f"Skill '{skill['name']}' path not found: {skill['path']}"

    def test_skill_types_are_valid(self, registry_skills: list) -> None:
        """Skill types must be one of the valid types."""
        valid_types = {"command", "agent", "micro-skill", "orchestrator", "helper"}
        for skill in registry_skills:
            assert skill["type"] in valid_types, (
                f"Skill '{skill['name']}' has invalid type: {skill['type']}"
            )

    def test_skill_models_are_valid(self, registry_skills: list) -> None:
        """Skill models must be valid model tiers."""
        valid_models = {"opus", "sonnet", "haiku"}
        for skill in registry_skills:
            assert skill["model"] in valid_models, (
                f"Skill '{skill['name']}' has invalid model: {skill['model']}"
            )

    def test_skill_metadata_domains_valid(
        self, registry_skills: list, categories_data: dict
    ) -> None:
        """Skill research-domain must be from categories.json."""
        valid = set(categories_data["research-domains"])
        for skill in registry_skills:
            domain = skill.get("research-domain", "")
            if domain:
                assert domain in valid, (
                    f"Skill '{skill['name']}' has invalid domain: {domain}"
                )

    def test_skill_metadata_task_types_valid(
        self, registry_skills: list, categories_data: dict
    ) -> None:
        """Skill task-type must be from categories.json."""
        valid = set(categories_data["task-types"])
        for skill in registry_skills:
            task_type = skill.get("task-type", "")
            if task_type:
                assert task_type in valid, (
                    f"Skill '{skill['name']}' has invalid task-type: {task_type}"
                )

    def test_skill_metadata_phases_valid(
        self, registry_skills: list, categories_data: dict
    ) -> None:
        """Skill research-phase must be from categories.json."""
        valid = set(categories_data["research-phases"])
        for skill in registry_skills:
            phase = skill.get("research-phase", "")
            if phase:
                assert phase in valid, (
                    f"Skill '{skill['name']}' has invalid phase: {phase}"
                )

    def test_skill_metadata_verification_valid(
        self, registry_skills: list, categories_data: dict
    ) -> None:
        """Skill verification-level must be from categories.json."""
        valid = set(categories_data["verification-levels"])
        for skill in registry_skills:
            level = skill.get("verification-level", "")
            if level:
                assert level in valid, (
                    f"Skill '{skill['name']}' has invalid verification-level: {level}"
                )


class TestRegistryMatchesDisk:
    """Tests that registry index matches actual files on disk."""

    def test_all_commands_in_registry(
        self, registry_skills: list, all_command_files: list[Path]
    ) -> None:
        """All command files on disk should appear in the registry."""
        registry_paths = {s["path"] for s in registry_skills}
        missing = []
        for cmd_file in all_command_files:
            rel_path = str(cmd_file.relative_to(REPO_ROOT))
            if rel_path not in registry_paths:
                missing.append(rel_path)
        assert len(missing) == 0, f"Commands on disk but not in registry: {missing}"

    def test_all_agents_in_registry(
        self, registry_skills: list, all_agent_files: list[Path]
    ) -> None:
        """All agent files on disk should appear in the registry."""
        registry_paths = {s["path"] for s in registry_skills}
        missing = []
        for agent_file in all_agent_files:
            rel_path = str(agent_file.relative_to(REPO_ROOT))
            if rel_path not in registry_paths:
                missing.append(rel_path)
        assert len(missing) == 0, f"Agents on disk but not in registry: {missing}"
