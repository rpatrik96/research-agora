---
name: evidence-grader
description: |
  Grade evidence strength for a single claim. Takes claim + evidence references,
  returns strength level (L1-L6) and venue compliance. Trigger: "grade evidence for claim".
model: sonnet
color: gray
---

# Micro-Skill: Evidence Grader

> **LLM-required**: Grading evidence requires judgment about experimental rigor. No script alternative.

> **One-line description**: Assess the strength of evidence supporting a single claim using a 6-level hierarchy.

## Purpose

This skill evaluates how well a claim is supported by its evidence. It assigns a strength level (L1-L6), identifies issues, and checks compliance with venue-specific standards. This is the core verification step in claim auditing.

## Parallelization Properties

| Property | Value |
|----------|-------|
| **Input scope** | Single claim + its evidence |
| **State requirements** | Needs evidence content |
| **External calls** | None |
| **Typical runtime** | 10-30s |
| **Can run in parallel** | Yes |

## Input Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["claim", "evidence"],
  "properties": {
    "claim": {
      "type": "object",
      "required": ["id", "text", "type"],
      "properties": {
        "id": {"type": "string"},
        "text": {"type": "string"},
        "type": {"type": "string", "enum": ["empirical", "theoretical", "methodological", "comparative", "novelty", "assumed"]}
      }
    },
    "evidence": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["type", "ref", "content"],
        "properties": {
          "type": {"type": "string", "enum": ["table", "figure", "equation", "algorithm", "theorem", "text", "citation", "code"]},
          "ref": {"type": "string"},
          "content": {"type": "string", "description": "The actual evidence content (table data, figure description, proof text, etc.)"}
        }
      }
    },
    "venue_target": {
      "type": "string",
      "enum": ["neurips", "icml", "iclr", "aaai", "cvpr", "acl", "workshop", "arxiv", "other"],
      "default": "neurips"
    }
  }
}
```

### Example Input

```json
{
  "claim": {
    "id": "C1",
    "text": "Our method achieves 96.2% accuracy on CIFAR-10",
    "type": "empirical"
  },
  "evidence": [
    {
      "type": "table",
      "ref": "tab1",
      "content": "Method | CIFAR-10\nResNet-50 | 94.1 ± 0.2\nOurs | 96.2 ± 0.3"
    }
  ],
  "venue_target": "neurips"
}
```

## Output Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["claim_id", "overall_strength", "overall_label", "verdict"],
  "properties": {
    "claim_id": {"type": "string"},
    "evidence_assessment": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "ref": {"type": "string"},
          "strength": {"type": "integer", "minimum": 1, "maximum": 6},
          "strength_label": {"type": "string"},
          "justification": {"type": "string"},
          "issues": {"type": "array", "items": {"type": "string"}}
        }
      }
    },
    "overall_strength": {
      "type": "integer",
      "minimum": 1,
      "maximum": 6
    },
    "overall_label": {
      "type": "string",
      "enum": ["CODE_VERIFIED", "REPRODUCIBLE_EXPERIMENT", "PAPER_EVIDENCE", "CITATION_SUPPORT", "LOGICAL_ARGUMENT", "ASSERTION"]
    },
    "verdict": {
      "type": "string",
      "enum": ["verified", "weak", "unsupported"]
    },
    "recommendations": {
      "type": "array",
      "items": {"type": "string"}
    },
    "meets_venue_standard": {"type": "boolean"},
    "venue_gap_notes": {"type": "string"}
  }
}
```

### Example Output

```json
{
  "claim_id": "C1",
  "evidence_assessment": [
    {
      "ref": "tab1",
      "strength": 2,
      "strength_label": "REPRODUCIBLE_EXPERIMENT",
      "justification": "Table shows results with standard deviation (± 0.3), indicating multiple runs",
      "issues": ["Number of seeds not specified", "No statistical significance test"]
    }
  ],
  "overall_strength": 2,
  "overall_label": "REPRODUCIBLE_EXPERIMENT",
  "verdict": "verified",
  "recommendations": [
    "Add footnote specifying number of seeds (recommend 5+)",
    "Consider adding statistical significance test (e.g., paired t-test)"
  ],
  "meets_venue_standard": true,
  "venue_gap_notes": "Meets NeurIPS empirical claim standard (L2). Minor improvements would strengthen."
}
```

## Evidence Hierarchy

| Level | Label | Description | Quality Indicators |
|-------|-------|-------------|-------------------|
| **L1** | CODE_VERIFIED | Claim traceable to reproducible code | GitHub link, notebooks, Docker |
| **L2** | REPRODUCIBLE_EXPERIMENT | Multiple seeds, error bars, significance | ± values, seeds, p-values |
| **L3** | PAPER_EVIDENCE | Tables/figures present, single run | Results shown but no variance |
| **L4** | CITATION_SUPPORT | Supported by peer-reviewed citation | Cited work makes same claim |
| **L5** | LOGICAL_ARGUMENT | Informal reasoning, intuition | "It follows that...", "Intuitively..." |
| **L6** | ASSERTION | No explicit support | Stated without evidence |

## Venue Standards

### Tier 1 Venues (NeurIPS, ICML, ICLR)

| Claim Type | Required Level | Notes |
|------------|----------------|-------|
| Empirical | L1-L2 | Must have error bars, prefer code |
| Theoretical | L2 | Formal proof required |
| Comparative | L2 | Statistical significance preferred |
| Novelty | L4 | Thorough literature search |

### Tier 2 Venues (AAAI, CVPR, ACL)

| Claim Type | Required Level | Notes |
|------------|----------------|-------|
| Empirical | L2-L3 | Error bars recommended |
| Theoretical | L3 | Proof sketch acceptable |
| Comparative | L3 | Comparison table sufficient |
| Novelty | L4-L5 | Related work coverage |

### Workshops & ArXiv

| Claim Type | Required Level | Notes |
|------------|----------------|-------|
| Empirical | L3-L4 | Preliminary results OK |
| Theoretical | L4-L5 | Informal argument OK |
| Novelty | L5 | Brief positioning |

## Algorithm

1. **Assess each evidence item**
   - Determine evidence type (quantitative/qualitative)
   - Check quality indicators (error bars, seeds, proofs)
   - Assign strength level
   - Document issues

2. **Compute overall strength**
   - For single evidence: use that strength
   - For multiple: use minimum (weakest link)
   - Exception: code + paper evidence = L1

3. **Determine verdict**
   - L1-L3: "verified"
   - L4: "verified" (assumed claims) or "weak" (empirical)
   - L5-L6: "unsupported" (for critical claims) or "weak" (for minor)

4. **Check venue compliance**
   - Compare overall strength to venue requirement
   - Note any gaps

5. **Generate recommendations**
   - Specific actions to improve evidence
   - Prioritize by impact

## Quality Indicators

### For Tables (Empirical Claims)

| Indicator | Points To | Impact |
|-----------|-----------|--------|
| `±` or `std` present | Multiple runs | +1 level |
| `p < 0.05` or significance | Statistical test | +1 level |
| `n=` sample size | Proper methodology | Supports L2 |
| Seeds specified | Reproducibility | Supports L2 |
| Bold/underline for best | Comparison done | Supports claim |

### For Theorems (Theoretical Claims)

| Indicator | Points To | Impact |
|-----------|-----------|--------|
| `\begin{proof}` | Formal proof | L2 |
| "Proof sketch" | Partial proof | L3 |
| "See appendix" | Full proof elsewhere | L2 if exists |
| QED symbol | Completed proof | L2 |
| References prior theorem | Building on established | L3-L4 |

### For Code (All Claims)

| Indicator | Points To | Impact |
|-----------|-----------|--------|
| GitHub link | Available code | Enables L1 |
| Docker/conda env | Reproducible env | Supports L1 |
| README with instructions | Usable code | Supports L1 |
| Tests present | Verified code | Strong L1 |

## Constraints

- **DO**: Assess each piece of evidence independently
- **DO**: Note specific missing quality indicators
- **DO**: Provide actionable recommendations
- **DON'T**: Search for external evidence (novelty-checker does that)
- **DON'T**: Modify the claim
- **DON'T**: Assess novelty (separate skill)

## Error Handling

| Error Condition | Response |
|-----------------|----------|
| No evidence provided | Assign L6 (ASSERTION), verdict "unsupported" |
| Evidence content empty | Note as issue, assess based on metadata only |
| Unknown claim type | Default to empirical standards |

## Context Requirements

| Context Item | Required | Source |
|--------------|----------|--------|
| Claim | Yes | Direct input |
| Evidence content | Yes | Extracted from paper |
| Venue target | No | Default: neurips |

## Examples

### Example 1: Weak Empirical Evidence

**Input**:
```json
{
  "claim": {
    "id": "C7",
    "text": "Our model outperforms all baselines",
    "type": "comparative"
  },
  "evidence": [
    {
      "type": "table",
      "ref": "tab3",
      "content": "Method | Accuracy\nBaseline A | 85.0\nBaseline B | 87.2\nOurs | 89.5"
    }
  ],
  "venue_target": "neurips"
}
```

**Output**:
```json
{
  "claim_id": "C7",
  "evidence_assessment": [
    {
      "ref": "tab3",
      "strength": 3,
      "strength_label": "PAPER_EVIDENCE",
      "justification": "Table shows comparison but no variance/error bars",
      "issues": [
        "No standard deviation or confidence intervals",
        "No indication of multiple runs",
        "No statistical significance test"
      ]
    }
  ],
  "overall_strength": 3,
  "overall_label": "PAPER_EVIDENCE",
  "verdict": "weak",
  "recommendations": [
    "Add error bars from multiple runs (5+ seeds recommended)",
    "Include statistical significance test (paired t-test or Wilcoxon)",
    "Report number of runs and seed selection method"
  ],
  "meets_venue_standard": false,
  "venue_gap_notes": "NeurIPS comparative claims require L2 (statistical significance). Current L3 evidence is insufficient."
}
```

### Example 2: Strong Theoretical Evidence

**Input**:
```json
{
  "claim": {
    "id": "C15",
    "text": "The algorithm converges to a global optimum",
    "type": "theoretical"
  },
  "evidence": [
    {
      "type": "theorem",
      "ref": "thm2",
      "content": "Theorem 2 (Global Convergence). Under Assumptions 1-3, Algorithm 1 converges to a global optimum almost surely. Proof. We proceed by showing... [full proof with QED]"
    }
  ],
  "venue_target": "icml"
}
```

**Output**:
```json
{
  "claim_id": "C15",
  "evidence_assessment": [
    {
      "ref": "thm2",
      "strength": 2,
      "strength_label": "REPRODUCIBLE_EXPERIMENT",
      "justification": "Formal theorem with complete proof. Assumptions clearly stated.",
      "issues": []
    }
  ],
  "overall_strength": 2,
  "overall_label": "REPRODUCIBLE_EXPERIMENT",
  "verdict": "verified",
  "recommendations": [],
  "meets_venue_standard": true,
  "venue_gap_notes": "Meets ICML theoretical claim standard with formal proof."
}
```

### Example 3: No Evidence (Assertion)

**Input**:
```json
{
  "claim": {
    "id": "C22",
    "text": "This is the most important problem in machine learning",
    "type": "assumed"
  },
  "evidence": [],
  "venue_target": "workshop"
}
```

**Output**:
```json
{
  "claim_id": "C22",
  "evidence_assessment": [],
  "overall_strength": 6,
  "overall_label": "ASSERTION",
  "verdict": "weak",
  "recommendations": [
    "Soften language: 'one of the important problems' instead of 'most important'",
    "Add citation to survey or position paper supporting importance",
    "Provide specific motivation for why this problem matters"
  ],
  "meets_venue_standard": false,
  "venue_gap_notes": "Even workshop papers should avoid unsupported superlative claims. Recommend softening or supporting with citations."
}
```

## Integration Notes

### Called By
- `parallel-audit` orchestrator (main verification step)
- Can be called directly for single-claim grading

### Calls
- None

### State Updates
- Updates claim `verification_status` in research-state.json
- Populates claim `verification_details` with strength and issues
