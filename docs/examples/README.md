# Examples: Domain-Specific Starter Prompts

Executable prompt templates organized by research workflow. Each file contains self-contained prompts you can run immediately in Claude.ai (browser) or Claude Code (CLI), along with what to look for in the output.

---

## Choose Your File

| If you work with... | Start here |
|--------------------|-----------|
| Data files, CSV/Excel, visualizations, EDA pipelines | [code-and-data.md](code-and-data.md) |
| Papers, citations, literature reviews, BibTeX files | [literature-and-citations.md](literature-and-citations.md) |
| Email, teaching materials, administrative documents, review rebuttals | [writing-and-admin.md](writing-and-admin.md) |
| R, clinical workflows, C++ or TypeScript codebases, econometrics | [technical-workflows.md](technical-workflows.md) |
| Automated research pipelines, Zotero+MCP, privacy audits, AI-generated code maintenance | [advanced-research.md](advanced-research.md) |

---

## How These Examples Work

Each file follows a consistent format:

1. **Use case** — what problem this solves and when to use it
2. **Prerequisites** — what you need before running (files, subscriptions, tools)
3. **Prompt blocks** — copy-paste directly; replace `[placeholders]` with your content
4. **Expected output** — what good output looks like
5. **What to verify** — the specific things you must check before trusting the result
6. **Related skills** — Research Agora skills that automate or extend the workflow

---

## General Principles

**Replace every `[placeholder]`** before running. Vague placeholders produce generic output. The more specific you are, the more useful the response.

**Verify everything that matters.** Citations either exist or they don't. Numbers either match or they don't. Writing quality requires your judgment — no automated check can substitute for reading the output critically.

**Start with one task.** These prompts are designed to do one thing well. Don't combine them until you've seen each work individually.

**Rephrase, don't repeat.** If the output misses the mark, the prompt is usually the problem. Add constraints, narrow scope, or break the task into smaller steps.

---

## Browser vs. CLI

All prompts in this directory work in [Claude.ai](https://claude.ai) (browser, no installation). Paste the prompt, replace placeholders, run.

For prompts that reference files (`path/to/data.csv`, `.bib` files, source code), you need Claude Code (CLI) so the agent can read actual files from your disk. The prompt text is the same; the delivery mechanism differs.

See [../quickstart.md](../quickstart.md) for a 5-minute setup guide.
