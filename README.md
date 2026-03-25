# Research Agora

[![Tests](https://github.com/rpatrik96/research-agora/actions/workflows/tests.yml/badge.svg)](https://github.com/rpatrik96/research-agora/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-74-blue.svg)](https://rpatrik96.github.io/research-agora)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

A community-driven skills marketplace for AI-assisted research. Browse, install, and share modular AI workflows for ML research.

<p align="center">
  <img src="dissemination/research-agora-demo.gif" alt="Research Agora Demo" width="700">
</p>

**[Browse Skills](https://rpatrik96.github.io/research-agora)** | **[Platform Design](PLATFORM.md)** | **[Contributing](CONTRIBUTING.md)**

## Getting Started

**Reading time:** PI: 5 min | Researcher: 15 min | Student: 10 min

### Install

```bash
npm install -g @anthropic-ai/claude-code    # if you don't have Claude Code yet
```

```
/plugin marketplace add rpatrik96/research-agora
/plugin install academic@research-agora
/plugin install development@research-agora
/plugin install formatting@research-agora
/plugin install research-agents@research-agora
```

> **New here?** Run `/onboard` — it asks a few questions about your work and generates a personalized setup with recommended skills.

### Your First 5 Minutes

Run citation verification on any project with a `.bib` file:

```bash
cd /path/to/your/project && claude
/paper-references
```

Every entry marked `mismatch` or `not found` is a potential hallucinated or corrupted reference. **Cost: ~$0.10–0.30.**

No `.bib` file? No CLI? See the [full quickstart](docs/quickstart.md) for browser-only paths.

### Choose Your Path

<details>
<summary><strong>PI: Evaluate and deploy for your group</strong></summary>

74 reusable AI workflows for the full paper lifecycle. Skills encode your group's standards in a shared `CLAUDE.md` — every student and postdoc runs the same verified checks.

- **Cost:** $20/mo Pro + ~$5–80/mo API tokens depending on usage. Team plan ($30/seat) adds GDPR DPA.
- **Privacy:** No patient data or unpublished results on Pro. Team plan required for institutional compliance. [Full guide →](docs/privacy-gdpr.md)
- **Rollout:** (1) Pilot one high-pain task, (2) Create shared `CLAUDE.md`, (3) Set verification standards, (4) Review monthly.
- Skills are plain Markdown — they transfer across providers. No lock-in.

**Start with:** [Quickstart](docs/quickstart.md) → [Verification guide](docs/verification.md) → [CLAUDE.md template](templates/CLAUDE.md.researcher)

</details>

<details>
<summary><strong>Researcher: Get productive today</strong></summary>

| I want to... | Run this |
|-------------|---------|
| Verify citations | `/paper-references` |
| Critical review of my draft | `/paper-review path/to/paper.pdf` |
| Write a rebuttal | `/paper-rebuttal` |
| Find related work | `/literature-synthesizer` |
| Publication-ready figures | `/publication-figures` |
| Debug LaTeX | `/latex-debugger` |
| Clean up code | `/code-simplify` |

**Not sure which skill?** Run `/choose-skill` — describe your task and get matched recommendations.

**Start with:** [Quickstart](docs/quickstart.md) → [Examples by domain](docs/examples/) → [CLAUDE.md template](templates/CLAUDE.md.researcher)

</details>

<details>
<summary><strong>Student: Learn by doing</strong></summary>

AI tools amplify expertise — they don't replace it. Verify everything. Build understanding before optimizing speed.

**Week 1:** Run `/paper-references` on your bibliography. Check 3 entries manually.
**Week 2:** Set up `CLAUDE.md` for your project with `/onboard`.
**Week 3:** Try `/paper-review` on a section draft. Do you agree with the critique?
**Week 4:** Connect GitHub MCP, try `/pr-automation`.

**Rule of thumb:** If you couldn't do the task without AI, the AI shouldn't do it for you yet.

**Start with:** [Concepts](docs/concepts.md) → [Examples](docs/examples/) → [Verification guide](docs/verification.md)

</details>

### Documentation

| Doc | What it covers |
|-----|---------------|
| [Quickstart](docs/quickstart.md) | Install → first task → 5-minute win |
| [Concepts](docs/concepts.md) | Evolution stack, key terms, delegate vs. protect |
| [Verification](docs/verification.md) | TDR recipes, hierarchy, limits |
| [Privacy & GDPR](docs/privacy-gdpr.md) | Compliance checklist, paid plans, medical data |
| [Examples](docs/examples/) | Domain-specific prompts by use case |
| [CLAUDE.md Template](templates/CLAUDE.md.researcher) | Commented template — customizing it IS the tutorial |

---

## Available Plugins

### academic@research-agora

Paper writing, research, and dissemination skills:

| Skill | Description |
|-------|-------------|
| `paper-introduction` | Write introduction sections for ML papers |
| `paper-abstract` | Write or improve paper abstracts |
| `literature-synthesizer` | Write related work and discover relevant literature |
| `paper-experiments` | Document experimental setups with GitHub integration |
| `paper-discussion` | Write discussion and limitations sections |
| `paper-review` | Generate critical reviews simulating skeptical reviewers |
| `paper-rebuttal` | Write rebuttals to reviewer comments |
| `paper-references` | Fact-check citations using bibtexupdater |
| `paper-verify-experiments` | Verify claims against source code |
| `paper-poster` | Create academic conference posters |
| `paper-slides` | Create presentation slides from papers |
| `paper-twitter` | Create Twitter threads to announce research |
| `paper-title` | Brainstorm compelling paper titles |
| `experiment-tracker` | Sync experiment results to paper drafts |
| `benchmark-scout` | Find benchmarks and generate experiment plans |
| `openreview-submission` | Prepare OpenReview metadata: plain-text abstract, keywords, TL;DR, lay summary |

### development@research-agora

Code quality and automation skills:

| Skill | Description |
|-------|-------------|
| `commit` | Create conventional commits with co-authorship |
| `code-simplify` | Remove dead code, eliminate duplication |
| `pr-automation` | Create GitHub pull requests from changes |
| `python-docs` | Generate NumPy-style docstrings |
| `python-cicd` | Set up CI/CD with GitHub Actions |
| `htcondor` | Generate HTCondor submission files for cluster jobs |
| `latex-sync-setup` | Initialize latex-code-sync in a project |
| `latex-sync-annotate` | Link functions to paper equations via decorators |
| `latex-sync-verify` | Verify paper equations match code implementations |

### formatting@research-agora

Document and code formatting skills:

| Skill | Description |
|-------|-------------|
| `latex-consistency` | Enforce consistent LaTeX formatting |
| `publication-figures` | Create publication-ready matplotlib figures |
| `tikz-figures` | Create TikZ/PGF diagrams for ML papers |

### office@research-agora

Microsoft Office document creation:

| Skill | Description |
|-------|-------------|
| `pptx-create` | Create PowerPoint presentations |
| `docx-create` | Create Word documents |
| `xlsx-create` | Create Excel spreadsheets |

### research-agents@research-agora

Specialized research analysis agents:

| Agent | Description |
|-------|-------------|
| `devils-advocate` | Challenge arguments and identify biases |
| `evidence-checker` | Verify evidence quality for claims |
| `perspective-synthesizer` | Synthesize multiple viewpoints |
| `audience-checker` | Evaluate audience alignment |
| `claim-auditor` | Deep verify all paper claims |
| `clarity-optimizer` | Analyze readability and reduce jargon |
| `statistical-validator` | Verify statistical rigor |
| `figure-storyteller` | Generate publication-quality figures |
| `reviewer-response-generator` | Generate structured rebuttals |
| `latex-debugger` | Parse logs and diagnose compilation errors |
| `artifact-packager` | Prepare code/data for public release |
| `co-author-sync` | Multi-author coordination |
| `discussion-monitor` | Track citations and social mentions |
| `state-generator` | Generate research-state.json for parallel analysis pipelines |
| `proof-auditor` | Decompose and verify proofs step-by-step (T1-T6 hierarchy) |
| `bounds-analyst` | Analyze convergence rates and complexity bounds |
| `notation-consistency-checker` | Build symbol table, detect notation inconsistencies |
| `theorem-dependency-mapper` | Build theorem/lemma dependency DAG with criticality scores |
| `proof-strategy-advisor` | Suggest proof approaches for theorems and conjectures |
| `counterexample-searcher` | Stress-test theorems by dropping assumptions |
| `intuition-formalizer` | Translate informal intuitions into formal theorem statements |
| `theory-connector` | Find cross-domain theoretical connections and analogies |

## Optional: Templates

Some skills use presentation templates. After cloning, install them to your local config:

```bash
mkdir -p ~/.claude/skills/templates
cp -r plugins/office/templates/slides ~/.claude/skills/templates/
cp -r plugins/academic/templates/posters ~/.claude/skills/templates/
```

To add new templates:
```bash
cd templates
python analyze_template.py /path/to/your/template.pptx --output slides --name "template-name"
```

## Optional: bibtexupdater

For the `paper-references` skill:
```bash
pip install bibtex-updater
```

## Domain Context

- **Primary audience:** ML researchers
- **Target venues:** NeurIPS, ICML, ICLR, AAAI
- **LaTeX packages:** cleveref, booktabs, amsmath
- **Figures:** matplotlib/seaborn, colorblind-safe palettes, PDF export

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding new skills and agents.

## License

MIT License - see [LICENSE](LICENSE) for details.
