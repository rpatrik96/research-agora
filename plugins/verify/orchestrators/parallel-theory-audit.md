---
name: parallel-theory-audit
description: |
  Orchestrates parallel theoretical verification across a paper's proofs,
  assumptions, bounds, and notation. The theory analogue of parallel-audit.
  Trigger: "parallel theory audit", "audit proofs", "theory verification",
  "verify all proofs".
model: opus
color: purple
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: verification
  verification-level: heuristic
  visibility: internal
---

# Orchestrator: Parallel Theory Audit

> **LLM-required**: Orchestrating parallel theory verification requires coordinating multiple analysis agents. No script alternative.

> **One-line description**: Coordinates parallel verification of all proofs, bounds, assumptions, and notation in a theoretical paper.

## Purpose

This orchestrator parallelizes theoretical verification by:
1. Extending research state with theory section (theorems, proofs, assumptions)
2. Building a theorem dependency graph
3. Extracting proof steps in parallel
4. Verifying steps, assumptions, and bounds in parallel
5. Merging results into a unified theory audit report

Fan-out bounds wall-clock by the slowest worker rather than the sum. No speedup figure has been measured.

## Orchestration Pattern

```
Phase 1: Setup (Sequential)
├── Check for existing research-state.json
├── If missing: invoke state-generator (with theory parsing)
├── Load research state, verify theory section populated
├── Build theorem dependency graph via theorem-dependency-mapper
├── Compute criticality scores for verification priority
└── Plan subagent allocation based on proof count and complexity

Phase 2: Fan-Out Stage 1 (Parallel)
├── Proof Decomposition
│   └── For each proof: spawn proof-step-extractor
├── Assumption Analysis
│   └── For each assumption: spawn assumption-analyzer
├── Notation Checking
│   └── Spawn notation-consistency-checker (full paper)
└── Bounds Extraction
    └── Spawn bounds-analyst (all bounds)

Phase 3: Fan-Out Stage 2 (Parallel, depends on Phase 2)
├── Step Verification
│   └── For each extracted step: spawn proof-step-verifier
└── Derivation Checking
    └── For each derivation step: spawn proof-step-verifier (level: computation)

Phase 4: Fan-In (Sequential)
├── Collect all subagent results
├── Merge proof step verdicts into per-proof assessments
├── Cross-reference with dependency graph (criticality weighting)
├── Assign T1-T6 levels to each proof
├── Generate unified theory audit report
└── Update research-state.json with audit results
```

## Input Specification

```json
{
  "type": "object",
  "required": ["paper_path"],
  "properties": {
    "paper_path": {
      "type": "string",
      "description": "Path to paper (LaTeX dir, .tex file, or .pdf)"
    },
    "venue_target": {
      "type": "string",
      "enum": ["neurips", "icml", "iclr", "aaai", "cvpr", "acl", "workshop", "arxiv", "other"],
      "default": "neurips"
    },
    "options": {
      "type": "object",
      "properties": {
        "skip_notation_check": {"type": "boolean", "default": false},
        "skip_bounds_analysis": {"type": "boolean", "default": false},
        "max_proofs": {"type": "integer", "default": 20},
        "force_regenerate_state": {"type": "boolean", "default": false}
      }
    }
  }
}
```

## Phase 1: Setup

### 1.1 Research State Check

```
If research-state.json exists AND has theory section:
  Load and use cached state
Else if research-state.json exists WITHOUT theory section:
  Re-run state-generator with --force to add theory parsing
Else:
  Run state-generator from scratch
```

### 1.2 Theorem Dependency Graph

Invoke `theorem-dependency-mapper` to build the DAG:
- Identify all theorem-like environments
- Extract explicit and implicit dependencies
- Compute criticality scores
- Determine verification priority order

### 1.3 Subagent Planning

| Paper Size | Proofs | Max Concurrent |
|-----------|--------|----------------|
| Small | 1-3 | 5 |
| Medium | 4-8 | 8 |
| Large | 9+ | 10 |

The concurrency cap is a real constraint and is enforced. Duration is not
predicted here — it depends on proof length and model latency, and no
measurement exists to base an estimate on.

## Phase 2: Fan-Out Stage 1

### Proof Decomposition

For each proof in research state:

```
SPAWN: proof-step-extractor
  input:
    proof_id: [proof ID]
    theorem_statement: [statement being proved]
    proof_text: [full proof text]
    assumptions: [available assumptions]
  timeout: 45s
  on_error: mark proof as "extraction_failed", continue
```

### Assumption Analysis

For each formally stated assumption:

```
SPAWN: assumption-analyzer
  input:
    assumption_id: [assumption ID]
    assumption_text: [full text]
    context: [what it's used for]
    domain: [detected domain]
  timeout: 30s
  on_error: skip, note in report
```

### Notation Consistency

```
SPAWN: notation-consistency-checker
  input:
    paper_files: [list of .tex files]
  timeout: 60s
  on_error: skip notation check, note in report
```

### Bounds Analysis

```
SPAWN: bounds-analyst
  input:
    paper_text: [full paper text]
    theorems: [theorem list from state]
    venue_target: [target venue]
  timeout: 90s
  on_error: skip bounds analysis, note in report
```

## Phase 3: Fan-Out Stage 2

Depends on Phase 2 completion (needs extracted proof steps).

### Step Verification

For each step extracted by `proof-step-extractor`:

```
SPAWN: proof-step-verifier
  input:
    step: [step object from extractor]
    premises: [prior steps + assumptions + definitions]
    theorem_context: [what the proof establishes]
  timeout: 30s
  on_error: mark step as "verification_failed"
```

### Derivation Checking

For steps classified as algebraic/inequality/gradient computations:

```
SPAWN: proof-step-verifier
  input:
    derivation_id: [step ID]
    from_expression: [starting expression]
    to_expression: [result expression]
    operation: [operation type]
    context: [surrounding context]
  timeout: 30s
  on_error: mark as "check_failed"
```

## Phase 4: Fan-In

### 4.0 Provenance Gate (run before aggregating anything)

Not every subagent in this fan-out verifies. `assumption-analyzer` and `bounds-analyst` generate from recalled knowledge: `assumption-analyzer` proposes weaker and stronger alternatives from memorized hierarchies and makes no external call, and `bounds-analyst` compares against rate tables it recalls rather than retrieves. Their output is a hypothesis about the paper, not a finding about it.

**Tag every incoming result with its provenance before it enters the merged report:**

| Source | Provenance | How it may appear in the report |
|---|---|---|
| `proof-step-verifier`, `cross-referencer` | checked against the paper's own text | as a finding |
| `notation-consistency-checker` | extracted by regex from the source | as a finding |
| `bounds-analyst` | recalled, unless it retrieved the cited work | as a finding only where it retrieved; otherwise `UNVERIFIED` |
| `assumption-analyzer` | recalled | as a suggestion, never as a finding |

An unretrieved rate comparison and a recalled assumption hierarchy are carried into the output as `UNVERIFIED — <what would settle it>`. **They never contribute to the criticality score in 4.2 or the T1–T6 level in 4.3**, because a level assignment is a claim about the paper's proofs and a recalled comparison is not evidence about this paper.

This orchestrator is `verification-level: heuristic` for exactly this reason: it coordinates a mix of checkers and generators, and a report that flattens the two would launder recall into verification.

### 4.1 Per-Proof Assessment

For each proof, aggregate step verdicts:

```
Proof verdict rules:
- ALL steps valid → T2 (COMPLETE_PROOF)
- Some steps suspicious, no errors → T2 with caveats
- Any step marked "gap" → T3 (PROOF_WITH_GAPS)
- Any step marked "error" → NEEDS_FIX
- Extraction failed → T5 (INFORMAL_ARGUMENT) or T6
- No proof present → T6 (THEOREM_ASSERTION)
```

### 4.2 Criticality-Weighted Scoring

Weight issues by theorem criticality from dependency graph:
- Issue in high-criticality theorem: **Critical**
- Issue in medium-criticality lemma: **Major**
- Issue in low-criticality remark: **Minor**

### 4.3 T1-T6 Level Assignment

| Level | Label | Criteria |
|-------|-------|----------|
| T1 | FORMALLY_VERIFIED | Lean/Coq proof exists (not assessed by this tool) |
| T2 | COMPLETE_PROOF | All steps verified as valid |
| T3 | PROOF_WITH_GAPS | Proof present but has unjustified leaps |
| T4 | PROOF_SKETCH | High-level strategy only, key steps omitted |
| T5 | INFORMAL_ARGUMENT | Intuitive reasoning without formal proof |
| T6 | THEOREM_ASSERTION | Stated without proof or argument |

## Error Handling

| Error | Strategy |
|-------|----------|
| State generation fails | Abort with clear error |
| Single proof extraction fails | Mark proof as "extraction_failed", continue others |
| Single step verification fails | Mark step as "verification_failed", continue |
| Notation checker fails | Skip notation, note in report |
| Bounds analyst fails | Skip bounds, note in report |
| >50% subagents fail | Abort parallel mode, suggest sequential `proof-auditor` |
| Dependency mapper fails | Continue without criticality scoring |

## Concurrency Limits

| Limit | Value | Reason |
|-------|-------|--------|
| Max concurrent Phase 2 agents | 10 | Avoid overwhelming executor |
| Max concurrent Phase 3 agents | 10 | Rate limiting |
| Max total subagents | 80 | Cap for very large papers |
| Steps exceeding 80 | Batch into groups of 40 | Sequential batches |

## Output Format

```markdown
# Theory Audit Report

**Paper**: [Title]
**Proofs audited**: [N]
**Assumptions analyzed**: [N]
**Bounds checked**: [N]
**Audit Date**: [Date]
**Mode**: parallel-theory-audit

---

## Executive Summary

| Metric | Count |
|--------|-------|
| Total theorems/lemmas | [N] |
| Proofs at T2 (complete) | [N] |
| Proofs at T3 (gaps) | [N] |
| Proofs at T4-T6 (incomplete/missing) | [N] |
| Assumptions analyzed | [N] |
| Bounds verified | [N] |
| Notation issues | [N] |
| Critical issues | [N] |

**Overall verdict**: [SOUND / GAPS_FOUND / MAJOR_ISSUES]

---

## Proof Verification Results

| Proof | Result | Steps | Level | Issues | Criticality |
|-------|--------|-------|-------|--------|-------------|
| Theorem 1 | Convergence | 12 | T2 | 0 | HIGH |
| Lemma 1 | Concentration | 8 | T3 | 1 gap | HIGH |
| Theorem 2 | Lower bound | 15 | T2 | 0 | MEDIUM |
| Prop 1 | Extension | 0 | T6 | Missing | LOW |

---

## Critical Issues (Must Fix)

### Issue 1: [Title]
**Location**: [Proof of Theorem X, Step Y]
**Type**: [gap / error / missing_proof]
**Criticality**: [HIGH — Z downstream results depend on this]
**Description**: [Details]
**Recommended fix**: [Specific action]

---

## Assumption Analysis

| Assumption | Standard? | Frequency | Testable? | Reviewer Risk |
|-----------|-----------|-----------|-----------|---------------|
| A1: L-smoothness | Yes | Common | Yes | Low |
| A2: Bounded variance | Yes | Common | Partial | Low |
| A3: Custom condition | No | Novel | No | High |

---

## Bounds Analysis

| Bound | Expression | Known Optimal | Verdict |
|-------|-----------|---------------|---------|
| B1 | O(1/T²) | Ω(1/T²) | OPTIMAL |
| B2 | O(d²/ε²) | Ω(d/ε²) | SUBOPTIMAL |

---

## Notation Consistency

| Issue | Severity | Description |
|-------|----------|-------------|
| Overloaded θ | Critical | Two meanings in Sections 3 and 5 |
| Undefined d | Major | First used line 33, never defined |

---

## Dependency Graph Summary

**Most critical nodes**: [List top 3 by criticality score]
**Orphan lemmas**: [Any proved but unused]
**Missing proofs**: [Any theorems without proofs]

---

## Recommendations (Priority Order)

### High Priority
1. [Fix critical issue]
2. [Fix critical issue]

### Medium Priority
3. [Address gap]
4. [Strengthen assumption]

### Low Priority
5. [Notation cleanup]
6. [Style improvement]

---

## Subagent Execution Log

| Agent | Count | Succeeded | Failed | Total Time |
|-------|-------|-----------|--------|------------|
| proof-step-extractor | [N] | [N] | [N] | [Xs] |
| proof-step-verifier | [N] | [N] | [N] | [Xs] |
| assumption-analyzer | [N] | [N] | [N] | [Xs] |

| notation-consistency-checker | 1 | [0/1] | [0/1] | [Xs] |
| bounds-analyst | 1 | [0/1] | [0/1] | [Xs] |
| theorem-dependency-mapper | 1 | [0/1] | [0/1] | [Xs] |
```

## Performance Expectations

Two-stage fan-out limits how much concurrency helps here: Phase 3 cannot start
until Phase 2 finishes, so the two stages add rather than overlap. Setup and
merge stay sequential on top of that. No figure is published, because none was
measured.

## Integration

### Called By
- `proof-auditor` agent (parallel mode)
- User directly for comprehensive theory audit

### Calls
- `state-generator` (with theory parsing)
- `theorem-dependency-mapper`
- `proof-step-extractor` (N instances)
- `proof-step-verifier` (K instances)
- `assumption-analyzer` (M instances)

- `notation-consistency-checker` (1 instance)
- `bounds-analyst` (1 instance)

### Updates
- Writes audit results to `research-state.json` theory section
- Creates `theory-audit-report.md` in paper directory
