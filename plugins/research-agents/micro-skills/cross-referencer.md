---
name: cross-referencer
description: |
  Check cross-section consistency of claims. Identifies contradictions,
  inconsistencies, and unsupported references between sections.
  Trigger: "check consistency", "cross-reference claims", "find contradictions".
model: sonnet
color: gray
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: verification
  verification-level: heuristic
---

# Micro-Skill: Cross-Referencer

> **Hybrid**: Finding cross-references uses grep for labels/refs. LLM checks semantic consistency between referenced elements.

> **One-line description**: Check consistency of claims and statements across different paper sections.

## Purpose

This skill identifies inconsistencies between different parts of a paper. Common issues include: abstract claims not matching results, methodology descriptions inconsistent with experiments, and numbers that don't match between sections. These issues often catch reviewers' attention and should be fixed.

## Parallelization Properties

| Property | Value |
|----------|-------|
| **Input scope** | Multiple claims or full paper |
| **State requirements** | Needs research-state.json |
| **External calls** | None |
| **Typical runtime** | 10-30s |
| **Can run in parallel** | No (needs full context) |

## Input Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["claims"],
  "properties": {
    "claims": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "text", "location"],
        "properties": {
          "id": {"type": "string"},
          "text": {"type": "string"},
          "location": {
            "type": "object",
            "properties": {
              "section": {"type": "string"}
            }
          },
          "type": {"type": "string"}
        }
      }
    },
    "structure": {
      "type": "object",
      "description": "Paper structure from research-state.json"
    },
    "evidence_map": {
      "type": "object",
      "description": "Evidence mappings"
    }
  }
}
```

### Example Input

```json
{
  "claims": [
    {
      "id": "C1",
      "text": "Our method achieves 95% accuracy on ImageNet",
      "location": {"section": "abstract"},
      "type": "empirical"
    },
    {
      "id": "C5",
      "text": "Table 1 shows our model reaches 94.8% top-1 accuracy",
      "location": {"section": "sec5"},
      "type": "empirical"
    }
  ],
  "evidence_map": {
    "C1": [{"type": "table", "ref": "tab1"}],
    "C5": [{"type": "table", "ref": "tab1"}]
  }
}
```

## Output Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["consistency_issues"],
  "properties": {
    "consistency_issues": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["type", "severity", "claims_involved"],
        "properties": {
          "id": {"type": "string"},
          "type": {
            "type": "string",
            "enum": ["numerical_mismatch", "claim_contradiction", "missing_support", "scope_inconsistency", "terminology_inconsistency"]
          },
          "severity": {
            "type": "string",
            "enum": ["critical", "major", "minor"]
          },
          "claims_involved": {
            "type": "array",
            "items": {"type": "string"}
          },
          "description": {"type": "string"},
          "evidence": {"type": "string"},
          "recommendation": {"type": "string"}
        }
      }
    },
    "consistency_score": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Overall consistency (1 = fully consistent)"
    },
    "summary": {
      "type": "object",
      "properties": {
        "total_issues": {"type": "integer"},
        "critical_issues": {"type": "integer"},
        "claims_checked": {"type": "integer"}
      }
    }
  }
}
```

### Example Output

```json
{
  "consistency_issues": [
    {
      "id": "I1",
      "type": "numerical_mismatch",
      "severity": "major",
      "claims_involved": ["C1", "C5"],
      "description": "Abstract claims 95% accuracy but results section reports 94.8%",
      "evidence": "C1 says '95%', C5 says '94.8%'",
      "recommendation": "Update abstract to match exact figure from results (94.8%) or clarify if rounding"
    }
  ],
  "consistency_score": 0.85,
  "summary": {
    "total_issues": 1,
    "critical_issues": 0,
    "claims_checked": 2
  }
}
```

## Algorithm

1. **Group related claims**
   - By topic (same metric, dataset, method)
   - By evidence (same table/figure reference)
   - By temporal relationship (abstract → results)

2. **Check numerical consistency**
   - Extract all numbers from related claims
   - Flag mismatches (even minor rounding differences)
   - Consider context (rounded vs exact)

3. **Check logical consistency**
   - Claims about same topic should not contradict
   - Scope should be consistent (all datasets vs specific)
   - Qualitative claims should match quantitative

4. **Check evidence support**
   - Claims referencing same evidence should be consistent
   - Evidence should support all related claims

5. **Check terminology consistency**
   - Same concepts should use same terms
   - Abbreviations should be consistent

6. **Generate issues and recommendations**
   - Prioritize by severity
   - Provide specific fix suggestions

## Issue Types

### Numerical Mismatch

| Pattern | Example | Severity |
|---------|---------|----------|
| Different exact values | "95%" vs "94.8%" | major |
| Different rounding | "95%" vs "95.2%" | minor |
| Different metrics | "accuracy" vs "F1" | major |
| Missing decimal | "95" vs "95.0%" | minor |

### Claim Contradiction

| Pattern | Example | Severity |
|---------|---------|----------|
| Direct contradiction | "outperforms" vs "comparable to" | critical |
| Scope mismatch | "all datasets" vs "CIFAR-10" | major |
| Condition mismatch | "always converges" vs "converges under X" | major |

### Missing Support

| Pattern | Example | Severity |
|---------|---------|----------|
| Claim in abstract, no result | "achieves X" but no evidence | critical |
| Forward reference unfulfilled | "see Section 5" but not there | major |
| Orphan evidence | Table exists but not referenced | minor |

### Scope Inconsistency

| Pattern | Example | Severity |
|---------|---------|----------|
| Overgeneralization | "works for all X" but tested on one | major |
| Undergeneralization | Results broader than claim | minor |

### Terminology Inconsistency

| Pattern | Example | Severity |
|---------|---------|----------|
| Different names for same thing | "our method" vs "proposed approach" vs "Model X" | minor |
| Abbreviation inconsistency | "LLM" vs "large language model" after definition | minor |
| Undefined terms | Using term before definition | minor |

## Section Relationships

Typical claim flow and expected consistency:

```
Abstract → Introduction → Methods → Results → Discussion → Conclusion
   ↓           ↓            ↓         ↓          ↓           ↓
Claims     Expanded     Details   Numbers    Caveats    Restate
(high)     claims                 (exact)              (match abstract)
```

### Expected Consistency Patterns

| From | To | Check |
|------|-----|-------|
| Abstract | Results | Numbers must match |
| Abstract | Conclusion | Claims should match |
| Introduction | Methods | Method description consistent |
| Methods | Results | Procedure matches experiments |
| Results | Discussion | Interpretation matches numbers |

## Constraints

- **DO**: Check all claim pairs that might be related
- **DO**: Extract and compare exact numbers
- **DO**: Flag even minor inconsistencies
- **DO**: Provide specific fix recommendations
- **DON'T**: Change claim text
- **DON'T**: Verify claim truth (just consistency)
- **DON'T**: Access external resources

## Error Handling

| Error Condition | Response |
|-----------------|----------|
| Single claim | Return no issues (nothing to compare) |
| No related claims found | Return empty issues, note in summary |
| Ambiguous relationship | Flag as potential issue, low severity |

## Context Requirements

| Context Item | Required | Source |
|--------------|----------|--------|
| Claims | Yes | research-state.json |
| Evidence map | Recommended | research-state.json |
| Structure | Recommended | For section context |

## Examples

### Example 1: Multiple Issues

**Input**:
```json
{
  "claims": [
    {"id": "C1", "text": "We propose a novel attention mechanism", "location": {"section": "abstract"}, "type": "novelty"},
    {"id": "C2", "text": "Our method achieves state-of-the-art on all benchmarks", "location": {"section": "abstract"}, "type": "comparative"},
    {"id": "C3", "text": "Building on existing attention mechanisms, we...", "location": {"section": "sec1"}, "type": "methodological"},
    {"id": "C8", "text": "Table 1 shows SOTA results on 3 of 5 benchmarks", "location": {"section": "sec5"}, "type": "empirical"}
  ]
}
```

**Output**:
```json
{
  "consistency_issues": [
    {
      "id": "I1",
      "type": "claim_contradiction",
      "severity": "major",
      "claims_involved": ["C1", "C3"],
      "description": "Abstract claims 'novel' attention but introduction says 'building on existing'",
      "evidence": "C1: 'novel attention mechanism', C3: 'Building on existing attention mechanisms'",
      "recommendation": "Clarify novelty: either 'novel combination/application of' or specify what's new vs existing"
    },
    {
      "id": "I2",
      "type": "scope_inconsistency",
      "severity": "critical",
      "claims_involved": ["C2", "C8"],
      "description": "Abstract claims SOTA on 'all' benchmarks but results show only 3 of 5",
      "evidence": "C2: 'all benchmarks', C8: '3 of 5 benchmarks'",
      "recommendation": "Update abstract: 'achieves state-of-the-art on most benchmarks' or 'competitive results across benchmarks'"
    }
  ],
  "consistency_score": 0.65,
  "summary": {
    "total_issues": 2,
    "critical_issues": 1,
    "claims_checked": 4
  }
}
```

### Example 2: Fully Consistent

**Input**:
```json
{
  "claims": [
    {"id": "C1", "text": "Our model achieves 94.8% accuracy on ImageNet", "location": {"section": "abstract"}, "type": "empirical"},
    {"id": "C2", "text": "We report 94.8% top-1 accuracy (Table 1)", "location": {"section": "sec5"}, "type": "empirical"},
    {"id": "C3", "text": "In summary, we demonstrated 94.8% ImageNet accuracy", "location": {"section": "sec7"}, "type": "empirical"}
  ]
}
```

**Output**:
```json
{
  "consistency_issues": [],
  "consistency_score": 1.0,
  "summary": {
    "total_issues": 0,
    "critical_issues": 0,
    "claims_checked": 3
  }
}
```

### Example 3: Terminology Inconsistency

**Input**:
```json
{
  "claims": [
    {"id": "C1", "text": "We propose TransNet for image classification", "location": {"section": "abstract"}},
    {"id": "C3", "text": "Our transformer model processes images...", "location": {"section": "sec3"}},
    {"id": "C5", "text": "The proposed architecture achieves...", "location": {"section": "sec5"}}
  ]
}
```

**Output**:
```json
{
  "consistency_issues": [
    {
      "id": "I1",
      "type": "terminology_inconsistency",
      "severity": "minor",
      "claims_involved": ["C1", "C3", "C5"],
      "description": "Model referred to as 'TransNet', 'transformer model', and 'proposed architecture'",
      "evidence": "Three different names used for same model",
      "recommendation": "Use consistent name throughout. Suggestion: 'TransNet' (as named in abstract) or 'our model'"
    }
  ],
  "consistency_score": 0.90,
  "summary": {
    "total_issues": 1,
    "critical_issues": 0,
    "claims_checked": 3
  }
}
```

## Integration Notes

### Called By
- `parallel-audit` orchestrator (final consistency check)
- Can be called directly after claim extraction

### Calls
- None

### State Updates
- Adds `consistency_issues` to research-state.json
- May flag claims with inconsistency warnings
