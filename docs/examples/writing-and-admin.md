# Writing & Admin

Prompts for email drafts, review rebuttals, teaching materials, and administrative documents. Everything here works in [Claude.ai](https://claude.ai) with zero installation.

---

## Who This Is For

If you want to reduce time spent on correspondence, rebuttal drafts, problem sets, or course materials — and you have no interest in installing anything — start here. Every prompt below works directly in a browser.

You don't need Claude Code for any of this. Open [Claude.ai](https://claude.ai), paste a prompt, iterate.

---

## Prerequisites

| What you need | Where to get it |
|--------------|----------------|
| Claude.ai account | [claude.ai](https://claude.ai) — free tier works for all prompts below |
| Your specific content | The email context, reviewer comments, or topic you're working with |

---

## Prompt 1: Administrative Email Draft

**Use case:** You need a professional academic email — to a collaborator, funder, journal editor, or administrator — and want a clean first draft you can edit rather than start from blank.

**Works in:** Browser

```
Draft a professional academic email on my behalf.

Context:
- I am a [role] at [institution]
- Recipient: [who they are and your relationship to them]
- Situation: [2–3 sentences describing what happened and what you need]
- Tone: [formal / direct / diplomatic / collegial]

Requirements:
- Maximum 150 words in the body
- No filler phrases ("I hope this email finds you well", "Please do not hesitate")
- One clear action item or request at the end
- Subject line suggestion at the top
```

**Expected output:** A subject line and email body, under 150 words, with a clear closing ask.

**What to verify:**
- Does it accurately represent your situation? The agent only knows what you told it — check that no assumptions crept in.
- Is the tone calibrated correctly for the relationship?
- Is the action item specific enough that the recipient knows exactly what to do?
- Edit before sending — treat this as a first draft, not a final product.

**Related skills:** `docx-create` (office@research-agora)

---

## Prompt 2: Review Rebuttal Paragraph

**Use case:** You're writing a rebuttal to peer reviewers and need a first draft for a specific concern — one that acknowledges the criticism without being defensive and points to evidence.

**Works in:** Browser

```
You are helping me write a rebuttal to a peer reviewer.

Context:
- Venue: [journal or conference name]
- Our paper: [1–2 sentence description of what it does and its main claim]
- Reviewer concern: "[paste the exact reviewer comment here]"

Draft a rebuttal paragraph that:
1. Acknowledges the concern without being defensive (start by partially conceding the framing)
2. Explains why our approach is sound despite the concern
3. Points to specific evidence in the paper (use placeholder like "[Section 3.2]" if needed)
4. Stays under 150 words

Tone: Professional and collegial. No dismissiveness.
```

**Expected output:** A single rebuttal paragraph, under 150 words.

**What to verify:**
- Does it actually address the reviewer's specific concern, or does it deflect?
- Is the evidence pointer plausible — i.e., does your paper actually contain what the draft claims?
- Does it start by partially conceding, or does it open defensively?
- Read it as the reviewer: would you find this response convincing?

**Related skills:** `paper-rebuttal` (academic@research-agora), `reviewer-response-generator` (research-agents@research-agora)

---

## Prompt 3: Teaching Material Generation

**Use case:** You need a problem set, rubric, or exam question for a graduate course. Generating a complete problem set from scratch takes an hour; structured prompting can produce a usable first draft in minutes.

**Works in:** Browser

```
I need a problem set on [topic] for graduate-level [field] students.

Generate:
1. A 1-paragraph learning objective using Bloom's taxonomy level: [Apply / Analyze / Evaluate / Create]
2. Three graded questions:
   - Q1: Conceptual (tests understanding of a key definition or principle)
   - Q2: Quantitative (requires calculation or formal derivation)
   - Q3: Applied (connects theory to a real dataset, system, or experiment)
3. A marking rubric for each question: 3–4 criteria with point allocations (total: [X] points per question)

Assumptions:
- Students have taken: [prerequisite course or list of concepts]
- Time available: [e.g., 90-minute exam / take-home over 1 week]
```

**Expected output:** Learning objective, three questions of increasing complexity, and three rubrics with explicit criteria.

**What to verify:**
- Is the difficulty calibrated correctly for your students' background?
- Does Q2 have a unique correct answer, or is it ambiguous?
- Are the rubric criteria specific enough that a TA could grade consistently, or are they vague?
- Read Q3 critically: is the "applied" scenario realistic, or does it require domain knowledge the students don't have?

**Related skills:** `docx-create` (office@research-agora), `pptx-create` (office@research-agora)

---

## Prompt 4: Group CLAUDE.md Setup

**Use case:** You want to roll out a shared AI context file for your research group so every student and postdoc gets consistent, project-aware responses — without calibrating the agent from scratch each session.

**Works in:** Browser (generates a file you copy into your project) or CLI (writes the file directly)

```
Help me create a CLAUDE.md file for my research group's main project repository.

Our group context:
- Field: [e.g., computational neuroscience, NLP, experimental economics]
- Main project: [1–2 sentence description]
- Primary language(s): [Python / R / MATLAB / other]
- Build/run commands: [e.g., `python train.py`, `latexmk -pdf main.tex`]
- Coding conventions: [e.g., type hints required, black formatting, tidyverse in R]
- Paper formatting: [e.g., ICLR 2026 style, use cleveref, booktabs]
- Quality standards: [e.g., all figures must be colorblind-safe, all citations verified]

Generate a CLAUDE.md that covers:
1. Project overview (2–3 sentences)
2. Key files and their purpose
3. Build and test commands
4. Coding and writing conventions
5. Common mistakes to avoid (I'll add to this as we discover them)
6. Verification requirements before considering any task complete
```

**Expected output:** A complete `CLAUDE.md` file ready to commit to your repository.

**What to verify:**
- Are the build commands correct for your actual project?
- Does it reflect your actual conventions, not generic best practices?
- Is anything missing that a new postdoc would need to know?
- After committing: have one team member run a task with this context and compare the output quality.

**Related skills:** None — `CLAUDE.md` is used by Claude Code directly; no skill needed.

---

## Further Reading

- [AI for Education Prompt Library](https://www.aiforeducation.io/prompt-library): 100+ prompts for teaching: rubrics, syllabi, assessments.
- [cv_rebuttal_template](https://github.com/guanyingc/cv_rebuttal_template): LaTeX rebuttal templates for conferences.
- [Korinek — AI for Economic Research (JEL 2023)](https://www.aeaweb.org/articles?id=10.1257/jel.20231736): Overview of AI workflows for researchers across disciplines.
- [Korinek — AI Agents for Research (NBER 2025)](https://www.nber.org/papers/w34202): Building research agents without programming.
