---
name: paper-references
description: Fact-check references in ML paper drafts. Use when asked to "verify citations", "check references", "fact-check bibliography", "validate citations", or "audit references". Verifies papers exist on arXiv, checks author names, years, and titles against actual publications.
model: sonnet
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: verification
  verification-level: formal
---

# Reference Fact-Checking

> **Script-first**: This skill uses `bibtexupdater` CLI tool for automated reference verification. LLM is used only as fallback for entries the tool cannot resolve.

Verify the accuracy of citations in ML conference papers by cross-referencing against arXiv, Crossref, DBLP, and Semantic Scholar. Identifies errors, hallucinated references, missing fields, and outdated preprints.

## Tools

### Primary: bibtexupdater

Install from PyPI: `pip install bibtex-updater` (source: https://github.com/rpatrik96/bibtexupdater)

Three complementary commands:
1. **bibtexupdater** - Upgrade preprints to published versions, verify/fill fields
2. **bibtexupdater-filter** - Filter .bib to only cited references
3. **bibtexupdater-zotero** - Update Zotero library preprints

### Secondary: arXiv MCP

For manual verification when bibtexupdater needs human judgment:
```
mcp__arxiv__search_papers - Search by title/author
mcp__arxiv__get_paper_by_id - Verify known arXiv IDs
mcp__arxiv__search_author - Verify author publications
```

## Workflow

1. **Filter citations**: Keep only cited references
2. **Dry-run verification**: Preview what bibtexupdater would change
3. **Review changes**: Manually verify flagged items with arXiv MCP
4. **Apply fixes**: Run bibtexupdater to auto-fix, manually fix remainder
5. **Generate report**: Document verification results

### Workflow Operationalization
1. Use bibtexupdater for bulk automated verification
2. Spawn subagents (haiku) for parallel manual verification of flagged items
3. Use arXiv MCP for papers bibtexupdater couldn't resolve

## Step 1: Filter Bibliography

Keep only references actually cited in the paper:

```bash
cd /path/to/paper

# List all citations found in LaTeX
bibtexupdater-filter *.tex -b references.bib --list-citations

# Create filtered bibliography (dry-run first)
bibtexupdater-filter *.tex -b references.bib -o refs_filtered.bib --dry-run

# Apply filter
bibtexupdater-filter *.tex -b references.bib -o refs_filtered.bib
```

For multi-file projects:
```bash
# Recursive search in chapters directory
bibtexupdater-filter ./chapters/ -b refs.bib -o filtered.bib -r

# Multiple bib files merged
bibtexupdater-filter *.tex -b refs1.bib refs2.bib -o merged_filtered.bib
```

## Step 2: Verify & Upgrade References

### Dry-Run Verification

Always preview changes first:

```bash
bibtexupdater references.bib \
    --dry-run \
    --verbose \
    --report changes.jsonl \
    --check-fields \
    --field-report field_status.json
```

This will:
- Detect preprints (arXiv, bioRxiv, medRxiv)
- Search for published versions via Crossref, DBLP, Semantic Scholar
- Check for missing required/recommended fields
- Generate detailed reports without modifying files

### Understanding the Output

**Console output:**
```
INFO: Summary: total=50, detected_preprints=15, upgraded=12, unchanged=35, failures=3
INFO: Failed to find published versions for 3 preprint(s):
  - [paper_key] Some preprint title... (No reliable published match found)
```

**JSONL report (changes.jsonl):**
```json
{
  "file": "references.bib",
  "key_old": "kingma2014adam",
  "key_new": "kingma2014adam",
  "action": "upgraded",
  "method": "SemanticScholar(arXiv)",
  "confidence": 0.95,
  "title_old": "Adam: A Method for Stochastic Optimization",
  "title_new": "Adam: A Method for Stochastic Optimization"
}
```

**Actions:** `upgraded`, `unchanged`, `failed`, `field_filled`, `skipped`

**Field report (field_status.json):**
```json
{
  "total": 50,
  "complete": 35,
  "filled": 10,
  "partial": 4,
  "unfillable": 1,
  "field_statistics": {
    "volume": {"total_missing": 8, "filled": 5, "still_missing": 3},
    "pages": {"total_missing": 6, "filled": 3, "still_missing": 3}
  }
}
```

### Apply Changes

After reviewing dry-run output:

```bash
# Output to new file (safest)
bibtexupdater references.bib \
    -o references_updated.bib \
    --verbose \
    --keep-preprint-note \
    --fill-fields \
    --field-fill-mode recommended

# Or edit in-place
bibtexupdater references.bib \
    --in-place \
    --keep-preprint-note
```

### Key Options

| Option | Purpose |
|--------|---------|
| `--dry-run` | Preview changes without writing |
| `--verbose` | Detailed logging |
| `--report FILE` | JSONL report of all changes |
| `--keep-preprint-note` | Preserve arXiv ID in note field |
| `--check-fields` | Report missing fields |
| `--fill-fields` | Auto-fill missing fields from APIs |
| `--field-fill-mode {required,recommended,all}` | Which fields to fill |
| `--dedupe` | Merge duplicate entries |
| `--rekey` | Regenerate citation keys as authorYearTitle |
| `--use-scholarly` | Enable Google Scholar fallback |

## Step 3: Manual Verification of Failures

For entries bibtexupdater couldn't resolve, use arXiv MCP:

```python
# Verify by title
mcp__arxiv__search_papers(title="Attention Is All You Need", maxResults=5)

# Verify specific arXiv ID
mcp__arxiv__get_paper_by_id(ids=["1706.03762"])

# Search by author
mcp__arxiv__search_author(author="Vaswani, Ashish", maxResults=20)
```

### Verification Categories

| Status | Meaning | Action |
|--------|---------|--------|
| **VERIFIED** | Paper found, metadata matches | None |
| **UPGRADED** | Preprint upgraded to published | Review change |
| **MINOR ISSUE** | Small discrepancies | Review, likely accept |
| **MAJOR ISSUE** | Significant mismatches | Manual fix required |
| **NOT FOUND** | Cannot locate paper | Potential hallucination - investigate |
| **AMBIGUOUS** | Multiple matches | Manual disambiguation |

## Common Error Patterns

### Preprints That Should Be Published
```bibtex
% bibtexupdater will auto-fix this
@article{vaswani2017attention,
  title={Attention Is All You Need},
  journal={arXiv preprint arXiv:1706.03762},  % Should be NeurIPS 2017
  year={2017}
}
```

### Hallucinated References
Signs to check manually:
- bibtexupdater returns `action: failed` with "No reliable published match found"
- Author combinations that never collaborated
- Title sounds plausible but yields no results
- arXiv ID format correct but doesn't exist

### Missing Fields
```bibtex
% --check-fields will flag this
@inproceedings{chen2020simclr,
  title={A Simple Framework for Contrastive Learning},
  author={Chen, Ting and Kornblith, Simon and Norouzi, Mohammad and Hinton, Geoffrey},
  year={2020}
  % Missing: booktitle, pages, publisher
}
```

### Author Errors
```bibtex
% Manual check needed - bibtexupdater verifies but may not catch all
@article{chen2020simclr,
  author={Chen, Ting and Kornblith, Simon and Noruzi, Mohammad},  % Norouzi, not Noruzi
}
```

## Verification Report Format

After running bibtexupdater + manual verification:

```markdown
## Reference Verification Report

**Paper**: [Paper title]
**Total citations**: [N]
**Auto-verified**: [N] | **Manual verified**: [N] | **Issues**: [N]

---

### bibtexupdater Results

| Metric | Count |
|--------|-------|
| Total processed | 50 |
| Preprints detected | 15 |
| Successfully upgraded | 12 |
| Fields filled | 8 |
| Failed to resolve | 3 |

---

### Entries Requiring Manual Review

#### [citation_key] - FAILED
**Reason**: No reliable published match found
**Current entry**:
```bibtex
@misc{...}
```

**arXiv MCP search results**:
- [Search result 1]
- [Search result 2]

**Recommendation**: [Keep as preprint / Replace with X / Remove - potential hallucination]

---

### Summary Statistics

| Category | Count | Percentage |
|----------|-------|------------|
| Auto-verified | [N] | [%] |
| Upgraded to published | [N] | [%] |
| Manual verified | [N] | [%] |
| Issues found | [N] | [%] |
| Potential hallucinations | [N] | [%] |

---

### Action Items

#### Critical (Paper Integrity)
- [ ] Investigate potential hallucination: [key]
- [ ] Fix author misspelling: [key]

#### Recommended (Accuracy)
- [ ] Update year for published version: [key]
- [ ] Add missing venue: [key]

#### Optional (Polish)
- [ ] Fill missing page numbers
- [ ] Standardize key format with --rekey
```

## Zotero Integration

If managing references in Zotero:

```bash
# Set credentials
export ZOTERO_LIBRARY_ID="your_user_id"
export ZOTERO_API_KEY="your_api_key"

# Preview updates
bibtexupdater-zotero --dry-run --verbose

# Update specific collection
bibtexupdater-zotero --collection ABCD1234

# Update items with specific tag
bibtexupdater-zotero --tag "to-update"
```

## API Sources Used

bibtexupdater queries these sources in order:

1. **arXiv API** - Extract DOI from arXiv metadata
2. **Crossref** - DOI lookup, bibliographic search
3. **DBLP** - Title + author search (good for CS venues)
4. **Semantic Scholar** - Direct arXiv lookup, general search
5. **Google Scholar** (optional) - Fallback with `--use-scholarly`

Matching uses fuzzy title matching (≥90% similarity) + author Jaccard similarity.

## Quality Metrics

After verification, assess:

1. **Verification rate**: % auto-verified by bibtexupdater
2. **Upgrade rate**: % preprints upgraded to published
3. **Field completeness**: % entries with all required fields
4. **Risk assessment**: High/Medium/Low based on unverified count
5. **Hallucination risk**: Count of NOT FOUND entries

## Quick Reference

```bash
# Full verification workflow
cd /path/to/paper

# 1. Filter to cited references only
bibtexupdater-filter *.tex -b refs.bib -o refs_cited.bib

# 2. Dry-run verification
bibtexupdater refs_cited.bib \
    --dry-run --verbose --report verify.jsonl --check-fields

# 3. Review verify.jsonl, then apply
bibtexupdater refs_cited.bib \
    -o refs_verified.bib --keep-preprint-note --fill-fields

# 4. Manually verify failures using arXiv MCP
```
