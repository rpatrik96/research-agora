# Research Agora Launch Thread (X.com)

**Strategy:** 8 posts. Start a conversation about what AI-assisted research actually needs — frame through three unsolved problems (discoverability, verification, benchmarking), use bibtexupdater as the origin story that revealed the pattern, then reveal the platform. Discussion-first, tool second. Each post under 280 chars. Pin thread after posting.

---

## Post 1 (Provocation — redefine research)
AI is changing how we do research. But we're not talking about the right problems.

Our own experience of AI-assisted research, conversations across the globe, and preliminary survey data taught us there are exactly three problems nobody is solving well yet.

A thread. 🧵

---

## Post 2 (Problem 1 — Discoverability)
Problem 1: Discoverability.

There are thousands of AI prompts, agents, and workflows for research. You can't find them. There's no search, no taxonomy, no way to compare.

We need a shared registry — categorized by research phase, task type, and domain — so the best tools surface, not just the loudest.

---

## Post 3 (Problem 2 — Verification)
Problem 2: Verification.

Most AI research tools have no way to tell you when they're wrong. They generate text that looks right. You trust it. Sometimes it isn't.

The fix isn't "don't use AI." It's defining what "correct" means *before* you delegate — acceptance criteria, not vibes.

---

## Post 4 (Problem 3 — Benchmarking)
Problem 3: Benchmarking.

If you can't measure a skill, you can't improve it. And right now, almost nobody ships benchmarks with their AI research tools.

How good is your citation checker? Your paper reviewer? Without numbers, you're guessing. With numbers, you're engineering.

---

## Post 5 (Origin story — bibtexupdater)
This started with one tool.

In January, I released bibtexupdater — a CLI that verifies BibTeX references against CrossRef, DBLP, Semantic Scholar, and arXiv. Upgrades preprints to published versions. Catches wrong authors, bad DOIs, missing fields.

It solved verification for citations. But building it surfaced the bigger question: why isn't every AI research tool this verifiable?

github.com/rpatrik96/bibtexupdater

---

## Post 6 (The platform — generalizing the pattern)
That question became a position paper for ICLR 2026 — and then a platform.

Research Agora: 61 open-source skills across 6 plugins. Paper writing, adversarial review, LaTeX diagnostics, 22 research agents, slides, posters.

Built for Claude Code. Works with Cursor, Gemini CLI, Copilot. MIT license.

[ATTACH: branding/spiral-pure-mark-dark.png — Archimedean spiral logo]

---

## Post 7 (How the three problems map to the tool)
How the three problems map to the platform:

1. Discoverability → skills marketplace with searchable taxonomy (domain, phase, task type)
2. Verification → evidence hierarchy (L1–L6) grading every claim from CODE_VERIFIED to ASSERTION
3. Benchmarking → shipped benchmarks you can run yourself and compare against

bibtexupdater is the proof of concept — script-verified, benchmarked, discoverable through the registry.

---

## Post 8 (CTA — join the conversation)
Get started in 5 minutes:

1. /plugin marketplace add rpatrik96/research-agora
2. Try /paper-review on any draft
3. Browse the skill registry: rpatrik96.github.io/research-agora

Paper: [arXiv link]
Code: github.com/rpatrik96/research-agora

What's your biggest friction point in AI-assisted research? Curious what problems 4, 5, 6 are.

---

## Tagline
AI skills for researchers, by researchers.

---

## Posting notes
- Post 1 first, then reply to it with posts 2–8 as a thread
- Attach spiral logo (`branding/spiral-pure-mark-dark.png`) to post 6 (the platform reveal)
- Move site URL to bio to avoid reach penalty — keep only in post 8
- Best posting times: Tue–Thu, 9–11am ET (ML Twitter peak)
- Tag relevant people only if you have a relationship (avoid cold-tagging)
- Free account: no edit button, double-check before posting
- Fill [arXiv link] placeholder in Post 8 before posting
- Twitter counts URLs as 23 chars regardless of actual length
- Post 8 ends with a question to spark replies — this is intentional for engagement
- bibtexupdater link in post 5 gives the thread a concrete, already-shipped artifact — establishes credibility before the bigger platform announcement
