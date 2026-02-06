---
name: latex-consistency
description: Enforce consistent LaTeX formatting for ML conference papers. Use when asked to "fix LaTeX", "make LaTeX consistent", "format paper", "check LaTeX style", or "standardize notation". Covers math notation, references, tables, and common ML conventions.
model: haiku
---

# LaTeX Consistency

Standardize LaTeX formatting for ML conference submissions (NeurIPS, ICML, AISTATS, ICLR, AAAI).

> **Script-first**: Run the automated grep checks below first to find concrete violations, then apply fixes. LLM review is only needed for semantic consistency (e.g., same symbol used for same concept).

## Step 1: Automated Consistency Checks

Run these grep commands on your `.tex` files to detect common issues before any manual review:

```bash
TEX_FILES="*.tex"

# --- Abbreviation issues ---
# Raw abbreviations that should use macros
grep -n '\bi\.e\.\b' $TEX_FILES          # Should be \ie
grep -n '\be\.g\.\b' $TEX_FILES          # Should be \eg
grep -n '\bet al\.' $TEX_FILES            # Should be \etal
grep -n '\bw\.r\.t\.\b' $TEX_FILES       # Should be \wrt

# --- Reference issues ---
# Raw \ref instead of \cref
grep -n '\\ref{' $TEX_FILES              # Should be \cref
grep -En 'Figure\\s+\\ref' $TEX_FILES    # Should be \cref{fig:}
grep -En 'Table\\s+\\ref' $TEX_FILES     # Should be \cref{tab:}
grep -En 'Section\\s+\\ref' $TEX_FILES   # Should be \cref{sec:}
grep -En 'Equation\\s+\\ref' $TEX_FILES  # Should be \cref{eq:}

# --- Formatting issues ---
# Multiple sentences on one line (lines with 2+ sentence-ending periods)
grep -En '\.[^.]*\.[^.]*\.' $TEX_FILES | grep -v '^%' | grep -v '\\(ie\|eg\|etal\|wrt\|vs\)'
# Bare percent sign
grep -n '[0-9] %' $TEX_FILES             # Should be 50\%
# Single dash for ranges instead of en-dash
grep -En '[0-9]-[0-9]' $TEX_FILES        # Should be 1--10
# Vertical lines in tables
grep -n '|.*&\|&.*|' $TEX_FILES          # Tables should not use |

# --- Glossary in abstract ---
grep -n '\\gls{' abstract.tex 2>/dev/null   # No \gls in abstract
grep -n '\\glspl{' abstract.tex 2>/dev/null
grep -n '\\acrshort{' abstract.tex 2>/dev/null
grep -n '\\acrfull{' abstract.tex 2>/dev/null

# --- Unreferenced floats ---
# Find labels not referenced
for label in $(grep -oh '\\label{[^}]*}' $TEX_FILES | sed 's/\\label{//;s/}//'); do
  grep -q "\\\\cref{$label}\|\\\\ref{$label}" $TEX_FILES || echo "Unreferenced: $label"
done
```

Fix all script-detected issues first, then proceed to the reference guide below for manual review.

## File Structure

Organize papers modularly:

```
main.tex                 # Entry point, document class, includes
├── packages.tex         # Package imports
├── commands.tex         # Custom command definitions
├── config.tex           # Configuration and warning suppression
├── abstract.tex         # Abstract content
├── main_text.tex        # Primary content (intro, methods, experiments)
├── appendix.tex         # Supplementary materials
├── acronyms.tex         # Acronym definitions
├── refs.bib             # Bibliography
└── figures/             # Figure files (SVG, PDF, TikZ)
```

Use `\input{}` for modular includes.

## One Line = One Sentence

**Each sentence in the LaTeX source should be on its own line.** This is a critical formatting rule for collaboration and version control.

```latex
% WRONG - multiple sentences on one line
We propose a novel method for causal discovery. Our approach leverages neural networks to estimate the causal graph. Experiments show significant improvements.

% CORRECT - one sentence per line
We propose a novel method for causal discovery.
Our approach leverages neural networks to estimate the causal graph.
Experiments show significant improvements.
```

Benefits:
- **Git diffs are cleaner**: Changes to one sentence don't affect neighboring lines
- **Easier reviews**: Reviewers can comment on specific sentences
- **Simpler merges**: Reduces merge conflicts when multiple authors edit
- **Better tracking**: `git blame` shows when each sentence was added/modified

Note: Long sentences can wrap naturally in the editor; the key is that each sentence *starts* on a new line and no line contains multiple sentence-ending periods.

## Abbreviation Macros

Define standard abbreviations with proper spacing:

```latex
\usepackage{xspace}

\newcommand{\ie}{i.e.\@\xspace}
\newcommand{\Ie}{I.e.\@\xspace}
\newcommand{\eg}{e.g.\@\xspace}
\newcommand{\Eg}{E.g.\@\xspace}
\newcommand{\etal}{et al.\@\xspace}
\newcommand{\etc}{etc.\@\xspace}
\newcommand{\vs}{vs.\@\xspace}
\newcommand{\wrt}{w.r.t.\@\xspace}
\newcommand{\wolog}{w.l.o.g.\@\xspace}
```

## Math Notation Standards

### Vectors and matrices

```latex
% Vectors: bold lowercase
\newcommand{\myvec}[1]{\ensuremath{\mathbf{#1}}}
% Usage: \myvec{x}, \myvec{y}

% Matrices: bold mathrm uppercase
\newcommand{\mat}[1]{\ensuremath{\boldsymbol{\mathrm{#1}}}}
% Usage: \mat{W}, \mat{A}

% Sets: calligraphic or blackboard bold
\mathcal{D}, \mathcal{X}, \mathcal{L}
\mathbb{R}, \mathbb{E}, \mathbb{P}
```

### Matrix operations

```latex
\newcommand{\inv}[1]{\ensuremath{#1^{-1}}}
\newcommand{\pinv}[1]{\ensuremath{#1^{\dagger}}}
\newcommand{\transpose}[1]{\ensuremath{#1^{\top}}}
\newcommand{\invtranspose}[1]{\ensuremath{#1^{-\top}}}
\newcommand{\diag}[1]{\ensuremath{\mathrm{diag}\parenthesis{#1}}}
\newcommand{\rank}[1]{\ensuremath{\mathrm{rank}\parenthesis{#1}}}
\newcommand{\vectorize}[1]{\ensuremath{\mathrm{vec}\parenthesis{#1}}}
```

### Parenthesis helpers

```latex
\newcommand{\parenthesis}[1]{\ensuremath{\left(#1\right)}}
\newcommand{\brackets}[1]{\ensuremath{\left[#1\right]}}
\newcommand{\braces}[1]{\ensuremath{\left\{#1\right\}}}
```

### Norms and inner products

```latex
\newcommand{\norm}[1]{\ensuremath{\left\Vert#1\right\Vert}}
\newcommand{\normsquared}[1]{\ensuremath{\norm{#1}^2}}
\newcommand{\abs}[1]{\ensuremath{\left|#1\right|}}
\newcommand{\inner}[2]{\langle{#1},{#2}\rangle}
\newcommand{\dotprod}[2]{\ensuremath{\langle #1; #2 \rangle}}
```

### Probability and statistics

```latex
\newcommand{\E}{\mathbb{E}}
\newcommand{\Var}{\mathrm{Var}}
\newcommand{\Cov}{\mathrm{Cov}}
\newcommand{\Prob}{\mathbb{P}}
\newcommand{\conditional}[2]{\ensuremath{p\parenthesis{#1|#2}}}
\newcommand{\marginal}[1]{\ensuremath{p\parenthesis{#1}}}
\def\indep{\perp\!\!\!\perp}  % Independence symbol
```

### Derivatives

```latex
\newcommand{\derivative}[2]{\ensuremath{\dfrac{\partial #1}{\partial #2}}}
\newcommand{\totalderivative}[2]{\ensuremath{\dfrac{\mathrm{d} #1}{\mathrm{d} #2}}}
\newcommand{\grad}{\nabla}

% Common differentials with spacing
\newcommand{\dt}{\,\mathrm{d} t}
\newcommand{\dx}{\,\mathrm{d} x}
```

### Common operators

```latex
\DeclareMathOperator*{\argmin}{arg\,min}
\DeclareMathOperator*{\argmax}{arg\,max}
\DeclareMathOperator{\softmax}{softmax}
\DeclareMathOperator{\relu}{ReLU}
\DeclareMathOperator{\tr}{tr}

% Summation shortcuts
\newcommand{\sumk}[1][M]{\ensuremath{\sum_{k=1}^{#1}}}
\newcommand{\prodn}[1][n]{\ensuremath{\prod_{i=1}^{#1}}}
```

### Text in equations

```latex
\newcommand{\qtext}[1]{\quad\text{#1}\quad}
\newcommand{\qqtext}[1]{\qquad\text{#1}\qquad}
\newcommand{\stext}[1]{\ \text{#1}\ }
\newcommand{\sstext}[1]{\ \ \text{#1}\ \ }

% Usage in equations:
\begin{align}
    T = g(X) + \eta \sstext{and} Y = \theta T + f(X) + \varepsilon
\end{align}
```

### Common symbols

```latex
\def\reals{\mathbb{R}}
\newcommand{\eps}{\varepsilon}
\newcommand{\defeq}{\triangleq}  % "defined as"
\newcommand{\half}{\frac{1}{2}}
```

## Reference Style (Cleveref)

### Setup

```latex
\usepackage[capitalize,noabbrev,nameinlink]{cleveref}

% Reference format configuration
\crefname{equation}{}{}  % No prefix for equations
\crefname{section}{\S}{\S}
\crefname{figure}{Fig.}{Figs.}
\crefname{table}{Tab.}{Tabs.}
\crefname{proposition}{Prop.}{Props.}
\crefname{theorem}{Thm.}{Thms.}
\crefname{definition}{Defn.}{Defns.}
\crefname{lemma}{Lem.}{Lems.}
\crefname{corollary}{Cor.}{Cors.}
\crefname{appendix}{Appx.}{Appxs.}
\crefname{algorithm}{Alg.}{Algs.}
\crefname{assumption}{Assum.}{Assums.}
\crefname{example}{Ex.}{Exs.}
```

### Usage

```latex
\cref{fig:results}       % "Fig. 1"
\cref{eq:loss}           % "(1)" (no prefix)
\cref{sec:method}        % "§2"
\cref{thm:main}          % "Thm. 1"

% Named reference with title
\newcommand{\ncref}[1]{\cref{#1}: \nameref*{#1}}
% Usage: \ncref{thm:main} → "Thm. 1: Main Result"

% For proof section titles
\newcommand{\pcref}[1]{\texorpdfstring{Proof of \ncref{#1}}{}}
```

### Citations (natbib)

```latex
\usepackage[round]{natbib}

\citep{key}           % (Author et al., 2024)
\citet{key}           % Author et al. (2024)
\citep{a,b,c}         % (A; B; C)
```

## Table Formatting

```latex
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{makecell}
\usepackage{adjustbox}

\begin{table}[t]
    \centering
    \scriptsize
    \setlength{\tabcolsep}{2pt}
    \renewcommand{\arraystretch}{0.95}
    \begin{adjustbox}{max width=\columnwidth}
    \begin{tabular}{@{}l c c c@{}}
        \toprule\midrule
        \textbf{Method} & \textbf{Accuracy} & \textbf{F1} & \textbf{AUC} \\
        \midrule\midrule
        Baseline & 82.3 & 79.1 & 0.85 \\
        Ours & \textbf{87.5} & \textbf{84.2} & \textbf{0.91} \\
        \midrule
        \bottomrule
    \end{tabular}
    \end{adjustbox}
    \caption{\textbf{Main result message.} Additional details and context.}
    \label{tab:results}
\end{table}
```

### Table rules
- Use `booktabs` (`\toprule`, `\midrule`, `\bottomrule`)
- Double midrule for header separation: `\toprule\midrule` ... `\midrule\midrule`
- No vertical lines
- Bold best results with `\textbf{}`
- Use `\scriptsize` for dense tables
- Wrap with `\adjustbox{max width=\columnwidth}` for width control
- Caption starts with `\textbf{Main message.}`

## Figure Formatting

### Color definitions

```latex
\usepackage{xcolor}

\definecolor{figblue}{HTML}{4A90E2}
\definecolor{figred}{HTML}{D0021B}
\definecolor{figgreen}{HTML}{2CA02C}
\definecolor{figpurple}{HTML}{7030A0}
```

### Figure environment

```latex
\begin{figure*}[t]
    \centering
    \includegraphics[width=\textwidth]{figures/main_result.pdf}
    \caption{\textbf{Overview of the method.}
             \textbf{(Left:)} Description of left panel.
             \textbf{(Center:)} Description of center panel.
             \textbf{(Right:)} Description of right panel.}
    \label{fig:overview}
\end{figure*}
```

### Caption convention
- Start with `\textbf{Main message.}`
- Use `\textbf{(Left:)}`, `\textbf{(Center:)}`, `\textbf{(Right:)}` for multi-panel figures

## Theorem Environments

```latex
\usepackage{amsthm}
\usepackage{thmtools,thm-restate}  % For restatable theorems

\theoremstyle{plain}
\newtheorem{theorem}{Theorem}[section]
\newtheorem{proposition}{Proposition}[section]
\newtheorem{lem}{Lemma}[section]
\newtheorem{corollary}{Corollary}[section]

\theoremstyle{definition}
\newtheorem{definition}{Definition}[section]
\newtheorem{assum}{Assumption}[section]
\newtheorem{conjecture}{Conjecture}[section]

\theoremstyle{remark}
\newtheorem{remark}{Remark}[section]
\newtheorem{example}{Example}
```

## Acronyms (Glossaries)

```latex
\usepackage[acronym,automake,toc,nomain,nopostdot,
            style=tree,nonumberlist,numberedsection]{glossaries}

% Define acronyms
\newacronym{ica}{ICA}{Independent Component Analysis}
\newacronym{dag}{DAG}{Directed Acyclic Graph}
\newacronym{mlp}{MLP}{Multi-Layer Perceptron}

% Usage (everywhere except in the abstract)
\gls{ica}        % First: "Independent Component Analysis (ICA)", then: "ICA"
\glspl{dag}      % Plural
\acrfull{ica}    % Always full: "Independent Component Analysis (ICA)"
\acrshort{ica}   % Always short: "ICA"
```

### No `\gls` in the abstract

**Never use `\gls{}`, `\glspl{}`, `\acrshort{}`, or `\acrfull{}` commands in the abstract.** The abstract must be self-contained and should not rely on the glossary system. Instead, write out acronyms manually:

```latex
% In abstract.tex - WRONG
We propose a novel \gls{dag} learning method using \gls{ica}.

% In abstract.tex - CORRECT
We propose a novel Directed Acyclic Graph (DAG) learning method
using Independent Component Analysis (ICA).
```

Reasons:
- Abstracts are often extracted separately (indexing, search engines)
- PDF metadata/bookmarks may not render glossary commands correctly
- The glossary first-use expansion may conflict with the main text

## Hyperref Configuration

```latex
\usepackage[hidelinks,backref=page]{hyperref}
\hypersetup{
    colorlinks,
    linkcolor={red!50!black},
    citecolor={blue!50!black},
    urlcolor={blue!80!black}
}

% Handle glossary in PDF strings
\pdfstringdefDisableCommands{%
    \def\gls#1{<#1>}%
    \def\glspl#1{<#1>}%
    \def\acrshort#1{<#1>}%
}
```

## Appendix Setup

```latex
\appendix
\usepackage{etoc}  % Partial table of contents

% Appendix-specific TOC
\etocdepthtag.toc{appendix}
\etocsettagdepth{main}{none}
\etocsettagdepth{appendix}{subsection}
\etocsettocstyle{\section*{Contents}}{}
\tableofcontents

% Renumber figures/tables as A.1, A.2, etc.
\counterwithin{figure}{section}
\counterwithin{table}{section}
\renewcommand{\thefigure}{\Alph{section}.\arabic{figure}}
\renewcommand{\thetable}{\Alph{section}.\arabic{table}}
```

## Warning Suppression

```latex
% Suppress overfull/underfull warnings (use sparingly)
\vbadness=10000
\hbadness=10000
\hfuzz=3500pt
```

## Author Comments (Development)

```latex
\usepackage{todonotes}
\usepackage{xcolor}

\newcommand{\authorname}[1]{\textcolor{cyan}{[\textbf{Author:} #1]}}
\newcommand{\todo}[1]{\textcolor{red}{\textbf{TODO:} #1}}

% Disable for submission
% \renewcommand{\authorname}[1]{}
% \renewcommand{\todo}[1]{}
```

## Preamble Template

```latex
% Core packages
\usepackage{amsmath,amssymb,mathtools}
\usepackage{amsthm,thmtools,thm-restate}
\usepackage{microtype}

% Tables
\usepackage{booktabs,multirow,makecell,adjustbox}

% Figures
\usepackage{graphicx,subcaption,float}
\usepackage{xcolor}

% References
\usepackage[round]{natbib}
\usepackage[capitalize,noabbrev,nameinlink]{cleveref}
\usepackage[colorlinks]{hyperref}

% Acronyms (optional)
\usepackage[acronym,automake]{glossaries}

% Abbreviation macros
\usepackage{xspace}
\newcommand{\ie}{i.e.\@\xspace}
\newcommand{\eg}{e.g.\@\xspace}
\newcommand{\etal}{et al.\@\xspace}
\newcommand{\wrt}{w.r.t.\@\xspace}

% Math macros
\newcommand{\myvec}[1]{\ensuremath{\mathbf{#1}}}
\newcommand{\mat}[1]{\ensuremath{\boldsymbol{\mathrm{#1}}}}
\newcommand{\E}{\mathbb{E}}
\def\reals{\mathbb{R}}
\DeclareMathOperator*{\argmin}{arg\,min}
\DeclareMathOperator*{\argmax}{arg\,max}
```

## Consistency Checklist

### Notation
- [ ] Vectors consistently bold lowercase (`\myvec{}`)
- [ ] Matrices consistently bold mathrm (`\mat{}`)
- [ ] Sets consistently calligraphic (`\mathcal{}`)
- [ ] Same symbol for same concept throughout
- [ ] All symbols defined on first use
- [ ] Use `\ensuremath{}` wrapper in macro definitions

### References
- [ ] All figures/tables referenced in text
- [ ] Using `\cref{}` for smart references
- [ ] Consistent citation style (`\citep`/`\citet`)
- [ ] No orphan references

### Formatting
- [ ] Using abbreviation macros (`\ie`, `\eg`, `\etal`)
- [ ] Consistent hyphenation
- [ ] Captions start with `\textbf{Main message.}`
- [ ] Figure panels labeled `\textbf{(Left:)}` etc.
- [ ] Tables use `booktabs` rules
- [ ] One line = one sentence

### Structure
- [ ] Modular file organization
- [ ] Appendix figures numbered as A.1, A.2
- [ ] Acronyms using `\gls{}` system everywhere except in the abstract

## Common Fixes

| Issue | Wrong | Correct |
|-------|-------|---------|
| Vector notation | `$x$` | `$\myvec{x}$` |
| Text in math | `$accuracy$` | `$\text{accuracy}$` |
| Abbreviation | `i.e.` | `\ie` |
| Et al | `et. al` | `\etal` |
| Reference | `Figure \ref` | `\cref{fig:}` |
| Citation style | `[Author]` | `\citep{key}` |
| Percent | `50 %` | `50\%` |
| Range | `1-10` | `1--10` |
| Independence | `\perp` | `\indep` |
| Defined as | `=` (ambiguous) | `\defeq` |
