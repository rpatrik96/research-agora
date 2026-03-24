# Literature & Citations

Prompts for literature search, synthesis, gap identification, and citation verification — with explicit guards against hallucination.

---

## Who This Is For

If you write related work sections, maintain a BibTeX file, run systematic reviews, or want to find relevant papers quickly without spending hours on Google Scholar, start here. Citation verification is the highest-ROI use case in this file: GPT-4 still hallucinates 18–29% of citations in literature reviews. These prompts build in verification from the start.

---

## Prerequisites

| For browser prompts | For citation verification (CLI) |
|--------------------|--------------------------------|
| [Claude.ai](https://claude.ai) account (free tier works) | Claude Code + `pip install bibtexupdater` |
| Papers available as PDFs to upload, or titles/abstracts to paste | `.bib` file on disk in your project directory |
| — | Internet access (queries Semantic Scholar and CrossRef) |

---

## Prompt 1: Literature Search with Methodology Focus

**Use case:** You need a rapid survey of how a specific topic has been studied — not just what claims exist, but what methods were used and what limitations researchers acknowledge.

**Works in:** Browser or CLI

```
Conduct a literature review on [topic].

Find the 5 most-cited papers published between 2022 and 2025. For each paper:
1. State the main claim in one sentence
2. Describe the methodology in 2–3 sentences (dataset, model, evaluation protocol)
3. Identify one key limitation the authors themselves acknowledge

Output: A markdown table with columns — Paper (author, year), Main claim, Methodology, Limitation.

Do not invent citations. If you are uncertain about a fact, write [UNCERTAIN] in that cell.
```

**Expected output:** A 5-row table. Every `[UNCERTAIN]` marker is a cell you must verify before using the content.

**What to verify:**
- For each paper: search the title on [Semantic Scholar](https://semanticscholar.org) or [Google Scholar](https://scholar.google.com). Does the paper exist? Is the year correct?
- Are the methodology descriptions consistent with the actual abstracts?
- Are any `[UNCERTAIN]` markers present? Follow up on each one.
- Do not use this table in a paper without checking at least the top 2–3 citations against the actual PDFs.

**Related skills:** `literature-synthesizer` (academic@research-agora), `paper-references` (academic@research-agora)

---

## Prompt 2: Synthesis with Verification Guard

**Use case:** You have a set of papers and need a cohesive related-work paragraph — written, not just listed — with inline citations and explicit uncertainty markers.

**Works in:** Browser (paste titles/abstracts) or CLI (upload PDFs)

```
Synthesize the findings from these papers into a 300-word summary suitable for a related work section:

[Paste titles, authors, years, and key abstracts — or upload PDFs]

Requirements:
- Cite each claim using author–year format inline (e.g., Smith et al., 2023)
- Group claims thematically, not chronologically
- For each claim you are uncertain about, write [UNCERTAIN: reason]
- Do not invent sources. If you cannot ground a claim in one of the provided papers, omit it.

Output: The synthesis paragraph, followed by a list of all citations used with full titles.
```

**Expected output:** A coherent paragraph with inline citations, uncertainty markers where appropriate, and a reference list at the end.

**What to verify:**
- Cross-check 3–5 inline citations against the actual papers. Does the cited paper actually support the claim?
- Are all papers in the reference list ones you actually provided, or did the agent invent new ones?
- Any `[UNCERTAIN]` markers: investigate each before using that claim.

**Related skills:** `literature-synthesizer` (academic@research-agora), `evidence-checker` (research-agents@research-agora)

---

## Prompt 3: Citation Verification (CLI)

**Use case:** You have a `.bib` file — hand-written, AI-generated, or accumulated over time — and need to confirm every entry resolves to a real publication before submission.

**Works in:** CLI only (requires file access and `bibtexupdater`)

First, install the dependency:
```bash
pip install bibtexupdater
```

Then run the Research Agora skill:
```
/paper-references
```

Or use this manual prompt if you prefer to run it without the skill:

```
You are a BibTeX librarian.

Read the file [references.bib]. For each entry:
1. Extract the cite key, title, authors, and year
2. Query Semantic Scholar and CrossRef for a matching publication
3. Compare metadata: title, authors, year

Output: A markdown table with columns — Cite key, Status (verified / mismatch / not found), Details (what mismatched, or confirmation of match).

Flag any entry where:
- The title does not match any indexed publication
- The year differs from what is indexed
- The authors differ substantially
```

**Expected output:** A table with one row per BibTeX entry. `not found` entries are likely hallucinated references. `mismatch` entries have metadata errors.

**What to verify:**
- For every `not found` entry: search the title manually on [Semantic Scholar](https://semanticscholar.org). If it genuinely doesn't exist, remove or replace the entry.
- For every `mismatch` entry: open the actual paper and correct the metadata.
- Re-run verification after corrections. All entries should reach `verified` before submission.

**Related skills:** `paper-references` (academic@research-agora)

---

## Prompt 4: Gap Identification

**Use case:** You want to identify what has *not* been studied — open questions, contradictions, and methodological gaps — to position your own contribution.

**Works in:** Browser (paste titles/abstracts) or CLI

```
Based on the following papers [paste titles and abstracts, or upload PDFs]:

Identify:
1. The 3 most common experimental methodologies across these papers
2. Contradictions or disagreements between studies — where papers reach different conclusions
3. The 3 research questions that appear most consistently open or unresolved

Do not invent citations. For each point, name which paper(s) support it.
Flag any claim you cannot ground in the provided papers.
```

**Expected output:** Three numbered sections. Claims should be traceable to named papers.

**What to verify:**
- Are the "contradictions" real disagreements, or differences in scope/setting that don't actually conflict?
- Are the open questions ones your research could actually address?
- Are any claims grounded in papers you didn't provide? (A sign the agent is hallucinating.)

**Related skills:** `literature-synthesizer` (academic@research-agora), `benchmark-scout` (academic@research-agora)

---

## Citation Verification Tools

| Tool | What it checks | Notes |
|------|---------------|-------|
| [SwanRef](https://swanref.org) | Citation existence against academic papers | Free, batch upload |
| [Semantic Scholar API](https://semanticscholar.org/product/api) | 214M papers, programmatic access | Free API key |
| [Elicit](https://elicit.com) | Structured data extraction from papers | Free tier available |
| [Veru](https://truvio.vercel.app) | Existence AND attribution accuracy | Checks whether a claim is actually in the cited paper |

**Warning:** GPT-4 still hallucinates 18–29% of citations in literature reviews. Always verify AI-generated references before submission — not just existence, but that the cited paper actually supports the claim attributed to it.

---

## Further Reading

- [Agentic AI for Literature Reviews (Anara)](https://anara.com/blog/agentic-ai-for-literature-reviews): Six-step workflow with prompt templates.
- [Claude Code for Scientists (Mineault)](https://www.neuroai.science/p/claude-code-for-scientists): Best practices for researchers using Claude Code for literature work.
- [ML Tools for Scientists (Mineault)](https://www.neuroai.science/p/ml-tools-for-neuroscientists): Curated toolkit: Claude, NotebookLM, Elicit, Perplexity.
