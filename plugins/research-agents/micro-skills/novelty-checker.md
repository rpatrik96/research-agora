---
name: novelty-checker
description: |
  Verify novelty claims by searching arXiv for prior/concurrent work.
  Uses batch queries for efficiency. Trigger: "check novelty claim",
  "verify novelty", "search for prior work".
model: sonnet
color: orange
---

# Micro-Skill: Novelty Checker

> **Hybrid**: Prior work search uses MCP/API tools. LLM assesses novelty relative to discovered prior art.

> **One-line description**: Verify novelty claims by searching academic literature for prior and concurrent work.

## Purpose

This skill verifies claims about novelty ("first to...", "novel approach", "new method") by searching arXiv for potentially overlapping prior work. It identifies relevant papers, assesses overlap, and classifies work as prior (challenge) or concurrent (acknowledge).

## Parallelization Properties

| Property | Value |
|----------|-------|
| **Input scope** | Single claim |
| **State requirements** | Needs paper_date for temporal filtering |
| **External calls** | arXiv MCP tools |
| **Typical runtime** | 30-120s |
| **Can run in parallel** | Yes (rate-limited) |

## Input Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["claim"],
  "properties": {
    "claim": {
      "type": "object",
      "required": ["id", "text"],
      "properties": {
        "id": {"type": "string"},
        "text": {"type": "string"},
        "type": {"type": "string"},
        "keywords": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Pre-extracted keywords for search"
        }
      }
    },
    "search_queries": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Pre-generated search queries (optional)"
    },
    "paper_date": {
      "type": "string",
      "format": "date",
      "description": "Submission/publication date for temporal filtering"
    },
    "paper_arxiv_id": {
      "type": "string",
      "description": "ArXiv ID of paper being analyzed (to exclude from results)"
    }
  }
}
```

### Example Input

```json
{
  "claim": {
    "id": "C3",
    "text": "We are the first to apply transformers to protein folding prediction",
    "type": "novelty",
    "keywords": ["transformer", "protein folding", "structure prediction"]
  },
  "paper_date": "2024-06-15",
  "paper_arxiv_id": "2406.12345"
}
```

## Output Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["claim_id", "novelty_verdict"],
  "properties": {
    "claim_id": {"type": "string"},
    "searches_performed": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "query": {"type": "string"},
          "results_count": {"type": "integer"},
          "relevant_papers": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "arxiv_id": {"type": "string"},
                "title": {"type": "string"},
                "date": {"type": "string"},
                "relevance": {"type": "string", "enum": ["high", "medium", "low"]},
                "overlap_description": {"type": "string"}
              }
            }
          }
        }
      }
    },
    "novelty_verdict": {
      "type": "string",
      "enum": ["confirmed", "challenged", "requires_clarification"]
    },
    "prior_work": {
      "type": "array",
      "items": {"type": "string"},
      "description": "ArXiv IDs of prior work that challenges novelty"
    },
    "concurrent_work": {
      "type": "array",
      "items": {"type": "string"},
      "description": "ArXiv IDs of concurrent work (within 6 months)"
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "recommendations": {
      "type": "array",
      "items": {"type": "string"}
    }
  }
}
```

### Example Output

```json
{
  "claim_id": "C3",
  "searches_performed": [
    {
      "query": "transformer protein folding",
      "results_count": 45,
      "relevant_papers": [
        {
          "arxiv_id": "2106.04426",
          "title": "AlphaFold2: Using attention mechanisms for protein structure prediction",
          "date": "2021-06-08",
          "relevance": "high",
          "overlap_description": "Uses attention mechanisms (transformer component) for protein structure prediction. Published 3 years prior."
        }
      ]
    }
  ],
  "novelty_verdict": "challenged",
  "prior_work": ["2106.04426"],
  "concurrent_work": [],
  "confidence": 0.85,
  "recommendations": [
    "Revise claim: 'We are the first to apply...' → 'We propose a novel application of...'",
    "Cite AlphaFold2 and discuss how your approach differs",
    "Clarify the specific novelty (e.g., 'first to use full transformer architecture' vs 'first to use attention')"
  ]
}
```

## Algorithm

1. **Generate search queries**
   - If not provided, extract from claim text
   - Create 3-5 query variations:
     - Direct keywords: "[method] [application]"
     - Technique-focused: "[core technique] [domain]"
     - Problem-focused: "[problem statement]"
     - Synonym expansion

2. **Execute arXiv searches**
   - Use `mcp__arxiv__search_papers` for each query
   - Filter results by date (before paper_date)
   - Limit to 10 results per query
   - Rate limit: max 3 requests per second

3. **Filter and rank results**
   - Exclude self-citations (paper_arxiv_id)
   - Rank by relevance to claim
   - Classify temporal relationship:
     - **Prior**: > 6 months before submission
     - **Concurrent**: within 6 months of submission
     - **After**: ignore

4. **Assess overlap for relevant papers**
   - For high-relevance papers (top 3-5):
     - Read abstract via `mcp__arxiv__get_paper_by_id`
     - Determine overlap with claimed novelty
     - Document specific overlap

5. **Generate verdict**
   - `confirmed`: No relevant prior work found
   - `challenged`: High-relevance prior work exists
   - `requires_clarification`: Partial overlap, claim could be refined

6. **Generate recommendations**
   - If challenged: How to revise claim
   - If concurrent: What to cite/acknowledge
   - If confirmed: Note search limitations

## Search Strategies

### Query Generation

| Claim Pattern | Query Strategy | Example |
|---------------|----------------|---------|
| "first to X" | Direct: X | "transformer protein folding" |
| "novel [method]" | Method + domain | "attention mechanism NLP" |
| "new approach to [problem]" | Problem keywords | "efficient graph neural networks" |
| "unique [property]" | Property + method | "linear attention transformer" |

### Keyword Extraction

Extract from claim text:
- Technical terms (capitalized, hyphenated)
- Method names
- Application domains
- Metrics mentioned

### Synonym Expansion

| Term | Synonyms |
|------|----------|
| transformer | attention mechanism, self-attention |
| neural network | deep learning, NN |
| efficient | fast, scalable, lightweight |
| novel | new, first, unique |

## Temporal Classification

| Category | Timing | Impact on Novelty |
|----------|--------|-------------------|
| **Prior work** | > 6 months before | Challenges novelty |
| **Concurrent** | ± 6 months | Acknowledge, doesn't invalidate |
| **After** | After submission | Ignore |

## MCP Tool Usage

```
# Search for papers
mcp__arxiv__search_papers(
  query="transformer protein folding",
  maxResults=10,
  sortBy="relevance"
)

# Get paper details
mcp__arxiv__get_paper_by_id(
  ids=["2106.04426"]
)
```

## Constraints

- **DO**: Search multiple query variations
- **DO**: Filter by temporal relationship
- **DO**: Provide specific overlap descriptions
- **DO**: Generate actionable recommendations
- **DON'T**: Make more than 5 searches per claim
- **DON'T**: Return more than 10 relevant papers
- **DON'T**: Search non-arXiv sources
- **DON'T**: Verify other claim types (empirical, etc.)

## Error Handling

| Error Condition | Response |
|-----------------|----------|
| ArXiv API unavailable | Return `{"error": "ArXiv API unavailable", "code": "API_ERROR"}` |
| No search results | Return `confirmed` with note about search limitations |
| Rate limited | Retry with backoff, max 3 attempts |
| paper_date missing | Use current date, note in output |

## Context Requirements

| Context Item | Required | Source |
|--------------|----------|--------|
| Claim | Yes | Direct input |
| paper_date | Recommended | research-state.json metadata |
| paper_arxiv_id | Recommended | For self-exclusion |
| keywords | No | Auto-extracted if missing |

## Examples

### Example 1: Novelty Confirmed

**Input**:
```json
{
  "claim": {
    "id": "C8",
    "text": "We propose the first method to perform real-time neural radiance field rendering on mobile devices",
    "type": "novelty"
  },
  "paper_date": "2024-01-15"
}
```

**Output**:
```json
{
  "claim_id": "C8",
  "searches_performed": [
    {"query": "neural radiance field mobile rendering", "results_count": 8, "relevant_papers": []},
    {"query": "real-time NeRF mobile", "results_count": 3, "relevant_papers": []},
    {"query": "efficient NeRF edge device", "results_count": 12, "relevant_papers": [
      {
        "arxiv_id": "2308.12345",
        "title": "MobileNeRF: Efficient Neural Radiance Fields for Edge Computing",
        "date": "2023-08-15",
        "relevance": "medium",
        "overlap_description": "Addresses efficient NeRF but targets edge servers, not mobile devices"
      }
    ]}
  ],
  "novelty_verdict": "confirmed",
  "prior_work": [],
  "concurrent_work": [],
  "confidence": 0.75,
  "recommendations": [
    "Cite MobileNeRF (2308.12345) as related work on efficient NeRF",
    "Note search limitations: arXiv only, some mobile graphics work may be in ACM/IEEE",
    "Consider searching for 'smartphone' and 'mobile GPU' variations"
  ]
}
```

### Example 2: Requires Clarification

**Input**:
```json
{
  "claim": {
    "id": "C12",
    "text": "Our approach is the first to combine contrastive learning with graph neural networks",
    "type": "novelty"
  },
  "paper_date": "2024-03-01"
}
```

**Output**:
```json
{
  "claim_id": "C12",
  "searches_performed": [
    {"query": "contrastive learning graph neural network", "results_count": 156, "relevant_papers": [
      {
        "arxiv_id": "2006.04131",
        "title": "Graph Contrastive Learning with Augmentations",
        "date": "2020-06-07",
        "relevance": "high",
        "overlap_description": "Directly combines contrastive learning with GNNs for node classification"
      },
      {
        "arxiv_id": "2010.00826",
        "title": "GCC: Graph Contrastive Coding for Graph Neural Network Pre-Training",
        "date": "2020-10-02",
        "relevance": "high",
        "overlap_description": "Uses contrastive learning for GNN pre-training"
      }
    ]}
  ],
  "novelty_verdict": "challenged",
  "prior_work": ["2006.04131", "2010.00826"],
  "concurrent_work": [],
  "confidence": 0.95,
  "recommendations": [
    "Remove 'first to combine' claim - multiple prior works exist from 2020",
    "Cite GraphCL (2006.04131) and GCC (2010.00826)",
    "Clarify specific novelty: 'first to apply to [specific domain]' or 'first to use [specific technique]'",
    "Consider: 'Building on contrastive learning for graphs [cite], we propose...'"
  ]
}
```

### Example 3: Concurrent Work Found

**Input**:
```json
{
  "claim": {
    "id": "C5",
    "text": "We introduce the first dataset for multilingual code generation",
    "type": "novelty"
  },
  "paper_date": "2024-02-15"
}
```

**Output**:
```json
{
  "claim_id": "C5",
  "searches_performed": [
    {"query": "multilingual code generation dataset", "results_count": 23, "relevant_papers": [
      {
        "arxiv_id": "2401.01234",
        "title": "MultiCode: A Benchmark for Multilingual Code Generation",
        "date": "2024-01-05",
        "relevance": "high",
        "overlap_description": "Multilingual code generation dataset released 6 weeks before"
      }
    ]}
  ],
  "novelty_verdict": "requires_clarification",
  "prior_work": [],
  "concurrent_work": ["2401.01234"],
  "confidence": 0.80,
  "recommendations": [
    "Acknowledge concurrent work: 'Concurrently, [cite] also released...'",
    "Differentiate: Specify unique aspects (languages covered, task types, size)",
    "Consider: 'independently developed' or 'complementary to'"
  ]
}
```

## Integration Notes

### Called By
- `parallel-audit` orchestrator (for novelty claims)
- Can be called directly for novelty verification

### Calls
- `mcp__arxiv__search_papers`
- `mcp__arxiv__get_paper_by_id`

### State Updates
- Updates claim `verification_status` for novelty claims
- Adds `prior_work` and `concurrent_work` to claim details
