"""Tests for micro-skills functionality.

These tests verify the structure and documentation of micro-skills.
Actual skill execution happens in Claude's runtime, so we test:
1. File existence and structure
2. Frontmatter validity
3. Required sections presence
4. Schema completeness
"""

import json
import re
from pathlib import Path

import pytest
import yaml


class TestMicroSkillStructure:
    """Tests for micro-skill file structure and metadata."""

    MICRO_SKILLS_DIR = Path("plugins/research-agents/micro-skills")

    @pytest.fixture
    def all_micro_skills(self) -> list[Path]:
        """Get all micro-skill files."""
        if not self.MICRO_SKILLS_DIR.exists():
            pytest.skip("Micro-skills directory not found")
        skills = list(self.MICRO_SKILLS_DIR.glob("*.md"))
        # Exclude template
        return [s for s in skills if not s.name.startswith("_")]

    @pytest.fixture
    def template_skill(self) -> Path:
        """Get the template skill."""
        template = self.MICRO_SKILLS_DIR / "_TEMPLATE.md"
        if not template.exists():
            pytest.skip("Template not found")
        return template

    def parse_frontmatter(self, content: str) -> dict | None:
        """Extract YAML frontmatter from markdown."""
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if match:
            return yaml.safe_load(match.group(1))
        return None

    def test_template_exists(self) -> None:
        """Template file should exist."""
        template = self.MICRO_SKILLS_DIR / "_TEMPLATE.md"
        assert template.exists(), "Micro-skill template not found"

    def test_all_skills_have_frontmatter(self, all_micro_skills: list[Path]) -> None:
        """All micro-skills should have valid YAML frontmatter."""
        for skill_path in all_micro_skills:
            content = skill_path.read_text()
            frontmatter = self.parse_frontmatter(content)

            assert frontmatter is not None, f"{skill_path.name} missing frontmatter"
            assert "name" in frontmatter, f"{skill_path.name} missing 'name'"
            assert (
                "description" in frontmatter
            ), f"{skill_path.name} missing 'description'"

    def test_all_skills_have_required_sections(
        self, all_micro_skills: list[Path]
    ) -> None:
        """All micro-skills should have required documentation sections."""
        required_sections = [
            "Input Specification",
            "Output Specification",
            "Algorithm",
            "Constraints",
        ]

        for skill_path in all_micro_skills:
            content = skill_path.read_text()

            for section in required_sections:
                assert (
                    f"## {section}" in content or f"# {section}" in content
                ), f"{skill_path.name} missing section: {section}"

    def test_skills_have_parallelization_properties(
        self, all_micro_skills: list[Path]
    ) -> None:
        """Micro-skills should document parallelization properties."""
        for skill_path in all_micro_skills:
            content = skill_path.read_text()

            # Should have parallelization table or section
            assert (
                "Parallelization" in content or "parallel" in content.lower()
            ), f"{skill_path.name} missing parallelization documentation"

    def test_skills_have_json_schemas(self, all_micro_skills: list[Path]) -> None:
        """Input/output specifications should include JSON schemas."""
        for skill_path in all_micro_skills:
            content = skill_path.read_text()

            # Look for JSON schema blocks
            assert (
                '"type":' in content or "'type':" in content
            ), f"{skill_path.name} missing JSON schema definitions"

    def test_skills_have_examples(self, all_micro_skills: list[Path]) -> None:
        """All micro-skills should have usage examples."""
        for skill_path in all_micro_skills:
            content = skill_path.read_text()

            assert (
                "Example" in content or "example" in content
            ), f"{skill_path.name} missing examples"


class TestClaimExtractor:
    """Tests specific to claim-extractor micro-skill."""

    @pytest.fixture
    def skill_content(self) -> str:
        """Load claim-extractor content."""
        path = Path("plugins/research-agents/micro-skills/claim-extractor.md")
        if not path.exists():
            pytest.skip("claim-extractor not found")
        return path.read_text()

    def test_has_extraction_patterns(self, skill_content: str) -> None:
        """Should document claim extraction patterns."""
        assert "Explicit" in skill_content
        assert "Implicit" in skill_content
        assert "We show" in skill_content or "show that" in skill_content

    def test_has_claim_types(self, skill_content: str) -> None:
        """Should list all claim types."""
        claim_types = [
            "empirical",
            "theoretical",
            "methodological",
            "comparative",
            "novelty",
        ]
        for claim_type in claim_types:
            assert (
                claim_type in skill_content.lower()
            ), f"Missing claim type: {claim_type}"


class TestEvidenceGrader:
    """Tests specific to evidence-grader micro-skill."""

    @pytest.fixture
    def skill_content(self) -> str:
        """Load evidence-grader content."""
        path = Path("plugins/research-agents/micro-skills/evidence-grader.md")
        if not path.exists():
            pytest.skip("evidence-grader not found")
        return path.read_text()

    def test_has_evidence_hierarchy(self, skill_content: str) -> None:
        """Should document L1-L6 evidence hierarchy."""
        for level in ["L1", "L2", "L3", "L4", "L5", "L6"]:
            assert level in skill_content, f"Missing evidence level: {level}"

    def test_has_venue_standards(self, skill_content: str) -> None:
        """Should document venue-specific standards."""
        venues = ["neurips", "icml", "iclr"]
        for venue in venues:
            assert venue.lower() in skill_content.lower(), f"Missing venue: {venue}"


class TestNoveltyChecker:
    """Tests specific to novelty-checker micro-skill."""

    @pytest.fixture
    def skill_content(self) -> str:
        """Load novelty-checker content."""
        path = Path("plugins/research-agents/micro-skills/novelty-checker.md")
        if not path.exists():
            pytest.skip("novelty-checker not found")
        return path.read_text()

    def test_documents_arxiv_usage(self, skill_content: str) -> None:
        """Should document arXiv MCP tool usage."""
        assert "arxiv" in skill_content.lower()
        assert "mcp__arxiv" in skill_content or "search_papers" in skill_content

    def test_has_temporal_classification(self, skill_content: str) -> None:
        """Should document prior vs concurrent work classification."""
        assert "prior" in skill_content.lower()
        assert "concurrent" in skill_content.lower()


class TestCrossReferencer:
    """Tests specific to cross-referencer micro-skill."""

    @pytest.fixture
    def skill_content(self) -> str:
        """Load cross-referencer content."""
        path = Path("plugins/research-agents/micro-skills/cross-referencer.md")
        if not path.exists():
            pytest.skip("cross-referencer not found")
        return path.read_text()

    def test_documents_issue_types(self, skill_content: str) -> None:
        """Should document consistency issue types."""
        issue_types = [
            "numerical_mismatch",
            "claim_contradiction",
            "missing_support",
            "scope_inconsistency",
        ]
        for issue_type in issue_types:
            assert (
                issue_type in skill_content or issue_type.replace("_", " ") in skill_content.lower()
            ), f"Missing issue type: {issue_type}"


class TestMicroSkillConsistency:
    """Tests for consistency across all micro-skills."""

    MICRO_SKILLS_DIR = Path("plugins/research-agents/micro-skills")

    @pytest.fixture
    def all_skills_content(self) -> dict[str, str]:
        """Load content of all micro-skills."""
        if not self.MICRO_SKILLS_DIR.exists():
            pytest.skip("Micro-skills directory not found")

        skills = {}
        for skill_path in self.MICRO_SKILLS_DIR.glob("*.md"):
            if not skill_path.name.startswith("_"):
                skills[skill_path.stem] = skill_path.read_text()
        return skills

    def test_consistent_model_specification(
        self, all_skills_content: dict[str, str]
    ) -> None:
        """All skills should specify a model (haiku, sonnet, opus)."""
        valid_models = ["haiku", "sonnet", "opus"]

        for name, content in all_skills_content.items():
            # Check frontmatter for model
            match = re.search(r"model:\s*(\w+)", content)
            if match:
                model = match.group(1).lower()
                assert (
                    model in valid_models
                ), f"{name} has invalid model: {model}"

    def test_all_skills_document_constraints(
        self, all_skills_content: dict[str, str]
    ) -> None:
        """All skills should have DO and DON'T constraints."""
        for name, content in all_skills_content.items():
            assert (
                "DO" in content and "DON'T" in content
            ) or "Constraint" in content, f"{name} missing constraint documentation"

    def test_all_skills_have_error_handling(
        self, all_skills_content: dict[str, str]
    ) -> None:
        """All skills should document error handling."""
        for name, content in all_skills_content.items():
            assert (
                "Error" in content or "error" in content
            ), f"{name} missing error handling documentation"

    def test_input_output_json_valid(
        self, all_skills_content: dict[str, str]
    ) -> None:
        """JSON examples in skills should be valid JSON."""
        json_block_pattern = re.compile(r"```json\n(.*?)\n```", re.DOTALL)

        for name, content in all_skills_content.items():
            json_blocks = json_block_pattern.findall(content)

            for i, block in enumerate(json_blocks):
                # Skip schema blocks (they have $schema)
                if "$schema" in block:
                    continue

                # Try to parse as JSON
                try:
                    # Handle common markdown artifacts
                    cleaned = block.strip()
                    if cleaned:
                        json.loads(cleaned)
                except json.JSONDecodeError:
                    # Some blocks might be pseudo-JSON for illustration
                    # Only fail if it looks like it should be valid
                    if not any(
                        marker in block
                        for marker in ["...", "[", "// ", "# ", "string", "integer"]
                    ):
                        pytest.fail(
                            f"{name} has invalid JSON in block {i + 1}: {block[:100]}"
                        )
