---
name: proof-step-verifier
description: |
  Verify whether a single proof step follows from its premises. Checks
  algebraic correctness, inequality direction, and logical validity.
  Atomic, parallelizable operation. Trigger: "verify proof step".
model: opus
color: gray
---

# Micro-Skill: Proof Step Verifier

> **LLM-required**: Verifying mathematical reasoning in individual proof steps requires deep mathematical understanding. No script alternative.

> **One-line description**: Verify whether a single proof step logically follows from its stated premises and assumptions.

## Purpose

This skill takes a single proof step (from `proof-step-extractor`) along with its premises and verifies whether the step is logically valid. It checks algebraic correctness, inequality direction, assumption applicability, and logical soundness. This is the atomic verification unit for parallel proof auditing.

## Parallelization Properties

| Property | Value |
|----------|-------|
| **Input scope** | Single proof step + its premises |
| **State requirements** | Needs premise content |
| **External calls** | None |
| **Typical runtime** | 10-20s |
| **Can run in parallel** | Yes |

## Input Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["step", "premises"],
  "properties": {
    "step": {
      "type": "object",
      "required": ["step_id", "action", "justification", "latex"],
      "properties": {
        "step_id": {"type": "string"},
        "action": {"type": "string"},
        "justification": {"type": "string"},
        "justification_detail": {"type": "string"},
        "latex": {"type": "string"},
        "depends_on": {"type": "array", "items": {"type": "string"}}
      }
    },
    "premises": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"type": "string"},
          "content": {"type": "string"},
          "type": {"type": "string", "enum": ["step", "assumption", "definition", "cited_result"]}
        }
      },
      "description": "All premises this step depends on (prior steps, assumptions, definitions)"
    },
    "theorem_context": {
      "type": "string",
      "description": "Brief description of what the overall proof is establishing"
    }
  }
}
```

## Output Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["step_id", "verdict", "confidence"],
  "properties": {
    "step_id": {"type": "string"},
    "verdict": {
      "type": "string",
      "enum": ["valid", "suspicious", "gap", "error"],
      "description": "Verification verdict"
    },
    "confidence": {
      "type": "string",
      "enum": ["high", "medium", "low"],
      "description": "Confidence in the verdict"
    },
    "issues": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": {"type": "string", "enum": ["algebraic_error", "wrong_direction", "missing_condition", "unjustified_step", "sign_error", "dropped_term", "invalid_exchange", "circular_reasoning", "vacuous", "other"]},
          "description": {"type": "string"},
          "severity": {"type": "string", "enum": ["critical", "major", "minor"]}
        }
      }
    },
    "explanation": {
      "type": "string",
      "description": "Brief explanation of the verification reasoning"
    },
    "suggested_fix": {
      "type": "string",
      "description": "If issues found, how to fix the step"
    }
  }
}
```

## Algorithm

1. **Parse the step** — extract the mathematical claim being made
2. **Load premises** — gather all prior steps, assumptions, and definitions this step depends on
3. **Check logical validity** — does the conclusion follow from premises?
4. **Check algebraic correctness** — are expansions, signs, and terms correct?
5. **Check inequality direction** — is the inequality applied correctly?
6. **Check assumption applicability** — do conditions of the invoked assumption hold?
7. **Assess confidence** — rate certainty in the verdict (high/medium/low)
8. **Generate explanation** — provide brief reasoning for the verdict
9. **Suggest fix** — if issues found, describe how to correct the step

## Verification Checks

### Check 1: Does the conclusion follow from premises?
- Can the result be derived from the stated inputs?
- Are all referenced prior steps actually available?

### Check 2: Algebraic correctness
- Are expansions correct?
- Are signs correct in products and sums?
- Are terms properly tracked (nothing dropped)?

### Check 3: Inequality direction
- Is the inequality applied in the correct direction?
- Are conditions for the inequality satisfied?

### Check 4: Assumption applicability
- Does the assumption actually apply in this context?
- Are conditions of the assumption met?
- Is the assumption being used correctly (not misquoted)?

### Check 5: Logical validity
- No circular reasoning
- Quantifiers in correct order
- Conclusion not stronger than what premises support

## Verdict Definitions

| Verdict | Meaning | Action |
|---------|---------|--------|
| **valid** | Step follows from premises with high confidence | No action needed |
| **suspicious** | Step likely correct but hard to verify fully | Flag for manual review |
| **gap** | Step skips intermediate reasoning | Author should add missing steps |
| **error** | Step contains a detectable mistake | Must fix before submission |

## Constraints

- **DO**: Check every stated justification against the actual mathematical content
- **DO**: Flag steps that skip intermediate reasoning as "gap"
- **DO**: Rate confidence honestly — use "low" when unsure
- **DON'T**: Decompose steps further (that's proof-step-extractor's job)
- **DON'T**: Attempt to fix errors (just report them)
- **DON'T**: Access external resources
- **DON'T**: Spend more than 20s on a single step

## Example

### Example Input

```json
{
  "step": {
    "step_id": "S2",
    "action": "Substitute GD update rule",
    "justification": "substitution",
    "justification_detail": "GD update with step size eta = 1/L",
    "latex": "f(x_{t+1}) \\leq f(x_t) - \\frac{1}{2L} \\|\\nabla f(x_t)\\|^2",
    "depends_on": ["S1"]
  },
  "premises": [
    {
      "id": "S1",
      "content": "f(x_{t+1}) \\leq f(x_t) + \\langle \\nabla f(x_t), x_{t+1} - x_t \\rangle + \\frac{L}{2} \\|x_{t+1} - x_t\\|^2",
      "type": "step"
    }
  ],
  "theorem_context": "Convergence rate of gradient descent under L-smoothness"
}
```

### Example Output

```json
{
  "step_id": "S2",
  "verdict": "valid",
  "confidence": "high",
  "issues": [],
  "explanation": "Substituting x_{t+1} = x_t - (1/L) grad f(x_t) into S1 and simplifying yields the stated bound. The algebra checks out: inner product term gives -1/L ||grad f||^2, quadratic term gives +1/(2L) ||grad f||^2, net result is -1/(2L) ||grad f||^2.",
  "suggested_fix": null
}
```

## Integration

### Called By
- `proof-auditor` agent (parallel mode)
- `parallel-theory-audit` orchestrator

### Receives From
- `proof-step-extractor` micro-skill (provides steps to verify)

## Worker Preamble Compliance

This micro-skill follows the Worker Preamble Protocol:
- Returns structured JSON output
- Reports errors in `error` field
- Does not make external API calls
- Completes within timeout (20s typical)
