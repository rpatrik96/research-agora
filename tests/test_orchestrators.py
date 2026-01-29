"""Tests for orchestrator functionality.

These tests verify the structure and documentation of orchestrators.
Orchestrators coordinate parallel execution of micro-skills, so we test:
1. File existence and structure
2. Frontmatter validity
3. Required phase documentation (Setup, Fan-Out, Fan-In)
4. Model routing configuration references
5. Worker preamble wrapping documentation
6. Input/output schema documentation
7. Error handling documentation
"""

import json
import re
from pathlib import Path

import pytest
import yaml


class TestOrchestratorStructure:
    """Tests for orchestrator file structure and metadata."""

    ORCHESTRATORS_DIR = Path("plugins/research-agents/orchestrators")

    @pytest.fixture
    def all_orchestrators(self) -> list[Path]:
        """Get all orchestrator files."""
        if not self.ORCHESTRATORS_DIR.exists():
            pytest.skip("Orchestrators directory not found")
        orchestrators = list(self.ORCHESTRATORS_DIR.glob("*.md"))
        # Exclude templates
        return [o for o in orchestrators if not o.name.startswith("_")]

    @pytest.fixture
    def parallel_audit(self) -> Path:
        """Get the parallel-audit orchestrator."""
        path = self.ORCHESTRATORS_DIR / "parallel-audit.md"
        if not path.exists():
            pytest.skip("parallel-audit orchestrator not found")
        return path

    @pytest.fixture
    def parallel_review(self) -> Path:
        """Get the parallel-review orchestrator."""
        path = self.ORCHESTRATORS_DIR / "parallel-review.md"
        if not path.exists():
            pytest.skip("parallel-review orchestrator not found")
        return path

    def parse_frontmatter(self, content: str) -> dict | None:
        """Extract YAML frontmatter from markdown."""
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if match:
            return yaml.safe_load(match.group(1))
        return None

    def test_orchestrators_directory_exists(self) -> None:
        """Orchestrators directory should exist."""
        assert self.ORCHESTRATORS_DIR.exists(), "Orchestrators directory not found"

    def test_all_orchestrators_have_frontmatter(
        self, all_orchestrators: list[Path]
    ) -> None:
        """All orchestrators should have valid YAML frontmatter."""
        for orch_path in all_orchestrators:
            content = orch_path.read_text()
            frontmatter = self.parse_frontmatter(content)

            assert frontmatter is not None, f"{orch_path.name} missing frontmatter"
            assert "name" in frontmatter, f"{orch_path.name} missing 'name'"
            assert (
                "description" in frontmatter
            ), f"{orch_path.name} missing 'description'"

    def test_all_orchestrators_specify_model(
        self, all_orchestrators: list[Path]
    ) -> None:
        """All orchestrators should specify a model in frontmatter."""
        valid_models = ["haiku", "sonnet", "opus"]

        for orch_path in all_orchestrators:
            content = orch_path.read_text()
            frontmatter = self.parse_frontmatter(content)

            assert frontmatter is not None, f"{orch_path.name} missing frontmatter"
            assert "model" in frontmatter, f"{orch_path.name} missing 'model'"
            assert (
                frontmatter["model"] in valid_models
            ), f"{orch_path.name} has invalid model: {frontmatter['model']}"


class TestOrchestratorPhases:
    """Tests for orchestrator phase documentation."""

    ORCHESTRATORS_DIR = Path("plugins/research-agents/orchestrators")

    @pytest.fixture
    def all_orchestrators(self) -> list[Path]:
        """Get all orchestrator files."""
        if not self.ORCHESTRATORS_DIR.exists():
            pytest.skip("Orchestrators directory not found")
        orchestrators = list(self.ORCHESTRATORS_DIR.glob("*.md"))
        return [o for o in orchestrators if not o.name.startswith("_")]

    def test_all_orchestrators_document_setup_phase(
        self, all_orchestrators: list[Path]
    ) -> None:
        """All orchestrators should document the Setup phase."""
        for orch_path in all_orchestrators:
            content = orch_path.read_text()

            assert (
                "Phase 1: Setup" in content or "Setup" in content
            ), f"{orch_path.name} missing Setup phase documentation"

    def test_all_orchestrators_document_fan_out_phase(
        self, all_orchestrators: list[Path]
    ) -> None:
        """All orchestrators should document the Fan-Out phase."""
        for orch_path in all_orchestrators:
            content = orch_path.read_text()

            assert (
                "Fan-Out" in content or "fan-out" in content.lower()
            ), f"{orch_path.name} missing Fan-Out phase documentation"

    def test_all_orchestrators_document_fan_in_phase(
        self, all_orchestrators: list[Path]
    ) -> None:
        """All orchestrators should document the Fan-In phase."""
        for orch_path in all_orchestrators:
            content = orch_path.read_text()

            assert (
                "Fan-In" in content or "fan-in" in content.lower()
            ), f"{orch_path.name} missing Fan-In phase documentation"

    def test_phases_in_correct_order(self, all_orchestrators: list[Path]) -> None:
        """Phases should be documented in order: Setup, Fan-Out, Fan-In."""
        for orch_path in all_orchestrators:
            content = orch_path.read_text()

            setup_pos = content.find("Phase 1")
            fanout_pos = content.find("Phase 2")
            fanin_pos = content.find("Phase 3")

            # All phases should be found
            if setup_pos != -1 and fanout_pos != -1 and fanin_pos != -1:
                assert (
                    setup_pos < fanout_pos < fanin_pos
                ), f"{orch_path.name} phases not in correct order"


class TestOrchestratorInputOutputSchemas:
    """Tests for input/output schema documentation."""

    ORCHESTRATORS_DIR = Path("plugins/research-agents/orchestrators")

    @pytest.fixture
    def all_orchestrators(self) -> list[Path]:
        """Get all orchestrator files."""
        if not self.ORCHESTRATORS_DIR.exists():
            pytest.skip("Orchestrators directory not found")
        orchestrators = list(self.ORCHESTRATORS_DIR.glob("*.md"))
        return [o for o in orchestrators if not o.name.startswith("_")]

    def test_all_orchestrators_have_input_specification(
        self, all_orchestrators: list[Path]
    ) -> None:
        """All orchestrators should have an Input Specification section."""
        for orch_path in all_orchestrators:
            content = orch_path.read_text()

            assert (
                "Input Specification" in content or "## Input" in content
            ), f"{orch_path.name} missing Input Specification"

    def test_all_orchestrators_have_output_format(
        self, all_orchestrators: list[Path]
    ) -> None:
        """All orchestrators should have an Output Format section."""
        for orch_path in all_orchestrators:
            content = orch_path.read_text()

            assert (
                "Output Format" in content or "## Output" in content
            ), f"{orch_path.name} missing Output Format documentation"

    def test_input_has_json_schema(self, all_orchestrators: list[Path]) -> None:
        """Input specifications should include JSON schema."""
        for orch_path in all_orchestrators:
            content = orch_path.read_text()

            # Look for JSON schema indicators in input section
            input_match = re.search(
                r"## Input.*?```json(.*?)```", content, re.DOTALL
            )
            assert (
                input_match is not None
            ), f"{orch_path.name} missing JSON schema in Input Specification"

            # Verify it contains schema properties
            schema_content = input_match.group(1)
            assert (
                '"type"' in schema_content
            ), f"{orch_path.name} input schema missing 'type' field"
            assert (
                '"properties"' in schema_content
            ), f"{orch_path.name} input schema missing 'properties' field"

    def test_input_schema_has_required_fields(
        self, all_orchestrators: list[Path]
    ) -> None:
        """Input schemas should specify required fields."""
        for orch_path in all_orchestrators:
            content = orch_path.read_text()

            input_match = re.search(
                r"## Input.*?```json(.*?)```", content, re.DOTALL
            )
            if input_match:
                schema_content = input_match.group(1)
                assert (
                    '"required"' in schema_content
                ), f"{orch_path.name} input schema missing 'required' field"


class TestOrchestratorErrorHandling:
    """Tests for error handling documentation."""

    ORCHESTRATORS_DIR = Path("plugins/research-agents/orchestrators")

    @pytest.fixture
    def all_orchestrators(self) -> list[Path]:
        """Get all orchestrator files."""
        if not self.ORCHESTRATORS_DIR.exists():
            pytest.skip("Orchestrators directory not found")
        orchestrators = list(self.ORCHESTRATORS_DIR.glob("*.md"))
        return [o for o in orchestrators if not o.name.startswith("_")]

    def test_all_orchestrators_have_error_handling(
        self, all_orchestrators: list[Path]
    ) -> None:
        """All orchestrators should document error handling."""
        for orch_path in all_orchestrators:
            content = orch_path.read_text()

            assert (
                "Error Handling" in content or "Error" in content
            ), f"{orch_path.name} missing Error Handling documentation"

    def test_error_handling_has_table(self, all_orchestrators: list[Path]) -> None:
        """Error handling should include a table of error types and strategies."""
        for orch_path in all_orchestrators:
            content = orch_path.read_text()

            # Look for error handling section with table
            error_section = re.search(
                r"## Error Handling.*?(\|.*\|)", content, re.DOTALL
            )
            assert (
                error_section is not None
            ), f"{orch_path.name} missing error handling table"

    def test_subagent_spawning_has_on_error(
        self, all_orchestrators: list[Path]
    ) -> None:
        """Subagent spawning blocks should include on_error handling."""
        for orch_path in all_orchestrators:
            content = orch_path.read_text()

            # Find SPAWN_SUBAGENT blocks
            spawn_blocks = re.findall(
                r"SPAWN_SUBAGENT:.*?(?=SPAWN_SUBAGENT:|```|$)", content, re.DOTALL
            )

            for block in spawn_blocks:
                # At least some blocks should have on_error
                if "on_error" in content:
                    break
            else:
                # If no blocks have on_error, check if there's general error handling
                assert (
                    "on_error" in content or "Error Handling" in content
                ), f"{orch_path.name} missing on_error in subagent spawning"


class TestOrchestratorSubagentSpawning:
    """Tests for subagent spawning and worker preamble documentation."""

    ORCHESTRATORS_DIR = Path("plugins/research-agents/orchestrators")

    @pytest.fixture
    def all_orchestrators(self) -> list[Path]:
        """Get all orchestrator files."""
        if not self.ORCHESTRATORS_DIR.exists():
            pytest.skip("Orchestrators directory not found")
        orchestrators = list(self.ORCHESTRATORS_DIR.glob("*.md"))
        return [o for o in orchestrators if not o.name.startswith("_")]

    def test_all_orchestrators_document_subagent_spawning(
        self, all_orchestrators: list[Path]
    ) -> None:
        """All orchestrators should document how subagents are spawned."""
        for orch_path in all_orchestrators:
            content = orch_path.read_text()

            assert (
                "SPAWN_SUBAGENT" in content
                or "Subagent" in content
                or "subagent" in content
            ), f"{orch_path.name} missing subagent spawning documentation"

    def test_subagent_spawning_specifies_skill(
        self, all_orchestrators: list[Path]
    ) -> None:
        """Subagent spawning should specify which skill to invoke."""
        for orch_path in all_orchestrators:
            content = orch_path.read_text()

            # Find SPAWN_SUBAGENT blocks
            if "SPAWN_SUBAGENT" in content:
                spawn_blocks = re.findall(
                    r"SPAWN_SUBAGENT:.*?(?=SPAWN_SUBAGENT:|```|$)", content, re.DOTALL
                )
                for block in spawn_blocks:
                    assert (
                        "skill:" in block
                    ), f"{orch_path.name} SPAWN_SUBAGENT missing skill specification"

    def test_subagent_spawning_specifies_input(
        self, all_orchestrators: list[Path]
    ) -> None:
        """Subagent spawning should specify input parameters."""
        for orch_path in all_orchestrators:
            content = orch_path.read_text()

            # Find SPAWN_SUBAGENT blocks
            if "SPAWN_SUBAGENT" in content:
                spawn_blocks = re.findall(
                    r"SPAWN_SUBAGENT:.*?(?=SPAWN_SUBAGENT:|```|$)", content, re.DOTALL
                )
                for block in spawn_blocks:
                    assert (
                        "input:" in block
                    ), f"{orch_path.name} SPAWN_SUBAGENT missing input specification"

    def test_subagent_spawning_specifies_timeout(
        self, all_orchestrators: list[Path]
    ) -> None:
        """Subagent spawning should specify timeout."""
        for orch_path in all_orchestrators:
            content = orch_path.read_text()

            # Find SPAWN_SUBAGENT blocks
            if "SPAWN_SUBAGENT" in content:
                spawn_blocks = re.findall(
                    r"SPAWN_SUBAGENT:.*?(?=SPAWN_SUBAGENT:|```|$)", content, re.DOTALL
                )
                for block in spawn_blocks:
                    assert (
                        "timeout:" in block
                    ), f"{orch_path.name} SPAWN_SUBAGENT missing timeout specification"


class TestOrchestratorIntegration:
    """Tests for orchestrator integration documentation."""

    ORCHESTRATORS_DIR = Path("plugins/research-agents/orchestrators")

    @pytest.fixture
    def all_orchestrators(self) -> list[Path]:
        """Get all orchestrator files."""
        if not self.ORCHESTRATORS_DIR.exists():
            pytest.skip("Orchestrators directory not found")
        orchestrators = list(self.ORCHESTRATORS_DIR.glob("*.md"))
        return [o for o in orchestrators if not o.name.startswith("_")]

    def test_all_orchestrators_document_called_by(
        self, all_orchestrators: list[Path]
    ) -> None:
        """All orchestrators should document what triggers them."""
        for orch_path in all_orchestrators:
            content = orch_path.read_text()

            assert (
                "Called By" in content or "Trigger" in content or "trigger" in content.lower()
            ), f"{orch_path.name} missing Called By / Trigger documentation"

    def test_all_orchestrators_document_calls(
        self, all_orchestrators: list[Path]
    ) -> None:
        """All orchestrators should document what subagents they call."""
        for orch_path in all_orchestrators:
            content = orch_path.read_text()

            assert (
                "Calls" in content or "Subagent" in content
            ), f"{orch_path.name} missing Calls / Subagents documentation"

    def test_all_orchestrators_document_state_updates(
        self, all_orchestrators: list[Path]
    ) -> None:
        """All orchestrators should document state updates."""
        for orch_path in all_orchestrators:
            content = orch_path.read_text()

            assert (
                "State" in content or "state" in content
            ), f"{orch_path.name} missing state documentation"


class TestParallelAuditOrchestrator:
    """Tests specific to parallel-audit orchestrator."""

    @pytest.fixture
    def orchestrator_content(self) -> str:
        """Load parallel-audit content."""
        path = Path("plugins/research-agents/orchestrators/parallel-audit.md")
        if not path.exists():
            pytest.skip("parallel-audit orchestrator not found")
        return path.read_text()

    def test_documents_claim_partitioning(self, orchestrator_content: str) -> None:
        """Should document how claims are partitioned."""
        assert "partition" in orchestrator_content.lower()
        assert "Claim Partitioning" in orchestrator_content

    def test_documents_claim_types(self, orchestrator_content: str) -> None:
        """Should document all claim types for partitioning."""
        claim_types = [
            "empirical",
            "theoretical",
            "novelty",
            "comparative",
            "methodological",
        ]
        for claim_type in claim_types:
            assert (
                claim_type in orchestrator_content.lower()
            ), f"Missing claim type: {claim_type}"

    def test_documents_result_merging(self, orchestrator_content: str) -> None:
        """Should document how results are merged."""
        assert "Result Merging" in orchestrator_content or "merge" in orchestrator_content.lower()

    def test_documents_conflict_resolution(self, orchestrator_content: str) -> None:
        """Should document conflict resolution strategies."""
        assert "Conflict" in orchestrator_content

    def test_documents_parallelism_limits(self, orchestrator_content: str) -> None:
        """Should document parallelism limits."""
        assert "Parallelism Limits" in orchestrator_content or "concurrent" in orchestrator_content.lower()

    def test_documents_fallback_mode(self, orchestrator_content: str) -> None:
        """Should document fallback to sequential mode."""
        assert "Fallback" in orchestrator_content or "fallback" in orchestrator_content.lower()

    def test_documents_performance_expectations(self, orchestrator_content: str) -> None:
        """Should document performance expectations."""
        assert "Performance" in orchestrator_content
        assert "Speedup" in orchestrator_content or "speedup" in orchestrator_content.lower()


class TestParallelReviewOrchestrator:
    """Tests specific to parallel-review orchestrator."""

    @pytest.fixture
    def orchestrator_content(self) -> str:
        """Load parallel-review content."""
        path = Path("plugins/research-agents/orchestrators/parallel-review.md")
        if not path.exists():
            pytest.skip("parallel-review orchestrator not found")
        return path.read_text()

    def test_documents_reviewer_personas(self, orchestrator_content: str) -> None:
        """Should document reviewer personas."""
        assert "Reviewer Personas" in orchestrator_content
        personas = ["expert", "skeptic", "newcomer", "practitioner"]
        for persona in personas:
            assert (
                persona.lower() in orchestrator_content.lower()
            ), f"Missing persona: {persona}"

    def test_documents_review_tracks(self, orchestrator_content: str) -> None:
        """Should document different review tracks."""
        tracks = ["Technical", "Presentation", "Visual", "Novelty", "Consistency"]
        for track in tracks:
            assert (
                track in orchestrator_content
            ), f"Missing review track: {track}"

    def test_documents_feedback_prioritization(self, orchestrator_content: str) -> None:
        """Should document feedback prioritization."""
        assert "Priority" in orchestrator_content or "priorit" in orchestrator_content.lower()
        priorities = ["Critical", "Major", "Minor"]
        for priority in priorities:
            assert (
                priority in orchestrator_content
            ), f"Missing priority level: {priority}"

    def test_documents_review_synthesis(self, orchestrator_content: str) -> None:
        """Should document how reviews are synthesized."""
        assert "Synthesis" in orchestrator_content or "synthesize" in orchestrator_content.lower()

    def test_documents_revision_checklist(self, orchestrator_content: str) -> None:
        """Should document revision checklist generation."""
        assert "Revision Checklist" in orchestrator_content or "checklist" in orchestrator_content.lower()

    def test_calls_parallel_audit(self, orchestrator_content: str) -> None:
        """Should document that it calls parallel-audit orchestrator."""
        assert "parallel-audit" in orchestrator_content

    def test_documents_comparison_with_sequential(self, orchestrator_content: str) -> None:
        """Should document comparison with sequential review."""
        assert "Sequential" in orchestrator_content or "sequential" in orchestrator_content.lower()


class TestOrchestratorConsistency:
    """Tests for consistency across all orchestrators."""

    ORCHESTRATORS_DIR = Path("plugins/research-agents/orchestrators")

    @pytest.fixture
    def all_orchestrators_content(self) -> dict[str, str]:
        """Load content of all orchestrators."""
        if not self.ORCHESTRATORS_DIR.exists():
            pytest.skip("Orchestrators directory not found")

        orchestrators = {}
        for orch_path in self.ORCHESTRATORS_DIR.glob("*.md"):
            if not orch_path.name.startswith("_"):
                orchestrators[orch_path.stem] = orch_path.read_text()
        return orchestrators

    def test_consistent_spawn_block_format(
        self, all_orchestrators_content: dict[str, str]
    ) -> None:
        """All orchestrators should use consistent SPAWN_SUBAGENT format."""
        for name, content in all_orchestrators_content.items():
            if "SPAWN_SUBAGENT" in content:
                # Check for consistent structure
                spawn_blocks = re.findall(
                    r"SPAWN_SUBAGENT:.*?(?=SPAWN_SUBAGENT:|```|$)", content, re.DOTALL
                )
                for block in spawn_blocks:
                    # All should have skill and input at minimum
                    assert (
                        "skill:" in block and "input:" in block
                    ), f"{name} has inconsistent SPAWN_SUBAGENT format"

    def test_all_orchestrators_have_one_line_description(
        self, all_orchestrators_content: dict[str, str]
    ) -> None:
        """All orchestrators should have a one-line description."""
        for name, content in all_orchestrators_content.items():
            assert (
                "One-line description" in content or "**One-line" in content
            ), f"{name} missing one-line description"

    def test_all_orchestrators_document_purpose(
        self, all_orchestrators_content: dict[str, str]
    ) -> None:
        """All orchestrators should have a Purpose section."""
        for name, content in all_orchestrators_content.items():
            assert (
                "## Purpose" in content
            ), f"{name} missing Purpose section"

    def test_json_blocks_valid(
        self, all_orchestrators_content: dict[str, str]
    ) -> None:
        """JSON blocks in orchestrators should be valid JSON schemas."""
        json_block_pattern = re.compile(r"```json\n(.*?)\n```", re.DOTALL)

        for name, content in all_orchestrators_content.items():
            json_blocks = json_block_pattern.findall(content)

            for i, block in enumerate(json_blocks):
                try:
                    cleaned = block.strip()
                    if cleaned:
                        json.loads(cleaned)
                except json.JSONDecodeError:
                    # Only fail if it looks like it should be valid JSON
                    if not any(
                        marker in block
                        for marker in ["...", "// ", "# ", "{claim", "{section", "{paper"]
                    ):
                        pytest.fail(
                            f"{name} has invalid JSON in block {i + 1}: {block[:100]}"
                        )
