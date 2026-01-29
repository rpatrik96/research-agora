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
│   ├── formatting/           # Document formatting skills
│   ├── office/               # Office document creation skills
│   │   ├── .claude-plugin/plugin.json
│   │   ├── commands/
│   │   └── templates/slides/
│   └── research-agents/      # Specialized research agents
│       ├── .claude-plugin/plugin.json
│       └── agents/
├── templates/
│   ├── analyze_template.py   # Template extraction tool
│   └── README.md
└── tests/
```

## Adding a New Skill

### 1. Choose the Right Plugin

| Plugin | Use For |
|--------|---------|
| `academic` | Paper writing, citations, presentations |
| `development` | Code quality, CI/CD, git workflows |
| `formatting` | LaTeX, figures, document styling |
| `office` | Word, PowerPoint, Excel creation |

### 2. Create the Skill File

Create a markdown file in `plugins/{category}/commands/skill-name.md`:

```yaml
---
name: skill-name
description: |
  Brief description of what this skill does. Use when asked to
  "trigger phrase 1", "trigger phrase 2", "trigger phrase 3".
model: sonnet  # or haiku for simpler tasks
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

### 3. Naming Conventions

- **File name:** `kebab-case.md` (e.g., `paper-introduction.md`)
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
tools: Read, Grep, Glob, Bash, WebFetch  # Tools this agent can use
color: yellow  # Optional: yellow, blue, green, red
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
cd research-agora
pytest tests/
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
