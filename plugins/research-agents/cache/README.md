# Research Agents Cache System

> Last Updated: 2026-01-29
> Version: 1.0.0

This document describes the caching infrastructure for the research-agents plugin, enabling efficient data reuse across agent operations.

## Overview

The cache system provides persistent storage for:
- arXiv query results (paper metadata, search results)
- Research state snapshots (paper analysis, evidence tracking)
- Agent intermediate results (synthesis outputs, validation states)

## Cache Directory Structure

```
.research-cache/
├── arxiv/                    # arXiv API response cache
│   ├── queries/              # Search query results
│   │   └── {query_hash}.json
│   └── papers/               # Individual paper metadata
│       └── {arxiv_id}.json
├── state/                    # Research state cache
│   ├── papers/               # Paper analysis state
│   │   └── {paper_hash}.json
│   └── sessions/             # Session-level state
│       └── {session_id}.json
├── agents/                   # Agent-specific cache
│   ├── evidence/             # Evidence checker results
│   │   └── {content_hash}.json
│   ├── synthesis/            # Perspective synthesizer results
│   │   └── {input_hash}.json
│   └── validation/           # Statistical validator results
│       └── {data_hash}.json
└── index.json                # Cache index with metadata
```

## Cache File Naming Conventions

### Hash-Based Keys
- **Query hash**: SHA-256 of normalized query string (lowercase, sorted params)
- **Paper hash**: SHA-256 of paper content (abstract + sections used)
- **Content hash**: SHA-256 of input content being analyzed
- **Session ID**: UUID v4 generated per research session

### File Format
All cache files are JSON with metadata envelope:
```json
{
  "version": "1.0.0",
  "created_at": "2026-01-29T10:30:00Z",
  "expires_at": "2026-01-30T10:30:00Z",
  "ttl_seconds": 86400,
  "cache_key": "sha256:abc123...",
  "data_type": "arxiv_query|paper_state|agent_result",
  "data": { ... }
}
```

### Naming Examples
| Type | Pattern | Example |
|------|---------|---------|
| arXiv query | `{sha256_first16}.json` | `a1b2c3d4e5f67890.json` |
| arXiv paper | `{arxiv_id_safe}.json` | `2401.12345v2.json` |
| Paper state | `{sha256_first16}.json` | `f0e1d2c3b4a59687.json` |
| Session | `{uuid}.json` | `550e8400-e29b-41d4-a716-446655440000.json` |

## TTL Policies

### Time-Based Expiration

| Cache Type | Default TTL | Rationale |
|------------|-------------|-----------|
| arXiv queries | 24 hours | Papers update daily, balance freshness vs. API limits |
| arXiv paper metadata | 7 days | Metadata rarely changes after publication |
| Research state | Hash-based | Invalidate when source content changes |
| Agent results | 1 hour | Short-lived for iterative workflows |
| Session state | 24 hours | Persist across work sessions |

### Hash-Based Expiration

For content-dependent caches (paper analysis, evidence checking):

1. **Compute content hash** from source material
2. **Compare with cached hash** in metadata
3. **Invalidate if mismatch** - source has changed

```python
# Example hash computation
import hashlib

def compute_paper_hash(abstract: str, sections: list[str]) -> str:
    content = abstract + "".join(sorted(sections))
    return hashlib.sha256(content.encode()).hexdigest()[:16]
```

## Cache Invalidation Triggers

### Automatic Invalidation

| Trigger | Action |
|---------|--------|
| TTL expired | Entry removed on next access |
| Content hash mismatch | Entry invalidated, fresh computation triggered |
| Cache version mismatch | All entries with old version cleared |
| Disk space threshold | LRU eviction of oldest entries |

### Manual Invalidation

```bash
# Clear all cache
python scripts/cache_manager.py clear --all

# Clear specific cache type
python scripts/cache_manager.py clear --type arxiv
python scripts/cache_manager.py clear --type state
python scripts/cache_manager.py clear --type agents

# Clear expired entries only
python scripts/cache_manager.py clear --expired

# Clear by age
python scripts/cache_manager.py clear --older-than 7d

# Clear specific entry
python scripts/cache_manager.py invalidate --key "sha256:a1b2c3d4..."
```

### Programmatic Invalidation

```python
from scripts.cache_manager import CacheManager

cache = CacheManager()

# Invalidate single entry
cache.invalidate("arxiv/queries/a1b2c3d4e5f67890")

# Invalidate by pattern
cache.invalidate_pattern("arxiv/papers/2401.*")

# Clear category
cache.clear_category("agents/evidence")

# Clear all
cache.clear_all()
```

## Integration Points

### batch-arxiv Integration

The batch-arxiv skill uses cache for:
- Query result caching (24h TTL)
- Paper metadata caching (7d TTL)
- Rate limit compliance via cached responses

```python
# In batch-arxiv workflow
cache = CacheManager()

# Check cache first
cached = cache.get_cached("arxiv/queries", query_hash)
if cached and not cached.is_expired():
    return cached.data

# Fetch fresh and cache
results = fetch_arxiv(query)
cache.set_cached("arxiv/queries", query_hash, results, ttl=86400)
```

### research-state Integration

Research state caching preserves:
- Paper analysis progress
- Evidence collection state
- Cross-reference mappings

```python
# In research-state workflow
cache = CacheManager()

# Save state with content hash
paper_hash = compute_paper_hash(paper_content)
cache.set_cached(
    "state/papers",
    paper_hash,
    analysis_state,
    ttl=None,  # Hash-based, no time expiry
    content_hash=paper_hash
)

# Retrieve state (validates hash)
state = cache.get_cached("state/papers", paper_hash, validate_hash=paper_content)
```

## Manual Cache Clearing Instructions

### Clear All Cache

```bash
# Remove entire cache directory
rm -rf .research-cache/

# Or use cache manager
python scripts/cache_manager.py clear --all
```

### Clear Specific Categories

```bash
# Clear arXiv cache only
rm -rf .research-cache/arxiv/

# Clear agent results only
rm -rf .research-cache/agents/

# Clear research state only
rm -rf .research-cache/state/
```

### Clear Expired Entries

```bash
# Safe cleanup - only removes expired entries
python scripts/cache_manager.py clear --expired

# Preview what would be cleared
python scripts/cache_manager.py clear --expired --dry-run
```

### Cache Statistics

```bash
# View cache statistics
python scripts/cache_manager.py stats

# Output example:
# Cache Statistics:
#   Total entries: 147
#   Total size: 2.3 MB
#   Expired entries: 23
#   By category:
#     arxiv/queries: 45 entries (890 KB)
#     arxiv/papers: 67 entries (1.1 MB)
#     state/papers: 12 entries (156 KB)
#     agents/*: 23 entries (154 KB)
```

## Configuration

Cache behavior can be configured via environment variables or config file:

### Environment Variables

```bash
export RESEARCH_CACHE_DIR=".research-cache"
export RESEARCH_CACHE_MAX_SIZE_MB="100"
export RESEARCH_CACHE_ARXIV_TTL="86400"
export RESEARCH_CACHE_STATE_TTL="0"  # 0 = hash-based only
export RESEARCH_CACHE_AGENT_TTL="3600"
```

### Config File (.research-cache/config.json)

```json
{
  "version": "1.0.0",
  "max_size_mb": 100,
  "ttl_defaults": {
    "arxiv_queries": 86400,
    "arxiv_papers": 604800,
    "state": 0,
    "agents": 3600
  },
  "auto_cleanup": true,
  "cleanup_threshold_percent": 90
}
```

## Best Practices

1. **Always use cache manager** - Don't manipulate cache files directly
2. **Prefer hash-based keys** - For content that may change
3. **Set appropriate TTLs** - Balance freshness vs. performance
4. **Monitor cache size** - Run periodic cleanup in long sessions
5. **Clear before releases** - Ensure reproducibility with fresh cache
