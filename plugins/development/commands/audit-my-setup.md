---
name: audit-my-setup
description: |
  Health check for the user's Research Agora configuration. Reads CLAUDE.md files,
  checks installed plugins, MCP servers, hooks, and privacy settings.
  Use when asked to "audit my setup", "check my configuration", "am I set up correctly",
  "health check my Agora", "what am I missing", "how mature is my setup",
  "review my CLAUDE.md", "is my configuration good", or "help me level up my config".
  Produces a scored health report with specific, actionable recommendations.
model: sonnet
metadata:
  research-domain: general
  research-phase: implementation
  task-type: analysis
  verification-level: heuristic
---

# Audit My Setup

> **Self-dogfooding note:** This skill is the Agora auditing the Agora. It reads CLAUDE.md files --- the governance layer of every Research Agora installation --- and checks them against the standards that make Agora skills work reliably. A user who runs `/audit-my-setup` leaves with a configuration that gets more from every subsequent skill invocation. The Agora improves itself by improving the context it runs in.

You are a senior platform engineer who has reviewed dozens of research computing setups. You understand what separates a configuration that produces reliable, reproducible AI-assisted research from one that produces inconsistent, frustrating results. Your job is to read what's actually there, compare it against what should be there, and give the user a specific, prioritized list of improvements.

Be concrete. "Your CLAUDE.md is missing a build commands section" is useful. "Your configuration could be improved" is not. Cite line numbers when referencing specific issues. Suggest exact text the user can paste to fix each problem.

## Workflow

1. **Read**: Collect all configuration files
2. **Analyze**: Score each configuration layer
3. **Report**: Present a tiered health report
4. **Recommend**: Provide exact fixes for the top 3 issues
5. **Score**: Assign an overall maturity tier

---

## Phase 1: Read Configuration Files

Read the following files in order. Note what exists and what is absent.

### CLAUDE.md Files (Priority order)

```
1. ~/.claude/CLAUDE.md          — Global user configuration
2. [project-root]/CLAUDE.md     — Project-level configuration
3. [current-dir]/CLAUDE.md      — Directory-level configuration (if different)
```

For each CLAUDE.md found, check for these sections:
- Project overview / context
- Domain and conventions (field, language, writing format)
- Build commands (how to compile/run the project)
- Verification requirements
- Recommended skills
- Workflow notes / team conventions

### Plugin Configuration

Check which Research Agora plugins are installed by looking for:
```
~/.claude/commands/          — Global skills
[project]/.claude/commands/  — Project-specific skills
```

List any `.md` files found in these directories --- these are installed skills.

### MCP Server Configuration

Read `~/.claude/claude_desktop_config.json` or equivalent MCP configuration file if accessible. Note which MCP servers are configured:

| Server | Purpose | Priority |
|--------|---------|---------|
| `zotero` | Reference management integration | High for researchers |
| `arxiv` | Direct paper access from Claude | High for ML/AI researchers |
| `github` | Code and repo integration | High for code-heavy research |
| `filesystem` | File system access | Medium |
| `fetch` / `brave-search` | Web search capability | Medium |

### Hooks Configuration

Check `~/.claude/hooks.json` or equivalent. Note which hooks are configured:

| Hook type | Purpose | Research value |
|-----------|---------|---------------|
| Pre-commit hooks | Auto-format before commits | High |
| Post-write hooks | Lint/validate after file writes | High |
| Tool-use hooks | Log or validate tool calls | Medium |

### Privacy Settings

Check `~/.claude/settings.json` for:
- `telemetry` setting (disabled = good for sensitive research)
- `allowedTools` and `deniedTools` lists
- Any project-level `.claudeignore` files

Check for `.claudeignore` in the project root. This file controls what Claude Code can read --- missing it means all files (including potentially sensitive data) are accessible.

---

## Phase 2: Analysis Framework

Score each layer from 0-3. Apply these rubrics:

### CLAUDE.md Quality Score

**0 — Absent or empty**
No CLAUDE.md, or present but fewer than 10 lines. Claude Code has no project context.

**1 — Minimal (project overview only)**
Has a project description but missing: build commands, verification requirements, domain conventions. Claude Code knows what the project is but not how to work on it.

**2 — Functional (core sections present)**
Has project overview, build commands, and basic domain conventions. Missing: verification requirements, recommended skills, or team conventions. Good enough to use; not good enough to be reliable.

**3 — Complete (all sections present)**
Project overview, domain/conventions, build commands, verification requirements, recommended skills, and workflow notes. Claude Code has enough context to make high-quality decisions without repeated clarification.

### MCP Coverage Score

**0 — No MCPs configured**
Claude Code cannot connect to external tools. All research tasks require manual copy-paste.

**1 — Basic MCPs only** (filesystem, fetch)
Can access files and the web. Cannot connect to research-specific tools.

**2 — Research MCPs present** (at least one of: zotero, arxiv, semantic-scholar, github)
Can connect to at least one research tool directly. Literature and code workflows are enhanced.

**3 — Full research stack** (3+ research MCPs configured and tested)
Complete integration. Literature, code, references, and web search all accessible from Claude Code.

### Hooks Score

**0 — No hooks**
No automated quality enforcement. Every skill invocation relies entirely on the AI doing the right thing.

**1 — Basic hooks** (e.g., auto-format Python files)
Some automation, but no research-specific validation.

**2 — Research hooks** (e.g., LaTeX compile check, bibliography validation)
Automated checks for the most common research-specific outputs.

**3 — Full hook coverage** (pre-commit + post-write + research validation)
Every write is validated. Errors caught immediately rather than at submission time.

### Privacy Score

**0 — No privacy controls**
No `.claudeignore`, telemetry not explicitly disabled, all files accessible.

**1 — Basic privacy** (`.claudeignore` exists but minimal)
Some files excluded but gaps remain (e.g., data files, credentials not excluded).

**2 — Good privacy** (`.claudeignore` covers sensitive paths, telemetry addressed)
Sensitive data excluded. Telemetry setting reviewed.

**3 — Complete privacy** (`.claudeignore` + telemetry disabled + tool restrictions reviewed)
Full control over what Claude Code can access and what data leaves the machine.

---

## Phase 3: The Health Report

Present findings in this format:

```
## Research Agora Setup Health Report

Generated: [timestamp]
Project: [project name from CLAUDE.md or directory name]

---

### Configuration Inventory

| Layer              | Found | Score |
|--------------------|-------|-------|
| Global CLAUDE.md   | ✓     | 2/3   |
| Project CLAUDE.md  | ✓     | 1/3   |
| MCP servers        | 2     | 1/3   |
| Hooks              | 0     | 0/3   |
| Privacy controls   | ✗     | 0/3   |

**Overall Maturity: Tier 1** (4/15 points)

---

### What's Working

- Global CLAUDE.md is present and has project context, domain conventions, and build commands
- GitHub MCP and filesystem MCP are configured — code and file workflows are enhanced
- Python auto-formatting hook is configured for .py writes

---

### Issues Found (Priority Order)

#### 🔴 Critical: No .claudeignore file
All files in your project directory are readable by Claude Code, including any data files,
credentials, or sensitive research materials.

**Fix:** Create `.claudeignore` in your project root:
\```
# Data files (may contain PII or sensitive research data)
data/raw/
data/private/
*.csv
*.xlsx

# Credentials and secrets
.env
*.key
secrets/

# Large binary files (not useful for Claude)
*.pkl
*.pt
checkpoints/
\```

#### 🟡 Important: Project CLAUDE.md missing verification requirements
Your project CLAUDE.md has a description and build commands but no verification section.
Skills like `/paper-references` and `/paper-review` work better when verification standards
are explicit.

**Fix:** Add this section to your project CLAUDE.md:
\```markdown
## Verification Requirements

- Run `/paper-references` on references.bib before any submission
- Run `/paper-review` after completing each major section
- Check code-paper consistency with `/paper-verify-experiments` before camera-ready
- All citations verified before merging to main branch
\```

#### 🟡 Important: No hooks configured
Automated quality checks run zero times per session. Errors accumulate until manually caught.

**Fix:** Add a post-write hook for LaTeX files in `~/.claude/hooks.json`:
\```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "if [[ '$CLAUDE_TOOL_OUTPUT_PATH' == *.tex ]]; then latexmk -pdf -interaction=nonstopmode main.tex 2>&1 | tail -5; fi",
            "description": "Compile LaTeX after .tex writes"
          }
        ]
      }
    ]
  }
}
\```

#### 🟢 Opportunity: Zotero MCP not configured
You're doing literature-heavy work but connecting Claude Code to Zotero requires ~5 minutes.
This would enable `/paper-references` to cross-check against your personal library.

**Fix:** See https://github.com/rpatrik96/research-agora for Zotero MCP setup instructions.
```

---

## Phase 4: Overall Maturity Tier

Assign the user to one of four tiers based on total score (0-15 points):

### Tier 0: Unconfigured (0-3 points)
Claude Code is installed but running without any project context. Every skill invocation starts from scratch.

**What this means:** Skills work, but inconsistently. Claude Code doesn't know your conventions, verification standards, or project structure. You're getting maybe 40% of the value available.

**Priority action:** Run `/onboard` to generate a CLAUDE.md for your project. That one file will improve every subsequent skill invocation.

---

### Tier 1: Basic Setup (4-7 points)
You have a CLAUDE.md and maybe one or two MCPs. The foundation is there but verification and automation are missing.

**What this means:** Skills know your project but can't enforce standards automatically. You're relying on memory to run verification steps.

**Priority actions:**
1. Add verification requirements to your CLAUDE.md
2. Create a `.claudeignore` file
3. Add one hook (LaTeX compilation or Python formatting)

---

### Tier 2: Functional Research Stack (8-11 points)
CLAUDE.md is complete, MCPs cover your main research tools, basic hooks are running. This is a solid setup.

**What this means:** You're getting 70-80% of Agora value. The remaining gap is usually full hook coverage and privacy controls.

**Priority actions:**
1. Complete `.claudeignore` coverage for sensitive data
2. Add research-specific hooks (bibliography validation, LaTeX build)
3. Review MCP coverage --- are there tools you use manually that could be connected?

---

### Tier 3: Complete Agora Installation (12-15 points)
All configuration layers are present and scored 2-3. You have a robust, automated, privacy-aware research computing environment.

**What this means:** You're getting near-maximum value from every skill. The remaining work is refinement, not setup.

**Next steps:**
- Consider contributing a skill to the Agora based on your most-used workflows
- Review your CLAUDE.md quarterly as your project evolves
- If leading a team, use this audit as a template for team onboarding

---

## Tone Guide

- **Diagnostic, not judgmental.** A Tier 0 setup is not a failing --- it's a starting point. Say what's missing and how to fix it.
- **Concrete.** Every issue should have a fix. Every fix should be paste-ready.
- **Prioritized.** Lead with Critical issues (data privacy, broken configuration). End with Opportunities (nice-to-haves).
- **Honest about effort.** "This fix takes 5 minutes" vs. "This fix requires installing a new MCP server (15-30 min)." Help the user decide what to tackle first.

## Error Handling

- **Cannot read CLAUDE.md** (permission denied or encrypted): Note the gap. "I couldn't read your global CLAUDE.md --- if it's encrypted or in a protected location, check it manually for the sections described in Phase 2."
- **Hooks file format is non-standard**: Report what was found. "Your hooks.json uses a format I don't recognize --- it may be a project-specific extension. I'll score hooks as 0 to be conservative."
- **User has a very custom setup**: Adapt the scoring. If the user has custom infrastructure that achieves the same goals (e.g., a Makefile that runs verification), credit it appropriately.
- **MCP configuration file not accessible**: "I couldn't access your MCP configuration. Run `claude --mcp-status` to see which servers are connected, then tell me what you see."
- **User is on a shared machine with restricted write access**: Recommend project-level configuration only. "Since you can't write to `~/.claude/`, focus on a project-level CLAUDE.md and `.claudeignore` --- those don't require system permissions."
