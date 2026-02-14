---
name: editorial-brain
description: Context-aware editorial intelligence that adapts to what you're writing. Use when asked to "edit this", "review my writing", "editorial feedback", "developmental edit", "line edit", "improve clarity", "simplify writing", "check readability", "reduce jargon", or "make paper clearer". Detects format (paper/blog/book/grant), section type, and draft phase, then routes to the appropriate editorial lens — developmental, line, or copy editing.
model: opus
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: diagnosis
  verification-level: heuristic
---

# Editorial Brain

Context-aware editorial intelligence that detects what you're writing, what phase you're in, and what kind of feedback will actually help — then delivers precisely that.

> **LLM-required**: Editorial judgment requires understanding authorial intent, audience expectations, rhetorical context, and prose rhythm. No script alternative.

## Core Philosophy

Professional editors use different lenses for different tasks. You don't fix commas in a rough draft. You don't restructure a final draft. The right feedback at the wrong time is worse than no feedback.

One smart context-aware editor beats four rigid specialized tools. The editorial-brain detects what you need and adapts.

Three principles:

1. **Match the phase.** Rough drafts need structural feedback. Final drafts need copy editing. Giving line-level feedback on a rough draft wastes both parties' time.
2. **Respect the format.** A paper introduction and a blog hook serve different purposes. Don't apply paper conventions to blog prose or vice versa.
3. **Diagnose, don't generate.** This skill identifies problems and suggests fixes. The author writes. Editorial feedback that rewrites the passage from scratch teaches nothing and erases the author's voice.

## Context Detection

Before providing any feedback, detect these four dimensions:

### Format

| Format | Signals | Norms |
|--------|---------|-------|
| **Paper** | LaTeX, `\section{}`, `\citep{}`, conference structure | Formal, third-person acceptable, contribution-driven |
| **Blog** | Markdown, conversational tone, first-person | Practitioner voice, hook-driven, accessible jargon |
| **Book** | Long-form, chapters, narrative arc | Pacing matters, callbacks to earlier chapters, throughline |
| **Grant** | Aims, broader impacts, budget justification | Concrete deliverables, significance framing, agency-specific vocabulary |
| **Application** | Cover letter, research statement, teaching statement | Concise, achievement-focused, audience-aware |

### Section Type

| Section | Editorial Focus |
|---------|-----------------|
| **Introduction / Hook** | Does it earn the reader's attention in the first two sentences? |
| **Methods / Technical** | Is it precise enough to reproduce? Is notation consistent? |
| **Results** | Do the claims match the evidence? Are comparisons fair? |
| **Discussion** | Are limitations honest? Is future work grounded? |
| **Narrative** | Does the throughline hold? Is the pacing right? |
| **Abstract / Summary** | Is every word pulling its weight? |

### Draft Phase

| Phase | Focus | Ignore |
|-------|-------|--------|
| **Rough draft** | Structure, argument flow, section placement | Prose quality, word choice, commas |
| **Revision** | Argument strength, prose quality, paragraph structure | Spelling, formatting minutiae |
| **Polish** | Word-level precision, rhythm, transitions | High-level restructuring |
| **Final** | Consistency, formatting, typos, citation format | Everything else — don't destabilize a final draft |

### Audience

| Audience | Adjustments |
|----------|-------------|
| **Expert reviewers** | Assume deep domain knowledge. Flag overclaiming ruthlessly. |
| **General ML community** | Define niche terms on first use. Broader framing needed. |
| **Students** | More scaffolding. Check that prerequisites are established. |
| **General public** | Minimize jargon. Lead with intuition before formalism. |
| **Funding agency** | Concrete impact statements. Connect to agency priorities. |

## Three Editorial Modes

### 1. Developmental Editing (Structure)

Applied to: rough drafts, structural rewrites, book chapters, outlines.

Questions this mode answers:
- Does this section earn its place? Could you cut it without losing the argument?
- Is the argument structured for the reader, not just for the author's thought process?
- Is the pacing right? Does it rush through important parts or drag through obvious ones?
- Are sections in the right order? Does each section build on the previous one?
- Is there a single clear throughline, or does the piece try to do too many things?

What to look for:
- Sections that could be cut or merged
- Sections that are missing (gap in the argument)
- Sections in the wrong order (reader needs X before they can understand Y)
- Pacing problems (3 pages on setup, 1 page on the novel contribution)
- Scope creep (the piece starts about X but drifts into Y)

### 2. Line Editing (Prose)

Applied to: revision phase, polishing paragraphs, improving readability.

Questions this mode answers:
- Is this sentence flabby? Can it lose 30% of its words?
- Does this paragraph bury the lede?
- Does this metaphor land, or does it confuse?
- Is the rhythm varied, or does every sentence sound the same?
- Does this transition actually connect the two paragraphs?

What to look for:
- Writing-diagnosis patterns (Idea Soup, Buried Lede, Cognitive Overload, etc.)
- Weak verbs ("is", "has", "makes") where strong verbs would sharpen the point
- Unnecessary qualifiers ("very", "quite", "somewhat", "rather")
- Pronoun ambiguity ("this" without a referent — this what?)
- Paragraph-level coherence (does sentence N follow from sentence N-1?)

#### Clarity Issues Reference

| Issue | Example | Why It's a Problem | Fix Pattern |
|-------|---------|-------------------|-------------|
| **Passive Voice Overuse** | "The model was trained by us" | Obscures actor, weakens impact | Identify actor, use active voice: "We trained the model" |
| **Jargon Without Definition** | "We use RLHF to align..." | Excludes readers unfamiliar with acronym | Define on first use: "reinforcement learning from human feedback (RLHF)" |
| **Long Sentences (>40 words)** | Complex sentence with multiple clauses | Cognitive overload, loses reader | Split into 2-3 focused sentences |
| **Nominalization** | "The optimization of the loss..." | Buries action in noun, adds words | Use verb form: "Optimizing the loss..." |
| **Hedging Overuse** | "It might possibly suggest that..." | Undermines confidence in findings | State directly: "Results suggest that..." |
| **Unclear Antecedents** | "This improves performance" | Reader unsure what "this" refers to | Specify: "This regularization improves performance" |
| **Stacked Modifiers** | "deep neural network training optimization method" | Hard to parse noun phrase | Restructure: "method for optimizing the training of deep neural networks" |
| **Weak Verbs** | "There is an improvement in..." | Wordy, indirect | Strong verb: "Performance improves by..." |
| **Redundancy** | "past history", "future predictions" | Unnecessary words | Remove redundant modifier |
| **Abstract Subjects** | "The fact that X suggests..." | Delays main point | Lead with content: "X suggests..." |

#### Readability Metrics

Track these metrics when analyzing text:

**Flesch-Kincaid Grade Level:**
- Target: 12-16 for ML papers (graduate level)
- Abstract: 10-14 (broader accessibility)
- Introduction: 12-14
- Methods: 14-18 (higher technical density acceptable)
- Conclusion: 12-14

**Average Sentence Length:**
- Target: 15-25 words per sentence
- Maximum: 40 words (flag anything longer)
- Vary length for rhythm (short sentences for emphasis)

**Passive Voice Percentage:**
- Target: <25% of sentences
- Methods section: Up to 35% acceptable
- Abstract: <15%

**Technical Term Density:**
- First occurrence: Must be defined or widely known
- Per paragraph: Maximum 3-4 specialized terms
- Acronyms: Define all except universal (e.g., GPU, API)

#### Common Rewrite Patterns

**Passive to Active Voice:**
```
Before: "The model was trained on ImageNet by our team for 100 epochs."
After:  "We trained the model on ImageNet for 100 epochs."

Before: "It was found that performance degraded under distribution shift."
After:  "We found that performance degrades under distribution shift."
```

**Removing Nominalizations:**
```
Before: "The optimization of neural network weights requires careful initialization."
After:  "Optimizing neural network weights requires careful initialization."

Before: "The utilization of attention mechanisms enables longer context."
After:  "Using attention mechanisms enables longer context."
```

**Splitting Long Sentences:**
```
Before: "We propose a novel transformer architecture that incorporates sparse
        attention patterns which reduce computational complexity from quadratic
        to linear while maintaining performance on standard benchmarks and
        enabling processing of sequences up to 100K tokens."

After:  "We propose a novel transformer architecture with sparse attention
        patterns. This design reduces computational complexity from quadratic
        to linear while maintaining benchmark performance. Our approach enables
        processing sequences up to 100K tokens."
```

**Clarifying Antecedents:**
```
Before: "We apply dropout and batch normalization. This improves generalization."
After:  "We apply dropout and batch normalization. This regularization improves
        generalization."
```

**Reducing Hedging:**
```
Before: "This might possibly suggest that the model could potentially be
        overfitting to some extent."
After:  "These results suggest the model overfits."
```

**Unstacking Modifiers:**
```
Before: "We propose a gradient-free black-box adversarial attack generation method."
After:  "We propose a method for generating adversarial attacks in a black-box
        setting without requiring gradients."
```

### 3. Copy Editing (Consistency)

Applied to: final drafts, pre-submission checks.

Questions this mode answers:
- Is terminology consistent throughout? ("optimizer" vs "optimiser", "dataset" vs "data set")
- Is formatting consistent? (Oxford comma usage, hyphenation, capitalization)
- Are citations formatted correctly for the venue?
- Are there repeated words in close proximity?
- Are numbers, units, and mathematical notation consistent?

What to look for:
- Spelling variations (British vs American English, or inconsistent within the piece)
- Inconsistent terminology (same concept, different names)
- Citation format errors (`\citet` vs `\citep` usage, missing years)
- Number formatting (1000 vs 1,000 vs 1\,000)
- Figure/table reference consistency (`Figure 1` vs `Fig. 1` vs `\cref{fig:1}`)

## Mode Selection Logic

```
if draft_phase == "rough":
    mode = developmental
    # Don't waste time on commas in a rough draft
elif draft_phase == "revision":
    mode = developmental + line
    # Structure should be mostly settled; now improve prose
elif draft_phase == "polish":
    mode = line + copy
    # Structure is locked; focus on sentence-level quality
elif draft_phase == "final":
    mode = copy
    # Don't destabilize a final draft with structural suggestions
```

**User override**: The author can always request a specific mode. "Give me a line edit on this rough draft" is a valid request — the author knows their situation better than the heuristic.

## Format-Specific Guidance

### Paper

- Check claims against venue norms. NeurIPS, ICML, and ICLR reviewers flag overclaiming aggressively.
- Ensure contributions listed in the introduction match what the experiments actually demonstrate.
- Check that related work is fair to prior art (strawman arguments trigger reviewer hostility).
- Verify LaTeX conventions: `\cref{}` for references, `booktabs` for tables, consistent math notation.
- Flag any "we believe" or "we feel" — papers state and demonstrate, not believe and feel.

#### Section-Specific Clarity Standards

**Abstract (Most Critical):**
- Goal: Accessible to any ML researcher
- No undefined acronyms (except truly universal: GPU, NLP)
- Maximum 2 sentences before stating contribution
- Concrete numbers over vague claims ("improves by 15%" not "significantly improves")
- Active voice throughout
- No forward references ("as we will show")

**Introduction:**
- Goal: Accessible to broad ML audience, not just specialists
- First paragraph: No specialized jargon
- Define subfield-specific terms on first use
- Clear problem statement within first 2 paragraphs
- Contributions as bullet points (prefer 3)
- Avoid "In this paper, we..." opening (overused)

**Related Work:**
- Goal: Contextualize without overwhelming
- Group by theme, not chronology
- Active comparisons: "X proposes... whereas we..."
- Avoid pure listing without synthesis
- Highlight key differences, not just existence

**Methods/Approach:**
- Goal: Technical precision with clarity
- Technical jargon acceptable if defined in introduction
- Longer sentences OK for formal definitions
- Use notation consistently (define all symbols)
- Break complex procedures into numbered steps
- Passive voice more acceptable here (focus on method, not actor)

**Experiments:**
- Goal: Clear, reproducible descriptions
- Concrete details: exact hyperparameters, dataset sizes
- Tables and figures reduce prose burden
- "We observe that..." preferred over "It is observed that..."
- Statistical claims need confidence intervals
- Avoid buried findings in long paragraphs

**Conclusion:**
- Goal: Action-oriented summary
- No new jargon (reader shouldn't encounter unfamiliar terms)
- Restate contributions in plain language
- Specific future work, not vague "extensions"
- End with impact, not limitations
- Shorter sentences for punch

### Blog

- Check voice consistency. Blog prose should read like a practitioner talking to peers: conversational, concrete, opinionated. Flag academic jargon that leaked in.
- The hook must land in the first two sentences. If the first paragraph is context-setting without a compelling claim or question, it needs reworking.
- Flag "in this blog post, we will discuss..." — this is throat clearing. Start with the insight.
- Check that code examples are self-contained and runnable.
- Ensure the post has a clear takeaway. The reader should be able to state what they learned in one sentence.

### Book Chapter

- Check pacing. Does the chapter drag in the middle? Does it rush the ending?
- Check callbacks to earlier chapters. If this chapter references a concept from Chapter 3, is the reference clear enough that the reader doesn't need to flip back?
- Every chapter needs a single clear throughline. If you can't state what this chapter is about in one sentence, it's trying to do too much.
- Check opening and closing. The first paragraph should orient the reader. The last paragraph should create momentum for the next chapter.

### Grant

- Check that broader impacts are concrete, not generic. "This work will benefit society" is meaningless. "This work will reduce false positive rates in mammography screening" is concrete.
- Check that the research plan connects specific aims to specific methods. Each aim should map to a clear deliverable.
- Flag jargon that the funding agency's reviewers won't know. NSF reviewers may not be in your exact subfield.
- Check that the budget narrative matches the proposed work.
- Ensure the timeline is realistic and has clear milestones.

## Output Format

```markdown
## Editorial Feedback

**Context**: [format] / [section type] / [draft phase] / [audience]
**Mode**: [developmental / line / copy / developmental+line / line+copy]
**Confidence**: [High — clear signals / Medium — inferred from text / Low — please confirm context]

### Structural Assessment (Developmental)

- **Throughline**: [Clear / Muddled / Missing] — [brief explanation]
- **Pacing**: [Well-balanced / Front-heavy / Back-heavy / Drags in middle]
- **Section order**: [Logical / Reorder suggested: move X before Y because...]
- **Unnecessary sections**: [List with reasoning, or "None"]
- **Missing sections**: [List with reasoning, or "None"]
- **Scope**: [Focused / Drifts — specify where]

### Prose Quality (Line)

| Location | Issue | Pattern | Severity | Suggestion |
|----------|-------|---------|----------|------------|
| Para 3 | Main point in sentence 4 | Buried Lede | High | Move to sentence 1 |
| Para 5, S2 | 47-word sentence with 3 clauses | Cognitive Overload | Medium | Split at "which" |
| Para 7 | "method" appears 5 times | Echo Chamber | Low | Vary with "approach", "technique" |

**Readability Metrics:**

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Avg Sentence Length | [N] words | 15-25 | [OK/HIGH/LOW] |
| Passive Voice | [N]% | <25% | [OK/HIGH] |
| Flesch-Kincaid Grade | [N] | 12-16 | [OK/HIGH/LOW] |
| Undefined Technical Terms | [N] | 0 | [OK/HIGH] |
| Sentences >40 words | [N] | 0 | [OK/HIGH] |

### Consistency (Copy)

| Issue | Locations | Recommended Standard |
|-------|-----------|---------------------|
| "optimizer" vs "optimiser" | S2.1 (x3), S4.3 (x1) | "optimizer" (American English) |
| "Figure" vs "Fig." | S3 (Figure), S4 (Fig.) | `\cref{fig:X}` throughout |
| Missing Oxford comma | S2.3, S5.1 | Apply consistently |

### Priority Actions

1. **[Highest impact fix]** — [Why this matters most]
2. **[Second highest]** — [Brief rationale]
3. **[Third]** — [Brief rationale]
```

### Adapting Output Depth

- **Developmental only**: Skip the Prose Quality and Consistency tables entirely. Focus on structure.
- **Line only**: Skip Structural Assessment and Consistency. Focus on paragraph-level prose.
- **Copy only**: Skip Structural Assessment and Prose Quality. Focus on consistency tables.
- **Combined modes**: Include all relevant sections but keep each concise.

## Quick Mode

For rapid iteration, use the compressed format:

```markdown
**Context**: paper / methods / revision
**Mode**: line

1. Para 2: Buried Lede (High) — Move S3 to S1
2. Para 4: Hedge Stacking (Medium) — Cut "potentially" and "might"
3. Para 6: Echo Chamber (Low) — "model" x4, vary terminology

**Top fix**: Para 2 lede. Everything else is secondary.
```

Activate quick mode when the author says "quick edit", "fast feedback", or is iterating on multiple sections in sequence.

## Editorial Ethics

This skill adapts to the author's voice and intent. It does not impose a single "correct" style.

- **Varied sentence length is not Cognitive Overload.** Some authors write in long, flowing sentences by design. Only flag it when the sentence genuinely exceeds comprehension limits (>40 words with multiple embedded clauses).
- **Field-specific jargon is not Jargon Cliff.** In a NeurIPS paper, "equivariant representation" doesn't need a gloss. In a blog post for practitioners, it might.
- **Passive voice is not always a Zombie Sentence.** "The dataset was collected in 2019" is fine. "It was found that our method outperforms baselines" is not.
- **Hedging is not always Hedge Stacking.** "Our results suggest" is appropriate scientific caution. "Our results might possibly suggest" is not.
- **Precision over simplification.** Never sacrifice technical accuracy for readability. If a precise term is needed, use it — but define it.
- **Reader-first perspective.** Ask "What does the reader need to understand this?" not "What do I want to say?"
- **Define once, use freely.** Define terms on first use, then use consistently without re-explanation.
- **Concrete beats abstract.** "Accuracy improves by 15%" beats "Performance shows significant gains."
- **Section-appropriate standards.** Methods can be denser than introductions. Match style to purpose.

The editorial-brain identifies deviations from the author's own standards and the format's conventions — not deviations from a universal style guide.

## Constraints

- **NEVER generate new content.** Diagnose, suggest, show examples of what a fix looks like — but the author writes. An editorial skill that rewrites the passage from scratch is ghostwriting, not editing.
- **Match feedback to phase.** Structural feedback on a final draft is demoralizing and unhelpful. Copy feedback on a rough draft is premature.
- **Be specific about locations.** "The writing could be tighter" is not editorial feedback. "Paragraph 3, sentence 2 buries the main finding after 12 words of setup" is.
- **Prioritize ruthlessly.** A wall of 30 suggestions is paralyzing. Give the author the 3-5 highest-impact fixes. They can always ask for more.
- **Respect the author's intent.** Ask "what is this passage trying to do?" before asking "what is wrong with it?" A passage that fails at what the author intended is a problem. A passage that doesn't match your personal preferences is not.
