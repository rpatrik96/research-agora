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

### Registry & Site
```bash
python3 scripts/generate-registry.py    # Regenerate registry/index.json from skill files
python3 scripts/generate-site.py        # Generate static site at site/output/
python3 scripts/add-metadata.py --dry-run  # Preview metadata additions
python3 scripts/create-skill.py --help  # Scaffold a new skill
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
metadata:
  research-domain: general
  task-type: writing
  research-phase: paper-writing
  verification-level: none
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
| `registry/index.json` | Auto-generated skill index (72 skills) |
| `registry/categories.json` | Taxonomy: domains, task-types, phases, verification-levels |
| `scripts/generate-registry.py` | Generates registry/index.json from skill files |
| `scripts/generate-site.py` | Generates static site from registry |
| `scripts/create-skill.py` | Scaffolds new skill files with metadata |
| `scripts/add-metadata.py` | Bulk-adds metadata to skill frontmatter |
| `templates/analyze_template.py` | Extract design specs from PPTX files |
| `plugins/research-agents/config/model-routing.json` | Model/mode configuration |
| `plugins/research-agents/config/WORKER_PREAMBLE.md` | Leaf agent protocol |
| `PLATFORM.md` | Platform design blueprint |

## Domain Context

- **Primary audience**: ML researchers
- **Target venues**: NeurIPS, ICML, ICLR, AAAI
- **LaTeX conventions**: cleveref, booktabs, amsmath
- **Figures**: matplotlib/seaborn, colorblind-safe, PDF export

## Adding New Content

### New Skill
1. Run `python3 scripts/create-skill.py --name skill-name --category academic` or manually create `plugins/{category}/commands/skill-name.md` with YAML frontmatter
2. Use kebab-case naming; group related skills with common prefix (e.g., `paper-*`)
3. Keep concise (150-400 lines), include examples in fenced blocks
4. Include `metadata:` block with research-domain, task-type, research-phase, verification-level (see `registry/categories.json` for valid values)
4. **Script-first principle**: If a skill's task (or a sub-task within it) can be accomplished via a script, CLI tool, or deterministic program, implement it that way. Reserve LLM-based approaches for tasks that genuinely require language understanding, creative writing, or nuanced judgment. Hybrid skills should run scriptable steps first, then use the LLM only for analysis or synthesis of results. Examples:
   - **Script-first**: Reference verification (`bibtexupdater`), dead code detection (`vulture`/`flake8`), LaTeX-to-plaintext conversion (regex/sed), metric extraction from configs (grep/parse), CI/CD setup (file generation), document creation (`python-docx`/`python-pptx`/`openpyxl`)
   - **LLM-appropriate**: Writing paper sections, generating rebuttals, reviewing papers, brainstorming titles, synthesizing literature narratives, designing TikZ diagrams
   - **Hybrid**: Extract data with scripts first, then have the LLM interpret/write prose from structured results

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
