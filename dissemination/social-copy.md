# Social Copy — Research Agora Launch

**Context**: Research Agora — 61 public AI skills across 6 plugins for ML research.
Site: rpatrik96.github.io/research-agora | GitHub: github.com/rpatrik96/research-agora
Position paper: "Skills, Benchmarks, and Verification Are What AI-Assisted Research Needs" @ P-AGI Workshop, ICLR 2026.

---

## Twitter/X

### Bio Options

**Option A** (tool-builder + breadth):
> Building AI research infrastructure. Research Agora: 61 open-source skills for paper writing, citation verification & adversarial review. PhD @UniTuebingen @ELLIS_network @MPI_IS.

**Option B** (credential-first):
> PhD researcher @UniTuebingen / @ELLIS_network / @MPI_IS. Built Research Agora — a verified AI skills marketplace for ML research. rpatrik96.github.io/research-agora

**Option C** (problem-first):
> AI-assisted research needs verification, not just generation. Building Research Agora: 61 skills, 2 benchmarks, MIT license. P-AGI@ICLR 2026. @UniTuebingen @ELLIS_network.

---

### Day-Two Quote Tweet

*(Quote-tweets Post 1 from the launch thread)*

> Ran /paper-references on a 47-entry .bib file.
>
> Caught 3 hallucinated citations that had passed two rounds of human review. One paper didn't exist. One had the wrong author list. One DOI resolved to a different paper entirely.
>
> This is what verification infrastructure looks like — not a chat assistant, a reproducible pipeline with a pass/fail signal.

---

### Week +1 Follow-Up Tweet

> CiteBench numbers after running against the validation set:
>
> /paper-references hits F1 0.908 on HALLMARK — the hallucination benchmark we shipped with the tool.
>
> What it catches: fabricated DOIs, wrong author lists, title drift, year mismatches.
> What it misses: paywalled sources it can't verify.
>
> Benchmark ships with the plugin. Run it yourself: github.com/rpatrik96/research-agora

---

## LinkedIn

### Headline Options

**Option A** (builder + venue):
> PhD Researcher @ University of Tübingen / ELLIS / MPI-IS | Building Research Agora: verified AI skills for ML research | P-AGI Workshop @ ICLR 2026

**Option B** (problem-solution):
> Building AI research infrastructure that verifies its own outputs | Research Agora: 61 open-source skills, 2 benchmarks | PhD @ Tübingen / ELLIS / MPI-IS | ICLR 2026

**Option C** (credential-led):
> PhD Researcher @ University of Tübingen / ELLIS / MPI-IS | Author, "Skills, Benchmarks, and Verification Are What AI-Assisted Research Needs" — P-AGI @ ICLR 2026

---

### About Section (First 3 Paragraphs)

Paragraph 1 — The problem:

ML researchers now use AI tools daily, but the workflows are ad hoc, unverified, and unreusable. A researcher prompts a model to check citations, gets plausible-sounding output, and has no way to know if the citations are real. The same researcher writes a prompt from scratch next week. There is no shared infrastructure, no reproducibility, and no accountability — just repeated improvisation at each step of the research process.

Paragraph 2 — The solution:

Research Agora is an open-source AI skills marketplace built for ML researchers. It ships 61 public skills across 6 plugins: academic writing (paper abstracts, introductions, discussions, rebuttals), citation management (hallucination detection via CrossRef / DBLP / Semantic Scholar / arXiv), adversarial review (skeptical reviewer simulation, claim auditing, proof verification), formatting (LaTeX diagnostics, slide and poster generation), office document workflows, and a research-agents layer of 22 autonomous agents coordinated by orchestrators. Every verification skill ships paired with a benchmark — CiteBench and HALLMARK — so you can measure what the skill actually catches before trusting it.

Paragraph 3 — The invitation:

Research Agora is MIT licensed and installs in one command. It runs cross-platform: Claude Code, Cursor, Gemini CLI, and GitHub Copilot, with a conversion tool for non-Claude platforms. The framework accompanies a position paper accepted to the P-AGI Workshop at ICLR 2026 arguing for test-driven AI research — define verification criteria before delegating to AI. Contributions are welcome.

rpatrik96.github.io/research-agora

---

### Pre-Launch Post 1 (Week -2): Citation Hallucination Problem

At NeurIPS 2025, 53 published papers contained hallucinated citations that passed peer review.

Not typos. Not formatting errors. Citations to papers that do not exist, or exist with different authors, different titles, or different conclusions than what was cited.

This is not a fringe problem. It is a structural one. When researchers use AI to assist with literature review, the model generates plausible-sounding references. Plausible is not the same as correct. And reviewers — under time pressure, reading 6 papers in a weekend — rarely verify every BibTeX entry against the original source.

The cost is not just one bad citation. It compounds. A hallucinated finding gets cited, then cited again. The error propagates faster than any correction can.

The fix is not "don't use AI." The fix is verification infrastructure — tools that check AI output against ground truth before it reaches a reviewer.

I've been building that infrastructure. More on this soon.

What's your experience with citation errors in submitted or published work?

---

### Pre-Launch Post 2 (Week -1): Evidence Hierarchy

One of the hardest problems in AI-assisted research is knowing how much to trust an output.

A model tells you a claim is supported by the literature. But what does that mean? It found a sentence that sounds related? It retrieved the actual paper and read the relevant section? It verified the experimental result against the data?

These are very different things, and treating them the same is how errors compound.

I've been developing a 6-level evidence hierarchy for research verification:

L1 CODE_VERIFIED — reproducible with actual code execution
L2 REPRODUCIBLE_EXPERIMENT — replicated with methodology documented
L3 PAPER_EVIDENCE — traceable to a specific table, figure, or equation
L4 CITATION_SUPPORT — backed by a verified, real citation
L5 LOGICAL_ARGUMENT — follows from stated premises
L6 ASSERTION — stated without evidence

Most AI outputs in research workflows sit at L5 or L6. The goal is not to eliminate AI assistance. The goal is to be honest about what level of evidence you actually have — and to push claims up the hierarchy before publishing.

I'll share the full framework next week.

---

### Pre-Launch Post 3 (3 Days Before): Teaser

Something I've been building for the past several months is almost ready.

61 skills. 2 benchmarks. A position paper at ICLR 2026.

All open source.

Comment "research" if you want a heads-up when it launches.

---

### Launch Post (Accompanies Carousel)

**Visual**: Use `branding/spiral-pure-og-image.png` (1200x630) or `branding/spiral-pure-mark-light.png` as the post image. The spiral logo has 6 color segments representing the plugin categories.

Most researchers use AI to write. Almost none use it with any form of verification.

That gap is the problem Research Agora was built to close.

Research Agora is an open-source AI skills marketplace: 61 skills across 6 plugins, designed specifically for ML research workflows. Not a chatbot. Not a prompt collection. A structured plugin system that installs in one command and runs inside the tools you already use.

Highlights:

- Citation verification that checks every BibTeX entry against CrossRef, DBLP, Semantic Scholar, and arXiv — catching hallucinated references before they reach a reviewer
- Adversarial review simulation: /paper-review runs a skeptical reviewer pass, /claim-auditor grades each claim on a 6-level evidence hierarchy, /devils-advocate surfaces the strongest counterarguments
- Full paper writing workflow: abstract, introduction, discussion, rebuttal, slides, poster — all as modular, reusable skills
- Cross-platform: Claude Code, Cursor, Gemini CLI, GitHub Copilot — one conversion tool handles all four

Every verification skill ships paired with a benchmark. CiteBench and HALLMARK let you measure what the tool catches before you trust it. That is what test-driven AI research looks like.

This accompanies a position paper accepted to the P-AGI Workshop at ICLR 2026: "Skills, Benchmarks, and Verification Are What AI-Assisted Research Needs."

Save this post. Link in first comment.

---

### First Comment (Under Launch Post)

Links:

GitHub (MIT license, full source): github.com/rpatrik96/research-agora

Quickstart guide (5 minutes to first skill): rpatrik96.github.io/research-agora/quickstart.html

Cross-platform setup (Cursor, Gemini CLI, Copilot): rpatrik96.github.io/research-agora/interop.html

ICLR 2026 position paper: [add arXiv link when available]

---

### Week +1 Benchmark Post

One week since launch. Sharing the benchmark numbers.

/paper-references — the citation hallucination detector — scores F1 0.908 on HALLMARK, the benchmark we ship alongside it.

What it catches reliably: fabricated DOIs, wrong author lists, title drift (paper exists but with a different title), year mismatches, and DOIs that resolve to a different paper than cited.

What it misses: paywalled sources it cannot retrieve, preprints not yet indexed by Semantic Scholar or arXiv, and cases where a real paper is cited but the specific claim attributed to it is not in the paper.

That last category — real citation, wrong claim — is the next thing to build. The benchmark flags it but the fix requires reading the full paper, not just verifying the metadata.

Benchmark is in the repo. Run it on your own .bib files and share results.

---

*File created: 2026-03-25. Companion file: dissemination/twitter-thread-launch.md*
