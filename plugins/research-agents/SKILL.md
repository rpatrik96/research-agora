# Research Agents

Specialized research analysis agents for critical thinking, evidence verification, synthesis, and parallel paper analysis.

## Features

- **Parallel Execution**: Fan-out/fan-in pattern for 2-3x speedup on large papers
- **Research State**: Structured JSON intermediate representation for caching
- **Evidence Hierarchy**: L1-L6 evidence grading with venue-specific standards

## Components

### Agents (14)
- `claim-auditor` - Verify all paper claims systematically
- `devils-advocate` - Adversarial analysis of arguments
- `evidence-checker` - Verify evidence backing claims
- `perspective-synthesizer` - Synthesize multiple viewpoints
- `audience-checker` - Evaluate audience alignment
- `clarity-optimizer` - Improve writing readability
- `figure-storyteller` - Assess figure narratives
- `latex-debugger` - Debug LaTeX compilation errors
- `statistical-validator` - Verify statistical rigor
- `artifact-packager` - Prepare code/data for release
- `reviewer-response-generator` - Generate rebuttals
- `co-author-sync` - Multi-author coordination
- `discussion-monitor` - Track citations and discussions
- `state-generator` - Generate research-state.json

### Micro-Skills (8)
Atomic, parallelizable operations for paper analysis.

### Orchestrators (2)
- `parallel-audit` - Parallel claim verification
- `parallel-review` - Comprehensive multi-perspective review

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
