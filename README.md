# Research Agora

A plugin marketplace for Claude Code with skills for ML research workflows, academic writing, and development automation.

## Installation

1. **Add the marketplace:**
   ```bash
   /plugin marketplace add rpatrik96/research-agora
   ```

2. **Install plugins:**
   ```bash
   /plugin install academic@research-agora
   /plugin install development@research-agora
   /plugin install formatting@research-agora
   /plugin install office@research-agora
   /plugin install research-agents@research-agora
   ```

## Available Plugins

### academic@research-agora

Paper writing, research, and dissemination skills:

| Skill | Description |
|-------|-------------|
| `paper-introduction` | Write introduction sections for ML papers |
| `paper-abstract` | Write or improve paper abstracts |
| `paper-literature` | Write literature review and related work |
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
| `literature-synthesizer` | Discover and synthesize relevant literature |
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
pip install bibtexupdater
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
