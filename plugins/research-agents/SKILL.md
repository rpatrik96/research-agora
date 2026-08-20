# Research Agents

Specialized research analysis agents for critical thinking, evidence verification, synthesis, and parallel paper analysis.

## Features

- **Parallel Execution**: Fan-out/fan-in pattern for 2-3x speedup on large papers
- **Research State**: Structured JSON intermediate representation for caching
- **Evidence Hierarchy**: L1-L6 evidence grading with venue-specific standards

## Components

### Agents (22)

**Claims and evidence**
- `claim-auditor` - Verify all paper claims against the L1-L6 evidence hierarchy
- `state-generator` - Generate research-state.json from a paper

**Critique and audience**
- `devils-advocate` - Adversarial analysis of arguments
- `audience-checker` - Evaluate alignment with a target reader persona

**Theory**
- `proof-auditor` - Decompose proofs and check each step
- `counterexample-searcher` - Stress-test theorems by weakening assumptions
- `bounds-analyst` - Analyze convergence rates and complexity bounds
- `intuition-formalizer` - Turn informal intuitions into formal statements
- `theorem-dependency-mapper` - Build a DAG of theorem dependencies
- `notation-consistency-checker` - Build a symbol table and check consistency

**Experiments and figures**
- `statistical-validator` - Verify statistical rigor
- `figure-storyteller` - Generate publication-quality figures
- `artifact-packager` - Prepare code and data for release

**Writing and dissemination**
- `voice-drift-detector` - Detect voice inconsistency across documents
- `reviewer-response-generator` - Draft rebuttals
- `latex-debugger` - Diagnose LaTeX compilation errors

### Micro-Skills (12)
Atomic, parallelizable operations for paper analysis: `claim-extractor`,
`claim-classifier`, `evidence-locator`, `evidence-grader`, `assumption-surfacer`,
`assumption-analyzer`, `citation-verifier`, `cross-referencer`, `novelty-checker`,
`derivation-checker`, `proof-step-extractor`, `proof-step-verifier`.

### Orchestrators (4)
- `parallel-audit` - Parallel claim verification
- `parallel-review` - Comprehensive multi-perspective review
- `parallel-theory-audit` - Parallel verification of proofs and bounds
- `pre-submission-audit` - Five diagnostic passes with a readiness verdict

### Helpers (3)
- `batch-arxiv` - Batched arXiv searches
- `prefetch-evidence` - Pre-fetch evidence
- `context-compactor` - Compress context for efficiency

## Installation

```bash
/plugin install research-agents@research-agora
```

## License

MIT
