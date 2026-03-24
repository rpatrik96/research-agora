# Technical Workflows

Prompts for R/econometrics, clinical/medical imaging setup, C++/TypeScript projects, and referee responses. Bring a real task. Measure the time saved.

---

## Who This Is For

If you write code in R, work with clinical or medical imaging data, maintain a compiled language codebase (C++, TypeScript), or regularly respond to reviewers — this file is for you. These prompts assume you're comfortable in a terminal and have a specific technical task in mind.

---

## Prerequisites

| Workflow | Requirements |
|----------|-------------|
| R econometrics | Claude Code + R installed; data file on disk |
| Medical/clinical setup | Claude Code; no patient data needed for setup step |
| C++/TypeScript project | Claude Code; project directory accessible |
| Referee response | Browser or CLI; reviewer comments available |

---

## Prompt 1: R Econometrics Workflow

**Use case:** You work with panel data in R and want a complete fixed-effects analysis — from data loading through regression, table output, and diagnostic checks — without writing boilerplate from scratch.

**Works in:** CLI (requires R and data file)

```
I am working with panel data in R.

Dataset: [describe your data — units (e.g., firms, individuals, countries), time periods, key variables and their types]
Research question: [state it in one sentence]
Outcome variable: [name]
Predictors: [names]

Please:
1. Write an R script that:
   a. Loads the data from [path/to/data.csv or .dta]
   b. Checks for panel balance (reports N units, T periods, any missing)
   c. Runs a two-way fixed-effects regression: outcome ~ predictors + unit FE + time FE
   d. Produces a regression table using modelsummary (preferred) or stargazer
   e. Runs a Hausman test comparing FE vs. random effects
2. Flag any common econometric issues: multicollinearity (VIF), heteroskedasticity (Breusch-Pagan), serial correlation (Wooldridge test)
3. Comment each step explaining what it does and why

Use tidyverse conventions throughout. Save the regression table as table1.html and table1.tex.
```

**Expected output:** A runnable R script with comments, a saved regression table in both formats, and diagnostic output.

**What to verify:**
- Run the script. Does it complete without errors?
- Is the panel structure correct? Verify N and T match your expectation from the data documentation.
- Check the Hausman test interpretation: if FE is preferred, is the script using FE throughout?
- Does the regression table match the model specification you intended?
- Are standard errors clustered appropriately for your research design?

**Related skills:** `statistical-validator` (research-agents@research-agora)

---

## Prompt 2: Medical Imaging / Clinical Workflow Setup

**Use case:** You work with MRI, CT, or other medical imaging data and want to set up a Claude Code workflow that keeps patient data isolated and never transmits identifiable information.

Run this *before* any real data is involved. The goal is architecture, not analysis.

**Works in:** CLI or browser

```
I work with medical imaging data ([MRI / CT / other]). I want to set up a Claude Code workflow for: [describe your task — e.g., preprocessing pipeline, segmentation QA, results summarization].

Before we touch any data:

1. What GDPR/data protection considerations apply to this specific workflow? List the key requirements.
2. Suggest a project directory structure that:
   - Keeps raw DICOM files outside the Claude Code working directory
   - Separates raw data, de-identified data, and outputs into distinct directories
   - Makes it structurally impossible for the agent to reach raw patient data
3. Draft a .claudeignore file that excludes all patient-identifiable paths
4. Outline the steps to de-identify DICOM data with pydicom before any AI processing, including which DICOM tags to strip
5. Write a CLAUDE.md section titled "Data Handling Rules" that any collaborator can follow

Output each section clearly labeled.
```

**Expected output:** A project structure recommendation, a `.claudeignore` file, a de-identification outline, and a `CLAUDE.md` data handling section.

**What to verify:**
- Does the proposed project structure physically isolate raw DICOM from the agent's working directory?
- Does the `.claudeignore` cover your actual data paths?
- Is the de-identification step using `pydicom` (or CTP) rather than `dcm2niix` (which is a format converter, not an anonymizer)?
- Before running any real data through this setup: review with your institution's Datenschutzbeauftragte(r).

**Related skills:** See [../privacy-gdpr.md](../privacy-gdpr.md) for full compliance guidance.

---

## Prompt 3: New Project Evaluation (C++ or TypeScript)

**Use case:** You want to evaluate whether Claude Code is worth adopting for your compiled-language project. Rather than a generic demo, this prompt runs a real task on your actual codebase and produces a concrete ROI assessment.

**Works in:** CLI (requires your project directory)

```
I want to evaluate whether Claude Code is worth adopting for my [C++ / TypeScript] project.

Project context:
- Codebase size: [approximate lines of code, number of files]
- Structure: [brief description — e.g., CMake build, single library + tests, or npm monorepo]
- Main language: [C++17 / TypeScript 5 / other]
- Test runner: [e.g., GoogleTest / jest / catch2]

Task 1 — Setup:
1. Create a CLAUDE.md tailored for this project. Include:
   - Build command (e.g., `cmake --build build/` or `npm run build`)
   - Test command (e.g., `ctest --test-dir build/` or `npm test`)
   - Coding conventions specific to this language
   - Any known gotchas (e.g., "always initialize CUDA context before allocating device memory")
2. Run `/init` to let Claude Code read the codebase and suggest additions to CLAUDE.md.

Task 2 — Real task:
[Describe a specific, scoped task: e.g., "Refactor the matrix multiplication kernel in src/ops/matmul.cu to use shared memory tiling" or "Add TypeScript types to the untyped API response objects in src/api/"]

After completing the task:
- How long did it take?
- What would this have taken without AI?
- What was the single biggest friction point?

Output: 3-bullet ROI assessment.
```

**Expected output:** A `CLAUDE.md`, completed task output, and a 3-bullet assessment.

**What to verify:**
- Does the build still pass after the task? Run it yourself.
- Does the test suite still pass? Check for regressions.
- Review the diff: does the agent's change match what you asked for?
- Is the CLAUDE.md accurate? Correct any wrong commands before committing.

**Related skills:** `commit` (development@research-agora), `pr-automation` (development@research-agora), `python-cicd` (development@research-agora)

---

## Prompt 4: Referee Response (Technical Paper)

**Use case:** You have reviewer comments on a paper with technical critiques — missing experiments, methodological concerns, or requests for clarification — and need a structured response that addresses each point specifically.

**Works in:** Browser or CLI

```
You are helping me write a response to reviewer comments on a technical paper.

Paper summary: [2–3 sentences: what problem you solve, your method, main result]
Venue: [journal or conference]

Reviewer comment:
"[Paste the exact reviewer comment here]"

Draft a response that:
1. Opens by acknowledging the validity of the concern (1 sentence)
2. States what we did to address it (specific, not vague — cite section, table, or experiment number)
3. If we ran new experiments: summarizes the result in 1–2 sentences
4. If the concern is a misunderstanding: corrects it clearly without condescension
5. Closes with what changed in the revision

Constraints:
- Under 200 words
- No phrases like "we appreciate the reviewer's insightful comment"
- No defensiveness
- Specific over general
```

**Expected output:** A response paragraph under 200 words, specific to the reviewer's concern.

**What to verify:**
- Does the response actually address the specific criticism, or does it deflect?
- Are any claims about new experiments or revisions accurate? (Don't promise experiments you haven't run.)
- Is the section/table/figure reference correct?
- Read it as the reviewer: is the concern actually resolved?

**Related skills:** `paper-rebuttal` (academic@research-agora), `reviewer-response-generator` (research-agents@research-agora)

---

## Further Reading

- [Cunningham — Claude Code for Causal Inference](https://causalinf.substack.com/p/claude-code-27-research-and-publishing): Economist automates a full empirical paper workflow with Claude Code.
- [Awesome Econ AI Stuff](https://meleantonio.github.io/awesome-econ-ai-stuff/): Stata/R/Python skills directory for economists.
- [Willison — Agentic Engineering Patterns](https://simonwillison.net/2026/Feb/23/agentic-engineering-patterns/): Practical patterns for reliable agent workflows — relevant for both C++ and clinical contexts.
- [Claude Code Data Usage (Official)](https://code.claude.com/docs/en/data-usage): Exactly what gets sent to the cloud — essential reading before clinical workflows.
