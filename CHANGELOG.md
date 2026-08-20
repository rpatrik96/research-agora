# Changelog

## [1.2.0] - 2026-08-20

### The rule this release applies

A skill stays in the Agora only if something can check what it produced. A
generative skill ships with the mechanism that verifies its output — a script
that extracts the numbers, a tool that resolves the citation — or it does not
ship. Where a tool-backed skill and a freehand one do the same job, the
tool-backed one is the product.

The rule now lives in `README.md` and `CONTRIBUTING.md`, and it governs what
gets accepted as well as what gets retired. This release is that rule applied
to the existing catalog in one pass: **80 skills → 63, 59 public → 44.**
There is no second wave planned.

### Removed

**Generation with nothing to check it**

- `/paper-introduction`, `/paper-discussion` — an introduction states a paper's
  novelty and a discussion states its limitations; `docs/concepts.md` puts both
  in the Protect column and `docs/verification.md` records that novelty has no
  automated oracle. `paper-discussion` also asked for "any new `\citet` or
  `\citep` references that need BibTeX entries" with nothing verifying they
  exist. **Use `/paper-review`**, which now carries their contribution rubric,
  overclaiming traps, and limitation categories.
- `theory-connector`, `proof-strategy-advisor` — both hand back ready-to-cite
  attributions recalled from model weights, never retrieved.
  `proof-strategy-advisor` names real papers in three tables while its own body
  says *"This is an active research support tool, not a verification tool"* and
  its metadata said `task-type: verification`. **No replacement**; retrieve the
  reference yourself, then run `/paper-references`.
- `perspective-synthesizer` — emitted paste-ready related-work LaTeX
  (`\citet{paperA} report [result], while \citet{paperB} observe [opposite]`)
  with no faithfulness check. **Use `/literature-synthesizer`** for verified
  discovery, then write the synthesis yourself.
- `/paper-poster`, `/paper-slides`, `/science-gif` — all three restate a paper's
  claims in another medium with nothing checking the restatement is faithful,
  and all three carried `verification-level: none`. `science-gif` additionally
  defaulted two of its five code examples to simulated data. **No replacement**
  for poster and GIF; `figure-storyteller` reads real data files and stays.

**No research-specific knowledge (the `pr-automation` rule, applied again)**

- `/python-cicd` — 134 lines of black/isort/flake8 boilerplate. The repo's own
  `.pre-commit-config.yaml` uses none of those tools. **Use your project's
  existing linter config.**
- `/commit` — standard `git add`/`git commit` with a message table.
  **Claude writes commits without it.**

**Obsolete — the model does this unaided now**

These were designed when a skill file was how you got structured, careful
output. That is no longer where the leverage is: a current model given the
same one-line request produces the same result, so the file only adds a
template and a maintenance cost.

- `/paper-summarizer` — "summarize this paper: contribution, method, results,
  limitations" is the most default task there is. Its one arXiv MCP mention was
  a retrieval suggestion, never an invocation.
- `/review-prompt` — critiquing an underspecified prompt is default behavior,
  and the underlying problem shrinks with every model release.
- `/register-translator` — "rewrite this section as a blog post, keep every
  number" needs no skill file.
- `reader-simulation`, `audience-checker`'s overlap partner — "read this as a
  second-year PhD student and tell me where you get lost" gets the same
  walk-through without inventing comprehension percentages.
- `redundancy-radar` — asked for "[N]% semantic overlap" it has no way to
  compute, which invites fabricated precision. "Where am I repeating myself?"
  answers it honestly.
- `content-archaeologist` — its >70% / 40-70% / <40% similarity bands are
  unmeasurable; clustering posts into chapters is a one-line request.

**Duplicated by a tool-backed skill**

- `/editorial-brain` — asked the model to eyeball clarity metrics that
  `/writing-verify` computes (passive %, hedges, fillers, Flesch-Kincaid
  against per-section targets). **Use `/writing-verify`** to score and
  **`/writing-diagnosis`** to remediate. `/writing-diagnosis` loses
  `disable-model-invocation`, so the editorial plugin keeps an entry point the
  model can reach on its own.

**Earlier in this release**

- `office` plugin (`docx-create`, `pptx-create`, `xlsx-create`) — 1,412 lines
  documenting python-docx, openpyxl and python-pptx. The `iem-talk` slide
  template went with it. **Use Anthropic's `document-skills`.**
- `reviewer-response-generator`'s Quick Mode — it drafted rebuttal text with
  "no external evidence gathering" and triggered on a tight deadline, which is
  when an invented number is most likely to reach a reviewer. The agent now has
  one evidence-backed path, and an unfilled `[EVIDENCE NEEDED: …]` marker is a
  valid output.

### Deprecated

Nothing is currently deprecated. `/paper-introduction` and `/paper-discussion`
were marked deprecated earlier in this release and are removed above; their
replacement path is unchanged.

### Changed

- **`/paper-abstract` is diagnosis-only.** It audits an abstract you wrote
  against the five-part structure, venue word limits, specificity, and claim
  support. It no longer generates one.
- **`/literature-synthesizer` is discovery-only.** arXiv search, programmatic
  dedup and the approval gate stay; the narrative prose is gone, and
  `paper-references` verification is now required rather than optional.
- **`bounds-analyst` is `task-type: analysis`.** It proposes rate comparisons
  for a human to check; it is not a verifier, and its metadata said it was.
- `/writing-diagnosis` is now model-invocable, replacing `/editorial-brain` as
  the editorial plugin's automatic entry point.
- `CLAUDE.md`'s script-first guidance no longer lists writing paper sections or
  generating rebuttals as LLM-appropriate work.
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
- `TestSpawnTargetsResolve` — every skill an orchestrator spawns must resolve
  to a live registry entry, across all three spawn syntaxes in the repo
  (`SPAWN_SUBAGENT`, `SPAWN_TASK`, and the bare `SPAWN:` that
  `parallel-theory-audit` uses). The previous test asserted only that the
  literal string `skill:` appeared, and never ran against two of the four
  orchestrators — so every dangling target passed. This is the February 2026
  defect (`8787d48` deleted `clarity-optimizer` while `pre-submission-audit`
  still spawned it) turned into a red test.
- The retirement rule, stated in `README.md` and `CONTRIBUTING.md`, with a
  deprecation policy: a deprecated skill keeps working for at least one minor
  release, the CHANGELOG names its replacement or says there is none, and the
  file stays in git history under MIT.
- **`scripts/limpid_bridge.py`** — an optional bridge to the
  [limpid](https://github.com/rpatrik96/limpid) CLI. Where limpid is installed
  (`$LIMPID_CLI` or on `PATH`), `/writing-verify` uses it instead of
  `writing_verify.py`: same dimensions, but line-anchored findings and voice
  guards that stop it penalising scope-hedging, paired em-dashes, and long
  sentences that resolve. `/writing-diagnosis` uses its findings as evidence for
  the seven mechanically-detectable patterns. limpid is **not** a dependency —
  it is not on npm, and every failure path falls back to `writing_verify.py`
  with no change in behaviour.
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
