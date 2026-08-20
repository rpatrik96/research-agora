---
name: citation-verifier
description: |
  Verify citation accuracy against arXiv and other sources. Checks that cited
  papers exist, author names are correct, and claims about cited work are accurate.
  Trigger: "verify citation", "check reference accuracy".
model: haiku
color: gray
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: verification
  verification-level: formal
  visibility: internal
---

# Micro-Skill: Citation Verifier

> **Hybrid**: Citation lookup uses API/MCP tools. LLM verifies semantic accuracy of citations in context.

> **One-line description**: Verify that citations are accurate and claims about cited work are faithful representations.

## Purpose

This skill verifies citation accuracy by checking: (1) the cited paper exists, (2) author names and year are correct, (3) claims about the cited work accurately represent its content. This prevents common citation errors like misciting, phantom citations, and misrepresentation.

## Parallelization Properties

| Property | Value |
|----------|-------|
| **Input scope** | Single citation |
| **State requirements** | Stateless |
| **External calls** | arXiv MCP tools |
| **Typical runtime** | 10-30s |
| **Can run in parallel** | Yes (rate-limited) |

## Input Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["citation"],
  "properties": {
    "citation": {
      "type": "object",
      "required": ["key"],
      "properties": {
        "key": {"type": "string", "description": "Citation key (e.g., 'vaswani2017attention')"},
        "title": {"type": "string"},
        "authors": {"type": "string"},
        "year": {"type": "integer"},
        "venue": {"type": "string"},
        "arxiv_id": {"type": "string"}
      }
    },
    "claim_about_citation": {
      "type": "string",
      "description": "What the paper claims about this citation (optional)"
    },
    "context_sentence": {
      "type": "string",
      "description": "Sentence where citation appears"
    }
  }
}
```

### Example Input

```json
{
  "citation": {
    "key": "vaswani2017attention",
    "title": "Attention Is All You Need",
    "authors": "Vaswani et al.",
    "year": 2017,
    "arxiv_id": "1706.03762"
  },
  "claim_about_citation": "The Transformer architecture was introduced by Vaswani et al. (2017), which achieved state-of-the-art results on machine translation.",
  "context_sentence": "Building on the Transformer architecture [vaswani2017attention], we propose..."
}
```

## Output Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["citation_key", "verification_status"],
  "properties": {
    "citation_key": {"type": "string"},
    "verification_status": {
      "type": "string",
      "enum": ["verified", "minor_issues", "major_issues", "not_found"]
    },
    "paper_found": {"type": "boolean"},
    "metadata_accuracy": {
      "type": "object",
      "properties": {
        "title_match": {"type": "boolean"},
        "authors_match": {"type": "boolean"},
        "year_match": {"type": "boolean"},
        "venue_match": {"type": "boolean"}
      }
    },
    "actual_metadata": {
      "type": "object",
      "description": "Correct metadata from source"
    },
    "claim_accuracy": {
      "type": "string",
      "enum": ["accurate", "partially_accurate", "inaccurate", "not_assessed"]
    },
    "claim_issues": {
      "type": "array",
      "items": {"type": "string"}
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
  "citation_key": "vaswani2017attention",
  "verification_status": "verified",
  "paper_found": true,
  "metadata_accuracy": {
    "title_match": true,
    "authors_match": true,
    "year_match": true,
    "venue_match": true
  },
  "actual_metadata": {
    "title": "Attention Is All You Need",
    "authors": "Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, Illia Polosukhin",
    "year": 2017,
    "venue": "NeurIPS",
    "arxiv_id": "1706.03762"
  },
  "claim_accuracy": "accurate",
  "claim_issues": [],
  "recommendations": []
}
```

## Algorithm

1. **Locate paper**
   - If arxiv_id provided: Use `mcp__arxiv__get_paper_by_id`
   - If title provided: Search via `mcp__arxiv__search_papers`
   - If only key: Parse key for author/year, search

2. **Verify metadata**
   - Compare title (fuzzy match, ignore case/punctuation)
   - Compare authors (first author match is sufficient)
   - Compare year (exact match)
   - Compare venue (if provided)

3. **Assess claim accuracy** (if claim_about_citation provided)
   - Read abstract of cited paper
   - Check if claim accurately represents paper's contribution
   - Flag misrepresentations

4. **Generate recommendations**
   - Correct any metadata errors
   - Suggest claim revisions if inaccurate
   - Note if paper is retracted/superseded

## Verification Criteria

### Metadata Matching

| Field | Match Criteria | Tolerance |
|-------|----------------|-----------|
| Title | Fuzzy match | Ignore punctuation, case |
| Authors | First author matches | Allow "et al." |
| Year | Exact match | None |
| Venue | Contains or abbreviation | Allow NeurIPS/NIPS |

### Claim Accuracy Assessment

| Accuracy Level | Criteria |
|----------------|----------|
| **accurate** | Claim faithfully represents cited work |
| **partially_accurate** | Generally correct but imprecise or incomplete |
| **inaccurate** | Misrepresents cited work's findings or scope |

### Common Claim Issues

| Issue | Example | Detection |
|-------|---------|-----------|
| **Overgeneralization** | "X solves problem" vs "X improves on problem" | Absolute language |
| **Misattribution** | Crediting wrong paper for contribution | Abstract mismatch |
| **Phantom citation** | Paper doesn't support claim | Claim not in abstract |
| **Outdated claim** | Paper has been updated/superseded | Check versions |

## MCP Tool Usage

```
# Get paper by arXiv ID
mcp__arxiv__get_paper_by_id(
  ids=["1706.03762"]
)

# Search by title
mcp__arxiv__search_papers(
  title="Attention Is All You Need",
  maxResults=5
)

# Search by author
mcp__arxiv__search_author(
  author="Vaswani",
  maxResults=10
)
```

## Constraints

- **DO**: Verify all metadata fields available
- **DO**: Check claim accuracy when claim text provided
- **DO**: Note version discrepancies (v1 vs v2)
- **DON'T**: Read full paper (abstract only)
- **DON'T**: Verify claims not explicitly made
- **DON'T**: Search beyond arXiv

## Error Handling

| Error Condition | Response |
|-----------------|----------|
| Paper not found on arXiv | `verification_status: "not_found"`, note non-arXiv papers exist |
| Multiple papers match | Return best match, note ambiguity |
| ArXiv API unavailable | `{"error": "ArXiv API unavailable", "code": "API_ERROR"}` |
| No metadata to verify | Skip metadata check, focus on existence |

## Context Requirements

| Context Item | Required | Source |
|--------------|----------|--------|
| Citation | Yes | Direct input |
| claim_about_citation | No | Improves verification |
| arxiv_id | No | Speeds up lookup |

## Examples

### Example 1: Metadata Error

**Input**:
```json
{
  "citation": {
    "key": "devlin2018bert",
    "title": "BERT: Pre-training of Deep Bidirectional Transformers",
    "authors": "Devlin et al.",
    "year": 2018,
    "arxiv_id": "1810.04805"
  }
}
```

**Output**:
```json
{
  "citation_key": "devlin2018bert",
  "verification_status": "minor_issues",
  "paper_found": true,
  "metadata_accuracy": {
    "title_match": false,
    "authors_match": true,
    "year_match": true,
    "venue_match": true
  },
  "actual_metadata": {
    "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
    "authors": "Jacob Devlin, Ming-Wei Chang, Kenton Lee, Kristina Toutanova",
    "year": 2018,
    "venue": "NAACL",
    "arxiv_id": "1810.04805"
  },
  "claim_accuracy": "not_assessed",
  "claim_issues": [],
  "recommendations": [
    "Title is truncated. Full title: 'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding'"
  ]
}
```

### Example 2: Inaccurate Claim

**Input**:
```json
{
  "citation": {
    "key": "brown2020gpt3",
    "title": "Language Models are Few-Shot Learners",
    "authors": "Brown et al.",
    "year": 2020,
    "arxiv_id": "2005.14165"
  },
  "claim_about_citation": "GPT-3 was fine-tuned on downstream tasks to achieve strong performance."
}
```

**Output**:
```json
{
  "citation_key": "brown2020gpt3",
  "verification_status": "major_issues",
  "paper_found": true,
  "metadata_accuracy": {
    "title_match": true,
    "authors_match": true,
    "year_match": true,
    "venue_match": true
  },
  "actual_metadata": {
    "title": "Language Models are Few-Shot Learners",
    "authors": "Tom Brown et al.",
    "year": 2020,
    "venue": "NeurIPS",
    "arxiv_id": "2005.14165"
  },
  "claim_accuracy": "inaccurate",
  "claim_issues": [
    "GPT-3's key contribution is few-shot learning WITHOUT fine-tuning",
    "The paper explicitly demonstrates task performance with only in-context examples",
    "Claiming 'fine-tuned' misrepresents the paper's core contribution"
  ],
  "recommendations": [
    "Revise to: 'GPT-3 achieved strong performance using in-context learning without fine-tuning'",
    "Or: 'GPT-3 demonstrated that large language models can perform tasks with few-shot prompting'"
  ]
}
```

### Example 3: Paper Not Found

**Input**:
```json
{
  "citation": {
    "key": "smith2019unknown",
    "title": "A Novel Approach to Everything",
    "authors": "Smith et al.",
    "year": 2019
  }
}
```

**Output**:
```json
{
  "citation_key": "smith2019unknown",
  "verification_status": "not_found",
  "paper_found": false,
  "metadata_accuracy": {
    "title_match": false,
    "authors_match": false,
    "year_match": false
  },
  "actual_metadata": null,
  "claim_accuracy": "not_assessed",
  "claim_issues": [],
  "recommendations": [
    "Paper not found on arXiv. Possible issues:",
    "- Paper may not be on arXiv (check ACM DL, IEEE, journal site)",
    "- Title or author name may be incorrect",
    "- Paper may be unpublished or retracted",
    "Verify citation manually or provide DOI/URL"
  ]
}
```

## Integration Notes

### Called By
- `parallel-audit` orchestrator (for bibliography verification)
- Can be called directly for citation checking

### Calls
- `mcp__arxiv__get_paper_by_id`
- `mcp__arxiv__search_papers`
- `mcp__arxiv__search_author`

### State Updates
- Updates citation entries in research-state.json with verified metadata
- Flags inaccurate claims for review
