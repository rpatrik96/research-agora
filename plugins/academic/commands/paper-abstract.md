---
name: paper-abstract
description: |
  Write or improve abstracts for ML conference papers. Use when asked to
  "write abstract", "improve abstract", "draft abstract", "summarize paper",
  or "abstract for submission". Structures context, problem, approach, results, and impact.
model: sonnet
---

# Abstract Writing

Generate compelling abstracts for ML conference papers (NeurIPS, ICML, ICLR, AAAI) that capture the essence of the work and attract readers.

## Workflow

1. **Read the paper**: Understand contributions, methods, and key results
2. **Identify the core message**: What is the single most important takeaway?
3. **Extract key results**: Find specific, quantitative claims
4. **Draft the abstract**: Follow the 5-part structure
5. **Compress and refine**: Ensure every word earns its place
6. **Verify claims**: Check that all statements are supported in the paper

## Before Writing

Read these sections to understand the paper:
- Introduction - Problem statement and contributions
- Methods - Core approach and key innovations
- Experiments - Main results and comparisons
- Conclusion - Takeaways and impact

## Abstract Structure (5-Part Model)

The abstract should flow through these components in ~150-300 words:

```latex
\begin{abstract}
% === PART 1: Context & Motivation (1-2 sentences) ===
% Why does this problem matter? Set the stage.
[Area] is important for [reason], but current methods [limitation].

% === PART 2: Problem Statement (1 sentence) ===
% What specific gap/challenge does this work address?
A key challenge is [problem], which [consequence].

% === PART 3: Approach (2-3 sentences) ===
% What do you propose? What is the key insight?
We propose [method name], a [brief description] that [key property].
Our approach [key mechanism/insight].
Unlike prior work, [method] achieves [advantage] by [how].

% === PART 4: Results (2-3 sentences) ===
% Specific, quantitative outcomes
Experiments on [benchmarks] demonstrate that [method] achieves [result],
outperforming [baselines] by [specific margin].
We also show [secondary finding] and [ablation insight].

% === PART 5: Impact/Implications (1 sentence, optional) ===
% Broader significance or released artifacts
[Method] enables [new capability] / Our code is available at [url].
\end{abstract}
```

## Word Count Guidelines

| Venue | Typical Limit | Recommended |
|-------|--------------|-------------|
| NeurIPS | No strict limit | 150-200 words |
| ICML | No strict limit | 150-200 words |
| ICLR | No strict limit | 150-250 words |
| AAAI | 150 words | 140-150 words |
| CVPR | 200 words | 180-200 words |
| ACL | 200 words | 180-200 words |

## Writing Principles

### Every Word Must Earn Its Place

```latex
% Bad - verbose
In this paper, we propose and present a novel method called X that is designed
to address the challenging problem of Y.

% Good - direct
We propose X, a method for Y that [key property].
```

### Be Specific, Not Vague

```latex
% Bad - vague
Our method significantly outperforms baselines on multiple benchmarks.

% Good - specific
X achieves 92.3% accuracy on ImageNet, outperforming the best baseline by 2.1%.
```

### Lead with Impact, Not Process

```latex
% Bad - process-focused
We train a neural network on dataset X and evaluate on dataset Y.

% Good - impact-focused
We demonstrate that [insight], achieving state-of-the-art results on [task].
```

### Avoid Jargon and Acronyms

```latex
% Bad - acronym soup
We propose using CLIP embeddings with LoRA fine-tuning and DPO alignment.

% Good - accessible
We propose using vision-language embeddings with parameter-efficient fine-tuning.
```

## Strong Opening Patterns

```latex
% Problem urgency
Despite advances in [area], [challenge] remains a fundamental obstacle.

% Practical importance
As [systems] are increasingly deployed in [context], [property] becomes critical.

% Gap identification
While [existing approaches] excel at [X], they fail to [Y].

% Surprising observation
We discover that [counterintuitive finding], which enables [new approach].

% Direct statement
We present [method], a [description] for [task].
```

## Result Presentation Patterns

```latex
% Comparative improvement
[Method] outperforms [best baseline] by [X%] on [benchmark] while
reducing [cost] by [Y%].

% State-of-the-art claim
Experiments demonstrate state-of-the-art results on [benchmark],
achieving [specific result].

% Multiple benchmarks
Across [N] benchmarks, [method] consistently achieves [outcome],
with improvements of [range].

% Efficiency gain
[Method] achieves comparable performance to [baseline] while
requiring [fraction] of the [computation/data/parameters].

% Novel capability
Unlike prior methods, [approach] enables [new capability] without
requiring [removed limitation].
```

## Abstract Templates

### Template 1: Method Paper

```latex
\begin{abstract}
[Problem area] is crucial for [application], yet existing methods
[limitation]. We propose [Method], a [description] that [key property].
Our key insight is [observation], which allows us to [capability].
[Method] consists of [brief technical description]. Experiments on
[benchmarks] show that [Method] achieves [result], outperforming
[baselines] by [margin]. We further demonstrate [secondary finding]
through [analysis type]. Code is available at [url].
\end{abstract}
```

### Template 2: Analysis/Understanding Paper

```latex
\begin{abstract}
Understanding [phenomenon] is essential for [reason]. In this work,
we provide a [comprehensive/systematic] analysis of [subject]. We
discover that [key finding 1], and show that [key finding 2].
Our analysis reveals [insight], suggesting that [implication].
We validate our findings on [benchmarks/settings], demonstrating
[practical consequence]. These insights [impact statement].
\end{abstract}
```

### Template 3: Theory Paper

```latex
\begin{abstract}
We study [problem] in [setting]. Prior work [limitation of existing
theory]. We prove that [main result], providing the first [type of
guarantee] for [setting]. Our proof introduces [technique], which
may be of independent interest. We complement our theory with
experiments showing [empirical finding]. Our results imply [practical
implication].
\end{abstract}
```

### Template 4: Application Paper

```latex
\begin{abstract}
[Application domain] presents unique challenges including [challenge 1]
and [challenge 2]. We introduce [System/Method], a [description] for
[task]. [System] combines [components] to enable [capability].
On [benchmark/real-world data], [System] achieves [result],
representing [improvement] over [prior solutions]. We deploy [System]
in [real-world context], demonstrating [practical impact].
\end{abstract}
```

## Common Mistakes to Avoid

1. **Too vague**: "We achieve good results" → Give specific numbers
2. **Too detailed**: Don't explain the full method architecture
3. **Missing problem**: Jumping straight to the solution
4. **No results**: Abstract must include quantitative outcomes
5. **Jargon overload**: Should be readable by non-experts in subfield
6. **Passive voice excess**: "It is shown that" → "We show that"
7. **Overclaiming**: "Revolutionary breakthrough" → Let reviewers judge
8. **Missing comparison**: Results without baselines are meaningless
9. **Acronyms without definition**: Define once or avoid entirely
10. **Future tense**: "We will show" → "We show" (it's done)

## Improvement Checklist

When improving an existing abstract, verify:

- [ ] **First sentence hooks the reader** with clear motivation
- [ ] **Problem is explicitly stated** before the solution
- [ ] **Method name and description** are clear and concise
- [ ] **Key insight/novelty** is articulated
- [ ] **Quantitative results** with specific numbers
- [ ] **Comparison to baselines** is included
- [ ] **No unnecessary words** (every word earns its place)
- [ ] **Accessible to ML generalist** (minimal subfield jargon)
- [ ] **All claims are verifiable** in the paper
- [ ] **Word count is appropriate** for the venue

## Compression Techniques

When the abstract is too long:

```latex
% Combine sentences
% Before (2 sentences, 24 words):
Our method achieves 92% accuracy. This outperforms the best baseline by 3%.
% After (1 sentence, 13 words):
Our method achieves 92% accuracy, outperforming the best baseline by 3%.

% Remove hedging
% Before:
Our results seem to suggest that the proposed method might be effective.
% After:
Our method is effective.

% Cut redundancy
% Before:
We propose a novel new method that has not been explored before.
% After:
We propose [method].

% Merge context and problem
% Before:
X is important. However, current methods fail at Y.
% After:
While X is important, current methods fail at Y.
```

## Output Format

When asked to write or improve an abstract, provide:

### 1. The Abstract

```latex
\begin{abstract}
[Complete abstract text]
\end{abstract}
```

### 2. Word Count

```
Word count: [N] words
```

### 3. Verification Notes (if improving)

```markdown
## Changes Made
- [Change 1]: [Reason]
- [Change 2]: [Reason]

## Claims to Verify
- "[Claim]" - check [section] for support
```

### 4. Alternative Openings (optional)

```markdown
## Alternative Openings
1. [Different hook approach]
2. [Different hook approach]
```
