# Evidence scales — the single definition

Two scales grade how well a claim is supported. **This file is the only place
they are defined.** A skill that grades evidence points here; it does not
restate the levels, because four copies of a scale drift and one former copy
graded a formal theorem with a complete proof as
`REPRODUCIBLE_EXPERIMENT`, which is not what that evidence is.

Enforced by `tests/test_registry.py::TestEvidenceScales`, which fails if a skill
redefines the levels inline.

---

## L1–L6 — empirical evidence

For claims about what a system *does*. L1 is strongest.

| Level | Label | What it means |
|---|---|---|
| **L1** | `CODE_VERIFIED` | Traceable to a specific implementation, with tests validating the claimed behaviour, reproducible from provided scripts |
| **L2** | `REPRODUCIBLE_EXPERIMENT` | Multiple seeds with error bars or confidence intervals, ablations isolating the contribution, significance tests |
| **L3** | `PAPER_EVIDENCE` | Results in the paper's own tables and figures. Single-seed results with no interval land here, not L2 |
| **L4** | `CITATION_SUPPORT` | Backed by a peer-reviewed publication, a standard practice, or an established benchmark |
| **L5** | `LOGICAL_ARGUMENT` | Informal reasoning, intuitive justification, analogy. "This makes sense because…" |
| **L6** | `AUTHOR_ASSERTION` | No support offered. "It is well known that…", "Clearly…", "Obviously…" |

**Downgrade rule.** Where code is available and an empirical claim has not been
checked against it, drop the claim one level. An unverified L1 is an L2.

## T1–T6 — theoretical evidence

For claims about what is *provable*. T1 is strongest. Theory does not fit the
L-scale: a complete proof is not an experiment, which is the mismatch that made
this scale necessary.

| Level | Label | What it means |
|---|---|---|
| **T1** | `FORMALLY_VERIFIED` | Proof checked by Lean, Coq or Isabelle |
| **T2** | `COMPLETE_PROOF` | Full proof, every step justified |
| **T3** | `PROOF_WITH_GAPS` | Proof present, with unjustified leaps |
| **T4** | `PROOF_SKETCH` | Strategy only; key steps omitted |
| **T5** | `INFORMAL_ARGUMENT` | Intuitive reasoning, no formal proof |
| **T6** | `THEOREM_ASSERTION` | Stated with no proof or argument |

**Which scale.** A claim about measured behaviour takes L1–L6. A claim about a
theorem, lemma or bound takes T1–T6. A paper claiming both gets both, reported
separately — never averaged into one number.

## Required levels by venue

The bar a claim must clear to be defensible at review.

| Venue tier | Empirical claims | Theoretical claims | Seeds |
|---|---|---|---|
| NeurIPS / ICML / ICLR | L1–L2 | T1–T2 | 3–5 minimum, with std or CI |
| CVPR / ACL / AAAI | L2–L3 | T2–T3 | 3 minimum |
| Workshop | L3–L4 | T3–T4 | 1, acknowledged as such |

A claim below its venue's bar is a finding, not a preference.

## Provenance

A level is a statement about the paper, so it must come from the paper. A level
inferred from what a model recalls about the field is a suggestion, and
`parallel-theory-audit`'s Phase 4.0 gate keeps that kind out of the score.
