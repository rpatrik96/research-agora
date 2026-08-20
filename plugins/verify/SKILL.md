# Verify

Check what the draft claims. Citations against four databases, paper text against the code that produced it, statistics against their assumptions, proofs step by step, notation across the whole source. Every skill here checks something against a source outside itself.

```bash
/plugin install verify@research-agora
```

## Checks against ground truth

Runs a tool or script and compares against something outside itself.

| Skill | Description |
|-------|-------------|
| `/paper-references` | Fact-check references in ML paper drafts |
| `/paper-verify-experiments` | Verify experimental claims in ML papers against source code repositories |
| `/pre-submission-audit` | Comprehensive pre-submission paper audit combining reviewer simulation, claim verification, clarity analysis, notation checking, and statistical validation |
| `/statistical-validator` | Use this agent to verify statistical rigor in ML papers - p-values, confidence intervals, significance tests, effect sizes. Activates when asked to "validate statistics", "check statistical rigor", "verify p-values", "statistical validation", or "check significance" |

## Checks against a rubric

Applies a stated standard. You are the oracle.

| Skill | Description |
|-------|-------------|
| `/claim-auditor` | Deep verify ALL paper claims with systematic evidence hierarchy. NOW SUPPORTS PARALLEL MODE via parallel-audit orchestrator for 2-3x speedup. Activates when asked to "audit claims", "verify claims", "check paper claims", "claim verification", "evidence check", "verify evidence", or "quick evidence scan". Includes Quick Mode for rapid brainstorming checks |
| `/devils-advocate` | Use this agent to challenge arguments, identify logical fallacies, and expose cognitive biases. Supports iterative refinement through constructive adversarial thinking. Invoke during brainstorming, hypothesis formation, or before committing to claims |
| `/notation-consistency-checker` | Build a symbol table and check notation consistency throughout a paper. Detects overloaded symbols, undefined notation, and convention violations. Hybrid: script-based regex extraction + LLM semantic analysis. Trigger: "check notation", "notation consistency", "symbol table", "find notation issues", "verify notation" |
| `/proof-auditor` | Decompose proofs into logical steps, check each step follows from prior ones, identify assumption usage, and flag gaps or unjustified leaps. The theoretical analogue of claim-auditor. Trigger: "audit proof", "check proof", "verify proof", "proof verification", "find proof gaps" |

## Produces something for you to check

Generates an artifact or a candidate. Verifying it is your job.

| Skill | Description |
|-------|-------------|
| `/counterexample-searcher` | Stress-test theorems by systematically exploring what happens when assumptions are dropped or weakened. Generates low-dimensional test cases and boundary conditions. Trigger: "find counterexample", "stress test theorem", "test assumptions", "break this theorem", "assumption necessity" |
| `/theorem-dependency-mapper` | Build a DAG of theorem/lemma/proposition dependencies across the paper. Computes criticality scores, maps assumption flow, and detects orphan lemmas or circular dependencies. Trigger: "map theorem dependencies", "theorem DAG", "dependency graph", "trace assumptions" |

## Internal

Building blocks other skills call. You will not normally invoke these directly.

| Skill | Type |
|-------|------|
| `assumption-analyzer` | micro-skill |
| `citation-verifier` | micro-skill |
| `cross-referencer` | micro-skill |
| `derivation-checker` | micro-skill |
| `parallel-audit` | orchestrator |
| `parallel-review` | orchestrator |
| `parallel-theory-audit` | orchestrator |
| `proof-step-verifier` | micro-skill |
| `state-generator` | agent |

## License

MIT
