---
name: commit
description: |
  Commit changes made during the current conversation. Use when asked to
  "commit", "save changes", "create a commit", or "commit my changes".
  Generates conventional commit messages with co-authorship attribution.
model: haiku
---

# Commit Changes

Commit changes made during the current Claude Code conversation with proper conventional commit format and co-authorship.

## Overview

This skill commits staged and unstaged changes from the current session. It analyzes the changes to generate a meaningful commit message following conventional commit conventions and includes Claude as co-author.

## Workflow

1. **Check repository status** - Run `git status` to see all changes
2. **Review changes** - Run `git diff` to understand what was modified
3. **Check recent commits** - Run `git log --oneline -5` to match commit style
4. **Stage changes** - Add relevant files with `git add`
5. **Create commit** - Write conventional commit message with co-author
6. **Verify** - Run `git status` to confirm commit succeeded

## Pre-requisites

- Git repository initialized
- Changes exist (staged or unstaged)
- User has requested or approved the commit

## Commit Message Format

### Conventional Commits

```
<type>(<scope>): <description>

[optional body]

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no code change |
| `refactor` | Code change that neither fixes nor adds |
| `perf` | Performance improvement |
| `test` | Adding or updating tests |
| `chore` | Maintenance, dependencies |

### Examples

```bash
# Simple feature
git commit -m "$(cat <<'EOF'
feat: add user authentication endpoint

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

# Bug fix with scope
git commit -m "$(cat <<'EOF'
fix(api): handle null response from external service

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

# Multi-line with body
git commit -m "$(cat <<'EOF'
refactor: simplify data processing pipeline

- Extract validation into separate function
- Remove redundant error handling
- Improve type annotations

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

## Guidelines

### DO

- Summarize the "what" and "why" in the first line
- Keep the subject line under 72 characters
- Use imperative mood ("add" not "added")
- Include scope when changes are localized (e.g., `fix(auth):`)
- Add body for complex changes explaining motivation

### DON'T

- Don't commit secrets, credentials, or `.env` files
- Don't use vague messages like "fix bug" or "update code"
- Don't commit unrelated changes in one commit
- Don't skip the co-author line

## Selective Commits

When changes span multiple concerns, create separate commits:

```bash
# Commit only specific files
git add src/auth.py tests/test_auth.py
git commit -m "feat(auth): add JWT token validation

Co-Authored-By: Claude <noreply@anthropic.com>"

# Then commit remaining changes
git add .
git commit -m "docs: update API documentation

Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Output

After running this skill:
- Changes are committed to the current branch
- Commit message follows conventional format
- Claude is listed as co-author
- `git status` shows clean working tree (or remaining unstaged changes)

## Checklist

- [ ] All intended changes are staged
- [ ] No secrets or credentials included
- [ ] Commit message describes the change clearly
- [ ] Type prefix matches the nature of changes
- [ ] Co-author line is included
- [ ] Commit succeeded (verified with `git status`)
