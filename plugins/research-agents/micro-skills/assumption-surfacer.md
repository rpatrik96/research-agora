---
name: assumption-surfacer
description: |
  Surface implicit and explicit assumptions from a paper section. Identifies
  unstated assumptions that affect claim validity. Trigger: "find assumptions",
  "surface implicit assumptions", "check assumptions".
model: haiku
color: gray
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: verification
  verification-level: heuristic
---

# Micro-Skill: Assumption Surfacer

> **LLM-required**: Identifying hidden assumptions requires understanding implicit reasoning. No script alternative.

> **One-line description**: Identify explicit and implicit assumptions in a paper section that affect claim validity.

## Purpose

This skill surfaces assumptions that authors make but may not explicitly state. Implicit assumptions can be crucial for understanding a paper's scope and limitations. Reviewers often challenge unstated assumptions, so identifying them proactively strengthens the paper.

## Parallelization Properties

| Property | Value |
|----------|-------|
| **Input scope** | Single section |
| **State requirements** | Stateless |
| **External calls** | None |
| **Typical runtime** | <10s |
| **Can run in parallel** | Yes |

## Input Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["section_id", "section_text"],
  "properties": {
    "section_id": {
      "type": "string",
      "description": "Section identifier"
    },
    "section_title": {
      "type": "string",
      "description": "Section title"
    },
    "section_text": {
      "type": "string",
      "description": "Full section text"
    },
    "domain": {
      "type": "string",
      "description": "Research domain (e.g., 'machine learning', 'NLP')",
      "default": "machine learning"
    },
    "claims_in_section": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Claim IDs in this section (for linking)"
    }
  }
}
```

### Example Input

```json
{
  "section_id": "sec3",
  "section_title": "Methodology",
  "section_text": "We train our model on the standard ImageNet dataset. The model is optimized using Adam with learning rate 1e-4. Following standard practice, we use data augmentation including random crops and horizontal flips. Our method achieves 95% accuracy.",
  "domain": "computer vision",
  "claims_in_section": ["C5", "C6"]
}
```

## Output Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["section_id", "assumptions"],
  "properties": {
    "section_id": {"type": "string"},
    "assumptions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "text", "explicit", "category"],
        "properties": {
          "id": {"type": "string", "pattern": "^A[0-9]+$"},
          "text": {"type": "string"},
          "explicit": {"type": "boolean"},
          "category": {
            "type": "string",
            "enum": ["data", "model", "optimization", "evaluation", "theoretical", "domain", "resource"]
          },
          "severity": {
            "type": "string",
            "enum": ["critical", "moderate", "minor"]
          },
          "standard_in_field": {"type": "boolean"},
          "affects_claims": {
            "type": "array",
            "items": {"type": "string"}
          },
          "potential_issues": {
            "type": "array",
            "items": {"type": "string"}
          },
          "recommendations": {
            "type": "array",
            "items": {"type": "string"}
          }
        }
      }
    },
    "summary": {
      "type": "object",
      "properties": {
        "explicit_count": {"type": "integer"},
        "implicit_count": {"type": "integer"},
        "critical_count": {"type": "integer"}
      }
    }
  }
}
```

### Example Output

```json
{
  "section_id": "sec3",
  "assumptions": [
    {
      "id": "A1",
      "text": "ImageNet is representative of the target deployment distribution",
      "explicit": false,
      "category": "data",
      "severity": "moderate",
      "standard_in_field": true,
      "affects_claims": ["C5"],
      "potential_issues": [
        "Performance may degrade on out-of-distribution data",
        "ImageNet biases may affect model behavior"
      ],
      "recommendations": [
        "Acknowledge ImageNet limitations in discussion",
        "Consider additional evaluation on OOD datasets"
      ]
    },
    {
      "id": "A2",
      "text": "Adam optimizer with default hyperparameters is suitable",
      "explicit": false,
      "category": "optimization",
      "severity": "minor",
      "standard_in_field": true,
      "affects_claims": ["C5"],
      "potential_issues": [],
      "recommendations": []
    },
    {
      "id": "A3",
      "text": "Data augmentation (crops, flips) is appropriate and sufficient",
      "explicit": true,
      "category": "data",
      "severity": "minor",
      "standard_in_field": true,
      "affects_claims": ["C5"],
      "potential_issues": [],
      "recommendations": []
    }
  ],
  "summary": {
    "explicit_count": 1,
    "implicit_count": 2,
    "critical_count": 0
  }
}
```

## Algorithm

1. **Scan for explicit assumptions**
   - Look for: "We assume...", "Assuming that...", "Under the assumption..."
   - Look for: "standard", "common practice", "following prior work"
   - Extract stated assumptions with context

2. **Identify implicit assumptions by category**
   - **Data**: Distribution, size, quality, labeling
   - **Model**: Architecture choices, capacity, inductive biases
   - **Optimization**: Convergence, hyperparameters, compute
   - **Evaluation**: Metrics, baselines, statistical validity
   - **Theoretical**: Mathematical conditions, bounds
   - **Domain**: Problem formulation, scope
   - **Resource**: Compute, memory, time requirements

3. **Assess each assumption**
   - Is it standard in the field?
   - What severity if violated?
   - Which claims does it affect?

4. **Generate recommendations**
   - For critical implicit assumptions: Suggest making explicit
   - For non-standard assumptions: Suggest justification
   - For all: Consider limitations section mention

## Assumption Categories

### Data Assumptions

| Pattern | Assumption | Severity |
|---------|------------|----------|
| "trained on [dataset]" | Dataset is representative | moderate |
| "test set" | Test/train split is valid | moderate |
| "labeled data" | Labels are correct | critical |
| No mention of distribution shift | IID assumption | moderate |

### Model Assumptions

| Pattern | Assumption | Severity |
|---------|------------|----------|
| "neural network" | NN is appropriate for task | minor |
| Specific architecture | Architecture is suitable | minor |
| "pretrained model" | Pretraining is relevant | moderate |
| No uncertainty quantification | Point estimates sufficient | moderate |

### Optimization Assumptions

| Pattern | Assumption | Severity |
|---------|------------|----------|
| "converged" | Training reached optimum | moderate |
| "learning rate X" | LR is appropriate | minor |
| Single run reported | Result is reproducible | critical |

### Evaluation Assumptions

| Pattern | Assumption | Severity |
|---------|------------|----------|
| "accuracy" | Accuracy is right metric | moderate |
| "compared to [baseline]" | Baseline is appropriate | moderate |
| No confidence intervals | Single point is sufficient | moderate |

### Theoretical Assumptions

| Pattern | Assumption | Severity |
|---------|------------|----------|
| "smooth", "convex", "Lipschitz" | Property holds | critical |
| "bounded" | Bounds are reasonable | critical |
| "i.i.d." | Independence holds | critical |

## Severity Classification

| Severity | Criteria | Action Needed |
|----------|----------|---------------|
| **critical** | If violated, main claims invalid | Must address |
| **moderate** | If violated, scope/applicability limited | Should acknowledge |
| **minor** | Standard practice, unlikely to matter | Optional mention |

## Constraints

- **DO**: Identify both explicit and implicit assumptions
- **DO**: Link assumptions to affected claims
- **DO**: Distinguish standard vs non-standard assumptions
- **DO**: Provide actionable recommendations
- **DON'T**: Verify assumption validity (out of scope)
- **DON'T**: Challenge experimental design (that's reviewer's job)
- **DON'T**: Generate more than 10 assumptions per section

## Error Handling

| Error Condition | Response |
|-----------------|----------|
| Empty section text | Return empty assumptions list |
| No assumptions found | Return empty list with note "No assumptions identified" |
| Too many assumptions | Return top 10 by severity |

## Context Requirements

| Context Item | Required | Source |
|--------------|----------|--------|
| Section text | Yes | Direct input |
| Domain | No | Default: machine learning |
| Claims in section | No | Helps link assumptions |

## Examples

### Example 1: Theoretical Section

**Input**:
```json
{
  "section_id": "sec4",
  "section_title": "Theoretical Analysis",
  "section_text": "Theorem 1: Under Assumptions 1-3, our algorithm converges at rate O(1/t). Assumption 1: The loss function is L-smooth. Assumption 2: The gradients are bounded by G. We do not require convexity.",
  "domain": "optimization"
}
```

**Output**:
```json
{
  "section_id": "sec4",
  "assumptions": [
    {
      "id": "A1",
      "text": "The loss function is L-smooth",
      "explicit": true,
      "category": "theoretical",
      "severity": "critical",
      "standard_in_field": true,
      "affects_claims": [],
      "potential_issues": [
        "Deep neural network losses are not globally smooth",
        "L constant may be unknown in practice"
      ],
      "recommendations": [
        "Discuss when smoothness holds in practice",
        "Provide guidance on estimating L"
      ]
    },
    {
      "id": "A2",
      "text": "The gradients are bounded by G",
      "explicit": true,
      "category": "theoretical",
      "severity": "critical",
      "standard_in_field": true,
      "affects_claims": [],
      "potential_issues": [
        "Gradient clipping may be needed to enforce this"
      ],
      "recommendations": [
        "Note if gradient clipping is used in experiments"
      ]
    },
    {
      "id": "A3",
      "text": "The convergence rate O(1/t) is measured in iterations, not wall-clock time",
      "explicit": false,
      "category": "theoretical",
      "severity": "moderate",
      "standard_in_field": true,
      "affects_claims": [],
      "potential_issues": [
        "Per-iteration cost may vary",
        "Practical speedup may differ from theoretical"
      ],
      "recommendations": []
    }
  ],
  "summary": {"explicit_count": 2, "implicit_count": 1, "critical_count": 2}
}
```

### Example 2: Empirical Section with Hidden Assumptions

**Input**:
```json
{
  "section_id": "sec5",
  "section_title": "Experiments",
  "section_text": "We evaluate on GLUE benchmark. Our model uses BERT-base as the backbone. We fine-tune for 3 epochs with batch size 32. Results show our method improves by 2% over the baseline.",
  "domain": "NLP",
  "claims_in_section": ["C8"]
}
```

**Output**:
```json
{
  "section_id": "sec5",
  "assumptions": [
    {
      "id": "A1",
      "text": "GLUE benchmark is representative of NLU capabilities",
      "explicit": false,
      "category": "evaluation",
      "severity": "moderate",
      "standard_in_field": true,
      "affects_claims": ["C8"],
      "potential_issues": [
        "GLUE has known limitations and biases",
        "May not reflect real-world NLU performance"
      ],
      "recommendations": [
        "Acknowledge GLUE limitations",
        "Consider additional evaluation (e.g., SuperGLUE, domain-specific)"
      ]
    },
    {
      "id": "A2",
      "text": "BERT-base is sufficient for fair comparison",
      "explicit": false,
      "category": "model",
      "severity": "minor",
      "standard_in_field": true,
      "affects_claims": ["C8"],
      "potential_issues": [],
      "recommendations": []
    },
    {
      "id": "A3",
      "text": "3 epochs is sufficient for convergence",
      "explicit": false,
      "category": "optimization",
      "severity": "minor",
      "standard_in_field": true,
      "affects_claims": ["C8"],
      "potential_issues": [],
      "recommendations": []
    },
    {
      "id": "A4",
      "text": "2% improvement is meaningful/significant",
      "explicit": false,
      "category": "evaluation",
      "severity": "moderate",
      "standard_in_field": false,
      "affects_claims": ["C8"],
      "potential_issues": [
        "No statistical significance test reported",
        "Single run may not be reproducible"
      ],
      "recommendations": [
        "Add error bars from multiple runs",
        "Include statistical significance test"
      ]
    }
  ],
  "summary": {"explicit_count": 0, "implicit_count": 4, "critical_count": 0}
}
```

## Integration Notes

### Called By
- `parallel-audit` orchestrator (per-section processing)
- `state-generator` (to populate assumptions)

### Calls
- None

### State Updates
- Populates `assumptions` array in research-state.json
- Links assumptions to affected claims
