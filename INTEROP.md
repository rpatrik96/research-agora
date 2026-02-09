# Agent Interoperability

Research Agora skills are designed for Claude Code but can be converted for use with other AI coding agents.

## Supported Platforms

| Platform | Native Format | Converter | Status |
|----------|---------------|-----------|--------|
| **Claude Code** | `commands/*.md` (YAML frontmatter) | Native | Full support |
| **Cursor** | `.cursor/rules/*.mdc` | `--format cursor` | Skill instructions |
| **Gemini CLI** | `.gemini/agents/*.md` | `--format gemini` | Skill instructions |
| **GitHub Copilot** | `.github/copilot-instructions.md` | `--format copilot` | Single file |
| **AgentSkills.io** | `SKILL.md` | `--format agentskills` | Standard format |

## Converting Skills

### Single Skill

```bash
# Convert paper-references to Cursor format
python scripts/convert-skill.py --format cursor --skill paper-references --output /path/to/project

# Convert to Gemini CLI format
python scripts/convert-skill.py --format gemini --skill paper-references --output /path/to/project
```

### All Skills in a Plugin

```bash
# Convert all academic skills to Cursor format
python scripts/convert-skill.py --format cursor --plugin academic --output /path/to/project
```

### All Skills

```bash
# Convert everything to AgentSkills.io format
python scripts/convert-skill.py --format agentskills --all --output /path/to/export
```

## Format Details

### Claude Code (Native)

```yaml
---
name: paper-references
description: Verify citations against scholarly databases.
model: sonnet
metadata:
  research-domain: general
  task-type: verification
  research-phase: paper-writing
  verification-level: formal
---
# Skill content...
```

### Cursor (.mdc)

```yaml
---
description: Verify citations against scholarly databases.
globs:
alwaysApply: false
---
# Skill content...
```

### Gemini CLI

```markdown
# paper-references
Verify citations against scholarly databases.
# Skill content...
```

### GitHub Copilot

All skills are concatenated into `.github/copilot-instructions.md`:

```markdown
## paper-references
Verify citations against scholarly databases.
# Skill content...
```

### AgentSkills.io

```yaml
---
name: paper-references
version: "1.0.0"
description: Verify citations against scholarly databases.
author: Research Agora
license: MIT
model: sonnet
tags: [general, verification, paper-writing]
platforms: [claude-code, cursor, gemini-cli]
---
# Skill content...
```

## Limitations

- **Tool calls**: Skills that use Claude Code-specific tools (e.g., `mcp__arxiv__search_papers`) will need manual adaptation for other platforms
- **Agent architecture**: The orchestrator/micro-skill/helper pattern in `research-agents` is Claude Code-specific
- **Model routing**: Model tiers (opus/sonnet/haiku) map differently across platforms
- **Metadata**: The `metadata:` block is Research Agora-specific; other platforms may ignore it

## Contributing Cross-Platform Support

When creating new skills, consider cross-platform compatibility:

1. **Avoid platform-specific tool names** in the main skill logic where possible
2. **Use standard markdown** for instructions
3. **Document external dependencies** (CLI tools, APIs) clearly
4. **Test with the converter** before submitting
