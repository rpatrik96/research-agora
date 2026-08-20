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
        """All category values must be non-empty lists (except 'groups' which is a dict)."""
        for key, values in categories_data.items():
            if key == "groups":
                assert isinstance(values, dict), f"{key} must be a dict"
                assert len(values) > 0, f"{key} must not be empty"
            else:
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


class TestVisibility:
    """Tests for skill visibility field."""

    def test_all_skills_have_visibility(self, registry_skills: list) -> None:
        """Every skill must have a visibility field."""
        for skill in registry_skills:
            assert "visibility" in skill, (
                f"Skill '{skill['name']}' missing visibility field"
            )

    def test_visibility_values_are_valid(self, registry_skills: list) -> None:
        """Visibility must be 'public' or 'internal'."""
        valid = {"public", "internal"}
        for skill in registry_skills:
            assert skill["visibility"] in valid, (
                f"Skill '{skill['name']}' has invalid visibility: {skill['visibility']}"
            )

    def test_public_skills_count(self, registry_skills: list) -> None:
        """There should be more public skills than internal ones."""
        public = [s for s in registry_skills if s["visibility"] == "public"]
        internal = [s for s in registry_skills if s["visibility"] == "internal"]
        assert len(public) > len(internal), (
            f"Expected more public ({len(public)}) than internal ({len(internal)}) skills"
        )

    def test_internal_skills_are_building_blocks(self, registry_skills: list) -> None:
        """Internal skills should be micro-skills, helpers, orchestrators, or internal agents."""
        building_block_types = {"micro-skill", "helper", "orchestrator"}
        for skill in registry_skills:
            if skill["visibility"] == "internal":
                is_building_block = skill["type"] in building_block_types
                is_state_generator = skill["name"] == "state-generator"
                assert is_building_block or is_state_generator, (
                    f"Internal skill '{skill['name']}' has unexpected type '{skill['type']}'"
                )

    def test_public_skills_stats_match(self, registry_data: dict, registry_skills: list) -> None:
        """Registry stats.public_skills must match actual public skill count."""
        public_count = sum(1 for s in registry_skills if s["visibility"] == "public")
        assert registry_data["stats"]["public_skills"] == public_count


class TestGroupsTaxonomy:
    """Tests for the groups taxonomy in categories.json."""

    def test_groups_key_exists(self, categories_data: dict) -> None:
        """categories.json must have a 'groups' key."""
        assert "groups" in categories_data

    def test_groups_have_required_fields(self, categories_data: dict) -> None:
        """Each group must have label, description, and icon."""
        groups = categories_data.get("groups", {})
        for group_id, group_meta in groups.items():
            assert "label" in group_meta, f"Group '{group_id}' missing 'label'"
            assert "description" in group_meta, f"Group '{group_id}' missing 'description'"
            assert "icon" in group_meta, f"Group '{group_id}' missing 'icon'"

    def test_groups_labels_are_nonempty(self, categories_data: dict) -> None:
        """Group labels must be non-empty strings."""
        groups = categories_data.get("groups", {})
        for group_id, group_meta in groups.items():
            assert isinstance(group_meta["label"], str) and len(group_meta["label"]) > 0, (
                f"Group '{group_id}' has empty or non-string label"
            )

    def test_groups_are_exactly_the_plugins(
        self, categories_data: dict, registry_data: dict
    ) -> None:
        """Browse groups and plugins are the same set (RFC-0002).

        Groups derive from plugin membership, so a group that is not a plugin
        would render empty and a plugin that is not a group would render its
        skills as ungrouped.
        """
        groups = set(categories_data.get("groups", {}).keys())
        plugins = {
            s["plugin"]
            for repo in registry_data.get("repos", [])
            for s in repo.get("skills", [])
        }
        assert groups == plugins, (
            f"groups {sorted(groups)} != plugins {sorted(plugins)}"
        )


class TestGroupDerivation:
    """Groups derive from plugin membership; there is no mapping table.

    RFC-0002 replaced the hand-maintained SKILL_GROUP_MAP with derivation. The
    table was the surface that let the February 2026 consolidation leave 34
    dangling references behind, because a retired skill's entry survived it.
    """

    @staticmethod
    def _site_module():
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "generate_site", REPO_ROOT / "scripts" / "generate-site.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_no_hand_maintained_group_map(self) -> None:
        """The mapping table must stay gone."""
        mod = self._site_module()
        assert not hasattr(mod, "SKILL_GROUP_MAP"), (
            "SKILL_GROUP_MAP is back; groups must derive from plugin membership"
        )

    def test_every_public_skill_lands_in_a_group(self, registry_skills: list) -> None:
        mod = self._site_module()
        public = [s for s in registry_skills if s.get("visibility", "public") == "public"]
        unplaced = [
            s["name"] for s in public if mod.skill_group(s) not in mod.GROUP_ORDER
        ]
        assert not unplaced, f"Public skills outside GROUP_ORDER: {unplaced}"

    def test_every_skill_lands_in_a_verification_band(
        self, registry_skills: list
    ) -> None:
        mod = self._site_module()
        band_ids = {b[0] for b in mod.VERIFICATION_BANDS}
        unbanded = [s["name"] for s in registry_skills if mod.skill_band(s) not in band_ids]
        assert not unbanded, f"Skills with no verification band: {unbanded}"

    def test_bands_cover_every_verification_level(self, categories_data: dict) -> None:
        """No level may fall through to the default band silently."""
        mod = self._site_module()
        covered = set()
        for _bid, _label, _blurb, levels in mod.VERIFICATION_BANDS:
            covered |= levels
        declared = set(categories_data["verification-levels"])
        assert declared <= covered, f"Levels with no band: {sorted(declared - covered)}"


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


class TestAdvertisedCounts:
    """The advertised skill count drifted to four different numbers across nine
    files (61 / 74 / 80+ / 83) before anyone noticed, because every one of them
    was hand-typed. registry/index.json stats is the only source of truth, and
    these tests fail when a public claim stops matching it.
    """

    # CHANGELOG records what was true at each release and RFCs record what was
    # true when the decision was made. Their counts are history; rewriting them
    # to match today would falsify the record.
    EXEMPT = {"CHANGELOG.md"}
    EXEMPT_PREFIXES = ("docs/rfcs/",)

    def _public_count(self, registry_data: dict) -> int:
        """What the marketplace advertises: public and not deprecated."""
        return registry_data["stats"]["active_public_skills"]

    def test_readme_badge_matches_registry(self, registry_data: dict) -> None:
        """The README badge must match registry stats."""
        import re

        readme = (REPO_ROOT / "README.md").read_text()
        m = re.search(r"badge/skills-(\d+)", readme)
        assert m, "README skills badge not found"
        assert int(m.group(1)) == self._public_count(registry_data), (
            f"README badge says {m.group(1)} public skills; "
            f"registry says {self._public_count(registry_data)}"
        )

    def test_no_stale_skill_counts_in_tracked_markdown(
        self, registry_data: dict
    ) -> None:
        """Any '<N> [public] skills' claim in tracked docs must match the registry."""
        import re
        import subprocess

        public = self._public_count(registry_data)
        total = registry_data["stats"]["total_skills"]
        allowed = {public, total, registry_data["stats"]["public_skills"]}

        tracked = subprocess.run(
            ["git", "ls-files", "*.md"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()

        pattern = re.compile(r"\b(\d{2,3})\+?\s+(?:public\s+)?(?:AI\s+)?skills\b")
        stale = []
        for rel in tracked:
            if rel in self.EXEMPT or rel.startswith(self.EXEMPT_PREFIXES):
                continue
            for line_no, line in enumerate(
                (REPO_ROOT / rel).read_text().splitlines(), 1
            ):
                for found in pattern.findall(line):
                    if int(found) not in allowed:
                        stale.append(f"{rel}:{line_no} claims {found} skills")

        assert not stale, (
            f"Stale skill counts (registry: {public} public / {total} total):\n"
            + "\n".join(stale)
        )

    def test_plugin_count_matches_marketplace(self, registry_data: dict) -> None:
        """registry plugin count must match the marketplace manifest."""
        import json

        manifest = json.loads(
            (REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text()
        )
        assert len(manifest["plugins"]) == registry_data["stats"]["plugins"], (
            f"marketplace.json lists {len(manifest['plugins'])} plugins; "
            f"registry says {registry_data['stats']['plugins']}"
        )


class TestRecommendationSurfacesAreLive:
    """No surface may recommend a skill that does not exist.

    Four hand-maintained tables recommend skills to users: scripts/onboard.py,
    the two onboard resources, and the standalone browser quiz. Each has drifted
    at least once — the 1.2.0 cut left `/openreview-submission` in three of them
    and `/choose-skill` in the fourth, so a new user's first recommendation was
    a command that no longer resolved. The registry is the catalog; these check
    against it.
    """

    SURFACES = [
        "scripts/onboard.py",
        "plugins/discover/resources/onboard-profiles.json",
        "plugins/discover/resources/onboard-reference.md",
        "site/static/onboard.html",
        "plugins/discover/commands/navigator.md",
    ]

    # Slash commands that belong to Claude Code or the user, not the catalog.
    NOT_OURS = {"plugin", "clear", "model", "compact", "init", "help", "onboard"}

    # Documentation shows what a contributed skill would look like. These are
    # illustrations, not recommendations.
    PLACEHOLDER = ("skill-name", "new-skill", "improved-skill", "affected-skill",
                   "your-skill", "example-skill")

    def test_every_recommended_skill_exists(self, registry_skills: list) -> None:
        import re

        live = {s["name"] for s in registry_skills} | self.NOT_OURS
        dead = []
        for rel in self.SURFACES:
            path = REPO_ROOT / rel
            if not path.exists():
                continue
            in_fence = False
            for line_no, line in enumerate(path.read_text().splitlines(), 1):
                if line.lstrip().startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                for name in re.findall(r'["\'`/]/([a-z][a-z0-9-]{2,})["\'`\s,\]|]', line):
                    if any(ph in name for ph in self.PLACEHOLDER):
                        continue
                    if name not in live:
                        dead.append(f"{rel}:{line_no} recommends /{name}")
        assert not dead, "Recommendation surfaces name retired skills:\n" + "\n".join(
            dict.fromkeys(dead)
        )
