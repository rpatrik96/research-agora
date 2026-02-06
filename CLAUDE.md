# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Research Agora is a Claude Code plugin marketplace providing skills for ML research workflows. It bundles 5 category-based plugins: `academic`, `development`, `formatting`, `office`, and `research-agents`.

## Commands

### Testing
```bash
pytest tests/                    # Run all tests
pytest tests/test_skills.py      # Run specific test file
pytest tests/ -k "test_name"     # Run tests matching pattern
```

### Code Quality
```bash
ruff check .                     # Lint Python files
ruff format .                    # Format Python files
```

### Template Analysis
```bash
cd templates
python analyze_template.py /path/to/template.pptx --output slides --name "template-name"
```

## Architecture

### Plugin Structure
Each plugin lives in `plugins/{category}/` with:
- `.claude-plugin/plugin.json` - Plugin metadata
- `commands/` - Skill definitions (YAML frontmatter + markdown)
- `templates/` - Optional presentation/poster templates

### Skill Format
Skills in `commands/*.md` use YAML frontmatter:
```yaml
---
name: skill-name
description: Brief description with trigger phrases
model: sonnet  # or haiku, opus
---
```

### Agent Format
Agents in `plugins/research-agents/agents/*.md`:
```yaml
---
name: agent-name
description: Brief description for Task tool
model: opus
color: orange  # optional
---
```

### Research-Agents Architecture
The `research-agents` plugin uses a layered architecture:
- **Orchestrators** (`orchestrators/`) - Fan-out/fan-in parallel coordinators
- **Agents** (`agents/`) - 14 high-level analysis agents
- **Micro-skills** (`micro-skills/`) - 8 atomic, parallelizable operations
- **Helpers** (`helpers/`) - Utility skills for efficiency

Central to this is `research-state.json`, an intermediate representation enabling parallel claim processing.

### Evidence Hierarchy
Claims are graded L1-L6:
- L1: CODE_VERIFIED (reproducible with code)
- L2: REPRODUCIBLE_EXPERIMENT
- L3: PAPER_EVIDENCE (tables/figures)
- L4: CITATION_SUPPORT
- L5: LOGICAL_ARGUMENT
- L6: ASSERTION (no evidence)

## Key Files

| Path | Purpose |
|------|---------|
| `.claude-plugin/marketplace.json` | Marketplace metadata, lists all plugins |
| `plugins/*/.claude-plugin/plugin.json` | Individual plugin manifests |
| `templates/analyze_template.py` | Extract design specs from PPTX files |
| `plugins/research-agents/config/model-routing.json` | Model/mode configuration |
| `plugins/research-agents/config/WORKER_PREAMBLE.md` | Leaf agent protocol |

## Domain Context

- **Primary audience**: ML researchers
- **Target venues**: NeurIPS, ICML, ICLR, AAAI
- **LaTeX conventions**: cleveref, booktabs, amsmath
- **Figures**: matplotlib/seaborn, colorblind-safe, PDF export

## Adding New Content

### New Skill
1. Create `plugins/{category}/commands/skill-name.md` with YAML frontmatter
2. Use kebab-case naming; group related skills with common prefix (e.g., `paper-*`)
3. Keep concise (150-400 lines), include examples in fenced blocks

### New Agent
1. Create `plugins/research-agents/agents/agent-name.md`
2. Include tools list in frontmatter
3. Design for autonomous operation with structured output

### New Template
```bash
python templates/analyze_template.py /path/to/file.pptx --output slides --name "name"
```
This copies the PPTX and generates `STYLE.md` and `specs.json`.

## Dependencies

- `python-pptx` - Template analysis and Office document creation
- `bibtexupdater` - Optional, for `paper-references` skill
