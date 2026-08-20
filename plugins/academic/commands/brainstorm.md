---
name: brainstorm
description: |
  Checkpoint-gated interactive brainstorming for research and knowledge-organization
  decisions: framing a problem, exploring the option space, and choosing a direction
  WITH the user rather than for them. Use when asked to "brainstorm", "think through
  options", "explore approaches", "help me decide", "what's the best way to
  structure/represent/organize X", "weigh alternatives", "design a study/benchmark/
  taxonomy", or when a task's hardest part is a decision the user must own.
  Supports optional multi-agent debate (opposing-prior proposers + a fact-checking
  devil's advocate) between checkpoints. For software-implementation design and specs,
  defer to superpowers:brainstorming if that plugin is installed — this skill owns
  research and representation decisions, not code architecture.
model: opus
metadata:
  research-domain: general
  research-phase: ideation
  task-type: analysis
  verification-level: heuristic
---

# Brainstorm

Interactive ideation with a contract: the agent explores, researches, and debates freely *within* a phase — but every phase ends at a user checkpoint, and no deliverable exists until the user has chosen a direction at one.

> **LLM-required**: Option generation, trade-off analysis, and adversarial critique require judgment. No script alternative.

<HARD-GATE>
Do NOT produce the deliverable (the document, the restructure, the code, the design) until the user has picked a direction at a checkpoint. Exploration, research, and agent debates are always allowed; acting on their conclusions without a user choice is not. If the user is unavailable, stop at the checkpoint and present — never "provisionally proceed."
</HARD-GATE>

## Core Philosophy

Brainstorming fails in two symmetric ways. **Autonomous drift**: the agent explores, converges on its own favorite, and presents a fait accompli — the user rubber-stamps a decision they never actually made. **Interrogation fatigue**: the agent asks twenty serial questions the user doesn't care about, outsourcing thinking back to the person who asked for help. The contract that avoids both:

1. **Ask only what is genuinely user-owned.** Taste, priorities, constraints, appetite for maintenance — ask. Facts checkable against files or the web — check them yourself and report. Never ask a question whose answer you could have looked up.
2. **Frame serially, then batch.** During Phase 1 the questions are one at a time — framing questions build on each other, and a wrong frame poisons everything downstream. From Phase 4 onward, batch up to four decisions per checkpoint, each with 2–4 concrete options and a marked recommendation.
3. **Findings that reshape the option space surface immediately** — not at the next scheduled checkpoint. If exploration reveals the question is different from what the user asked, that IS the next checkpoint.
4. **Divergence is cheap, convergence is the user's.** Generate options wide (personas, agents, literature); the choice among survivors always lands on the user.

## Phases

| Phase | Agent may | Must end with |
|---|---|---|
| **1. Frame** | Read context: the files/repo/notes involved, prior decisions, constraints already recorded | Serial clarifying questions (one at a time), then a checkpoint restating the problem; offer the agent debate here if warranted (see below) |
| **2. Explore** | Research ground truth: survey the actual artifacts, prior art, tool capabilities; verify what exists vs. what is assumed | Findings report (inline, brief) — escalate to a checkpoint only if the frame changed |
| **3. Diverge** | Generate candidates inline; run the agent debate only if the user opted in | Synthesis of 2–3 surviving options |
| **4. Choose** | — | Checkpoint: batched options with trade-offs, previews where structure is visual, a recommendation; user picks |
| **5. Converge** | Detail the chosen option; resolve its open parameters | Checkpoint: detailed design approved |
| **6. Record** | Write the decision record; hand off | Deliverable + record of what was rejected and why |

Phases compress for small decisions (1→4→6 in one sitting) but never skip a Choose checkpoint.

## The Debate Protocol (Phase 3)

**Default: inline.** Argue the opposing personas yourself in the main context — assign each a prior, steelman each, then attack both. This is cheap and usually sufficient.

**Escalate to agents only by user opt-in.** When Phase 1 reveals a genuinely contested option space — high stakes, real disagreement between defensible designs, factual claims that need independent verification — offer the full debate at the Frame checkpoint, **with a rough cost estimate** (a two-proposer + critic run is on the order of hundreds of thousands of subagent tokens). The user decides whether the decision is worth it. Never dispatch the debate unoffered.

When the full debate runs:

1. **Opposing-prior proposers (parallel).** Two (or three) agents, each ASSIGNED a prior that brackets the space ("metadata-first" vs. "prose-first"; "buy" vs. "build"; "formalize" vs. "measure"). Each must: argue its position as well as it can be argued, ground every claim in files it actually read or sources it actually verified, and end with the 3 strongest objections to its own design. Read-only mandate — proposers never edit.
2. **Adversarial verification (sequential).** A devil's-advocate agent receives both proposals compressed, with an explicit fact-check list: every load-bearing factual claim (a tool capability, a file's contents, a feature's existence) gets verified against ground truth. It must rule on each disagreement axis — which side survives, under what condition the loser would win — and steelman the best hybrid. **Every attack must be labeled *disproven* (verified false) or *unverified* (no evidence either way): absence of precedent is a verification cost, not a counterargument, and the two must never be blurred.** No both-sides mush.
3. **Convergence is signal.** Where adversarial proposers independently agree, treat that as settled and spend the user's attention only on the axes where they split.

Forward into EVERY agent prompt: the domain constraints, the user's recorded rules, and an anti-fabrication directive ("if you claim a capability, cite where you verified it") — global rules do not reach subagents on their own.

If the research-agents plugin is installed, use `devils-advocate` for step 2; otherwise run the personas inline.

## Checkpoint Mechanics

- Phase 1: one question per message; each may build on the previous answer. Everywhere else: use the structured-question tool (AskUserQuestion or equivalent) with up to four batched decisions when options are enumerable; free-text when the decision needs the user's own words.
- **Previews are mandatory whenever options differ in shape** — a structure, layout, or document skeleton is judged by looking at it, not by its description. Sketch the actual markdown/mockup in each option's preview.
- Multi-select when preferences are not mutually exclusive; always mark a recommendation and give the reason inline.
- After a checkpoint: restate what got locked, in one line, before moving on. Locked decisions are not re-litigated; keep a short discard ledger (option → why rejected) so late arrivals don't resurrect them.

## The Decision Record (Phase 6)

Write where the project keeps decisions (docs/, the vault note, an ADR file — follow project convention; ask once only if none exists):

- The decision, in one sentence, dated
- Options considered and why each lost (from the discard ledger)
- The conditions under which this should be revisited
- What was deliberately deferred

Implementation of the chosen design starts only on explicit request — the record is the deliverable of this skill.

## Anti-Patterns

| Anti-pattern | Instead |
|---|---|
| "I explored and went ahead with the obvious choice" | The obvious choice is a checkpoint with one recommended option — still the user's click |
| Asking the user facts ("does your vault use Bases?") | Look it up; report what you found |
| Presenting agent-debate output raw | Synthesize: what converged (settled), what split (the user's decision) |
| Options that are one real option plus strawmen | Each option must have a condition under which it wins |
| A critique that dresses "unverified" as "disproven" | Label the attack; unverified claims cost a verification step, not the design |
| Dispatching the agent debate because it's available | Offer it with a cost estimate; the user decides if the decision is worth it |
| Re-asking a locked decision after new info | Surface the new info, name the locked decision it touches, ask ONLY if it genuinely invalidates it |
