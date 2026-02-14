---
name: pre-submission-audit
description: Comprehensive pre-submission paper audit combining reviewer simulation, claim verification, clarity analysis, notation checking, and statistical validation. Use when asked to "audit before submission", "pre-submission check", "is my paper ready", "self-review", or "submission readiness". Runs 5 diagnostic passes in parallel and produces a unified readiness report.
model: opus
color: red
metadata:
  research-domain: general
  research-phase: submission
  task-type: verification
  verification-level: layered
---

# Orchestrator: Pre-Submission Audit

> **LLM-required**: Coordinating five parallel diagnostic passes and synthesizing results into a unified readiness verdict requires judgment. No script alternative.

> **One-line description**: One command to assess submission readiness -- chains 5 diagnostic tools in parallel and produces a unified readiness report with go/no-go recommendation.

## Purpose

This orchestrator is the "self-review" you run before submitting a paper. It coordinates five independent diagnostic tools, each targeting a different dimension of paper quality, then synthesizes their outputs into a single actionable readiness report. It does NOT replace any individual tool -- it chains them.

**What it covers:**

| Pass | Tool | Dimension |
|------|------|-----------|
| 1 | `paper-review` | External reviewer simulation |
| 2 | `claim-auditor` | Evidence verification (L1-L6 hierarchy) |
| 3 | `clarity-optimizer` | Prose quality and readability |
| 4 | `notation-consistency-checker` | Symbol table and notation consistency |
| 5 | `statistical-validator` | Statistical rigor of experiments |

## Pipeline Architecture

```
Paper Input (all LaTeX files)
    |
    +---> paper-review (external reviewer simulation)
    +---> claim-auditor (evidence verification)
    +---> clarity-optimizer (prose quality)
    +---> notation-consistency-checker (notation/symbols)
    +---> statistical-validator (statistical rigor)
    |
    v
Synthesis --> Unified Readiness Report
```

All 5 passes run in PARALLEL using the Task tool with concurrent agents. No pass depends on the output of another.

## Input Specification

```json
{
  "type": "object",
  "required": ["paper_path"],
  "properties": {
    "paper_path": {
      "type": "string",
      "description": "Path to paper directory (LaTeX project root) or single .tex file"
    },
    "venue_target": {
      "type": "string",
      "enum": ["neurips", "icml", "iclr", "aaai", "cvpr", "acl", "workshop", "arxiv", "journal", "other"],
      "default": "neurips"
    },
    "skip_passes": {
      "type": "array",
      "items": {"type": "string", "enum": ["review", "claims", "clarity", "notation", "statistics"]},
      "default": [],
      "description": "Skip specific passes if already run recently"
    }
  }
}
```

## Workflow

### Phase 1: Setup — Paper Ingestion (Sequential, ~1 min)

```
1. Locate all LaTeX source files in paper_path
2. Read the complete paper (main .tex, all \input/\include files, appendix)
3. Identify paper title, target venue, and structure
4. Prepare shared context: full paper text available to all passes
```

### Phase 2: Fan-Out — Parallel Diagnostic Passes (Parallel, ~5-8 min)

Launch all 5 passes simultaneously using the Task tool (fan-out). Each pass receives the full paper text and venue target.

```
SPAWN_TASK: paper-review
  description: "Run paper-review on [paper_path] targeting [venue]. Simulate a skeptical reviewer. Return the full review with recommendation score, strengths, weaknesses, and prioritized fixes."
  skill: academic/paper-review
  input: Full paper text, venue target
  timeout: 300s

SPAWN_TASK: claim-auditor
  description: "Run claim-auditor on [paper_path] targeting [venue]. Extract all claims, classify by type, grade evidence level (L1-L6), and flag unsupported claims. Return the claim audit report."
  skill: research-agents/claim-auditor
  input: Full paper text, venue target, code path (if available)
  timeout: 300s

SPAWN_TASK: clarity-optimizer
  description: "Run clarity-optimizer on [paper_path]. Compute readability metrics, flag passive voice, undefined jargon, long sentences, and unclear antecedents. Return the clarity analysis report with score."
  skill: research-agents/clarity-optimizer
  input: Full paper text
  timeout: 180s

SPAWN_TASK: notation-consistency-checker
  description: "Run notation-consistency-checker on [paper_path]. Build a symbol table, detect overloaded symbols, undefined notation, and convention violations. Return the notation consistency report."
  skill: research-agents/notation-consistency-checker
  input: Full paper text (LaTeX source)
  timeout: 180s

SPAWN_TASK: statistical-validator
  description: "Run statistical-validator on [paper_path]. Check for missing error bars, significance tests, data leakage, single-seed results, and other statistical issues. Return the statistical validation report."
  skill: research-agents/statistical-validator
  input: Full paper text, experiment code (if available)
  timeout: 180s
```

### Phase 3: Fan-In — Result Collection (Sequential, ~30s)

```
1. Collect results from all 5 Task completions (fan-in)
2. Handle partial failures: if a pass fails, note it in the report and continue with remaining passes
3. Extract key metrics from each pass for the summary
4. Update orchestrator state with collected pass results
```

### Phase 4: Synthesis (Sequential, ~2 min)

```
1. Cross-reference findings across passes (e.g., claim-auditor flags unsupported claim + reviewer also flags it = higher severity)
2. Deduplicate issues reported by multiple passes
3. Assign unified severity: Critical > Major > Minor
4. Compute overall readiness verdict
5. Build prioritized action items sorted by severity then effort
6. Generate the unified report
```

### Verdict Logic

```python
def compute_verdict(pass_results):
    """Determine submission readiness from pass results."""
    critical_issues = count_critical(pass_results)
    reviewer_score = pass_results["review"]["recommendation"]
    claim_score = pass_results["claims"]["audit_score_pct"]
    clarity_score = pass_results["clarity"]["clarity_score"]

    if critical_issues > 0 or reviewer_score in ["Reject", "Weak Reject"]:
        return "NOT READY"
    elif (reviewer_score == "Borderline"
          or claim_score < 80
          or clarity_score < 60
          or pass_results["statistics"]["critical_count"] > 0):
        return "READY WITH MINOR FIXES"
    else:
        return "READY"
```

## Output Format

```markdown
## Pre-Submission Audit Report

**Paper**: [Title]
**Target venue**: [Venue]
**Date**: [Date]
**Verdict**: [READY / READY WITH MINOR FIXES / NOT READY]

### Executive Summary
[2-3 sentence overall assessment synthesizing findings from all 5 passes. Highlight the single biggest risk and the strongest aspect of the paper.]

### Pass Results

#### 1. Reviewer Simulation
**Score**: [Accept / Weak Accept / Borderline / Weak Reject / Reject]
**Critical issues**: [N]
**Top concern**: [Issue]

#### 2. Claim Verification
**Claims audited**: [N]
**Unsupported claims**: [N]
**Weakest claim**: [Claim + evidence level]

#### 3. Clarity Analysis
**Clarity score**: [N/100]
**Passive voice**: [N%]
**Undefined jargon**: [N terms]

#### 4. Notation Consistency
**Inconsistencies found**: [N]
**Critical**: [List]

#### 5. Statistical Rigor
**Issues found**: [N]
**Missing error bars**: [Y/N]
**Missing significance tests**: [Y/N]

### Prioritized Action Items
| # | Issue | Source | Severity | Effort | Section |
|---|-------|--------|----------|--------|---------|
| 1 | [Issue] | [Which pass] | Critical | [Time] | [Section] |
| 2 | [Issue] | [Which pass] | Critical | [Time] | [Section] |
| 3 | [Issue] | [Which pass] | Major | [Time] | [Section] |
| ... | | | | | |

### Submission Readiness Checklist
- [ ] All claims supported (L1-L3 evidence)
- [ ] No undefined notation
- [ ] Clarity score >70
- [ ] Statistical tests complete
- [ ] No critical reviewer concerns
```

## Venue-Specific Calibration

Standards adjust based on target venue:

| Criterion | NeurIPS/ICML/ICLR | AAAI/CVPR/ACL | Workshop | Journal |
|-----------|-------------------|---------------|----------|---------|
| Evidence level required | L1-L2 for main claims | L2-L3 acceptable | L3-L4 acceptable | L1-L2 with full reproduction |
| Random seeds | 5+ with CI | 3+ with std | 1+ acknowledged | 5+ with significance tests |
| Clarity score threshold | 70+ | 65+ | 60+ | 75+ |
| Notation rigor | No overloading | Minor overloading OK | Relaxed | No overloading |
| Reviewer bar | Weak Accept+ | Borderline+ | Borderline+ | Accept |
| Ablation depth | Every claimed contribution | Key contributions | Optional | Comprehensive |

The verdict logic and action item severity adapt to these thresholds.

## Error Handling

| Error | Strategy |
|-------|----------|
| One pass fails | Report partial results, note missing pass, continue with 4/5 |
| Two+ passes fail | Report available results, warn that audit is incomplete |
| Paper cannot be parsed | Abort with clear error, suggest checking LaTeX compilation |
| No experiments section | Skip statistical-validator, note in report |
| No math content | Skip notation-consistency-checker, note in report |

## Important Constraints

1. **Diagnosis only**: This orchestrator NEVER modifies the paper. It only reads and reports.

2. **No redundant work**: If the user has already run an individual pass recently, use `skip_passes` to avoid re-running it.

3. **Standalone follow-up**: For detailed investigation of any individual pass, run that tool directly. This orchestrator produces summaries, not full individual reports.

4. **Cross-referencing adds value**: The synthesis phase should identify issues flagged by multiple passes (convergent evidence of a problem) and elevate their priority.

5. **Actionable output**: Every item in the prioritized action list must specify what to fix, where to fix it, and estimated effort. Vague recommendations like "improve clarity" are not acceptable.

## Performance Expectations

| Phase | Duration | Notes |
|-------|----------|-------|
| Paper ingestion | ~1 min | Depends on paper length |
| Parallel passes | ~5-8 min | Bounded by slowest pass (usually paper-review or claim-auditor) |
| Result collection | ~30s | Waiting for stragglers |
| Synthesis | ~2 min | Cross-referencing and report generation |
| **Total** | **~8-12 min** | vs ~25-35 min running all 5 sequentially |

## Integration Notes

### Called By
- User: "audit before submission", "pre-submission check", "is my paper ready", "self-review", "submission readiness"
- Can be invoked as final step of a writing workflow

### Calls (Parallel Subagents)
- `paper-review` (academic plugin, reviewer simulation)
- `claim-auditor` (research-agents, evidence verification)
- `clarity-optimizer` (research-agents, prose quality)
- `notation-consistency-checker` (research-agents, notation)
- `statistical-validator` (research-agents, statistical rigor)

### Does NOT Call
- Any paper modification or rewriting tools
- Any external APIs beyond what individual passes use internally

---
*Generated by pre-submission-audit orchestrator*
*Passes: paper-review, claim-auditor, clarity-optimizer, notation-consistency-checker, statistical-validator*
