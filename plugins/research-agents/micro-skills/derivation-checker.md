---
name: derivation-checker
description: |
  Verify a single algebraic or calculus derivation. Checks inequality applications,
  gradient computations, expectation calculations. Detects sign errors, dropped terms,
  and invalid limit exchanges. Trigger: "check derivation", "verify algebra".
model: opus
color: gray
---

# Micro-Skill: Derivation Checker

> **LLM-required**: Verifying algebraic and calculus derivations requires mathematical understanding beyond pattern matching. No script alternative.

> **One-line description**: Verify a single algebraic or calculus derivation, detecting sign errors, dropped terms, and invalid operations.

## Purpose

This skill verifies a single algebraic or calculus derivation -- applying an inequality, taking a gradient, computing an expectation, or simplifying an expression. It detects common errors: sign errors, dropped terms, invalid exchanges of limits, and incorrect inequality applications. This is the computation-level verification complement to `proof-step-verifier`'s logic-level verification.

## Parallelization Properties

| Property | Value |
|----------|-------|
| **Input scope** | Single derivation (2-5 lines of math) |
| **State requirements** | Needs derivation context |
| **External calls** | None |
| **Typical runtime** | 10-20s |
| **Can run in parallel** | Yes |

## Input Specification

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

## Output Specification

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

## Verification by Operation Type

### Algebraic Manipulation
- Track every term through the transformation
- Verify signs in products and sums
- Check that no terms are dropped or created
- Verify factoring and expansion

### Inequality Application
- Verify the inequality is stated correctly
- Check it is applied in the correct direction
- Verify conditions are satisfied (e.g., non-negative quantities for AM-GM)
- Check that the bound is tight enough (not too loose)

### Gradient Computation
- Verify chain rule application
- Check dimensions of gradient vector
- Verify partial derivatives
- Check for missing transpose operations

### Expectation Computation
- Verify linearity of expectation is applicable
- Check independence assumptions for E[XY] = E[X]E[Y]
- Verify Jensen's inequality direction (convex vs concave)
- Check for invalid exchange of E and nonlinear operations

### Limit/Integral Operations
- Verify conditions for exchanging limit and integral (dominated convergence)
- Check conditions for exchanging limit and sum (uniform convergence)
- Verify Fubini's theorem conditions for integral exchange
- Check convergence of series

## Common Error Patterns

| Error | Frequency | Detection Method |
|-------|-----------|------------------|
| Sign error in expansion | Very common | Track signs term by term |
| Dropped constant factor | Common | Compare coefficient counts |
| Wrong Cauchy-Schwarz direction | Common | Verify inner product inequality direction |
| Missing squared in norm bound | Common | Check exponents |
| E[f(X)] != f(E[X]) confusion | Common | Check linearity |
| Sum and lim exchange without justification | Occasional | Check uniform convergence |
| Gradient of trace vs element | Occasional | Verify matrix calculus |

## Integration

### Called By
- `proof-auditor` agent
- `parallel-theory-audit` orchestrator

### Receives From
- `proof-step-extractor` (derivation steps to check)

## Worker Preamble Compliance

This micro-skill follows the Worker Preamble Protocol:
- Returns structured JSON output
- Reports errors in `error` field
- Does not make external API calls
- Completes within timeout (20s typical)
