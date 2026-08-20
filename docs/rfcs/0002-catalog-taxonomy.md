# RFC-0002: Catalog taxonomy — four plugins by research phase, verification bands on the site

**Status:** accepted
**Date:** 2026-08-20
**Supersedes:** the five-plugin split (`academic`, `development`, `editorial`, `formatting`, `research-agents`) and the eleven-group site taxonomy.

## Decision

The marketplace is reorganised into **four plugins named for the phase of work they serve** — `discover`, `write`, `verify`, `toolkit` — and the site groups those same four, with skills sorted inside each group into **labelled bands by what the skill can check**. Five merges and one removal reduce the catalog to **47 skills, 35 public**.

## Why now

The 1.2.0 cut took the catalog from 83 skills to 56 and left the taxonomy describing a shape that no longer existed:

- Three site groups held **one skill each** (`ideation`, `documents-figures`, `dissemination`).
- **Six LaTeX skills sat in two different plugins** — `latex-build`, `latex-consistency` and `tikz-figures` in `formatting`; the three `latex-sync-*` in `development`.
- `academic` had become a junk drawer of 15: paper work, all four navigation skills, and `brainstorm`.
- `editorial` and `formatting` were three skills each, too small to be install units.
- `research-agents` held 28 entries, over half the catalog, mixing verification agents with `figure-storyteller`, `latex-debugger` and `voice-drift-detector`.
- `writing-polish` grouped three latex-sync skills, a LaTeX linter, a LaTeX debugger, a voice-drift detector and an audience checker under one heading.

Two taxonomies existed — plugins and site groups — and both described the same axis badly. They now do two different jobs.

## The plugins

| Plugin | What you install it for | Public |
|---|---|---|
| `discover` | Finding out what exists and deciding what to do | 5 |
| `write` | Producing and diagnosing the draft | 8 |
| `verify` | Checking what the draft claims | 12 |
| `toolkit` | The machinery around the paper | 10 |

Names are imperative rather than nominal (`verify`, not `verification`) so that `/plugin install verify@research-agora` states the marketplace's claim in the command itself.

**This breaks every existing install command.** Accepted because nothing is tagged, no GitHub release exists, and 1.2.0 has not been announced outside the repo — the cost never gets lower than it is today.

## The site groups

The four plugin names become the four site headings, and **group membership derives from plugin membership** rather than from a hand-maintained `SKILL_GROUP_MAP`. That removes the drift class `test_no_orphan_group_map_entries` currently guards against: a retired skill can no longer leave a mapping entry behind, because there are no entries.

Within each group, skills sort into bands:

- **Checks against ground truth** — runs a tool or script and compares against something outside itself.
- **Checks against a rubric** — applies a stated standard, with no external oracle.
- **Proposes for you to check** — generates a candidate whose verification is the reader's job.
- **Builds from your inputs** — produces an artifact from data you supplied.
- **Finds your way around** — navigation.

The band is the teaching layer: a visitor learns what `formal` and `layered` mean by seeing which skills sit under which heading, rather than by looking up a four-value enum that `registry/categories.json` never defined. The per-card `verification-level` badge stays.

## The merges

| New skill | Absorbs | Why |
|---|---|---|
| `latex` | `latex-build`, `latex-consistency`, `latex-debugger` | One `.tex` source, three lenses. `latex-build` already produced the log `latex-debugger` reads and deliberately deferred to it rather than duplicate its taxonomy. |
| `latex-sync` | `latex-sync-setup`, `latex-sync-annotate`, `latex-sync-verify` | Three steps of one workflow against one CLI, split across three files for no reason a user benefits from. Becomes one skill with `setup` / `annotate` / `verify` modes. |
| `figures` | `tikz-figures`, `figure-storyteller` | Both carry the Wong colorblind-safe palette and conference column widths **verbatim**. Two copies of a constant table drift; one does not. |
| `rebuttal` | `review-triage`, `reviewer-response-generator` | Already declared a two-step pipeline in their own front matter ("Step 1 of a 2-step pipeline"). `review-triage`'s Reviewer Complaint Decoder survives as the triage half. |
| `navigator` | `choose-skill`, `five-minute-win`, `whats-new` | Three public skills whose only job was navigating the catalog. `choose-skill` argued against itself in its own body: *"The Research Agora's discovery problem is real."* |

## The removal

`openreview-submission` goes. Its distinctive content is a five-row form-field table, and the limits it records are printed on the form the user is filling in. The remaining four steps ask a model to write keywords, a TL;DR under 250 characters, and a lay summary — from an abstract the author already wrote. The form-field table moves into `paper-abstract`, which already carries per-venue word limits.

## Options considered and rejected

| Option | Why it lost |
|---|---|
| **Three plugins** (research / writing / tooling) | `verify` stops being visible as its own install unit, which is the one thing the marketplace claims to be. A PI evaluating it could no longer see the bar at a glance. |
| **Keep five plugins, rebalance membership** | Lowest risk and the names stay wrong: `formatting` would hold `latex-sync`, and `academic` versus `research-agents` is not an axis a user navigates by. Deferring a rename gets more expensive after the first release, not less. |
| **Site groups mirroring plugins with no bands** | Simplest to build, but the browse page would then add nothing the install list does not already say, and `layered` stays meaningless to anyone who has not read `CONTRIBUTING.md`. |
| **Verification bands as the top level, phase inside** | The strongest statement of the thesis, and the worst ergonomics: someone arriving with a task ("I need to write related work") would scan every band to find their skill. |
| **Nominal plugin names** (literature / drafting / verification / tooling) | Reads as a conventional taxonomy and loses the imperative framing that makes `verify` land as a claim rather than a category. |

## Revisit when

- A fifth phase earns a plugin — most likely `theory`, if the theory agents (`proof-auditor`, `bounds-analyst`, `counterexample-searcher`, `theorem-dependency-mapper`, `intuition-formalizer`, and the theory micro-skills) grow past comfortable residence inside `verify`.
- A band goes empty or holds one skill, which is the signal that started this RFC.
- The internal micro-skill layer is redesigned. Eight remain, consumed only by orchestrators; whether they survive as separate files is deferred here, not settled.

## Deferred at the time, settled since

All three were taken up the same day; recorded here so the RFC does not read as
open work.

- **The micro-skill layer stays, minus one.** Every remaining micro-skill is a
  live worker of `parallel-audit` or `parallel-theory-audit`, so collapsing the
  layer would mean redesigning both orchestrators for no gain. Two were genuine
  near-duplicates: `proof-step-verifier` and `derivation-checker` asked the same
  question at different levels and their error enums had already drifted —
  `invalid_exchange` against `invalid_limit_exchange`, `algebraic_error` against
  `algebraic_manipulation`, for the same defects. They are one skill with a
  `level: logic | computation` flag and one shared vocabulary. Seven remain.
- **`assumption-analyzer` carries its own provenance gate now.** The rule that
  its output is a suggestion and never a finding existed only in
  `parallel-theory-audit`'s fan-in, so direct invocation — and `parallel-audit`,
  once it was repointed there — presented recalled hierarchies as findings about
  the paper. The gate is in the skill file, where every caller meets it.
- **`parallel-review` is retired.** Nothing invoked it: it appeared only in
  catalogs, the routing config and "called by" prose, the same profile as the
  three helpers this release removed. Its one distinct pass, `audience-checker`,
  moves into `pre-submission-audit`, which now runs six.
- **The speedup claims are gone rather than measured.** "2-3x", a phase table of
  minutes, "18 min → 8-9 min", "1.5-1.7x" — none had a measurement behind it.
  Publishing unverified performance numbers is the defect this marketplace
  exists to catch, so the numbers are replaced by what actually holds: fan-out
  bounds wall-clock by the slowest worker rather than the sum, setup and merge
  stay sequential and set the floor, and every worker is a separate model call,
  so it trades token cost for latency rather than saving both. Concurrency caps
  are real constraints and stay. Anyone wanting a figure is told to time their
  own runs.

## Still deferred

Nothing from this RFC. The `_TEMPLATE.md` scaffolding in `micro-skills/` and
`orchestrators/` is retained deliberately — it documents the worker and
orchestrator contracts for contributors.
