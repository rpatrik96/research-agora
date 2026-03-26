# Git as a Safety Net for AI Agent Workflows

Think of git as **"Save Game" for your project**. You save before attempting something risky, and if it goes wrong, you load the save.

AI agents edit your files directly. That's what makes them powerful — and what makes them risky. A single misunderstood instruction can rewrite a section of your paper, delete a file, or overwrite hours of work. Git makes those mistakes cheap to fix.

> **Already use git?** Skip to [If You Already Use Git](#if-you-already-use-git) for agent-specific recommendations.

---

## The Problem: Agents Act Faster Than You Can Review

When you use Claude Code (or any agentic coding tool), the agent reads and writes files on your machine. Most of the time, this is exactly what you want. But agents can:

- **Overwrite good work** — an edit that "improves" a paragraph may destroy a carefully worded argument.
- **Delete files** — cleanup operations can remove things you still need.
- **Make sweeping changes** — a single instruction like "refactor this" can touch dozens of files at once.

Agents operate faster than you can read their output. You need a way to go back.

---

## What This Guide Does NOT Cover

Git recovery works only if a snapshot exists before the damage happens. Be aware of these limitations:

- **No prior snapshot = no recovery.** If you never ran `git commit` before starting an agent session, git cannot help you. This is the most common way people lose work.
- **New files survive undo.** When you undo agent changes, files the agent *created* (that were never committed) are not removed automatically. You must delete them manually or with `git clean -fd` (which permanently deletes all untracked files — cannot be undone).
- **Shared repositories need extra care.** If your project lives on GitHub with collaborators, agent changes pushed to a shared branch affect everyone. Local undo does not reverse a remote push. Always review before pushing.
- **Data leaves your machine.** Claude Code sends file contents to Anthropic's servers for processing. **Do not use it with**: patient/health data (HIPAA), student records (FERPA), export-controlled material (ITAR/EAR), data covered by a third-party NDA or data-sharing agreement, or anything under a confidentiality clause in a grant. For general unpublished research, review [Anthropic's privacy policy](https://www.anthropic.com/privacy) and your institution's acceptable-use policy for AI tools. If in doubt, check with your research compliance office. See also our [Privacy & GDPR guide](privacy.html).

---

## What Git Does (30-Second Version)

Git takes **snapshots** of your project. Each snapshot (called a **commit**) records the exact state of every file at that moment. Files included in a snapshot are called **tracked**. New files the agent creates are **untracked** until you include them in a snapshot — undoing changes does not remove untracked files.

You can:

- **Compare** any two snapshots to see what changed.
- **Restore** any file to any previous snapshot.
- **Undo** everything an agent did since the last snapshot, in one command.

---

## Before You Start

Two things must be true before the commands below will work.

### 1. Git must be installed

Open your terminal:
- **macOS**: Press Cmd+Space, type "Terminal", press Enter.
- **Windows**: Search for "Git Bash" in the Start menu (installed with git). If you don't have it, install git first from [git-scm.com/downloads](https://git-scm.com/downloads).
- **Linux**: Open your distribution's terminal application.

Type this and press Enter:

```bash
git --version
```

If you see a version number (e.g., `git version 2.39.0`), you're ready. If you see an error, install git from [git-scm.com/downloads](https://git-scm.com/downloads), then restart your terminal and try again.

### 2. You need to know where your project folder is

You'll need the **path** — the address of your folder on disk. To find it:
- **macOS**: Drag your project folder from Finder into the Terminal window. The path appears automatically.
- **Windows**: Right-click the folder in File Explorer and choose "Copy as path."
- **Linux**: Right-click the folder in your file manager and look for "Copy path" or similar.

---

## Setup (One Time, 2 Minutes)

### Step 1: Create a .gitignore file

This tells git which files to skip — large binaries, credentials, and generated output. The safest way to create it: open **VS Code**, press Ctrl+N (Windows/Linux) or Cmd+N (macOS) to create a new file, paste the contents below, then use "Save As" and type `.gitignore` exactly (including the dot) as the filename, saving it in your project folder.

> **Warning:** If you use Notepad (Windows) or TextEdit (macOS) instead, they may silently append `.txt` to the filename, producing `.gitignore.txt` — which git ignores entirely. VS Code does not have this problem.

```
# Large files (model weights, datasets)
*.pt
*.pkl
*.h5
*.ckpt
data/
outputs/
wandb/

# Secrets and credentials
.env
.env.*
```

After saving, verify it worked by running this in your terminal (Windows users: run this in Git Bash, not PowerShell or Command Prompt):

```bash
ls -a
```

You should see `.gitignore` in the output. (`ls -a` lists all files, including hidden ones that start with a dot.)

### Step 2: Initialize git and take your first snapshot

`cd` means "change directory" — it tells the terminal which folder to work in. Replace the example path with your actual project path. (`~` is shorthand for your home folder, so `~/Documents` is the same as `/Users/yourname/Documents` on macOS.)

```bash
cd ~/Documents/my-paper
git init
git add -A
git commit -m "Initial snapshot before using AI agents"
```

What each line does:
1. `cd ~/Documents/my-paper` — navigates to your project folder. Replace with your actual path (see "Before You Start" above).
2. `git init` — tells git to start tracking this folder. A hidden `.git` folder is created inside your project. You won't see it in your file manager — that's normal and intentional. You can verify it exists by running `ls -a` and looking for `.git` in the output.
3. `git add -A` — selects all files (except those in `.gitignore`) for the snapshot.
4. `git commit -m "..."` — saves the snapshot with a label you choose.

If any command shows an error starting with `error:` or `fatal:`, check that git is installed (`git --version`) and that you're in the right folder.

---

## The Two Commands That Matter

### Before an agent session: save a snapshot

```bash
git add -A && git commit -m "Snapshot before agent session"
```

(`&&` runs the second command only if the first succeeds. You can also type them as two separate commands, one at a time.)

Before committing, scan for surprises with `git status` — agents occasionally create configuration or credential files. Verify nothing sensitive is listed before proceeding.

This records the current state. If the agent makes unwanted changes, you can always get back here.

### After an agent session: review what changed

```bash
git diff HEAD
```

This shows every line the agent added, removed, or modified in your working tree since your last snapshot. In the output, lines starting with `+` were added and lines starting with `-` were removed. Use the arrow keys or spacebar to scroll. Press `q` to exit the diff view.

Read through it. If the changes look good, save a new snapshot:

```bash
git add -A && git commit -m "Agent session: revised introduction"
```

If the changes look bad, undo everything:

```bash
git restore .
```

This restores every **tracked** file to the last snapshot. Files the agent *created* (that were never in a snapshot) remain — remove them manually or run `git clean -fd` (which permanently deletes all untracked files — cannot be undone).

---

## When to Snapshot

| Moment | Why |
|--------|-----|
| Before starting Claude Code | Creates a restore point |
| After reviewing good changes | Locks in the progress |
| Before risky instructions ("refactor", "rewrite", "clean up") | Extra safety for broad edits |
| At the end of a work session | Checkpoint before you step away |

The cost of snapshotting is near zero (one command, under a second). The cost of *not* snapshotting is potentially hours of lost work.

---

## Recovering from Bad Agent Edits

### Undo all changes since last snapshot

```bash
git restore .
```

(Tracked files only. To also remove new files the agent created: `git clean -fd` — this permanently deletes all untracked files and cannot be undone.)

### Undo changes to one specific file

```bash
git restore paper/introduction.tex
```

### See what the agent changed

```bash
git diff HEAD                # Everything changed since last snapshot
git log --oneline -10        # Last 10 snapshots (change the number to see more)
```

### Go back to a specific snapshot

`git log --oneline` shows output like:

```
3f2a9c1 Before agent: rewrite methods section
a7d3e02 Agent session: revised introduction
e5b1f83 Initial snapshot before using AI agents
```

The 7-character code at the start is the snapshot ID. Use it to restore:

```bash
git restore --source=3f2a9c1 .
```

This updates your working files to match that snapshot. Your commit history is unchanged — older commits remain visible in `git log`. After running this, run `git add -A && git commit -m "Restored to pre-agent state"` to record the rollback as a new snapshot.

---

## Making Mistakes Cheap to Fix

Git doesn't prevent agents from making mistakes — it makes those mistakes **cheap to fix**. Here's the mental model:

1. **Snapshot before, review after.** This is the entire workflow. Everything else is optional.
2. **Small snapshots beat big ones.** If you snapshot every 15 minutes, the most you can lose is 15 minutes of work. If you snapshot once a day, you could lose an entire day.
3. **Commit messages are your memory.** Write what you're about to ask the agent to do: `"Before agent: rewrite methods section"`. When something goes wrong, you'll know exactly which snapshot to return to.
4. **`git diff HEAD` is your review tool.** Agents can change 50 files at once. Scrolling through terminal output isn't enough. `git diff HEAD` gives you a structured, line-by-line account of every change.

---

## What You Can Safely Ignore (For Now)

Git has hundreds of commands and concepts. For backup purposes with a **solo, local** project, you need exactly these:

| Command | What it does |
|---------|-------------|
| `git init` | One-time setup |
| `git add -A` | Select all changes for snapshot |
| `git commit -m "message"` | Take a snapshot |
| `git diff HEAD` | See what changed since last snapshot |
| `git restore .` | Undo all changes since last snapshot |
| `git log --oneline` | List your snapshots |

If you work in a **shared repository** with collaborators (e.g., a paper repo on GitHub), you will also need `git push`, `git pull`, and branches. The key rule: **never push agent-generated changes to a shared branch without reviewing them first.** Create a personal branch (see [Branches for Risky Experiments](#advanced-branches-for-risky-experiments) below — ignore the "skip this" note if you are on a shared repository), review with `git diff HEAD`, and coordinate with collaborators before merging.

---

## Advanced: Branches for Risky Experiments

> Skip this until you are comfortable with the six commands above — unless you work on a shared repository, in which case read this now.

If you want to try a risky agent instruction without touching your main work, create a separate branch — an independent copy of your project:

```bash
git switch -c experiment-rewrite     # Create a separate branch
# ... run the agent ...
git switch main                      # Switch back to your safe version
git branch -D experiment-rewrite     # Delete the experiment if it failed
```

`-D` force-deletes the branch even if you haven't merged it. Use it when you're sure the experiment failed. Use `-d` (lowercase) for a safer delete that warns you if you have unmerged work.

Note: your default branch may be called `main` or `master` depending on your git version. Check with `git branch` — the one marked with `*` is your current branch.

---

## Quick Reference Card

```
BEFORE agent session:     git add -A && git commit -m "Before: [what you plan to do]"
AFTER agent session:      git diff HEAD
KEEP changes:             git add -A && git commit -m "After: [what the agent did]"
UNDO all changes:         git restore .                       # if nothing is staged
UNDO + remove new files:  git restore . && git clean -fd      # irreversible
UNDO one file:            git restore paper/introduction.tex
```

---

## If You Already Use Git

You already have the safety net. Agent-specific recommendations:

- **Commit more frequently.** Agents make more changes per unit time than humans. A commit per logical agent task is a reasonable cadence.
- **Claude Code writes to your working tree by default.** It does not stage, commit, or push unless you instruct it to — but it can execute shell commands, so a sufficiently broad instruction (e.g., "save and sync your changes") could trigger a push. If your lab uses shared repositories, establish an explicit rule: no `git push` during agent sessions.
- **Stash or commit before starting.** If you have staged but uncommitted changes, the agent can overwrite those files. Run `git stash --include-untracked` (to set aside all work including new files) or `git add -A && git commit` (to record the current state as a snapshot) before starting a session.
- **Pre-commit hooks run normally.** When you commit after a session, your hooks fire as usual — the agent does not bypass them.
- **Use `git switch -c experiment/<task>` for risky instructions.** Keeps your main branch clean regardless of outcome.
- **`git reflog` is your last resort.** If you accidentally reset or delete commits, `git reflog` shows recent HEAD positions and lets you recover.

---

## FAQ

**Q: Will git slow down my workflow?**
No. A commit takes under a second. Reviewing a diff takes 30 seconds. Compared to the hours you could lose from an unrecoverable agent edit, this is negligible.

**Q: What about large files (datasets, models)?**
The `.gitignore` file created during setup excludes them. Git works best with text files (`.tex`, `.py`, `.md`). Large binary files like model weights or datasets should always be in `.gitignore`. If you forgot and already committed them, ask Claude Code to help you clean up the history.

**Q: What if I forget to snapshot and the agent wrecks my files?**
If the files were never committed, git cannot recover them. This is why the pre-session snapshot habit matters. As a last resort: VS Code and PyCharm maintain local file history independently — check there. On macOS, Time Machine may also have a recent backup.

**Q: My lab uses Overleaf. Does this apply?**
Overleaf has its own version history (History tab in the editor). If you don't use Overleaf's git sync feature, this guide does not apply directly — use Overleaf's built-in history instead. If you do use git sync, the same snapshot workflow works.

**Q: Can an agent push changes to my GitHub repo?**
Not unless you instruct it to. Claude Code does not push automatically. However, broadly worded instructions could trigger a push via shell commands, so be specific in your prompts. Always review changes locally with `git diff HEAD` before pushing to a shared remote.
