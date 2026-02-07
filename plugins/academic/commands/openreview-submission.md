---
name: openreview-submission
description: |
  Prepare OpenReview submission metadata from a paper draft. Use when asked to
  "prepare OpenReview submission", "format abstract for OpenReview", "generate keywords",
  "write TL;DR", "create lay summary", "submission form", or "camera-ready metadata".
  Produces copy-pasteable abstract, keywords, TL;DR, and lay summary.
model: sonnet
---

# OpenReview Submission Preparation

Generate all text metadata fields for OpenReview submission forms from a paper draft. Produces copy-pasteable outputs for the abstract, keywords, TL;DR, and lay summary.

> **Hybrid**: LaTeX-to-plain-text conversion and character counting are handled via script (sed/regex). Keywords, TL;DR, and lay summary require LLM for creative writing and judgment.

## Workflow

1. **Read the paper**: Focus on abstract, introduction, contributions, and conclusion
2. **Script: Extract and convert abstract**: Strip LaTeX commands via sed/regex, count characters
3. **LLM: Generate keywords**: Domain-specific, venue-appropriate terms
4. **LLM: Write TL;DR**: Single sentence, max 250 characters
5. **LLM: Write lay summary**: Accessible explanation for non-experts
6. **Present all outputs**: In copy-pasteable format with character counts

## Input Required

Point me to one of:
- A LaTeX file containing the paper (`.tex`)
- A compiled PDF of the paper
- A pasted abstract in LaTeX format

Optionally specify:
- **Target venue**: ICLR, NeurIPS, ICML, AAAI (affects keyword style)
- **Submission stage**: initial submission or camera-ready (lay summary is typically camera-ready only)

## OpenReview Form Field Reference

| Field | Limit | Required | Stage |
|-------|-------|----------|-------|
| Title | 1-250 chars | Yes | Submission |
| Abstract | 1-5,000 chars | Yes | Submission |
| Keywords | Comma-separated | Optional | Submission |
| TL;DR | Max 250 chars | Optional | Submission |
| Lay summary | ~200-300 words | Venue-dependent | Camera-ready |

## Step 1: Abstract (Plain Text) — Script-First

Convert the LaTeX abstract to clean, copy-pasteable plain text. Run the sed pipeline first, then fix any remaining artifacts manually.

### Automated conversion script

Run this to strip most LaTeX commands from the abstract:

```bash
# Extract abstract from .tex file and convert to plain text
sed -n '/\\begin{abstract}/,/\\end{abstract}/p' main.tex | \
  sed '1d;$d' | \
  sed -E '
    # Remove formatting commands
    s/\\textbf\{([^}]*)\}/\1/g
    s/\\emph\{([^}]*)\}/\1/g
    s/\\textit\{([^}]*)\}/\1/g
    s/\\textsc\{([^}]*)\}/\1/g
    s/\\texttt\{([^}]*)\}/\1/g
    # Remove citations and refs
    s/\\cite[pt]?\{[^}]*\}//g
    s/\\[cC]ref\{[^}]*\}//g
    # Abbreviation macros
    s/\\eg/e.g./g
    s/\\ie/i.e./g
    s/\\etal/et al./g
    s/\\wrt/w.r.t./g
    # Special characters
    s/~/ /g
    s/``/"/g
    s/'\''"/'\''"'/g
    s/\\%/%/g
    s/\\&/\&/g
    s/---/-/g
    s/--/-/g
    # Strip remaining simple commands
    s/\\[a-zA-Z]+\{([^}]*)\}/\1/g
    # Remove dollar-sign math delimiters (keep content)
    s/\$([^$]*)\$/\1/g
  ' | \
  tr '\n' ' ' | sed 's/  */ /g'
```

After running the script, count characters:
```bash
# Count characters in the converted abstract
echo -n "<paste abstract here>" | wc -c
```

### Remaining cleanup (LLM-assisted)

The script handles most conversions. Fix any remaining issues:

1. **Expand custom macros**: `\method` -> actual method name, `\ours` -> model name
2. **Convert complex math to Unicode**: `\alpha` -> α, `\mathbb{R}` -> R
3. **Verify character count**: Must be under 5,000 characters

### Common LaTeX-to-plain-text substitutions reference

```
\textbf{X}       ->  X
\emph{X}         ->  X
\textit{X}       ->  X
\textsc{X}       ->  X (or UPPERCASE)
\texttt{X}       ->  X
\method           ->  [expand to actual method name]
~                 ->  [space]
``X''             ->  "X"
\%                ->  %
\&                ->  &
--                ->  -
---               ->  -
\eg               ->  e.g.
\ie               ->  i.e.
\etal              ->  et al.
\wrt              ->  w.r.t.
```

### Unicode math symbols (prefer these for readability)

```
\alpha -> α    \beta -> β    \gamma -> γ    \delta -> δ
\epsilon -> ε  \lambda -> λ  \sigma -> σ    \theta -> θ
\phi -> φ      \pi -> π      \mu -> μ       \omega -> ω
\ell -> ℓ      \infty -> ∞   \approx -> ≈   \leq -> ≤
\geq -> ≥      \neq -> ≠     \times -> ×    \cdot -> ·
\in -> ∈       \subset -> ⊂  \nabla -> ∇    \partial -> ∂
\mathbb{R} -> R (or ℝ)       \mathbb{E} -> E
\sum -> Σ      \prod -> Π    \rightarrow -> ->
```

**Note**: OpenReview supports TeX in the abstract field (`$...$` and `$$...$$`). If the venue renders TeX, you may keep simple inline math as `$...$`. Provide both versions: one with TeX kept for OpenReview's renderer, and one fully plain-text as fallback.

## Step 2: Keywords

Generate 5-10 keywords as a comma-separated list.

### Keyword selection principles

1. **Include the task/problem**: e.g., "image classification", "language modeling"
2. **Include the method family**: e.g., "transformers", "diffusion models", "reinforcement learning"
3. **Include key techniques**: e.g., "self-supervised learning", "knowledge distillation"
4. **Include the domain**: e.g., "computer vision", "natural language processing", "computational biology"
5. **Include distinguishing properties**: e.g., "parameter-efficient", "few-shot", "robust"
6. **Match venue taxonomy**: Use terms that appear in the venue's subject area list

### Keyword style

- Lowercase unless proper noun or acronym
- No trailing periods
- Specific over generic: "vision transformers" > "deep learning"
- Include both broad and narrow terms for discoverability
- Avoid redundancy with the title

### Examples by subfield

**Computer Vision**:
```
image generation, diffusion models, text-to-image, classifier-free guidance, denoising score matching
```

**NLP**:
```
large language models, instruction tuning, reinforcement learning from human feedback, alignment, safety
```

**Theory**:
```
optimization, convergence rates, non-convex optimization, stochastic gradient descent, generalization bounds
```

**Representation Learning**:
```
self-supervised learning, contrastive learning, disentangled representations, transfer learning, foundation models
```

## Step 3: TL;DR

Write a single sentence of **max 250 characters** that captures the paper's core contribution.

### TL;DR formula

```
We [verb] [what] [how/insight], achieving [key result].
```

### Principles

- **One sentence only**: No periods followed by more text
- **Lead with the contribution**: What you did, not why the problem matters
- **Be specific**: Name the method, mention the key property
- **Include the main result if space permits**: A number or comparison
- **Count characters carefully**: 250 characters max including spaces

### Examples

```
We propose FlashAttention, an IO-aware exact attention algorithm that trains Transformers 2-4x faster with linear memory scaling. (131 chars)
```

```
We show that language models can learn to reason through chain-of-thought prompting without any fine-tuning. (108 chars)
```

```
We introduce a diffusion-based video generation model that produces temporally coherent clips up to 60 seconds. (112 chars)
```

```
We prove that overparameterized neural networks converge to global optima at a linear rate under standard initialization. (121 chars)
```

### Common mistakes

- Exceeding 250 characters (OpenReview silently truncates or rejects)
- Writing two sentences
- Being too vague: "We propose a new method for X" (what method? what's new?)
- Restating the title verbatim

## Step 4: Lay Summary

Write a ~200-300 word summary accessible to a **scientifically literate non-expert** (e.g., a science journalist, a program manager, a researcher in a different field).

### When needed

- **NeurIPS 2025+**: Required for accepted papers (camera-ready)
- **ICML 2026+**: Required for accepted papers (camera-ready)
- **ICLR**: Not yet required (check venue-specific guidance)
- Generating one early helps clarify your paper's narrative even if not yet required

### Structure (4-part model)

```markdown
[1. CONTEXT - Why should anyone care? (1-2 sentences)]
What real-world problem or scientific question motivates this work?
Use concrete, tangible language. No jargon.

[2. CHALLENGE - What makes this hard? (1-2 sentences)]
What specific obstacle or limitation exists today?
Frame in terms a non-expert can understand.

[3. WHAT WE DID - Your contribution (2-3 sentences)]
Describe your approach using analogy or plain language.
Avoid formulas, acronyms, and technical terms.
If you must use a technical term, define it inline.

[4. WHY IT MATTERS - Impact and implications (1-2 sentences)]
What does this enable? Who benefits?
Connect back to the real-world context from part 1.
```

### Writing principles

- **No jargon**: Replace "latent space" with "compressed representation", "gradient descent" with "iterative optimization process", or better yet, use an analogy
- **No acronyms**: Spell everything out; avoid even common ones like "LLM" or "RL"
- **Use analogies**: "Like a spellchecker for images..." or "Similar to how a translator..."
- **Be concrete**: "medical images" not "downstream tasks"; "chatbots" not "language agents"
- **Active voice**: "We developed" not "A method was developed"
- **No overclaiming**: Be honest about scope and limitations

### Example

For a paper on efficient attention mechanisms:

```
Modern artificial intelligence systems that process text, such as chatbots and
translation tools, work by examining relationships between every pair of words
in a passage. As passages grow longer, this process becomes extremely slow and
memory-intensive - processing a book-length text can require more computer
memory than is available on most hardware.

We developed a new algorithm that reorganizes how these word-to-word comparisons
are computed, taking advantage of the layered structure of computer memory
(similar to how a well-organized filing cabinet is faster to search than a
pile of loose papers). Our approach produces exactly the same results as the
standard method but runs two to four times faster and uses significantly less
memory.

This means AI systems can now process much longer documents - entire books,
lengthy legal contracts, or long conversation histories - on the same hardware
that previously could only handle short passages. This advances the practical
deployment of AI tools that need to understand and reason over large amounts
of text.
```

## Output Format

Present all outputs in a single, copy-pasteable block with clear section headers and character/word counts.

```markdown
---

## OpenReview Submission Metadata

### Abstract (with TeX)

<abstract for OpenReview's TeX-enabled field>

Characters: [N] / 5,000

### Abstract (plain text fallback)

<fully plain-text version, no TeX markup>

Characters: [N] / 5,000

### Keywords

<comma-separated keyword list>

### TL;DR

<single sentence, max 250 characters>

Characters: [N] / 250

### Lay Summary

<accessible summary for non-experts>

Words: [N] (~200-300 target)

---
```

## Verification Checklist

Before finalizing, verify:

- [ ] **Abstract**: All LaTeX commands removed or converted; no `\cite`, `\ref`, `\cref` remnants
- [ ] **Abstract**: Character count under 5,000
- [ ] **Abstract**: Custom macros expanded (check for `\method`, `\ours`, `\dataset`, etc.)
- [ ] **Abstract**: TeX version uses only `$...$` / `$$...$$` (no `\begin`, `\textbf`, etc.)
- [ ] **Keywords**: 5-10 terms, comma-separated, lowercase (except proper nouns/acronyms)
- [ ] **Keywords**: Cover task, method, domain, and distinguishing properties
- [ ] **Keywords**: No overlap with exact title words (adds no discoverability)
- [ ] **TL;DR**: Single sentence, max 250 characters (count carefully)
- [ ] **TL;DR**: Mentions the method and key result or property
- [ ] **Lay summary**: 200-300 words, no jargon or acronyms
- [ ] **Lay summary**: Understandable by someone outside ML
- [ ] **All fields**: No claims beyond what the paper supports
- [ ] **All fields**: No author-identifying information (if double-blind)
