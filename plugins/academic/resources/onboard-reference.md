# Onboard Reference Material

> This file is read on-demand by the onboard skill after the interview phase completes.
> Do NOT load this into the skill prompt — use `Read` tool to access when needed.

## Phase 3: Generate Personalized CLAUDE.md

Based on interview answers, generate a `CLAUDE.md` file tailored to the user's project. Present it as a code block they can save to their project root.

### Template Structure

```markdown
# [Project Name or Domain] --- CLAUDE.md

## Project Overview

[1-2 sentences describing what this project is about, derived from interview answers]

## Domain & Conventions

- **Field**: [their domain]
- **Writing format**: [LaTeX / Markdown / Word --- inferred from answers]
- **Citation style**: [BibTeX / APA / etc. --- inferred or ask]
- **Programming language(s)**: [from interview]

## Build Commands

[Only include sections relevant to their stack]

### Paper
```bash
latexmk -pdf main.tex          # if LaTeX
```

### Code
```bash
[language-appropriate commands: pytest, Rscript, julia, make, etc.]
```

## Git Safety Net

[Include if user does not already use git, or if Tier 0-1]

Before running any AI agent on your project, take a snapshot so you can undo changes:

```bash
git add -A && git commit -m "Snapshot before agent session"
```

After a session, review what the agent changed:

```bash
git diff HEAD
```

Undo everything if needed: `git restore .`

For the full guide: https://rpatrik96.github.io/research-agora/git-backup.html

## Verification Requirements

[Tier-appropriate verification expectations]

### Tier 0-1:
- Check AI-generated citations against Google Scholar before including them
- Read AI-drafted text critically --- treat it as a first draft from a hasty coauthor

### Tier 2:
- Run `/paper-references` on bibliography before submission
- Use `/paper-verify-experiments` to check claims against code
- Cross-reference AI-generated literature claims with actual papers

### Tier 3:
- All citations verified via `bibtexupdater` before merge
- Experiment-paper sync via `/experiment-tracker`
- Code-paper consistency checked in CI

## Recommended Skills

[3-5 skills selected based on their task interests and tier]

| Skill | What it does | When to use |
|-------|-------------|-------------|
| `/skill-name` | [one-line description] | [trigger phrase] |
| ... | ... | ... |

## Workflow Notes

[Any domain-specific or tier-specific guidance]
```

### Skill Recommendations by Task

Select 3-5 skills from this mapping based on the user's primary task and tier:

**Literature review / references:**
| Skill | Tier | Description |
|-------|------|-------------|
| `/paper-references` | 1+ | Verify citations against arXiv, Crossref, DBLP |
| `/literature-synthesizer` | 1+ | Discover and synthesize related work |
| `/benchmark-scout` | 2+ | Find relevant benchmarks and baselines |

**Writing:**
| Skill | Tier | Description |
|-------|------|-------------|
| `/paper-abstract` | 1+ | Diagnose an abstract you wrote |
| `/argument-autopsy` | 1+ | Map the paper's claim-evidence structure |
| `/paper-review` | 2+ | Simulate skeptical reviewer feedback |

**Experiments / code:**
| Skill | Tier | Description |
|-------|------|-------------|
| `/paper-verify-experiments` | 2+ | Check paper claims against source code |
| `/experiment-tracker` | 2+ | Sync experiment results to paper tables |
| `/code-simplify` | 1+ | Simplify and refactor research code |

**Dissemination:**
| Skill | Tier | Description |
|-------|------|-------------|

**Admin / teaching:**
| Skill | Tier | Description |
|-------|------|-------------|
| `/review-triage` | 2+ | Organize and prioritize reviewer comments |
| `/openreview-submission` | 2+ | Format and submit to OpenReview |

## Phase 4: The 5-Minute Win

After generating the `CLAUDE.md`, recommend ONE concrete task the user can do right now. This is the moment they go from "interested" to "using it." Make it specific.

### Tier 0: A Structured Prompt

Give them a copy-pasteable prompt for Claude.ai or ChatGPT that addresses their stated task. Frame it as: "Paste this into Claude.ai and see what happens."

**Example for literature review:**

```
I'm writing a paper about [TOPIC] in [DOMAIN]. I need to find the 10 most
important papers I should cite. For each paper, give me:
1. Full citation (authors, title, venue, year)
2. One sentence on why it matters to my work
3. A key finding or claim I might reference

After listing them, organize them into 2-3 thematic groups and suggest
how my related work section could be structured.

IMPORTANT: For each paper you list, I will verify it exists. If you are
not confident a paper is real, say so. Do not fabricate citations.
```

**Example for writing:**

```
Here is my paper abstract. Diagnose it:
- Does it have all 5 parts? (context, problem, approach, results, impact)
- Are claims specific or vague?
- What's the weakest sentence and how would you fix it?

[PASTE ABSTRACT]
```

Tell them: "This is what structured prompting looks like. The Research Agora packages hundreds of these into reusable skills. When you're ready to move to the CLI, come back and we'll set up Claude Code."

### Tier 1: Run Your First Skill

If the user doesn't have git set up, offer to initialize it first as a safety net:

```bash
# Optional but recommended: set up git as your undo button
cd /path/to/your/project
git init
git add -A && git commit -m "Initial snapshot before using AI agents"
# Full guide: https://rpatrik96.github.io/research-agora/git-backup.html
```

Then walk them through running a single skill. Choose based on their task:

**If literature/references:**
```bash
# In your paper directory:
claude "/paper-references"
# Point it at your .bib file when it asks
```

**If writing:**
```bash
# In your paper directory:
claude "/paper-review"
# It will read your LaTeX files and generate a reviewer-style critique
```

**If code:**
```bash
# In your code directory:
claude "/code-simplify"
# Point it at a file you've been meaning to clean up
```

Tell them: "That's it. One command, one skill, one result you can evaluate. If it's useful, try another. If it's not, tell me what went wrong."

### Tier 2: Set Up Verification

If their project isn't under git yet, set it up first. If it is, recommend more frequent commits during agent sessions (see the "If You Already Use Git" section at https://rpatrik96.github.io/research-agora/git-backup.html).

Walk them through a verification workflow:

```bash
# 0. Safety net: snapshot before agent work
git add -A && git commit -m "Before verification run"

# 1. Save the CLAUDE.md we just generated
#    (copy the block above to your project root)

# 2. Run citation verification
claude "/paper-references"

# 3. If you have experiment code, check paper-code consistency
claude "/paper-verify-experiments"

# 4. Get a simulated review
claude "/paper-review"
```

Tell them: "You now have a verification pipeline. Before your next submission, run steps 2-4. Treat it like running tests before a release."

**If they use Zotero**, also mention:
```
The Zotero MCP can connect Claude Code directly to your library.
Ask me to help configure it --- takes about 5 minutes.
```

### Tier 3: Build or Extend

For power users, the 5-minute win is about agency, not hand-holding:

- **If they want orchestration**: Point them to multi-agent patterns (research-agents plugin) and show how skills compose.
- **If they want to contribute**: Show them the skill file format (this very file is an example) and suggest they package one of their existing workflows as a skill.
- **If they want governance**: Discuss `CLAUDE.md` as a governance document --- encoding team standards, verification requirements, and review checklists.

Tell them: "The Agora is built by researchers for researchers. If you've built a workflow that works, package it as a skill and submit a PR. That's how this thing grows."

## Phase 5: What's Next

Close with a short orientation pointing to the appropriate next steps. Adjust based on tier.

### Tier 0
```markdown
## What's Next

1. **Try the structured prompts** above for your immediate task
2. **When you're ready for more**: Install Claude Code (https://docs.anthropic.com/en/docs/claude-code)
3. **Set up git as a safety net**: Follow the 2-minute setup at https://rpatrik96.github.io/research-agora/git-backup.html --- it gives you an undo button for agent edits
4. **Come back**: Run `/onboard` again once you have Claude Code --- I'll set you up with skills
```

### Tier 1
```markdown
## What's Next

1. **Save your CLAUDE.md** to your project root
2. **Set up git** if you haven't already --- it's your undo button for agent edits (https://rpatrik96.github.io/research-agora/git-backup.html)
3. **Try 2-3 skills** this week --- see which ones stick
4. **When something doesn't work**: That's feedback. Adjust your CLAUDE.md or try a different skill
5. **Level up**: Once you're comfortable, explore the verification workflows (`/paper-references`, `/paper-verify-experiments`)
```

### Tier 2
```markdown
## What's Next

1. **Save your CLAUDE.md** and commit it to your repo
2. **Snapshot before agent sessions**: `git add -A && git commit -m "Before: [task]"` --- see agent-specific git tips at https://rpatrik96.github.io/research-agora/git-backup.html#already-use-git
3. **Integrate verification** into your pre-submission checklist
4. **Explore MCP tools**: Zotero, arXiv, and GitHub MCPs extend what skills can do
5. **Customize**: Edit your CLAUDE.md as you learn what works --- it's a living document
6. **Share**: If a colleague asks how you verified your citations, show them `/onboard`
```

### Tier 3
```markdown
## What's Next

1. **Audit your current workflows** --- which ones are skill-shaped?
2. **Package one workflow** as a skill and submit it to the Agora
3. **Explore research-agents**: 22 specialized agents for devil's advocate analysis, evidence checking, audience alignment
4. **Governance**: Use CLAUDE.md to encode your lab's standards across projects
5. **Benchmark**: If you're working on evaluation, the Agora needs benchmark contributions --- especially for citation hallucination detection
```
