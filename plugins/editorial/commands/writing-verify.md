---
name: writing-verify
description: >
  Quantitative writing quality verification for scientific papers.
  Use when asked to "score my writing", "grade this paper", "writing quality check",
  "verify writing quality", "how good is my writing", "rate my prose",
  "writing metrics", "readability analysis", "check my paper's clarity",
  "writing score", or "assess writing quality". Produces a structured report
  with A-F grade, dimension scores, and prioritized fix suggestions.
model: sonnet
disable-model-invocation: true
metadata:
  research-domain: general
  task-type: verification
  research-phase: paper-writing
  verification-level: layered
---

# Writing Quality Verification

> **Hybrid**: Runs `scripts/writing_verify.py` first for deterministic metrics,
> then applies LLM semantic analysis for dimensions scripts cannot measure.
> Produces a quantitative score — not a rewrite.

## Philosophy

This tool scores; it does not fix. It is the **verification** complement to the diagnostic
editorial skills. Use it to measure where you stand, then use `/writing-diagnosis`,
`/editorial-brain`, or `/argument-autopsy` for remediation.

Sources codified: Strunk & White (omit needless words, active voice), Hemingway (short
declarative sentences), Orwell (6 rules), Steven Pinker (curse of knowledge, concrete nouns),
Smart Brevity (Core 4, reader-first), Stephen King (vary rhythm, kill darlings),
The Economist Style Guide (clarity follows clarity of thought, short words are strong words).

## Modes

**Standard Mode** (default): Full script metrics + LLM semantic analysis + combined A-F grade.

**Quick Mode**: Script metrics only, no LLM semantic layer. Triggered by "quick check",
"just the numbers", "quick score", or when user says "re-check" after making edits.

## Workflow

### Step 1: Determine Input

- If user provides a file path, use it directly.
- If user pastes text, save to a temporary file.
- If no input specified, check for common paper files (`main.tex`, `paper.tex`, `draft.tex`,
  `*.tex`) in the current directory.
- Auto-detect format: LaTeX, Markdown, or plain text.

### Step 2: Run Script Metrics (ALWAYS FIRST)

```bash
python3 scripts/writing_verify.py "$INPUT_FILE" --json --format auto
```

For quick mode, add `--quick`. Parse the JSON output to extract all metrics.

### Step 3: LLM Semantic Analysis (Standard Mode Only)

With script metrics as context, evaluate dimensions scripts cannot measure:

**Precision Assessment** (score 1-10):
- For each paragraph's opening sentence (from `opening_sentences` in script output): does it
  state the paragraph's main point? Count buried ledes.
- Are claims backed by specific evidence? Flag unsupported assertions.
- Is terminology consistent? The same concept should use the same word throughout.
- Are transitions between paragraphs logical? Flag orphan transitions.
- Are citations specific? ("Smith et al. (2023) showed X" vs. "previous work showed")

**Opening Strength**:
- Apply the Smart Brevity test to the abstract's first sentence: "Would you read this if you
  hadn't written it?"
- Check the introduction's first sentence: does it earn attention?

**Curse-of-Knowledge Check**:
- Flag assumptions about reader background that may not hold.
- Identify undefined terms assumed familiar.
- Note missing context that experts forget is non-obvious.

**Claim-Evidence Alignment**:
Using the L1-L6 evidence hierarchy (CODE_VERIFIED, REPRODUCIBLE_EXPERIMENT, PAPER_EVIDENCE,
CITATION_SUPPORT, LOGICAL_ARGUMENT, ASSERTION):
- Flag L6 assertions in core-claims sections (methods, results).
- L6 is acceptable in motivation and future work.

### Step 4: Compute Scores and Grade

Four dimensions, each scored 1-10:

| Dimension | Weight | Source |
|-----------|--------|--------|
| Accessibility | 20% | Script: FK grade, sentence length, jargon density |
| Clarity | 30% | Script: passive %, hedges, fillers, weak openers |
| Flow | 20% | Script: sentence CV, monotony, length distribution |
| Precision | 30% | LLM: buried ledes, claim-evidence, terminology, transitions |

Overall grade = weighted average mapped to:

| Grade | Threshold | Meaning | Action |
|-------|-----------|---------|--------|
| A+ | >=9 | Publication-ready prose | Ship it |
| A | >=8 | Strong draft | Ship it |
| B+ | >=7 | Good draft, targeted fixes | One editing pass |
| B | >=6.5 | Good draft, targeted fixes | One editing pass |
| B- | >=5.5 | Noticeable issues | Focused revision |
| C+ | >=4.5 | Noticeable issues | Focused revision |
| C | >=4.0 | Reviewer will complain about clarity | Significant revision |
| D | >=3.0 | Comprehension barriers | Major rewrite |
| F | <3.0 | Not ready for review | Start over on prose |

### Step 5: Generate Report

```markdown
## Writing Quality Report

**File**: {filename}
**Format**: {paper/blog/markdown}
**Words**: {N} | **Sentences**: {N} | **Paragraphs**: {N}
**Overall Grade**: {A-F}

### Dimension Scores

| Dimension | Score | Key Metric | Status |
|-----------|-------|------------|--------|
| Accessibility | {N}/10 | FK grade {X}, avg sentence {Y}w | {OK/WARN/FAIL} |
| Clarity | {N}/10 | {X}% passive, {Y} hedges/100w | {OK/WARN/FAIL} |
| Flow | {N}/10 | CV {X}, monotony {Y} | {OK/WARN/FAIL} |
| Precision | {N}/10 | {LLM summary} | {OK/WARN/FAIL} |

### Top 3 Issues (Highest Impact)

1. **{Issue name}** ({Dimension}, severity {X}/10)
   - **Where**: {section/paragraph reference}
   - **Metric**: {concrete number}
   - **Example**: "{problematic text excerpt}"
   - **Fix direction**: {what to change}
   - **Remediation**: `/writing-diagnosis` or `/editorial-brain`

2. ...
3. ...

### Section Breakdown

| Section | Access. | Clarity | Flow | FK Grade | Passive% | Notes |
|---------|---------|---------|------|----------|----------|-------|
| Abstract | {N} | {N} | {N} | {X} | {Y}% | {one-line} |
| Introduction | ... | ... | ... | ... | ... | ... |
...

### Detailed Metrics

#### Accessibility
- Flesch-Kincaid grade: {X} (section target: {Y})
- Average sentence length: {X} words
- Sentences >40 words: {N} (list top 3)
- Jargon density: {X} per paragraph

#### Clarity
- Passive voice: {X}% of sentences
  - Worst: {list 3 examples}
- Hedge density: {X} per 100 words
- Filler words: {X} per 100 words
  - Inventory: {word: count, ...}
- Weak openers: {N} instances

#### Flow
- Sentence length CV: {X}
- Monotony score: {X}
- Distribution: {X}% short / {Y}% medium / {Z}% long
- Paragraph length: avg {X}w (SD {Y})

#### Precision (Semantic)
- Buried ledes: {N} paragraphs ({list})
- Terminology inconsistencies: {list}
- Unsupported claims: {list}
- Weak transitions: {list}
- Vague citations: {list}

### Next Steps

- **Score improvement**: Run `/writing-diagnosis` on flagged paragraphs
- **Structural issues**: Run `/editorial-brain` in {recommended} mode
- **Argument gaps**: Run `/argument-autopsy` on flagged claims
- **Audience fit**: Run `/audience-checker` with reviewer persona
```

## Quick Mode Output

```markdown
## Writing Quality: Quick Check

**Grade**: {A-F} (script-only) | A:{N} C:{N} F:{N}

| Metric | Value | Target | |
|--------|-------|--------|-|
| FK grade | {X} | 12-16 | ✓/! |
| Passive % | {X} | <25% | ✓/! |
| Avg sentence | {X}w | 15-25 | ✓/! |
| Hedges/100w | {X} | <1.0 | ✓/! |
| Fillers/100w | {X} | <0.6 | ✓/! |
| Monotony | {X} | <0.4 | ✓/! |
| Long sentences | {N} | 0 | ✓/! |

**Worst issues**: {top 3 failing metrics}
Run `/writing-verify` for full semantic analysis.
```

## Incremental Mode

When user says "re-check", "check improvement", or provides text previously analyzed:
1. Run script for new metrics.
2. If a previous report exists in the conversation, show deltas:

```markdown
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Passive % | 31% | 22% | -9% ✓ |
...

**Grade**: C+ → B (improved)
**Fixed**: {issues resolved}
**Still open**: {issues remaining}
```

## Edge Cases

- **Short input (<100 words)**: Warn that metrics may be unreliable; still compute.
- **No sections detected**: Treat entire text as one section `_default`.
- **Script fails**: Report the error verbatim and suggest checking the file path and format.
- **Non-English input**: Warn that all metrics are calibrated for English scientific prose.

## Integration

This skill is the entry point of an editorial workflow:

```
writing-verify (score + identify)
    ├── /writing-diagnosis    (deep pattern analysis)
    ├── /editorial-brain      (phase-appropriate editing)
    ├── /argument-autopsy     (claim-evidence verification)
    ├── /audience-checker     (accessibility with persona)
    └── /voice-drift-detector (cross-section consistency)
```
