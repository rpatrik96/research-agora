---
name: proof-step-verifier
description: |
  Verify a single proof step. Two levels over one shape: **logic** checks that
  the step follows from its stated premises; **computation** checks that the
  algebra, gradient, expectation or limit exchange inside it is correct.
  Detects sign errors, dropped terms, inequality-direction flips and invalid
  exchanges. Atomic, parallelizable operation.
  Trigger: "verify proof step", "check derivation", "verify algebra".
model: opus
color: gray
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: verification
  verification-level: heuristic
  visibility: internal
---

# Micro-Skill: Proof Step Verifier

> **LLM-required**: Deciding whether a step follows requires mathematical
> reasoning. A CAS can settle the computation half where the expression is
> mechanisable; the logic half has no script path.

A step can fail two ways, and they need different questions asked:

| `level` | Asks | Catches |
|---|---|---|
| `logic` | Does the conclusion follow from the stated premises? | Non-sequiturs, unstated assumptions, circular steps, quantifier slips |
| `computation` | Is the manipulation inside the step correct? | Sign errors, dropped terms, inequality direction, invalid limit/integral exchange, gradient mistakes |

Set `level` from what the caller asks. When unset, run both: a step that is
computationally right can still not follow, and a step that follows can still
have the algebra wrong.

**One error vocabulary, shared by both levels.** These were two skills until
RFC-0002 and their enums had already drifted — `invalid_exchange` against
`invalid_limit_exchange`, `algebraic_error` against `algebraic_manipulation`,
for the same defects. One list cannot disagree with itself:

| Code | Meaning |
|---|---|
| `sign_error` | A sign flipped or was lost |
| `dropped_term` | A term vanished between lines |
| `inequality_direction` | An inequality points the wrong way after an operation |
| `invalid_exchange` | Limit, sum, integral or expectation swapped without justification |
| `algebraic_error` | The manipulation is not valid |
| `unjustified_step` | The conclusion does not follow from the premises given |
| `unstated_assumption` | The step needs something not in the premises |

**Rate confidence honestly, and use `low` when unsure.** A confident wrong
verdict on a proof step is worse than an admitted uncertainty, because the
caller stops looking.

---

## Level: logic

> **LLM-required**: Verifying mathematical reasoning in individual proof steps requires deep mathematical understanding. No script alternative.

> **One-line description**: Verify whether a single proof step logically follows from its stated premises and assumptions.

### Purpose

This skill takes a single proof step (from `proof-step-extractor`) along with its premises and verifies whether the step is logically valid. It checks algebraic correctness, inequality direction, assumption applicability, and logical soundness. This is the atomic verification unit for parallel proof auditing.

### Parallelization Properties

| Property | Value |
|----------|-------|
| **Input scope** | Single proof step + its premises |
| **State requirements** | Needs premise content |
| **External calls** | None |
| **Typical runtime** | 10-20s |
| **Can run in parallel** | Yes |

### Input Specification

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

### Output Specification

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

### Algorithm

1. **Parse the step** — extract the mathematical claim being made
2. **Load premises** — gather all prior steps, assumptions, and definitions this step depends on
3. **Check logical validity** — does the conclusion follow from premises?
4. **Check algebraic correctness** — are expansions, signs, and terms correct?
5. **Check inequality direction** — is the inequality applied correctly?
6. **Check assumption applicability** — do conditions of the invoked assumption hold?
7. **Assess confidence** — rate certainty in the verdict (high/medium/low)
8. **Generate explanation** — provide brief reasoning for the verdict
9. **Suggest fix** — if issues found, describe how to correct the step

### Verification Checks

#### Check 1: Does the conclusion follow from premises?
- Can the result be derived from the stated inputs?
- Are all referenced prior steps actually available?

#### Check 2: Algebraic correctness
- Are expansions correct?
- Are signs correct in products and sums?
- Are terms properly tracked (nothing dropped)?

#### Check 3: Inequality direction
- Is the inequality applied in the correct direction?
- Are conditions for the inequality satisfied?

#### Check 4: Assumption applicability
- Does the assumption actually apply in this context?
- Are conditions of the assumption met?
- Is the assumption being used correctly (not misquoted)?

#### Check 5: Logical validity
- No circular reasoning
- Quantifiers in correct order
- Conclusion not stronger than what premises support

### Verdict Definitions

| Verdict | Meaning | Action |
|---------|---------|--------|
| **valid** | Step follows from premises with high confidence | No action needed |
| **suspicious** | Step likely correct but hard to verify fully | Flag for manual review |
| **gap** | Step skips intermediate reasoning | Author should add missing steps |
| **error** | Step contains a detectable mistake | Must fix before submission |

### Constraints

- **DO**: Check every stated justification against the actual mathematical content
- **DO**: Flag steps that skip intermediate reasoning as "gap"
- **DO**: Rate confidence honestly — use "low" when unsure
- **DON'T**: Decompose steps further (that's proof-step-extractor's job)
- **DON'T**: Attempt to fix errors (just report them)
- **DON'T**: Access external resources
- **DON'T**: Spend more than 20s on a single step

### Example

#### Example Input

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

#### Example Output

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

### Integration

#### Called By
- `proof-auditor` agent (parallel mode)
- `parallel-theory-audit` orchestrator

#### Receives From
- `proof-step-extractor` micro-skill (provides steps to verify)

### Worker Preamble Compliance

This micro-skill follows the Worker Preamble Protocol:
- Returns structured JSON output
- Reports errors in `error` field
- Does not make external API calls
- Completes within timeout (20s typical)

---

## Level: computation

> **LLM-required**: Verifying algebraic and calculus derivations requires mathematical understanding beyond pattern matching. No script alternative.

> **One-line description**: Verify a single algebraic or calculus derivation, detecting sign errors, dropped terms, and invalid operations.

### Purpose

This skill verifies a single algebraic or calculus derivation -- applying an inequality, taking a gradient, computing an expectation, or simplifying an expression. It detects common errors: sign errors, dropped terms, invalid exchanges of limits, and incorrect inequality applications. This is the computation-level verification complement to `proof-step-verifier`'s logic-level verification.

### Parallelization Properties

| Property | Value |
|----------|-------|
| **Input scope** | Single derivation (2-5 lines of math) |
| **State requirements** | Needs derivation context |
| **External calls** | None |
| **Typical runtime** | 10-20s |
| **Can run in parallel** | Yes |

### Input Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["derivation_id", "from_expression", "to_expression", "operation"],
  "properties": {
    "derivation_id": {
      "type": "string",
      "description": "Identifier for this derivation"
    },
    "from_expression": {
      "type": "string",
      "description": "Starting expression (LaTeX)"
    },
    "to_expression": {
      "type": "string",
      "description": "Resulting expression (LaTeX)"
    },
    "operation": {
      "type": "string",
      "enum": ["algebraic_manipulation", "inequality_application", "gradient_computation", "expectation", "limit", "integral", "summation", "substitution", "other"],
      "description": "Type of mathematical operation"
    },
    "operation_detail": {
      "type": "string",
      "description": "Specific operation (e.g., 'Apply Cauchy-Schwarz', 'Take gradient w.r.t. theta')"
    },
    "context": {
      "type": "string",
      "description": "Surrounding context for the derivation"
    }
  }
}
```

### Output Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["derivation_id", "verdict", "confidence"],
  "properties": {
    "derivation_id": {"type": "string"},
    "verdict": {
      "type": "string",
      "enum": ["correct", "likely_correct", "suspicious", "error"],
      "description": "Verification verdict"
    },
    "confidence": {
      "type": "string",
      "enum": ["high", "medium", "low"]
    },
    "errors_found": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": {
            "type": "string",
            "enum": ["sign_error", "dropped_term", "wrong_inequality_direction", "invalid_limit_exchange", "dimension_mismatch", "incorrect_gradient", "missing_absolute_value", "wrong_exponent", "incorrect_expectation", "other"]
          },
          "description": {"type": "string"},
          "expected": {"type": "string", "description": "What the result should be"},
          "got": {"type": "string", "description": "What was written"}
        }
      }
    },
    "explanation": {"type": "string"},
    "corrected_expression": {
      "type": "string",
      "description": "If errors found, the corrected LaTeX expression"
    }
  }
}
```

### Algorithm

1. **Parse expressions** — extract the `from_expression` and `to_expression` as mathematical objects
2. **Identify the operation** — classify the transformation type (algebraic, inequality, gradient, etc.)
3. **Reproduce the derivation** — attempt to derive `to_expression` from `from_expression` using the stated operation
4. **Check for common errors** — scan for sign errors, dropped terms, wrong inequality direction
5. **Verify conditions** — ensure prerequisites of the operation are met (e.g., non-negativity for AM-GM)
6. **Assign verdict** — correct, likely_correct, suspicious, or error
7. **Provide correction** — if errors found, give the corrected expression

### Constraints

- **DO**: Track every term through the transformation
- **DO**: Check that inequality conditions are satisfied
- **DO**: Provide the corrected expression when errors are found
- **DON'T**: Verify the overall proof structure (that's proof-step-verifier's job)
- **DON'T**: Access external resources
- **DON'T**: Spend more than 20s on a single derivation
- **DON'T**: Verify more than one derivation per invocation

### Example

#### Example Input

```json
{
  "derivation_id": "thm1_S2",
  "from_expression": "f(x_t) + \\langle \\nabla f(x_t), -\\frac{1}{L} \\nabla f(x_t) \\rangle + \\frac{L}{2} \\|\\frac{1}{L} \\nabla f(x_t)\\|^2",
  "to_expression": "f(x_t) - \\frac{1}{2L} \\|\\nabla f(x_t)\\|^2",
  "operation": "algebraic_manipulation",
  "operation_detail": "Simplify inner product and quadratic terms",
  "context": "Substituting GD update into descent lemma"
}
```

#### Example Output

```json
{
  "derivation_id": "thm1_S2",
  "verdict": "correct",
  "confidence": "high",
  "errors_found": [],
  "explanation": "Inner product term: <grad f, -(1/L) grad f> = -1/L ||grad f||^2. Quadratic term: L/2 * 1/L^2 ||grad f||^2 = 1/(2L) ||grad f||^2. Sum: -1/L + 1/(2L) = -1/(2L). Result matches.",
  "corrected_expression": null
}
```

### Verification by Operation Type

#### Algebraic Manipulation
- Track every term through the transformation
- Verify signs in products and sums
- Check that no terms are dropped or created
- Verify factoring and expansion

#### Inequality Application
- Verify the inequality is stated correctly
- Check it is applied in the correct direction
- Verify conditions are satisfied (e.g., non-negative quantities for AM-GM)
- Check that the bound is tight enough (not too loose)

#### Gradient Computation
- Verify chain rule application
- Check dimensions of gradient vector
- Verify partial derivatives
- Check for missing transpose operations

#### Expectation Computation
- Verify linearity of expectation is applicable
- Check independence assumptions for E[XY] = E[X]E[Y]
- Verify Jensen's inequality direction (convex vs concave)
- Check for invalid exchange of E and nonlinear operations

#### Limit/Integral Operations
- Verify conditions for exchanging limit and integral (dominated convergence)
- Check conditions for exchanging limit and sum (uniform convergence)
- Verify Fubini's theorem conditions for integral exchange
- Check convergence of series

### Common Error Patterns

| Error | Frequency | Detection Method |
|-------|-----------|------------------|
| Sign error in expansion | Very common | Track signs term by term |
| Dropped constant factor | Common | Compare coefficient counts |
| Wrong Cauchy-Schwarz direction | Common | Verify inner product inequality direction |
| Missing squared in norm bound | Common | Check exponents |
| E[f(X)] != f(E[X]) confusion | Common | Check linearity |
| Sum and lim exchange without justification | Occasional | Check uniform convergence |
| Gradient of trace vs element | Occasional | Verify matrix calculus |

### Integration

#### Called By
- `proof-auditor` agent
- `parallel-theory-audit` orchestrator

#### Receives From
- `proof-step-extractor` (derivation steps to check)

### Worker Preamble Compliance

This micro-skill follows the Worker Preamble Protocol:
- Returns structured JSON output
- Reports errors in `error` field
- Does not make external API calls
- Completes within timeout (20s typical)
