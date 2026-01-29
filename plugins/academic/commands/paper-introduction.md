---
name: paper-introduction
description: Write or improve introduction sections for ML conference papers. Use when asked to "write introduction", "improve intro", "draft intro", "motivate the paper", or "write opening". Structures motivation, problem statement, contributions, and paper outline.
model: sonnet
---

# Introduction Section

Generate compelling introduction sections for ML conference papers (NeurIPS, ICML, ICLR).

## Workflow

1. **Understand the contribution**: Read the abstract, methods, and results to grasp the core contribution
2. **Identify the gap**: What problem exists that this work addresses?
3. **Structure the narrative**: Build from broad context to specific contribution
4. **Draft the introduction**: Write following the standard structure
5. **Refine contributions**: Make contribution statements specific and verifiable

## Before Writing

Read these files to understand the paper:
- `abstract.tex` - Core message
- Methods section - What the approach actually does
- Experiments section - What claims are supported
- Related work - How this differs from prior art

## Introduction Structure (Hourglass Model)

```latex
\section{Introduction}
\label{sec:introduction}

% === PARAGRAPH 1: Broad Context (2-3 sentences) ===
% Start wide: Why does this area matter?
[Area/field] has become increasingly important for [reason].
Recent advances in [specific subarea] have enabled [capability],
with applications ranging from [application 1] to [application 2].

% === PARAGRAPH 2: Narrow to the Problem (3-4 sentences) ===
% What's the specific challenge?
Despite this progress, a key challenge remains: [problem statement].
Existing approaches typically [current approach], which [limitation 1].
Furthermore, [limitation 2] makes it difficult to [desired capability].
This gap is particularly problematic when [practical scenario].

% === PARAGRAPH 3: Why Existing Solutions Fall Short (2-3 sentences) ===
% Brief critique of prior work (detailed comparison in Related Work)
Prior work has attempted to address this through [approach A] \citep{ref1}
and [approach B] \citep{ref2}. However, [approach A] requires [strong assumption],
while [approach B] suffers from [limitation]. A principled solution that
[desired property] remains elusive.

% === PARAGRAPH 4: This Paper's Approach (3-4 sentences) ===
% Your solution - be specific about the key insight
In this paper, we propose [method name], a [brief description].
Our key insight is that [key insight/observation].
This allows us to [capability 1] while [capability 2].
Unlike prior approaches, [method name] achieves [key advantage].

% === PARAGRAPH 5: Contributions (bulleted list) ===
% Specific, verifiable claims
Our main contributions are:
\begin{itemize}
    \item We propose [specific methodological contribution], which [what it enables].
    \item We provide [theoretical contribution, if any], showing that [result].
    \item We demonstrate [empirical contribution] on [benchmarks], achieving
          [specific improvement] over [baselines].
    \item We release [code/data/models] to facilitate future research.\footnote{
          \url{https://github.com/username/repo}}
\end{itemize}

% === PARAGRAPH 6: Paper Outline (optional, 1-2 sentences) ===
% Brief roadmap - some venues prefer this, others don't
The remainder of this paper is organized as follows: \cref{sec:background}
provides necessary background, \cref{sec:method} presents our approach,
\cref{sec:experiments} reports experimental results, and \cref{sec:conclusion}
concludes with discussion.
```

## Contribution Statement Guidelines

### Good Contributions
- **Specific**: "We prove convergence in $\mathcal{O}(1/\sqrt{T})$ iterations"
- **Verifiable**: Claims that can be checked in the paper
- **Novel**: Clearly distinct from prior work
- **Significant**: Addresses a real limitation

### Bad Contributions
- **Vague**: "We propose a novel method"
- **Overclaimed**: "We solve the problem of X" (when you improve on it)
- **Unverifiable**: "Our method is more intuitive"
- **Trivial**: "We apply X to Y" (unless non-obvious)

### Contribution Templates

```latex
% Methodological
\item We introduce [method], a [description] that [key property].
\item We propose [technique] for [task], enabling [new capability].

% Theoretical
\item We prove that [result], providing the first [guarantee type] for [setting].
\item We establish [bound/connection], showing that [implication].

% Empirical
\item We demonstrate state-of-the-art results on [benchmarks], improving
      [metric] by [X\%] over [strongest baseline].
\item We conduct extensive experiments showing [finding], with ablations
      confirming [insight].

% Practical
\item We release [artifact] at [url], enabling [use case].
\item We provide an efficient implementation achieving [speedup] over [baseline].
```

## Opening Hooks

Strong openings that grab attention:

```latex
% Surprising fact
While [assumption] has long been believed, recent evidence suggests [counterpoint].

% Practical urgency
As [systems/applications] are increasingly deployed in [context],
the need for [property] becomes critical.

% Theoretical puzzle
A fundamental question in [area] is [question]. Despite decades of research,
[gap remains].

% Recent breakthrough creating opportunity
The success of [recent advance] has opened new possibilities for [area].
However, [remaining challenge] limits [application].
```

## Connecting Problem to Solution

The transition from "problem" to "our approach" should feel natural:

```latex
% Observation-based
We observe that [observation about the problem].
This suggests that [approach direction].

% Principled
From [theoretical perspective], the key challenge is [X].
This motivates our approach of [method principle].

% Empirical insight
Our analysis reveals that existing methods fail because [reason].
To address this, we design [solution] that [how it helps].
```

## Common Mistakes to Avoid

1. **Starting too narrow**: Don't begin with "In this paper, we..."
2. **Vague problem statements**: "X is challenging" - explain WHY
3. **Strawman prior work**: Fairly represent existing approaches
4. **Contribution mismatch**: Claims must match what's actually in the paper
5. **Buried key insight**: The main idea should be clear, not hidden
6. **Too long**: NeurIPS/ICML intros are typically 1-1.5 pages
7. **No citations in context**: Cite relevant work when setting up the problem
8. **Overselling**: "Revolutionary", "paradigm shift" - let reviewers judge

## LaTeX Conventions

```latex
% Footnote for code release
\footnote{\url{https://github.com/user/repo}}

% Reference to later sections
as we show in \cref{sec:experiments}
detailed in \cref{sec:method}

% Citing prior work
\citet{author2023} showed that...  % Author (Year) - subject of sentence
Following \citep{author2023}, we... % (Author, Year) - parenthetical

% Emphasizing the key insight
\textbf{Key insight:} [insight statement]
```

## Output Format

Generate a complete `\section{Introduction}` that:
1. Follows the hourglass structure
2. Contains 4-6 paragraphs
3. Has 3-5 specific, verifiable contributions
4. Includes appropriate citations (note which need BibTeX entries)
5. Fits within 1-1.5 pages when compiled

If the paper already has an introduction, read it first and improve rather than replace.
