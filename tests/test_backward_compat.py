"""
Tests for backward compatibility after parallel mode additions.

Ensures that existing agent interfaces still work after the parallel mode
enhancements to claim-auditor.md and evidence-checker.md.
"""

import re
from pathlib import Path
from typing import Any

import pytest
from conftest import REPO_ROOT, parse_yaml_frontmatter


class TestClaimAuditorBackwardCompatibility:
    """Backward compatibility tests for claim-auditor.md agent."""

    @pytest.fixture
    def claim_auditor_path(self) -> Path:
        """Return path to claim-auditor.md."""
        return REPO_ROOT / "plugins" / "research-agents" / "agents" / "claim-auditor.md"

    @pytest.fixture
    def claim_auditor_content(self, claim_auditor_path: Path) -> str:
        """Return claim-auditor.md content."""
        return claim_auditor_path.read_text()

    @pytest.fixture
    def claim_auditor_frontmatter(self, claim_auditor_path: Path) -> dict[str, Any]:
        """Return claim-auditor.md frontmatter."""
        frontmatter = parse_yaml_frontmatter(claim_auditor_path)
        assert frontmatter is not None, "claim-auditor.md missing frontmatter"
        return frontmatter

    def test_has_required_frontmatter_name(
        self, claim_auditor_frontmatter: dict[str, Any]
    ) -> None:
        """claim-auditor.md must have 'name' field in frontmatter."""
        assert "name" in claim_auditor_frontmatter
        assert claim_auditor_frontmatter["name"] == "claim-auditor"

    def test_has_required_frontmatter_description(
        self, claim_auditor_frontmatter: dict[str, Any]
    ) -> None:
        """claim-auditor.md must have 'description' field in frontmatter."""
        assert "description" in claim_auditor_frontmatter
        description = str(claim_auditor_frontmatter["description"])
        assert len(description.strip()) > 0

    def test_has_required_frontmatter_model(
        self, claim_auditor_frontmatter: dict[str, Any]
    ) -> None:
        """claim-auditor.md must have 'model' field in frontmatter."""
        assert "model" in claim_auditor_frontmatter
        assert claim_auditor_frontmatter["model"] in ["haiku", "sonnet", "opus"]

    def test_has_required_frontmatter_color(
        self, claim_auditor_frontmatter: dict[str, Any]
    ) -> None:
        """claim-auditor.md must have 'color' field in frontmatter."""
        assert "color" in claim_auditor_frontmatter
        assert len(str(claim_auditor_frontmatter["color"]).strip()) > 0

    def test_documents_sequential_workflow(
        self, claim_auditor_content: str
    ) -> None:
        """claim-auditor.md must document the original sequential workflow."""
        # Check for sequential mode section
        assert "Sequential Mode" in claim_auditor_content or "SEQUENTIAL MODE" in claim_auditor_content, (
            "claim-auditor.md must document Sequential Mode (original workflow)"
        )

    def test_has_workflow_section(self, claim_auditor_content: str) -> None:
        """claim-auditor.md must have WORKFLOW section with original steps."""
        assert "## WORKFLOW" in claim_auditor_content, (
            "claim-auditor.md must have ## WORKFLOW section"
        )
        # Verify key workflow steps are present
        workflow_steps = [
            "Gather Context",
            "Extract All Claims",
            "Classify Claims",
            "Map Evidence Sources",
            "Grade Evidence Level",
        ]
        for step in workflow_steps:
            assert step in claim_auditor_content, (
                f"claim-auditor.md WORKFLOW missing step: {step}"
            )

    def test_has_claim_types_section(self, claim_auditor_content: str) -> None:
        """claim-auditor.md must have CLAIM TYPES section."""
        assert "## CLAIM TYPES" in claim_auditor_content, (
            "claim-auditor.md must have ## CLAIM TYPES section"
        )
        # Verify key claim types
        claim_types = ["Empirical", "Methodological", "Comparative", "Theoretical", "Novelty"]
        for claim_type in claim_types:
            assert claim_type in claim_auditor_content, (
                f"claim-auditor.md CLAIM TYPES missing: {claim_type}"
            )

    def test_has_evidence_hierarchy_section(self, claim_auditor_content: str) -> None:
        """claim-auditor.md must have EVIDENCE HIERARCHY section."""
        assert "## EVIDENCE HIERARCHY" in claim_auditor_content, (
            "claim-auditor.md must have ## EVIDENCE HIERARCHY section"
        )
        # Verify evidence levels L1-L6
        for level in range(1, 7):
            assert f"L{level}" in claim_auditor_content, (
                f"claim-auditor.md EVIDENCE HIERARCHY missing level L{level}"
            )

    def test_has_output_format_section(self, claim_auditor_content: str) -> None:
        """claim-auditor.md must have OUTPUT FORMAT section."""
        assert "## OUTPUT FORMAT" in claim_auditor_content, (
            "claim-auditor.md must have ## OUTPUT FORMAT section"
        )
        # Verify key output format elements
        output_elements = [
            "Claim Audit Report",
            "Executive Summary",
            "Critical Issues",
            "Claim-by-Claim Analysis",
        ]
        for element in output_elements:
            assert element in claim_auditor_content, (
                f"claim-auditor.md OUTPUT FORMAT missing: {element}"
            )

    def test_has_mcp_integration_section(self, claim_auditor_content: str) -> None:
        """claim-auditor.md must preserve MCP INTEGRATION section."""
        assert "## MCP INTEGRATION" in claim_auditor_content, (
            "claim-auditor.md must have ## MCP INTEGRATION section"
        )
        # Verify key MCP tools are documented
        mcp_tools = ["mcp__github", "mcp__arxiv", "mcp__filesystem"]
        for tool in mcp_tools:
            assert tool in claim_auditor_content, (
                f"claim-auditor.md MCP INTEGRATION missing tool: {tool}"
            )

    def test_has_venue_specific_standards_section(
        self, claim_auditor_content: str
    ) -> None:
        """claim-auditor.md must have VENUE-SPECIFIC STANDARDS section."""
        assert "## VENUE-SPECIFIC STANDARDS" in claim_auditor_content, (
            "claim-auditor.md must have ## VENUE-SPECIFIC STANDARDS section"
        )
        # Verify key venues are documented
        venues = ["NeurIPS", "ICML", "ICLR", "AAAI", "Workshop"]
        for venue in venues:
            assert venue in claim_auditor_content, (
                f"claim-auditor.md VENUE-SPECIFIC STANDARDS missing: {venue}"
            )

    def test_has_important_principles_section(
        self, claim_auditor_content: str
    ) -> None:
        """claim-auditor.md must have IMPORTANT PRINCIPLES section."""
        assert "## IMPORTANT PRINCIPLES" in claim_auditor_content, (
            "claim-auditor.md must have ## IMPORTANT PRINCIPLES section"
        )


class TestEvidenceCheckerBackwardCompatibility:
    """Backward compatibility tests for evidence-checker.md agent."""

    @pytest.fixture
    def evidence_checker_path(self) -> Path:
        """Return path to evidence-checker.md."""
        return REPO_ROOT / "plugins" / "research-agents" / "agents" / "evidence-checker.md"

    @pytest.fixture
    def evidence_checker_content(self, evidence_checker_path: Path) -> str:
        """Return evidence-checker.md content."""
        return evidence_checker_path.read_text()

    @pytest.fixture
    def evidence_checker_frontmatter(
        self, evidence_checker_path: Path
    ) -> dict[str, Any]:
        """Return evidence-checker.md frontmatter."""
        frontmatter = parse_yaml_frontmatter(evidence_checker_path)
        assert frontmatter is not None, "evidence-checker.md missing frontmatter"
        return frontmatter

    def test_has_required_frontmatter_name(
        self, evidence_checker_frontmatter: dict[str, Any]
    ) -> None:
        """evidence-checker.md must have 'name' field in frontmatter."""
        assert "name" in evidence_checker_frontmatter
        assert evidence_checker_frontmatter["name"] == "evidence-checker"

    def test_has_required_frontmatter_description(
        self, evidence_checker_frontmatter: dict[str, Any]
    ) -> None:
        """evidence-checker.md must have 'description' field in frontmatter."""
        assert "description" in evidence_checker_frontmatter
        description = str(evidence_checker_frontmatter["description"])
        assert len(description.strip()) > 0

    def test_has_required_frontmatter_model(
        self, evidence_checker_frontmatter: dict[str, Any]
    ) -> None:
        """evidence-checker.md must have 'model' field in frontmatter."""
        assert "model" in evidence_checker_frontmatter
        assert evidence_checker_frontmatter["model"] in ["haiku", "sonnet", "opus"]

    def test_has_required_frontmatter_color(
        self, evidence_checker_frontmatter: dict[str, Any]
    ) -> None:
        """evidence-checker.md must have 'color' field in frontmatter."""
        assert "color" in evidence_checker_frontmatter
        assert len(str(evidence_checker_frontmatter["color"]).strip()) > 0

    def test_documents_sequential_workflow(
        self, evidence_checker_content: str
    ) -> None:
        """evidence-checker.md must document the original sequential workflow."""
        assert "Sequential Mode" in evidence_checker_content or "SEQUENTIAL MODE" in evidence_checker_content, (
            "evidence-checker.md must document Sequential Mode (original workflow)"
        )

    def test_has_workflow_section(self, evidence_checker_content: str) -> None:
        """evidence-checker.md must have WORKFLOW section with original steps."""
        assert "## WORKFLOW" in evidence_checker_content, (
            "evidence-checker.md must have ## WORKFLOW section"
        )
        # Verify key workflow steps
        workflow_steps = [
            "Extract Claims",
            "Classify Claims",
            "Locate Evidence",
            "Assess Strength",
            "Search External Sources",
            "Generate Report",
        ]
        for step in workflow_steps:
            assert step in evidence_checker_content, (
                f"evidence-checker.md WORKFLOW missing step: {step}"
            )

    def test_has_evidence_strength_hierarchy_section(
        self, evidence_checker_content: str
    ) -> None:
        """evidence-checker.md must have EVIDENCE STRENGTH HIERARCHY section."""
        assert "## EVIDENCE STRENGTH HIERARCHY" in evidence_checker_content, (
            "evidence-checker.md must have ## EVIDENCE STRENGTH HIERARCHY section"
        )
        # Verify strength levels
        strength_levels = ["EMPIRICAL", "THEORETICAL", "OBSERVATIONAL", "PRECEDENT", "REASONING", "ASSUMED"]
        for level in strength_levels:
            assert level in evidence_checker_content, (
                f"evidence-checker.md EVIDENCE STRENGTH HIERARCHY missing: {level}"
            )

    def test_has_claim_classification_section(
        self, evidence_checker_content: str
    ) -> None:
        """evidence-checker.md must have CLAIM CLASSIFICATION section."""
        assert "## CLAIM CLASSIFICATION" in evidence_checker_content, (
            "evidence-checker.md must have ## CLAIM CLASSIFICATION section"
        )

    def test_has_output_format_section(self, evidence_checker_content: str) -> None:
        """evidence-checker.md must have OUTPUT FORMAT section."""
        assert "## OUTPUT FORMAT" in evidence_checker_content, (
            "evidence-checker.md must have ## OUTPUT FORMAT section"
        )
        # Verify key output format elements
        output_elements = [
            "Evidence Assessment Report",
            "Executive Summary",
            "Critical Issues",
            "Claim-by-Claim Analysis",
            "Strengthening Recommendations",
        ]
        for element in output_elements:
            assert element in evidence_checker_content, (
                f"evidence-checker.md OUTPUT FORMAT missing: {element}"
            )

    def test_has_quick_mode_section(self, evidence_checker_content: str) -> None:
        """evidence-checker.md must preserve QUICK MODE section."""
        assert "## QUICK MODE" in evidence_checker_content, (
            "evidence-checker.md must have ## QUICK MODE section for brainstorming"
        )

    def test_has_mcp_integration_section(self, evidence_checker_content: str) -> None:
        """evidence-checker.md must preserve MCP INTEGRATION section."""
        assert "## MCP INTEGRATION" in evidence_checker_content, (
            "evidence-checker.md must have ## MCP INTEGRATION section"
        )
        # Verify arXiv MCP tools are documented
        assert "mcp__arxiv" in evidence_checker_content, (
            "evidence-checker.md MCP INTEGRATION must document arXiv tools"
        )

    def test_has_venue_specific_standards_section(
        self, evidence_checker_content: str
    ) -> None:
        """evidence-checker.md must have VENUE-SPECIFIC STANDARDS section."""
        assert "## VENUE-SPECIFIC STANDARDS" in evidence_checker_content, (
            "evidence-checker.md must have ## VENUE-SPECIFIC STANDARDS section"
        )
        # Verify key venues
        venues = ["NeurIPS", "ICML", "ICLR", "Workshop"]
        for venue in venues:
            assert venue in evidence_checker_content, (
                f"evidence-checker.md VENUE-SPECIFIC STANDARDS missing: {venue}"
            )

    def test_has_important_principles_section(
        self, evidence_checker_content: str
    ) -> None:
        """evidence-checker.md must have IMPORTANT PRINCIPLES section."""
        assert "## IMPORTANT PRINCIPLES" in evidence_checker_content, (
            "evidence-checker.md must have ## IMPORTANT PRINCIPLES section"
        )

    def test_has_red_flag_phrases_section(
        self, evidence_checker_content: str
    ) -> None:
        """evidence-checker.md must preserve RED FLAG PHRASES section."""
        assert "## RED FLAG PHRASES" in evidence_checker_content, (
            "evidence-checker.md must have ## RED FLAG PHRASES section"
        )


class TestParallelModeAdditionsDoNotBreakInterface:
    """Verify that parallel mode additions don't break the original interface."""

    @pytest.fixture
    def claim_auditor_path(self) -> Path:
        return REPO_ROOT / "plugins" / "research-agents" / "agents" / "claim-auditor.md"

    @pytest.fixture
    def evidence_checker_path(self) -> Path:
        return REPO_ROOT / "plugins" / "research-agents" / "agents" / "evidence-checker.md"

    def test_claim_auditor_parallel_mode_is_optional(
        self, claim_auditor_path: Path
    ) -> None:
        """Parallel mode should be optional with sequential as fallback."""
        content = claim_auditor_path.read_text()
        # Check that fallback to sequential is documented
        assert "fallback" in content.lower() or "sequential" in content.lower(), (
            "claim-auditor.md must document sequential mode as fallback"
        )

    def test_evidence_checker_parallel_mode_is_optional(
        self, evidence_checker_path: Path
    ) -> None:
        """Parallel mode should be optional with sequential as fallback."""
        content = evidence_checker_path.read_text()
        # Check that fallback to sequential is documented
        assert "fallback" in content.lower() or "sequential" in content.lower(), (
            "evidence-checker.md must document sequential mode as fallback"
        )

    def test_claim_auditor_mode_selection_documented(
        self, claim_auditor_path: Path
    ) -> None:
        """claim-auditor.md must document MODE SELECTION criteria."""
        content = claim_auditor_path.read_text()
        assert "MODE SELECTION" in content, (
            "claim-auditor.md must have MODE SELECTION section"
        )

    def test_evidence_checker_mode_selection_documented(
        self, evidence_checker_path: Path
    ) -> None:
        """evidence-checker.md must document MODE SELECTION criteria."""
        content = evidence_checker_path.read_text()
        assert "MODE SELECTION" in content, (
            "evidence-checker.md must have MODE SELECTION section"
        )

    def test_claim_auditor_preserves_original_content_length(
        self, claim_auditor_path: Path
    ) -> None:
        """claim-auditor.md should have substantial content (not truncated)."""
        content = claim_auditor_path.read_text()
        lines = content.strip().split("\n")
        # Original content was substantial; ensure it's preserved
        assert len(lines) >= 200, (
            f"claim-auditor.md seems truncated ({len(lines)} lines). "
            "Original content should be preserved."
        )

    def test_evidence_checker_preserves_original_content_length(
        self, evidence_checker_path: Path
    ) -> None:
        """evidence-checker.md should have substantial content (not truncated)."""
        content = evidence_checker_path.read_text()
        lines = content.strip().split("\n")
        # Original content was substantial; ensure it's preserved
        assert len(lines) >= 150, (
            f"evidence-checker.md seems truncated ({len(lines)} lines). "
            "Original content should be preserved."
        )


class TestOriginalMCPIntegrationPreserved:
    """Ensure all original MCP integration sections are preserved."""

    @pytest.fixture
    def claim_auditor_content(self) -> str:
        path = REPO_ROOT / "plugins" / "research-agents" / "agents" / "claim-auditor.md"
        return path.read_text()

    @pytest.fixture
    def evidence_checker_content(self) -> str:
        path = REPO_ROOT / "plugins" / "research-agents" / "agents" / "evidence-checker.md"
        return path.read_text()

    def test_claim_auditor_github_mcp(self, claim_auditor_content: str) -> None:
        """claim-auditor.md must document GitHub MCP tools."""
        github_tools = ["search_repositories", "get_file_contents", "search_code"]
        for tool in github_tools:
            assert tool in claim_auditor_content, (
                f"claim-auditor.md missing GitHub MCP tool: {tool}"
            )

    def test_claim_auditor_arxiv_mcp(self, claim_auditor_content: str) -> None:
        """claim-auditor.md must document arXiv MCP tools."""
        arxiv_tools = ["search_papers", "get_paper", "get_recent_papers"]
        for tool in arxiv_tools:
            assert tool in claim_auditor_content, (
                f"claim-auditor.md missing arXiv MCP tool: {tool}"
            )

    def test_claim_auditor_filesystem_mcp(self, claim_auditor_content: str) -> None:
        """claim-auditor.md must document Filesystem MCP tools."""
        fs_tools = ["read_file", "search_files", "list_directory"]
        for tool in fs_tools:
            assert tool in claim_auditor_content, (
                f"claim-auditor.md missing Filesystem MCP tool: {tool}"
            )

    def test_evidence_checker_arxiv_mcp(self, evidence_checker_content: str) -> None:
        """evidence-checker.md must document arXiv MCP tools."""
        arxiv_tools = [
            "mcp__arxiv__search_papers",
            "mcp__arxiv__get_recent_papers",
            "mcp__arxiv__search_author",
        ]
        for tool in arxiv_tools:
            assert tool in evidence_checker_content, (
                f"evidence-checker.md missing arXiv MCP tool: {tool}"
            )

    def test_claim_auditor_verification_strategies(
        self, claim_auditor_content: str
    ) -> None:
        """claim-auditor.md must document verification strategies."""
        strategies = [
            "Empirical claims",
            "Novelty claims",
            "Comparative claims",
            "Theoretical claims",
        ]
        for strategy in strategies:
            assert strategy in claim_auditor_content, (
                f"claim-auditor.md missing verification strategy: {strategy}"
            )

    def test_evidence_checker_search_strategies(
        self, evidence_checker_content: str
    ) -> None:
        """evidence-checker.md must document search strategies."""
        assert "Search Strategies" in evidence_checker_content, (
            "evidence-checker.md must have Search Strategies section"
        )


class TestVenueSpecificStandardsPreserved:
    """Ensure venue-specific standards are properly documented."""

    @pytest.fixture
    def claim_auditor_content(self) -> str:
        path = REPO_ROOT / "plugins" / "research-agents" / "agents" / "claim-auditor.md"
        return path.read_text()

    @pytest.fixture
    def evidence_checker_content(self) -> str:
        path = REPO_ROOT / "plugins" / "research-agents" / "agents" / "evidence-checker.md"
        return path.read_text()

    def test_claim_auditor_tier1_venues(self, claim_auditor_content: str) -> None:
        """claim-auditor.md must document Tier 1 venue requirements."""
        tier1_indicators = ["NeurIPS", "ICML", "ICLR", "Tier 1"]
        found = any(ind in claim_auditor_content for ind in tier1_indicators)
        assert found, "claim-auditor.md must document Tier 1 venue requirements"

    def test_claim_auditor_seeds_requirement(self, claim_auditor_content: str) -> None:
        """claim-auditor.md must mention multiple seeds requirement."""
        assert "seed" in claim_auditor_content.lower(), (
            "claim-auditor.md must document multiple seeds requirement"
        )

    def test_claim_auditor_ablations_requirement(
        self, claim_auditor_content: str
    ) -> None:
        """claim-auditor.md must mention ablation requirement."""
        assert "ablation" in claim_auditor_content.lower(), (
            "claim-auditor.md must document ablation requirements"
        )

    def test_evidence_checker_tier1_venues(self, evidence_checker_content: str) -> None:
        """evidence-checker.md must document Tier 1 venue requirements."""
        assert "NeurIPS/ICML/ICLR" in evidence_checker_content, (
            "evidence-checker.md must document Tier 1 venue requirements"
        )

    def test_evidence_checker_workshop_standards(
        self, evidence_checker_content: str
    ) -> None:
        """evidence-checker.md must document workshop-specific standards."""
        assert "Workshop" in evidence_checker_content, (
            "evidence-checker.md must document workshop standards"
        )
        # Workshop standards should be more relaxed
        workshop_section_match = re.search(
            r"\*\*Workshops?\*\*:.*?(?=\n\n|\Z)", evidence_checker_content, re.DOTALL
        )
        if workshop_section_match:
            workshop_section = workshop_section_match.group()
            relaxed_indicators = ["relaxed", "preliminary", "Relaxed", "Preliminary"]
            found = any(ind in workshop_section for ind in relaxed_indicators)
            assert found, "Workshop standards should mention relaxed requirements"
