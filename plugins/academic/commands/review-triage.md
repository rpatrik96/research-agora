---
name: review-triage
description: Triage and prioritize revision work after receiving peer reviews. Decodes reviewer subtext and plans strategic responses. Use when asked to "triage reviews", "plan my revision", "revision strategy", "prioritize reviewer comments", "what should I fix first", "decode reviewer feedback", or "what do reviewers really mean". Step 1 of a 2-step pipeline (review-triage → reviewer-response-generator).
model: sonnet
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: analysis
  verification-level: heuristic
---

# Review Triage

> **LLM-required**: Categorizing reviewer intent, estimating revision effort, and resolving contradictions between reviewers requires judgment. No script alternative.

> **Pipeline Context**: This is step 1 of the rebuttal pipeline. Use `review-triage` (this skill) to plan, then `reviewer-response-generator` to write the actual rebuttal.

You got 4 reviews with 47 comments. Don't start fixing randomly. Triage first: what's critical, what's quick, what's out of scope, what's the optimal revision order? This skill decodes reviewer subtext, turns surface complaints into actionable fixes, and creates a structured revision plan with time estimates and dependencies.

## Workflow

1. **Parse all reviews** into individual, atomic comments
2. **Decode surface complaints** into underlying issues using the Reviewer Complaint Decoder
3. **Categorize each comment** along impact, effort, type, and section axes
4. **Identify quick wins**: high impact, low effort
5. **Identify critical blockers**: must fix for acceptance
6. **Identify out-of-scope requests**: politely decline in rebuttal
7. **Flag contradictions** between reviewers
8. **Build dependency graph**: what must be done before what
9. **Generate revision plan** with day-by-day schedule and time estimates

## Comment Parsing

Break each review into atomic comments. One reviewer paragraph often contains multiple distinct concerns:

```
Original: "The experiments are limited. Only two datasets are used and
the baselines seem outdated. Also, no ablation is provided for the
attention module."

Parsed as:
- R2.1: Only two datasets (Experimental, add data)
- R2.2: Outdated baselines (Experimental, update comparison)
- R2.3: No ablation for attention module (Experimental, add ablation)
```

Each parsed comment gets its own row in the triage matrix.

## Categorization Axes

### Impact
- **Blocks acceptance**: Reviewer explicitly or implicitly conditions acceptance on this
- **Strengthens paper**: Addressing this visibly improves the submission
- **Nice to have**: Marginal improvement, but addressing shows diligence
- **Out of scope**: Legitimate concern but beyond this paper's contribution

### Effort
- **Quick fix** (<30 min): Typo, add citation, clarify sentence, add definition
- **Moderate** (1-4 hours): Rewrite section, add figure, expand discussion
- **Significant** (1+ day): Run new experiment, add baseline, major restructure
- **Major rework** (3+ days): New theoretical analysis, large-scale experiment, fundamental reframing

### Type
- **Add experiment**: New baseline, dataset, ablation, or analysis
- **Add analysis**: Theoretical justification, failure mode discussion, sensitivity analysis
- **Rewrite section**: Restructure, clarify, or expand existing text
- **Fix error**: Correct a mistake in text, math, or results
- **Add reference**: Cite missing related work
- **Clarify text**: Minor rewording for clarity without restructuring

## Triage Quadrants

### Do First: High Impact + Low Effort (Quick Wins)
These create maximum positive impression per hour spent. Knock them out on day 1.

Examples:
- Adding a missing citation (10 min, shows responsiveness)
- Defining a term that confused reviewers (15 min, removes friction)
- Fixing a typo in an equation (5 min, removes "sloppy" impression)
- Adding one sentence of motivation (15 min, addresses "unclear why")

### Plan Carefully: High Impact + High Effort (Critical)
These determine acceptance. Plan them before starting. Allocate specific time blocks.

Examples:
- Running a missing baseline experiment (1-3 days)
- Adding an ablation study (0.5-2 days)
- Restructuring the methods section (4-8 hours)
- Adding theoretical analysis (1-3 days)

### Do If Time: Low Impact + Low Effort (Nice to Have)
Fill gaps in the revision with these. They signal thoroughness.

Examples:
- Improving figure aesthetics (1 hour)
- Expanding related work discussion (2 hours)
- Adding minor experimental analysis (2-4 hours)

### Decline Gracefully: Low Impact + High Effort (Out of Scope)
Not worth the time investment. Explain why in the rebuttal without being dismissive.

Examples:
- "Apply to NLP tasks" (when paper is about vision)
- "Compare to method X on dataset Y" (when neither is standard for your problem)
- "Provide convergence proof" (when paper is empirical)
- "Extend to the multi-agent setting" (when paper handles single-agent)

Rebuttal template for declining:
> "We thank the reviewer for this suggestion. Extending to [X] is an interesting direction that we discuss in Section 6 as future work. In this paper, we focus on [Y] because [reason]. We believe the current scope provides a complete contribution to [Z]."

## Output Format

```markdown
## Revision Triage

### Overview
- **Total comments parsed**: [N]
- **Critical (must fix)**: [N] comments
- **Quick wins**: [N] comments
- **Out of scope**: [N] comments
- **Estimated total effort**: [X hours/days]
- **Deadline**: [If provided]
- **Feasibility**: [All critical items achievable before deadline? Yes/No/At risk]

### Triage Matrix

#### Do First (Quick Wins) -- [Estimated: X hours]
| # | Comment Summary | Section | Effort | Action |
|---|----------------|---------|--------|--------|
| R1.3 | "Define X before using it" | 2.1 | 15 min | Add definition after Eq. 1 |
| R3.1 | "Cite Smith 2024" | Related Work | 10 min | Add citation in paragraph 3 |
| R2.4 | "Typo in Eq. 7" | 3.2 | 5 min | Fix subscript |

#### Plan Carefully (Critical) -- [Estimated: X days]
| # | Comment Summary | Section | Effort | Action |
|---|----------------|---------|--------|--------|
| R2.1 | "Add baseline Y" | 4 | 1.5 days | Run Y on all datasets, add to Tables 2-3 |
| R1.1 | "Ablation for attention" | 4.3 | 1 day | Run 3 ablation variants, add Table 5 |
| R3.3 | "Methods section confusing" | 3 | 4 hours | Restructure into 3.1 Overview, 3.2 Details |

#### Do If Time (Nice to Have) -- [Estimated: X hours]
| # | Comment Summary | Section | Effort | Action |
|---|----------------|---------|--------|--------|
| R1.5 | "Visualize attention maps" | 4 | 3 hours | Add Figure 5 with qualitative examples |

#### Decline Gracefully (Out of Scope)
| # | Comment Summary | Why Decline | Rebuttal Language |
|---|----------------|-------------|-------------------|
| R2.5 | "Extend to video" | Paper scope is images; video is future work | "Extending to video is interesting future work..." |

### Contradictions Between Reviewers
| Issue | R1 Says | R2 Says | Resolution |
|-------|---------|---------|------------|
| Paper length | "Too verbose" | "Needs more detail in Section 3" | Cut Section 2 background; expand Section 3 methods |
| Novelty | "Novel approach" | "Incremental" | R2 likely knows Smith 2024; add differentiation table |

### Revision Plan

**Day 1: Quick wins + experiment setup** [~5 hours active]
- [ ] All quick-win fixes (2 hours)
- [ ] Launch baseline Y experiments (30 min setup, runs overnight)
- [ ] Launch ablation experiments (30 min setup)
- [ ] Outline Section 3 restructure (1 hour)

**Day 2-3: Critical experiments** [~8 hours active]
- [ ] Collect baseline Y results, add to tables (2 hours)
- [ ] Collect ablation results, add Table 5 (2 hours)
- [ ] Rewrite Section 3 with new structure (4 hours)

**Day 4: Polish + nice-to-haves** [~6 hours]
- [ ] Add attention map visualizations (3 hours)
- [ ] Expand related work for R2's missing references (1 hour)
- [ ] Proofread all changes (2 hours)

**Day 5: Rebuttal draft** [~4 hours]
- [ ] Draft rebuttal using completed fixes as evidence
- [ ] Review rebuttal for tone and completeness
- [ ] Final consistency check across paper

### Dependencies
- Run baseline Y experiments BEFORE updating Tables 2-3
- Restructure Section 3 BEFORE polishing prose
- Complete all experiments BEFORE writing rebuttal (need results to cite)
- Fix notation issues BEFORE restructuring (avoid propagating errors)
```

## Handling Common Contradictions

### "Expand" vs. "Cut"
Different reviewers want different things from different sections. Parse carefully:
- R1 says "too long" -> which sections? Usually background/related work.
- R2 says "more detail needed" -> which sections? Usually methods/experiments.
- Resolution: Almost always cut background, expand methods. Both reviewers are right about different parts.

### "Novel" vs. "Incremental"
- The reviewer who says "incremental" knows a paper you didn't cite or differentiate from.
- Ask: what specific prior work makes this incremental? The answer reveals the fix.
- Resolution: Add explicit differentiation from the closest prior work. A comparison table works well.

### "Clear" vs. "Confusing"
- Different expertise levels. The confused reviewer reveals where non-experts lose the thread.
- Resolution: Add a high-level overview or intuitive explanation before technical details. Don't dumb down -- provide multiple entry points.

## Reviewer Complaint Decoder

The core translation table. Surface complaints map to underlying issues:

| Surface Complaint | Likely Underlying Issue | Strategic Fix |
|---|---|---|
| "Incremental" | Novelty not differentiated from prior work | Add comparison table showing the ONE key difference from closest prior work |
| "Limited novelty" | Positioning problem, not quality problem | Reframe contributions, cite the missing related work reviewer has in mind |
| "Unclear motivation" | Reader doesn't know why this problem matters | Add concrete real-world example in intro paragraph 1 |
| "Missing baselines" | Reviewer knows a specific method you didn't compare to | Ask: which specific baseline? Add it if feasible, explain omission if not |
| "Overclaimed" | Claims broader than evidence supports | Narrow claim language to match exact experiment scope |
| "Not convinced" | Missing ablation or analysis for a specific component | Add the specific ablation they're hinting at |
| "Writing needs improvement" | Structure problem disguised as prose complaint | Restructure sections before wordsmithing individual sentences |
| "Limited experiments" | Reviewer wants one specific experiment, not more experiments | Identify which ONE experiment would satisfy this reviewer |
| "Not sure this is the right venue" | Paper doesn't fit reviewer's mental model of the conference | Reframe positioning, strengthen connection to venue themes |
| "Lacks theoretical grounding" | Reviewer wants intuition for WHY the method works | Add analysis section: ablation + discussion of failure modes |
| "Hard to follow" | Too many ideas without clear hierarchy | Cut secondary contributions, strengthen main narrative arc |
| "Seems obvious" | Contribution not framed as surprising or non-trivial | Add "why this is harder than it looks" discussion |
| "Related work is incomplete" | Reviewer's own paper or their subfield is missing | Find the specific missing reference and add it prominently |

## Estimating Revision Time

### Common Underestimates
Researchers consistently underestimate these tasks:
- "Run one more experiment": 1-3 days (setup, debug, iterate, format results)
- "Rewrite Section X": 4-8 hours (restructuring is harder than writing fresh)
- "Add ablation": 1-2 days (designing meaningful ablations takes thought)
- "Address reviewer concern about Y": Variable. Decode the concern first.

### Common Overestimates
These are faster than expected:
- "Add a citation and discussion": 30 minutes
- "Fix notation": 1-2 hours (find-replace + consistency check)
- "Add error bars": 2-4 hours (if experiments are already scripted)
- "Improve figure quality": 1-3 hours (matplotlib style tweaks)

### Buffer Rule
Add 30% buffer to all time estimates. Revisions always surface secondary issues.

## Scope Boundaries

This skill **plans** the revision and **decodes** reviewer intent. It does not:
- Write the actual rebuttal document (use `reviewer-response-generator` for that)
- Review the paper to find additional issues (use `paper-review`)
- Execute the revision itself (use writing and experiment skills)

After completing triage, use `reviewer-response-generator` to draft the actual rebuttal responses.

## Output

Generate:
1. Complete triage matrix with all comments categorized
2. Contradiction analysis across reviewers
3. Day-by-day revision plan with time estimates
4. Dependency graph for revision tasks
5. Feasibility assessment against revision deadline