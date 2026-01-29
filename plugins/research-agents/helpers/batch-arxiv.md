---
name: batch-arxiv
description: |
  Execute multiple arXiv searches efficiently. Collects queries, deduplicates,
  executes with rate limiting, and caches results. Trigger: "batch arxiv search".
model: haiku
color: gray
---

# Helper: Batch ArXiv Search

> **One-line description**: Efficiently execute multiple arXiv searches with deduplication, caching, and rate limiting.

## Purpose

This helper optimizes arXiv API usage when multiple searches are needed (e.g., checking novelty for multiple claims). It:
- Deduplicates similar queries
- Checks cache for recent results
- Executes with rate limiting (3 req/sec)
- Merges and deduplicates results

## Input Specification

```json
{
  "type": "object",
  "required": ["queries"],
  "properties": {
    "queries": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "query"],
        "properties": {
          "id": {"type": "string", "description": "Query identifier for result mapping"},
          "query": {"type": "string", "description": "Search query"},
          "max_results": {"type": "integer", "default": 10},
          "date_filter": {"type": "string", "description": "e.g., 'before:2024-01-01'"},
          "category": {"type": "string", "description": "e.g., 'cs.LG', 'cs.CL'"}
        }
      }
    },
    "dedup": {
      "type": "boolean",
      "default": true,
      "description": "Deduplicate similar queries"
    },
    "use_cache": {
      "type": "boolean",
      "default": true,
      "description": "Check cache for recent identical queries"
    },
    "cache_ttl_hours": {
      "type": "integer",
      "default": 24,
      "description": "Cache time-to-live in hours"
    }
  }
}
```

### Example Input

```json
{
  "queries": [
    {"id": "q1", "query": "transformer attention mechanism", "max_results": 10},
    {"id": "q2", "query": "attention mechanism transformer", "max_results": 10},
    {"id": "q3", "query": "efficient attention linear complexity", "max_results": 10, "category": "cs.LG"}
  ],
  "dedup": true,
  "use_cache": true
}
```

## Output Specification

```json
{
  "type": "object",
  "required": ["results", "stats"],
  "properties": {
    "results": {
      "type": "object",
      "description": "Map from query ID to results",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "papers": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "arxiv_id": {"type": "string"},
                "title": {"type": "string"},
                "authors": {"type": "string"},
                "abstract": {"type": "string"},
                "published": {"type": "string"},
                "categories": {"type": "array", "items": {"type": "string"}}
              }
            }
          },
          "total_found": {"type": "integer"},
          "returned": {"type": "integer"},
          "from_cache": {"type": "boolean"},
          "deduplicated_to": {"type": "string", "description": "If deduped, which query it merged with"}
        }
      }
    },
    "stats": {
      "type": "object",
      "properties": {
        "queries_submitted": {"type": "integer"},
        "queries_deduplicated": {"type": "integer"},
        "queries_cached": {"type": "integer"},
        "queries_executed": {"type": "integer"},
        "total_papers_found": {"type": "integer"},
        "unique_papers": {"type": "integer"},
        "execution_time_ms": {"type": "integer"}
      }
    }
  }
}
```

### Example Output

```json
{
  "results": {
    "q1": {
      "papers": [
        {
          "arxiv_id": "1706.03762",
          "title": "Attention Is All You Need",
          "authors": "Vaswani et al.",
          "published": "2017-06-12"
        }
      ],
      "total_found": 1500,
      "returned": 10,
      "from_cache": false
    },
    "q2": {
      "papers": [],
      "total_found": 0,
      "returned": 0,
      "from_cache": false,
      "deduplicated_to": "q1"
    },
    "q3": {
      "papers": [...],
      "total_found": 245,
      "returned": 10,
      "from_cache": true
    }
  },
  "stats": {
    "queries_submitted": 3,
    "queries_deduplicated": 1,
    "queries_cached": 1,
    "queries_executed": 1,
    "total_papers_found": 1745,
    "unique_papers": 18,
    "execution_time_ms": 1200
  }
}
```

## Algorithm

1. **Query Normalization**
   - Lowercase and strip whitespace
   - Sort words alphabetically for comparison
   - Generate query hash

2. **Deduplication**
   - Compare normalized queries
   - Merge queries with >80% word overlap
   - Map deduplicated queries to primary

3. **Cache Check**
   - Compute cache key: `SHA256(normalized_query + date_filter + category)`
   - Check `.research-cache/arxiv/` for valid cache entry
   - If found and not expired, use cached results

4. **Batch Execution**
   - Queue remaining queries
   - Execute with rate limiting (max 3/sec, 1 sec between batches)
   - Handle 429 errors with exponential backoff

5. **Result Merging**
   - Collect all papers
   - Deduplicate by arxiv_id
   - Map results back to original query IDs

6. **Cache Update**
   - Store results with timestamp
   - Prune expired entries

## MCP Tool Usage

```
# Execute search
mcp__arxiv__search_papers(
  query="transformer attention mechanism",
  category="cs.LG",
  maxResults=10,
  sortBy="relevance"
)
```

## Deduplication Logic

```python
def is_similar_query(q1, q2, threshold=0.8):
    """Check if two queries are similar enough to deduplicate."""
    words1 = set(normalize(q1).split())
    words2 = set(normalize(q2).split())

    intersection = len(words1 & words2)
    union = len(words1 | words2)

    return intersection / union >= threshold if union > 0 else False
```

## Rate Limiting

| Scenario | Strategy |
|----------|----------|
| Normal | 3 requests per second |
| 429 received | Wait 5s, then 10s, then 30s |
| 5 consecutive 429s | Abort, return partial results |

## Caching

### Cache Structure

```
.research-cache/
└── arxiv/
    ├── index.json          # Cache index with timestamps
    └── queries/
        ├── abc123.json     # Cached query result
        └── def456.json
```

### Cache Entry Format

```json
{
  "query_hash": "abc123",
  "query": "transformer attention mechanism",
  "date_filter": "before:2024-01-01",
  "category": "cs.LG",
  "cached_at": "2025-01-29T10:00:00Z",
  "expires_at": "2025-01-30T10:00:00Z",
  "results": [...]
}
```

## Error Handling

| Error | Response |
|-------|----------|
| API unavailable | Retry 3x with backoff, then fail |
| Rate limited | Backoff and retry |
| Invalid query | Skip, note in results |
| Cache corrupted | Clear cache, execute fresh |

## Constraints

- **DO**: Respect arXiv API rate limits
- **DO**: Cache results for efficiency
- **DO**: Deduplicate queries and results
- **DON'T**: Execute more than 50 queries per batch
- **DON'T**: Store cache longer than 7 days

## Integration Notes

### Called By
- `novelty-checker` micro-skill
- `parallel-audit` orchestrator

### Calls
- `mcp__arxiv__search_papers`
- Local file system for caching

### State Updates
- Manages `.research-cache/arxiv/` directory
