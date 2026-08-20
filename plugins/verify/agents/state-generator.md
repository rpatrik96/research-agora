---
name: state-generator
description: |
  Generate a research-state.json file from a paper. This is the FIRST step
  in any parallel research analysis pipeline. Creates structured representation
  enabling subagent delegation. Trigger: "generate research state",
  "parse paper for analysis", "prepare paper for audit".
model: sonnet
color: blue
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: verification
  verification-level: layered
  visibility: internal
---

# Research State Generator

> **Hybrid**: `scripts/parse_latex.py` extracts the structure; the LLM adds only the claim layer on top of it.

Generate a structured JSON representation of a research paper for parallel analysis.

## Purpose

This agent creates the `research-state.json` file that enables:
- Parallel subagent processing (fan-out/fan-in)
- Scoped context for each analysis task
- Efficient caching and incremental updates
- Claim tracking across verification stages

## When to Use

- Before running `parallel-audit`, `parallel-theory-audit`, or any orchestrator
- When you need to analyze a paper's structure
- When preparing for claim verification or proof auditing
- When caching paper analysis for repeated queries

## Input Requirements

Provide ONE of:
1. **LaTeX source file**: `paper.tex` or directory with `.tex` files
2. **PDF file**: `paper.pdf` (less accurate, uses text extraction)
3. **arXiv ID**: Will download and parse automatically

## Workflow

### Phase 1: Structure (script)

`scripts/parse_latex.py` already extracts every structural element this agent
needs, and writes them in the `research-state.json` shape. Run it; do not
re-derive its output by reading the LaTeX yourself.

```bash
python3 scripts/parse_latex.py "$PAPER_DIR" --output research-state.json
```

It resolves `\input`/`\include` from the main file, and returns sections,
figures, tables, equations, algorithms, theorem environments (with labels and
proof locations), and the citation list. It prints a per-category count; if a
category you expect is zero, the parse is wrong and the fix is the parser, not
a hand-written substitute.

**Everything the script produces is settled.** Structure is a parsing problem
with a right answer, and a model reading `.tex` gets it nearly right in a way
that is expensive to detect. What follows is only the layer the script cannot
do: which sentences are claims, and what backs them.

### Phase 2b: Theory Structure Parsing (for theoretical papers)

`parse_latex.py` already returns the theorem-like environments — theorem,
lemma, proposition, corollary, definition — each with its label, statement, and
whether a proof follows. Take those from the script. Three things it does not
extract, and these are what this phase is for:

#### Assumption Extraction

Formally stated assumptions, which have no single environment to grep:
- `\begin{assumption}` environments
- Numbered conditions ("(A1)", "(A2)") stated inline in theorem statements
- "Assume that...", "Suppose that..." patterns in surrounding prose

#### Bound Extraction

Asymptotic bounds, wherever they appear:
- `O(...)`, `\Omega(...)`, `\Theta(...)` expressions
- Explicit rate expressions: `\leq C/\sqrt{T}`
- `\tilde{O}(...)` (ignoring log factors)

#### Proof-Theorem Linking

The script records that a `\begin{proof}` follows a theorem; it does not
resolve which theorem a detached proof belongs to. Link them by:
- `\begin{proof}[Proof of Theorem 1]` headers
- Proximity, where a proof immediately follows its theorem
- `\ref{}` back-references inside the proof body

> **Note**: The `theory` section is **optional** — populate it only when
> theorem-like environments are detected. Empirical-only papers get
> `"theory": null`.

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
  "theory": {
    "theorems": [
      {
        "id": "thm1",
        "type": "theorem",
        "statement": "Under Assumptions A1-A3, ...",
        "assumptions_used": ["A1", "A2", "A3"],
        "proof_text": "...",
        "depends_on": ["lem1", "lem2"],
        "proof_location": {"file": "appendix.tex", "line": 45}
      }
    ],
    "assumptions": [
      {
        "id": "A1",
        "text": "The function f is L-Lipschitz continuous",
        "standard_name": "L-smoothness",
        "used_by": ["thm1", "lem1"]
      }
    ],
    "definitions": [
      {
        "id": "def1",
        "term": "complexity measure",
        "definition": "We define the complexity...",
        "first_use": {"file": "main.tex", "line": 32}
      }
    ],
    "bounds": [
      {
        "id": "B1",
        "expression": "O(1/T^2)",
        "context": "convergence rate",
        "parameters": ["T", "L", "d"],
        "source_theorem": "thm1"
      }
    ],
    "dependency_graph": {
      "nodes": [],
      "edges": []
    },
    "symbol_table": {}
  },
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
- `parallel-theory-audit` orchestrator
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
