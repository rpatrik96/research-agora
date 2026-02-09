---
name: paper-literature
description: Write literature review and related work sections for ML papers. Use when asked to "write related work", "literature review", "find related papers", "survey prior work", or "position the paper". Searches arXiv for relevant papers and synthesizes them into a coherent narrative.
model: sonnet
metadata:
  research-domain: general
  research-phase: literature-review
  task-type: writing
  verification-level: layered
---

# Literature Review & Related Work

> **LLM-required**: Writing related work sections requires synthesis of multiple papers into a coherent narrative. No script alternative.

Generate comprehensive related work sections for ML conference papers (NeurIPS, ICML, ICLR) with arXiv-powered paper discovery.

## Workflow

1. **Understand the paper**: Read the draft to identify key concepts, methods, and claims
2. **Identify search terms**: Extract keywords for literature search
3. **Search arXiv**: Use the arXiv MCP tools to find relevant papers
4. **Present candidates**: Show found papers for user approval before including
5. **Synthesize**: Write a structured related work section
6. **Generate BibTeX**: Provide entries for all cited papers

## ArXiv Search Strategy

Use these MCP tools for paper discovery:

```
mcp__arxiv__search_papers - Search by keywords, author, category
mcp__arxiv__get_recent_papers - Find latest work in a category
mcp__arxiv__search_author - Find papers by specific authors
mcp__arxiv__get_paper_by_id - Get details for known arXiv IDs
```

### Search Queries to Run

For a paper about [topic], search for:

1. **Direct topic**: `[main topic] [key method]`
2. **Alternative approaches**: `[problem] [alternative method]`
3. **Foundational work**: `[base technique] survey OR tutorial`
4. **Recent advances**: Category search with `lastUpdatedDate` sorting
5. **Key authors**: Author search for known researchers in the area

### Example Search Session

```python
# Main topic
search_papers(query="contrastive learning representations", maxResults=20, sortBy="relevance")

# Alternative approaches
search_papers(query="self-supervised learning vision", maxResults=15)

# Recent work
get_recent_papers(category="cs.LG", maxResults=30)

# Known author
search_author(author="Geoffrey Hinton", maxResults=10)

# Specific paper mentioned in draft
get_paper_by_id(ids=["2002.05709"])
```

## Paper Approval Process

**IMPORTANT**: Before including any paper in the related work, present candidates and get explicit approval.

### Step 1: Present Found Papers

```markdown
## Found Papers for Review

### Category: [Primary Topic]
1. **[Title]** (arXiv:XXXX.XXXXX)
   [Authors], [Year]
   Summary: [1-2 sentence description]
   Relevance: [Why this is relevant to the paper]

2. **[Title]** (arXiv:XXXX.XXXXX)
   ...

### Category: [Secondary Topic]
...
```

### Step 2: Ask for Approval

```markdown
## Please Review

- Should I include paper #1? [Y/N]
- Should I include paper #2? [Y/N]
...

### Additional Searches
Are there specific papers or topics I should search for?
- Known papers to include (provide arXiv IDs or titles)?
- Additional keywords to search?
- Specific authors to look up?
```

### Step 3: Only Include Approved Papers

After receiving approval, write the related work section using only the approved papers plus any papers already cited in the draft.

## Related Work Structure

### Option A: By Topic/Theme (Recommended)

```latex
\section{Related Work}
\label{sec:related}

\paragraph{[Theme 1: e.g., Self-Supervised Learning]}
[2-3 sentences covering this line of work, citing key papers]
\citet{paper1} introduced [concept], later extended by \citet{paper2}.
Recent work \citep{paper3,paper4} has focused on [direction].
Our approach differs by [key difference].

\paragraph{[Theme 2: e.g., Contrastive Methods]}
[Similar structure]

\paragraph{[Theme 3: e.g., Application Domain]}
[Similar structure]

\paragraph{[Theme 4: e.g., Theoretical Foundations]}
[Similar structure, if applicable]
```

### Option B: By Methodology

```latex
\section{Related Work}

\paragraph{[Approach A]-based Methods}
Methods based on [Approach A] include [papers]. These typically [characteristic].
However, [limitation that our work addresses].

\paragraph{[Approach B]-based Methods}
An alternative line of work uses [Approach B] \citep{papers}.
While effective for [scenario], these methods [limitation].

\paragraph{Hybrid Approaches}
Recent work has combined [A] and [B] \citep{papers}.
Our method extends this by [contribution].
```

## Writing Guidelines

### Narrative Flow
- **Start broad**: Begin with the general area
- **Narrow progressively**: Move toward your specific problem
- **End with positioning**: Clarify how your work fits

### Citation Density
- Aim for 15-30 citations in related work
- 2-4 citations per paragraph
- Mix seminal works and recent papers

### Positioning Statements

Every paragraph should end with differentiation:

```latex
% Good
Unlike \citet{prior}, which requires [assumption], our method [advantage].

% Good
While these methods focus on [X], we address the complementary problem of [Y].

% Bad (no differentiation)
These papers are related to our work.
```

### Fair Representation

```latex
% Good - acknowledge strengths
\citet{prior} achieves strong results on [task]. However, their reliance
on [assumption] limits applicability to [our setting].

% Bad - strawman
\citet{prior} fails to handle [cherry-picked case].
```

## BibTeX Generation

For each included paper, generate a BibTeX entry:

```bibtex
@inproceedings{chen2020simclr,
  title={A Simple Framework for Contrastive Learning of Visual Representations},
  author={Chen, Ting and Kornblith, Simon and Norouzi, Mohammad and Hinton, Geoffrey},
  booktitle={International Conference on Machine Learning},
  pages={1597--1607},
  year={2020},
  organization={PMLR}
}

@article{he2019moco,
  title={Momentum Contrast for Unsupervised Visual Representation Learning},
  author={He, Kaiming and Fan, Haoqi and Wu, Yuxin and Xie, Saining and Girshick, Ross},
  journal={arXiv preprint arXiv:1911.05722},
  year={2019}
}
```

### BibTeX Style Guide
- Use lowercase keys: `author2020keyword`
- Prefer published versions over arXiv when available
- Include DOI if available
- Use consistent venue abbreviations (ICML, NeurIPS, ICLR)

## Common Organizational Patterns

### For a Methods Paper
1. Problem setup and prior approaches
2. Related techniques (your building blocks)
3. Alternative solutions
4. Applications of similar methods

### For a Theory Paper
1. Problem formulation history
2. Related theoretical frameworks
3. Prior analysis techniques
4. Connections to other domains

### For an Applications Paper
1. Prior work on this application
2. Related methods from other domains
3. Benchmark and evaluation history
4. Practical deployment considerations

## LaTeX Conventions

```latex
% First mention in sentence - use \citet
\citet{author2020} introduced [concept], which...

% Parenthetical citation - use \citep
This approach builds on prior work~\citep{author2020,other2021}.

% Multiple citations - chronological order
\citep{foundational2015,extension2018,recent2023}

% Distinguish similar methods
Unlike the GAN-based approach of~\citet{gan_paper}, the VAE-based
method of~\citet{vae_paper} provides [advantage].
```

## Anti-Patterns to Avoid

1. **Laundry list**: Don't just list papers without synthesis
2. **Missing connections**: Show how papers relate to each other
3. **No positioning**: Always explain how your work differs
4. **Outdated coverage**: Include recent work (last 2-3 years)
5. **Missing seminal work**: Include foundational papers
6. **Unfair criticism**: Represent prior work accurately
7. **Over-citation**: Don't cite papers just to increase count

## Output Format

Generate these outputs in order:

### 1. Search Summary
```markdown
## ArXiv Searches Performed
- Query: "[query 1]" → [N] results
- Query: "[query 2]" → [N] results
- Category: [category] recent → [N] results
```

### 2. Papers for Approval
```markdown
## Candidate Papers

[Present each paper with title, authors, arXiv ID, and relevance]

**Please indicate which papers to include.**
```

### 3. After Approval: Related Work Section
```latex
\section{Related Work}
...
```

### 4. BibTeX Entries
```bibtex
% New entries for refs.bib
...
```

### 5. Coverage Analysis
```markdown
## Coverage Notes
- Well covered: [topics]
- Could use more: [topics]
- Suggested additional searches: [if any gaps]
```
