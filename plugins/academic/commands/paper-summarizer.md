---
name: paper-summarizer
description: Summarize research papers for rapid triage and comprehension. Use when asked to "summarize this paper", "paper summary", "what does this paper do", "triage papers", or "TLDR this paper". Takes an arXiv ID or paper text and produces structured summaries at configurable depth.
model: sonnet
metadata:
  research-domain: general
  research-phase: literature-review
  task-type: analysis
  verification-level: heuristic
---

# Paper Summarizer

> **Hybrid approach**: Script-first for paper retrieval (arXiv API, PDF extraction). LLM for synthesis and relevance assessment.

Help researchers triage their reading queue. "Which of these 30 papers should I actually read?" Answer in 2 minutes what would take 30 minutes of skimming. This skill extracts, structures, and synthesizes -- it surfaces what a paper CLAIMS, not whether claims hold.

## Workflow

1. **Retrieve paper**: arXiv ID -> download via arXiv MCP tools, or user provides text/PDF path
2. **Extract structure**: title, authors, abstract, section headers, tables, figures
3. **Identify core elements**: contribution, method, key results, limitations
4. **Generate summary** at requested depth (TLDR / Standard / Deep)
5. **Assess relevance** to user's research context (if provided)

## Script-First Components

Before LLM synthesis, extract programmatically:

- **Paper retrieval**: Use arXiv MCP tools (`mcp__arxiv__search_papers`, `mcp__arxiv__download_paper`) for fetching papers by ID or keyword
- **Metadata extraction**: Parse title, authors, venue, date from arXiv API response or PDF headers
- **Section structure**: Extract section/subsection headers to build a skeleton
- **Tables**: Extract table contents for result comparison
- **Bibliography**: Parse reference list for citation context and related work pointers
- **Figure captions**: Extract captions to identify key visualizations without rendering

The LLM handles: synthesizing the contribution narrative, assessing novelty, identifying unstated limitations, and relevance scoring.

## Depth Levels

### TLDR (30 seconds)

2-3 sentences. Core contribution + key result + main limitation. Nothing else.

Example:
```
Proposes DiffAugment, applying differentiable data augmentation to both real
and fake images during GAN training. Improves FID by 15-30% on CIFAR-10/100
with limited data. Only tested on image generation; unclear if it helps
conditional GANs or other modalities.
```

### Standard (2 minutes)

Structured summary covering all sections in the output format below. This is the default depth.

### Deep (5 minutes)

Standard summary plus:
- **Technical details**: Key equations, architectural choices, training procedures
- **Equation highlights**: The 1-3 equations that define the method, with plain-language explanation
- **Comparison to related work**: How this positions against the 3-5 most relevant prior methods
- **Reproducibility assessment**: Is there code? Are hyperparameters specified? Could you reimplement this?
- **Follow-up questions**: What would you ask the authors at a poster session?

## Output Format (Standard Depth)

```markdown
## Paper Summary

**Title**: [Title]
**Authors**: [First author et al., Year]
**Venue**: [Conference/Journal if known]
**arXiv**: [ID if available]

### Core Contribution
[1-2 sentences: What is the main new thing?]

### Method
[2-3 sentences: How does it work? Key idea, not implementation details.]

### Key Results
| Benchmark | Metric | Result | vs. Prior SOTA |
|-----------|--------|--------|----------------|
| [Dataset] | [Metric] | [Value] | [+/- X%] |

### Limitations (Author-Stated)
- [Limitation 1]
- [Limitation 2]

### Limitations (Unstated)
- [Limitation the paper doesn't acknowledge]

### Relevance Assessment
**If you work on [X]**: [High/Medium/Low relevance because...]
**Read the full paper if**: [Condition]
**Skip if**: [Condition]

### Key Figures
- Figure [N]: [What it shows and why it matters]
```

## Batch Mode

When summarizing multiple papers:

1. Summarize each paper at TLDR depth
2. Rank by relevance to user's stated research context
3. Group by theme/approach if papers cluster naturally
4. Produce a comparison table for overlapping papers

Output format for batch:
```markdown
## Reading Queue Triage ([N] papers)

### Must Read
| # | Paper | Why | Time to Read |
|---|-------|-----|--------------|
| 1 | [Title] | [Reason] | [Estimate] |

### Skim Abstract + Results
| # | Paper | Why Skim |
|---|-------|----------|

### Skip
| # | Paper | Why Skip |
|---|-------|----------|

### Individual Summaries
[TLDR for each paper]
```

## Comparison Mode

When asked "How does paper A differ from paper B?":

```markdown
## Paper Comparison

### Shared Problem
[What both papers address]

### Key Differences
| Aspect | Paper A | Paper B |
|--------|---------|---------|
| Approach | [Method A] | [Method B] |
| Key assumption | [Assumption A] | [Assumption B] |
| Best result | [Result A] | [Result B] |
| Limitation | [Limit A] | [Limit B] |

### When to Prefer A
[Conditions where A is the better choice]

### When to Prefer B
[Conditions where B is the better choice]

### Gap Between Them
[What neither paper addresses]
```

## Handling Different Input Formats

### arXiv ID
```
User: "Summarize 2301.07041"
Action: Fetch via arXiv MCP tools, extract full text, summarize
```

### PDF Path
```
User: "Summarize /path/to/paper.pdf"
Action: Read PDF, extract text and structure, summarize
```

### Pasted Text
```
User: "Summarize this paper: [text]"
Action: Parse provided text directly, summarize
```

### URL
```
User: "Summarize https://arxiv.org/abs/2301.07041"
Action: Extract arXiv ID from URL, fetch via MCP tools, summarize
```

## Quality Checks

Before delivering a summary, verify:

- [ ] Core contribution is stated as the AUTHORS frame it (not your interpretation)
- [ ] Key results include actual numbers, not vague claims ("improves performance")
- [ ] Limitations include at least one unstated limitation
- [ ] Relevance assessment is specific to a research area, not generic
- [ ] Method description captures the KEY IDEA, not a list of components

## Scope Boundaries

This skill surfaces what a paper **claims**. It does not:
- Evaluate whether claims are correct (use `paper-review`)
- Assess argument validity (use `argument-autopsy` from research-agents)
- Synthesize across a body of literature (use `literature-synthesizer`)
- Generate new text based on the paper (use writing skills)

## Output

Generate:
1. A structured summary at the requested depth (default: Standard)
2. Relevance assessment tied to user's research context
3. Actionable read/skip recommendation
4. For batch mode: ranked reading queue with time estimates