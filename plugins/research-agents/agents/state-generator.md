---
name: state-generator
description: |
  Generate a research-state.json file from a paper. This is the FIRST step
  in any parallel research analysis pipeline. Creates structured representation
  enabling subagent delegation. Trigger: "generate research state",
  "parse paper for analysis", "prepare paper for audit".
model: sonnet
color: blue
---

# Research State Generator

> **Hybrid**: Claim extraction produces structured JSON (research-state.json). LLM is needed to identify and classify claims from paper text.

Generate a structured JSON representation of a research paper for parallel analysis.

## Purpose

This agent creates the `research-state.json` file that enables:
- Parallel subagent processing (fan-out/fan-in)
- Scoped context for each analysis task
- Efficient caching and incremental updates
- Claim tracking across verification stages

## When to Use

- Before running `parallel-audit` or any orchestrator
- When you need to analyze a paper's structure
- When preparing for claim verification
- When caching paper analysis for repeated queries

## Input Requirements

Provide ONE of:
1. **LaTeX source file**: `paper.tex` or directory with `.tex` files
2. **PDF file**: `paper.pdf` (less accurate, uses text extraction)
3. **arXiv ID**: Will download and parse automatically

## Workflow

### Phase 1: Source Loading

1. **Identify source type**:
   - If arXiv ID provided: Download using `mcp__arxiv__download_paper`
   - If LaTeX: Read main `.tex` file and imports
   - If PDF: Extract text with page structure

2. **Compute source hash**:
   ```
   SHA256(file_contents) → source_hash
   ```

3. **Check cache**:
   - If `research-state.json` exists with matching `source_hash`, skip regeneration
   - Use `--force` flag to regenerate anyway

### Phase 2: Structure Parsing

#### LaTeX Source

Parse the following elements:

| Element | LaTeX Pattern | Output |
|---------|---------------|--------|
| Sections | `\section{Title}` | `{id: "sec1", title: "Title", level: 1}` |
| Subsections | `\subsection{Title}` | `{id: "sec1.1", title: "Title", level: 2}` |
| Abstract | `\begin{abstract}` | `{id: "abstract", level: 0}` |
| Figures | `\begin{figure}...\caption{...}` | `{id: "fig1", caption: "..."}` |
| Tables | `\begin{table}...\caption{...}` | `{id: "tab1", caption: "..."}` |
| Equations | `\begin{equation}...\label{...}` | `{id: "eq1", label: "...", latex: "..."}` |
| Algorithms | `\begin{algorithm}` | `{id: "alg1", caption: "..."}` |
| Theorems | `\begin{theorem}` | `{id: "thm1", statement: "..."}` |
| Lemmas | `\begin{lemma}` | `{id: "lem1", statement: "..."}` |

#### PDF Source

Use heuristics:
- Section detection: Font size changes, numbering patterns ("1.", "2.1")
- Figure detection: "Figure X:" captions
- Table detection: "Table X:" captions

### Phase 3: Claim Extraction

Scan text for claim indicators:

#### Explicit Claim Patterns

| Pattern | Claim Type |
|---------|------------|
| `We show that...` | empirical/theoretical |
| `We demonstrate that...` | empirical |
| `We prove that...` | theoretical |
| `Our method achieves...` | empirical |
| `We propose...` | methodological |
| `We introduce...` | methodological/novelty |
| `Theorem N:` | theoretical |
| `Experiments demonstrate...` | empirical |

#### Implicit Claim Patterns

| Pattern | Claim Type |
|---------|------------|
| `X outperforms Y` | comparative |
| `better than`, `faster than` | comparative |
| `novel`, `first`, `new approach` | novelty |
| `state-of-the-art` | comparative |
| `significant improvement` | empirical |

### Phase 4: Claim Classification

For each extracted claim, determine:

#### Type Classification

| Type | Indicators | Example |
|------|------------|---------|
| **empirical** | Numbers, metrics, dataset names | "Achieves 95% accuracy on CIFAR-10" |
| **theoretical** | Theorem/lemma/proof context | "The algorithm converges in O(n log n)" |
| **methodological** | "our approach", "we design" | "We propose a novel attention mechanism" |
| **comparative** | Comparison words, baselines | "Outperforms BERT by 5%" |
| **novelty** | "first", "novel", "new" | "First method to solve X" |
| **assumed** | "well-known", implicit, citations | "Neural networks are universal approximators" |

#### Importance Classification

| Importance | Location | Description |
|------------|----------|-------------|
| **critical** | Abstract, contributions list | Core claims that paper acceptance depends on |
| **major** | Methods, main results | Important supporting claims |
| **minor** | Related work, limitations | Context or caveats |

### Phase 5: Evidence Mapping

Link claims to evidence:

1. **Find references in claim text**:
   - Table references: "Table 1", "Tab. 2", `\ref{tab:results}`
   - Figure references: "Figure 3", "Fig. 4", `\ref{fig:arch}`
   - Equation references: "Eq. 5", `\eqref{eq:loss}`

2. **Build evidence map**:
   ```json
   {
     "C1": [
       {"type": "table", "ref": "tab1", "strength": null},
       {"type": "figure", "ref": "fig2", "strength": null}
     ]
   }
   ```

### Phase 6: Terminology Extraction

Build glossary of paper-specific terms:

1. **Explicit definitions**: "We define X as..."
2. **Acronyms**: "Large Language Model (LLM)"
3. **Novel terms**: Terms in italics or quotes at first use

### Phase 7: Citation Processing

Parse bibliography:

1. Extract `.bib` file or inline `\bibitem` entries
2. For each citation, record:
   - Citation key
   - Title, authors, year, venue
   - arXiv ID if available

### Phase 8: Output Generation

Write `research-state.json` to paper directory:

```json
{
  "metadata": {
    "title": "Paper Title",
    "arxiv_id": "2301.00001",
    "venue_target": "neurips",
    "generated_at": "2025-01-29T10:30:00Z",
    "source_path": "/path/to/paper.tex",
    "source_hash": "abc123...",
    "word_count": 8500,
    "page_count": 9
  },
  "structure": {
    "sections": [...],
    "figures": [...],
    "tables": [...],
    "equations": [...],
    "algorithms": [...],
    "theorems": [...]
  },
  "claims": [...],
  "evidence_map": {...},
  "citations": [...],
  "terminology": {...},
  "assumptions": [],
  "processing_log": [
    {
      "timestamp": "2025-01-29T10:30:00Z",
      "agent": "state-generator",
      "action": "initial_generation",
      "details": {"claims_extracted": 15, "sections_found": 7}
    }
  ]
}
```

## Caching Behavior

| Scenario | Action |
|----------|--------|
| No existing state file | Generate new |
| State file exists, hash matches | Skip (return cached) |
| State file exists, hash differs | Regenerate |
| `--force` flag provided | Regenerate |
| `--incremental` flag | Update only changed sections |

## Error Handling

| Error | Response |
|-------|----------|
| File not found | Return error, list searched locations |
| LaTeX parse error | Attempt recovery, log warning, continue |
| PDF extraction fails | Return error, suggest LaTeX source |
| No claims found | Generate state with empty claims, log warning |

## Output Verification

Before saving, verify:
- [ ] `metadata.title` is non-empty
- [ ] `metadata.generated_at` is valid ISO 8601
- [ ] At least one section exists
- [ ] All claim IDs are unique and match pattern `C[0-9]+`
- [ ] All evidence refs in claims point to existing elements

## Integration

### Called By
- `parallel-audit` orchestrator
- `parallel-review` orchestrator
- User directly for preprocessing

### Updates
- Creates `research-state.json` in paper directory
- Adds entry to `.research-cache/index.json` if caching enabled

## Example Usage

```
User: Generate research state for /papers/my-paper/main.tex

Agent:
1. Reading /papers/my-paper/main.tex...
2. Computing source hash: sha256:a1b2c3...
3. No existing state file found, generating...
4. Parsed structure: 7 sections, 5 figures, 3 tables
5. Extracted 18 claims (8 empirical, 3 theoretical, 4 comparative, 3 novelty)
6. Mapped evidence for 15/18 claims
7. Processed 45 citations
8. Writing research-state.json...

Done! Generated state file with:
- 18 claims (pending verification)
- 5 figures, 3 tables, 8 equations
- 45 citations

Next steps:
- Run `/parallel-audit` to verify claims in parallel
- Run `/evidence-grader` on specific claims
```

## Validation Schema

Output must validate against `schemas/research-state.schema.json`.

## Performance Notes

- LaTeX parsing: ~5-10 seconds for typical paper
- PDF extraction: ~10-30 seconds (more variable)
- arXiv download: ~5-15 seconds (network dependent)
- Claim extraction: ~20-40 seconds (LLM dependent)

Total typical time: 30-90 seconds for initial generation.
