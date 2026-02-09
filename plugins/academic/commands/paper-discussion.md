---
name: paper-discussion
description: Write or improve discussion and limitations sections for ML conference papers. Use when asked to "write discussion", "add limitations", "discuss results", "write conclusion", or "identify weaknesses". Generates balanced analysis of contributions, implications, and honest limitations.
model: sonnet
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: writing
  verification-level: none
---

# Discussion & Limitations Section

> **LLM-required**: Writing discussion sections requires interpretive analysis and scientific reasoning. No script alternative.

Generate publication-quality discussion and limitations sections for ML conference papers (NeurIPS, ICML, ICLR).

## Workflow

1. **Read the paper**: Read the main LaTeX files to understand the contributions, methods, and experimental results
2. **Identify key points**: Extract the main findings, unexpected results, and implications
3. **Draft discussion**: Write a structured discussion covering interpretation, implications, and connections to prior work
4. **Draft limitations**: Honestly assess weaknesses, assumptions, and scope constraints
5. **Output LaTeX**: Produce clean LaTeX ready for insertion

## Before Writing

Read these files to understand the paper:
- `main.tex` or entry point
- Methods/approach sections
- Experimental results sections
- Related work (to connect findings)

## Discussion Section Structure

```latex
\section{Discussion}
\label{sec:discussion}

% 1. Summary of main findings (1-2 sentences)
Our experiments demonstrate that [main finding].
This suggests [high-level interpretation].

% 2. Interpretation of key results
The observed [specific result] can be attributed to [explanation].
Notably, [unexpected finding] indicates that [interpretation].

% 3. Implications for the field
These findings have several implications for [area]:
\begin{itemize}
    \item \textbf{Practical:} [application/deployment implications]
    \item \textbf{Theoretical:} [what this reveals about underlying mechanisms]
    \item \textbf{Methodological:} [implications for future methods]
\end{itemize}

% 4. Connection to prior work
Our results [align with/contrast with] prior findings by \citet{key}.
While \citet{other} observed [X], we find [Y], which suggests [reconciliation].

% 5. Future directions (brief, 2-3 sentences max)
Future work could explore [direction 1] and [direction 2].
```

## Limitations Section Structure

```latex
\section{Limitations}
\label{sec:limitations}

% Be honest and specific - reviewers appreciate this

\paragraph{Methodological Limitations}
\begin{itemize}
    \item \textbf{Assumptions:} Our approach assumes [assumption], which may not hold when [scenario].
    \item \textbf{Scalability:} The computational cost scales as $\mathcal{O}(n^2)$, limiting applicability to [constraint].
    \item \textbf{Hyperparameters:} Performance depends on [hyperparameter], requiring [tuning effort].
\end{itemize}

\paragraph{Experimental Limitations}
\begin{itemize}
    \item \textbf{Datasets:} We evaluate on [datasets], which may not capture [real-world aspect].
    \item \textbf{Baselines:} Comparison with [missing baseline] would strengthen claims about [aspect].
    \item \textbf{Metrics:} We focus on [metrics]; other measures like [alternative] may reveal different behavior.
\end{itemize}

\paragraph{Scope Limitations}
\begin{itemize}
    \item \textbf{Generalization:} Results are demonstrated for [domain]; extension to [other domain] requires further validation.
    \item \textbf{Negative societal impact:} [If applicable, discuss potential misuse or bias concerns].
\end{itemize}
```

## Common Limitation Categories

### Methodological
- Assumptions made (distributional, structural, independence)
- Computational complexity / scalability
- Sensitivity to hyperparameters
- Theoretical gaps (convergence, optimality guarantees)
- Approximations or simplifications

### Experimental
- Dataset size, diversity, or representativeness
- Synthetic vs real-world data gap
- Missing baselines or ablations
- Limited evaluation metrics
- Reproducibility concerns (randomness, compute requirements)

### Scope
- Domain/task specificity
- Input modality constraints
- Failure modes not fully characterized
- Generalization bounds unknown

### Broader Impact
- Potential for misuse
- Fairness/bias concerns
- Environmental cost (compute)
- Dual-use considerations

## Writing Guidelines

### Discussion
- **Interpret, don't repeat**: Don't rehash results; explain what they mean
- **Be specific**: "This improves accuracy by 5%" not "This significantly improves performance"
- **Acknowledge surprises**: If something unexpected occurred, discuss why
- **Connect the dots**: Link findings to the broader literature
- **Stay grounded**: Avoid overclaiming; match claims to evidence

### Limitations
- **Be honest**: Reviewers respect candor; they'll find weaknesses anyway
- **Be specific**: "Assumes i.i.d. data" not "Has some assumptions"
- **Suggest mitigations**: Where possible, note how limitations could be addressed
- **Prioritize**: Lead with the most significant limitations
- **Don't apologize**: State limitations factually, not defensively

## Anti-Patterns to Avoid

### Discussion
- Repeating the abstract or introduction
- Vague statements ("This is an important contribution")
- Ignoring negative or unexpected results
- Overclaiming significance without evidence
- Disconnected bullet points without narrative flow

### Limitations
- Generic disclaimers ("More experiments needed")
- Hiding limitations in dense paragraphs
- Defensive language ("Despite these minor issues...")
- Missing obvious limitations reviewers will catch
- Excessive length (be concise)

## LaTeX Conventions

```latex
% Use cleveref for references
As shown in \cref{sec:experiments}, our method...
The results in \cref{tab:main} demonstrate...

% Use consistent math notation
The complexity is $\mathcal{O}(n^2)$ rather than $O(n^2)$

% Citations in discussion
Our findings align with \citet{author2023}, who showed...
This contrasts with prior work \citep{other2022,another2021}.

% Emphasize key points
\textbf{Key insight:} The improvement stems from...
```

## Output Format

When generating content, output:
1. A complete `\section{Discussion}` block
2. A complete `\section{Limitations}` block (or subsection if venue prefers)
3. Any new `\citet` or `\citep` references that need BibTeX entries

If the paper already has partial discussion/limitations, read them first and enhance rather than replace.
