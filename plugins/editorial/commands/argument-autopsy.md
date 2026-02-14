---
name: argument-autopsy
description: Visualize the logical skeleton of a paper's argument as a claim-evidence DAG. Use when asked to "map my argument", "does my logic hold", "argument structure", "find logical gaps", or "why doesn't my paper flow". Flags missing links, orphan claims, circular reasoning, and unsupported assertions.
model: opus
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: diagnosis
  verification-level: layered
---

# Argument Autopsy

Visualize the logical skeleton of a paper's argument as a claim-evidence dependency graph. Surface invisible structural gaps that cause reviewer comments like "the argument doesn't flow" or "this claim is unsupported."

> **LLM-required**: Extracting implicit claims, mapping logical dependencies, and assessing evidence quality requires deep reading comprehension and domain judgment. No script alternative.

## Core Philosophy

"My advisor says it doesn't flow" is the most common complaint about paper drafts. The problem is that argument structure is invisible in prose. You can't fix what you can't see.

This skill makes the invisible visible. It extracts every claim (explicit and implicit), maps each one to its supporting evidence, and renders the result as a structured DAG. Once you SEE the gaps — the missing links, the orphan claims, the assertions masquerading as proven results — fixing them is straightforward.

The autopsy reads and analyzes. It never rewrites the paper.

## Workflow

1. **Read the full paper or section**: Read without judgment. Understand the intended argument before dissecting it.
2. **Extract all claims**: Both explicit ("We show that X") and implicit (claims embedded in framing or word choice). Number them C1, C2, ...
3. **Extract all evidence**: Data, citations, proofs, logical arguments, experimental results. Number them E1, E2, ...
4. **Map claim-evidence dependencies**: Which evidence supports which claim? Which claims depend on other claims?
5. **Grade evidence quality**: Assign L1-L6 levels to each piece of evidence.
6. **Identify gaps**: Missing links, orphans, circular dependencies, scope mismatches.
7. **Render the DAG**: Produce a structured visualization of the argument skeleton.
8. **Diagnose and recommend**: Prioritized list of fixes with estimated effort.

## Evidence Grading (L1-L6 Hierarchy)

Every piece of evidence gets graded on a six-level scale. Higher levels are stronger.

| Level | Name | Description | Example |
|-------|------|-------------|---------|
| **L1** | CODE_VERIFIED | Reproducible with provided code | "Run `train.py` to reproduce Table 1" |
| **L2** | REPRODUCIBLE_EXPERIMENT | Experimental result with full details | "Table 2 shows accuracy across 5 seeds" |
| **L3** | PAPER_EVIDENCE | Tables, figures, or proofs in the paper | "Figure 3 shows the ablation" |
| **L4** | CITATION_SUPPORT | Supported by cited prior work | "As shown by Smith et al. (2023)" |
| **L5** | LOGICAL_ARGUMENT | Supported by reasoning alone | "Since X implies Y, we expect Z" |
| **L6** | ASSERTION | No evidence provided | "Our method is more efficient" |

### When L6 Assertions Are Acceptable

Not every claim needs L1 evidence. The standard depends on the claim's role:

- **Motivation/context**: L5-L6 acceptable. "Deep learning models are increasingly deployed in safety-critical settings" doesn't need a citation in most papers.
- **Future work**: L6 acceptable. These are speculative by nature.
- **Core method claims**: L1-L3 required. "Our method achieves state-of-the-art" must have experimental evidence.
- **Theoretical claims**: L3 required (proof in paper) or L4 (proof in cited work).
- **Comparative claims**: L2-L3 required. "We outperform X" needs a direct comparison.

Flag L6 assertions on core claims. Leave L6 assertions in motivation alone.

## Gap Types

### Missing Link

**Definition**: Claim A depends on Claim B, but the logical connection is asserted rather than proven.

**Example**: "Our method converges (C3)" depends on "the loss landscape is convex (C2)", but no proof of convexity is provided.

**Severity**: Critical if the missing link is on the path from evidence to a main claim. Minor if it's in peripheral discussion.

**Fix**: Add the missing proof, experiment, or citation.

### Orphan Claim

**Definition**: A claim exists in the paper but nothing depends on it. It doesn't support any higher-level claim, and no conclusion references it.

**Example**: "We also note that our method can handle non-IID data distributions (C7)" — but the paper never evaluates on non-IID data and no conclusion mentions this capability.

**Severity**: Minor for isolated claims. Concerning if it suggests the author lost track of the argument.

**Fix**: Either connect it to the main argument or remove it. If it's important, add evidence and thread it into the contribution list.

### Orphan Evidence

**Definition**: Evidence is presented (a table, figure, or proof) but not connected to any claim. It exists without rhetorical purpose.

**Example**: Table 4 shows runtime comparisons, but no claim in the paper discusses computational efficiency.

**Severity**: Minor (wasted space) unless the evidence contradicts a claim (then it's a vulnerability).

**Fix**: Either make an explicit claim that the evidence supports, or move it to the appendix, or remove it.

### Circular Reasoning

**Definition**: Claim A depends on Claim B, which depends on Claim A. The argument is self-referential.

**Example**: "Our method works because the representations are disentangled (C2). The representations are disentangled because our method learns them correctly (C3)."

**Severity**: Critical. Circular reasoning invalidates the argument.

**Fix**: Break the cycle by grounding one of the claims in independent evidence.

### Evidence Downgrade

**Definition**: A critical claim (core contribution, main result) is supported only by L5-L6 evidence. The claim's importance demands stronger evidence than what is provided.

**Example**: Main contribution: "Our method generalizes to unseen domains (C1)." Evidence: "We expect generalization because the architecture is domain-agnostic (L5)."

**Severity**: Critical for core claims. Minor for secondary claims.

**Fix**: Add experimental evidence (L2-L3) or a formal proof (L3).

### Assumption Gap

**Definition**: A proof or argument relies on an unstated assumption. The assumption may be reasonable, but it's never made explicit.

**Example**: Convergence proof assumes bounded gradients, but the assumption is never stated.

**Severity**: Critical if the assumption is non-obvious or potentially violated. Minor if it's standard in the field.

**Fix**: State the assumption explicitly. Discuss whether it holds in practice.

### Scope Mismatch

**Definition**: The scope of the evidence doesn't match the scope of the claim. Results on MNIST, claims about "vision tasks." Results on English text, claims about "natural language."

**Example**: "Our method is effective for medical imaging (C1)" supported by "We evaluate on CIFAR-10 and ImageNet (E2)."

**Severity**: Critical. This is the most common source of "overclaiming" reviewer complaints.

**Fix**: Either narrow the claim to match the evidence scope, or add evidence at the claimed scope.

## Common Argument Patterns in ML Papers

### Standard Contribution Pattern

```
C0: Main thesis (this method advances the state of the art)
├── C1: Methodological contribution (we propose X)
│   └── E1: Method description (Section 3) [L3]
├── C2: Theoretical contribution (X has property Y)
│   └── E2: Proof (Theorem 1) [L3]
├── C3: Empirical contribution (X outperforms baselines)
│   ├── E3: Main results table [L2]
│   └── E4: Ablation study [L2]
└── C4: Practical contribution (X is efficient/usable)
    └── E5: Runtime comparison [L3]
```

### Theory Paper Pattern

```
C0: Main theorem
├── C1: Lemma 1
│   └── E1: Proof [L3]
├── C2: Lemma 2
│   ├── E2: Proof [L3]
│   └── C3: Intermediate result
│       └── E3: Proof [L3]
└── C4: Experiments validate theory
    └── E4: Synthetic experiments [L2]
```

### Empirical Paper Pattern

```
C0: Method X is state-of-the-art for task T
├── C1: X outperforms baselines on standard benchmarks
│   └── E1: Main results (Table 1) [L2]
├── C2: Each component of X is necessary
│   └── E2: Ablations (Table 2) [L2]
├── C3: X generalizes across settings
│   └── E3: Cross-dataset evaluation (Table 3) [L2]
└── C4: X is practically viable
    ├── E4: Runtime analysis [L3]
    └── E5: Qualitative examples (Figure 4) [L3]
```

## Output Format

```markdown
## Argument Autopsy

### Paper Structure
**Title**: [Paper title or section heading]
**Scope analyzed**: [Full paper / Section N / Introduction + Methods]

### Claim Inventory

| ID | Claim | Location | Type | Evidence | Grade |
|----|-------|----------|------|----------|-------|
| C1 | [Main claim text] | Abstract, S1 | Core | E1, E3 | L2 |
| C2 | [Sub-claim text] | S3.1 | Supporting | E2 | L3 |
| C3 | [Sub-claim text] | S3.2 | Supporting | -- | L6 |
| C4 | [Peripheral claim] | S5 | Peripheral | -- | L6 |

### Evidence Inventory

| ID | Evidence | Location | Type | Supports |
|----|----------|----------|------|----------|
| E1 | Table 1: Main results | S4.1 | Experiment | C1 |
| E2 | Theorem 1: Convergence | S3.2 | Proof | C2 |
| E3 | Figure 3: Ablation | S4.3 | Experiment | C1 |

### Claim-Evidence DAG

```
┌──────────────────────────────┐
│ C0: [Main thesis]            │
│ Evidence: L2 (E1, E3)        │ <── supported
└──────────┬───────────────────┘
           │ depends on
     ┌─────┴─────┐
     │           │
┌────▼────┐ ┌───▼─────────────┐
│ C1      │ │ C2              │
│ E1 [L2] │ │ E2 [L3]         │ <── supported
└─────────┘ └───┬─────────────┘
                │ depends on
           ┌────▼────────────┐
           │ C3              │
           │ Evidence: -- [L6]│ <── UNSUPPORTED
           └─────────────────┘
```

### Gap Analysis

| # | Gap Type | Claims | Location | Severity | Recommended Fix |
|---|----------|--------|----------|----------|-----------------|
| 1 | Evidence Downgrade | C3 | S3.2 | Critical | Add ablation or proof |
| 2 | Scope Mismatch | C1 vs E1 | S4.1 | Major | Narrow claim or add benchmarks |
| 3 | Orphan Claim | C4 | S5 | Minor | Connect to conclusion or remove |

### Diagnosis

[2-3 sentence summary of argument health. Is the argument structurally sound with minor gaps, or does it have critical missing links? What is the single most important thing to fix?]

### Recommended Fixes (Prioritized)

1. **[Most critical gap]**: [What to do] — Estimated effort: [low/medium/high]
2. **[Second gap]**: [What to do] — Estimated effort: [low/medium/high]
3. **[Third gap]**: [What to do] — Estimated effort: [low/medium/high]
```

## Analyzing Partial Drafts

When the paper is incomplete (e.g., methods written but experiments not yet done):

- Mark expected evidence as "Planned" rather than "Missing"
- Focus the gap analysis on the logical structure of what exists
- Flag claims that will need experimental support and specify what experiments would suffice
- This turns the autopsy into a planning tool: "here's what you need to run to close the gaps"

## Multi-Section Analysis

For full papers, analyze section by section and then synthesize:

1. **Introduction**: Extract promised contributions (these become the top-level claims)
2. **Methods**: Extract method claims and their theoretical backing
3. **Experiments**: Extract evidence and map to claims
4. **Discussion/Conclusion**: Check that all claims from the introduction are addressed

The most common gap: contributions promised in the introduction that are never demonstrated in experiments.

## Constraints

- **Read and analyze only.** This skill never rewrites the paper. It diagnoses structural issues and recommends fixes.
- **Distinguish explicit from implicit claims.** Implicit claims (embedded in word choice like "efficiently" or "robustly") still need evidence. Flag them.
- **Respect the author's argument.** The goal is to strengthen the argument the author is making, not to impose a different argument.
- **Be specific about locations.** Every gap must reference a section, paragraph, or sentence. "The argument has gaps" is not a diagnosis.
