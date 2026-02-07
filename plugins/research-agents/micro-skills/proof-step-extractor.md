---
name: proof-step-extractor
description: |
  Decompose a single proof into atomic logical steps with dependency arrows.
  Atomic, parallelizable operation for proof auditing pipelines.
  Trigger: "extract proof steps", "decompose proof".
model: sonnet
color: gray
---

# Micro-Skill: Proof Step Extractor

> **LLM-required**: Decomposing proofs into atomic logical steps requires understanding mathematical reasoning. No script alternative.

> **One-line description**: Decompose a single proof into atomic logical steps with dependency arrows and assumption tracking.

## Purpose

This skill takes a single proof and decomposes it into atomic logical steps. Each step records what it does, what it depends on, and which assumptions it consumes. This enables parallel verification by `proof-step-verifier`.

## Parallelization Properties

| Property | Value |
|----------|-------|
| **Input scope** | Single proof |
| **State requirements** | Stateless |
| **External calls** | None |
| **Typical runtime** | 15-30s |
| **Can run in parallel** | Yes |

## Input Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["proof_id", "theorem_statement", "proof_text"],
  "properties": {
    "proof_id": {
      "type": "string",
      "description": "Identifier for the proof (e.g., 'thm1_proof')"
    },
    "theorem_statement": {
      "type": "string",
      "description": "The statement being proved"
    },
    "proof_text": {
      "type": "string",
      "description": "Full LaTeX text of the proof"
    },
    "assumptions": {
      "type": "array",
      "items": {"type": "object"},
      "description": "Available assumptions the proof may reference"
    }
  }
}
```

## Output Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["proof_id", "steps"],
  "properties": {
    "proof_id": {"type": "string"},
    "steps": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["step_id", "action", "justification", "depends_on"],
        "properties": {
          "step_id": {
            "type": "string",
            "description": "Step identifier (e.g., 'S1', 'S2')"
          },
          "action": {
            "type": "string",
            "description": "What this step does (e.g., 'Apply Cauchy-Schwarz inequality')"
          },
          "justification": {
            "type": "string",
            "enum": ["definition", "assumption", "prior_step", "algebraic", "inequality", "limit", "substitution", "cited_result", "unjustified"],
            "description": "Type of justification for this step"
          },
          "justification_detail": {
            "type": "string",
            "description": "Specific justification (e.g., 'Assumption A1: L-smoothness')"
          },
          "depends_on": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Step IDs this step depends on"
          },
          "assumptions_consumed": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Assumption IDs used in this step"
          },
          "latex": {
            "type": "string",
            "description": "The LaTeX expression for this step"
          },
          "complexity": {
            "type": "string",
            "enum": ["trivial", "routine", "nontrivial", "complex"],
            "description": "Difficulty of verifying this step"
          }
        }
      }
    },
    "total_steps": {"type": "integer"},
    "assumptions_used": {
      "type": "array",
      "items": {"type": "string"}
    },
    "gap_count": {
      "type": "integer",
      "description": "Number of steps with 'unjustified' justification"
    }
  }
}
```

## Algorithm

1. **Read the full proof text** and identify the starting point and conclusion
2. **Identify major transitions** — each application of a definition, assumption, inequality, or algebraic manipulation is a boundary
3. **Create atomic steps** — one mathematical operation per step following granularity rules below
4. **Assign justifications** — categorize each step's justification type from the taxonomy
5. **Build dependency graph** — record which prior steps and assumptions each step depends on
6. **Track assumptions consumed** — note which formal assumptions are invoked at each step
7. **Assess complexity** — rate each step's verification difficulty (trivial/routine/nontrivial/complex)
8. **Count gaps** — tally steps with `unjustified` justification

## Step Decomposition Guidelines

### Granularity Rules

1. **One mathematical operation per step**: Each step should do exactly one thing
2. **Separate setup from application**: Defining a quantity is one step; using it is another
3. **Explicit inequality applications**: Each inequality (Cauchy-Schwarz, Jensen, etc.) is its own step
4. **Algebraic simplifications**: Group routine algebra into one step, but separate non-obvious manipulations
5. **Limit operations**: Each limit exchange (lim/integral, lim/sum) is its own step

### Justification Categories

| Category | When to Use | Example |
|----------|------------|---------|
| `definition` | Introducing a new quantity | "Define V(t) = f(x_t) - f*" |
| `assumption` | Invoking a stated assumption | "By A1 (L-smoothness)..." |
| `prior_step` | Building on an earlier step | "Substituting S3 into S4..." |
| `algebraic` | Routine algebraic manipulation | "Expanding the square..." |
| `inequality` | Applying a named inequality | "By Cauchy-Schwarz..." |
| `limit` | Limit operation or exchange | "Taking expectation..." |
| `substitution` | Substituting a specific value | "Setting eta = 1/L..." |
| `cited_result` | Using a result from another paper | "By Theorem 3 of [Smith 2023]..." |
| `unjustified` | No justification provided | "It follows that..." |

## Constraints

- **DO**: Produce one step per mathematical operation
- **DO**: Track all assumption usage explicitly
- **DO**: Mark unjustified leaps honestly (don't invent justifications)
- **DON'T**: Verify steps (that's proof-step-verifier's job)
- **DON'T**: Skip "trivial" steps — decompose everything
- **DON'T**: Access external resources
- **DON'T**: Generate more than 50 steps per proof (flag overflow)

## Example

### Example Input

```json
{
  "proof_id": "thm1_proof",
  "theorem_statement": "Under L-smoothness (A1), GD with step size 1/L satisfies f(x_T) - f* <= L||x_0 - x*||^2 / (2T)",
  "proof_text": "By L-smoothness, f(x_{t+1}) <= f(x_t) + <grad f(x_t), x_{t+1} - x_t> + L/2 ||x_{t+1} - x_t||^2. Substituting x_{t+1} = x_t - (1/L) grad f(x_t), we get f(x_{t+1}) <= f(x_t) - 1/(2L) ||grad f(x_t)||^2. Summing from t=0 to T-1 and rearranging gives the result.",
  "assumptions": [{"id": "A1", "text": "f is L-smooth"}]
}
```

### Example Output

```json
{
  "proof_id": "thm1_proof",
  "steps": [
    {
      "step_id": "S1",
      "action": "Apply L-smoothness descent lemma",
      "justification": "assumption",
      "justification_detail": "Assumption A1: L-smoothness",
      "depends_on": [],
      "assumptions_consumed": ["A1"],
      "latex": "f(x_{t+1}) \\leq f(x_t) + \\langle \\nabla f(x_t), x_{t+1} - x_t \\rangle + \\frac{L}{2} \\|x_{t+1} - x_t\\|^2",
      "complexity": "routine"
    },
    {
      "step_id": "S2",
      "action": "Substitute GD update rule x_{t+1} = x_t - (1/L) grad f(x_t)",
      "justification": "substitution",
      "justification_detail": "GD update with step size eta = 1/L",
      "depends_on": ["S1"],
      "assumptions_consumed": [],
      "latex": "f(x_{t+1}) \\leq f(x_t) - \\frac{1}{2L} \\|\\nabla f(x_t)\\|^2",
      "complexity": "routine"
    },
    {
      "step_id": "S3",
      "action": "Telescope sum from t=0 to T-1 and rearrange",
      "justification": "algebraic",
      "justification_detail": "Summing S2 over t=0..T-1, telescoping f terms",
      "depends_on": ["S2"],
      "assumptions_consumed": [],
      "latex": "\\sum_{t=0}^{T-1} \\frac{1}{2L} \\|\\nabla f(x_t)\\|^2 \\leq f(x_0) - f^*",
      "complexity": "routine"
    }
  ],
  "total_steps": 3,
  "assumptions_used": ["A1"],
  "gap_count": 0
}
```

## Integration

### Called By
- `proof-auditor` agent (parallel mode)
- `parallel-theory-audit` orchestrator

### Feeds Into
- `proof-step-verifier` micro-skill (verifies each extracted step)

## Worker Preamble Compliance

This micro-skill follows the Worker Preamble Protocol:
- Returns structured JSON output
- Reports errors in `error` field
- Does not make external API calls
- Completes within timeout (30s typical)
