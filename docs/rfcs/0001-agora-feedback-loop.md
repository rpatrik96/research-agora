# RFC-0001: Agora Self-Improvement Feedback Loop

- **RFC**: 0001
- **Title**: Agora Self-Improvement Feedback Loop
- **Status**: Draft (MVP implemented — see §14)
- **Author**: Patrik Reizinger
- **Created**: 2026-07-30
- **Discussion**: PR for this document

---

## 1. Summary

The Agora currently has no signal about which of its skills are used, work, or
fail. This RFC designs a self-improvement feedback loop: users **opt in** to
local, content-free usage capture; their agents draft structured insights from
that local record; **nothing leaves the machine until the user inspects the
exact payload and explicitly submits it**; submissions land in the hub repo
through a sink abstraction (GitHub-native MVP, HTTP server fully specified but
stubbed); a scheduled, deterministic aggregation pipeline turns them into
`registry/feedback.json`; and the aggregate drives skill improvement,
deprecation, and new-skill proposals through the existing PR-based contribution
flow.

The loop is the first Agora feature that pressures design principle #1
("Zero-backend"). This RFC amends the principle rather than breaking it
silently: **GitHub remains canonical** — `registry/feedback.json` in the hub
repo is the single source of truth for aggregates regardless of how reports
travel — and any server is an optional deployment profile that syncs back to
GitHub.

## 2. Motivation

Three facts about the current repo make the case:

1. **The marketplace is flying blind.** `choose-skill` ships a hand-authored
   task-to-skill confidence table, and `whats-new` infers skill impact from
   commit messages, because no usage signal exists. Both are the loop's natural
   consumers, already waiting.
2. **The verification hierarchy has an empty slot.** PLATFORM.md defines L4
   *Consensus — community agreement*, but skills only use the
   formal/heuristic/layered/none subset. Community feedback is the first
   concrete mechanism that can ground an L4 badge in evidence rather than
   author declaration.
3. **The loop already ran once, by hand.** The maintainer analyzed ~19K local
   observations across ~30 projects and turned the patterns into four new
   skills and a rule file. That manual pass is precisely the pipeline this RFC
   automates and opens to the community.

The design also serves the position-paper thesis behind the Agora: evaluation
criteria should be *explicit and collectively negotiated*. A feedback loop
with a published schema, published scoring math, and human-gated lifecycle
decisions is that negotiation made operational. The standing caveat comes from
Goodhart (via Hardt): as soon as something becomes a benchmark, it detaches
from reality. §9 therefore treats every score as *one facet among several*,
never the sole ranking, and keeps objective, non-vote signals in the mix.

Benchmarks (Pillar 2) and feedback are complements, not rivals: benchmarks
measure capability *in vitro* on curated tasks; feedback measures usefulness
*in vivo* across real sessions — the transferability signal that SAGE
(Wang et al., 2025, arXiv:2512.17102) shows is the load-bearing measure of a
skill library's value.

## 3. Goals and non-goals

**Goals**

1. An evidence-based pipeline for improving, deprecating, and proposing skills.
2. A concrete implementation of verification level L4 (Consensus).
3. Full compatibility with the Agora's published privacy posture
   (`docs/privacy-gdpr.md`, `audit-my-setup`) and its GDPR-sensitive audience.
4. A sink-agnostic client, so hosting can evolve (GitHub → institute → cloud)
   without touching capture or consent.

**Non-goals**

- No automatic transmission of anything, ever. Submission is always a manual,
  reviewed act.
- No collection of prompts, file contents, file paths, or repository names.
- No public per-user reputation, points, or user leaderboards (§9.3).
- No automated skill deprecation or removal without a human decision (§10).
- No integration with Anthropic telemetry; the channels stay visibly distinct.

## 4. Design principles

1. **GitHub-canonical (amended zero-backend).** The default deployment needs no
   server and costs $0/month. Optional servers are deployment profiles of the
   HTTP sink; their aggregates sync back into `registry/feedback.json` by PR.
   Invariant: *the hub repo's `registry/feedback.json` is the single canonical
   aggregate, regardless of sink.*
2. **Consent gate.** Capture is off by default. Enabling it is explicit
   (`/agora-feedback enable`). Submission is a second, separate decision, made
   per report, after inspecting the exact serialized payload.
3. **Script-first.** Capture, spooling, validation, aggregation, and scoring
   are deterministic scripts (stdlib-only on the client). The LLM appears in
   exactly two places — drafting insights and curating aggregates — and both
   outputs pass through human review.
4. **Never block a session.** Capture hooks follow the established
   `... 2>/dev/null || true` posture and exit 0 unconditionally. A broken
   feedback pipeline must be invisible to normal skill use.
5. **Goodhart guardrail.** Feedback scores render as a facet (badge + filter),
   never as the default sort order of the marketplace.

## 5. Architecture

```
 user's machine                                  hub repo (GitHub)
┌───────────────────────────────────┐           ┌──────────────────────────────┐
│ hooks (PostToolUse Skill/Task,    │           │ issues labeled skill-feedback│
│        SessionEnd)                │  submit   │        │                     │
│   └─> spool ~/.agora/spool/*.jsonl│ ────────> │ aggregate-feedback.yml (cron)│
│         └─> /agora-feedback       │  (GitHub  │   └─> scripts/aggregate-     │
│              preview → review     │   issue │ │        feedback.py           │
│              gate → submit        │   HTTP  │ │   └─> bot PR updating        │
│                                   │   file) │ │       registry/feedback.json │
└───────────────────────────────────┘           │        │                     │
                                                │  site badges · maintainer    │
        optional HTTP sink (institute/cloud) ─> │  digest · whats-new ·        │
        syncs aggregates back by PR             │  choose-skill · lifecycle    │
                                                └──────────────────────────────┘
```

The pipeline is deliberately a second instance of the benchmarks shape the
repo already runs: PR-maintained data files in `registry/`
(`benchmarks.json`/`results.json` → `feedback.json`), a submission surface
(PR → labeled issue form), referential-integrity tests
(`test_benchmarks.py` → `test_feedback.py`), and site rendering joined in
`generate-site.py`.

## 6. Capture layer

**Hook events.** The `development` plugin ships `hooks/hooks.json` with two
entries, both invoking the bundled client
(`${CLAUDE_PLUGIN_ROOT}/scripts/agora_feedback.py capture`):

| Event | Matcher | What it yields |
|-------|---------|----------------|
| `PostToolUse` | `Skill\|Task` | Skill invocations (explicit and description-triggered) via the `Skill` tool; research-agents subagent completions via the `Task` tool |
| `SessionEnd` | — | Session count for the reporting period; spool flush |

`Stop` is deliberately avoided — it is commonly occupied in real setups
(continuation enforcers, VCS integrations), and the capture design must
compose with existing hooks. Matchers stay generic; all filtering happens
inside the script.

**Honesty about coverage.** Clients differ in how skills activate. The `Skill`
tool covers both slash-typed and description-triggered invocations where the
client routes skills through it; older flows that expand slash commands
directly into the prompt are invisible to `PostToolUse` and are an open
question (§13). Reports state what they measure; partial coverage is fine
because scoring is comparative, not absolute.

**What an event records** (one JSONL line in the spool):

```json
{"ts": "2026-07-30T14:02:11", "session": "3f9c2a1b", "event": "invocation",
 "skill": "paper-references", "outcome": "success", "error_code": null,
 "duration_bucket": "10-60s", "model": "sonnet"}
```

- `outcome` ∈ `success | partial | error | unknown`; `error_code` reuses the
  WORKER_PREAMBLE taxonomy verbatim (`INVALID_INPUT`, `TIMEOUT`,
  `SERVICE_UNAVAILABLE`, `SCOPE_EXCEEDED`, `CONFIDENCE_LOW`,
  `PARTIAL_RESULT`) so agent envelopes and feedback share one vocabulary.
- `duration_bucket` ∈ `<10s | 10-60s | 1-5m | >5m` — never precise durations
  in reports.
- Never recorded: prompt text, file contents, file paths, repository names.

**Insights are not captured by hooks.** They are drafted at review time
(§8) by the user's own agent reading the spool. This keeps hooks
deterministic and cheap, and places all LLM-generated content at the consent
point where the user reviews it anyway.

**Off by default.** The hook script exits 0 immediately unless
`~/.agora/config.json` has `"enabled": true` *and* `AGORA_FEEDBACK` is not
`0`. For users who never opt in, the hook's cost is one no-op process spawn
per matched tool call.

## 7. Local spool and report schema

**Spool.** `~/.agora/spool/events.jsonl`, deliberately in the home directory,
outside any project root — the same reasoning `privacy-gdpr.md` applies to
`.env` files: if it is not in the project tree, the agent does not read it
into context by accident. Full timestamps are fine here (the file never
leaves the machine); reports round to day precision. Retention: 90 days
rolling; submitted events move to `~/.agora/spool/archive/`;
`/agora-feedback purge` deletes everything.

**Report.** The unit of submission, assembled from the spool:

```json
{
  "schema_version": 1,
  "report_id": "r-8f3a1c2e-4b5d-4e6f-9a0b-1c2d3e4f5a6b",
  "created": "2026-07-30",
  "reporter": {
    "installation_id": "a1b2c3d4e5f60718293a4b5c6d7e8f90",
    "client": "claude-code",
    "marketplace_sha": "89b1ddf"
  },
  "period": {"from": "2026-07-01", "to": "2026-07-30", "sessions": 41},
  "consent": {"reviewed": true, "channel": "github-issue", "policy_version": 1},
  "skills": [
    {
      "skill": "paper-references",
      "skill_sha": "3b73527",
      "invocations": 12,
      "outcomes": {"success": 9, "partial": 2, "error": 1},
      "error_codes": {"SERVICE_UNAVAILABLE": 1},
      "duration_buckets": {"10-60s": 8, "1-5m": 4},
      "models": {"sonnet": 12},
      "criteria": {"declared": 4, "met": 3},
      "insights": [
        {"type": "improvement", "text": "bibtex-updater CLI flags changed; skill instructions cite the old ones", "confidence": 0.8},
        {"type": "missing-skill", "text": "no skill covers OpenReview rebuttal-diff checking", "confidence": 0.6}
      ]
    }
  ],
  "environment": {"os": "darwin"}
}
```

| Field group | Decisions |
|-------------|-----------|
| `skill` + `skill_sha` | The registry has no per-skill version field, so the skill file's git commit (best-effort from the installed marketplace checkout; `null` if unavailable) is the version pin. This implements for skills what `registry/BENCHMARKS.md` already mandates for benchmark results ("results are tied to specific skill versions/commits"). Aggregation can branch scores on SHA after a rewrite. |
| `installation_id` | Random 128-bit, generated at `enable`, user-resettable. Exists for dedup, rate caps, and unique-installation counts. Under GDPR it is pseudonymous personal data and is treated as such (§11). |
| Identity | With the GitHub sink, the submitting GitHub account is visible on the issue — a feedback submission is an attributable public contribution, like any OSS PR. The RFC states this plainly rather than pretending otherwise. Users who want pseudonymity can paste the payload from a secondary account, or wait for the HTTP sink. |
| `outcomes` / `error_codes` | WORKER_PREAMBLE taxonomy, verbatim. |
| `criteria` | The Test-Driven Research hook: where a session declared acceptance criteria before delegating (Pillar 3), "criteria met / declared" is an objective outcome signal, strictly preferable to satisfaction ratings. Optional. |
| `insights` | Closed type enum: `bug \| improvement \| docs-gap \| missing-skill \| overlap \| deprecation-signal \| praise`. Free text capped at 500 characters and PII-linted (§8). |
| `consent` | Records that the gate ran; `policy_version` forces re-consent when the schema or policy changes. |

## 8. Review gate: `/agora-feedback`

One skill (`plugins/development/commands/agora-feedback.md`,
`disable-model-invocation: true` — it never triggers implicitly) fronting one
stdlib-only script. Subcommands:

| Subcommand | Effect | Network |
|------------|--------|---------|
| `enable` / `disable` | Toggle capture; `enable` creates `~/.agora/config.json` with a fresh `installation_id` | none |
| `status` | Config, spool size, kill-switch state | none |
| `stats` | Local per-skill usage dashboard from the spool | none |
| `preview` | Assemble the report; the agent drafts insights from the spool; the user accepts/edits/deletes each one | none |
| `submit` | Render the exact final payload, verbatim; require explicit confirmation; deliver via the configured sink; archive the spool | only on confirm |
| `purge` | Delete spool, archive, and pending reports | none |

The submission walkthrough, in order: (1) `preview` builds counters and
drafts insights; (2) the user reviews each insight; (3) a PII lint pass
(regex: email addresses, `/home/...` and `/Users/...` paths, URLs carrying
query tokens) highlights hits and blocks until resolved or overridden;
(4) the full payload prints verbatim; (5) the user explicitly confirms;
(6) the sink delivers and returns a receipt (issue URL); (7) submitted events
move to the archive.

**Kill switches**, in order of precedence:

1. `AGORA_FEEDBACK=0` — disables capture and submission, overriding config.
2. `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` — disables the submit path;
   local capture and `stats` still work.
3. `~/.agora/config.json` `enabled: false` (the default) — no capture.

## 9. Scoring and voting mechanisms

### 9.1 Option space

| Mechanism | Signal | Pros | Cons | Verdict |
|-----------|--------|------|------|---------|
| Naive invocation counts | popularity | trivial | popularity ≠ quality; rich-get-richer | display only, never rank |
| **Wilson 95% lower bound on success rate** | quality | deterministic, explainable, conservative at small n | no priors, no decay | **MVP scoring** |
| Beta-Binomial posterior | quality | verification-level priors, credible intervals, exponential decay (half-life ≈ 180 days) | harder to explain | v2 |
| Elo / Bradley-Terry on pairwise choices | relative preference | grounded in real selection behavior (`choose-skill` picks among candidates) | needs pairwise data; Goodhart-prone | deferred; ethics in §13 |
| SAGE-style transferability | objective usefulness | hard to game with votes: success across distinct task-types, domains, installations | needs richer task labels than the spool has | v2 tie-breaker |
| Human votes (GitHub reactions) | sentiment | free, existing UI | brigading, low information | steward-weighted input to lifecycle reviews only |

MVP scoring, implemented in `scripts/aggregate-feedback.py`: with
`n = success + partial + error` and effective successes
`s = success + 0.5·partial`, the displayed score is the Wilson 95% lower
bound of `s/n`. It is deliberately conservative: a skill with 2/2 successes
scores below one with 18/20, which is the right cold-start behavior.

### 9.2 Combining agent and human signal

Agent-reported counters set the quantitative floor; they are behavioral,
cheap, and hard to argue with. Human judgment is *required* at every
lifecycle transition (§10) — no promotion, flagging, deprecation, or removal
happens automatically. This is the "collectively negotiated evaluation
criteria" of the position paper made operational: the numbers propose, people
dispose.

### 9.3 Reputation — deliberately absent

Chiu et al. (2025, arXiv:2512.04988) show what reputation dynamics do to
agentic labour markets: adverse selection, monopolization, price deflation.
A skill marketplace with public contributor reputation invites the same
failure modes plus brigading. Decision: **no public per-user or
per-installation reputation in v1.** The only per-installation state is
invisible: submission caps and anomaly quarantine. Revisit when stewards
exist (governance Phase 2).

### 9.4 Anti-gaming

- Per-installation cap: at most 8 reports per installation per aggregation
  window; excess reports are dropped deterministically (newest kept).
- Dedup on `report_id`; re-running aggregation is idempotent.
- Version pinning via `skill_sha` (extends the BENCHMARKS.md measure).
- Volume outliers (>3σ above median invocations per installation) are
  quarantined into the PR body for manual review instead of entering the
  aggregate.
- Sink-side rate limits (GitHub abuse limits for free; explicit limits in the
  HTTP sink).
- The facet-not-sort rule (§4.5).

### 9.5 Cold start, decay, silence

- No score is displayed below **n ≥ 5 unique installations**; the card shows
  a neutral "candidate" state instead. Nothing about a new skill should look
  like failure.
- Displayed stats use a 90-day rolling window. In v2 the posterior decays
  exponentially; a skill whose feedback goes silent drifts toward its prior,
  not toward zero — **silence is not failure**, it may be a stable skill in a
  quiet season.

## 10. Skill lifecycle

States, with *advisory* triggers computed by aggregation and *decisions* made
by humans:

| State | Advisory trigger | Decided by |
|-------|-----------------|------------|
| `candidate` | < 5 unique installations | automatic (display only) |
| `established` | Wilson lb ≥ 0.7 with ≥ 5 installations | automatic (display only) |
| `flagged` | Wilson lb < 0.5 with ≥ 10 reported invocations, or ≥ 3 unique installations filing `deprecation-signal` insights | trigger auto-opens a `lifecycle-review` issue; maintainer/steward decides |
| `deprecated` | — | human decision on the review issue; skill keeps a `status: deprecated` frontmatter marker, hidden from default site view, install warning |
| `removed` | two quarters deprecated | normal PR, human-merged |

Deprecation is a first-class feature, not an afterthought: unlike commercial
markets, science has no exit mechanism for bad methods — they persist
indefinitely unless someone builds the exit. The Agora builds it.

**L4 Consensus, operationalized.** A skill earns the `consensus` verification
badge when it is `established` with ≥ 20 successful reports across ≥ 5
unique installations. This is the first concrete criterion for PLATFORM.md's
L4 row, rendered alongside the existing formal/heuristic/layered/none
shields — author-declared rigor and community-evidenced usefulness are
different axes and both stay visible.

## 11. Privacy and GDPR

**Data minimization.**

| Collected (in a report) | Never collected |
|-------------------------|-----------------|
| Skill names + git SHAs, counters, outcome/error codes, bucketed durations, model names, day-precision dates, user-reviewed insight text | Prompts, file contents, file paths, repository names, precise timestamps, machine identifiers, IP-derived location (GitHub sink sees only what GitHub always sees) |

**Lawful basis** is consent (Art. 6(1)(a)): capture and submission are both
explicit opt-ins, revocable at any time (`disable`, `purge`, issue deletion
on request). `installation_id` is treated as pseudonymous personal data.

**Controller analysis per sink.** GitHub sink: the user self-publishes to a
public repository — the same act, with the same GDPR posture, as opening any
OSS pull request; the payload is user-reviewed before publication. HTTP sink:
the operator becomes a data controller and owes a privacy policy, retention
limits, and erasure — which is why the sink spec (§12) includes
`DELETE /v1/installations/{id}` as a required endpoint, not a nicety.

**k-anonymity.** Published per-skill breakdowns are suppressed below
k = 3 unique installations; the site renders no feedback badge below that
threshold (the `candidate` state covers it).

**Reconciliation with the published stance.** `docs/privacy-gdpr.md` and
`audit-my-setup` tell users to disable telemetry — advice this RFC keeps.
The Agora channel is different in kind, and the docs must say so in the same
breath, or the marketplace ships a self-contradiction (its own audit skill
would penalize its own feature). Shipped with this RFC:

- `docs/privacy-gdpr.md` gains a "Research Agora Feedback (Opt-In)" section
  distinguishing the channel from Anthropic telemetry (off by default,
  local-only capture, payload-inspected, manually submitted) and adds
  `AGORA_FEEDBACK=0` to the kill-switch block.
- `audit-my-setup.md`'s privacy rubric is amended: an *enabled* Agora
  feedback channel with the review gate intact does not reduce the privacy
  score; an auto-submitting configuration would.

## 12. Sink abstraction and deployment profiles

**Interface** (language-neutral): `submit(report) → receipt`,
`healthcheck()`, `policy() → {schema_version, max_report_bytes}`. The sink is
selected in `~/.agora/config.json`.

### 12.1 GitHub sink (MVP, canonical)

A submission is a GitHub issue: label `skill-feedback`, JSON payload in a
fenced block, created via `gh issue create` — or pasted manually through the
`skill-feedback.yml` issue form by users who prefer the browser (or a
secondary account). Alternatives considered:

| Option | Why not |
|--------|---------|
| GitHub Discussions | GraphQL-only tooling, no label-driven CI triage, category setup |
| PR appending to a `feedback-inbox/` | fork+PR friction, merge conflicts, routes every report through the single-maintainer CODEOWNERS bottleneck |

Ingested issues remain open until the aggregate PR merges; auto-closing with
a receipt comment is M3 polish. Idempotent dedup makes re-ingestion safe
either way.

### 12.2 HTTP sink (specified, stubbed)

| Endpoint | Behavior |
|----------|----------|
| `POST /v1/reports` | Validate against schema; 202 + receipt id; append-only store |
| `GET /v1/policy` | Schema version, size caps, retention policy |
| `GET /v1/skills/{name}/stats` | Public aggregates (k ≥ 3 suppression applies) |
| `DELETE /v1/installations/{id}` | GDPR erasure — required, not optional |

Auth ladder: anonymous + rate-limited → API token on registration → GitHub
OAuth device flow. Storage: append-only reports (SQLite, single container;
Postgres when scale demands). **The server is never a second source of
truth**: a scheduled exporter opens a PR syncing its aggregates into
`registry/feedback.json`.

### 12.3 Deployment profiles

- **A — GitHub-native** (default, canonical): $0, no auth beyond GitHub
  accounts, portable.
- **B — institute self-hosted**: the HTTP sink as a lab-private aggregator
  with periodic GitHub sync. Honest assessment for the MPI cluster: only the
  login node has outbound network, under a 4 GiB per-user memory cap, and
  compute nodes are offline — a container on lab web infrastructure (not the
  cluster) is the realistic shape. Institutional runway is finite (maintainer
  relocation ~Sept 2026), so profile B is a *profile*, never the primary
  path, and must stay portable: single container, SQLite, no
  institute-specific assumptions.
- **C — hosted service** (long-term): small cloud deployment, open-access
  reads, authenticated writes, still GitHub-synced.

## 13. Aggregation, consumption, and closing the loop

**Aggregation.** `.github/workflows/aggregate-feedback.yml` (weekly cron +
manual dispatch — the repo's first scheduled workflow; staged in
`.github/workflows-pending/` until a maintainer installs it, because the
authoring session's token lacked the `workflow` scope) runs
`scripts/aggregate-feedback.py`: fetch open `skill-feedback` issues, extract
fenced JSON, validate, dedup, cap, quarantine outliers, compute Wilson
bounds, and open a bot PR updating `registry/feedback.json`. The PR body is
the digest: per-skill deltas, new insights, lifecycle triggers. A human
merges it — the BDFL-phase review model, by construction not a bottleneck
because reports batch into one weekly PR. `feedback.json` is a separate file
because `generate-registry.py` clobbers `index.json` wholesale on every CI
run — the same reason `results.json` is separate.

**Consumption.**

- **Site**: `generate-site.py` joins `feedback.json` exactly as it joins
  benchmarks — a community badge (score + "n installations") on skill cards
  when k ≥ 3, plus aggregate counts in the stats header.
- **`whats-new`**: ranks new skills by "new *and* successfully used" instead
  of commit-message inference.
- **`choose-skill`**: hand-authored confidence values annotated (later
  replaced) by empirical success rates.
- **Maintainer digest**: the weekly bot PR; monthly, insights cluster into
  `skill-improvement` issues.
- **New skills**: `missing-skill` insights clustering across ≥ 3
  installations auto-open an issue with the existing `skill-proposal` label.
- **Agent-assisted curation (M5)**: a `skill-doctor` command drafting
  improvement PRs from a skill file plus its accumulated feedback — human
  review mandatory. This is the ADAS/meta-agent trajectory (Hu et al., 2024,
  arXiv:2408.08435) applied to a skill archive, with the human gate keeping
  it a tool rather than an autonomous editor.

**Open questions.**

1. Implicit skill activation that bypasses the `Skill` tool is invisible to
   capture — is prompt-side detection worth its privacy surface?
2. Spoke (third-party) skills: feedback via the hub (one inbox, foreign
   skills) or per-spoke (fragmented)? Leaning hub, with `repo` added to the
   per-skill report block.
3. Model-version confounds: a skill's success rate shifts when models change
   under it; `models` in the report enables per-model splits, but when to
   surface them is open.
4. Can `choose-skill` selections ethically feed pairwise preference data
   (Bradley-Terry) without turning skill choice into a surveilled act?
5. Re-consent mechanics on `policy_version` bumps: block submission until
   re-confirmed (current design) or re-run `enable`?

## 14. Roadmap and MVP status

| Milestone | Scope | Status |
|-----------|-------|--------|
| M0 | This RFC; `docs/rfcs/` process bootstrap | this PR |
| M1 | Capture client + spool + `/agora-feedback` + GitHub sink + issue form | **implemented in this PR** |
| M2 | Aggregation script + scheduled workflow + `registry/feedback.json` + `tests/test_feedback.py` + site badges (Wilson) | **implemented in this PR** |
| M3 | Beta-Binomial scoring, decay, lifecycle-review automation, issue auto-close, `whats-new`/`choose-skill` integration, L4 `consensus` badge, `registry/FEEDBACK.md` | next |
| M4 | HTTP sink reference implementation + deployment profiles + erasure endpoint | later |
| M5 | `skill-doctor` agent-assisted curation, spoke-skill feedback, cross-marketplace federation | later |

Alternatives considered and rejected: fully automatic telemetry (contradicts
the published privacy stance); piggybacking Anthropic telemetry (opaque,
wrong data controller); server-first architecture (breaks $0 hosting before
the loop has proven value); pure star-voting (no behavioral grounding,
brigading-prone).

**Failure modes tracked**: low adoption (mitigated by selfish-first local
`stats` — capture pays off without ever submitting — plus reciprocity: public
aggregates, contributor credit, triage priority for submitters'
`missing-skill` proposals; the "whole product" lesson is that infrastructure
without an incentive layer stalls); poisoning (caps, quarantine, human gate);
Goodhart drift (facet-not-sort, objective complements, periodic criteria
renegotiation); maintainer bottleneck (weekly batching, stewards);
schema drift (`schema_version` + backward-compat tests); client specificity
(hooks are Claude Code-specific while the SKILL.md standard has no telemetry
hook — worth raising upstream with AgentSkills.io).

## 15. References

- PLATFORM.md — pillars, verification hierarchy (L4), governance, roadmap.
- `registry/BENCHMARKS.md` — the sibling pipeline and its anti-gaming
  measures.
- `plugins/research-agents/config/WORKER_PREAMBLE.md` — structured envelope
  and error-code taxonomy.
- `docs/privacy-gdpr.md` — the privacy posture this design preserves.
- Wang et al., *Reinforcement Learning for Self-Improving Agent with Skill
  Library* (SAGE), arXiv:2512.17102, ACL 2026.
- Chiu, Zhang, van der Schaar, *Strategic Self-Improvement for Competitive
  Agents in AI Labour Markets*, arXiv:2512.04988.
- Hu, Zhou, Clune, *Automated Design of Agentic Systems* (ADAS),
  arXiv:2408.08435.
- Jain et al., *LiveCodeBench*, arXiv:2403.07974 — temporal-segmentation
  anti-contamination, already adopted by the benchmarks pillar.
