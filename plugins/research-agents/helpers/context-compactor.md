---
name: context-compactor
description: |
  Generate minimal context summaries for subagent delegation. Creates
  focused context packages that preserve essential information while
  reducing token count. Trigger: "compact context", "generate subagent context".
model: sonnet
color: blue
---

# Helper: Context Compactor

> **One-line description**: Generate minimal, sufficient context packages for subagent tasks to reduce token usage.

## Purpose

This helper creates compact context packages for subagents that:
- Include only information relevant to the specific task
- Preserve essential terminology and definitions
- Reduce token count by 60-90% compared to full paper
- Enable efficient parallel processing

## Compaction Levels

| Level | Tokens | Description | Use Case |
|-------|--------|-------------|----------|
| **L1: Full** | ~30K | Complete paper | Orchestrator, cross-ref |
| **L2: Summary** | ~5K | Section summaries + relevant detail | Most subagents |
| **L3: Minimal** | ~1K | Single section + glossary | Extraction tasks |
| **L4: Micro** | ~200 | Single claim + evidence | Grading, verification |

## Input Specification

```json
{
  "type": "object",
  "required": ["research_state", "task_type"],
  "properties": {
    "research_state": {
      "type": "object",
      "description": "Full research state from research-state.json"
    },
    "task_type": {
      "type": "string",
      "enum": [
        "claim_extraction",
        "claim_classification",
        "evidence_grading",
        "novelty_checking",
        "citation_verification",
        "assumption_surfacing",
        "cross_referencing",
        "clarity_analysis"
      ]
    },
    "target_items": {
      "type": "array",
      "description": "Specific items (claim IDs, section IDs) to include"
    },
    "max_tokens": {
      "type": "integer",
      "default": 5000,
      "description": "Maximum tokens for output context"
    }
  }
}
```

### Example Input

```json
{
  "research_state": { /* full state */ },
  "task_type": "evidence_grading",
  "target_items": ["C5", "C6"],
  "max_tokens": 2000
}
```

## Output Specification

```json
{
  "type": "object",
  "required": ["context_package", "metadata"],
  "properties": {
    "context_package": {
      "type": "object",
      "properties": {
        "level": {"type": "string", "enum": ["L1", "L2", "L3", "L4"]},
        "paper_summary": {"type": "string"},
        "terminology": {"type": "object"},
        "included_sections": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "id": {"type": "string"},
              "title": {"type": "string"},
              "content": {"type": "string", "description": "Full or summarized"},
              "summarized": {"type": "boolean"}
            }
          }
        },
        "included_claims": {"type": "array"},
        "included_evidence": {"type": "object"},
        "context_markdown": {"type": "string", "description": "Ready-to-use context string"}
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "original_tokens": {"type": "integer"},
        "compacted_tokens": {"type": "integer"},
        "compression_ratio": {"type": "number"},
        "sections_summarized": {"type": "integer"},
        "sections_included_full": {"type": "integer"}
      }
    }
  }
}
```

## Context Templates by Task

### L2 Summary Template (Most Subagents)

```markdown
# Paper Context (Compact)

## Metadata
- **Title**: [title]
- **Venue Target**: [venue]
- **Main Contribution**: [1-sentence summary]

## Key Terminology
| Term | Definition |
|------|------------|
| [term1] | [definition] |
| [term2] | [definition] |

## Structure Overview
- **Abstract**: [1-sentence summary]
- **Introduction**: [1-sentence summary]
- **Methods**: [1-sentence summary]
- **Experiments**: [1-sentence summary]
- **Conclusion**: [1-sentence summary]

## Relevant Section: [section_id]
[Full text of section relevant to task]

## Evidence References
| Ref | Type | Caption |
|-----|------|---------|
| tab1 | table | [brief caption] |
| fig2 | figure | [brief caption] |
```

### L3 Minimal Template (Extraction Tasks)

```markdown
# Minimal Context

**Paper**: [title]
**Target Section**: [section_id] - [section_title]

## Section Text
[full section text]

## Relevant Terms
- [term1]: [definition]
- [term2]: [definition]

## Task
[specific instruction for extraction]
```

### L4 Micro Template (Single-Item Tasks)

```markdown
# Task Context

**Claim**: "[claim text]"
**Type**: [claim type]
**Location**: [section]

## Evidence
### [ref_id]: [type]
[evidence content]

## Task
[specific grading/verification instruction]
```

## Compaction Algorithm

### Step 1: Determine Compaction Level

```python
def determine_level(task_type, target_items, max_tokens):
    """Select appropriate compaction level."""

    task_levels = {
        "claim_extraction": "L3",
        "claim_classification": "L4",
        "evidence_grading": "L4",
        "novelty_checking": "L4",
        "citation_verification": "L4",
        "assumption_surfacing": "L3",
        "cross_referencing": "L2",
        "clarity_analysis": "L3"
    }

    base_level = task_levels.get(task_type, "L2")

    # Adjust based on token budget
    if max_tokens < 500:
        return "L4"
    elif max_tokens < 2000:
        return min_level(base_level, "L3")
    else:
        return base_level
```

### Step 2: Extract Required Elements

```python
def extract_required(research_state, task_type, target_items):
    """Identify what must be included."""

    required = {
        "sections": set(),
        "claims": set(),
        "evidence": set(),
        "terminology": set()
    }

    # Add target items
    for item in target_items:
        if item.startswith("C"):  # Claim
            required["claims"].add(item)
            claim = get_claim(research_state, item)
            required["sections"].add(claim["location"]["section"])
            required["evidence"].update(claim.get("evidence_refs", []))
        elif item.startswith("sec"):  # Section
            required["sections"].add(item)

    # Add task-specific requirements
    if task_type == "cross_referencing":
        required["claims"] = set(c["id"] for c in research_state["claims"])

    return required
```

### Step 3: Summarize Non-Essential Sections

```python
def summarize_section(section_text, max_sentences=2):
    """Generate brief summary of section."""
    # Extract first sentence as topic
    # Extract conclusion sentence if present
    # Combine into summary
    return summary
```

### Step 4: Build Terminology Glossary

```python
def build_glossary(research_state, required_terms, max_terms=10):
    """Extract most relevant terminology."""
    glossary = {}

    # Priority: terms used in target claims
    # Then: terms defined in paper
    # Then: domain-standard terms

    for term in prioritized_terms[:max_terms]:
        glossary[term] = research_state["terminology"].get(term, "")

    return glossary
```

### Step 5: Assemble Context Package

```python
def assemble_context(level, components):
    """Build final context markdown."""

    if level == "L4":
        return MICRO_TEMPLATE.format(**components)
    elif level == "L3":
        return MINIMAL_TEMPLATE.format(**components)
    else:
        return SUMMARY_TEMPLATE.format(**components)
```

## Task-Specific Context Requirements

| Task | Level | Required Context |
|------|-------|------------------|
| claim_extraction | L3 | Section text, terminology |
| claim_classification | L4 | Claim text, type indicators |
| evidence_grading | L4 | Claim, evidence content, venue |
| novelty_checking | L4 | Claim, keywords, paper date |
| citation_verification | L4 | Citation entry, claim about it |
| assumption_surfacing | L3 | Section text, claims in section |
| cross_referencing | L2 | All claims, structure overview |
| clarity_analysis | L3 | Section text, terminology |

## Token Estimation

```python
def estimate_tokens(text):
    """Estimate token count."""
    # GPT-style: ~4 chars per token
    return len(text) // 4

def fit_to_budget(components, max_tokens):
    """Trim components to fit budget."""
    current = estimate_tokens(str(components))

    while current > max_tokens:
        # Remove least important component
        # Summarize longest section
        # Trim terminology
        pass

    return components
```

## Error Handling

| Error | Response |
|-------|----------|
| Target item not found | Skip, note in metadata |
| Cannot fit in budget | Return minimal context, warn |
| Missing terminology | Omit glossary section |
| Section text too long | Summarize to fit |

## Constraints

- **DO**: Preserve exact claim text (never paraphrase)
- **DO**: Include all referenced evidence
- **DO**: Maintain terminology definitions
- **DON'T**: Include unrelated sections
- **DON'T**: Exceed token budget
- **DON'T**: Remove evidence from target claims

## Example: Evidence Grading Context

**Input**:
```json
{
  "task_type": "evidence_grading",
  "target_items": ["C5"],
  "max_tokens": 1000
}
```

**Output context_markdown**:
```markdown
# Task Context

**Claim C5**: "Our model achieves 96.2% accuracy on CIFAR-10, outperforming ResNet-50 by 2.1%"
**Type**: empirical + comparative
**Location**: sec4 (Experiments)
**Venue**: neurips

## Evidence

### tab1: Results Table
| Method | CIFAR-10 | ImageNet |
|--------|----------|----------|
| ResNet-50 | 94.1 ± 0.2 | 76.5 |
| Ours | 96.2 ± 0.3 | 78.2 |

*Has error bars: Yes*

## Key Terms
- **CIFAR-10**: Standard image classification benchmark (10 classes, 60K images)

## Task
Grade evidence strength (L1-L6) for this claim. Check:
1. Does table support the claimed accuracy (96.2%)?
2. Does table support the comparison (2.1% over ResNet)?
3. Are error bars present?
4. Does evidence meet NeurIPS standards?
```

**Metadata**:
```json
{
  "original_tokens": 28000,
  "compacted_tokens": 450,
  "compression_ratio": 62.2,
  "sections_summarized": 6,
  "sections_included_full": 0
}
```

## Integration Notes

### Called By
- Orchestrators before spawning subagents
- Any agent needing to delegate with scoped context

### Calls
- Research state (read only)
- Token estimator utility

### State Updates
- None (read-only utility)
