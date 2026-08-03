---
name: latex-build
description: Compile a LaTeX paper with latexmk (full bibliography and glossary passes) and prove the PDF on disk is the one just built. Use when asked to "build the pdf", "recompile", "rebuild the paper", "compile the paper", "make the pdf", "why won't my paper compile", or when "the pdf is still the old version". Reports the absolute path, a freshness verdict, page count, and verbatim compiler errors.
model: haiku
disable-model-invocation: true
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: automation
  verification-level: formal
---

# LaTeX Build

Compile a paper correctly, then prove the PDF you are about to read is the one the compiler just wrote.

> **Script-first**: `scripts/build_latex.py` performs root detection, the build, the glossary pass, dependency extraction, and the freshness comparison. The LLM is needed only to fix source errors and decide when a fix requires an author's judgment.

## Why this exists

Two failure modes waste more time than any genuine LaTeX error.

**Bare `pdflatex` skips passes.** One `pdflatex` run resolves no citations and no glossary entries. The document compiles, exits 0, and ships with `[?]` where every reference should be. `latexmk` runs the passes to convergence, which is why this skill never calls the engine directly.

**An exit code of 0 does not mean a new PDF exists.** `latexmk` skips work when it believes nothing changed, `-outdir` sends output somewhere other than the source directory, and a directory holding several `\documentclass` files can compile a standalone TikZ figure instead of the paper. Each case returns success over a stale PDF. The script therefore compares the PDF's modification time against every file the build actually read and reports `fresh: false` when the PDF did not move.

## Step 1: Build

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

### What the script decides on its own

- **Root file.** The `.tex` declaring `\documentclass` that no other file pulls in via `\input`, `\include`, or `\subfile`. `\documentclass{standalone}` files are excluded, since those are figures. With several candidates left it prefers a top-level `main.tex` or `paper.tex` and reports its choice in `root` — check that field when the output looks wrong.
- **Output directory.** Read from `$out_dir` in `.latexmkrc` before anything is stat-ed, so freshness is checked on the PDF the build actually wrote rather than a stale sibling in the source directory.
- **Glossary pass.** When the preamble loads `glossaries`, `glossaries-extra`, or `acronym` *without* the `automake` option, the script runs `makeglossaries` and rebuilds. With `automake`, latexmk already handles it.
- **Dependency set.** Taken from the `.fls` recorder file, which lists the files the compiler actually opened. Globbing every `.tex` in the tree would flag an unused draft as a dependency and report a false stale. `dep_source` reports `fls` or the `glob` fallback.

## Step 2: Read the verdict

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

## Step 3: Triage a failed build

Report the `errors` array verbatim — file, line, and the compiler's own words. Do not paraphrase a compiler message into a guess about its cause.

Two error classes are worth separating in the report because they behave differently:

- **`errors`** stop the build. Nothing is produced until they are fixed.
- **`undefined_refs` and `undefined_cites`** do not. They compile to `??` and `[?]`, so the PDF exists and looks finished while pointing nowhere. Surface these even on a clean build — they are the most common way a paper reaches a reviewer broken.

When `rerun_limit_hit` is set, latexmk stopped before references converged. That is usually an unresolved citation feeding a rerun loop, so fix the citations first and rebuild.

For anything beyond the obvious, hand `<root>.log` to `research-agents:latex-debugger`, which carries the full error taxonomy and quick-fix table. Do not restate that taxonomy here; two copies drift apart. When the `research-agents` plugin is not installed, report the raw evidence and stop rather than guessing.

## Step 4: Fix and rebuild

Apply the fix, rerun step 1, and repeat until the build is clean and fresh. Stop and ask the author when the fix is a content decision rather than a mechanical one:

- A citation key with no matching `.bib` entry — the right entry is the author's to choose, and inventing one fabricates a reference.
- A `\label` referenced from two places with different intent.
- A missing figure file that may be unrendered rather than misnamed.

## Step 5: Deliver

State the absolute PDF path and its modification time, the page count, and any undefined references or citations that survived. Open the PDF with `--open` when the author is at a desktop.

A page count matters more than it looks: NeurIPS, ICML, ICLR, and AAAI all enforce a hard page limit on the main body, and discovering an overrun at the submission deadline is avoidable.

## Constraints

- **Never report a build as done without `fresh: true`.** A stale PDF that reads as current is the failure this skill exists to prevent.
- **Never invent a citation key or a bibliography entry** to clear an undefined-citation warning. Flag it and let the author supply the source.
- Style and notation are out of scope. `\ref` versus `\cref`, booktabs, and abbreviation macros belong to `/latex-consistency`, which greps for them directly.
- `latexmk -c` cleans auxiliary files. Run it only when asked; it deletes the `.fls` this skill depends on.

## Requirements

`latexmk` and a TeX engine on `PATH`. All three major distributions ship latexmk: TeX Live (Linux), MacTeX (macOS), MiKTeX (Windows). `makeglossaries` ships with the same distributions and is needed only for documents using glossary packages without `automake`. The script itself uses only the Python standard library.

## Cross-references

- **Compilation errors you cannot read**: `research-agents:latex-debugger` parses the `.log` this skill produces and returns targeted fixes.
- **Formatting and notation consistency**: `/latex-consistency` after the paper compiles.
- **Bibliography correctness**: `/paper-references` verifies that the entries resolving those citations describe real papers.
- **Submission readiness**: `research-agents:pre-submission-audit` once the document builds clean.
