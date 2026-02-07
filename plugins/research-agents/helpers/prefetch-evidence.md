---
name: prefetch-evidence
description: |
  Pre-fetch all evidence references from a paper before parallel analysis.
  Loads tables, figures, equations into memory for fast subagent access.
  Trigger: "prefetch evidence", "load paper evidence".
model: haiku
color: gray
---

# Helper: Evidence Pre-fetcher

> **Script-first**: Evidence prefetching uses grep/glob to collect files. LLM is not needed for the collection step.

> **One-line description**: Load all evidence elements from a paper into structured format for efficient subagent access.

## Purpose

This helper extracts and caches all evidence content (tables, figures, equations, algorithms) from a paper before spawning subagents. This avoids:
- Each subagent re-reading the paper
- Duplicate parsing of the same content
- Context bloat from full paper text

Subagents receive only the specific evidence they need.

## Input Specification

```json
{
  "type": "object",
  "required": ["paper_path"],
  "properties": {
    "paper_path": {
      "type": "string",
      "description": "Path to paper (LaTeX or PDF)"
    },
    "research_state_path": {
      "type": "string",
      "description": "Path to research-state.json (optional, will be generated if missing)"
    },
    "extract_types": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["tables", "figures", "equations", "algorithms", "theorems", "code"]
      },
      "default": ["tables", "figures", "equations", "algorithms", "theorems"]
    }
  }
}
```

### Example Input

```json
{
  "paper_path": "/papers/my-paper/main.tex",
  "extract_types": ["tables", "figures", "equations"]
}
```

## Output Specification

```json
{
  "type": "object",
  "required": ["evidence_cache", "stats"],
  "properties": {
    "evidence_cache": {
      "type": "object",
      "properties": {
        "tables": {
          "type": "object",
          "additionalProperties": {
            "type": "object",
            "properties": {
              "id": {"type": "string"},
              "caption": {"type": "string"},
              "content": {"type": "string", "description": "Markdown table format"},
              "section": {"type": "string"},
              "has_error_bars": {"type": "boolean"},
              "columns": {"type": "array", "items": {"type": "string"}},
              "row_count": {"type": "integer"}
            }
          }
        },
        "figures": {
          "type": "object",
          "additionalProperties": {
            "type": "object",
            "properties": {
              "id": {"type": "string"},
              "caption": {"type": "string"},
              "description": {"type": "string", "description": "Generated description if available"},
              "section": {"type": "string"},
              "file_path": {"type": "string"}
            }
          }
        },
        "equations": {
          "type": "object",
          "additionalProperties": {
            "type": "object",
            "properties": {
              "id": {"type": "string"},
              "label": {"type": "string"},
              "latex": {"type": "string"},
              "section": {"type": "string"}
            }
          }
        },
        "algorithms": {
          "type": "object",
          "additionalProperties": {
            "type": "object",
            "properties": {
              "id": {"type": "string"},
              "caption": {"type": "string"},
              "pseudocode": {"type": "string"},
              "section": {"type": "string"}
            }
          }
        },
        "theorems": {
          "type": "object",
          "additionalProperties": {
            "type": "object",
            "properties": {
              "id": {"type": "string"},
              "type": {"type": "string"},
              "statement": {"type": "string"},
              "proof": {"type": "string"},
              "section": {"type": "string"}
            }
          }
        }
      }
    },
    "stats": {
      "type": "object",
      "properties": {
        "tables": {"type": "integer"},
        "figures": {"type": "integer"},
        "equations": {"type": "integer"},
        "algorithms": {"type": "integer"},
        "theorems": {"type": "integer"},
        "total_tokens_estimated": {"type": "integer"},
        "extraction_time_ms": {"type": "integer"}
      }
    }
  }
}
```

### Example Output

```json
{
  "evidence_cache": {
    "tables": {
      "tab1": {
        "id": "tab1",
        "caption": "Main results on ImageNet and CIFAR-10",
        "content": "| Method | ImageNet | CIFAR-10 |\n|--------|----------|----------|\n| ResNet | 76.5 ± 0.3 | 94.1 ± 0.2 |\n| Ours | 78.2 ± 0.2 | 96.2 ± 0.3 |",
        "section": "sec4",
        "has_error_bars": true,
        "columns": ["Method", "ImageNet", "CIFAR-10"],
        "row_count": 2
      }
    },
    "figures": {
      "fig1": {
        "id": "fig1",
        "caption": "Model architecture overview showing the transformer encoder-decoder structure",
        "description": "Diagram showing encoder (left) and decoder (right) with attention layers",
        "section": "sec3",
        "file_path": "figures/architecture.pdf"
      }
    },
    "equations": {
      "eq1": {
        "id": "eq1",
        "label": "eq:attention",
        "latex": "\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V",
        "section": "sec3"
      }
    }
  },
  "stats": {
    "tables": 3,
    "figures": 5,
    "equations": 8,
    "algorithms": 1,
    "theorems": 2,
    "total_tokens_estimated": 4500,
    "extraction_time_ms": 850
  }
}
```

## Algorithm

### Table Extraction

```python
def extract_table(table_env):
    """Extract table content to markdown format."""
    # 1. Find \begin{tabular} content
    # 2. Parse column spec for headers
    # 3. Convert rows to markdown
    # 4. Detect error bars (± or \pm)
    # 5. Extract caption
    return {
        "content": markdown_table,
        "caption": caption,
        "has_error_bars": "±" in content or "\\pm" in content,
        "columns": headers,
        "row_count": len(rows)
    }
```

### Figure Extraction

```python
def extract_figure(figure_env):
    """Extract figure metadata and generate description."""
    # 1. Extract caption from \caption{}
    # 2. Find \includegraphics path
    # 3. If multimodal available, generate description
    # 4. Otherwise, use caption + context
    return {
        "caption": caption,
        "description": generated_or_caption,
        "file_path": image_path
    }
```

### Equation Extraction

```python
def extract_equation(equation_env):
    """Extract equation with label."""
    # 1. Extract LaTeX content
    # 2. Find \label{} if present
    # 3. Clean up formatting
    return {
        "latex": cleaned_latex,
        "label": label
    }
```

### Theorem Extraction

```python
def extract_theorem(theorem_env, theorem_type):
    """Extract theorem statement and proof if present."""
    # 1. Extract statement
    # 2. Look for \begin{proof} after theorem
    # 3. Extract proof content if found
    return {
        "type": theorem_type,
        "statement": statement,
        "proof": proof_content,
        "has_proof": proof_content is not None
    }
```

## Subagent Evidence Delivery

When spawning a subagent for a claim, deliver only relevant evidence:

```python
def get_evidence_for_claim(claim, evidence_cache, evidence_map):
    """Extract relevant evidence for a specific claim."""
    relevant = {}

    for evidence_ref in evidence_map.get(claim["id"], []):
        ref_type = evidence_ref["type"]
        ref_id = evidence_ref["ref"]

        if ref_type == "table" and ref_id in evidence_cache["tables"]:
            relevant[ref_id] = evidence_cache["tables"][ref_id]
        elif ref_type == "figure" and ref_id in evidence_cache["figures"]:
            relevant[ref_id] = evidence_cache["figures"][ref_id]
        # ... etc

    return relevant
```

## Token Estimation

```python
def estimate_tokens(content):
    """Estimate token count for context budgeting."""
    # Rough estimate: 1 token ≈ 4 characters
    return len(content) // 4
```

## Caching

Evidence cache is stored alongside research-state.json:

```
paper_directory/
├── main.tex
├── research-state.json
└── .evidence-cache.json  # Pre-fetched evidence
```

## Error Handling

| Error | Response |
|-------|----------|
| LaTeX parse error | Log warning, skip element, continue |
| Missing figure file | Note in description, continue |
| Malformed table | Return raw content, mark as unparsed |
| PDF extraction fails | Skip figures, extract text only |

## Constraints

- **DO**: Extract all requested evidence types
- **DO**: Convert tables to readable markdown
- **DO**: Estimate token counts for context budgeting
- **DON'T**: Include full paper text
- **DON'T**: Process images (just metadata)
- **DON'T**: Cache more than 7 days

## Integration Notes

### Called By
- `parallel-audit` orchestrator (before spawning subagents)
- `state-generator` agent (during initial parsing)

### Calls
- Local file system (paper reading)
- LaTeX parser

### State Updates
- Creates `.evidence-cache.json` in paper directory
- Updates `evidence_map` in research-state.json if needed
