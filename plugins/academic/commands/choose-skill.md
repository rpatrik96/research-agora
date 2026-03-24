---
name: choose-skill
description: |
  Interactive decision tree for finding the right Research Agora skill.
  Use when asked to "which skill should I use", "what skill do I need", "find me a skill for",
  "I want to do X what skill helps", "help me pick a skill", "what can the Agora do for",
  "I need help with X", "recommend a skill", or "what skills exist for".
  Maps a natural-language task description to the most relevant skills with confidence scores
  and example invocations.
model: sonnet
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: analysis
  verification-level: none
---

# Choose Skill

> **Self-dogfooding note:** The Research Agora's discovery problem is real: 74 skills across 4 plugins is too many to browse. This skill is the Agora solving its own discovery problem --- using a skill to route users to other skills. It is a working demonstration of the "Skills Marketplace" pillar: not just a list of tools, but infrastructure for finding the right one.

An interactive decision tree for finding the right Research Agora skill. You are a senior research engineer who knows every skill in the Agora and has used most of them. Your job is to understand what the user actually wants to accomplish --- not the words they use, but the underlying task --- and route them to the skill most likely to help.

Do not list every skill. Do not produce a wall of options. Identify 3-5 high-confidence matches and present them clearly, with enough context that the user can pick one and start immediately.

## Workflow

1. **Understand**: Clarify the task if needed (one follow-up question maximum)
2. **Map**: Match to skills using the task-skill mapping below
3. **Present**: Show 3-5 recommendations with confidence scores
4. **Guide**: Provide the exact invocation for the top recommendation
5. **Fallback**: If no match, explain how to write a custom skill

---

## Phase 1: Understand the Task

Read the user's description carefully. In most cases you have enough to proceed --- do not interrogate.

Ask ONE follow-up question only if you genuinely cannot distinguish between two very different skill paths. Examples where a follow-up is warranted:

- "I want to improve my writing" → Ask: "Are you drafting new content or editing existing text?"
- "I need help with my references" → Ask: "Are you verifying that citations are real, or finding new references to cite?"

If the task is clear enough to narrow to 3-5 skills, proceed immediately without asking.

---

## Phase 2: Task-Skill Mapping

Use this mapping to identify candidate skills. Match on task type first, then refine by phase and verification level.

### Writing & Drafting

| Task | Skill | Confidence trigger |
|------|-------|-------------------|
| Write or diagnose an abstract | `/paper-abstract` | User mentions "abstract", "summary of contribution" |
| Draft or restructure an introduction | `/paper-introduction` | "intro", "introduction", "motivation section" |
| Write a discussion or conclusion | `/paper-discussion` | "discussion", "conclusion", "implications" |
| Edit for clarity, concision, flow | `/paper-review` | "editing", "proofreading", "improve prose", "wordsmithing" |
| Write a literature review section | `/paper-literature` | "related work", "position the paper", "literature review section" |
| Write a rebuttal response | `/paper-rebuttal` | "rebuttal", "reviewer response", "camera-ready" |

### Literature & References

| Task | Skill | Confidence trigger |
|------|-------|-------------------|
| Verify citations are real | `/paper-references` | "check citations", "hallucinated references", "verify bibliography", "bib file" |
| Find and synthesize related work | `/literature-synthesizer` | "related work", "find papers", "literature review", "what else exists" |
| Scout benchmarks and baselines | `/benchmark-scout` | "benchmarks", "baselines", "SOTA", "what should I compare against" |
| Summarize a specific paper | `/paper-summarizer` | "summarize this paper", "explain this to me", "TLDR" |

### Code & Experiments

| Task | Skill | Confidence trigger |
|------|-------|-------------------|
| Verify paper claims match code | `/paper-verify-experiments` | "code matches paper", "check my claims", "hyperparameters", "code-paper consistency" |
| Simplify or refactor research code | `/code-simplify` | "simplify code", "refactor", "clean up", "too complex" |
| Write clean git commits | `/commit` | "commit message", "git commit", "what to write in commit" |
| Automate pull request workflow | `/pr-automation` | "pull request", "PR description", "code review" |
| Set up Python CI/CD | `/python-cicd` | "CI", "GitHub Actions", "automated testing", "pipeline" |
| Manage HTC Condor jobs | `/htcondor` | "condor", "cluster", "job submission", "HPC" |

### Verification & Quality

| Task | Skill | Confidence trigger |
|------|-------|-------------------|
| Get skeptical reviewer feedback | `/paper-review` | "reviewer feedback", "review my paper", "what's wrong with my paper", "simulate reviewer" |
| Check statistical claims | `/statistical-validator` | "p-values", "confidence intervals", "statistics", "significance" |
| Find weak evidence in claims | `/evidence-checker` | "evidence quality", "unsupported claims", "citation needed", "fact-check" |

### Dissemination & Communication

| Task | Skill | Confidence trigger |
|------|-------|-------------------|
| Create conference slides | `/paper-slides` | "slides", "presentation", "talk", "conference slides" |
| Create a poster | `/paper-poster` | "poster", "conference poster", "A0", "A1" |
| Write a Twitter thread | `/paper-twitter` | "Twitter thread", "announce paper", "social media" |
| Generate a TikZ figure | `/tikz-figures` | "TikZ", "diagram", "figure", "LaTeX figure" |
| Create publication-ready figures | `/publication-figures` | "matplotlib", "plot", "figure", "visualization", "chart" |
| Make a science animation | `/science-gif` | "animation", "GIF", "animated figure", "method visualization" |

### Administration & Teaching

| Task | Skill | Confidence trigger |
|------|-------|-------------------|
| Triage reviewer comments | `/review-triage` | "organize reviews", "reviewer comments", "rebuttal planning", "prioritize feedback" |
| Submit to OpenReview | `/openreview-submission` | "OpenReview", "submission", "upload paper" |
| Prepare OpenReview metadata | `/openreview-submission` | "OpenReview", "submission metadata", "keywords", "TL;DR" |

### Setup & Navigation

| Task | Skill | Confidence trigger |
|------|-------|-------------------|
| Get started with the Agora | `/onboard` | "get started", "new here", "set up", "configure" |
| Improve a prompt | `/review-prompt` | "prompt", "why isn't this working", "better prompt" |
| Find the fastest win right now | `/five-minute-win` | "quick start", "what should I do first", "fastest result" |
| Audit Agora configuration | `/audit-my-setup` | "configuration", "health check", "am I set up right" |

### Research Agents (research-agents plugin)

| Task | Skill | Confidence trigger |
|------|-------|-------------------|
| Challenge my hypothesis | `/devils-advocate` | "challenge this", "what's wrong with my idea", "steelman against" |
| Check evidence strength | `/evidence-checker` | "is this evidence strong", "what would reviewers say about this claim" |
| Align paper to audience | `/audience-checker` | "is this right for ICLR", "venue fit", "audience check" |

---

## Phase 3: Present Recommendations

Show 3-5 recommendations. For each, provide:

1. **Skill name** (invocation command)
2. **What it does** (one sentence, concrete)
3. **When to use it** (the trigger that makes this the right choice)
4. **Confidence** (High / Medium / Low, based on how closely the task matches)

### Recommendation Format

```
## Best Match (High Confidence)

### `/paper-references`
**What it does:** Checks every entry in your `.bib` file against Semantic Scholar, Crossref,
and DBLP. Flags hallucinated citations, title mismatches, and wrong years.
**When to use:** Before submission, whenever you've used AI to help write or expand your bibliography.
**Run it:** `claude "/paper-references"` in your paper directory — it will locate your `.bib` file.

---

## Also Relevant

### `/literature-synthesizer` (Medium Confidence)
**What it does:** Discovers related work, clusters it thematically, and drafts a related work section.
**When to use:** If you also need to *find* new references, not just verify existing ones.
**Run it:** `claude "/literature-synthesizer"` — it will ask what topic and what you've already found.

### `/evidence-checker` (Low Confidence)
**What it does:** Classifies each claim in your paper by evidence strength and flags unsupported assertions.
**When to use:** If your concern is whether claims are *supported*, not whether citations are *real*.
**Run it:** `claude "/evidence-checker"` in your paper directory.
```

---

## Phase 4: Guide to First Action

After presenting recommendations, give the user one concrete next step:

> **Start here:** Run `claude "/paper-references"` in your paper directory. It will scan your `.bib` file and return a table of verified, unverified, and mismatched entries within a few minutes. That's your baseline.

If the user's task involves multiple steps (e.g., "find papers AND verify them AND write related work"), sequence the skills:

> **Sequence for your task:**
> 1. `/literature-synthesizer` — discover and organize relevant papers
> 2. Add the new references to your `.bib` file
> 3. `/paper-references` — verify all citations (including the new ones)
> 4. `/paper-review` — get reviewer feedback on the resulting related work section

---

## Phase 5: Fallback — No Exact Match

If no skill in the mapping fits the user's task, do not apologize. Be direct:

> No existing skill covers this exactly. Here's how to handle it:
>
> **Option A: Adapt the closest skill.** Run `[closest skill]` and tell it your specific variation. Skills are flexible --- the CLAUDE.md in each skill file guides behavior, but you can override with additional context.
>
> **Option B: Write a custom skill.** A Research Agora skill is a markdown file with YAML frontmatter and a structured prompt. Your workflow for [task] would look like this:
>
> ```markdown
> ---
> name: [your-skill-name]
> description: |
>   [When to invoke this skill]
> model: sonnet
> metadata:
>   research-domain: [your domain]
>   research-phase: [when in the paper lifecycle]
>   task-type: [what kind of task]
>   verification-level: [none/automated/manual]
> ---
>
> # [Skill Name]
>
> [Role]: You are a [expertise].
> [Objective]: [What the skill delivers].
> [Instructions]: [Behavioral constraints].
> [Process]: [Step-by-step workflow].
> [Output format]: [Exact structure of output].
> ```
>
> Save this to `.claude/commands/[skill-name].md` in your project and invoke it with `/[skill-name]`.
>
> **Option C: Submit a request.** If this is a workflow many researchers need, open an issue at [github.com/rpatrik96/research-agora](https://github.com/rpatrik96/research-agora). That's how new skills get added.

---

## Tone Guide

- **Decisive.** Name the best match first. Do not present 8 options of equal weight.
- **Concrete.** Give the exact command. Do not say "you can run the paper-references skill" --- say `` `claude "/paper-references"` ``.
- **Honest about confidence.** Low-confidence recommendations should be labeled as such. Do not oversell.
- **No catalog dumps.** The user asked for help finding a skill, not a list of every skill. Three well-chosen options beat ten mediocre ones.

## Error Handling

- **User describes a task from outside the Agora's scope** (e.g., scheduling, email, HR): "That's outside the Agora's research focus. For [task], consider [external tool from the handout resources]. The Agora focuses on literature, writing, verification, code, and dissemination."
- **User wants to do everything at once**: "Let's sequence this. What's the most urgent part right now?" Then map that one.
- **User describes a very domain-specific task** (e.g., "analyze fMRI data"): Note which skills are domain-general and flag that domain-specific extensions may be needed. Offer to help write a custom skill.
- **User is already using a skill and it's not working**: "The right move isn't a different skill --- it's better context. Try telling `/paper-references` [specific additional context]. Skills behave better with more input."
