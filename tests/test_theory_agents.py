"""Tests for theoretical research agents.

These tests verify the structure, content, and consistency of the new theory agents:
- Agents: proof-auditor, bounds-analyst, notation-consistency-checker,
  theorem-dependency-mapper, proof-strategy-advisor, counterexample-searcher,
  intuition-formalizer, theory-connector
- Micro-skills: proof-step-extractor, proof-step-verifier,
  assumption-analyzer, derivation-checker
- Orchestrator: parallel-theory-audit

Since agents execute in Claude's runtime, we test:
1. File existence and frontmatter validity
2. Required content sections
3. T1-T6 hierarchy documentation
4. Cross-references between agents
5. plugin.json and model-routing.json registration
6. State-generator theory extension
"""

import json
import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent
AGENTS_DIR = REPO_ROOT / "plugins" / "research-agents" / "agents"
MICRO_SKILLS_DIR = REPO_ROOT / "plugins" / "research-agents" / "micro-skills"
ORCHESTRATORS_DIR = REPO_ROOT / "plugins" / "research-agents" / "orchestrators"
PLUGIN_JSON = REPO_ROOT / "plugins" / "research-agents" / ".claude-plugin" / "plugin.json"
MODEL_ROUTING = REPO_ROOT / "plugins" / "research-agents" / "config" / "model-routing.json"

THEORY_AGENTS = [
    "proof-auditor",
    "bounds-analyst",
    "notation-consistency-checker",
    "theorem-dependency-mapper",
    "proof-strategy-advisor",
    "counterexample-searcher",
    "intuition-formalizer",
    "theory-connector",
]

THEORY_MICRO_SKILLS = [
    "proof-step-extractor",
    "proof-step-verifier",
    "assumption-analyzer",
    "derivation-checker",
]

THEORY_ORCHESTRATORS = [
    "parallel-theory-audit",
]


def parse_frontmatter(file_path: Path) -> dict | None:
    """Extract YAML frontmatter from a markdown file."""
    content = file_path.read_text()
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            return None
    return None


# ---------------------------------------------------------------------------
# Section 1: File existence
# ---------------------------------------------------------------------------


class TestTheoryAgentFiles:
    """Tests that all theory agent files exist with correct structure."""

    @pytest.mark.parametrize("agent_name", THEORY_AGENTS)
    def test_agent_file_exists(self, agent_name: str) -> None:
        """Each theory agent file must exist."""
        path = AGENTS_DIR / f"{agent_name}.md"
        assert path.exists(), f"Agent file missing: {path}"

    @pytest.mark.parametrize("skill_name", THEORY_MICRO_SKILLS)
    def test_micro_skill_file_exists(self, skill_name: str) -> None:
        """Each theory micro-skill file must exist."""
        path = MICRO_SKILLS_DIR / f"{skill_name}.md"
        assert path.exists(), f"Micro-skill file missing: {path}"

    @pytest.mark.parametrize("orch_name", THEORY_ORCHESTRATORS)
    def test_orchestrator_file_exists(self, orch_name: str) -> None:
        """Each theory orchestrator file must exist."""
        path = ORCHESTRATORS_DIR / f"{orch_name}.md"
        assert path.exists(), f"Orchestrator file missing: {path}"


# ---------------------------------------------------------------------------
# Section 2: Frontmatter validation
# ---------------------------------------------------------------------------


class TestTheoryAgentFrontmatter:
    """Tests for YAML frontmatter in theory agents."""

    VALID_MODELS = ["haiku", "sonnet", "opus"]

    @pytest.mark.parametrize("agent_name", THEORY_AGENTS)
    def test_agent_has_valid_frontmatter(self, agent_name: str) -> None:
        """Agent frontmatter must have name, description, and model."""
        fm = parse_frontmatter(AGENTS_DIR / f"{agent_name}.md")
        assert fm is not None, f"{agent_name} missing YAML frontmatter"
        assert fm.get("name") == agent_name, f"Name mismatch: {fm.get('name')} != {agent_name}"
        assert len(str(fm.get("description", "")).strip()) > 0, f"{agent_name} empty description"
        assert fm.get("model") in self.VALID_MODELS, f"{agent_name} invalid model: {fm.get('model')}"

    @pytest.mark.parametrize("skill_name", THEORY_MICRO_SKILLS)
    def test_micro_skill_has_valid_frontmatter(self, skill_name: str) -> None:
        """Micro-skill frontmatter must have name, description, and model."""
        fm = parse_frontmatter(MICRO_SKILLS_DIR / f"{skill_name}.md")
        assert fm is not None, f"{skill_name} missing YAML frontmatter"
        assert fm.get("name") == skill_name, f"Name mismatch: {fm.get('name')} != {skill_name}"
        assert len(str(fm.get("description", "")).strip()) > 0
        assert fm.get("model") in self.VALID_MODELS

    @pytest.mark.parametrize("orch_name", THEORY_ORCHESTRATORS)
    def test_orchestrator_has_valid_frontmatter(self, orch_name: str) -> None:
        """Orchestrator frontmatter must have name, description, and model."""
        fm = parse_frontmatter(ORCHESTRATORS_DIR / f"{orch_name}.md")
        assert fm is not None, f"{orch_name} missing YAML frontmatter"
        assert fm.get("name") == orch_name
        assert len(str(fm.get("description", "")).strip()) > 0
        assert fm.get("model") in self.VALID_MODELS


# ---------------------------------------------------------------------------
# Section 3: Model assignment correctness
# ---------------------------------------------------------------------------


class TestTheoryModelAssignment:
    """Tests that model assignments match the plan."""

    EXPECTED_MODELS = {
        # Agents
        "proof-auditor": "opus",
        "bounds-analyst": "opus",
        "notation-consistency-checker": "sonnet",
        "theorem-dependency-mapper": "sonnet",
        "proof-strategy-advisor": "opus",
        "counterexample-searcher": "opus",
        "intuition-formalizer": "opus",
        "theory-connector": "opus",
        # Micro-skills
        "proof-step-extractor": "sonnet",
        "proof-step-verifier": "opus",
        "assumption-analyzer": "sonnet",
        "derivation-checker": "opus",
        # Orchestrators
        "parallel-theory-audit": "opus",
    }

    @pytest.mark.parametrize(
        "name,expected_model",
        list(EXPECTED_MODELS.items()),
        ids=list(EXPECTED_MODELS.keys()),
    )
    def test_model_matches_plan(self, name: str, expected_model: str) -> None:
        """Model in frontmatter must match the planned assignment."""
        for directory in [AGENTS_DIR, MICRO_SKILLS_DIR, ORCHESTRATORS_DIR]:
            path = directory / f"{name}.md"
            if path.exists():
                fm = parse_frontmatter(path)
                assert fm is not None
                assert fm["model"] == expected_model, (
                    f"{name}: expected model '{expected_model}', got '{fm['model']}'"
                )
                return
        pytest.fail(f"File not found for {name}")


# ---------------------------------------------------------------------------
# Section 4: T1-T6 Theoretical Evidence Hierarchy
# ---------------------------------------------------------------------------


class TestTheoreticalEvidenceHierarchy:
    """Tests for T1-T6 hierarchy documentation."""

    T_LEVELS = ["T1", "T2", "T3", "T4", "T5", "T6"]
    T_LABELS = [
        "FORMALLY_VERIFIED",
        "COMPLETE_PROOF",
        "PROOF_WITH_GAPS",
        "PROOF_SKETCH",
        "INFORMAL_ARGUMENT",
        "THEOREM_ASSERTION",
    ]

    def test_proof_auditor_documents_all_t_levels(self) -> None:
        """proof-auditor must document all T1-T6 levels."""
        content = (AGENTS_DIR / "proof-auditor.md").read_text()
        for level in self.T_LEVELS:
            assert level in content, f"proof-auditor missing {level}"

    def test_proof_auditor_documents_all_t_labels(self) -> None:
        """proof-auditor must document all T-level labels."""
        content = (AGENTS_DIR / "proof-auditor.md").read_text()
        for label in self.T_LABELS:
            assert label in content, f"proof-auditor missing label {label}"

    def test_orchestrator_documents_t_levels(self) -> None:
        """parallel-theory-audit must reference T1-T6 levels."""
        content = (ORCHESTRATORS_DIR / "parallel-theory-audit.md").read_text()
        for level in self.T_LEVELS:
            assert level in content, f"parallel-theory-audit missing {level}"

    def test_plugin_json_registers_t_hierarchy(self) -> None:
        """plugin.json must register the theoretical evidence hierarchy."""
        data = json.loads(PLUGIN_JSON.read_text())
        features = data.get("features", {})
        assert "theoretical_evidence_hierarchy" in features
        levels = features["theoretical_evidence_hierarchy"].get("levels", [])
        for label in self.T_LABELS:
            assert label in levels, f"plugin.json missing T-level: {label}"


# ---------------------------------------------------------------------------
# Section 5: Agent-specific content tests
# ---------------------------------------------------------------------------


class TestProofAuditor:
    """Tests specific to proof-auditor agent."""

    @pytest.fixture
    def content(self) -> str:
        return (AGENTS_DIR / "proof-auditor.md").read_text()

    def test_has_common_error_detection(self, content: str) -> None:
        """Should document common proof errors."""
        error_categories = ["Inequality", "Algebraic", "Logic"]
        for cat in error_categories:
            assert cat in content, f"Missing error category: {cat}"

    def test_has_assumption_tracking(self, content: str) -> None:
        """Should document assumption tracking."""
        assert "Assumption Tracking" in content or "assumption" in content.lower()

    def test_has_gap_classification(self, content: str) -> None:
        """Should classify gap severity."""
        severities = ["Critical", "Major", "Minor"]
        for sev in severities:
            assert sev in content, f"Missing severity: {sev}"

    def test_references_micro_skills(self, content: str) -> None:
        """Should reference proof-step-extractor and proof-step-verifier."""
        assert "proof-step-extractor" in content
        assert "proof-step-verifier" in content

    def test_has_parallel_mode(self, content: str) -> None:
        """Should document parallel mode delegation."""
        assert "parallel-theory-audit" in content


class TestBoundsAnalyst:
    """Tests specific to bounds-analyst agent."""

    @pytest.fixture
    def content(self) -> str:
        return (AGENTS_DIR / "bounds-analyst.md").read_text()

    def test_has_known_rate_tables(self, content: str) -> None:
        """Should have tables of known optimal rates."""
        assert "Convex Optimization" in content
        assert "Learning Theory" in content

    def test_has_dimensional_analysis(self, content: str) -> None:
        """Should document dimensional consistency checking."""
        assert "Dimensional" in content or "dimensional" in content

    def test_has_hidden_constant_analysis(self, content: str) -> None:
        """Should analyze hidden constants in O-notation."""
        assert "Hidden Constant" in content or "hidden constant" in content.lower()

    def test_documents_common_red_flags(self, content: str) -> None:
        """Should document red flags for bounds."""
        red_flags = ["Missing dimension", "Exponential in d", "Wrong limit"]
        found = sum(1 for rf in red_flags if rf in content)
        assert found >= 2, "Missing most bound red flags"


class TestNotationConsistencyChecker:
    """Tests specific to notation-consistency-checker agent."""

    @pytest.fixture
    def content(self) -> str:
        return (AGENTS_DIR / "notation-consistency-checker.md").read_text()

    def test_is_hybrid(self, content: str) -> None:
        """Should be marked as hybrid (script + LLM)."""
        assert "Hybrid" in content

    def test_has_latex_patterns(self, content: str) -> None:
        """Should document LaTeX command patterns."""
        patterns = ["mathbf", "mathcal", "mathbb", "boldsymbol"]
        for pat in patterns:
            assert pat in content, f"Missing LaTeX pattern: {pat}"

    def test_has_convention_table(self, content: str) -> None:
        """Should have a convention checking table."""
        conventions = ["Vectors", "Matrices", "Sets", "Scalars"]
        found = sum(1 for c in conventions if c in content)
        assert found >= 3, "Missing most convention entries"

    def test_has_severity_levels(self, content: str) -> None:
        """Should classify issues by severity."""
        assert "Critical" in content
        assert "Major" in content
        assert "Minor" in content

    def test_has_extraction_commands(self, content: str) -> None:
        """Should include grep/regex extraction commands."""
        assert "grep" in content


class TestTheoremDependencyMapper:
    """Tests specific to theorem-dependency-mapper agent."""

    @pytest.fixture
    def content(self) -> str:
        return (AGENTS_DIR / "theorem-dependency-mapper.md").read_text()

    def test_has_environment_types(self, content: str) -> None:
        """Should list theorem-like environment types."""
        envs = ["theorem", "lemma", "proposition", "corollary", "definition", "assumption"]
        for env in envs:
            assert env.lower() in content.lower(), f"Missing environment: {env}"

    def test_has_criticality_scoring(self, content: str) -> None:
        """Should document criticality scoring."""
        assert "Criticality" in content or "criticality" in content

    def test_has_structural_checks(self, content: str) -> None:
        """Should check for orphan lemmas and circular dependencies."""
        assert "Orphan" in content or "orphan" in content
        assert "Circular" in content or "circular" in content

    def test_has_dag_output(self, content: str) -> None:
        """Should output a DAG structure."""
        assert "nodes" in content
        assert "edges" in content

    def test_has_assumption_flow(self, content: str) -> None:
        """Should trace assumption flow through results."""
        assert "Assumption Flow" in content or "assumption flow" in content.lower()


class TestProofStrategyAdvisor:
    """Tests specific to proof-strategy-advisor agent."""

    @pytest.fixture
    def content(self) -> str:
        return (AGENTS_DIR / "proof-strategy-advisor.md").read_text()

    def test_has_result_classification(self, content: str) -> None:
        """Should classify result types."""
        types = ["Convergence", "Generalization", "Impossibility", "Concentration"]
        found = sum(1 for t in types if t in content)
        assert found >= 3, "Missing most result types"

    def test_has_technique_tables(self, content: str) -> None:
        """Should have technique recommendation tables."""
        techniques = ["Lyapunov", "Rademacher", "PAC-Bayes", "Hoeffding"]
        found = sum(1 for t in techniques if t in content)
        assert found >= 3, "Missing most proof techniques"

    def test_has_simplification_suggestions(self, content: str) -> None:
        """Should suggest simplification paths."""
        assert "Simplification" in content

    def test_has_key_challenge_section(self, content: str) -> None:
        """Should identify the key technical challenge."""
        assert "Key Technical Challenge" in content or "key challenge" in content.lower()


class TestCounterexampleSearcher:
    """Tests specific to counterexample-searcher agent."""

    @pytest.fixture
    def content(self) -> str:
        return (AGENTS_DIR / "counterexample-searcher.md").read_text()

    def test_has_assumption_removal_workflow(self, content: str) -> None:
        """Should systematically drop assumptions."""
        assert "Dropping" in content or "dropping" in content
        assert "Assumption" in content

    def test_has_pathological_examples(self, content: str) -> None:
        """Should list standard pathological examples."""
        assert "Patholog" in content or "patholog" in content

    def test_has_edge_cases(self, content: str) -> None:
        """Should test edge cases."""
        edge_cases = ["n = 1", "d = 1", "T = 1"]
        found = sum(1 for ec in edge_cases if ec in content)
        assert found >= 2, "Missing most edge cases"

    def test_has_computational_verification(self, content: str) -> None:
        """Should suggest computational experiments."""
        assert "Computational" in content or "computational" in content
        assert "python" in content.lower() or "experiment" in content.lower()


class TestIntuitionFormalizer:
    """Tests specific to intuition-formalizer agent."""

    @pytest.fixture
    def content(self) -> str:
        return (AGENTS_DIR / "intuition-formalizer.md").read_text()

    def test_has_multi_level_formalization(self, content: str) -> None:
        """Should offer multiple formalization levels."""
        assert "Level 1" in content or "STRONG" in content
        assert "Level 2" in content or "MODERATE" in content
        assert "Level 3" in content or "WEAK" in content

    def test_has_condition_mapping(self, content: str) -> None:
        """Should map informal conditions to formal ones."""
        informal = ["smooth enough", "well-behaved", "not too complex"]
        found = sum(1 for i in informal if i in content)
        assert found >= 2, "Missing informal-to-formal mappings"

    def test_has_pitfall_warnings(self, content: str) -> None:
        """Should warn about formalization pitfalls."""
        assert "Pitfall" in content or "pitfall" in content

    def test_has_latex_output(self, content: str) -> None:
        """Should produce LaTeX output."""
        assert "\\begin{theorem}" in content or "LaTeX" in content


class TestTheoryConnector:
    """Tests specific to theory-connector agent."""

    @pytest.fixture
    def content(self) -> str:
        return (AGENTS_DIR / "theory-connector.md").read_text()

    def test_has_cross_domain_mappings(self, content: str) -> None:
        """Should map between domains."""
        domains = ["Optimization", "Game theory", "Learning theory", "Information theory"]
        found = sum(1 for d in domains if d in content)
        assert found >= 3, "Missing most cross-domain mappings"

    def test_has_vocabulary_translation(self, content: str) -> None:
        """Should provide vocabulary translations."""
        assert "Translation" in content or "translation" in content

    def test_has_generalization_paths(self, content: str) -> None:
        """Should identify generalization paths."""
        assert "Generalization" in content

    def test_has_utility_assessment(self, content: str) -> None:
        """Should assess connection utility."""
        assert "Utility" in content or "utility" in content


# ---------------------------------------------------------------------------
# Section 6: Micro-skill content tests
# ---------------------------------------------------------------------------


class TestTheoryMicroSkillContent:
    """Tests for theory micro-skill required content."""

    @pytest.mark.parametrize("skill_name", THEORY_MICRO_SKILLS)
    def test_has_parallelization_properties(self, skill_name: str) -> None:
        """All micro-skills must document parallelization properties."""
        content = (MICRO_SKILLS_DIR / f"{skill_name}.md").read_text()
        assert "Parallelization" in content, f"{skill_name} missing parallelization docs"

    @pytest.mark.parametrize("skill_name", THEORY_MICRO_SKILLS)
    def test_has_input_specification(self, skill_name: str) -> None:
        """All micro-skills must have input specification."""
        content = (MICRO_SKILLS_DIR / f"{skill_name}.md").read_text()
        assert "Input Specification" in content, f"{skill_name} missing Input Specification"

    @pytest.mark.parametrize("skill_name", THEORY_MICRO_SKILLS)
    def test_has_output_specification(self, skill_name: str) -> None:
        """All micro-skills must have output specification."""
        content = (MICRO_SKILLS_DIR / f"{skill_name}.md").read_text()
        assert "Output Specification" in content, f"{skill_name} missing Output Specification"

    @pytest.mark.parametrize("skill_name", THEORY_MICRO_SKILLS)
    def test_has_json_schemas(self, skill_name: str) -> None:
        """Micro-skills must include JSON schemas."""
        content = (MICRO_SKILLS_DIR / f"{skill_name}.md").read_text()
        assert '"type"' in content, f"{skill_name} missing JSON schema type fields"

    @pytest.mark.parametrize("skill_name", THEORY_MICRO_SKILLS)
    def test_has_worker_preamble_compliance(self, skill_name: str) -> None:
        """Micro-skills must document Worker Preamble compliance."""
        content = (MICRO_SKILLS_DIR / f"{skill_name}.md").read_text()
        assert "Worker Preamble" in content, f"{skill_name} missing Worker Preamble section"

    @pytest.mark.parametrize("skill_name", THEORY_MICRO_SKILLS)
    def test_can_run_in_parallel(self, skill_name: str) -> None:
        """All theory micro-skills must declare they can run in parallel."""
        content = (MICRO_SKILLS_DIR / f"{skill_name}.md").read_text()
        assert "Yes" in content and "parallel" in content.lower()


class TestProofStepExtractor:
    """Tests specific to proof-step-extractor micro-skill."""

    @pytest.fixture
    def content(self) -> str:
        return (MICRO_SKILLS_DIR / "proof-step-extractor.md").read_text()

    def test_has_justification_categories(self, content: str) -> None:
        """Should list justification categories for proof steps."""
        categories = ["definition", "assumption", "algebraic", "inequality"]
        for cat in categories:
            assert cat in content, f"Missing justification category: {cat}"

    def test_has_granularity_rules(self, content: str) -> None:
        """Should document granularity rules for decomposition."""
        assert "Granularity" in content or "granularity" in content

    def test_output_has_step_structure(self, content: str) -> None:
        """Output schema must include step_id, action, depends_on."""
        assert "step_id" in content
        assert "action" in content
        assert "depends_on" in content


class TestProofStepVerifier:
    """Tests specific to proof-step-verifier micro-skill."""

    @pytest.fixture
    def content(self) -> str:
        return (MICRO_SKILLS_DIR / "proof-step-verifier.md").read_text()

    def test_has_verdict_definitions(self, content: str) -> None:
        """Should define verdict types."""
        verdicts = ["valid", "suspicious", "gap", "error"]
        for v in verdicts:
            assert v in content, f"Missing verdict: {v}"

    def test_has_verification_checks(self, content: str) -> None:
        """Should list verification checks."""
        checks = ["Algebraic", "Inequality", "Logic"]
        found = sum(1 for c in checks if c in content)
        assert found >= 2, "Missing most verification checks"


class TestAssumptionAnalyzer:
    """Tests specific to assumption-analyzer micro-skill."""

    @pytest.fixture
    def content(self) -> str:
        return (MICRO_SKILLS_DIR / "assumption-analyzer.md").read_text()

    def test_has_standardness_assessment(self, content: str) -> None:
        """Should assess whether assumption is standard."""
        assert "standard" in content.lower()

    def test_has_weaker_alternatives(self, content: str) -> None:
        """Should suggest weaker alternatives."""
        assert "weaker" in content.lower() or "alternative" in content.lower()

    def test_has_assumption_hierarchies(self, content: str) -> None:
        """Should document known assumption hierarchies."""
        hierarchies = ["Convexity", "Smoothness", "Noise"]
        found = sum(1 for h in hierarchies if h in content)
        assert found >= 2, "Missing most assumption hierarchies"


class TestDerivationChecker:
    """Tests specific to derivation-checker micro-skill."""

    @pytest.fixture
    def content(self) -> str:
        return (MICRO_SKILLS_DIR / "derivation-checker.md").read_text()

    def test_has_operation_types(self, content: str) -> None:
        """Should list operation types."""
        ops = ["algebraic", "inequality", "gradient", "expectation"]
        for op in ops:
            assert op in content.lower(), f"Missing operation type: {op}"

    def test_has_common_error_patterns(self, content: str) -> None:
        """Should list common error patterns."""
        errors = ["Sign error", "Dropped", "Wrong"]
        found = sum(1 for e in errors if e in content)
        assert found >= 2, "Missing most error patterns"


# ---------------------------------------------------------------------------
# Section 7: Orchestrator content tests
# ---------------------------------------------------------------------------


class TestParallelTheoryAudit:
    """Tests specific to parallel-theory-audit orchestrator."""

    @pytest.fixture
    def content(self) -> str:
        return (ORCHESTRATORS_DIR / "parallel-theory-audit.md").read_text()

    def test_has_four_phases(self, content: str) -> None:
        """Should document 4 phases (Setup, Fan-Out 1, Fan-Out 2, Fan-In)."""
        assert "Phase 1" in content
        assert "Phase 2" in content
        assert "Phase 3" in content
        assert "Phase 4" in content

    def test_has_fan_out_fan_in(self, content: str) -> None:
        """Should use fan-out/fan-in pattern."""
        assert "Fan-Out" in content
        assert "Fan-In" in content

    def test_references_all_theory_micro_skills(self, content: str) -> None:
        """Should reference all theory micro-skills."""
        for skill in THEORY_MICRO_SKILLS:
            assert skill in content, f"Orchestrator missing reference to {skill}"

    def test_references_notation_checker(self, content: str) -> None:
        """Should invoke notation-consistency-checker."""
        assert "notation-consistency-checker" in content

    def test_references_bounds_analyst(self, content: str) -> None:
        """Should invoke bounds-analyst."""
        assert "bounds-analyst" in content

    def test_references_dependency_mapper(self, content: str) -> None:
        """Should invoke theorem-dependency-mapper."""
        assert "theorem-dependency-mapper" in content

    def test_has_error_handling(self, content: str) -> None:
        """Should document error handling."""
        assert "Error Handling" in content or "Error" in content

    def test_has_concurrency_limits(self, content: str) -> None:
        """Should document concurrency limits."""
        assert "Concurrency" in content or "concurrent" in content.lower()

    def test_has_performance_expectations(self, content: str) -> None:
        """Should document performance expectations."""
        assert "Performance" in content
        assert "Speedup" in content or "speedup" in content.lower()

    def test_has_output_format(self, content: str) -> None:
        """Should have structured output format."""
        assert "Output Format" in content or "## Output" in content

    def test_documents_state_generator_invocation(self, content: str) -> None:
        """Should invoke state-generator for setup."""
        assert "state-generator" in content


# ---------------------------------------------------------------------------
# Section 8: Registration and consistency
# ---------------------------------------------------------------------------


class TestTheoryRegistration:
    """Tests that all theory components are registered in config files."""

    @pytest.fixture
    def plugin_data(self) -> dict:
        return json.loads(PLUGIN_JSON.read_text())

    @pytest.fixture
    def routing_data(self) -> dict:
        return json.loads(MODEL_ROUTING.read_text())

    @pytest.mark.parametrize("agent_name", THEORY_AGENTS)
    def test_agent_registered_in_plugin_json(self, plugin_data: dict, agent_name: str) -> None:
        """Each theory agent must be listed in plugin.json components.agents."""
        agents = plugin_data["components"]["agents"]["items"]
        assert agent_name in agents, f"{agent_name} not registered in plugin.json agents"

    @pytest.mark.parametrize("skill_name", THEORY_MICRO_SKILLS)
    def test_micro_skill_registered_in_plugin_json(self, plugin_data: dict, skill_name: str) -> None:
        """Each theory micro-skill must be listed in plugin.json components.micro-skills."""
        skills = plugin_data["components"]["micro-skills"]["items"]
        assert skill_name in skills, f"{skill_name} not registered in plugin.json micro-skills"

    @pytest.mark.parametrize("orch_name", THEORY_ORCHESTRATORS)
    def test_orchestrator_registered_in_plugin_json(self, plugin_data: dict, orch_name: str) -> None:
        """Each theory orchestrator must be listed in plugin.json components.orchestrators."""
        orchs = plugin_data["components"]["orchestrators"]["items"]
        assert orch_name in orchs, f"{orch_name} not registered in plugin.json orchestrators"

    @pytest.mark.parametrize(
        "component_name",
        THEORY_AGENTS + THEORY_MICRO_SKILLS + THEORY_ORCHESTRATORS,
    )
    def test_component_in_model_routing(self, routing_data: dict, component_name: str) -> None:
        """Each theory component must have a model-routing entry."""
        all_routed = set()
        for section in routing_data["routing_rules"].values():
            all_routed.update(section.keys())
        assert component_name in all_routed, (
            f"{component_name} not found in model-routing.json"
        )

    @pytest.mark.parametrize(
        "component_name",
        THEORY_AGENTS + THEORY_MICRO_SKILLS + THEORY_ORCHESTRATORS,
    )
    def test_routing_has_reason(self, routing_data: dict, component_name: str) -> None:
        """Each routing entry must have a reason field."""
        for section in routing_data["routing_rules"].values():
            if component_name in section:
                assert "reason" in section[component_name], (
                    f"{component_name} routing missing reason"
                )
                return
        pytest.fail(f"{component_name} not found in routing rules")


# ---------------------------------------------------------------------------
# Section 9: State-generator theory extension
# ---------------------------------------------------------------------------


class TestStateGeneratorTheoryExtension:
    """Tests that state-generator has been extended for theory parsing."""

    @pytest.fixture
    def content(self) -> str:
        return (AGENTS_DIR / "state-generator.md").read_text()

    def test_has_theory_section_in_output(self, content: str) -> None:
        """Output schema must include theory section."""
        assert '"theory"' in content

    def test_theory_has_theorems(self, content: str) -> None:
        """Theory section must include theorems array."""
        assert '"theorems"' in content

    def test_theory_has_assumptions(self, content: str) -> None:
        """Theory section must include assumptions array."""
        assert '"assumptions"' in content

    def test_theory_has_definitions(self, content: str) -> None:
        """Theory section must include definitions array."""
        assert '"definitions"' in content

    def test_theory_has_bounds(self, content: str) -> None:
        """Theory section must include bounds array."""
        assert '"bounds"' in content

    def test_theory_has_dependency_graph(self, content: str) -> None:
        """Theory section must include dependency_graph."""
        assert '"dependency_graph"' in content

    def test_theory_has_symbol_table(self, content: str) -> None:
        """Theory section must include symbol_table."""
        assert '"symbol_table"' in content

    def test_has_phase_2b(self, content: str) -> None:
        """Should have Phase 2b for theory structure parsing."""
        assert "Phase 2b" in content

    def test_phase_2b_extracts_proofs(self, content: str) -> None:
        """Phase 2b should extract proof environments."""
        assert "Proof" in content and "begin{proof}" in content

    def test_phase_2b_extracts_assumptions(self, content: str) -> None:
        """Phase 2b should extract assumption environments."""
        assert "begin{assumption}" in content

    def test_phase_2b_extracts_bounds(self, content: str) -> None:
        """Phase 2b should extract asymptotic bounds."""
        assert "Bound Extraction" in content

    def test_references_parallel_theory_audit(self, content: str) -> None:
        """Should reference parallel-theory-audit in Called By."""
        assert "parallel-theory-audit" in content

    def test_theory_section_is_optional(self, content: str) -> None:
        """Theory section should be optional for empirical papers."""
        assert "optional" in content.lower()


# ---------------------------------------------------------------------------
# Section 10: Cross-reference consistency
# ---------------------------------------------------------------------------


class TestTheoryCrossReferences:
    """Tests that agents correctly cross-reference each other."""

    def test_proof_auditor_references_orchestrator(self) -> None:
        """proof-auditor should reference parallel-theory-audit."""
        content = (AGENTS_DIR / "proof-auditor.md").read_text()
        assert "parallel-theory-audit" in content

    def test_orchestrator_references_state_generator(self) -> None:
        """parallel-theory-audit should reference state-generator."""
        content = (ORCHESTRATORS_DIR / "parallel-theory-audit.md").read_text()
        assert "state-generator" in content

    def test_notation_checker_references_orchestrator(self) -> None:
        """notation-consistency-checker should reference parallel-theory-audit."""
        content = (AGENTS_DIR / "notation-consistency-checker.md").read_text()
        assert "parallel-theory-audit" in content

    def test_bounds_analyst_references_state(self) -> None:
        """bounds-analyst should reference research-state.json."""
        content = (AGENTS_DIR / "bounds-analyst.md").read_text()
        assert "research-state" in content

    def test_extractor_feeds_verifier(self) -> None:
        """proof-step-extractor should note it feeds proof-step-verifier."""
        content = (MICRO_SKILLS_DIR / "proof-step-extractor.md").read_text()
        assert "proof-step-verifier" in content

    def test_verifier_receives_from_extractor(self) -> None:
        """proof-step-verifier should note it receives from proof-step-extractor."""
        content = (MICRO_SKILLS_DIR / "proof-step-verifier.md").read_text()
        assert "proof-step-extractor" in content


# ---------------------------------------------------------------------------
# Section 11: README documentation
# ---------------------------------------------------------------------------


class TestREADMETheoryDocumentation:
    """Tests that README documents all theory agents."""

    @pytest.fixture
    def readme_content(self) -> str:
        return (REPO_ROOT / "README.md").read_text()

    @pytest.mark.parametrize("agent_name", THEORY_AGENTS)
    def test_agent_in_readme(self, readme_content: str, agent_name: str) -> None:
        """Each theory agent must be listed in README."""
        assert agent_name in readme_content, f"{agent_name} missing from README"
