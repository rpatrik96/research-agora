---
name: paper-rebuttal
description: Write rebuttals to reviewer comments for ML conference submissions. Use when asked to "write rebuttal", "respond to reviewers", "address feedback", "draft response", or "handle reviews". Generates professional, persuasive responses that address concerns constructively.
model: sonnet
---

# Rebuttal Writing

> **LLM-required**: Crafting rebuttals requires understanding reviewer concerns and composing persuasive arguments. No script alternative.

Generate effective rebuttals for ML conference submissions (NeurIPS, ICML, ICLR).

## Workflow

1. **Collect inputs**: Read the original paper and all reviewer comments
2. **Categorize concerns**: Group by type (misunderstanding, valid criticism, request for experiments)
3. **Prioritize**: Focus on major concerns and score-affecting issues
4. **Draft responses**: Write concise, professional responses
5. **Plan revisions**: Note what will be added to the paper

## Input Required

Before drafting, I need:
1. **Reviewer comments**: Paste or point to a file containing all reviews
2. **Original paper**: Path to the LaTeX files
3. **Word/page limit**: Rebuttals typically have strict limits
4. **Time for new experiments**: Can you run additional experiments?

## Rebuttal Structure

```markdown
We thank the reviewers for their constructive feedback. We address each concern below.

---

## Response to Reviewer 1 (R1)

**[W1: Concern about X]**

[Response addressing the concern directly]

**[W2: Missing baseline Y]**

[Response with results if available]

| Method | Metric 1 | Metric 2 |
|--------|----------|----------|
| Y (requested) | 0.XX | 0.XX |
| Ours | **0.XX** | **0.XX** |

---

## Response to Reviewer 2 (R2)

...

---

## Common Concerns Across Reviewers

**[If multiple reviewers raised the same issue]**

[Unified response addressing the shared concern]

---

## Summary of Revisions

We will incorporate the following changes in the camera-ready:
1. [Change 1]
2. [Change 2]
3. [Change 3]
```

## Response Strategy by Concern Type

### 1. Misunderstanding of the Paper

**Goal**: Clarify without being condescending

```markdown
**R1-W1: "The method assumes X, which is unrealistic"**

We apologize for the confusion. Our method does *not* assume X.
As stated in Section 3.2 (Line 145): "[direct quote]". We will
clarify this in the revision by [specific change].
```

**Tips**:
- Quote the paper directly
- Acknowledge that the writing could be clearer
- Commit to improving clarity

### 2. Missing Baselines/Experiments

**Goal**: Provide results if possible, explain if not

```markdown
**R2-W2: "Comparison with [Baseline] is missing"**

Thank you for this suggestion. We have now run [Baseline]:

| Method | Accuracy | F1 |
|--------|----------|-----|
| [Baseline] | 82.3 | 79.1 |
| Ours | **87.5** | **84.2** |

Our method outperforms [Baseline] by 5.2% on accuracy. We will
add this comparison to Table 2.
```

```markdown
**R2-W3: "Experiments on [Dataset] would strengthen the paper"**

We agree this would be valuable. Unfortunately, [Dataset] requires
[resource/access we don't have]. However, [Alternative dataset]
tests the same property, and our results in Table 3 show [finding].
We will add a discussion of this in the revision.
```

### 3. Technical Concerns

**Goal**: Address directly, admit limitations honestly

```markdown
**R1-W3: "The proof of Theorem 1 seems to require assumption Y"**

The reviewer is correct that assumption Y is needed. We have added
it explicitly to Theorem 1 (see revised statement below). This
assumption is standard in [area] and holds in [common cases].

**Revised Theorem 1**: Under assumptions X and Y, [statement].
```

```markdown
**R3-W1: "Convergence is not guaranteed for non-convex cases"**

We agree that our theoretical analysis is limited to convex settings.
However, our experiments in Section 5 demonstrate empirical convergence
across all tested non-convex problems (see Figure 3). We will
acknowledge this gap between theory and practice in the revision.
```

### 4. Significance/Novelty Concerns

**Goal**: Highlight the key differences and impact

```markdown
**R2-W1: "The contribution seems incremental over [Prior Work]"**

We respectfully disagree. While we build on [Prior Work], our
contribution is distinct in three ways:

1. **[Key difference 1]**: [Prior Work] requires [X], while we [Y].
2. **[Key difference 2]**: Our method achieves [improvement] which
   [Prior Work] cannot due to [reason].
3. **[Key difference 3]**: We provide [theoretical/practical contribution]
   not present in [Prior Work].

These differences enable [new capability], as demonstrated in
Section 5.2.
```

### 5. Presentation Issues

**Goal**: Acknowledge and commit to fixing

```markdown
**R3-W2: "Section 4 is hard to follow"**

We appreciate this feedback. We will restructure Section 4 to:
1. Add an overview paragraph at the start
2. Include a figure illustrating the key steps
3. Move technical details to the appendix

We have attached a revised outline in the supplementary material.
```

## Tone Guidelines

### Do
- **Be professional**: "We thank the reviewer for this observation"
- **Be direct**: Address the concern in the first sentence
- **Be specific**: Reference sections, equations, line numbers
- **Be concise**: Respect word limits
- **Be honest**: Admit valid limitations
- **Be constructive**: Show how you'll improve the paper

### Don't
- **Don't be defensive**: "The reviewer clearly didn't read..."
- **Don't be dismissive**: "This is a minor point"
- **Don't argue without evidence**: Back up claims with data
- **Don't ignore concerns**: Address everything, even briefly
- **Don't over-promise**: Only commit to feasible revisions
- **Don't be sycophantic**: Excessive praise wastes word count

## Persuasion Techniques

### Reframing
```markdown
**R1: "The method is limited to [setting]"**

While our theoretical analysis focuses on [setting], we note that:
1. [Setting] covers many practical applications including [examples]
2. Our experiments show the method works empirically beyond this
   (see Appendix B for [broader setting] results)
```

### Providing Evidence
```markdown
**R2: "The improvements seem marginal"**

The improvements are statistically significant (p < 0.01, paired
t-test over 10 seeds). Moreover, the 2.3% improvement in [metric]
translates to [practical impact]. For context, the gap between
the previous SOTA and their predecessor was 1.8%.
```

### Acknowledging + Pivoting
```markdown
**R3: "Missing comparison with [Method X]"**

We agree [Method X] is relevant. While we couldn't obtain their
code/reproduce their results, we compare against [Method Y], which
the [Method X] authors show is equivalent in [setting] (see their
Table 2). Against [Method Y], we achieve [improvement].
```

## Formatting for Impact

### Tables for New Results
```markdown
| Method | Metric 1 | Metric 2 | Metric 3 |
|--------|:--------:|:--------:|:--------:|
| Requested Baseline | 0.82 | 0.79 | 0.85 |
| Ours | **0.87** | **0.84** | **0.91** |
```

### Bullet Points for Multiple Items
```markdown
Our method differs from [Prior Work] in:
• **Architecture**: We use [X] vs their [Y]
• **Training**: We optimize [objective] vs [their objective]
• **Scope**: We handle [setting] which they cannot
```

### Emphasis for Key Points
```markdown
**Key point**: The reviewer's concern about X is addressed by Y.
```

## Word Count Management

Typical limits: 500-1000 words for main response

**Priority allocation**:
1. Major concerns from lowest-scoring reviewer (40%)
2. Concerns shared by multiple reviewers (25%)
3. Easy wins with new experiments (20%)
4. Minor clarifications (10%)
5. Thank you / summary of changes (5%)

**Word-saving techniques**:
- Use tables instead of prose for results
- Reference paper sections instead of re-explaining
- Group similar concerns together
- Skip obvious misunderstandings if space is tight

## Output Format

Generate:
1. A complete rebuttal ready for submission
2. A checklist of committed revisions
3. Assessment of likelihood that each concern is addressed satisfactorily
4. Suggested follow-up if reviewers respond (for venues with discussion)
