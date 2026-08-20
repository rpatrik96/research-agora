# Changelog

## [1.2.0] - 2026-08-20

### Removed
- **`office` plugin** (`docx-create`, `pptx-create`, `xlsx-create`) — 1,412 lines
  documenting python-docx, openpyxl and python-pptx, carrying no research- or
  repo-specific knowledge. Anthropic's own `document-skills` covers the ground.
  The `iem-talk` slide template moved to `plugins/academic/templates/slides/`.
  What to use instead: `document-skills`, or `/paper-slides` for a talk built
  from a paper.
- **`reviewer-response-generator`'s Quick Mode** — it drafted rebuttal text with
  "no external evidence gathering" and triggered on a tight deadline, which is
  when an invented number is most likely to reach a reviewer. The agent now has
  one evidence-backed path; every quantitative claim is sourced from your
  results, your code, or a retrieved paper, and an unfilled
  `[EVIDENCE NEEDED: …]` marker is a valid output.

### Deprecated
- **`/paper-introduction`** — an introduction frames novelty and states
  contributions, which `docs/concepts.md` puts in the Protect column and
  `docs/verification.md` records as having no automated oracle. Nothing in the
  skill checked what it wrote. **Use `/paper-review`**, which now carries the
  contribution rubric and the overclaiming checklist this skill held.
- **`/paper-discussion`** — its output format asked for "any new `\citet` or
  `\citep` references that need BibTeX entries" with nothing verifying they
  exist. **Use `/paper-review`**, which now carries the limitation categories
  and the be-specific rules.

Both still work and will be removed in a future release.

### Changed
- **`/paper-abstract` is diagnosis-only.** It audits an abstract you wrote
  against the five-part structure, venue word limits, specificity, and claim
  support. It no longer generates one. `task-type` moves to `diagnosis`.
- **`/literature-synthesizer` is discovery-only.** Multi-query arXiv search,
  programmatic dedup, and the paper approval gate stay; the narrative
  related-work prose is gone. `paper-references` verification is now a required
  final step rather than an optional dependency, so every entry it hands back
  has been checked. `task-type` moves to `analysis`.
- **`bounds-analyst` is `verification-level: heuristic`, not `formal`.** Its
  known-optimal-rate tables are recalled from model memory, and it was attaching
  those citations to OPTIMAL/SUBOPTIMAL verdicts. Rates must now be retrieved
  before they support a verdict; an unretrieved comparison reports `UNVERIFIED`.
- **`parallel-theory-audit` tags its inputs by provenance before fan-in.** It
  spawns `assumption-analyzer` and `bounds-analyst`, neither of which checks
  anything against the paper, and their recalled output can no longer reach the
  criticality score or the T1–T6 level.
- **`intuition-formalizer` emits a draft theorem statement**, not
  "publication-ready LaTeX". Nothing in it proves the statement.
- Corrected the NeurIPS 2025 hallucinated-citation figure in
  `docs/verification.md` and `/five-minute-win`: 100 hallucinated citations
  across 51 accepted papers, from a scan of all 4,841, now cited to GPTZero.
  The previously published "53 papers" was uncited and wrong.
- Fixed the `he2020moco` BibTeX exemplar in `/literature-synthesizer`, which
  cited the 2019 preprint under a 2020 key six lines below the rule "prefer
  published versions over arXiv preprints". Removed author reputation from its
  relevance ranking.
- Advertised skill counts now come from `registry/index.json` and are tested.
  The published figures had drifted to 61, 74, 80+ and 83 across nine files.

### Added
- `deprecated`, `superseded-by` and `deprecated-in` skill metadata, propagated
  to the registry and rendered on the site. `/whats-new` reads the
  `### Deprecated` and `### Removed` sections above.
- `/paper-review` gained a Contribution-Claim Audit and a Limitations Audit,
  carrying forward what the deprecated drafting skills encoded.
- `test_no_orphan_group_map_entries` — every `SKILL_GROUP_MAP` key must name a
  live skill. Its absence is why the February consolidation left 34 dangling
  references behind.
- `TestAdvertisedCounts` — the README badge, any "<N> skills" claim in tracked
  Markdown, and the marketplace plugin count must all match the registry.

## [1.0.0] - 2026-03-15

### Added
- 74 skills across 6 plugins (academic, development, formatting, office, research-agents, editorial)
- Static website with search and filtering at rpatrik96.github.io/research-agora
- Registry system with auto-generated index and category taxonomy
- 22 specialized research agents for paper analysis
- 12 micro-skills for parallel processing pipelines
- 4 orchestrators for multi-agent coordination
- Cross-platform support (Claude Code, Cursor, Gemini CLI, Copilot)
- Comprehensive test suite (414+ tests)
- PLATFORM.md design blueprint
- CONTRIBUTING.md and INTEROP.md documentation
