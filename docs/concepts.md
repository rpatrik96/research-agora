# How AI Agents Work

Reference material for Research Agora users. Reading time: ~10 minutes.

---

## The Evolution Stack: Chat to Skills

AI tools form a complexity ladder. Each level builds on the previous one.

| Level | What changes | Example |
|-------|-------------|---------|
| **Chat** | You talk to an LLM | ChatGPT, Claude.ai — Q&A, drafting, brainstorming |
| **Context** | The LLM knows your project | `CLAUDE.md` files, uploaded documents, conversation history |
| **Tools** | The LLM can act | Read files, run code, search the web, call APIs |
| **Agents** | The LLM pursues multi-step goals | Autonomous research pipelines, iterative debugging |
| **Skills** | Reusable compound workflows | `/paper-review`, `/paper-references` — packaged expertise |

Most researchers use Chat. The jump to Tools is where AI becomes genuinely useful for research tasks. Skills are the top of the stack — they encode the workflow once and let you (and your collaborators) invoke it repeatedly without rethinking the prompt structure each time.

---

## Key Concepts

**LLM (Large Language Model)**
A neural network trained on text to predict the next token. It has no memory, tools, or goals on its own. Everything it appears to "know" is a learned statistical pattern over training data.

**Chatbot**
An LLM wrapped in a conversational interface (e.g., ChatGPT, Claude.ai). You type, it responds. Stateless between sessions — it remembers nothing from last Tuesday unless you paste it back in.

**Agent**
An LLM that can use tools, maintain context, and pursue multi-step goals autonomously. It reads files, runs code, searches the web, and decides what to do next. This is what separates agents from chatbots: they act, not just respond.

**Tool use**
Agents are not limited to generating text. They can:

| Capability | Example |
|------------|---------|
| Read and write files | Edit your LaTeX source, update a BibTeX file |
| Execute code | Run a Python script and interpret the output |
| Search the web | Look up a paper on Semantic Scholar |
| Call APIs | Query a database, interact with GitHub |
| Chain actions | Find a bug, fix it, run tests, commit — all in one go |

**Context window**
The buffer of text the model can "see" at once. Everything the agent knows about your project in a given session lives here: your instructions, files it has read, conversation history, tool outputs. When the context window fills, older content gets dropped or summarized. Bigger context = more expensive per token.

**Tokens**
The units LLMs process text in. Roughly: 1 token ≈ 0.75 words, or ~4 characters in English. A 10-page paper is approximately 3,000–5,000 tokens. Token count determines API cost and context window usage.

**Skills (Custom Commands)**
Reusable prompt templates invoked with a slash command. A skill encodes a complete workflow — role, objective, process, output format — so you get consistent, structured output every time without rewriting the prompt.

| Skill | What it does |
|-------|-------------|
| `/commit` | Reviews changes, writes a conventional commit message, commits |
| `/paper-review` | Reads a paper and generates structured review feedback |
| `/literature-synthesizer` | Searches for related work given a research question |
| `/paper-references` | Checks that all citations in a BibTeX file resolve to real papers |

**Context engineering**
The practice of systematically providing agents with the right information to do their job well. Think of it as writing documentation for your AI collaborator. The better the "working with me" manual — explicit instructions, project knowledge, acceptance criteria — the better every interaction. A `CLAUDE.md` file placed in your project root is the primary mechanism.

---

## What to Delegate, What to Protect

Not everything should go to an AI agent. The value of delegation depends on whether the task has verifiable outputs and whether the judgment required is yours alone.

| Delegate | Protect |
|----------|---------|
| Code boilerplate and scaffolding | Algorithm design and architectural choices |
| BibTeX formatting and citation verification | Deciding which papers are actually relevant |
| Generating figure code from described data | Interpreting what the results mean |
| Drafting rebuttal structure | Deciding which reviewer concerns are legitimate |
| Literature search and summary | Assessing novelty and framing the contribution |
| Grammar, style, and consistency passes | Scientific claims and argument structure |
| Repetitive data cleaning scripts | Deciding what anomalies mean |
| Camera-ready formatting passes | Judging whether a result is publishable |

The pattern: delegate generation, protect judgment. AI expands what you can do; it does not replace what you are. If you delegate problem selection, you lose the skill that makes the problem selection meaningful.

**The verification asymmetry:** Survey data from 38 ML researchers found that 74% verify AI outputs for coding tasks, but only 11% verify for ideation tasks. This gap is explained entirely by tooling: citation checkers and test suites exist; ideation oracles don't. Tools enable verification. Where tools don't exist yet, the burden falls on your judgment — which means that domain is riskier to delegate, not safer.

---

## Where Research Agora Fits

Research Agora lives at the Skills level of the stack. It provides:

1. **A skills marketplace** — a repository of community-contributed, versioned prompt workflows covering the full research lifecycle (writing, verification, review, dissemination, code quality).

2. **Verification workflows** — skills that run formal checks: citation resolution against scholarly databases, code-paper consistency checking, statistical claim validation. These turn the "delegate freely, verify with tools" pattern into a one-command workflow.

3. **A benchmark agenda** — standardized evaluation protocols so researchers can compare skill performance objectively rather than relying on vibes. (Currently proposed; working examples shipped for pillars 1 and 2.)

The key insight: each pillar alone is insufficient. A skills marketplace without verification lets bad outputs circulate. Verification without discovery means researchers rebuild the same checks from scratch. Benchmarks without skills have nothing to evaluate. The Agora requires all three.

For the full argument, see the [position paper](https://openreview.net/forum?id=svFHXBd2wq).

---

## Further Reading

- [quickstart.md](quickstart.md) — Run your first skill in 5 minutes
- [verification.md](verification.md) — The verification hierarchy in detail
- [Claude Code documentation](https://code.claude.com/docs) — Official reference
- [CLAUDE.md template](../templates/CLAUDE.md.researcher) — Copy and customize for your project
- Willison, S. (2026). [Agentic Engineering Patterns](https://simonwillison.net/2026/Feb/23/agentic-engineering-patterns/) — Practical patterns for reliable agent workflows
