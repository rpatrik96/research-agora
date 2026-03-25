# Verification Guide — Test-Driven Research

This is the P0 guide for using Research Agora's verification capabilities. It covers the philosophy briefly, then gets to runnable recipes.

---

## 1. Why Verification Matters

At NeurIPS 2025, 53 accepted papers were found to contain fabricated citations — references that looked plausible but pointed to publications that do not exist. The AI that generated them expressed no uncertainty. It was confidently wrong.

This is the core asymmetry: AI systems produce fluent, authoritative-sounding outputs across a jagged frontier of actual competence. They excel at some tasks and fail unpredictably at similar ones, with no reliable signal about which is which. Citations either exist or they do not. Code either implements what the paper claims or it does not. Numbers either match or they diverge. For these correctness tasks, verification is mechanical and automatable — and the cost of skipping it is silent error embedded in the scientific record.

Your expertise is the oracle. The tools below help you apply it efficiently.

For the full argument, see the [position paper](https://openreview.net/forum?id=svFHXBd2wq) and [Research Agora platform design](../PLATFORM.md).

---

## 2. The Verification Hierarchy

Not all verification is equally tractable. Match the method to the task.

| Level | Method | When to Use | Example | Research Agora Skill |
|-------|--------|-------------|---------|----------------------|
| **Formal** | Automated check against ground truth | Citations, numerical claims, code correctness | DOI resolution, unit tests, `bibtexupdater` output | `/paper-references`, `/paper-verify-experiments`, `/statistical-validator` |
| **Automated** | Heuristic or rule-based check | Formatting, consistency, completeness | LaTeX compilation, reference count, grep for claimed values | `/latex-consistency`, grep scripts in `/paper-verify-experiments` |
| **Manual review** | Human expert reads output critically | Writing quality, argument structure, novelty claims | Read generated text; check that framing matches your intent | `/paper-review`, `/claim-auditor` (as input to your judgment) |
| **Trust** | Accept without checking | Never for research outputs | — | — |

The hierarchy is not a progression — it is a decision rule. Apply the highest-tractable level for each task type. Citations warrant formal checks. Novelty assessments do not have a formal oracle; manual review is the ceiling.

---

## 3. Runnable Verification Recipes

Each recipe follows a fixed format: what it checks, what you need, exact steps, what success looks like, what it does NOT cover, and an executable prompt you can run immediately.

---

### Recipe A: Citation Verification

**What it checks:** Whether each BibTeX entry in your `.bib` file corresponds to a real publication — correct title, authors, year, and venue — against Semantic Scholar, CrossRef, arXiv, and DBLP. Catches hallucinated references, stale preprints that were published, and author name errors.

**Prerequisites:**
- A `.bib` file (e.g., `references.bib`)
- `bibtex-updater` installed: `pip install bibtex-updater`
- Plugin: `academic@research-agora` (for `/paper-references`)

**Steps:**

1. Filter your `.bib` to only cited entries (avoids checking unused references):
   ```bash
   bibtexupdater-filter --bib references.bib --tex main.tex --output cited.bib
   ```

2. Run automated verification against scholarly databases:
   ```bash
   bibtexupdater --bib cited.bib --output verified.bib --report report.json
   ```

3. Review the report for flagged entries:
   ```bash
   cat report.json | python3 -c "import json,sys; [print(e) for e in json.load(sys.stdin)['issues']]"
   ```

4. For entries `bibtexupdater` cannot resolve (no DOI, preprint-only), invoke the `/paper-references` skill for LLM-assisted fallback:
   ```
   /paper-references
   ```
   Provide the flagged entries when prompted.

**Expected output:** A table with columns `cite_key | status | details` where status is `verified`, `updated` (preprint → published), `mismatch`, or `not_found`. Every `not_found` or `mismatch` entry requires action before submission.

**What this does NOT verify:** Whether the cited work actually supports the claim you are making. A paper can exist and still not be evidence for your sentence. That requires manual review.

**Try this now:**
```
/paper-references

I need to verify the citations in my paper. My .bib file is at references.bib and my main tex file is main.tex.

For each entry:
1. Check it exists (title, authors, year) against Semantic Scholar and CrossRef
2. Flag any entry where the publication cannot be confirmed
3. Identify preprints that have since been published (upgrade them)

Output: table with columns: cite_key | status (verified/mismatch/not_found/upgraded) | issue_detail | suggested_fix
```

---

### Recipe B: Code–Paper Consistency

**What it checks:** Whether the experimental claims in your paper match what your code actually does. Targets hyperparameters ("we train with learning rate 1e-4"), architectural choices ("a 3-layer MLP"), dataset sizes ("10,000 training samples"), and training procedures. Catches drift between the paper you wrote and the code you ran.

**Prerequisites:**
- Paper `.tex` files in a directory (e.g., `paper/`)
- Code repository accessible locally (e.g., `src/` or a cloned repo path)
- Plugin: `academic@research-agora` (for `/paper-verify-experiments`)

**Steps:**

1. Extract numerical claims from the paper (script-first):
   ```bash
   # Hyperparameters, dataset sizes, epoch counts, architecture specs
   grep -rn --include="*.tex" \
     -E "(learning.rate|batch.size|epoch|layer|hidden|dimension|training.sample|dataset)" \
     paper/ > claims_raw.txt
   ```

2. Extract actual values from code configs and source:
   ```bash
   # Config files (YAML/JSON)
   grep -rn --include="*.yaml" --include="*.json" --include="*.py" \
     -E "(lr|learning_rate|batch_size|num_epochs|hidden_size|num_layers)" \
     src/ > code_values.txt
   ```

3. Run `/paper-verify-experiments` to cross-reference and generate the discrepancy report:
   ```
   /paper-verify-experiments
   ```
   Provide both output files and the paper + code paths when prompted.

**Expected output:** A table with columns: `paper_claim (file:line) | code_evidence (file:line) | match | severity`. Severity levels: `critical` (wrong number reported), `warning` (ambiguous or indirect match), `info` (confirmed match).

**What this does NOT verify:** Whether the experimental design was appropriate for the research question, whether the reported results are cherry-picked from many runs, or whether the random seed was fixed. Those require your judgment and reproducibility practices (e.g., multiple seeds, ablations logged).

**Try this now:**
```
/paper-verify-experiments

Paper directory: paper/
Code repository: src/

Cross-reference all claims about:
- Hyperparameters (learning rate, batch size, optimizer, scheduler)
- Architecture (number of layers, hidden dimensions, activation functions)
- Dataset (size, splits, preprocessing steps)
- Training procedure (number of epochs, early stopping, augmentation)

For each claim: quote the paper sentence, find the corresponding code location, classify as match/mismatch/unverifiable.
Output: table sorted by severity (critical mismatches first).
```

---

### Recipe C: Statistical Validation

**What it checks:** Internal consistency of reported statistics — whether p-values, confidence intervals, effect sizes, and significance claims are mutually consistent and correctly interpreted. Flags cases where p < 0.05 is claimed but the confidence interval crosses zero, underpowered tests given the reported effect size, and standard errors reported as standard deviations (or vice versa).

**Prerequisites:**
- Paper `.tex` or `.pdf` with statistical results reported
- Plugin: `research-agents@research-agora` (for `/statistical-validator` agent)

**Steps:**

1. Invoke the statistical validator agent:
   ```
   /statistical-validator
   ```

2. Provide the paper section(s) containing statistical results — the methods section and any tables or figures with p-values, CIs, or effect sizes.

3. Review the output, which classifies each finding as:
   - `consistent` — values are internally coherent
   - `inconsistent` — values contradict each other (e.g., CI crosses zero but p < 0.05 claimed)
   - `underpowered` — sample size insufficient for claimed effect
   - `unclear` — insufficient information reported to verify

**Expected output:** Per-claim assessment table plus a summary of issues requiring correction. Critical inconsistencies must be resolved before submission; `underpowered` flags warrant a power analysis or hedged language.

**What this does NOT verify:** Whether the statistical test chosen was appropriate for your data distribution, whether the assumptions of the test (normality, independence) hold, or whether the reported metric (e.g., accuracy vs. F1) is the right one for your problem. That requires domain judgment.

**Try this now:**
```
/statistical-validator

Check the statistical claims in the attached paper section for internal consistency.

For each reported statistic:
1. Identify the claim (p-value, CI, effect size, sample size)
2. Check internal consistency (e.g., CI should exclude null if p < alpha)
3. Flag underpowered tests: estimate required n for reported effect size at 80% power
4. Flag ambiguous reporting (SEM vs SD, one-tailed vs two-tailed not stated)

Output: table with columns: location | statistic | value | status | issue
Severity: critical (inconsistent) / warning (underpowered or ambiguous) / info (consistent)
```

---

### Recipe D: Claim Auditing

**What it checks:** For each substantive claim in your paper, whether the evidence cited actually supports that claim. Classifies claims as: `supported` (cited evidence directly supports it), `partially-supported` (weak or indirect evidence), `unsupported` (no evidence cited), or `contradicted` (cited evidence argues against the claim). This catches the gap between what you wrote and what your citations actually say.

**Prerequisites:**
- Paper `.tex` files
- Plugin: `research-agents@research-agora` (for `/claim-auditor` agent)

**Steps:**

1. Run the claim auditor:
   ```
   /claim-auditor
   ```
   For a full paper, use parallel mode for a 2–3x speedup when prompted.

2. Provide the paper content. The agent will extract claims, locate cited evidence, and classify each.

3. For `unsupported` or `contradicted` claims: decide whether to add evidence, weaken the claim, or remove it.

**Expected output:** A structured report with each claim, its evidence classification, and suggested fixes. `contradicted` claims require immediate attention. `unsupported` claims either need a citation or need to be qualified ("we conjecture that..." vs. "it is well established that...").

**What this does NOT verify:** Whether the cited papers themselves are correct (science can be wrong), whether your claims are novel (novelty requires knowing the full literature), or whether the framing is fair to related work. Those are judgment calls the auditor surfaces for you to make.

**Try this now:**
```
/claim-auditor

Audit all substantive claims in this paper. For each claim:
1. Identify the exact sentence making the claim
2. Find the citation(s) used as evidence (if any)
3. Classify: supported / partially-supported / unsupported / contradicted
4. For unsupported: note whether the claim should be qualified or needs a citation
5. For contradicted: quote the conflicting source

Focus on: contributions section, related work comparisons, experimental result interpretations.
Output: table sorted by severity (contradicted → unsupported → partially-supported → supported).
```

---

## 4. The Quick Verification Checklist

Before accepting any AI output into your research, run through these five questions. This is a pre-commit check, not a post-hoc rationalization.

*(Adapted from [Simon Willison's NICAR 2026 workshop](https://simonwillison.net/2026/Mar/16/coding-agents-for-data-analysis/))*

- [ ] **Is it correct?** Run it yourself. Don't trust the agent's claim that it works — verify the output directly against ground truth.
- [ ] **Is the interpretation right?** Does the agent understand your domain concepts, your notation, your column meanings? AI reads surface patterns; it may miss what the numbers mean in context.
- [ ] **Is it actually novel?** Or is this restating something obvious, or something you already said three paragraphs earlier?
- [ ] **Could it be an artifact?** Of the data collection? Of how you phrased the prompt? Of the model's training distribution?
- [ ] **Does it open a door or close one?** The best findings raise new questions. If the output seems to neatly resolve everything, be skeptical.

This checklist applies whether the output is a generated paragraph, a literature summary, a code snippet, or a statistical result. The same critical eye you apply to peer review applies here.

---

## 5. Where Verification Breaks Down

Verification works for correctness. Research is not only correctness.

| Task type | Automatable? | What to do |
|-----------|-------------|------------|
| Citations (exist, title/author match) | Yes — formal check | Use `/paper-references` + `bibtexupdater`. Delegate freely. |
| Numerical claims (hyperparams, dataset sizes) | Yes — grep + cross-reference | Use `/paper-verify-experiments`. Delegate generation; verify output. |
| Statistical internal consistency | Yes — rule-based | Use `/statistical-validator`. Flag inconsistencies before submission. |
| Code correctness (unit behavior) | Yes — tests | Write tests. Run them. CI enforces this. |
| Consistency (paper ↔ code, claims ↔ data) | Partially — heuristics | Delegate generation; review mismatches manually. |
| Interpretation of results | No | Use AI to *generate competing interpretations* for you to evaluate. Do not delegate the judgment. |
| Novelty of contribution | No | No automated oracle exists. You need to know the literature. |
| Fairness of framing (related work) | No | `/claim-auditor` surfaces unsupported comparisons; you decide what's fair. |
| Problem importance | No | This is taste. It develops through doing research, not through delegation. |

The boundary is explicit: TDR solves correctness problems. It does not solve epistemological problems.

For interpretation, "manual review" means you thinking — not a verification shortcut. AI can generate three competing explanations of your experimental results. Only you can judge which one is scientifically sound given what you know about the system you studied.

Your judgment is the only oracle for the things that matter most.

---

## 6. Verification for Different Roles

<details>
<summary><strong>PI: Encoding verification policy across the lab</strong></summary>

The highest-leverage action is encoding verification requirements in your shared `CLAUDE.md` so every lab member runs the same checks automatically.

Add a verification section to your project's `CLAUDE.md`:

```markdown
## Verification Policy

Before any paper submission:
1. Run `bibtexupdater-filter` + `bibtexupdater` on the .bib file. Zero `not_found` entries required.
2. Run `/paper-verify-experiments` on the final paper + code. All critical mismatches resolved.
3. Run `/statistical-validator` on any section with p-values or CIs. Zero `inconsistent` flags.

For AI-generated sections:
- Run the Quick Verification Checklist (docs/verification.md) before committing.
- No AI-generated citation added without `bibtexupdater` confirmation it exists.
```

This transforms verification from a personal habit into a lab-wide protocol. Claude Code reads `CLAUDE.md` at session start — policy is enforced automatically.

For reproducibility, also consider adding `paper-verify-experiments` as a CI step. The grep-based claim extraction runs without LLM cost and catches the most common drift (hyperparameter changes post-writing).

</details>

<details>
<summary><strong>Postdoc / Researcher: A daily verification workflow</strong></summary>

Verification does not require running all four recipes every day. Match the check to the stage:

**During writing (any session that touches the paper):**
- After adding references: run `bibtexupdater` on new entries. 30 seconds per entry.
- After describing an experiment: run the code–paper grep check on the changed section.

**Before sending to co-authors:**
- Run `/claim-auditor` on any new section. Fix `unsupported` claims before review.
- Run the Quick Verification Checklist on any AI-generated paragraphs.

**Before submission:**
- Full citation verification (Recipe A) — required.
- Full code–paper consistency (Recipe B) — required if code is part of the contribution.
- Statistical validation (Recipe C) — required if you report p-values, CIs, or significance.
- Claim audit (Recipe D) — run on abstract, contributions, and comparison to related work.

Front-load verification. Catching a fabricated citation before submission costs 5 minutes. Catching it in a post-publication correction notice costs much more.

</details>

<details>
<summary><strong>Student: Building verification habits early</strong></summary>

The single most important habit: never copy a citation from AI output into your `.bib` without running `bibtexupdater` on it first. Citations are the one category where the cost of a miss is symmetric — the error is visible, permanent, and attached to your name.

Start with Recipe A. Run it every time you add references. Once this is automatic, add Recipe D (claim auditing) to your pre-advisor-meeting checklist.

On the epistemological side: AI is good at pattern-matching what results *usually mean* in a field. It is bad at knowing what your specific results mean in your specific experimental context. When the AI interprets your experimental output and the interpretation sounds authoritative, that is exactly when you should be most skeptical. Use the competing-interpretations pattern:

```
Generate three different interpretations of this result, ranging from the most conservative
(it could be an artifact) to the most ambitious (it implies something novel).
List what evidence would distinguish between them.
```

Then you evaluate which one is scientifically sound. That judgment is not delegatable — and developing it is the point of doing research.

</details>

---

## See Also

- [`/paper-references`](../plugins/academic/commands/paper-references.md) — full skill documentation
- [`/paper-verify-experiments`](../plugins/academic/commands/paper-verify-experiments.md) — full skill documentation
- [`/statistical-validator`](../plugins/research-agents/agents/statistical-validator.md) — agent documentation
- [`/claim-auditor`](../plugins/research-agents/agents/claim-auditor.md) — agent documentation, including parallel mode
- [Evidence Hierarchy](../CLAUDE.md#evidence-hierarchy) — L1–L6 claim grading used internally by research-agents
- [Position paper](https://openreview.net/forum?id=svFHXBd2wq) — full argument for Test-Driven Research and the Research Agora
