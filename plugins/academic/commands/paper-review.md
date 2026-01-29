---
name: paper-review
description: Generate critical reviews of ML paper drafts simulating a skeptical reviewer. Use when asked to "review my paper", "find weaknesses", "critique this draft", "what would reviewers say", or "assess my submission". Provides harsh but constructive feedback to strengthen the paper before submission.
model: sonnet
---

# Critical Paper Review

Simulate a skeptical ML conference reviewer (NeurIPS, ICML, ICLR) to identify weaknesses before submission. This skill adopts a deliberately critical stance to surface issues reviewers will find.

## Workflow

1. **Read the complete paper**: Read all LaTeX files thoroughly
2. **Assess each section**: Evaluate against reviewer criteria
3. **Identify weaknesses**: Find technical, experimental, and presentation issues
4. **Generate review**: Produce a realistic conference review
5. **Prioritize fixes**: Rank issues by severity and fixability

## Review Output Format

```markdown
## Summary
[2-3 sentence summary of what the paper claims to contribute]

## Strengths
- S1: [Strength with specific reference]
- S2: [Strength]
- S3: [Strength]

## Weaknesses
- W1: [MAJOR] [Weakness with specific reference]
- W2: [MAJOR] [Weakness]
- W3: [MINOR] [Weakness]
- W4: [MINOR] [Weakness]

## Questions for Authors
- Q1: [Clarification question]
- Q2: [Question about claims]
- Q3: [Question about experiments]

## Detailed Comments

### Technical Soundness
[Detailed assessment]

### Experimental Evaluation
[Detailed assessment]

### Clarity and Presentation
[Detailed assessment]

### Novelty and Significance
[Detailed assessment]

## Recommendation
[Score justification: Accept / Weak Accept / Borderline / Weak Reject / Reject]

## Actionable Fixes (Prioritized)
1. [Highest priority fix - blocks acceptance]
2. [High priority fix]
3. [Medium priority fix]
...
```

## Evaluation Criteria

### 1. Technical Soundness (Weight: High)

Check for:
- **Correctness**: Are proofs valid? Are algorithms correct?
- **Assumptions**: Are assumptions stated? Are they reasonable?
- **Theoretical claims**: Do they follow from the analysis?
- **Mathematical notation**: Is it consistent and well-defined?

Red flags:
```
- Undefined notation (symbols appear without definition)
- Hand-wavy proofs ("it can be shown that...")
- Missing assumptions that the proof relies on
- Circular reasoning
- Overclaimed theoretical results
```

### 2. Experimental Evaluation (Weight: High)

Check for:
- **Baselines**: Are appropriate baselines included? State-of-the-art?
- **Datasets**: Are they appropriate for the claims? Diverse enough?
- **Metrics**: Do metrics match the claims? Are they standard?
- **Statistical rigor**: Error bars? Multiple seeds? Significance tests?
- **Ablations**: Are claims about components validated?
- **Hyperparameters**: Fair comparison? Tuning procedure disclosed?
- **Reproducibility**: Enough detail to reproduce?

Red flags:
```
- Missing obvious baselines
- Weak baselines only ("compared to random")
- No error bars on stochastic results
- Cherry-picked datasets
- Unfair hyperparameter tuning
- Missing ablations for key claims
- Reproducibility concerns (no code, missing details)
```

### 3. Novelty and Significance (Weight: Medium-High)

Check for:
- **Novelty**: What is genuinely new vs. incremental combination?
- **Significance**: Does this advance the field meaningfully?
- **Applicability**: Will others use/build on this?

Red flags:
```
- Incremental modification of existing method
- Limited to narrow/synthetic settings
- Results don't substantially advance state-of-the-art
- Similar concurrent/prior work not cited
```

### 4. Clarity and Presentation (Weight: Medium)

Check for:
- **Writing quality**: Clear, concise, well-organized?
- **Motivation**: Is the problem well-motivated?
- **Contribution clarity**: Are contributions specific and verifiable?
- **Figure quality**: Informative? Readable?
- **Related work**: Comprehensive? Fair comparison?

Red flags:
```
- Dense, hard-to-follow writing
- Missing related work
- Unfair characterization of prior work
- Vague contributions ("novel method for X")
- Figures that don't convey information
- Notation inconsistencies
```

## Skeptical Reviewer Mindset

Ask these questions while reading:

### Claims vs. Evidence
- "Where is the evidence for this claim?"
- "Does the experiment actually test this hypothesis?"
- "Could an alternative explanation account for these results?"
- "Is this correlation or causation?"

### Methodology
- "What assumptions does this require?"
- "Would this work in realistic settings?"
- "Why this approach over simpler alternatives?"
- "What happens when assumption X is violated?"

### Experiments
- "Why these datasets and not others?"
- "Why is baseline X missing?"
- "Are the improvements statistically significant?"
- "How sensitive is this to hyperparameters?"

### Novelty
- "How is this different from [prior work]?"
- "Is this a principled advance or engineering?"
- "Will anyone use this in a year?"

## Common Weakness Patterns

### Technical
- Theorem statement doesn't match proof
- Assumptions too strong for practical use
- Algorithm complexity not analyzed
- Convergence not guaranteed
- Edge cases not handled

### Experimental
- Evaluation on toy/synthetic data only
- Missing comparison to [obvious baseline]
- No ablation for [key component]
- Hyperparameters tuned on test set
- Single random seed
- Metrics don't match claims

### Presentation
- Contribution X not supported in experiments
- Section Y unnecessarily long/short
- Related work missing [important paper]
- Notation undefined: [symbol]
- Figure X unreadable at print size

### Significance
- Improvement marginal (within error bars)
- Limited practical applicability
- Similar to [concurrent/prior work]
- Solves artificial problem

## Calibration Notes

Match severity to venue expectations:

**MAJOR (blocks acceptance)**
- Incorrect proofs/algorithms
- Missing critical baselines
- Claims unsupported by experiments
- Fundamental methodological flaws

**MINOR (should be fixed)**
- Missing ablations
- Presentation issues
- Minor experimental gaps
- Clarity problems

**NITPICK (nice to fix)**
- Typos
- Minor notation issues
- Additional experiments that would help

## Review Generation Guidelines

1. **Be specific**: Reference exact sections, equations, figures
2. **Be constructive**: Suggest fixes, not just problems
3. **Be fair**: Acknowledge strengths genuinely
4. **Be thorough**: Check every section systematically
5. **Be realistic**: Match the tone of actual reviews

## Output

Generate:
1. A complete review in the format above
2. A prioritized list of actionable fixes
3. Estimated effort for each fix (quick fix / moderate / significant rework)
4. Assessment of whether issues are addressable before deadline
