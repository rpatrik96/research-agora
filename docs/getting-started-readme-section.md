# Getting Started

**Reading time:** PI: 5 min | Researcher: 15 min | Student: 10 min

---

## Install

One command adds the full Research Agora skill library to Claude Code:

```bash
/plugin marketplace add rpatrik96/research-agora
/plugin install academic@research-agora
/plugin install development@research-agora
/plugin install formatting@research-agora
/plugin install research-agents@research-agora
```

**Prerequisites:** Claude Code installed (`npm install -g @anthropic-ai/claude-code`) and a Claude Pro subscription or API key. First-time setup takes 5–10 minutes. See [docs/quickstart.md](docs/quickstart.md) for the full walkthrough.

---

## Your First 5 Minutes

The fastest way to see what Research Agora does: run citation verification on a real `.bib` file.

**Step 1.** Navigate to a project with a bibliography:
```bash
cd /path/to/your/project
claude
```

**Step 2.** Install the citation verification dependency:
```bash
pip install bibtex-updater
```

**Step 3.** Run the skill:
```
/paper-references
```

**Step 4.** Read the output. Every row marked `mismatch` or `not found` is a potential hallucinated or corrupted reference. Fix or remove it before submission.

That task costs approximately $0.10–0.30 in API tokens and catches errors that a careful human reviewer would catch — programmatically, in under a minute. If you don't have a `.bib` file handy, paste the demo in [docs/quickstart.md](docs/quickstart.md) and watch the agent flag the fabricated entry.

---

## Choose Your Path

<details>
<summary><strong>PI: Evaluate and deploy for your group</strong></summary>

### What Research Agora actually does

Research Agora is a library of reusable AI workflows — skills — for the research tasks that consume the most time with the least payoff: citation verification, boilerplate code, related work synthesis, rebuttal drafts, figure formatting. Each skill encodes a verified prompt template that runs against your actual project files.

The practical question for a PI is not "is this impressive?" but "does this save enough time to justify the overhead?" The answer varies by workflow. Citation verification and figure formatting have near-zero failure rate and require no judgment calls — delegate freely. Literature synthesis and writing assistance require review — treat output as a first draft, not a final product.

### Cost

A light user (email drafts, occasional citation checks) pays $20/month (Pro subscription) + under $5/month in API tokens. A heavy user (daily literature search, multi-file code tasks, paper editing) pays $20 + $40–80/month. For a group of 5, the Team plan ($30/user/month) adds a Data Processing Agreement required for GDPR compliance — see [docs/privacy-gdpr.md](docs/privacy-gdpr.md).

### Privacy and institutional compliance

- **No patient data, unpublished results, or embargoed content** into any cloud AI tool on a Pro plan — no DPA is available at that tier.
- **Team plan (minimum for institutional use):** Anthropic acts as a data processor; DPA with EU SCCs included automatically. Conversations never used for training.
- **Medical/clinical data:** Local models (Ollama) only, on approved institutional infrastructure. Contact your Datenschutzbeauftragte(r) before proceeding.

Full compliance guide: [docs/privacy-gdpr.md](docs/privacy-gdpr.md)

### How to roll this out

1. **Pilot with one task.** Pick the highest-pain weekly workflow in your group — the citation check before submission, the figure formatting pass, the rebuttal draft. Run it. If it saves 30 minutes, the tool pays for itself in the first use.
2. **Create a shared `CLAUDE.md`** in your main project repository. This file encodes your group's conventions (LaTeX packages, coding style, build commands, quality standards) so every group member gets consistent, project-aware responses. Commit it to git so it propagates automatically.
3. **Set a verification standard.** Decide upfront: what requires human review before use? Suggested defaults: citations (always verify), generated code (always run tests), writing (always read before sending). Document this in your `CLAUDE.md`.
4. **Review monthly.** In a group meeting: what did the agent get wrong this month? Update the `CLAUDE.md` "common mistakes" section together. This is collective learning that persists across people and sessions.

Skills are plain Markdown files. They're model-agnostic and not locked to Claude. If you switch providers, the workflows transfer.

</details>

<details>
<summary><strong>Researcher: Get productive today</strong></summary>

### Install and configure (15 minutes total)

**Install Claude Code:**
```bash
npm install -g @anthropic-ai/claude-code
```

**Add Research Agora:**
```bash
/plugin marketplace add rpatrik96/research-agora
/plugin install academic@research-agora
/plugin install development@research-agora
/plugin install formatting@research-agora
/plugin install research-agents@research-agora
```

**Initialize your project:**
Navigate to your project directory and run:
```
/init
```
This reads your codebase and drafts a `CLAUDE.md` tailored to your project. Review and edit the output — correct any wrong build commands or conventions before committing.

### The skills you'll use most

| Task | Skill | What it does |
|------|-------|-------------|
| Citation check before submission | `/paper-references` | Verifies every BibTeX entry against Semantic Scholar and CrossRef |
| Publication-quality figures | `/publication-figures` | Reformats matplotlib figures to journal standards (colorblind-safe, vector, correct font sizes) |
| Conventional commits | `/commit` | Reviews staged changes, writes a commit message, commits |
| Paper review simulation | `/paper-review` | Generates structured critical feedback simulating a skeptical reviewer |
| Related work synthesis | `/literature-synthesizer` | Searches for related work and drafts a synthesis paragraph |

### Running a skill

```bash
cd /path/to/your/project
claude
# then type:
/paper-references
```

Skills run against files in your current directory. Make sure you're in the right project before running.

### Customizing for your workflow

Add a `CLAUDE.md` to any project to give the agent persistent context. Minimum useful content:

```markdown
# My Project

## Key files
- main.tex — paper source
- references.bib — bibliography

## Build
latexmk -pdf main.tex

## Conventions
- Use \cref{} not \ref{}
- booktabs for all tables
- Colorblind-safe palettes (seaborn "colorblind")

## Verification requirements
- All citations verified with /paper-references before submission
- All figures exported as PDF (vector)
```

For domain-specific examples, see [docs/examples/](docs/examples/).

### Verification

Delegate freely for: citations, code formatting, figure styling, commit messages.
Always review before use: generated prose, literature synthesis, code logic.
Never skip: running generated code yourself before accepting it.

Full verification guide: [docs/verification.md](docs/verification.md)

</details>

<details>
<summary><strong>Student: Learn by doing</strong></summary>

### What this actually is

Research Agora is a collection of AI workflows for research tasks. You use it through Claude Code — an AI agent that reads and writes files on your computer, runs code, and pursues multi-step tasks. It's more powerful than a chatbot because it can act, not just respond.

The most important thing to understand before you start: **AI output requires verification.** The agent will produce confident, plausible-sounding results that are sometimes wrong. Your job is to check them.

### Getting started (no experience required)

**Step 1.** Install Claude Code:
```bash
npm install -g @anthropic-ai/claude-code
```

You need Node.js and a Claude subscription. Ask your PI if the group has a shared account.

**Step 2.** Run your first task — citation verification on your paper's bibliography:
```bash
cd /path/to/your/project
claude
/paper-references
```

Watch what happens: the agent reads your `.bib` file, queries Semantic Scholar for each entry, and reports which citations resolve to real papers and which don't. This is an agent doing a multi-step task: read a file → extract data → query an external API → compare results → report findings.

**Step 3.** Check the output manually for 3 entries. Does the agent's verdict match what you find when you search manually on [Semantic Scholar](https://semanticscholar.org)? This calibration step — checking a sample against ground truth — is the habit that separates useful AI use from blind trust.

### Building good habits

The skills in Research Agora encode verified workflows. But a skill is a tool — it's only as useful as your ability to judge whether the output is correct.

Three habits that matter:

1. **Verify a sample.** For any AI output, pick 3–5 items and check them manually. If they're all correct, you can trust the rest at that confidence level. If any are wrong, verify everything.

2. **Rephrase, don't repeat.** If the agent's output misses the mark, the prompt is usually the problem. Add constraints, narrow scope, or break the task into smaller steps. Typing the same prompt louder doesn't help.

3. **Understand before you submit.** For AI-generated code: can you explain what every function does? If not, ask the agent to explain it. For AI-generated writing: can you defend every claim? If not, rewrite it in your own words. You are responsible for what you submit, regardless of who (or what) wrote the first draft.

### Suggested learning path

| Week | Goal | How |
|------|------|-----|
| 1 | Run one skill on a real task | `/paper-references` on your bibliography |
| 2 | Set up a `CLAUDE.md` for your project | Run `/init`, review output, commit the file |
| 3 | Use a writing skill, verify the output | `/paper-review` on a section draft |
| 4 | Connect one MCP server | GitHub MCP, then try `/pr-automation` |

For hands-on prompt templates organized by task type, see [docs/examples/](docs/examples/). Start with the file closest to your current work.

### On learning and delegation

The concern about AI tools reducing learning is real. The endoscopist analogy is apt: detection rates drop when the tool is removed. The goal is to use AI in ways that preserve the struggle that produces understanding — use it to accelerate execution of things you already know how to do, not to bypass the parts you haven't learned yet.

A useful rule: if you couldn't do the task without AI, the AI shouldn't do it for you yet. Learn the manual version first. Then use AI to go faster.

</details>
