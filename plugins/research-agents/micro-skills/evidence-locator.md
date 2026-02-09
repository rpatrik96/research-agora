---
name: evidence-locator
description: |
  Find evidence (tables, figures, equations, citations) that support a claim.
  Searches within paper structure for matching references.
  Trigger: "locate evidence for claim", "find supporting evidence".
model: haiku
color: gray
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: analysis
  verification-level: layered
---

# Micro-Skill: Evidence Locator

> **Hybrid**: Evidence location uses grep/search for figures, tables, and code. LLM maps claims to specific evidence artifacts.

> **One-line description**: Find all evidence elements (tables, figures, equations, citations) that support a given claim.

## Purpose

This skill identifies what evidence exists in the paper to support a specific claim. It examines explicit references in the claim text (e.g., "see Table 1") and searches for implicit supporting evidence based on claim content. Output is used by evidence-grader to assess strength.

## Parallelization Properties

| Property | Value |
|----------|-------|
| **Input scope** | Single claim + paper structure |
| **State requirements** | Needs research-state.json structure |
| **External calls** | None |
| **Typical runtime** | <10s |
| **Can run in parallel** | Yes |

## Input Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["claim", "paper_structure"],
  "properties": {
    "claim": {
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
    },
    "paper_structure": {
      "type": "object",
      "description": "Structure from research-state.json",
      "properties": {
        "figures": {"type": "array"},
        "tables": {"type": "array"},
        "equations": {"type": "array"},
        "algorithms": {"type": "array"},
        "theorems": {"type": "array"}
      }
    },
    "citations": {
      "type": "array",
      "description": "Bibliography entries"
    },
    "section_text": {
      "type": "string",
      "description": "Full text of section containing claim (optional, for context search)"
    }
  }
}
```

### Example Input

```json
{
  "claim": {
    "id": "C5",
    "text": "Our model achieves 95.2% accuracy on ImageNet (Table 1)",
    "location": {"section": "sec4"},
    "type": "empirical"
  },
  "paper_structure": {
    "tables": [
      {"id": "tab1", "caption": "Main results on ImageNet and CIFAR-10"},
      {"id": "tab2", "caption": "Ablation study results"}
    ],
    "figures": [
      {"id": "fig1", "caption": "Model architecture"},
      {"id": "fig2", "caption": "Training curves"}
    ]
  }
}
```

## Output Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["claim_id", "evidence_found"],
  "properties": {
    "claim_id": {"type": "string"},
    "evidence_found": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["type", "ref", "match_type"],
        "properties": {
          "type": {
            "type": "string",
            "enum": ["table", "figure", "equation", "algorithm", "theorem", "citation", "text", "code"]
          },
          "ref": {
            "type": "string",
            "description": "Reference ID (e.g., 'tab1', 'fig2')"
          },
          "match_type": {
            "type": "string",
            "enum": ["explicit", "implicit", "contextual"],
            "description": "How the evidence was matched"
          },
          "match_confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          },
          "caption": {
            "type": "string",
            "description": "Caption or description of evidence"
          },
          "relevance_note": {
            "type": "string",
            "description": "Why this evidence is relevant"
          }
        }
      }
    },
    "search_summary": {
      "type": "object",
      "properties": {
        "explicit_refs_found": {"type": "integer"},
        "implicit_matches": {"type": "integer"},
        "total_evidence": {"type": "integer"}
      }
    },
    "no_evidence_note": {
      "type": "string",
      "description": "Explanation if no evidence found"
    }
  }
}
```

### Example Output

```json
{
  "claim_id": "C5",
  "evidence_found": [
    {
      "type": "table",
      "ref": "tab1",
      "match_type": "explicit",
      "match_confidence": 1.0,
      "caption": "Main results on ImageNet and CIFAR-10",
      "relevance_note": "Explicitly referenced as 'Table 1' in claim text"
    },
    {
      "type": "figure",
      "ref": "fig2",
      "match_type": "implicit",
      "match_confidence": 0.7,
      "caption": "Training curves",
      "relevance_note": "Training curves may show accuracy progression"
    }
  ],
  "search_summary": {
    "explicit_refs_found": 1,
    "implicit_matches": 1,
    "total_evidence": 2
  }
}
```

## Algorithm

1. **Extract explicit references**
   - Search claim text for patterns:
     - "Table N" / "Tab. N" / "table N"
     - "Figure N" / "Fig. N" / "figure N"
     - "Equation N" / "Eq. N" / "(N)"
     - "Algorithm N" / "Alg. N"
     - "Theorem N" / "Lemma N"
     - Citation keys: "[N]", "\cite{key}"
   - Map to structure IDs with confidence 1.0

2. **Search for implicit evidence**
   - For empirical claims: Find tables with matching metrics/datasets
   - For theoretical claims: Find theorems/equations in same section
   - For comparative claims: Find comparison tables
   - For methodological claims: Find algorithm blocks
   - Assign confidence 0.5-0.8 based on match quality

3. **Contextual search** (if section_text provided)
   - Look for evidence referenced near claim location
   - Check sentences before/after claim
   - Lower confidence (0.3-0.6)

4. **Rank and deduplicate**
   - Remove duplicates (same ref found multiple ways)
   - Keep highest confidence match
   - Sort by confidence descending

## Reference Patterns

### Explicit Reference Patterns

| Pattern | Maps To | Example |
|---------|---------|---------|
| `Table \d+` / `Tab\. \d+` | table | "Table 1 shows..." |
| `Figure \d+` / `Fig\. \d+` | figure | "...see Figure 2" |
| `Equation \d+` / `Eq\. \d+` / `\(\d+\)` | equation | "by Equation (3)" |
| `Algorithm \d+` / `Alg\. \d+` | algorithm | "Algorithm 1 details..." |
| `Theorem \d+` / `Lemma \d+` | theorem | "By Theorem 2" |
| `\[\d+\]` / `\cite\{.*\}` | citation | "[15] showed..." |

### Implicit Evidence Matching

| Claim Type | Evidence Type | Match Criteria |
|------------|---------------|----------------|
| empirical | table | Caption mentions same metric/dataset |
| empirical | figure | Caption mentions results/comparison |
| theoretical | theorem | Same section, formal statement |
| theoretical | equation | Same section, key equation |
| methodological | algorithm | Same section, describes approach |
| comparative | table | Caption mentions comparison/baseline |
| novelty | citation | Cited as related/prior work |

## Constraints

- **DO**: Find all explicit references in claim text
- **DO**: Search for implicit evidence in same section
- **DO**: Provide relevance explanation for each match
- **DON'T**: Grade evidence strength (that's evidence-grader's job)
- **DON'T**: Read actual table/figure content (just metadata)
- **DON'T**: Access external resources

## Error Handling

| Error Condition | Response |
|-----------------|----------|
| No paper_structure provided | `{"error": "Paper structure required", "code": "MISSING_STRUCTURE"}` |
| Referenced element not found | Include in output with `match_confidence: 0` and note |
| No evidence found | Return empty `evidence_found` with `no_evidence_note` explanation |

## Context Requirements

| Context Item | Required | Source |
|--------------|----------|--------|
| Claim | Yes | Direct input |
| Paper structure | Yes | research-state.json |
| Section text | No | Improves implicit matching |

## Examples

### Example 1: Theoretical Claim

**Input**:
```json
{
  "claim": {
    "id": "C8",
    "text": "Our algorithm converges in O(1/t) rate (Theorem 1)",
    "location": {"section": "sec3"},
    "type": "theoretical"
  },
  "paper_structure": {
    "theorems": [
      {"id": "thm1", "type": "theorem", "statement": "Under Assumptions 1-3, Algorithm 1 converges at O(1/t) rate", "has_proof": true}
    ],
    "equations": [
      {"id": "eq5", "label": "convergence", "section": "sec3"}
    ]
  }
}
```

**Output**:
```json
{
  "claim_id": "C8",
  "evidence_found": [
    {
      "type": "theorem",
      "ref": "thm1",
      "match_type": "explicit",
      "match_confidence": 1.0,
      "caption": "Under Assumptions 1-3, Algorithm 1 converges at O(1/t) rate",
      "relevance_note": "Explicitly referenced as 'Theorem 1', states exact convergence rate claimed"
    },
    {
      "type": "equation",
      "ref": "eq5",
      "match_type": "implicit",
      "match_confidence": 0.65,
      "caption": "convergence",
      "relevance_note": "Equation labeled 'convergence' in same section, likely supports theorem"
    }
  ],
  "search_summary": {
    "explicit_refs_found": 1,
    "implicit_matches": 1,
    "total_evidence": 2
  }
}
```

### Example 2: No Evidence Found

**Input**:
```json
{
  "claim": {
    "id": "C3",
    "text": "Our approach is the first to solve this problem",
    "location": {"section": "sec1"},
    "type": "novelty"
  },
  "paper_structure": {
    "tables": [],
    "figures": []
  },
  "citations": []
}
```

**Output**:
```json
{
  "claim_id": "C3",
  "evidence_found": [],
  "search_summary": {
    "explicit_refs_found": 0,
    "implicit_matches": 0,
    "total_evidence": 0
  },
  "no_evidence_note": "Novelty claim with no explicit references. Requires literature search (novelty-checker skill) to verify no prior work exists."
}
```

### Example 3: Multiple Evidence Types

**Input**:
```json
{
  "claim": {
    "id": "C12",
    "text": "As shown in Figure 3 and Table 2, our method consistently outperforms baselines across all datasets",
    "location": {"section": "sec4"},
    "type": "comparative"
  },
  "paper_structure": {
    "tables": [
      {"id": "tab1", "caption": "Hyperparameters"},
      {"id": "tab2", "caption": "Comparison with baselines on all datasets"}
    ],
    "figures": [
      {"id": "fig1", "caption": "Architecture"},
      {"id": "fig2", "caption": "Ablation results"},
      {"id": "fig3", "caption": "Performance comparison across datasets"}
    ]
  }
}
```

**Output**:
```json
{
  "claim_id": "C12",
  "evidence_found": [
    {
      "type": "figure",
      "ref": "fig3",
      "match_type": "explicit",
      "match_confidence": 1.0,
      "caption": "Performance comparison across datasets",
      "relevance_note": "Explicitly referenced as 'Figure 3'"
    },
    {
      "type": "table",
      "ref": "tab2",
      "match_type": "explicit",
      "match_confidence": 1.0,
      "caption": "Comparison with baselines on all datasets",
      "relevance_note": "Explicitly referenced as 'Table 2'"
    }
  ],
  "search_summary": {
    "explicit_refs_found": 2,
    "implicit_matches": 0,
    "total_evidence": 2
  }
}
```

## Integration Notes

### Called By
- `parallel-audit` orchestrator (before evidence-grader)
- `state-generator` (to populate evidence_map)

### Calls
- None

### State Updates
- Populates `evidence_map` in research-state.json
- Updates `evidence_refs` in claim objects
