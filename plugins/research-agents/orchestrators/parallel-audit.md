---
name: parallel-audit
description: |
  Orchestrates parallel claim auditing across paper sections. Replaces
  sequential claim-auditor with fan-out/fan-in pattern for faster analysis.
  Trigger: "parallel audit", "fast claim audit", "audit paper claims".
model: opus
color: purple
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: verification
  verification-level: layered
---

# Orchestrator: Parallel Claim Audit

> **LLM-required**: Orchestrating parallel audits requires coordinating multiple analysis agents. No script alternative.

> **One-line description**: Coordinates parallel verification of all claims in a research paper using micro-skill subagents.

## Purpose

This orchestrator parallelizes claim verification by:
1. Generating research state (claims, structure, evidence)
2. Partitioning claims by type for parallel processing
3. Spawning specialized micro-skills for each claim
4. Merging results into a unified audit report

Expected speedup: **2-3x** for papers with >10 claims.

## Orchestration Pattern

```
Phase 1: Setup (Sequential, ~2 min)
├── Check for existing research-state.json
├── If missing: invoke state-generator
├── Load research state
├── Partition claims by type
├── Pre-fetch evidence content
└── Plan subagent allocation

Phase 2: Fan-Out (Parallel, ~3-5 min)
├── Empirical Claims Group
│   └── For each claim: spawn evidence-grader
├── Theoretical Claims Group
│   └── For each claim: spawn evidence-grader
├── Novelty Claims Group
│   └── For each claim: spawn novelty-checker
├── Comparative Claims Group
│   └── For each claim: spawn evidence-grader + novelty-checker
├── Citation Verification
│   └── For key citations: spawn citation-verifier
└── Assumption Surfacing
    └── For each section: spawn assumption-surfacer

Phase 3: Fan-In (Sequential, ~2 min)
├── Collect all subagent results
├── Merge into unified claim registry
├── Run cross-referencer for consistency
├── Calculate audit statistics
├── Aggregate recommendations
└── Generate final report
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
        "skip_novelty_check": {"type": "boolean", "default": false},
        "skip_citation_verify": {"type": "boolean", "default": false},
        "max_claims": {"type": "integer", "default": 50},
        "force_regenerate_state": {"type": "boolean", "default": false}
      }
    }
  }
}
```

## Claim Partitioning

```python
def partition_claims(research_state):
    """Partition claims by type for parallel processing."""
    partitions = {
        "empirical": [],      # → evidence-grader
        "theoretical": [],    # → evidence-grader
        "novelty": [],        # → novelty-checker
        "comparative": [],    # → evidence-grader + novelty-checker
        "methodological": [], # → evidence-grader
        "assumed": []         # → skip or minimal check
    }

    for claim in research_state["claims"]:
        partitions[claim["type"]].append(claim)

    return partitions
```

## Subagent Spawning

### For Empirical/Theoretical/Methodological Claims

```
SPAWN_SUBAGENT:
  skill: evidence-grader
  input:
    claim:
      id: {claim.id}
      text: {claim.text}
      type: {claim.type}
    evidence: [
      # Pre-fetched from evidence_map
      {type: "table", ref: "tab1", content: "..."}
    ]
    venue_target: {venue_target}
  context:
    - Relevant table/figure content (pre-fetched)
    - Section text containing claim
  timeout: 60s
  on_error: retry_once
```

### For Novelty Claims

```
SPAWN_SUBAGENT:
  skill: novelty-checker
  input:
    claim:
      id: {claim.id}
      text: {claim.text}
      keywords: [extracted keywords]
    paper_date: {metadata.generated_at}
    paper_arxiv_id: {metadata.arxiv_id}
  context:
    - Claim text only (minimal context)
  timeout: 120s
  on_error: mark_inconclusive
```

### For Comparative Claims (Dual Processing)

```
SPAWN_SUBAGENT:
  skill: evidence-grader
  input:
    claim: {claim}
    evidence: [comparison tables]
    venue_target: {venue_target}
  timeout: 60s

SPAWN_SUBAGENT:
  skill: novelty-checker
  input:
    claim: {claim}
    # Check if comparison baseline claims are accurate
  timeout: 120s
```

### For Key Citations

```
SPAWN_SUBAGENT:
  skill: citation-verifier
  input:
    citation: {citation_entry}
    claim_about_citation: {text referencing citation}
  timeout: 30s
  on_error: skip
```

### For Sections (Assumption Surfacing)

```
SPAWN_SUBAGENT:
  skill: assumption-surfacer
  input:
    section_id: {section.id}
    section_text: {section text}
    section_title: {section.title}
    claims_in_section: [claim IDs]
  context:
    - Section text only
  timeout: 45s
  on_error: skip
```

## Result Merging

### Claim Status Aggregation

```python
def merge_claim_results(grader_result, novelty_result=None):
    """Merge results from multiple subagents for a single claim."""
    result = {
        "claim_id": grader_result["claim_id"],
        "evidence_strength": grader_result["overall_strength"],
        "evidence_label": grader_result["overall_label"],
        "verdict": grader_result["verdict"],
        "issues": grader_result.get("evidence_assessment", [{}])[0].get("issues", []),
        "recommendations": grader_result.get("recommendations", []),
        "meets_venue_standard": grader_result.get("meets_venue_standard", True)
    }

    if novelty_result:
        result["novelty_status"] = novelty_result["novelty_verdict"]
        result["prior_work"] = novelty_result.get("prior_work", [])
        result["concurrent_work"] = novelty_result.get("concurrent_work", [])

        # Combine recommendations
        result["recommendations"].extend(novelty_result.get("recommendations", []))

    return result
```

### Conflict Resolution

| Conflict Type | Resolution Strategy |
|---------------|---------------------|
| Evidence-grader vs novelty-checker disagree | Trust novelty-checker for prior work; trust grader for evidence quality |
| Multiple graders for same claim | Take minimum strength (conservative) |
| Citation verifier finds error | Flag claim for review, add to recommendations |
| Cross-referencer finds inconsistency | Add to critical issues list |

### Statistics Calculation

```python
def calculate_statistics(merged_results):
    """Calculate audit summary statistics."""
    total = len(merged_results)
    verified = sum(1 for r in merged_results if r["verdict"] == "verified")
    weak = sum(1 for r in merged_results if r["verdict"] == "weak")
    unsupported = sum(1 for r in merged_results if r["verdict"] == "unsupported")
    novelty_challenged = sum(1 for r in merged_results
                            if r.get("novelty_status") == "challenged")

    return {
        "total_claims": total,
        "verified": verified,
        "verified_pct": round(100 * verified / total, 1) if total else 0,
        "weak_evidence": weak,
        "unsupported": unsupported,
        "novelty_challenged": novelty_challenged,
        "meets_venue": sum(1 for r in merged_results if r.get("meets_venue_standard", True))
    }
```

## Error Handling

| Error Type | Strategy |
|------------|----------|
| State generation fails | Abort with clear error message |
| Single claim grading fails | Mark as "audit_failed", continue with others |
| Novelty search times out | Mark as "inconclusive", add recommendation |
| Citation verification fails | Skip, note in report |
| >50% subagents fail | Abort, suggest sequential fallback |
| Cross-referencer fails | Skip consistency check, note limitation |

## Parallelism Limits

- **Maximum concurrent subagents**: 10
- **Maximum total subagents**: 50
- **If claims > 50**: Batch into groups of 50, process sequentially

### Batching Strategy

```python
def batch_claims(claims, batch_size=50):
    """Split claims into batches if too many."""
    for i in range(0, len(claims), batch_size):
        yield claims[i:i + batch_size]
```

## Output Format

```markdown
# Parallel Claim Audit Report

**Paper**: [Title]
**Audit Mode**: Parallel ([N] subagents, [M] seconds)
**State File**: research-state.json
**Venue Target**: [venue]

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Claims | [N] |
| Verified (L1-L3) | [N] ([%]) |
| Weak Evidence (L4-L5) | [N] ([%]) |
| Unsupported (L6) | [N] ([%]) |
| Novelty Challenged | [N] |
| Meets Venue Standard | [N] / [Total] |
| Assumptions Surfaced | [N] |
| Audit Failures | [N] |

## Critical Issues

### 1. [Issue Title]
- **Claim**: [C#] "[claim text]"
- **Problem**: [description]
- **Recommendation**: [action]

### 2. [Issue Title]
...

## Claim-by-Claim Results

### Empirical Claims

| ID | Claim | Evidence | Verdict | Issues |
|----|-------|----------|---------|--------|
| C1 | [text] | L2 | verified | [count] |
| C2 | [text] | L4 | weak | [count] |

### Novelty Claims

| ID | Claim | Status | Prior Work |
|----|-------|--------|------------|
| C3 | [text] | confirmed | - |
| C4 | [text] | challenged | [arxiv IDs] |

### Comparative Claims

| ID | Claim | Evidence | Novelty | Issues |
|----|-------|----------|---------|--------|
| C5 | [text] | L2 | confirmed | [count] |

## Assumptions Identified

| ID | Assumption | Section | Explicit | Severity |
|----|------------|---------|----------|----------|
| A1 | [text] | sec3 | No | moderate |

## Cross-Reference Check

[Consistency issues from cross-referencer, if any]

## Citation Verification

| Citation | Status | Issues |
|----------|--------|--------|
| [key] | verified | - |
| [key] | minor_issues | [description] |

## Aggregated Recommendations

### High Priority
1. [recommendation]
2. [recommendation]

### Medium Priority
1. [recommendation]

### Low Priority
1. [recommendation]

---
*Generated by parallel-audit orchestrator*
*Subagents: evidence-grader, novelty-checker, citation-verifier, assumption-surfacer, cross-referencer*
```

## Fallback Mode

If parallel execution is not available or >50% subagent failures:

```
FALLBACK: sequential-audit
  Invoke: claim-auditor (original sequential agent)
  Log: "Falling back to sequential audit due to [reason]"
  Note: Results will be slower but equivalent
```

## Performance Expectations

| Phase | Sequential | Parallel | Speedup |
|-------|------------|----------|---------|
| Setup | 2 min | 2 min | 1x |
| Analysis (20 claims) | 15 min | 4-5 min | 3x |
| Merge & Report | 1 min | 2 min | 0.5x |
| **Total** | **18 min** | **8-9 min** | **2x** |

*Note: Actual times depend on claim complexity and arXiv API latency.*

## Integration Notes

### Called By
- User: "audit paper claims", "parallel audit [path]"
- Refactored claim-auditor agent (auto-delegates)

### Calls (Subagents)
- `state-generator` (if research-state.json missing)
- `evidence-grader` (per empirical/theoretical/comparative claim)
- `novelty-checker` (per novelty claim)
- `citation-verifier` (for key citations)
- `assumption-surfacer` (per section)
- `cross-referencer` (final consistency check)

### State Updates
- Updates `research-state.json` with verification results
- Creates audit report in paper directory
- Caches results in `.research-cache/` for incremental updates
