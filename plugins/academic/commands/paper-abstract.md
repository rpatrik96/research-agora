---
name: paper-abstract
description: |
  Diagnose abstracts for ML conference papers against structure, venue word
  limits, specificity, and claim support. Use when asked to "audit my abstract",
  "diagnose abstract", "check my abstract", "review my abstract", "is my
  abstract too long", or "abstract feedback". Scores the five-part structure,
  flags vague or unsupported claims, and returns prioritized fixes. It does not
  write abstracts.
model: sonnet
disable-model-invocation: true
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: diagnosis
  verification-level: heuristic
---

# Abstract Diagnosis

> **LLM-required**: Diagnosing an abstract requires reading it against the paper it summarizes. No script alternative.

Audit an existing abstract for an ML conference paper (NeurIPS, ICML, ICLR, AAAI) and return what to fix, ranked. **This skill diagnoses; it does not write.** The abstract is where a paper stakes its claims, and a claim you did not write is a claim you have not checked — so the author writes, and this skill tells them where it breaks.

Ask for the abstract and the target venue. If the paper draft is available, read it too: half the useful findings come from claims the abstract makes that the paper does not support.

## Workflow

Work the abstract systematically rather than reacting to whatever stands out first.

### Diagnostic Checklist

1. **Structure Check**: Map the abstract to the 5-part model
   - **Context & Motivation**: Is the problem area introduced? Is motivation clear?
   - **Problem Statement**: Is the specific gap/challenge articulated?
   - **Approach**: Is the method described with key insight/novelty?
   - **Results**: Are quantitative, specific outcomes provided?
   - **Impact/Implications**: Is broader significance or impact stated?

2. **Word Count**: Compare against venue limits (AAAI: 150w, CVPR/ACL: 200w, others: flexible)

3. **Common Mistakes Scan**: Check for:
   - Vague claims ("significantly", "good results") instead of specific numbers
   - Missing problem statement (jumping to solution)
   - Missing quantitative results
   - Jargon overload (inaccessible to ML generalist)
   - Passive voice excess
   - Overclaiming ("revolutionary", "breakthrough")
   - Missing baseline comparison
   - Undefined acronyms
   - Future tense instead of present

4. **Specificity Check**: Are claims concrete?
   - ✅ "improves by 15%" / "achieves 92.3% accuracy"
   - ❌ "significantly improves" / "achieves high accuracy"

5. **Claim-Evidence Alignment**: Are claims verifiable?
   - Can each claim be traced to a table, figure, or section in the paper?
   - Are comparisons specific enough to verify?

6. **Accessibility Check**: Would an ML generalist understand this?
   - Is subfield jargon minimized?
   - Are acronyms defined or avoided?
   - Is the contribution clear without deep domain knowledge?

### Diagnostic Output Format

Provide analysis in this structure:

```markdown
## Abstract Diagnosis

**Word count**: [N] / [venue limit or "no strict limit"]
**Structure score**: [N]/5 parts present

### Structure Check

| Part | Status | Location | Issue |
|------|--------|----------|-------|
| Context & Motivation | ✅/⚠️/❌ | Sentence 1-2 | [issue if any] |
| Problem Statement | ✅/⚠️/❌ | Sentence X | [issue if any] |
| Approach | ✅/⚠️/❌ | Sentence X-Y | [issue if any] |
| Results | ✅/⚠️/❌ | Sentence X-Y | [issue if any] |
| Impact/Implications | ✅/⚠️/❌ | Sentence X / Missing | [issue if any] |

**Legend**: ✅ Present and strong | ⚠️ Weak or unclear | ❌ Missing

### Issues Found

1. **[Severity: Critical/Major/Minor]** [Issue description]
   - **Problem**: [What's wrong]
   - **Fix**: [Specific suggestion]

2. ...

### Specificity Analysis

- **Concrete claims**: [list specific numbers/percentages]
- **Vague claims**: [list vague statements that need quantification]

### Claim Verification Checklist

- [ ] All quantitative claims are verifiable in the paper
- [ ] Baseline comparisons are specific and fair
- [ ] Method description matches the paper's contribution
- [ ] Results match the experiments section

### Accessibility Score

- **Jargon level**: Low / Medium / High
- **Undefined acronyms**: [list]
- **Generalist readability**: Excellent / Good / Poor

### Verdict

[Choose one]:
- ✅ **Ready for submission** - Minor polish recommended
- ⚠️ **Needs revision** - Address [N] issues before submission
- ❌ **Major rewrite needed** - Structural problems require rework
```

### Example Diagnostic Output

For an abstract with issues:

```markdown
## Abstract Diagnosis

**Word count**: 187 / 150 (AAAI - exceeds limit by 37 words)
**Structure score**: 3/5 parts present

### Structure Check

| Part | Status | Location | Issue |
|------|--------|----------|-------|
| Context & Motivation | ✅ | Sentence 1 | Clear motivation |
| Problem Statement | ❌ | Missing | Jumps from context to solution |
| Approach | ⚠️ | Sentence 2-4 | Too detailed, missing key insight |
| Results | ⚠️ | Sentence 5 | Vague ("significantly outperforms") |
| Impact/Implications | ❌ | Missing | No broader significance stated |

### Issues Found

1. **[Severity: Critical]** Missing problem statement
   - **Problem**: Abstract jumps from motivation directly to proposed method
   - **Fix**: Add 1 sentence after context: "A key challenge is [X], which [consequence]"

2. **[Severity: Critical]** Vague results
   - **Problem**: "significantly outperforms baselines" - no numbers
   - **Fix**: Replace with "achieves X% accuracy, outperforming [best baseline] by Y%"

3. **[Severity: Major]** Exceeds AAAI word limit
   - **Problem**: 187 words vs. 150 word limit
   - **Fix**: Apply compression techniques (see Compression section)

4. **[Severity: Minor]** Undefined acronym "DPO"
   - **Problem**: "DPO alignment" not defined
   - **Fix**: Expand to "direct preference optimization" or avoid acronym

### Specificity Analysis

- **Concrete claims**: None
- **Vague claims**: "significantly outperforms", "achieves good results", "substantially reduces"

### Claim Verification Checklist

- [ ] All quantitative claims are verifiable in the paper (no quantitative claims present)
- [ ] Baseline comparisons are specific and fair (comparisons are vague)
- [ ] Method description matches the paper's contribution (yes)
- [ ] Results match the experiments section (cannot verify - no specific numbers)

### Accessibility Score

- **Jargon level**: Medium
- **Undefined acronyms**: DPO, LoRA
- **Generalist readability**: Good (mostly accessible)

### Verdict

❌ **Major rewrite needed** - Add problem statement, quantify all results, compress to meet word limit
```

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
