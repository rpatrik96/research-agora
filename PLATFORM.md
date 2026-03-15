# Research Agora Platform Design

## Vision

The Research Agora is community-driven infrastructure for AI-assisted research, built on three pillars:

1. **Discovery** (Skills Marketplace) — Find and share modular AI workflows for research tasks
2. **Comparison** (Benchmarks) — Evaluate and compare skill quality with standardized metrics
3. **Verification** (Test-Driven Research) — Define acceptance criteria before delegating to AI

Design principles:
- **Zero-backend:** GitHub-native, no servers to maintain, $0/month hosting
- **Community-driven:** Anyone can contribute skills or register third-party repos
- **Research-focused:** Taxonomy, metadata, and benchmarks designed for academic workflows
- **Agent-agnostic:** Skills follow the AgentSkills.io open standard (SKILL.md), compatible with Claude Code, Cursor, Gemini CLI, and GitHub Copilot

### Inspirations

| Platform | Strengths We Adopt | Gaps We Fill |
|----------|-------------------|--------------|
| **Tessl Registry** | Quality scores, CLI-first | Closed-source, expensive, developer-focused |
| **claudemarketplaces.com** | Zero-backend GitHub aggregator | No search/filter, no quality signals |
| **AgentSkills.io** | Open standard (SKILL.md), multi-agent | No research domain taxonomy |

---

## Architecture

### Federated GitHub Model

The Research Agora uses a **hub-and-spoke** architecture:

- **Hub repo** (`rpatrik96/research-agora`): Contains the registry index, first-party skills, static site, and CI/CD
- **Spoke repos** (third-party): Maintain their own skills independently, registered via PR to the hub

```
research-agora/              # Hub
├── registry/
│   ├── index.json           # Machine-readable index of ALL skills (first + third-party)
│   └── categories.json      # Taxonomy definition
├── plugins/                 # First-party skills
│   ├── academic/
│   ├── development/
│   ├── formatting/
│   ├── office/
│   └── research-agents/
├── site/                    # Static site templates
└── scripts/                 # Generators and validators

third-party-repo/            # Spoke
├── plugins/
│   └── my-domain/
│       ├── .claude-plugin/plugin.json
│       ├── SKILL.md
│       └── commands/
└── ...
```

### Registration Flow

1. Third-party repo creates skills following the skill schema
2. Author opens a PR to `research-agora` adding their repo to `registry/index.json`
3. CI validates the entry (repo exists, skills have valid frontmatter)
4. Merge makes the skills discoverable on the static site and via CLI

---

## Skill Schema

Skills use YAML frontmatter in Markdown files, extending the AgentSkills.io base with research-specific metadata.

### Base Fields (Required)

```yaml
---
name: paper-references
description: |
  Verify citations against scholarly databases. Use when asked to
  "verify citations", "check references", "fact-check bibliography".
model: sonnet  # sonnet | haiku | opus
---
```

### Research Extensions (Required for Registry)

```yaml
---
name: paper-references
description: |
  Verify citations against scholarly databases.
model: sonnet
metadata:
  research-domain: general       # From categories.json
  task-type: verification        # From categories.json
  research-phase: paper-writing  # From categories.json
  verification-level: formal     # formal | heuristic | layered | none
---
```

### Metadata Field Definitions

**research-domain**: The academic field this skill targets.
- `ml`, `nlp`, `cv`, `robotics`, `theory`, `statistics`, `biology`, `general`

**task-type**: What kind of work this skill performs.
- `writing` — Generates or improves text (abstracts, introductions, discussions)
- `verification` — Checks correctness (citations, claims, statistics)
- `analysis` — Analyzes or synthesizes information (literature, evidence, arguments)
- `formatting` — Formats output (LaTeX, figures, tables)
- `automation` — Automates workflows (CI/CD, commits, PRs)
- `dissemination` — Shares research (slides, posters, Twitter threads)
- `review` — Evaluates quality (peer review, audience checking)

**research-phase**: Which stage of the research lifecycle this skill supports.
- `literature-review`, `experiment-design`, `implementation`, `paper-writing`, `submission`, `rebuttal`, `dissemination`

**verification-level**: How rigorously this skill can verify its own output.
- `formal` — Deterministic checks against external sources (e.g., DOI lookup, unit tests)
- `heuristic` — Rule-based checks with known limitations (e.g., statistical thresholds)
- `layered` — Multiple complementary checks without formal guarantees (e.g., evidence hierarchy)
- `none` — Output quality depends entirely on LLM judgment

---

## Discovery

### Static Site (GitHub Pages)

A Jinja2-generated static site at `https://rpatrik96.github.io/research-agora` provides:

- **Card grid** showing all skills with name, plugin badge, description, verification badge, model tag
- **Filter sidebar** with checkboxes for domain, task-type, phase, verification-level
- **Client-side search** using lunr.js for full-text search across skill names and descriptions
- **One-click install** commands: `/plugin install {name}@research-agora`
- **Stats header**: skill count, plugin count, contributor count
- **Links** to GitHub source for each skill

Tech stack: Python + Jinja2 → static HTML, no Node.js build step. Pico CSS for classless styling (~10KB).

### CLI Discovery

The existing Claude Code plugin system already supports:

```bash
/plugin marketplace add rpatrik96/research-agora
/plugin list --marketplace research-agora
/plugin install paper-references@research-agora
```

### Taxonomy

Skills are organized along four independent dimensions, enabling faceted search:

```
Domains      × Task Types    × Phases           × Verification
─────────      ──────────      ──────             ────────────
ml             writing         literature-review   formal
nlp            verification    experiment-design   heuristic
cv             analysis        implementation      layered
theory         formatting      paper-writing       none
general        automation      submission
...            dissemination   rebuttal
               review          dissemination
```

---

## Benchmarks (Pillar 2)

### Design Principles

1. **Public dev sets + hidden test sets**: Dev sets for development, test sets in a private repo for evaluation
2. **Anti-gaming**: Quarterly refresh of test sets, temporal segmentation (inspired by LiveCodeBench)
3. **Contamination resistance**: Hidden test entries prevent memorization
4. **Baselines**: Every benchmark ships with baseline implementations others can build upon

### First Benchmark: Citation Hallucination Detection

**Task**: Given a BibTeX entry and optional context, classify it as valid or fabricated.

**Dataset structure**:
- ~1,000 entries: mix of real citations (from published papers) and fabricated ones (LLM-generated)
- Taxonomy of hallucination types: non-existent papers, wrong authors, wrong venues, wrong years, plausible but fake
- Public dev set (~200 entries) for development
- Hidden test set (~800 entries) for evaluation, refreshed quarterly

**Evaluation**:
- Precision, recall, F1 for hallucination detection
- Breakdown by hallucination type
- Per-model and per-skill leaderboard on the static site

### Future Benchmarks

- **Claim verification**: Does the code actually implement what the paper claims?
- **Statistical validation**: Are p-values, confidence intervals, and effect sizes correct?
- **Literature completeness**: Does the related work section cover the relevant prior art?

### Leaderboard

The static site includes a leaderboard page:
- Skills ranked by benchmark scores
- Filtering by benchmark, model, skill category
- Submission via PR with evaluation results (reproducible with provided scripts)

---

## Test-Driven Research (Pillar 3)

### Verification Hierarchy

Different research tasks afford different levels of verification:

| Level | Name | Description | Example |
|-------|------|-------------|---------|
| L1 | Formal | Deterministic, automated checks | Citation DOI lookup, unit tests |
| L2 | Heuristic | Rule-based with known limitations | Statistical threshold checks |
| L3 | Layered | Multiple complementary checks | Evidence hierarchy (L1-L6 scores) |
| L4 | Consensus | Community agreement | Peer review, reproducibility |
| L5 | Judgment | Human expert assessment | Writing quality, research taste |

### Trust Badges

Skills display verification badges on the static site:

- **Formal** (green shield) — Output verified against external ground truth
- **Heuristic** (yellow shield) — Rule-based checks with documented limitations
- **Layered** (blue shield) — Multiple checks, no single point of failure
- **None** (gray shield) — LLM judgment only, use with oversight

### Evidence Hierarchy (Already Implemented)

The `evidence-checker` agent implements a 6-level evidence hierarchy:
- L1: Empirical (controlled experiments, statistical significance)
- L2: Theoretical (formal proofs, established theorems)
- L3: Observational (case studies, correlational evidence)
- L4: Precedent (peer-reviewed citations, standard practice)
- L5: Reasoning (logical arguments, analogies)
- L6: Assumed (unstated assumptions, "well known")

---

## Contribution Workflow

### First-Party Skills (Direct Contribution)

```
1. Fork research-agora
2. Create skill:  python scripts/create-skill.py --name my-skill --category academic
3. Write skill:   plugins/academic/commands/my-skill.md
4. Add metadata:  Include metadata block in frontmatter
5. Test:          pytest tests/
6. PR:            Open PR to research-agora/main
```

### Third-Party Skills (Federation)

```
1. Create skills in your own repo following the skill schema
2. Add SKILL.md to your plugin root
3. Open PR to research-agora adding your repo to registry/index.json:
   {
     "repo": "your-org/your-repo",
     "description": "Your plugin description",
     "skills": [...]
   }
4. CI validates your entry
5. Merge makes your skills discoverable
```

### Scaffolding

```bash
# Create a new skill with full frontmatter template
python scripts/create-skill.py --name my-skill --category academic --type writing --domain ml

# Validate all skills have proper metadata
pytest tests/test_skills.py

# Regenerate the registry index
python scripts/generate-registry.py

# Generate the static site locally
python scripts/generate-site.py
```

---

## Governance

### Phased Model

**Phase 1 (Current): BDFL**
- Single maintainer reviews all PRs
- Focus on establishing quality standards and conventions

**Phase 2: Category Stewards**
- Trusted contributors become CODEOWNERS for specific plugin categories
- `plugins/academic/` → academic steward
- `plugins/research-agents/` → agents steward
- Stewards review PRs in their domain, maintainer handles cross-cutting concerns

**Phase 3: Council**
- Elected governance council for major decisions (new categories, breaking changes, benchmark design)
- RFC process for significant changes

### Licensing

- **Code**: MIT License
- **Skills**: MIT License (same as code — skills are code)
- **Benchmarks**: CC-BY-4.0 for datasets, MIT for evaluation scripts

### Citation

Skills are citable software. Each skill includes a suggested BibTeX entry:

```bibtex
@software{research-agora-paper-references,
  author = {Reizinger, Patrik},
  title = {paper-references: Citation Verification for ML Papers},
  year = {2026},
  url = {https://github.com/rpatrik96/research-agora},
  note = {Research Agora skill}
}
```

---

## Roadmap

### Phase 1: Static Site + Registry Index (Current)

- [x] Skills marketplace with 70+ workflows across 5 plugins
- [x] Test suite with 50+ tests validating structure and metadata
- [ ] Registry index (`registry/index.json`) generated from skill files
- [ ] Research metadata on all skills (domain, task-type, phase, verification-level)
- [ ] Static site with filters and search deployed to GitHub Pages
- [ ] Skill scaffolding tool (`scripts/create-skill.py`)

### Phase 2: Federation + Community

- [ ] Third-party repo registration via PR
- [ ] CI validation of third-party skill entries
- [ ] Contributor guidelines and steward roles
- [ ] CODEOWNERS for plugin categories
- [ ] Community discussion forum (GitHub Discussions)

### Phase 3: Benchmark Infrastructure

- [ ] Citation hallucination benchmark (dev + hidden test sets)
- [ ] Evaluation scripts and submission format
- [ ] Leaderboard on static site
- [ ] Quarterly test set refresh pipeline
- [ ] Additional benchmarks (claim verification, statistical validation)

### Phase 4: Agent-Agnostic Expansion

- [ ] SKILL.md compatibility layer for Cursor, Gemini CLI, GitHub Copilot
- [ ] Cross-platform skill format converter
- [ ] Multi-agent interoperability testing
- [ ] Research Agora as reference implementation for AgentSkills.io
