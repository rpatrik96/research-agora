# Research Agora Launch Thread (X.com)

**Strategy:** 9 posts. Start a conversation about what AI-assisted research actually needs — frame through three unsolved problems (discoverability, verification, benchmarking), use bibtexupdater + HALLMARK as the origin story showing coevolution, then reveal the platform. Science at large, not just ML. Discussion-first, tool second. Each post under 280 chars. Pin thread after posting.

---

## Post 1 (Provocation — redefine research)
[VISUAL: twitter banner (`dissemination/assets/twitter-banner.png`) or spiral logo on dark bg (`branding/spiral-pure-mark-dark.png`)]

AI is changing how we do research. But we're not talking about the right problems.

Our own experience of AI-assisted research, conversations across the globe, and preliminary survey data taught us there are exactly three problems nobody is solving well yet.

A thread. 🧵

---

## Post 2 (Problem 1 — Discoverability)
[VISUAL: `dissemination/assets/thread-post2-discoverability.png`]

Problem 1: Discoverability.

There are probably thousands of AI prompts, agents, and workflows for research. You can't find them. There's no search, no taxonomy, no way to compare.

We need a shared registry so the best tools actually surface and evolve, not just the loudest.

---

## Post 3 (Problem 2 — Verification)
[VISUAL: `dissemination/assets/thread-post3-verification.png`]

Problem 2: Verification.

Most AI research tools can't tell you when they're wrong. They generate text that looks right. You trust it. 
The fix isn't "don't use AI." It's defining "correct" before you delegate — acceptance criteria, not vibes.

---

## Post 4 (Problem 3 — Benchmarking)
[VISUAL: `dissemination/assets/thread-post4-benchmarking.png`]

Problem 3: Benchmarking.

If you can't measure a skill, you can't improve it. Almost nobody ships benchmarks with their AI research tools.

Without numbers, you're guessing. With numbers, you're engineering — and building the trust we need to preserve.

---

## Post 5 (Origin story — bibtexupdater)
[VISUAL: bibtexupdater terminal screenshot — capture live run with pass/fail output (TODO: take manually)]

This started with one tool.

In January, I released bibtexupdater — verifies BibTeX references against CrossRef, DBLP, Semantic Scholar, arXiv. Catches wrong authors, bad DOIs, upgrades preprints to published versions.

github.com/rpatrik96/bibtexupdater

---

## Post 6 (HALLMARK — coevolution)
[VISUAL: `dissemination/assets/thread-post6-coevolution.png`]

Weeks later, I had second thoughts: how well does bibtexupdater actually work?

So we built HALLMARK — a citation hallucination benchmark. Born from honest doubt.

The benchmark improved the tool. The tool sharpened the benchmark. They coevolve.

---

## Post 7 (The platform — generalizing the pattern)
[VISUAL: spiral logo (`branding/spiral-pure-mark-dark.png`) or social preview card (`branding/spiral-pure-social-preview.png`)]

That pattern became a position paper for ICLR 2026 — and a platform.

Research Agora: 61 open-source skills. Paper writing, adversarial review, LaTeX diagnostics, research agents, slides, posters.

Built for Claude Code. Works with Cursor, Gemini CLI, Copilot. MIT license.

---

## Post 8 (How the three problems map to the tool)
[VISUAL: `dissemination/assets/thread-post8-mapping.png`]

How the three problems map to Research Agora:

Discoverability → searchable skill registry
Verification → evidence hierarchy
Benchmarking → benchmarks (WIP)

bibtexupdater + HALLMARK: the proof of concept — tool and benchmark coevolving in the open.

---

## Post 9 (CTA — join the conversation)
[VISUAL: /onboard terminal screenshot or site homepage (TODO: take manually)]

No expertise needed. Run /onboard — it asks about your research and sets you up in 5 minutes.

Install: /plugin marketplace add rpatrik96/research-agora
Site: rpatrik96.github.io/research-agora
Paper: [arXiv link]
Code: github.com/rpatrik96/research-agora

What's your biggest friction in AI-assisted research?

---

## Tagline
AI skills for researchers, by researchers.

---

## Posting notes
- Post 1 first, then reply to it with posts 2–9 as a thread
- Attach spiral logo (`branding/spiral-pure-mark-dark.png`) to post 7 (the platform reveal)
- Move site URL to bio to avoid reach penalty — keep only in post 9
- Best posting times: Tue–Thu, 9–11am ET (ML Twitter peak)
- Tag relevant people only if you have a relationship (avoid cold-tagging)
- Free account: no edit button, double-check before posting
- Fill [arXiv link] placeholder in Post 9 before posting
- Twitter counts URLs as 23 chars regardless of actual length
- Post 9 ends with a question to spark replies — this is intentional for engagement
- bibtexupdater link in post 5 gives the thread a concrete, already-shipped artifact — establishes credibility before the bigger platform announcement
- Thread targets science at large, not just ML/CS — language is deliberately domain-agnostic
- /onboard in post 9 lowers the barrier: no expertise required, the skill figures out what you need
