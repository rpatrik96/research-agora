# Research Agents Plugin

> Parallel research analysis system for rigorous paper verification

## Overview

The `research-agents` plugin provides a comprehensive toolkit for analyzing research papers. It combines 14 high-level agents, 8 atomic micro-skills, 2 parallel orchestrators, and 3 utility helpers to deliver fast, thorough paper analysis.

**Key capability**: Fan-out/fan-in parallel execution achieves 2-3x speedup on papers with 10+ claims.

## Quick Start

```bash
# Install the plugin
/plugin install research-agents@research-agora

# Generate research state (required first step)
/state-generator /path/to/paper.tex

# Run parallel claim audit
/parallel-audit /path/to/paper.tex --venue neurips

# Run comprehensive paper review
/parallel-review /path/to/paper.tex --personas expert,skeptic
```

## Architecture

```
                    ┌─────────────────────┐
                    │   Orchestrators     │
                    │  (parallel-audit,   │
                    │   parallel-review)  │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
     ┌────────────────┐ ┌────────────┐ ┌────────────────┐
     │  Micro-Skills  │ │   Agents   │ │    Helpers     │
     │   (8 atomic    │ │ (14 high-  │ │ (3 utilities)  │
     │   operations)  │ │   level)   │ │                │
     └────────────────┘ └────────────┘ └────────────────┘
              │                │                │
              └────────────────┼────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │   research-state    │
                    │      .json          │
                    └─────────────────────┘
```

### Micro-Skills (8 Atomic Operations)

Stateless, parallelizable operations that process scoped input and return structured JSON.

| Skill | Model | Purpose |
|-------|-------|---------|
| `claim-extractor` | Haiku | Extract claims from a single section |
| `claim-classifier` | Haiku | Categorize claims (empirical, theoretical, etc.) |
| `evidence-locator` | Haiku | Find tables/figures/equations supporting claims |
| `evidence-grader` | Sonnet | Assess evidence quality (L1-L6 scale) |
| `novelty-checker` | Sonnet | Verify novelty claims against arXiv |
| `citation-verifier` | Haiku | Validate citation accuracy |
| `assumption-surfacer` | Sonnet | Identify implicit assumptions |
| `cross-referencer` | Opus | Check consistency across paper |

### Orchestrators (2 Parallel Coordinators)

Fan-out/fan-in coordinators that spawn and merge subagent results.

| Orchestrator | Purpose | Subagents Used |
|--------------|---------|----------------|
| `parallel-audit` | Verify all claims in parallel | evidence-grader, novelty-checker, citation-verifier, assumption-surfacer, cross-referencer |
| `parallel-review` | Multi-perspective paper review | parallel-audit, clarity-optimizer, audience-checker, figure-storyteller |

### Helpers (3 Utilities)

Efficiency utilities for common operations.

| Helper | Model | Purpose |
|--------|-------|---------|
| `batch-arxiv` | Haiku | Batch arXiv queries for related work |
| `prefetch-evidence` | Haiku | Pre-load table/figure content |
| `context-compactor` | Sonnet | Compress context for token efficiency |

### Agents (14 High-Level)

| Agent | Description |
|-------|-------------|
| `state-generator` | Parse paper into research-state.json |
| `claim-auditor` | Sequential claim verification (legacy) |
| `devils-advocate` | Adversarial analysis of arguments |
| `evidence-checker` | Deep-dive evidence assessment |
| `perspective-synthesizer` | Multi-viewpoint synthesis |
| `audience-checker` | Target audience alignment |
| `clarity-optimizer` | Writing quality improvements |
| `figure-storyteller` | Figure narrative assessment |
| `latex-debugger` | LaTeX error resolution |
| `statistical-validator` | Statistical methodology check |
| `artifact-packager` | Reproducibility packaging |
| `reviewer-response-generator` | Rebuttal drafting |
| `co-author-sync` | Multi-author coordination |
| `discussion-monitor` | Track reviewer discussions |

## Execution Modes

Configure via `config/model-routing.json`:

| Mode | Max Concurrent | Timeout | Model Overrides | Use Case |
|------|----------------|---------|-----------------|----------|
| `parallel` | 5 | 120s | None | Large papers, speed priority |
| `pipeline` | Sequential | - | None | Methodical, checkpointed |
| `eco` | 3 | 180s | Downgrade to Haiku | Budget-conscious |
| `thorough` | 3 | 300s | Upgrade to Opus | Pre-submission |

### Pipeline Stages (sequential mode)

```
parse → extract → classify → locate → grade → verify → synthesize
```

## Configuration

### Model Routing

Located at `config/model-routing.json`:

```json
{
  "routing_rules": {
    "micro-skills": {
      "claim-extractor": {"model": "haiku", "temperature": 0.1},
      "evidence-grader": {"model": "sonnet", "temperature": 0.2},
      "cross-referencer": {"model": "opus", "temperature": 0.2}
    }
  }
}
```

### Worker Preamble Protocol

All micro-skills follow the leaf agent protocol (see `config/WORKER_PREAMBLE.md`):

1. **No delegation** - Execute directly, no subagent spawning
2. **No clarification** - Work with provided input
3. **Scoped execution** - Stay within designated scope
4. **Structured output** - Return JSON only
5. **Graceful failure** - Return error codes, never hang

**Error Codes**:

| Code | Meaning |
|------|---------|
| `INVALID_INPUT` | Missing or malformed input |
| `TIMEOUT` | Task exceeded time limit |
| `SERVICE_UNAVAILABLE` | External API down |
| `SCOPE_EXCEEDED` | Task too large |
| `CONFIDENCE_LOW` | Uncertain result |
| `PARTIAL_RESULT` | Incomplete due to constraints |

## Research State

The `research-state.json` file is the intermediate representation enabling parallel processing.

```json
{
  "metadata": {
    "title": "Paper Title",
    "arxiv_id": "2301.00001",
    "venue_target": "neurips",
    "source_hash": "abc123..."
  },
  "structure": {
    "sections": [{"id": "sec1", "title": "Introduction"}],
    "figures": [{"id": "fig1", "caption": "..."}],
    "tables": [{"id": "tab1", "caption": "..."}]
  },
  "claims": [
    {
      "id": "C1",
      "text": "Our method achieves 95% accuracy",
      "type": "empirical",
      "importance": "critical"
    }
  ],
  "evidence_map": {
    "C1": [{"type": "table", "ref": "tab1"}]
  }
}
```

**Caching**: If `source_hash` matches, state is reused (use `--force` to regenerate).

## Evidence Hierarchy

Claims are graded on a 6-level scale:

| Level | Label | Description |
|-------|-------|-------------|
| L1 | CODE_VERIFIED | Reproducible with provided code |
| L2 | REPRODUCIBLE_EXPERIMENT | Clear methodology, could reproduce |
| L3 | PAPER_EVIDENCE | Tables/figures in paper |
| L4 | CITATION_SUPPORT | Supported by citations |
| L5 | LOGICAL_ARGUMENT | Reasoning without empirical data |
| L6 | ASSERTION | No supporting evidence |

## Cost Estimates

Per-task typical costs:

| Model | Input/1K | Output/1K | Typical Task |
|-------|----------|-----------|--------------|
| Haiku | $0.00025 | $0.00125 | $0.01 |
| Sonnet | $0.003 | $0.015 | $0.05 |
| Opus | $0.015 | $0.075 | $0.15 |

**Mode multipliers**:

| Mode | Multiplier | Typical Paper (20 claims) |
|------|------------|---------------------------|
| parallel | 1.0x | ~$1.50 |
| pipeline | 1.1x | ~$1.65 |
| eco | 0.4x | ~$0.60 |
| thorough | 2.5x | ~$3.75 |

## Examples

### Parallel Audit

```bash
/parallel-audit /papers/my-paper/main.tex --venue neurips
```

**Output**:
```markdown
# Parallel Claim Audit Report

| Metric | Value |
|--------|-------|
| Total Claims | 18 |
| Verified (L1-L3) | 12 (67%) |
| Weak Evidence (L4-L5) | 4 (22%) |
| Unsupported (L6) | 2 (11%) |

## Critical Issues
1. **C7**: "First to solve X" - Prior work found: arXiv:2305.12345
2. **C12**: Missing baseline comparison for ImageNet results
```

### Parallel Review

```bash
/parallel-review /papers/my-paper/ --personas expert,skeptic --focus technical,novelty
```

**Output**:
```markdown
# Comprehensive Paper Review

**Recommendation**: Weak Accept
**Confidence**: Medium

## Strengths
1. Novel attention mechanism with theoretical grounding
2. Comprehensive ablation studies

## Weaknesses
### Critical
- C3 novelty claim challenged by concurrent work

### Major
- Missing compute cost comparison with baselines

## Revision Checklist
- [ ] Address concurrent work in related work section
- [ ] Add FLOPs comparison table
```

### Using State Generator

```bash
/state-generator /papers/my-paper/main.tex

# Output:
# Parsed: 7 sections, 5 figures, 3 tables
# Extracted: 18 claims (8 empirical, 3 theoretical, 4 comparative, 3 novelty)
# Written: research-state.json
```

## Performance

| Phase | Sequential | Parallel | Speedup |
|-------|------------|----------|---------|
| Setup | 2 min | 2 min | 1x |
| Analysis (20 claims) | 15 min | 5 min | 3x |
| Merge & Report | 1 min | 2 min | 0.5x |
| **Total** | **18 min** | **9 min** | **2x** |

## Directory Structure

```
plugins/research-agents/
├── .claude-plugin/plugin.json
├── agents/                    # 14 high-level agents
├── micro-skills/              # 8 atomic operations
├── orchestrators/             # 2 parallel coordinators
├── helpers/                   # 3 utility skills
├── config/
│   ├── model-routing.json     # Model/mode configuration
│   └── WORKER_PREAMBLE.md     # Leaf agent protocol
└── cache/                     # Cached research states
```

## License

MIT
