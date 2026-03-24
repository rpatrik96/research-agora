# Advanced Research Workflows

Prompts for automated research pipelines, Zotero+MCP integration, interactive visualizations, privacy audits, and maintaining AI-generated code. These assume you're already using Claude Code regularly.

---

## Who This Is For

If you already run Claude Code daily, want to connect it to external tools (Zotero, GitHub, databases), are concerned about what your agent is transmitting, or inherited AI-generated code you need to understand — this file covers the next level.

---

## Prerequisites

| Workflow | Requirements |
|----------|-------------|
| Zotero+MCP | Claude Code + Zotero desktop app + [Zotero MCP server](https://github.com/kujenga/zotero-mcp) configured |
| Interactive HTML visualization | Claude Code + modern browser |
| Privacy audit | Claude Code (the tool you're auditing) |
| Cognitive debt audit | Claude Code + the codebase to audit |
| AutoResearch program | Claude Code + access to AutoResearch; GPU with ~1hr compute budget |

---

## Prompt 1: Automated Research Experiment (AutoResearch)

**Use case:** You want to run an overnight ML experiment guided by a structured specification — hypothesis, dataset, metrics, stopping criterion — rather than a loose prompt. This prompt helps you draft the specification file.

**Works in:** CLI

```
Help me draft a program.md for an AutoResearch experiment.

My research context:
- Research question: [state it in one sentence — what you want to know]
- Current results: [what you already know; what baseline you're comparing against]
- Compute budget: [e.g., 51 minutes on one A100]

Draft a program.md that specifies:
1. Research question (one sentence)
2. Hypothesis to test (falsifiable — what would a positive vs. negative result look like?)
3. Dataset: [name and source] — be concrete, not generic
4. Model: [architecture and size] — be concrete
5. Metrics to track: [list them, with acceptable ranges where known]
6. Stopping criterion: [time limit OR performance threshold — not both]
7. Success definition: what result would make this experiment worth reporting?

Follow the AutoResearch program.md format:
https://github.com/karpathy/autoresearch

Flag any part of the specification that is underspecified — a good experiment spec has no ambiguities.
```

**Expected output:** A complete `program.md` file with a flagged list of any remaining ambiguities.

**What to verify:**
- Is the hypothesis falsifiable? Can the experiment actually distinguish between the null and alternative?
- Is the dataset concrete enough that AutoResearch can locate it without ambiguity?
- Is the stopping criterion a single condition, not an "or"?
- Review the flagged ambiguities before launching. Resolve each one.

**Related skills:** `benchmark-scout` (academic@research-agora), `experiment-tracker` (academic@research-agora)

---

## Prompt 2: Zotero + MCP Literature Integration

**Use case:** You want Claude Code to search your personal Zotero library — the papers you've actually collected — and surface gaps: important papers on your current topic that you haven't read yet.

**Works in:** CLI (requires Zotero MCP server configured in `~/.claude/`)

First, verify your MCP server is configured:
```bash
cat ~/.claude/mcp_servers.json | grep zotero
```

If not configured, follow the [Zotero MCP setup guide](https://github.com/kujenga/zotero-mcp).

Then run:

```
I want to search my Zotero library for literature on [the topic you are currently writing about].

Steps:
1. Confirm the Zotero MCP server is connected — list available Zotero tools
2. Search my library for papers on [topic]
3. For each paper found, output: title, year, and the key claim in one sentence
4. Identify gaps: what important papers on this topic are NOT in my library?
   - Suggest 3 papers I should add, with full citations and DOIs to verify
5. Output: a markdown table I can paste directly into my notes

For the suggested additions: do not invent DOIs. If uncertain, write [DOI: verify manually].
```

**Expected output:** A table of your existing papers on the topic, plus 3 suggested additions with real DOIs marked for verification.

**What to verify:**
- Are the suggested papers real? Search each DOI on [doi.org](https://doi.org) before adding to your library.
- Are the one-sentence summaries of your existing papers accurate? Spot-check 2–3 against the actual abstracts.
- Any `[DOI: verify manually]` markers: look these up before citing.

**Related skills:** `literature-synthesizer` (academic@research-agora), `paper-references` (academic@research-agora)

---

## Prompt 3: Interactive HTML Visualization from Paper Results

**Use case:** You have results in a table or CSV and want an interactive figure for a presentation, website, or supplementary material — no server, no dependencies, self-contained.

**Works in:** CLI

```
I have results in [results.csv / paste the table here].

Create a self-contained interactive HTML page using D3.js from CDN (no server, no external dependencies beyond the CDN URL).

Requirements:
- Title and caption matching [the paper section this belongs to]
- Hover tooltip showing exact values for each data point
- Colorblind-safe palette (Okabe-Ito: #E69F00, #56B4E9, #009E73, #F0E442, #0072B2, #D55E00, #CC79A7)
- Clean screenshot-ready layout (white background, no browser chrome artifacts)
- Responsive: works at 1200px and 800px viewport widths

Save as paper-figure-interactive.html and open in my default browser.

After generating: explain in 3 bullets what the visualization shows and what a reader should take away.
```

**Expected output:** A self-contained HTML file that opens in a browser, plus a 3-bullet interpretation.

**What to verify:**
- Open the file in a browser. Do hover tooltips appear and show correct values?
- Do the values in the visualization match your source data exactly? Spot-check 5 data points.
- Does it render correctly at both 1200px and 800px?
- Is the Okabe-Ito palette applied, or did the agent substitute a different palette?

**Related skills:** `publication-figures` (formatting@research-agora), `figure-storyteller` (research-agents@research-agora)

---

## Prompt 4: Privacy Audit of the Current Session

**Use case:** Before continuing a session that has involved file reads, you want to understand what data has been transmitted and whether any sensitive files were accessed.

**Works in:** CLI (run at any point during a session)

```
Before we continue, I want to understand what data this session has transmitted.

Please:
1. List every file you have read in this session (full paths)
2. Check whether any .env, .env.*, credentials, or *.key files exist anywhere in the current directory tree — list their paths but do NOT read their contents
3. Check whether DISABLE_TELEMETRY and DISABLE_ERROR_REPORTING are set in the current environment
4. Review my .claudeignore (if it exists) and flag any sensitive file patterns that are NOT covered
5. Summarize: what should I add to .claudeignore, and what files (if any) should I move outside this directory?

Output each section clearly labeled.
```

**Expected output:** A file read list, a list of sensitive file paths found (not their contents), environment variable status, and `.claudeignore` recommendations.

**What to verify:**
- Are any files in the read list that shouldn't have been? If so, move them outside the project directory.
- Are `.env` files listed under the sensitive file paths found? Move them to a parent directory or use a secrets manager.
- Are `DISABLE_TELEMETRY` and `DISABLE_ERROR_REPORTING` set? If not, add them to your shell profile — see [../privacy-gdpr.md](../privacy-gdpr.md).

**Related skills:** See [../privacy-gdpr.md](../privacy-gdpr.md) for the full privacy setup guide.

---

## Prompt 5: Cognitive Debt Audit of AI-Generated Code

**Use case:** You have a Python tool that was largely AI-generated — it works, but you don't fully understand it, and you need to maintain or extend it. This prompt produces a comprehension map and a refactoring roadmap.

**Works in:** CLI

```
I have a Python tool at [path/to/tool/]. It was largely AI-generated and I want to understand it well enough to maintain and extend it.

Please:
1. Produce a plain-English architecture summary — one paragraph per file, describing what the file does and how it relates to the others
2. Identify the top 3 areas of "cognitive debt" — code that runs but whose design rationale is unclear or undocumented
3. For each cognitive debt area:
   a. Explain the problem
   b. Propose a concrete refactor
   c. Write the test that verifies the refactored version still works correctly
4. List any dependencies that appear unused, potentially hallucinated, or not pinned to a version
5. Output a CONTRIBUTING.md that documents:
   - What the tool does and how to run it
   - Which parts were AI-generated
   - Which parts have been human-reviewed
   - How to run the tests

Do not refactor anything yet — produce the plan first. I will review before you proceed.
```

**Expected output:** Architecture summary, 3 cognitive debt items with refactor proposals and tests, dependency audit, and a draft `CONTRIBUTING.md`.

**What to verify:**
- Does the architecture summary match your understanding of what the tool does?
- Are the cognitive debt items the actual hard-to-understand parts, or surface-level style issues?
- Do the proposed tests actually test the behavior you care about, or do they just confirm the current (possibly wrong) behavior?
- Check the dependency list: install each package and confirm it exists on PyPI.
- Review before authorizing any refactoring — the plan should make sense to you before any code changes.

**Related skills:** `code-simplify` (development@research-agora), `python-docs` (development@research-agora), `artifact-packager` (research-agents@research-agora)

---

## Further Reading

- [Willison — Agentic Engineering Patterns](https://simonwillison.net/2026/Feb/23/agentic-engineering-patterns/): Cognitive debt, TDD-first workflows, vibe coding risks.
- [Willison — Cognitive Debt](https://simonwillison.net/2026/Feb/15/cognitive-debt/): The distinction between technical debt and cognitive debt; why AI-generated code accumulates it silently.
- [Knostic — Claude Code Loads .env Secrets](https://www.knostic.ai/blog/claude-loads-secrets-without-permission): Security research on what Claude Code reads without explicit permission.
- [Vibe Coding in Practice (arXiv:2512.11922)](https://arxiv.org/abs/2512.11922): Academic analysis of AI-generated code and technical debt.
- [Lazar — Coding Agents for Humanities](https://philosophyofcomputing.substack.com/p/how-to-use-coding-agents-for-philosophy): Literature agents for conceptual and non-quantitative research.
