---
name: claim-extractor
description: |
  Extract all claims from a single paper section. Operates on section text only,
  no cross-references needed. Trigger: "extract claims from section".
model: haiku
color: gray
---

# Micro-Skill: Claim Extractor

> **LLM-required**: Extracting claims from prose requires understanding scientific assertions. No script alternative.

> **One-line description**: Extract explicit and implicit claims from a single section of text.

## Purpose

This skill identifies all claims (statements that require evidence) within a single paper section. It operates independently on section text, making it ideal for parallel processing across sections. The orchestrator aggregates results from multiple instances.

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
  "required": ["section_id", "section_title", "section_text"],
  "properties": {
    "section_id": {
      "type": "string",
      "description": "Section identifier (e.g., 'sec1', 'abstract')"
    },
    "section_title": {
      "type": "string",
      "description": "Human-readable section title"
    },
    "section_text": {
      "type": "string",
      "description": "Full text content of the section"
    },
    "line_offset": {
      "type": "integer",
      "default": 1,
      "description": "Starting line number for location tracking"
    }
  }
}
```

### Example Input

```json
{
  "section_id": "sec4",
  "section_title": "Experiments",
  "section_text": "We evaluate our method on CIFAR-10 and ImageNet. Our approach achieves 96.2% accuracy on CIFAR-10, outperforming ResNet-50 by 2.1%. Table 2 shows detailed results.",
  "line_offset": 145
}
```

## Output Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["claims", "section_id", "extraction_stats"],
  "properties": {
    "claims": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "text", "location", "type", "confidence"],
        "properties": {
          "id": {
            "type": "string",
            "description": "Temporary ID (e.g., 'sec4_c1')"
          },
          "text": {
            "type": "string",
            "description": "The claim text"
          },
          "location": {
            "type": "object",
            "properties": {
              "line_start": {"type": "integer"},
              "line_end": {"type": "integer"}
            }
          },
          "type": {
            "type": "string",
            "enum": ["empirical", "theoretical", "methodological", "comparative", "novelty", "assumed"]
          },
          "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          },
          "extraction_pattern": {
            "type": "string",
            "description": "Which pattern matched"
          }
        }
      }
    },
    "section_id": {
      "type": "string"
    },
    "extraction_stats": {
      "type": "object",
      "properties": {
        "explicit_count": {"type": "integer"},
        "implicit_count": {"type": "integer"},
        "total": {"type": "integer"}
      }
    }
  }
}
```

### Example Output

```json
{
  "claims": [
    {
      "id": "sec4_c1",
      "text": "Our approach achieves 96.2% accuracy on CIFAR-10",
      "location": {"line_start": 146, "line_end": 146},
      "type": "empirical",
      "confidence": 0.95,
      "extraction_pattern": "Our (method|approach) achieves"
    },
    {
      "id": "sec4_c2",
      "text": "outperforming ResNet-50 by 2.1%",
      "location": {"line_start": 146, "line_end": 146},
      "type": "comparative",
      "confidence": 0.90,
      "extraction_pattern": "outperforming X by Y"
    }
  ],
  "section_id": "sec4",
  "extraction_stats": {
    "explicit_count": 1,
    "implicit_count": 1,
    "total": 2
  }
}
```

## Algorithm

1. **Sentence segmentation**
   - Split section into sentences
   - Track line numbers for each sentence

2. **Explicit claim detection**
   - Match against explicit patterns (see below)
   - Extract full claim text including context
   - Assign high confidence (0.85-0.95)

3. **Implicit claim detection**
   - Match against implicit patterns
   - Extract claim with surrounding context
   - Assign medium confidence (0.6-0.8)

4. **Multi-sentence claim merging**
   - If consecutive sentences form single claim, merge
   - Example: "We show X. Specifically, Y." → single claim

5. **ID assignment**
   - Assign temporary IDs: `{section_id}_c{n}`
   - Orchestrator will reassign global IDs later

6. **Statistics calculation**
   - Count explicit vs implicit claims
   - Return totals

## Extraction Patterns

### Explicit Claim Patterns

| Pattern | Type | Confidence |
|---------|------|------------|
| `We (show\|demonstrate\|prove) that...` | empirical/theoretical | 0.95 |
| `Our (method\|approach\|model) (achieves\|obtains)...` | empirical | 0.95 |
| `Theorem \d+:` / `Lemma \d+:` | theoretical | 0.98 |
| `Experiments (show\|demonstrate\|reveal)...` | empirical | 0.90 |
| `We propose...` / `We introduce...` | methodological | 0.90 |
| `Contributions:` list items | varies | 0.95 |

### Implicit Claim Patterns

| Pattern | Type | Confidence |
|---------|------|------------|
| `X outperforms Y` | comparative | 0.85 |
| `better than` / `faster than` / `more efficient` | comparative | 0.80 |
| `(first\|novel\|new) (approach\|method)` | novelty | 0.85 |
| `state-of-the-art` | comparative | 0.80 |
| `significant(ly)? (improvement\|better)` | empirical | 0.75 |
| Numbers + metrics without hedging | empirical | 0.70 |

### Non-Claim Patterns (Exclude)

- Hedged statements: "may", "might", "could potentially"
- Related work descriptions: "Previous work showed..."
- Definitions without claims
- Background/context statements

## Constraints

- **DO**: Extract verbatim or near-verbatim claim text
- **DO**: Preserve exact numbers, percentages, metrics
- **DO**: Include evidence references found in claim text (e.g., "Table 2")
- **DON'T**: Cross-reference other sections
- **DON'T**: Verify claims (that's evidence-grader's job)
- **DON'T**: Access external resources
- **DON'T**: Extract more than 50 claims per section (flag overflow)

## Error Handling

| Error Condition | Response |
|-----------------|----------|
| Empty section text | Return `{"claims": [], "section_id": "...", "extraction_stats": {"explicit_count": 0, "implicit_count": 0, "total": 0}}` |
| Section too long (>10K words) | Return `{"error": "Section exceeds maximum length", "code": "SECTION_TOO_LONG"}` |
| >50 claims detected | Return claims + `{"warning": "Claim limit reached, some may be omitted"}` |

## Context Requirements

| Context Item | Required | Source |
|--------------|----------|--------|
| Section text | Yes | Direct input |
| Section title | Yes | Direct input |
| Line offset | No | Default 1 |

## Examples

### Example 1: Methodology Section

**Scenario**: Extracting claims from a methods section

**Input**:
```json
{
  "section_id": "sec3",
  "section_title": "Methodology",
  "section_text": "We propose a novel attention mechanism that operates in O(n) time complexity. Unlike standard attention which requires O(n²) computation, our approach scales linearly with sequence length. The key insight is that we can approximate the attention matrix using random features.",
  "line_offset": 80
}
```

**Output**:
```json
{
  "claims": [
    {
      "id": "sec3_c1",
      "text": "We propose a novel attention mechanism that operates in O(n) time complexity",
      "location": {"line_start": 80, "line_end": 80},
      "type": "methodological",
      "confidence": 0.92,
      "extraction_pattern": "We propose...novel"
    },
    {
      "id": "sec3_c2",
      "text": "our approach scales linearly with sequence length",
      "location": {"line_start": 81, "line_end": 81},
      "type": "theoretical",
      "confidence": 0.88,
      "extraction_pattern": "our approach [property]"
    }
  ],
  "section_id": "sec3",
  "extraction_stats": {"explicit_count": 2, "implicit_count": 0, "total": 2}
}
```

### Example 2: Abstract with Multiple Claim Types

**Scenario**: Dense abstract with various claim types

**Input**:
```json
{
  "section_id": "abstract",
  "section_title": "Abstract",
  "section_text": "Large language models have shown remarkable capabilities. We introduce GPT-5, the first model to achieve human-level reasoning on all benchmarks. Our model achieves 95% accuracy on GSM8K, outperforming GPT-4 by 15%. We prove that the model's capabilities scale predictably with compute.",
  "line_offset": 1
}
```

**Output**:
```json
{
  "claims": [
    {
      "id": "abstract_c1",
      "text": "We introduce GPT-5, the first model to achieve human-level reasoning on all benchmarks",
      "location": {"line_start": 1, "line_end": 1},
      "type": "novelty",
      "confidence": 0.95,
      "extraction_pattern": "We introduce...first"
    },
    {
      "id": "abstract_c2",
      "text": "Our model achieves 95% accuracy on GSM8K",
      "location": {"line_start": 2, "line_end": 2},
      "type": "empirical",
      "confidence": 0.95,
      "extraction_pattern": "achieves X% accuracy"
    },
    {
      "id": "abstract_c3",
      "text": "outperforming GPT-4 by 15%",
      "location": {"line_start": 2, "line_end": 2},
      "type": "comparative",
      "confidence": 0.90,
      "extraction_pattern": "outperforming X by Y"
    },
    {
      "id": "abstract_c4",
      "text": "We prove that the model's capabilities scale predictably with compute",
      "location": {"line_start": 3, "line_end": 3},
      "type": "theoretical",
      "confidence": 0.95,
      "extraction_pattern": "We prove that"
    }
  ],
  "section_id": "abstract",
  "extraction_stats": {"explicit_count": 3, "implicit_count": 1, "total": 4}
}
```

### Example 3: Related Work (Few Claims)

**Scenario**: Related work section typically has few original claims

**Input**:
```json
{
  "section_id": "sec2",
  "section_title": "Related Work",
  "section_text": "Attention mechanisms were introduced by Bahdanau et al. (2014). The Transformer architecture (Vaswani et al., 2017) demonstrated that attention alone is sufficient for sequence modeling. Several works have extended this approach to vision tasks. Our work differs from these approaches in two key ways.",
  "line_offset": 30
}
```

**Output**:
```json
{
  "claims": [
    {
      "id": "sec2_c1",
      "text": "Our work differs from these approaches in two key ways",
      "location": {"line_start": 33, "line_end": 33},
      "type": "novelty",
      "confidence": 0.75,
      "extraction_pattern": "Our work differs"
    }
  ],
  "section_id": "sec2",
  "extraction_stats": {"explicit_count": 0, "implicit_count": 1, "total": 1}
}
```

**Explanation**: Statements about prior work are not claims by this paper. Only the differentiation statement is a claim.

## Integration Notes

### Called By
- `state-generator` agent (initial extraction)
- `parallel-audit` orchestrator (per-section processing)

### Calls
- None (stateless, no external dependencies)

### State Updates
- None (produces output only, orchestrator aggregates)
