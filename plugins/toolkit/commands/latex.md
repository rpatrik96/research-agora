---
name: latex
description: |
  Build, debug and lint a LaTeX paper. Use when asked to "build the pdf",
  "recompile", "compile the paper", "why won't my paper compile", "the pdf is
  still the old version", "fix latex errors", "debug latex", "parse the log",
  "fix LaTeX", "make LaTeX consistent", "check LaTeX style", or "standardize
  notation". Three modes over one source tree: **build** compiles with latexmk
  and proves the PDF is fresh, **debug** reads the log that build produced and
  fixes what it reports, **lint** greps for house-style and notation violations.
model: haiku
disable-model-invocation: true
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: automation
  verification-level: formal
---

# LaTeX

One `.tex` source, three things you need from it.

| They said | Mode |
|---|---|
| "build", "recompile", "the pdf is stale" | **build** |
| "it won't compile", "fix these errors", "parse the log" | **debug** |
| "make it consistent", "check style", "standardize notation" | **lint** |

These were three skills until RFC-0002. They are three modes now because
**build** writes the log **debug** reads: running them separately meant
hand-carrying a path between two skills, and a failed build left the user
holding an error instead of a fix. When a build fails, continue into **debug**
rather than stopping.

---

## Mode: build

Compile a paper correctly, then prove the PDF you are about to read is the one the compiler just wrote.

> **Script-first**: `scripts/build_latex.py` performs root detection, the build, the glossary pass, dependency extraction, and the freshness comparison. The LLM is needed only to fix source errors and decide when a fix requires an author's judgment.

### Why this exists

Two failure modes waste more time than any genuine LaTeX error.

**Bare `pdflatex` skips passes.** One `pdflatex` run resolves no citations and no glossary entries. The document compiles, exits 0, and ships with `[?]` where every reference should be. `latexmk` runs the passes to convergence, which is why this skill never calls the engine directly.

**An exit code of 0 does not mean a new PDF exists.** `latexmk` skips work when it believes nothing changed, `-outdir` sends output somewhere other than the source directory, and a directory holding several `\documentclass` files can compile a standalone TikZ figure instead of the paper. Each case returns success over a stale PDF. The script therefore compares the PDF's modification time against every file the build actually read and reports `fresh: false` when the PDF did not move.

### Step 1: Build

```bash
python3 scripts/build_latex.py <root.tex-or-directory> --json
```

Options:

| Flag | Effect |
|------|--------|
| `--engine pdflatex\|xelatex\|lualatex` | Selects `-pdf` / `-pdfxe` / `-pdflua`. Default `pdflatex`. |
| `--outdir DIR` | Overrides the output directory. A `$out_dir` in `.latexmkrc` is honoured automatically. |
| `--timeout N` | Per-pass timeout in seconds. Default 600. |
| `--open` | Opens the PDF when the build is fresh. No-op on a headless machine. |
| `--json` | Machine-readable output. |

The script exits 0 only when the build succeeded **and** the PDF is fresh.

#### What the script decides on its own

- **Root file.** The `.tex` declaring `\documentclass` that no other file pulls in via `\input`, `\include`, or `\subfile`. `\documentclass{standalone}` files are excluded, since those are figures. With several candidates left it prefers a top-level `main.tex` or `paper.tex` and reports its choice in `root` — check that field when the output looks wrong.
- **Output directory.** Read from `$out_dir` in `.latexmkrc` before anything is stat-ed, so freshness is checked on the PDF the build actually wrote rather than a stale sibling in the source directory.
- **Glossary pass.** When the preamble loads `glossaries`, `glossaries-extra`, or `acronym` *without* the `automake` option, the script runs `makeglossaries` and rebuilds. With `automake`, latexmk already handles it.
- **Dependency set.** Taken from the `.fls` recorder file, which lists the files the compiler actually opened. Globbing every `.tex` in the tree would flag an unused draft as a dependency and report a false stale. `dep_source` reports `fls` or the `glob` fallback.

### Step 2: Read the verdict

```json
{
  "root": "/abs/path/main.tex",
  "engine": "pdflatex",
  "exit_code": 0,
  "pdf_path": "/abs/path/build/main.pdf",
  "pdf_mtime": 1785772000.0,
  "newest_dep": "/abs/path/sections/method.tex",
  "newest_dep_mtime": 1785771990.0,
  "fresh": true,
  "pages": 9,
  "glossary_pass": false,
  "dep_source": "fls",
  "errors": [{"file": "./main.tex", "line": 42, "text": "Undefined control sequence."}],
  "undefined_refs": ["sec:ghost"],
  "undefined_cites": ["smith2024"],
  "rerun_limit_hit": false,
  "warnings": [],
  "diagnosis": null
}
```

Three outcomes, and they are not interchangeable:

| `exit_code` | `fresh` | Meaning | What to do |
|---|---|---|---|
| 0 | `true` | The PDF was written by this build. | Report the path, mtime, and page count. Done. |
| 0 | `false` | The compiler succeeded over a stale PDF. | **Never report success.** Read `diagnosis`, then check the root, `-outdir`, and whether latexmk skipped the run. |
| non-zero | `false` | The build failed. | Go to step 3. |

### Step 3: Triage a failed build

Report the `errors` array verbatim — file, line, and the compiler's own words. Do not paraphrase a compiler message into a guess about its cause.

Two error classes are worth separating in the report because they behave differently:

- **`errors`** stop the build. Nothing is produced until they are fixed.
- **`undefined_refs` and `undefined_cites`** do not. They compile to `??` and `[?]`, so the PDF exists and looks finished while pointing nowhere. Surface these even on a clean build — they are the most common way a paper reaches a reviewer broken.

When `rerun_limit_hit` is set, latexmk stopped before references converged. That is usually an unresolved citation feeding a rerun loop, so fix the citations first and rebuild.

For anything beyond the obvious, hand `<root>.log` to `toolkit:latex`, which carries the full error taxonomy and quick-fix table. Do not restate that taxonomy here; two copies drift apart. When the `research-agents` plugin is not installed, report the raw evidence and stop rather than guessing.

### Step 4: Fix and rebuild

Apply the fix, rerun step 1, and repeat until the build is clean and fresh. Stop and ask the author when the fix is a content decision rather than a mechanical one:

- A citation key with no matching `.bib` entry — the right entry is the author's to choose, and inventing one fabricates a reference.
- A `\label` referenced from two places with different intent.
- A missing figure file that may be unrendered rather than misnamed.

### Step 5: Deliver

State the absolute PDF path and its modification time, the page count, and any undefined references or citations that survived. Open the PDF with `--open` when the author is at a desktop.

A page count matters more than it looks: NeurIPS, ICML, ICLR, and AAAI all enforce a hard page limit on the main body, and discovering an overrun at the submission deadline is avoidable.

### Constraints

- **Never report a build as done without `fresh: true`.** A stale PDF that reads as current is the failure this skill exists to prevent.
- **Never invent a citation key or a bibliography entry** to clear an undefined-citation warning. Flag it and let the author supply the source.
- Style and notation are out of scope. `\ref` versus `\cref`, booktabs, and abbreviation macros belong to `/latex`, which greps for them directly.
- `latexmk -c` cleans auxiliary files. Run it only when asked; it deletes the `.fls` this skill depends on.

### Requirements

`latexmk` and a TeX engine on `PATH`. All three major distributions ship latexmk: TeX Live (Linux), MacTeX (macOS), MiKTeX (Windows). `makeglossaries` ships with the same distributions and is needed only for documents using glossary packages without `automake`. The script itself uses only the Python standard library.

### Cross-references

- **Compilation errors you cannot read**: `toolkit:latex` parses the `.log` this skill produces and returns targeted fixes.
- **Formatting and notation consistency**: `/latex` after the paper compiles.
- **Bibliography correctness**: `/paper-references` verifies that the entries resolving those citations describe real papers.
- **Submission readiness**: `verify:pre-submission-audit` once the document builds clean.

---

## Mode: debug

> **Hybrid**: LaTeX compilation errors can be detected via script (pdflatex/latexmk output parsing). LLM is used to diagnose causes and suggest fixes.

You are a LaTeX Debugging Specialist - an expert diagnostician for LaTeX compilation issues in ML research papers. Your mission is to rapidly identify, explain, and fix compilation errors by parsing log files and understanding the complex interactions between packages, templates, and venue-specific style files.

**YOUR CORE MISSION:**
Parse LaTeX log files to extract errors and warnings, diagnose root causes (often different from reported errors), and provide copy-paste fixes. You specialize in ML venue templates (NeurIPS, ICML, ICLR) and understand common pitfalls with math-heavy documents, bibliography management, and figure placement.

### WORKFLOW

1. **Locate Log File**: Find the .log file in the project directory (usually same name as main .tex)
2. **Extract Errors**: Parse log for `!` errors, warnings, and bad boxes
3. **Identify Root Cause**: Trace errors to their source (often earlier than reported line)
4. **Check Package Conflicts**: Identify conflicting packages or load order issues
5. **Verify Template Compliance**: Check against venue-specific requirements
6. **Provide Targeted Fixes**: Give exact code to add, remove, or modify
7. **Explain the Why**: Help user understand the error for future prevention
8. **Test Suggestion**: Recommend minimal test to verify fix works
9. **Check for Cascading Issues**: One fix may reveal hidden errors
10. **Document Solution**: Provide fix in copy-paste format with context

### ERROR CATEGORIES

| Category | Example | Common Cause |
|----------|---------|--------------|
| **Missing Packages** | `! Undefined control sequence. \cref` | Package not loaded or loaded after dependent package |
| **Undefined References** | `Reference 'fig:main' undefined` | Label defined after reference, or typo in label name |
| **Math Mode Errors** | `! Missing $ inserted` | Math command outside math mode, or text in math |
| **Float Placement** | `! Too many unprocessed floats` | Too many figures/tables without `[htbp!]` or `\clearpage` |
| **Bibliography Errors** | `Citation 'smith2024' undefined` | Missing .bib file, bibtex not run, or key mismatch |
| **Encoding Issues** | `! Package inputenc Error: Invalid UTF-8 byte` | Non-UTF8 characters, often from copy-paste |
| **Package Conflicts** | `! Option clash for package` | Same package loaded twice with different options |
| **Font Errors** | `! Font ... not found` | Missing font or wrong engine (pdflatex vs xelatex) |
| **Dimension Errors** | `! Dimension too large` | Infinite loop in sizing, usually from circular refs |
| **Memory Errors** | `! TeX capacity exceeded` | Too many floats, huge tables, or package conflicts |

### ERROR PARSING PATTERNS

When reading .log files, search for these patterns in order of severity:

```
CRITICAL ERRORS (Stop compilation):
! LaTeX Error:              → Package/class errors
! Undefined control sequence → Missing package or typo
! Missing $ inserted        → Math mode boundary issue
! Emergency stop            → Fatal error, check preceding lines
! ==> Fatal error occurred  → Usually encoding or file issue

WARNINGS (Compilation continues but output affected):
LaTeX Warning: Reference     → Undefined \ref or \label
LaTeX Warning: Citation      → Undefined \cite
Package hyperref Warning     → PDF bookmark issues
LaTeX Warning: Float too large → Figure won't fit

BAD BOXES (Layout issues):
Overfull \hbox              → Line too wide (badness > 10000 is serious)
Underfull \hbox             → Line too sparse
Overfull \vbox              → Page overflow
```

### FIX TEMPLATES

#### Missing Package Errors

```latex
% Problem: ! Undefined control sequence. \cref
% Cause: cleveref package not loaded
% Fix: Add to preamble AFTER hyperref

\usepackage{hyperref}
\usepackage{cleveref}  % Must come after hyperref
```

```latex
% Problem: ! Undefined control sequence. \mathbb
% Cause: amssymb not loaded
% Fix: Add to preamble

\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsthm}
```

```latex
% Problem: ! Undefined control sequence. \toprule
% Cause: booktabs not loaded
% Fix: Add to preamble

\usepackage{booktabs}
```

#### Math Mode Errors

```latex
% Problem: ! Missing $ inserted (with \text inside equation)
% Cause: \text requires amsmath
% Fix: Ensure amsmath loaded, or use alternative

\usepackage{amsmath}
% Then use:
$x = 5 \text{ for all } y$
% Or without amsmath:
$x = 5 \mbox{ for all } y$
```

```latex
% Problem: ! Missing } inserted (in align environment)
% Cause: Unmatched braces in multi-line equation
% Fix: Check brace matching, especially in \underbrace, \overbrace

% Bad:
\begin{align}
  f(x) &= \underbrace{x^2 + y^2_{z}  % Missing }
\end{align}

% Good:
\begin{align}
  f(x) &= \underbrace{x^2 + y^2}_{z}
\end{align}
```

#### Reference Errors

```latex
% Problem: LaTeX Warning: Reference `fig:results' on page 5 undefined
% Cause: Label doesn't exist or is defined after reference
% Fix: Ensure \label comes AFTER \caption

% Bad:
\begin{figure}
  \label{fig:results}  % Wrong position!
  \includegraphics{results.pdf}
  \caption{Results}
\end{figure}

% Good:
\begin{figure}
  \includegraphics{results.pdf}
  \caption{Results}
  \label{fig:results}  % After caption
\end{figure}
```

#### Float Placement Errors

```latex
% Problem: ! Too many unprocessed floats
% Cause: LaTeX cannot place all floats before document end
% Fix: Add \clearpage or use float package

% Option 1: Force float placement
\clearpage  % Add before problematic section

% Option 2: Use float package for [H] placement
\usepackage{float}
\begin{figure}[H]  % Places figure exactly HERE
  ...
\end{figure}

% Option 3: Increase float limits in preamble
\setcounter{topnumber}{3}
\setcounter{bottomnumber}{3}
\setcounter{totalnumber}{6}
\renewcommand{\topfraction}{0.9}
\renewcommand{\bottomfraction}{0.9}
```

#### Bibliography Errors

```latex
% Problem: Citation 'smith2024' undefined
% Cause: bibtex/biber not run, or key mismatch
% Fix: Run full compilation sequence

% Compile sequence:
% pdflatex main.tex
% bibtex main       (or biber main for biblatex)
% pdflatex main.tex
% pdflatex main.tex

% Check .bib file has matching key:
@article{smith2024,  % This must match \cite{smith2024}
  author = {...},
  ...
}
```

#### Encoding Errors

```latex
% Problem: ! Package inputenc Error: Invalid UTF-8 byte sequence
% Cause: Non-UTF8 character (often copy-pasted from PDF)
% Fix: Find and replace problematic character

% Common culprits:
% - Smart quotes " " ' ' → Replace with " and '
% - En-dash – Em-dash — → Replace with -- and ---
% - Non-breaking space   → Replace with regular space
% - Degree symbol ° → Use $^\circ$ or \textdegree

% In preamble, ensure:
\usepackage[utf8]{inputenc}  % For pdflatex
% Or use XeLaTeX/LuaLaTeX which handles UTF-8 natively
```

#### Package Conflict Errors

```latex
% Problem: ! Option clash for package hyperref
% Cause: Package loaded twice with different options
% Fix: Load package once with all options, or use \PassOptionsToPackage

% Bad (in document that uses a class loading hyperref):
\usepackage[colorlinks]{hyperref}

% Good:
\PassOptionsToPackage{colorlinks}{hyperref}
% Put this BEFORE \documentclass
```

### VENUE-SPECIFIC ISSUES

#### NeurIPS Template

```latex
% Issue: \cref undefined with neurips_2024.sty
% Cause: Must load cleveref after hyperref, which neurips loads
% Fix:
\usepackage{neurips_2024}
% ... other packages ...
\usepackage{cleveref}  % Load LAST

% Issue: Line numbers overlap with equations
% Cause: lineno package conflict with amsmath
% Fix: Add to preamble BEFORE \begin{document}
\usepackage{etoolbox}
\makeatletter
\newcommand*\linenomathpatch[1]{%
  \expandafter\pretocmd\csname #1\endcsname {\linenomath}{}{}%
  \expandafter\apptocmd\csname #1*\endcsname {\endlinenomath}{}{}%
  \expandafter\pretocmd\csname end#1\endcsname {\endlinenomath}{}{}%
  \expandafter\pretocmd\csname end#1*\endcsname {\endlinenomath}{}{}%
}
\makeatother
\linenomathpatch{equation}
\linenomathpatch{align}
```

#### ICML Template

```latex
% Issue: \icmltitle undefined
% Cause: Using wrong template file
% Fix: Ensure you have icml2024.sty and use:
\documentclass{article}
\usepackage{icml2024}

% Issue: Author block errors in camera-ready
% Cause: Using [accepted] option incorrectly
% Fix: For camera-ready, use:
\usepackage[accepted]{icml2024}
```

#### ICLR Template

```latex
% Issue: Template doesn't compile with XeLaTeX
% Cause: iclr2024_conference.sty assumes pdflatex
% Fix: Use pdflatex, not xelatex

% Issue: \citep undefined
% Cause: natbib not loaded by template
% Fix: Add before template:
\usepackage{natbib}
```

### OUTPUT FORMAT

```markdown
## LaTeX Debug Report

**Log File**: [filename.log]
**Main Document**: [filename.tex]
**Compilation Engine**: [pdflatex/xelatex/lualatex]

---

### Error Summary

| # | Type | Line | Severity | Status |
|---|------|------|----------|--------|
| 1 | [Category] | [Line#] | Critical/Warning/Info | [Needs Fix/Informational] |

---

### Error 1: [Brief Description]

**Log Output**:
```
! LaTeX Error: [exact error message]
l.XX [line content]
```

**Root Cause**: [Explanation of why this happens]

**File**: [filename.tex]
**Line**: [approximate line number]

**Fix**:
```latex
% Replace this:
[problematic code]

% With this:
[fixed code]
```

**Verification**: Recompile and check line XX no longer shows error

---

### Warnings to Address

1. **[Warning type]** on line XX: [Brief fix]

---

### Recommended Compilation Sequence

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

---

### Prevention Tips

- [Tip based on errors found]
```

### MCP INTEGRATION

Use filesystem tools to read log and tex files:

**Strategy:**
1. First read the .log file completely
2. Identify line numbers from errors
3. Read corresponding .tex file sections
4. Cross-reference with any included files (.sty, .bib)

### QUICK FIXES TABLE

| Error Pattern | One-Line Fix |
|--------------|--------------|
| `Undefined control sequence \cref` | `\usepackage{cleveref}` after hyperref |
| `Undefined control sequence \toprule` | `\usepackage{booktabs}` |
| `Undefined control sequence \mathbb` | `\usepackage{amssymb}` |
| `Missing $ inserted` | Wrap math content in `$...$` or check brace matching |
| `Reference undefined` | Run LaTeX twice, or check `\label` after `\caption` |
| `Citation undefined` | Run `bibtex main` then `pdflatex` twice |
| `Too many unprocessed floats` | Add `\clearpage` before problematic section |
| `Option clash for package` | Use `\PassOptionsToPackage` before `\documentclass` |
| `Font ... not found` | Switch to pdflatex or install missing font |
| `Dimension too large` | Check for circular `\ref` in captions |
| `Float too large for page` | Reduce figure size or use `[p]` placement |
| `Overfull hbox (badness 10000)` | Add `\sloppy` locally or reword text |
| `Package hyperref Warning: Token not allowed` | Use `\texorpdfstring{$math$}{text}` in section titles |
| `Missing \begin{document}` | Check for syntax error before `\begin{document}` |
| `File not found` | Check filename spelling and path |

### IMPORTANT PRINCIPLES

1. **Read the FULL log**: Errors cascade; the first error often causes many others
2. **Look BEFORE the reported line**: The actual error is often 1-5 lines earlier
3. **Check package load order**: hyperref should be last (except cleveref), amsmath early
4. **Run full compile sequence**: Many "errors" are just incomplete compilation
5. **Suspect copy-paste**: Encoding errors often come from PDF or web copy-paste
6. **Check the class file**: Venue templates may conflict with common packages
7. **Binary search for errors**: Comment out sections to isolate the problem
8. **Keep fixes minimal**: Change one thing at a time to identify the actual fix
9. **Document your solution**: Future you will forget why you added that line
10. **Test incrementally**: Don't add 10 fixes then recompile; test each one

Your goal is to get the paper compiling quickly so the researcher can focus on content, not LaTeX debugging. Be specific, provide exact fixes, and explain enough to prevent future occurrences.

---

## Mode: lint

Standardize LaTeX formatting for ML conference submissions (NeurIPS, ICML, AISTATS, ICLR, AAAI).

> **Script-first**: Run the automated grep checks below first to find concrete violations, then apply fixes. LLM review is only needed for semantic consistency (e.g., same symbol used for same concept).

### Step 1: Automated Consistency Checks

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

### File Structure

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

### One Line = One Sentence

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

### Abbreviation Macros

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

### Math Notation Standards

#### Vectors and matrices

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

#### Matrix operations

```latex
\newcommand{\inv}[1]{\ensuremath{#1^{-1}}}
\newcommand{\pinv}[1]{\ensuremath{#1^{\dagger}}}
\newcommand{\transpose}[1]{\ensuremath{#1^{\top}}}
\newcommand{\invtranspose}[1]{\ensuremath{#1^{-\top}}}
\newcommand{\diag}[1]{\ensuremath{\mathrm{diag}\parenthesis{#1}}}
\newcommand{\rank}[1]{\ensuremath{\mathrm{rank}\parenthesis{#1}}}
\newcommand{\vectorize}[1]{\ensuremath{\mathrm{vec}\parenthesis{#1}}}
```

#### Parenthesis helpers

```latex
\newcommand{\parenthesis}[1]{\ensuremath{\left(#1\right)}}
\newcommand{\brackets}[1]{\ensuremath{\left[#1\right]}}
\newcommand{\braces}[1]{\ensuremath{\left\{#1\right\}}}
```

#### Norms and inner products

```latex
\newcommand{\norm}[1]{\ensuremath{\left\Vert#1\right\Vert}}
\newcommand{\normsquared}[1]{\ensuremath{\norm{#1}^2}}
\newcommand{\abs}[1]{\ensuremath{\left|#1\right|}}
\newcommand{\inner}[2]{\langle{#1},{#2}\rangle}
\newcommand{\dotprod}[2]{\ensuremath{\langle #1; #2 \rangle}}
```

#### Probability and statistics

```latex
\newcommand{\E}{\mathbb{E}}
\newcommand{\Var}{\mathrm{Var}}
\newcommand{\Cov}{\mathrm{Cov}}
\newcommand{\Prob}{\mathbb{P}}
\newcommand{\conditional}[2]{\ensuremath{p\parenthesis{#1|#2}}}
\newcommand{\marginal}[1]{\ensuremath{p\parenthesis{#1}}}
\def\indep{\perp\!\!\!\perp}  % Independence symbol
```

#### Derivatives

```latex
\newcommand{\derivative}[2]{\ensuremath{\dfrac{\partial #1}{\partial #2}}}
\newcommand{\totalderivative}[2]{\ensuremath{\dfrac{\mathrm{d} #1}{\mathrm{d} #2}}}
\newcommand{\grad}{\nabla}

% Common differentials with spacing
\newcommand{\dt}{\,\mathrm{d} t}
\newcommand{\dx}{\,\mathrm{d} x}
```

#### Common operators

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

#### Text in equations

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

#### Common symbols

```latex
\def\reals{\mathbb{R}}
\newcommand{\eps}{\varepsilon}
\newcommand{\defeq}{\triangleq}  % "defined as"
\newcommand{\half}{\frac{1}{2}}
```

### Reference Style (Cleveref)

#### Setup

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

#### Usage

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

#### Citations (natbib)

```latex
\usepackage[round]{natbib}

\citep{key}           % (Author et al., 2024)
\citet{key}           % Author et al. (2024)
\citep{a,b,c}         % (A; B; C)
```

### Table Formatting

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

#### Table rules
- Use `booktabs` (`\toprule`, `\midrule`, `\bottomrule`)
- Double midrule for header separation: `\toprule\midrule` ... `\midrule\midrule`
- No vertical lines
- Bold best results with `\textbf{}`
- Use `\scriptsize` for dense tables
- Wrap with `\adjustbox{max width=\columnwidth}` for width control
- Caption starts with `\textbf{Main message.}`

### Figure Formatting

#### Color definitions

```latex
\usepackage{xcolor}

\definecolor{figblue}{HTML}{4A90E2}
\definecolor{figred}{HTML}{D0021B}
\definecolor{figgreen}{HTML}{2CA02C}
\definecolor{figpurple}{HTML}{7030A0}
```

#### Figure environment

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

#### Caption convention
- Start with `\textbf{Main message.}`
- Use `\textbf{(Left:)}`, `\textbf{(Center:)}`, `\textbf{(Right:)}` for multi-panel figures

### Theorem Environments

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

### Acronyms (Glossaries)

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

#### No `\gls` in the abstract

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

### Hyperref Configuration

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

### Appendix Setup

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

### Warning Suppression

```latex
% Suppress overfull/underfull warnings (use sparingly)
\vbadness=10000
\hbadness=10000
\hfuzz=3500pt
```

### Author Comments (Development)

```latex
\usepackage{todonotes}
\usepackage{xcolor}

\newcommand{\authorname}[1]{\textcolor{cyan}{[\textbf{Author:} #1]}}
\newcommand{\todo}[1]{\textcolor{red}{\textbf{TODO:} #1}}

% Disable for submission
% \renewcommand{\authorname}[1]{}
% \renewcommand{\todo}[1]{}
```

### Preamble Template

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

### Consistency Checklist

#### Notation
- [ ] Vectors consistently bold lowercase (`\myvec{}`)
- [ ] Matrices consistently bold mathrm (`\mat{}`)
- [ ] Sets consistently calligraphic (`\mathcal{}`)
- [ ] Same symbol for same concept throughout
- [ ] All symbols defined on first use
- [ ] Use `\ensuremath{}` wrapper in macro definitions

#### References
- [ ] All figures/tables referenced in text
- [ ] Using `\cref{}` for smart references
- [ ] Consistent citation style (`\citep`/`\citet`)
- [ ] No orphan references

#### Formatting
- [ ] Using abbreviation macros (`\ie`, `\eg`, `\etal`)
- [ ] Consistent hyphenation
- [ ] Captions start with `\textbf{Main message.}`
- [ ] Figure panels labeled `\textbf{(Left:)}` etc.
- [ ] Tables use `booktabs` rules
- [ ] One line = one sentence

#### Structure
- [ ] Modular file organization
- [ ] Appendix figures numbered as A.1, A.2
- [ ] Acronyms using `\gls{}` system everywhere except in the abstract

### Common Fixes

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
