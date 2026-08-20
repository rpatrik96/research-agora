# Contributing to Research Agora

Thank you for your interest in contributing to Research Agora! This guide explains how to add new skills and agents.

## Repository Structure

```
research-agora/
├── .claude-plugin/
│   └── marketplace.json      # Marketplace metadata
├── plugins/
│   ├── academic/             # Paper writing & research skills
│   │   ├── .claude-plugin/plugin.json
│   │   ├── commands/         # Skill definitions
│   │   └── templates/posters/
│   ├── development/          # Code quality & automation skills
│   ├── editorial/            # Diagnostic editorial intelligence skills
│   ├── formatting/           # Document formatting skills
│   └── research-agents/      # Specialized research agents
│       ├── .claude-plugin/plugin.json
│       └── agents/
├── templates/
│   ├── analyze_template.py   # Template extraction tool
│   └── README.md
└── tests/
```

## Adding a New Skill

> **Before you start:** [Take the onboarding quiz](https://rpatrik96.github.io/research-agora/onboard.html) to see how users discover skills. Your skill's description and trigger phrases should match the vocabulary users express in their quiz answers.

### 1. Choose the Right Plugin

| Plugin | Use For |
|--------|---------|
| `academic` | Paper writing, citations, presentations |
| `development` | Code quality, CI/CD, git workflows |
| `editorial` | Diagnostic editorial intelligence — analyzes, diagnoses, and translates writing across contexts |
| `formatting` | LaTeX, figures, document styling |
| `research-agents` | Autonomous multi-step research analysis |

### The bar: a skill names the step that checks its own output

This is the rule the catalog is maintained against, and it is why skills get
retired as well as accepted.

**A skill that produces citations, numbers, or claims is accepted when
something verifies them before the model writes anything.** The pattern is
`/paper-experiments`: scripts extract the values from the repo, and the model
only arranges what the scripts found — *"The LLM should not guess any values -
only use what was extracted by the scripts above."* A tool lookup counts
(`bibtexupdater`, `limpid`, `latexmk`, an arXiv query); a script that greps the
source counts; an instruction to be careful does not.

**Skills that rephrase text the author already stands behind are accepted
without one** — `/paper-abstract` diagnoses an abstract you wrote against venue
limits and structure, and writes nothing.

**Skills that generate claims with nothing to check them are declined**, and
existing ones are retired on the same rule. An introduction states a paper's
novelty, and no oracle exists for novelty, so the Agora audits introductions
rather than writing them.

**Where a tool-backed skill and a freehand one do the same job, the tool-backed
one is the product.** If your skill overlaps one that calls a real tool, extend
that one instead.

**Retirement follows deprecation.** A skill marked `deprecated` keeps working
for at least one minor release; the CHANGELOG names its replacement or says
plainly that there is none; and the file stays in git history under MIT, so
anyone who wants it can lift it.

### 2. Create the Skill File

Use the scaffolding tool or create a markdown file manually in `plugins/{category}/commands/skill-name.md`:

```bash
# Scaffolding tool (recommended)
python scripts/create-skill.py --name my-skill --category academic --type writing --domain ml
```

Manual format:

```yaml
---
name: skill-name
description: |
  Brief description of what this skill does. Use when asked to
  "trigger phrase 1", "trigger phrase 2", "trigger phrase 3".
model: sonnet  # or haiku for simpler tasks
metadata:
  research-domain: general    # ml, nlp, cv, robotics, theory, statistics, biology, general
  task-type: writing          # writing, verification, analysis, formatting, automation, dissemination, review, diagnosis
  research-phase: paper-writing  # literature-review, experiment-design, implementation, paper-writing, submission, rebuttal, dissemination
  verification-level: none    # formal, heuristic, layered, none
---

# Skill Title

Detailed instructions for Claude to follow when this skill is invoked.

## Workflow

1. Step one
2. Step two
3. Step three

## Examples

Include concrete examples with code blocks.

## Output Format

Specify the expected output format.
```

The `metadata` block is **required** for all new skills. Valid values for each field are defined in `registry/categories.json`.

### 3. Naming Conventions

- **File name:** `kebab-case.md` (e.g., `paper-references.md`)
- **Related skills:** Use common prefix (e.g., `paper-*`)
- **Triggers:** Include 3-5 natural language phrases

### 4. Writing Style

- Direct and actionable: "Do X", "Avoid Y"
- Include code/LaTeX/markdown examples in fenced blocks
- Be specific to ML research context (assume NeurIPS/ICML/ICLR venues)
- Keep concise but complete (150-400 lines typical)

## Adding a New Agent

Agents are specialized subagents for complex multi-step tasks.

### 1. Create the Agent File

Create a markdown file in `plugins/research-agents/agents/agent-name.md`:

```yaml
---
name: agent-name
description: Brief description for the Task tool
model: opus
tools: Read, Grep, Glob, Bash, WebFetch  # Tools this agent can use
color: yellow  # Optional: yellow, blue, green, red, orange, violet, purple, teal, cyan
---

# Agent Title

## Purpose

What this agent does and when to use it.

## Activation Triggers

- "trigger phrase 1"
- "trigger phrase 2"

## Workflow

Detailed steps the agent follows.

## Output Format

What the agent produces.
```

### 2. Agent Design Principles

- **Single responsibility:** One clear purpose
- **Autonomous operation:** Should complete without user intervention
- **Structured output:** Consistent, parseable results
- **Error handling:** Graceful degradation when things go wrong

## Testing

Run the test suite before submitting:

```bash
pytest tests/
```

To validate registry consistency after adding skills:

```bash
python scripts/generate-registry.py
pytest tests/test_registry.py
```

## Pull Request Guidelines

1. **One skill/agent per PR** unless closely related
2. **Include description** of use case and triggers
3. **Test locally** before submitting
4. **Update plugin.json** if adding new files

## Code Quality

- Python scripts must pass `ruff` linting
- Markdown should be well-formatted
- No hardcoded personal paths

## Questions?

Open an issue for discussion before starting large contributions.
