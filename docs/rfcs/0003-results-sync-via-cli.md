# RFC-0003: `experiment-tracker` calls a CLI instead of improvising one

**Status:** Draft
**Date:** 2026-09-03
**Affects:** `plugins/toolkit/commands/experiment-tracker.md`, `registry/index.json`, the site catalog

## Decision

`experiment-tracker` stops asking the model to derive experimental numbers and
starts calling a deterministic tool. A new `results` subcommand group in
[`latex-code-sync`](https://github.com/rpatrik96/latex-code-sync) extracts
metrics from run artifacts into generated `\newcommand` macros plus a JSON
manifest, and offers two CI gates: `results check` in the code repository,
`results audit` in the paper repository. The command becomes a three-mode
wrapper around that CLI, in the same shape `latex-sync` already uses.

The full CLI design is `docs/RESULTS_SYNC_DESIGN.md` in that repository. This
RFC records the catalog decision and its consequences here.

## Why now

`experiment-tracker` is 389 lines instructing the model to run `find`, `grep`
and `python3 -c` one-liners it composes fresh on each invocation, then map the
output onto paper tables by reading them. Three properties follow from that
shape:

- **Nothing is reproducible.** Two runs of the command against the same
  repository can select different rows from the same CSV, because which row
  counts as the result is decided in prose ("final row values / best values")
  rather than in a config.
- **Nothing is checkable.** The command ends by writing numbers into the
  `.tex`. No artifact records which run a number came from, so no later step can
  ask whether it is still true.
- **Nothing fails.** `verification-level: none` in its own frontmatter is
  accurate. There is no exit code anywhere in the workflow, so a stale table
  passes CI exactly as a fresh one does.

The catalog already contains the counterexample. `latex-sync` covers the
identical drift problem for equations and resolves it by calling a package with
`--strict` and a real exit code. Results are the same problem one artifact class
over, and the same treatment applies.

A second reason is that `latex-code-sync.toml` is currently read by nothing.
Projects in the wild carry one — `compositional-symmetries/` has a fully
populated `[equations.*]` table — while the package parses no TOML at all. The
results work adds the loader, so both features end up configured from one file
that the tool actually reads.

## What changes in this repository

**The command.** `plugins/toolkit/commands/experiment-tracker.md` is rewritten
to three modes:

| They said | Mode |
|---|---|
| "set up", "wire up my results", "configure this project" | **setup** |
| "update results", "sync experiments", "refresh the numbers" | **sync** |
| "check the numbers", "are the tables current" | **verify** |

**setup** keeps today's artifact-discovery bash. Scanning for W&B summaries,
MLflow runs and CSV headers is genuinely how a first config gets written, and
that is the one part of the current command doing work a script cannot do
unaided. Its output is now a `[results.*]` block rather than an edit to the
paper. **sync** and **verify** call the CLI.

**The registry.** `experiment-tracker`'s frontmatter changes, and
`scripts/generate-registry.py` and `scripts/generate-site.py` are re-run:

| Field | Before | After |
|---|---|---|
| `verification-level` | `none` | `formal` |
| `research-phase` | `experiment-design` | `paper-writing` |
| `tools` | absent | `["latex-code-sync"]` |

The `verification-level` change moves the skill between bands on the site, which
is the visible point of RFC-0002's taxonomy: a skill that now fails CI on stale
numbers should not sit beside skills that check nothing.

**No new skill.** The catalog count is unchanged at 38. This is a rewrite of an
existing entry, not an addition, and `figures` keeps plotting while
`experiment-tracker` keeps numbers.

## Options considered and rejected

**A new agora-local script under `plugins/toolkit/scripts/`.** The plugin
already ships `agora_feedback.py`, so the precedent exists. Rejected because it
would rebuild a LaTeX parser and a config format that `latex-code-sync` has, and
because the resulting tool would be installable only as part of a Claude Code
plugin — the CI gate has to run in repositories that have never heard of the
Agora.

**Leaving the command prompt-only and adding a verification step to the prose.**
Rejected because the failure is that a model re-derives the numbers, and a
prose instruction to double-check them is another invocation of the same
mechanism.

**Folding results into `latex-sync`.** One command covering equations and
results would match RFC-0002's consolidation instinct. Rejected because the two
have different users and different moments: equations are linked once during
implementation, results are re-synced after every run.

## Revisit when

- A project needs figures regenerated rather than copied. The CLI records a
  SHA256 and refuses a mismatch; it deliberately does not run the plotting
  command. If that becomes the common request, it belongs in a build file, and
  the answer here is a documentation pattern rather than a feature.
- Non-Python pipelines need extraction. The declarative config was chosen partly
  so nothing imports the experiment code, which should already cover this; a
  concrete failing case would be evidence otherwise.
