---
name: literature-synthesizer
description: |
  Discover relevant literature for ML papers and build a verified bibliography. Use when asked to
  "find related work", "literature review", "survey the field", "find papers on [topic]",
  "build bibliography", "survey prior work", or "what papers should I cite". Runs multi-query
  arXiv searches, deduplicates programmatically, and puts every paper through an approval gate
  before it reaches your .bib. It finds and verifies papers; it does not write the prose.
model: sonnet
disable-model-invocation: true
metadata:
  research-domain: general
  research-phase: literature-review
  task-type: analysis
  verification-level: layered
---

# Literature Discovery

Multi-query literature discovery with a paper approval gate and a verified bibliography at the end. Supports guided mode (you name the papers) and autonomous mode (the skill searches and you approve).

> **Hybrid**: Paper discovery uses MCP tools (arXiv API) as structured searches - always execute these first. Deduplication is done programmatically. LLM is used for query generation and relevance ranking only.

**This skill does not write your related work section.** Positioning a paper against its field is an argument about what matters and why, and it is the argument reviewers read most closely — so the prose stays yours. What the skill gives you is the part a search engine does better than memory: real papers, deduplicated, each one confirmed to exist, with BibTeX that resolves. Run `/paper-review` on the section once you have written it.

## Workflow

1. **LLM: Generate search strategy** - Create 5-10 diverse search queries from paper context
2. **MCP: Execute parallel searches** - Run all queries via arXiv MCP tools
3. **Script: Deduplicate** - Remove duplicates by arXiv ID programmatically
4. **LLM: Rank and organize** - Assess relevance, organize by theme
5. **Present for approval**: Show top 30-50 papers organized by theme
6. **Generate BibTeX** - Emit entries for the approved papers, then verify every one via `paper-references` before handing them over

## Before Starting

Gather the following information:
- Paper draft (especially abstract, introduction, method description)
- Any papers already cited or known to be relevant
- Target venue (NeurIPS, ICML, ICLR) for formatting conventions
- Preferred related work length (typically 1-2 pages)

## Search Strategy Generation

### Query Categories

For a paper about [method] solving [problem] in [domain], generate queries for:

| Category | Query Pattern | Example |
|----------|---------------|---------|
| **Direct topic** | "[method] [domain]" | "contrastive learning vision" |
| **Problem focus** | "[problem] [approach]" | "representation learning self-supervised" |
| **Alternative methods** | "[problem] [other method]" | "visual representations generative" |
| **Foundational** | "[base technique] survey" | "self-supervised learning survey" |
| **Recent advances** | "[topic]" + sortBy=lastUpdatedDate | Latest in cs.LG/cs.CV |
| **Key authors** | Author search for leaders | "Yann LeCun", "Yoshua Bengio" |
| **Application domain** | "[application] [method type]" | "medical imaging contrastive" |

### Search Execution

Use these MCP tools in sequence:

```
# 1. Topic searches (run in parallel for speed)
mcp__arxiv__search_papers(query="[query1]", maxResults=20, sortBy="relevance")
mcp__arxiv__search_papers(query="[query2]", maxResults=20, sortBy="relevance")
...

# 2. Recent papers in relevant categories
mcp__arxiv__get_recent_papers(category="cs.LG", maxResults=30)
mcp__arxiv__get_recent_papers(category="cs.CV", maxResults=30)

# 3. Author searches for known leaders
mcp__arxiv__search_author(author="[known author]", maxResults=10)

# 4. Fetch details for any specific arXiv IDs mentioned
mcp__arxiv__get_paper_by_id(ids=["2301.00001", ...])
```

## Paper Presentation Format

After collecting papers, present them organized by theme:

```markdown
## Literature Discovery Results

### Search Summary
- Query: "contrastive learning representations" -> 18 results
- Query: "self-supervised visual learning" -> 22 results
- Recent cs.LG papers -> 30 results
- Author: Kaiming He -> 8 results
- **Total unique papers found: 67**
- **After relevance filtering: 42**

---

### Category 1: Contrastive Learning Methods

1. **SimCLR: A Simple Framework for Contrastive Learning** (arXiv:2002.05709)
   Chen, Kornblith, Norouzi, Hinton (2020)
   *Summary*: Introduces simple contrastive framework with data augmentation
   *Relevance*: Direct comparison - uses similar augmentation strategy
   *Citations*: 8000+

2. **MoCo: Momentum Contrast for Unsupervised Visual Representation Learning** (arXiv:1911.05722)
   He, Fan, Wu, Xie, Girshick (2019)
   *Summary*: Memory bank approach for contrastive learning
   *Relevance*: Alternative architecture to compare against
   *Citations*: 5000+

[Continue for all papers...]

---

### Category 2: Self-Supervised Learning Theory
[Papers in this category...]

### Category 3: Applications in [Domain]
[Papers in this category...]

---

## Approval Checklist

Please review and indicate which papers to include:

- [ ] Paper 1: SimCLR (arXiv:2002.05709)
- [ ] Paper 2: MoCo (arXiv:1911.05722)
- [ ] Paper 3: ...

### Additional Requests
- Are there specific papers I should search for? (provide arXiv IDs or titles)
- Any topics or authors I should explore further?
- Papers to definitely exclude?
```

## BibTeX Generation

Generate entries for all approved papers:

```bibtex
@inproceedings{chen2020simclr,
  title={A Simple Framework for Contrastive Learning of Visual Representations},
  author={Chen, Ting and Kornblith, Simon and Norouzi, Mohammad and Hinton, Geoffrey},
  booktitle={International Conference on Machine Learning},
  pages={1597--1607},
  year={2020},
  organization={PMLR}
}

@inproceedings{he2020moco,
  title={Momentum Contrast for Unsupervised Visual Representation Learning},
  author={He, Kaiming and Fan, Haoqi and Wu, Yuxin and Xie, Saining and Girshick, Ross},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition},
  pages={9729--9738},
  year={2020}
}
```

### BibTeX Best Practices

- Key format: `author2020keyword` (lowercase)
- Prefer published versions over arXiv preprints
- Include DOI when available
- Use consistent venue abbreviations

## MCP Integration

### Required MCPs

| MCP | Tools Used | Purpose |
|-----|------------|---------|
| **arxiv** | search_papers, get_paper_by_id, search_author, get_recent_papers | Paper discovery |
| **zotero** (optional) | search, add_item | Check existing library, add new entries |

### Tool Usage Patterns

```python
# Parallel topic searches
results = [
    mcp__arxiv__search_papers(query=q, maxResults=20, sortBy="relevance")
    for q in queries
]

# Deduplication by arXiv ID
seen_ids = set()
unique_papers = []
for paper in all_results:
    if paper.id not in seen_ids:
        seen_ids.add(paper.id)
        unique_papers.append(paper)

# Relevance ranking (conceptual)
# - Keyword match score
# - Citation count (if available)
# - Recency bonus for last 2 years
```

## Output Deliverables

1. **Search Summary**: Queries run, result counts, filtering stats
2. **Paper Catalog**: All discovered papers organized by theme
3. **Approval Checklist**: Interactive list for user selection
4. **BibTeX Entries**: Complete bibliography entries, each verified via `paper-references`
5. **Coverage Analysis**: Topics well-covered vs. gaps

## Verification Checklist

Before finalizing:

- [ ] All approved papers have BibTeX entries
- [ ] Mix of seminal and recent works
- [ ] Citation style matches venue requirements
- [ ] **`paper-references` run over the generated entries, and every entry resolves**
- [ ] All arXiv IDs verified as valid
- [ ] No hallucinated paper titles or authors

## Common Issues

| Issue | Solution |
|-------|----------|
| Too many results | Increase relevance threshold, focus on high-citation papers |
| Missing seminal work | Add explicit searches for "survey", "tutorial", author searches |
| Duplicate papers | Deduplicate by arXiv ID before presentation |
| Outdated coverage | Add recent papers query with date sorting |
| Missing domain papers | Add domain-specific category searches |

## Skill Dependencies

This skill **must** invoke before returning:
- `paper-references` - Verifies every generated entry against arXiv, Crossref, DBLP and Semantic Scholar. A bibliography this skill has not put through that check is not a deliverable, because "the search returned it" is not the same claim as "the paper exists as cited".
