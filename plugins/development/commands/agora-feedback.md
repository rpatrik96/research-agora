---
name: agora-feedback
description: |
  Opt-in, review-gated usage feedback for Research Agora skills (RFC-0001).
  Use when asked to "enable agora feedback", "share skill feedback",
  "show my skill usage stats", "submit agora feedback", "report skill usage",
  "disable feedback capture", or "purge my feedback spool".
  Nothing is ever sent without the user reviewing the exact payload and
  explicitly confirming.
model: sonnet
disable-model-invocation: true
metadata:
  research-domain: general
  research-phase: implementation
  task-type: automation
  verification-level: heuristic
---

# Agora Feedback

> **Self-dogfooding note:** This skill is how the Agora learns which of its
> skills earn their place. Aggregated, reviewed reports drive skill
> improvement, deprecation, and new-skill proposals — see
> `docs/rfcs/0001-agora-feedback-loop.md` for the full design.

You operate a strict consent pipeline. All mechanics are handled by the
bundled deterministic script — never reimplement them ad hoc, and never send
anything on the user's behalf without the explicit confirmation step below.

```
SCRIPT="${CLAUDE_PLUGIN_ROOT}/scripts/agora_feedback.py"
```

## Ground rules (non-negotiable)

1. **Capture is off by default.** Only `enable` turns it on, and only when the
   user asks for it.
2. **Submission is a second, separate decision.** Never chain
   `submit --confirm` onto anything. The user must see the exact payload
   first and explicitly say to send it.
3. **Respect the kill switches.** If `AGORA_FEEDBACK=0` or
   `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` is set, say so and stop; do
   not suggest unsetting them.
4. **Reports are content-free.** Counters, outcome codes, and short
   user-reviewed insights only. If the user tries to include prompts, file
   paths, or data, refuse and explain why.

## Subcommands

| User intent | Run |
|-------------|-----|
| Opt in to local capture | `python3 "$SCRIPT" enable` |
| Stop capturing | `python3 "$SCRIPT" disable` |
| Check configuration | `python3 "$SCRIPT" status` |
| Local usage dashboard (no network) | `python3 "$SCRIPT" stats` |
| Build a report for review | `python3 "$SCRIPT" report` |
| Add/remove/list insights | `python3 "$SCRIPT" insight add <skill> <type> "<text>" --confidence 0.8` |
| Show payload without sending | `python3 "$SCRIPT" submit` |
| Send after explicit user confirmation | `python3 "$SCRIPT" submit --confirm` |
| Delete all local feedback data | `python3 "$SCRIPT" purge` |

Insight types: `bug`, `improvement`, `docs-gap`, `missing-skill`, `overlap`,
`deprecation-signal`, `praise`. Text is capped at 500 characters and
PII-linted; the script blocks submission on suspected personal data.

## Submission walkthrough

When the user wants to submit feedback:

1. Run `report`. It aggregates the local spool into per-skill counters and
   writes a pending report.
2. **Draft insights** from what you can see in the spool aggregates (recurring
   error codes, skills with poor outcomes, gaps the user mentioned). Propose
   each one to the user; add only what they approve, via `insight add`.
   Insights must describe the *skill*, never the user's project or data.
3. Run `submit` (no flag). Show the user the exact payload it prints, in
   full. Do not summarize it — the point of the gate is that they see what
   leaves the machine.
4. Only if the user explicitly confirms, run `submit --confirm`. Report the
   receipt (issue URL) back.
5. If the GitHub CLI is unavailable, the script writes a manual-paste file
   and prints the issue-form URL — relay both to the user.

## What this is not

- Not Anthropic telemetry: `DISABLE_TELEMETRY=1` and this channel are
  unrelated; enabling one says nothing about the other.
- Not automatic: there is no background upload, no scheduled submission, no
  auto-consent. Deleting `~/.agora/` removes every trace.
- Not identity-free on the GitHub sink: submitting creates a public issue
  from the user's GitHub account, like any OSS contribution. Say this before
  the first submission; users wanting pseudonymity can paste the payload from
  another account.

## Error handling

- Script missing or errors: report the failure honestly; never fall back to
  hand-rolling a submission.
- Empty spool: tell the user capture has recorded nothing yet (or was never
  enabled) and how to enable it.
- PII lint block: show the flagged strings, help the user rephrase the
  insight, re-run. `--allow-pii` exists but only the user may request it.
