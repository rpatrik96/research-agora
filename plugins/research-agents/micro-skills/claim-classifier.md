---
name: claim-classifier
description: |
  Classify a single claim by type and importance. Takes claim text and context,
  returns classification with confidence. Trigger: "classify claim".
model: haiku
color: gray
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: analysis
  verification-level: layered
  visibility: internal
---

# Micro-Skill: Claim Classifier

> **LLM-required**: Classifying claim evidence levels requires judgment about evidence quality. No script alternative.

> **One-line description**: Classify a single claim's type (empirical, theoretical, etc.) and importance (critical, major, minor).

## Purpose

This skill performs detailed classification of a single claim, assigning both a type and importance level. It's used when initial extraction produced uncertain classifications, or when re-classification is needed after context analysis.

## Parallelization Properties

| Property | Value |
|----------|-------|
| **Input scope** | Single claim |
| **State requirements** | Stateless |
| **External calls** | None |
| **Typical runtime** | <5s |
| **Can run in parallel** | Yes |

## Input Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["claim_text"],
  "properties": {
    "claim_text": {
      "type": "string",
      "description": "The claim to classify"
    },
    "claim_id": {
      "type": "string",
      "description": "Claim ID for tracking"
    },
    "section_context": {
      "type": "string",
      "description": "Section title or type (e.g., 'abstract', 'experiments')"
    },
    "surrounding_text": {
      "type": "string",
      "description": "Text before/after claim for context (optional)"
    },
    "evidence_refs": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Evidence references found in claim (e.g., ['tab1', 'fig2'])"
    }
  }
}
```

### Example Input

```json
{
  "claim_text": "Our model achieves 95.2% accuracy on ImageNet, surpassing the previous state-of-the-art by 3.1%",
  "claim_id": "C5",
  "section_context": "abstract",
  "evidence_refs": ["tab1"]
}
```

## Output Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["claim_id", "type", "importance", "confidence"],
  "properties": {
    "claim_id": {
      "type": "string"
    },
    "type": {
      "type": "string",
      "enum": ["empirical", "theoretical", "methodological", "comparative", "novelty", "assumed"]
    },
    "type_confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "importance": {
      "type": "string",
      "enum": ["critical", "major", "minor"]
    },
    "importance_confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "classification_rationale": {
      "type": "string",
      "description": "Brief explanation for classification"
    },
    "alternative_types": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": {"type": "string"},
          "confidence": {"type": "number"}
        }
      },
      "description": "Other possible types if uncertain"
    }
  }
}
```

### Example Output

```json
{
  "claim_id": "C5",
  "type": "empirical",
  "type_confidence": 0.85,
  "importance": "critical",
  "importance_confidence": 0.95,
  "classification_rationale": "Contains specific numeric metric (95.2% accuracy) on standard benchmark (ImageNet). Located in abstract, indicating core contribution.",
  "alternative_types": [
    {"type": "comparative", "confidence": 0.75}
  ]
}
```

## Algorithm

1. **Type classification**
   - Analyze claim text for type indicators
   - Check evidence references (tables → empirical, proofs → theoretical)
   - Consider section context
   - Assign primary type and confidence

2. **Importance classification**
   - Check location (abstract/contributions = critical)
   - Check language strength ("key", "main", "significant" = major+)
   - Check if claim is novel contribution vs supporting detail
   - Assign importance and confidence

3. **Alternative type detection**
   - If primary type confidence < 0.8, identify alternatives
   - Some claims span multiple types (comparative + empirical)

4. **Rationale generation**
   - Explain key factors in classification
   - Note any ambiguity

## Classification Criteria

### Type Classification

| Type | Indicators | Evidence Pattern |
|------|------------|------------------|
| **empirical** | Numbers, metrics, datasets, experiments | Table, figure with data |
| **theoretical** | Theorem, lemma, proof, convergence, bounds | Proof block, equations |
| **methodological** | "we propose", "our approach", algorithm description | Algorithm block |
| **comparative** | "outperforms", "better than", "vs", baseline names | Comparison table |
| **novelty** | "first", "novel", "new", "unique" | Literature gap |
| **assumed** | "well-known", implicit, citations only | Citation |

### Importance Classification

| Importance | Indicators |
|------------|------------|
| **critical** | In abstract, listed contribution, theorem statement, main result |
| **major** | In methodology or results section, supports main claims |
| **minor** | In related work, limitations, footnotes, parenthetical |

### Section-Based Priors

| Section | Typical Importance | Typical Types |
|---------|-------------------|---------------|
| Abstract | critical | all types |
| Introduction | critical/major | novelty, methodological |
| Related Work | minor | assumed |
| Methods | major | methodological, theoretical |
| Experiments | major/critical | empirical, comparative |
| Results | critical | empirical, comparative |
| Discussion | major/minor | assumed, methodological |
| Conclusion | major | all types (summarized) |

## Constraints

- **DO**: Consider multiple type possibilities for ambiguous claims
- **DO**: Weight section context heavily in importance determination
- **DO**: Provide rationale for non-obvious classifications
- **DON'T**: Verify the claim's truth (separate skill)
- **DON'T**: Look up external information
- **DON'T**: Change the claim text

## Error Handling

| Error Condition | Response |
|-----------------|----------|
| Empty claim text | `{"error": "Empty claim text", "code": "EMPTY_CLAIM"}` |
| Claim too short (<5 words) | Classify with low confidence, note in rationale |
| Ambiguous type | Return primary + alternatives with confidences |

## Context Requirements

| Context Item | Required | Source |
|--------------|----------|--------|
| Claim text | Yes | Direct input |
| Section context | No | Helps importance |
| Evidence refs | No | Helps type |

## Examples

### Example 1: Theoretical Claim

**Input**:
```json
{
  "claim_text": "We prove that the optimization converges in O(1/t²) rate under standard smoothness assumptions",
  "claim_id": "C12",
  "section_context": "sec3"
}
```

**Output**:
```json
{
  "claim_id": "C12",
  "type": "theoretical",
  "type_confidence": 0.95,
  "importance": "major",
  "importance_confidence": 0.85,
  "classification_rationale": "Contains 'prove' and convergence rate bound (O(1/t²)), classic theoretical claim pattern. In methods section, supporting but not primary contribution.",
  "alternative_types": []
}
```

### Example 2: Ambiguous Claim

**Input**:
```json
{
  "claim_text": "Our novel architecture achieves 2x speedup compared to the baseline",
  "claim_id": "C8",
  "section_context": "abstract",
  "evidence_refs": ["tab2", "fig3"]
}
```

**Output**:
```json
{
  "claim_id": "C8",
  "type": "comparative",
  "type_confidence": 0.70,
  "importance": "critical",
  "importance_confidence": 0.95,
  "classification_rationale": "Contains both novelty language ('novel architecture') and comparative metric ('2x speedup compared to'). Comparative is primary due to explicit comparison. In abstract = critical.",
  "alternative_types": [
    {"type": "empirical", "confidence": 0.65},
    {"type": "novelty", "confidence": 0.60}
  ]
}
```

### Example 3: Minor Assumed Claim

**Input**:
```json
{
  "claim_text": "Neural networks have been widely adopted for natural language processing tasks",
  "claim_id": "C2",
  "section_context": "sec2"
}
```

**Output**:
```json
{
  "claim_id": "C2",
  "type": "assumed",
  "type_confidence": 0.90,
  "importance": "minor",
  "importance_confidence": 0.95,
  "classification_rationale": "General background statement without specific evidence or novelty claim. Located in related work section. Standard knowledge claim.",
  "alternative_types": []
}
```

## Integration Notes

### Called By
- `state-generator` (if initial extraction confidence low)
- `parallel-audit` (for re-classification after evidence mapping)
- `claim-extractor` (can delegate classification)

### Calls
- None

### State Updates
- Updates claim `type` and `importance` fields in research-state.json
