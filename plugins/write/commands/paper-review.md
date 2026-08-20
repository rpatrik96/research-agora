---
name: paper-review
description: Generate critical reviews of ML paper drafts simulating a skeptical reviewer. Use when asked to "review my paper", "find weaknesses", "critique this draft", "what would reviewers say", "audit my contributions", "check my limitations section", or "assess my submission". Audits contribution claims against the evidence and limitations against the categories reviewers check, then provides harsh but constructive feedback to strengthen the paper before submission.
model: sonnet
disable-model-invocation: true
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: review
  verification-level: layered
---

# Critical Paper Review

> **LLM-required**: Reviewing papers requires critical analysis and nuanced judgment. No script alternative.

Simulate a skeptical ML conference reviewer (NeurIPS, ICML, ICLR) to identify weaknesses before submission. This skill adopts a deliberately critical stance to surface issues reviewers will find.

## Workflow

1. **Compute missing error bars**: Run the scripted first pass below
2. **Read the complete paper**: Read all LaTeX files thoroughly
3. **Assess each section**: Evaluate against reviewer criteria
4. **Identify weaknesses**: Find technical, experimental, and presentation issues
5. **Generate review**: Produce a realistic conference review
6. **Prioritize fixes**: Rank issues by severity and fixability

### Scripted First Pass

Run from the repository root after generating `research-state.json`:

```bash
python3 - <<'PY'
import json
from pathlib import Path

state = json.loads(Path("research-state.json").read_text())
missing = [
    {
        "id": table["id"],
        "label": table.get("label"),
        "caption": table.get("caption", ""),
        "section": table.get("section", ""),
    }
    for table in state["structure"]["tables"]
    if table["has_error_bars"] is False
]
print(json.dumps({"tables_missing_error_bars": missing}, indent=2))
PY
```

Treat each reported table as the "no error bars on stochastic results" red
flag. The finding comes from
`structure.tables[].has_error_bars == false`; judge whether the table contains
stochastic results from the paper's experimental context.

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
- No error bars on stochastic results (computed from `structure.tables[].has_error_bars == false`)
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

## Contribution-Claim Audit

Read the contribution list against what the paper actually establishes, one claim at a time. A reviewer's sharpest objection is almost always that a contribution overshoots its evidence.

A contribution holds up when it is **specific** ("We prove convergence in $\mathcal{O}(1/\sqrt{T})$ iterations"), **verifiable** against something in the paper, **novel** in a way that survives comparison to prior work, and **significant** enough to address a real limitation.

Flag it when it is:

| Failure | Looks like | What to write |
|---|---|---|
| Vague | "We propose a novel method" | Ask which property is novel and where it is shown |
| Overclaimed | "We solve the problem of X" when the paper improves on X | Name the gap between the verb and the results table |
| Unverifiable | "Our method is more intuitive" | Ask what measurement would settle it |
| Trivial | "We apply X to Y" | Ask what was non-obvious about the application |
| Mismatched | A claim with no corresponding experiment or theorem | Point at the missing section |

Check the framing around the contributions too. **Strawman prior work** — representing an existing approach as weaker than it is — is the failure a reviewer who authored that prior work will catch first. **Overselling** ("revolutionary", "paradigm shift") reads as a substitute for evidence and costs the paper credibility it will need later.

## Limitations Audit

A limitations section is judged on candour and specificity, not on length. Work the categories below and name what is missing, since reviewers penalise the omission far more than the admission.

**Methodological** — assumptions (distributional, structural, independence), computational complexity and scalability, hyperparameter sensitivity, theoretical gaps in convergence or optimality, approximations made.
**Experimental** — dataset size, diversity and representativeness, the synthetic-versus-real gap, missing baselines or ablations, narrow metrics, reproducibility under randomness and compute cost.
**Scope** — domain and task specificity, input modality constraints, uncharacterised failure modes, unknown generalization bounds.
**Broader impact** — misuse potential, fairness and bias, environmental cost, dual use.

Two failure modes deserve their own flag. The first is the **generic disclaimer**: "more experiments needed", "has some assumptions". A real limitation names the binding assumption, the dataset, and the magnitude — "assumes i.i.d. data", not "has some assumptions" — and the section leads with the one that most constrains the result. The second is **defensive framing** ("despite these minor issues…"), which signals to a reviewer that the author knows the limitation bites.

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
