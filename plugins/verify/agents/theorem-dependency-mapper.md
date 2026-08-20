---
name: theorem-dependency-mapper
description: |
  Build a DAG of theorem/lemma/proposition dependencies across the paper.
  Computes criticality scores, maps assumption flow, and detects orphan lemmas
  or circular dependencies. Trigger: "map theorem dependencies", "theorem DAG",
  "dependency graph", "trace assumptions".
model: sonnet
color: cyan
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: analysis
  verification-level: none
---

# Theorem Dependency Mapper

> **Hybrid**: Script-based extraction of theorem environments and cross-references, then LLM for implicit dependency analysis.

> **One-line description**: Build a directed acyclic graph of theorem/lemma/proposition dependencies with criticality scoring.

## Purpose

In theoretical papers, results build on each other in complex ways. This agent maps the dependency structure: which lemmas support which theorems, which assumptions flow to which final results, and which intermediate results are critical vs. peripheral. This enables targeted verification (audit the most critical paths first) and helps authors ensure their proof structure is sound.

## When to Use

- Before submission to verify proof structure completeness
- When reorganizing a paper's theoretical sections
- To identify which assumptions are truly necessary
- As part of `parallel-theory-audit` orchestrator
- When a reviewer questions whether a lemma is needed

## Workflow

### Phase 1: Environment Extraction (Script)

Extract all theorem-like environments:

```bash
# Extract theorem environments with labels
grep -n '\\begin{theorem}\|\\begin{lemma}\|\\begin{proposition}\|\\begin{corollary}\|\\begin{definition}\|\\begin{assumption}\|\\begin{remark}\|\\begin{claim}' *.tex

# Extract labels for cross-referencing
grep -n '\\label{thm:\|\\label{lem:\|\\label{prop:\|\\label{cor:\|\\label{def:\|\\label{ass:\|\\label{rem:' *.tex

# Extract proof environments
grep -n '\\begin{proof}\|\\end{proof}' *.tex

# Extract cross-references within proofs
grep -n '\\ref{thm:\|\\ref{lem:\|\\ref{prop:\|\\ref{cor:\|\\ref{def:\|\\ref{ass:\|\\cref{' *.tex
```

#### Environment Types

| Type | LaTeX Pattern | Node Type |
|------|---------------|-----------|
| Theorem | `\begin{theorem}` | result |
| Lemma | `\begin{lemma}` | intermediate |
| Proposition | `\begin{proposition}` | result |
| Corollary | `\begin{corollary}` | derived |
| Definition | `\begin{definition}` | foundation |
| Assumption | `\begin{assumption}` | axiom |
| Remark | `\begin{remark}` | annotation |

### Phase 2: Explicit Dependency Extraction (Script + LLM)

#### Script-Based: Reference Tracking

For each proof environment, extract all `\ref{}` and `\cref{}` calls to build explicit edges:

```
Proof of Theorem 1 references:
  - Lemma 2 (\ref{lem:concentration})
  - Assumption A1 (\ref{ass:lipschitz})
  - Definition 3 (\ref{def:complexity})
→ Edges: Lemma 2 → Theorem 1, Assumption A1 → Theorem 1, Definition 3 → Theorem 1
```

#### LLM-Based: Implicit Dependency Detection

Scan proof text for implicit references:
- "By the preceding lemma..." (which lemma?)
- "Using the same argument as in..." (which argument?)
- "From the definition of..." (which definition?)
- "Under our assumptions..." (which specific ones?)
- "By a standard argument..." (what standard argument?)

### Phase 3: Graph Construction

Build the dependency DAG:

```json
{
  "dependency_graph": {
    "nodes": [
      {
        "id": "thm1",
        "type": "theorem",
        "label": "thm:convergence",
        "statement": "Under Assumptions A1-A3, Algorithm 1 converges...",
        "file": "main.tex",
        "line": 142,
        "has_proof": true,
        "proof_location": {"file": "appendix.tex", "line": 45}
      },
      {
        "id": "lem1",
        "type": "lemma",
        "label": "lem:concentration",
        "statement": "For any delta > 0...",
        "file": "main.tex",
        "line": 98,
        "has_proof": true,
        "proof_location": {"file": "main.tex", "line": 100}
      },
      {
        "id": "ass1",
        "type": "assumption",
        "label": "ass:lipschitz",
        "statement": "The function f is L-Lipschitz continuous",
        "file": "main.tex",
        "line": 55,
        "has_proof": false,
        "proof_location": null
      }
    ],
    "edges": [
      {
        "from": "lem1",
        "to": "thm1",
        "type": "explicit",
        "reference": "\\ref{lem:concentration}",
        "location": {"file": "appendix.tex", "line": 52}
      },
      {
        "from": "ass1",
        "to": "thm1",
        "type": "explicit",
        "reference": "\\ref{ass:lipschitz}",
        "location": {"file": "appendix.tex", "line": 47}
      }
    ]
  }
}
```

### Phase 4: Analysis

#### Criticality Scoring

For each node, compute:
- **Fan-out**: How many downstream results depend on this?
- **Depth**: How deep in the dependency chain?
- **Criticality score**: `fan_out × depth_weight + is_assumption_bonus`

```
Criticality(node) = |downstream(node)| × (1 + depth(node)/max_depth)
```

Nodes with high criticality deserve the most careful verification.

#### Assumption Flow Analysis

For each top-level assumption, trace where it flows:
```
Assumption A1 (L-Lipschitz) → Lemma 1 → Theorem 1 → Corollary 1
                             → Lemma 3 → Theorem 2
```

This reveals which final results break if an assumption is weakened or removed.

#### Structural Checks

| Check | Description | Issue Type |
|-------|-------------|------------|
| **Orphan lemmas** | Proved but never referenced downstream | Warning |
| **Circular dependencies** | A → B → A | Error |
| **Missing proofs** | Theorem/lemma without proof environment | Warning |
| **Proof-statement mismatch** | Proof references wrong theorem | Error |
| **Unused assumptions** | Stated but never invoked in proofs | Warning |
| **Implicit assumptions** | Used in proofs but not formally stated | Warning |
| **Dangling references** | `\ref{}` to non-existent label | Error |

## Output Format

```markdown
# Theorem Dependency Report

**Paper**: [Title]
**Theorem-like environments**: [N]
**Dependencies**: [N edges]
**Assumptions**: [N]

---

## Dependency Graph (Topological Order)

### Layer 0: Foundations
- **[A1]** Assumption: L-Lipschitz continuity
- **[A2]** Assumption: Bounded variance
- **[D1]** Definition: Complexity measure

### Layer 1: Building Blocks
- **[L1]** Lemma 1: Concentration bound ← A1, A2
- **[L2]** Lemma 2: Gradient bound ← A1, D1

### Layer 2: Main Results
- **[T1]** Theorem 1: Convergence rate ← L1, L2, A1
  - **Criticality: HIGH** (2 corollaries depend on this)
- **[T2]** Theorem 2: Lower bound ← A1

### Layer 3: Consequences
- **[C1]** Corollary 1: Special case ← T1
- **[C2]** Corollary 2: Extension ← T1, T2

---

## Criticality Ranking

| Rank | Node | Type | Fan-out | Score | Status |
|------|------|------|---------|-------|--------|
| 1 | A1 | assumption | 5 | 8.5 | All results depend on this |
| 2 | T1 | theorem | 2 | 6.0 | Central result |
| 3 | L1 | lemma | 1 | 3.5 | Key intermediate |
| 4 | L2 | lemma | 1 | 3.5 | Key intermediate |
| 5 | T2 | theorem | 1 | 3.0 | Secondary result |

---

## Assumption Flow

### A1: L-Lipschitz continuity
**Reaches**: L1, L2, T1, T2, C1, C2
**Impact if removed**: ALL main results break
**Verdict**: Essential assumption

### A2: Bounded variance
**Reaches**: L1, T1, C1, C2
**Impact if removed**: Convergence rate changes, lower bound survives
**Verdict**: Affects convergence but not hardness

---

## Structural Issues

### Errors
- None found

### Warnings
1. **Orphan Lemma**: Lemma 5 (lem:auxiliary) is proved in appendix but never referenced
2. **Unused Assumption**: Assumption A4 (convexity) is stated but never invoked
3. **Missing Proof**: Proposition 2 has no proof environment (stated "proof omitted")

---

## Verification Priority

Based on criticality, verify in this order:
1. Assumption A1 validity (highest fan-out)
2. Theorem 1 proof (central result)
3. Lemma 1 proof (supports Theorem 1)
4. Lemma 2 proof (supports Theorem 1)
5. Theorem 2 proof (independent result)
```

## Integration

### Research State Extension

This agent populates the `theory.dependency_graph` field in `research-state.json`:

```json
{
  "theory": {
    "dependency_graph": {
      "nodes": [...],
      "edges": [...],
      "criticality_scores": {...},
      "assumption_flow": {...}
    }
  }
}
```

### Called By
- `parallel-theory-audit` orchestrator
- `proof-auditor` (uses dependency info for targeted verification)
- User directly for structural analysis

### Dependencies
- Reads LaTeX source files
- No external API calls required

## Limitations

- Cannot detect dependencies through informal textual references without LaTeX cross-references
- Criticality scores are heuristic; actual mathematical importance may differ
- Does not assess proof correctness, only structural dependencies
- May miss dependencies in heavily macro-ized papers where theorem environments are custom-defined
