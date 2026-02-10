---
name: assumption-analyzer
description: |
  Deep analysis of a single mathematical assumption: is it standard, what does
  it rule out, what are weaker alternatives, and is it testable in practice.
  Atomic, parallelizable operation. Trigger: "analyze assumption".
model: sonnet
color: gray
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: analysis
  verification-level: layered
  visibility: internal
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

## Algorithm

1. **Identify the assumption** — parse the mathematical statement and any conditions
2. **Match to known assumptions** — check against standard assumption hierarchies (convexity, smoothness, noise)
3. **Assess standardness** — determine frequency in the literature (ubiquitous/common/occasional/rare/novel)
4. **Analyze implications** — what does this assumption rule out? What scenarios are excluded?
5. **Find weaker alternatives** — identify less restrictive assumptions that might still suffice
6. **Find stronger alternatives** — identify more restrictive assumptions that would simplify proofs
7. **Assess testability** — can the assumption be verified on real data/models?
8. **Predict reviewer concern** — estimate likelihood a reviewer will challenge this assumption

## Constraints

- **DO**: Map assumptions to their standard names when they exist
- **DO**: Provide concrete examples of what is ruled out
- **DO**: Suggest actionable weaker alternatives
- **DON'T**: Verify whether the assumption holds for the paper's specific setup
- **DON'T**: Challenge the paper's experimental design
- **DON'T**: Access external resources
- **DON'T**: Analyze more than one assumption per invocation

## Example

### Example Input

```json
{
  "assumption_id": "A1",
  "assumption_text": "The objective function f is L-smooth, i.e., ||grad f(x) - grad f(y)|| <= L ||x - y|| for all x, y.",
  "context": "convergence proof of SGD",
  "domain": "convex optimization"
}
```

### Example Output

```json
{
  "assumption_id": "A1",
  "analysis": {
    "standard_name": "L-smoothness (Lipschitz gradient)",
    "is_standard": true,
    "frequency": "common",
    "what_it_rules_out": [
      "Non-differentiable functions (e.g., |x|)",
      "Functions with rapidly changing gradients",
      "ReLU networks (non-smooth at origin)"
    ],
    "weaker_alternatives": [
      {
        "name": "Local smoothness",
        "statement": "L-smoothness holds in a neighborhood of the optimum",
        "tradeoff": "Weaker but only gives local convergence guarantees"
      }
    ],
    "stronger_alternatives": [
      {
        "name": "Strong smoothness",
        "statement": "f is L-smooth and mu-strongly convex",
        "benefit": "Enables linear convergence rate"
      }
    ],
    "testable_in_practice": true,
    "how_to_test": "Estimate L by computing max ||grad f(x_i) - grad f(x_j)|| / ||x_i - x_j|| over sample pairs",
    "common_violations": [
      "Deep neural networks with ReLU activations",
      "L1-regularized objectives"
    ],
    "reviewer_concern_level": "low"
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
