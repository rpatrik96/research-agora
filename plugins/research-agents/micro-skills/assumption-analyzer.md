---
name: assumption-analyzer
description: |
  Deep analysis of a single mathematical assumption: is it standard, what does
  it rule out, what are weaker alternatives, and is it testable in practice.
  Atomic, parallelizable operation. Trigger: "analyze assumption".
model: sonnet
color: gray
---

# Micro-Skill: Assumption Analyzer

> **LLM-required**: Assessing whether an assumption is standard and exploring alternatives requires broad mathematical knowledge. No script alternative.

> **One-line description**: Deep analysis of a single mathematical assumption — standardness, implications, weaker alternatives, and practical testability.

## Purpose

This skill performs deep analysis of a single mathematical assumption. It determines whether the assumption is standard in the field, what it rules out, what weaker alternatives exist, and whether it can be verified in practice. This supports both proof verification (are assumptions reasonable?) and paper strengthening (can we weaken assumptions?).

## Parallelization Properties

| Property | Value |
|----------|-------|
| **Input scope** | Single assumption |
| **State requirements** | Stateless |
| **External calls** | None |
| **Typical runtime** | 10-20s |
| **Can run in parallel** | Yes |

## Input Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["assumption_id", "assumption_text"],
  "properties": {
    "assumption_id": {
      "type": "string",
      "description": "Assumption identifier (e.g., 'A1')"
    },
    "assumption_text": {
      "type": "string",
      "description": "Full text of the assumption including mathematical statement"
    },
    "context": {
      "type": "string",
      "description": "What the assumption is used for (e.g., 'convergence proof of SGD')"
    },
    "domain": {
      "type": "string",
      "description": "Mathematical domain (e.g., 'convex optimization', 'learning theory')"
    }
  }
}
```

## Output Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["assumption_id", "analysis"],
  "properties": {
    "assumption_id": {"type": "string"},
    "analysis": {
      "type": "object",
      "properties": {
        "standard_name": {
          "type": "string",
          "description": "Standard name if known (e.g., 'L-smoothness', 'restricted isometry property')"
        },
        "is_standard": {
          "type": "boolean",
          "description": "Whether this is a well-known standard assumption"
        },
        "frequency": {
          "type": "string",
          "enum": ["ubiquitous", "common", "occasional", "rare", "novel"],
          "description": "How commonly this assumption appears in the literature"
        },
        "what_it_rules_out": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Examples of objects/scenarios excluded by this assumption"
        },
        "weaker_alternatives": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": {"type": "string"},
              "statement": {"type": "string"},
              "tradeoff": {"type": "string"}
            }
          }
        },
        "stronger_alternatives": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": {"type": "string"},
              "statement": {"type": "string"},
              "benefit": {"type": "string"}
            }
          }
        },
        "testable_in_practice": {
          "type": "boolean",
          "description": "Whether the assumption can be verified on real data/models"
        },
        "how_to_test": {
          "type": "string",
          "description": "If testable, how to verify it"
        },
        "common_violations": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Known cases where this assumption is violated"
        },
        "reviewer_concern_level": {
          "type": "string",
          "enum": ["none", "low", "medium", "high"],
          "description": "Likelihood that a reviewer will question this assumption"
        }
      }
    }
  }
}
```

## Analysis Framework

### Standardness Assessment

| Frequency | Definition | Examples |
|-----------|-----------|---------|
| **Ubiquitous** | Used in >80% of papers in subfield | i.i.d. data, bounded loss |
| **Common** | Used in 30-80% of papers | L-smoothness, strong convexity |
| **Occasional** | Used in 10-30% of papers | Polyak-Lojasiewicz, restricted strong convexity |
| **Rare** | Used in <10% of papers | Specific structural assumptions |
| **Novel** | Not seen before | Paper-specific conditions |

### Known Assumption Hierarchies

#### Convexity Hierarchy (weakest to strongest)
1. Non-convex (no assumption)
2. Polyak-Lojasiewicz (PL) condition
3. Weak convexity / approximate convexity
4. Convexity
5. Strong convexity (mu-strongly convex)

#### Smoothness Hierarchy
1. Continuous
2. Lipschitz continuous
3. Differentiable
4. L-smooth (Lipschitz gradient)
5. Twice differentiable with bounded Hessian
6. Strongly smooth

#### Noise Hierarchy
1. Adversarial noise
2. Sub-exponential
3. Sub-Gaussian
4. Bounded variance
5. Bounded noise
6. No noise (deterministic)

## Integration

### Called By
- `proof-auditor` agent
- `parallel-theory-audit` orchestrator
- `counterexample-searcher` (for understanding what assumptions rule out)

## Worker Preamble Compliance

This micro-skill follows the Worker Preamble Protocol:
- Returns structured JSON output
- Reports errors in `error` field
- Does not make external API calls
- Completes within timeout (20s typical)
