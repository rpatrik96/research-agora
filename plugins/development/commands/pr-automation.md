---
name: pr-automation
description: Create GitHub pull requests from changes made during a chat session. Use when asked to "create a PR", "open a pull request", "submit changes", "push and create PR", or at the end of a coding session when changes should be submitted for review. Handles branch creation, conventional commits, and PR description generation.
---

# PR Automation

> **Script-first**: This skill is implemented via git and gh CLI commands. No LLM generation needed.

Create GitHub pull requests from chat session changes.

## Prerequisites

- `gh` CLI installed and authenticated (`gh auth status`)
- Git repository initialized with remote
- Changes staged or working directory modifications

## Workflow

### 1. Create feature branch

```bash
# Branch naming: type/short-description
git checkout -b feat/add-data-loader
git checkout -b fix/memory-leak-training
git checkout -b refactor/simplify-config
```

Branch prefixes:
- `feat/` - New feature
- `fix/` - Bug fix
- `refactor/` - Code refactoring
- `docs/` - Documentation
- `test/` - Tests
- `chore/` - Maintenance

### 2. Stage and commit

```bash
# Stage all changes (or selective)
git add -A

# Conventional commit
git commit -m "feat: add streaming data loader

- Implement lazy loading for large datasets
- Add prefetch buffer configuration
- Support multiple file formats (csv, parquet, json)

Closes #123"
```

#### Conventional commit format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

### 3. Push branch

```bash
git push -u origin HEAD
```

### 4. Create PR with gh CLI

```bash
gh pr create \
  --title "feat: add streaming data loader" \
  --body "## Summary
Implements streaming data loader for memory-efficient training on large datasets.

## Changes
- Add \`StreamingDataset\` class with lazy loading
- Implement prefetch buffer for I/O optimization
- Support csv, parquet, and json formats

## Testing
- Unit tests in \`tests/test_streaming.py\`
- Verified on 100GB dataset with 2GB memory limit

## Checklist
- [x] Tests pass
- [x] Documentation updated
- [x] No breaking changes" \
  --reviewer username1,username2 \
  --label enhancement
```

## Quick Commands

### One-liner for simple changes

```bash
git checkout -b feat/quick-fix && \
git add -A && \
git commit -m "feat: quick description" && \
git push -u origin HEAD && \
gh pr create --fill
```

### Interactive PR creation

```bash
gh pr create --web  # Opens browser for PR form
```

### From existing branch

```bash
gh pr create --base main --head feature-branch
```

## PR Description Template

```markdown
## Summary
Brief description of what this PR does.

## Motivation
Why is this change needed?

## Changes
- Change 1
- Change 2
- Change 3

## Testing
How were the changes tested?

## Screenshots (if applicable)

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Breaking changes documented
- [ ] Linked to issue (if applicable)
```

## Automation Script

Run `scripts/create_pr.sh` for guided PR creation:

```bash
./scripts/create_pr.sh "feat" "add streaming loader" "Implements streaming data loader"
```

## Tips

- Use `--draft` for work-in-progress PRs
- Add `--assignee @me` to self-assign
- Use `gh pr view --web` to open PR in browser after creation
- Check PR status with `gh pr status`

## Handling Conflicts

```bash
# Update branch with main
git fetch origin main
git rebase origin/main

# If conflicts, resolve then:
git add -A
git rebase --continue
git push --force-with-lease
```
