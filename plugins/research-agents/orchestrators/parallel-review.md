---
name: parallel-review
description: |
  Orchestrates comprehensive parallel paper review combining claim audit,
  clarity analysis, and structural feedback. Simulates multiple reviewer
  perspectives. Trigger: "parallel review", "full paper review".
model: opus
color: purple
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: verification
  verification-level: layered
  visibility: internal
---

# Orchestrator: Parallel Paper Review

> **LLM-required**: Orchestrating parallel reviews requires coordinating multiple analysis agents. No script alternative.

> **One-line description**: Coordinates a comprehensive multi-perspective paper review by parallelizing different review aspects.

## Purpose

This orchestrator provides a thorough paper review by parallelizing:
1. **Claim verification** (via parallel-audit)
2. **Clarity and writing quality** (via clarity-optimizer)
3. **Figure and table assessment**
4. **Audience alignment check**
5. **Structural completeness**

Simulates having multiple expert reviewers examine different aspects simultaneously.

## Orchestration Pattern

```
Phase 1: Setup (Sequential, ~3 min)
├── Load or generate research state
├── Identify review dimensions
├── Extract key sections for targeted review
└── Plan reviewer allocation

Phase 2: Fan-Out (Parallel, ~5-8 min)
├── Technical Review Track
│   ├── Spawn: parallel-audit (claims + evidence)
│   └── Spawn: assumption-surfacer (all sections)
├── Presentation Review Track
│   ├── Spawn: clarity-optimizer (per section)
│   └── Spawn: audience-checker (full paper)
├── Visual Review Track
│   └── Spawn: figure-storyteller assessor (per figure)
├── Novelty Review Track
│   └── Spawn: novelty-checker (main contributions)
└── Consistency Review Track
    └── Spawn: cross-referencer (full paper)

Phase 3: Fan-In (Sequential, ~3 min)
├── Aggregate all review feedback
├── Synthesize across dimensions
├── Identify cross-cutting issues
├── Prioritize feedback by impact
├── Generate structured review
└── Create revision checklist
```

## Input Specification

```json
{
  "type": "object",
  "required": ["paper_path"],
  "properties": {
    "paper_path": {
      "type": "string",
      "description": "Path to paper"
    },
    "venue_target": {
      "type": "string",
      "enum": ["neurips", "icml", "iclr", "aaai", "cvpr", "acl", "workshop", "arxiv"],
      "default": "neurips"
    },
    "review_focus": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["technical", "presentation", "novelty", "experiments", "clarity"]
      },
      "default": ["technical", "presentation", "novelty"],
      "description": "Which aspects to focus on"
    },
    "reviewer_personas": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["expert", "skeptic", "newcomer", "practitioner"]
      },
      "default": ["expert", "skeptic"],
      "description": "Reviewer perspectives to simulate"
    },
    "options": {
      "type": "object",
      "properties": {
        "include_minor_issues": {"type": "boolean", "default": false},
        "max_recommendations": {"type": "integer", "default": 20}
      }
    }
  }
}
```

## Reviewer Personas

### Expert Reviewer
- Focus: Technical correctness, novelty, significance
- Checks: Proofs, experimental rigor, baselines
- Tone: Direct, expects polish

### Skeptic Reviewer
- Focus: Weaknesses, limitations, overclaims
- Checks: Edge cases, failure modes, reproducibility
- Tone: Challenging, demands justification

### Newcomer Reviewer
- Focus: Clarity, accessibility, motivation
- Checks: Jargon, explanations, figures
- Tone: Questions assumptions

### Practitioner Reviewer
- Focus: Applicability, scalability, real-world impact
- Checks: Compute requirements, deployment, limitations
- Tone: Practical concerns

## Subagent Spawning

### Technical Review Track

```
SPAWN_SUBAGENT:
  skill: parallel-audit
  input:
    paper_path: {paper_path}
    venue_target: {venue_target}
  context:
    - Full research state
  timeout: 600s
  on_error: partial_results
```

### Clarity Review Track

```
SPAWN_SUBAGENT:
  skill: clarity-optimizer
  input:
    section_id: {section.id}
    section_text: {section.text}
    target_audience: {reviewer_persona}
  context:
    - Section text
    - Terminology glossary
  timeout: 60s
  on_error: skip
  # Spawn per section
```

### Audience Check Track

```
SPAWN_SUBAGENT:
  skill: audience-checker
  input:
    paper_content: {abstract + intro + conclusion}
    target_audiences: {reviewer_personas}
    venue_target: {venue_target}
  context:
    - Paper summary
  timeout: 120s
  on_error: skip
```

### Figure Assessment Track

```
SPAWN_SUBAGENT:
  skill: figure-storyteller
  input:
    figure_id: {figure.id}
    figure_caption: {figure.caption}
    context_section: {figure.section}
    mode: "assess"  # Not create
  context:
    - Figure metadata
    - Surrounding text
  timeout: 45s
  on_error: skip
  # Spawn per figure
```

## Result Merging

### Review Synthesis

```python
def synthesize_reviews(track_results, personas):
    """Synthesize multiple review tracks into unified feedback."""

    synthesis = {
        "technical": extract_technical_feedback(track_results["parallel-audit"]),
        "presentation": merge_clarity_feedback(track_results["clarity"]),
        "novelty": track_results.get("novelty", {}),
        "figures": merge_figure_feedback(track_results["figures"]),
        "consistency": track_results.get("cross-ref", {}),
        "audience_fit": track_results.get("audience", {})
    }

    # Cross-cutting analysis
    synthesis["cross_cutting"] = identify_cross_cutting_issues(synthesis)

    # Prioritize by impact on acceptance
    synthesis["priority_order"] = prioritize_feedback(synthesis, personas)

    return synthesis
```

### Feedback Prioritization

| Priority | Criteria | Example |
|----------|----------|---------|
| **Critical** | Blocks acceptance | Unsupported main claim, major error |
| **Major** | Significantly weakens paper | Missing baselines, unclear method |
| **Minor** | Nice to fix | Typos, minor clarity issues |
| **Suggestion** | Could improve | Additional experiments, better figures |

### Conflict Resolution

| Conflict Type | Resolution |
|---------------|------------|
| Expert vs Skeptic disagree | Include both perspectives, note disagreement |
| Technical vs clarity conflict | Prioritize technical, note clarity issue |
| Multiple clarity issues same section | Merge, deduplicate |

## Error Handling

| Error Type | Strategy |
|------------|----------|
| Parallel-audit fails | Fall back to sequential claim-auditor |
| Clarity analysis fails | Skip, note incomplete review |
| Figure assessment fails | Skip figures, note limitation |
| >30% subagents fail | Generate partial review with caveats |

## Output Format

```markdown
# Comprehensive Paper Review

**Paper**: [Title]
**Venue Target**: [venue]
**Review Mode**: Parallel Multi-Perspective
**Reviewer Personas**: [list]

---

## Overall Assessment

### Summary
[2-3 sentence summary of paper and overall impression]

### Recommendation
**[Strong Accept / Weak Accept / Borderline / Weak Reject / Strong Reject]**

### Confidence
[High / Medium / Low] - [brief justification]

---

## Strengths

1. **[Strength 1 Title]**
   [Description from relevant track]

2. **[Strength 2 Title]**
   [Description]

---

## Weaknesses

### Critical Issues

1. **[Issue Title]** (Technical / Presentation / Novelty)
   - **Problem**: [description]
   - **Evidence**: [from which subagent]
   - **Recommendation**: [specific action]

### Major Issues

1. **[Issue Title]**
   [details]

### Minor Issues

1. [issue]
2. [issue]

---

## Detailed Feedback by Aspect

### Technical Correctness
[Summary from parallel-audit]

| Claim | Status | Notes |
|-------|--------|-------|
| [claim] | [verified/weak/unsupported] | [brief note] |

### Novelty Assessment
[From novelty-checker results]

### Presentation Quality
[From clarity-optimizer results]

| Section | Clarity Score | Issues |
|---------|---------------|--------|
| Abstract | [score] | [issues] |
| Intro | [score] | [issues] |

### Figure Quality
[From figure-storyteller assessments]

| Figure | Assessment | Recommendation |
|--------|------------|----------------|
| Fig 1 | [good/needs work] | [suggestion] |

### Audience Alignment
[From audience-checker]

| Persona | Alignment | Concerns |
|---------|-----------|----------|
| Expert | [high/medium/low] | [concerns] |
| Newcomer | [high/medium/low] | [concerns] |

---

## Revision Checklist

### Before Resubmission (Critical)
- [ ] [Action item 1]
- [ ] [Action item 2]

### Strongly Recommended
- [ ] [Action item]

### Nice to Have
- [ ] [Action item]

---

## Reviewer Perspectives

### Expert Reviewer Says
> [Quote-style feedback from expert perspective]

### Skeptic Reviewer Says
> [Quote-style feedback from skeptic perspective]

---

*Generated by parallel-review orchestrator*
*Review tracks: technical, presentation, novelty, figures, consistency*
```

## Performance Expectations

| Phase | Estimated Time |
|-------|---------------|
| Setup | 3 min |
| Fan-Out (all tracks) | 5-8 min |
| Fan-In (synthesis) | 3 min |
| **Total** | **11-14 min** |

*Compare to manual review: 30-60 min*

## Integration Notes

### Called By
- User: "review my paper", "parallel review [path]"
- Pre-submission workflow

### Calls (Subagents)
- `parallel-audit` (orchestrator - for technical track)
- `clarity-optimizer` (per section)
- `audience-checker` (once)
- `figure-storyteller` (per figure, assess mode)
- `cross-referencer` (once)
- `assumption-surfacer` (via parallel-audit)

### State Updates
- Creates comprehensive review report
- Updates research-state.json with review feedback
- Generates revision checklist

## Comparison with Sequential Review

| Aspect | Sequential | Parallel |
|--------|------------|----------|
| Time | 30-60 min | 11-14 min |
| Perspectives | 1 | Multiple |
| Coverage | Varies | Systematic |
| Consistency | May miss | Cross-checked |
| Parallelizable | No | Yes |
