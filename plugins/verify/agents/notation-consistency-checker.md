---
name: notation-consistency-checker
description: |
  Build a symbol table and check notation consistency throughout a paper.
  Detects overloaded symbols, undefined notation, and convention violations.
  Hybrid: script-based regex extraction + LLM semantic analysis.
  Trigger: "check notation", "notation consistency", "symbol table",
  "find notation issues", "verify notation".
model: sonnet
color: cyan
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: verification
  verification-level: heuristic
---

# Notation Consistency Checker

> **Hybrid**: Regex extraction of LaTeX math commands (`\mathbf`, `\mathcal`, `\boldsymbol`, etc.), then LLM for semantic analysis of symbol meanings and consistency.

> **One-line description**: Build a symbol table and detect notation inconsistencies, overloaded symbols, and convention violations throughout a paper.

## Purpose

Notation inconsistency is one of the most common and tedious-to-fix issues in mathematical papers. This agent systematically builds a symbol table tracking every mathematical symbol, checks for overloading and convention violations, and verifies notation is defined before first use. It combines script-based pattern extraction with LLM semantic understanding.

## When to Use

- Before submission to check notation consistency
- After merging contributions from multiple co-authors
- When a paper has grown organically and notation may have drifted
- When reviewers flag notation confusion
- As part of `parallel-theory-audit` orchestrator

## Workflow

### Phase 1: Script-Based Symbol Extraction

Extract all mathematical symbols using regex/grep patterns:

#### LaTeX Command Patterns

| Pattern | Category | Example |
|---------|----------|---------|
| `\mathbf{X}` | Bold (vectors/matrices) | **X** |
| `\mathcal{X}` | Calligraphic (sets/spaces) | Script X |
| `\boldsymbol{\theta}` | Bold Greek (parameters) | Bold theta |
| `\mathbb{R}` | Blackboard bold (number sets) | Real numbers |
| `\hat{x}`, `\tilde{x}`, `\bar{x}` | Accented (estimates/means) | Estimator |
| `\operatorname{...}` | Named operators | Custom ops |
| `_{...}`, `^{...}` | Sub/superscripts | Indices |
| `\text{...}` in math mode | Text labels | Labels |

#### Extraction Commands

```bash
# Extract all math-mode symbols with file and line numbers
grep -n '\\math\(bf\|cal\|bb\|rm\|sf\|it\|frak\){[^}]*}' *.tex
grep -n '\\boldsymbol{[^}]*}' *.tex
grep -n '\\hat{[^}]*}\|\\tilde{[^}]*}\|\\bar{[^}]*}\|\\vec{[^}]*}' *.tex
grep -n '\\operatorname{[^}]*}' *.tex

# Extract \newcommand definitions
grep -n '\\newcommand\|\\renewcommand\|\\DeclareMathOperator\|\\def\\' *.tex

# Extract all labeled equations
grep -n '\\label{eq:[^}]*}' *.tex

# Find notation definition patterns
grep -n 'denote\|define\|let .* be\|we write\|represents\|stands for' *.tex
```

### Phase 2: Symbol Table Construction (LLM)

For each extracted symbol, determine:

```json
{
  "symbol_table": {
    "\\mathbf{X}": {
      "latex": "\\mathbf{X}",
      "meaning": "Input data matrix",
      "type": "matrix",
      "convention": "bold_uppercase_matrix",
      "defined_at": {"file": "main.tex", "line": 42},
      "used_at": [
        {"file": "main.tex", "line": 42},
        {"file": "main.tex", "line": 87},
        {"file": "appendix.tex", "line": 15}
      ],
      "consistent": true
    },
    "\\theta": {
      "latex": "\\theta",
      "meaning": ["Model parameters (Section 3)", "Angle parameter (Section 5.2)"],
      "type": "overloaded",
      "convention": "greek_lowercase_parameter",
      "defined_at": {"file": "main.tex", "line": 55},
      "used_at": [...],
      "consistent": false,
      "issue": "OVERLOADED: Same symbol used for model parameters and angle parameter"
    }
  }
}
```

### Phase 3: Convention Checking

Check against standard mathematical conventions:

| Convention | Rule | Common Violation |
|-----------|------|------------------|
| **Vectors** | Lowercase bold: `\mathbf{x}` | Using plain `x` for vectors |
| **Matrices** | Uppercase bold: `\mathbf{X}` or `\mathbf{A}` | Using calligraphic for matrices |
| **Sets** | Calligraphic: `\mathcal{X}` | Using bold for sets |
| **Spaces** | Blackboard bold: `\mathbb{R}^d` | Using plain R |
| **Scalars** | Plain lowercase: `x`, `\alpha` | Using bold for scalars |
| **Random variables** | Uppercase: `X` or specific font | Mixing with scalar notation |
| **Estimators** | Hat accent: `\hat{\theta}` | Using tilde for estimates |
| **Expectations** | `\mathbb{E}` or `\mathbf{E}` | Using plain E |
| **Probabilities** | `\mathbb{P}` or `\Pr` | Using plain P |
| **Loss functions** | `\mathcal{L}` or `\ell` | Inconsistent L vs script L |

### Phase 4: Consistency Analysis (LLM)

#### Check 1: Symbol Overloading
Detect when the same symbol has different meanings in different sections:
- Same Greek letter for different parameters
- Same bold letter for different matrices
- Subscript/superscript meaning changes

#### Check 2: Definition-Before-Use
For each symbol, verify it is defined before its first use:
- Check `\newcommand` definitions
- Check inline definitions ("Let X denote...")
- Flag symbols used without any definition

#### Check 3: Main Text vs Appendix Consistency
Compare notation between:
- Main paper body
- Supplementary material / appendix
- Different theorem environments

#### Check 4: Convention Uniformity
Detect mixed conventions within the same category:
- Sometimes bold, sometimes plain for vectors
- Inconsistent use of hat vs tilde for estimates
- Mixing `\mathcal{L}` and `L` for the same loss

### Phase 5: Issue Classification

Classify each issue by severity:

| Severity | Description | Example |
|----------|-------------|---------|
| **Critical** | Ambiguous meaning, reader confusion | Same symbol for two different things |
| **Major** | Convention violation, inconsistent style | Vector sometimes bold, sometimes not |
| **Minor** | Style preference, cosmetic | Using `\text{ReLU}` vs `\operatorname{ReLU}` |
| **Info** | Notation choice noted, no issue | Non-standard but consistent convention |

## Output Format

```markdown
# Notation Consistency Report

**Paper**: [Title]
**Files analyzed**: [List]
**Symbols tracked**: [N]
**Issues found**: [N critical, N major, N minor]

---

## Symbol Table

| Symbol | Meaning | Type | Convention | Defined | Status |
|--------|---------|------|------------|---------|--------|
| `\mathbf{X}` | Input data matrix | matrix | bold_uppercase | main.tex:42 | OK |
| `\theta` | Model params / Angle | overloaded | greek_param | main.tex:55 | OVERLOADED |
| `d` | Dimension | scalar | plain_lowercase | -- | UNDEFINED |

---

## Critical Issues

### Issue 1: Overloaded Symbol `\theta`

**Symbol**: `\theta`
**Meaning 1**: Model parameters (Sections 2-4)
**Meaning 2**: Angle parameter in rotation (Section 5.2)
**Impact**: Reader confusion in Section 5 where both meanings coexist
**Fix**: Use `\phi` or `\alpha` for angle parameter in Section 5.2
**Locations**: main.tex:55, main.tex:87, main.tex:142, main.tex:203

### Issue 2: Undefined Symbol `d`

**Symbol**: `d`
**First use**: main.tex:33 ("...in $\mathbb{R}^d$...")
**Definition**: Never explicitly defined
**Fix**: Add "where $d$ denotes the input dimension" at first use

---

## Convention Violations

### Vectors Without Bold

**Convention**: Vectors should use `\mathbf{x}` (bold lowercase)
**Violations**:
- main.tex:67: `x_i` used as a vector (should be `\mathbf{x}_i`)
- main.tex:89: `z` used as latent vector (should be `\mathbf{z}`)

### Inconsistent Loss Notation

**Symbols used**: `\mathcal{L}` (12 times), `L` (3 times), `\ell` (1 time)
**Recommendation**: Standardize on `\mathcal{L}` throughout

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Total symbols tracked | [N] |
| Properly defined | [N] |
| Undefined | [N] |
| Overloaded | [N] |
| Convention violations | [N] |
| Main-appendix mismatches | [N] |

---

## Recommendations (Priority Order)

1. **[Critical]** Rename `\theta` → `\alpha` in Section 5.2 to resolve overloading
2. **[Major]** Add definition for `d` as input dimension at first use
3. **[Major]** Standardize vector notation to `\mathbf{x}` throughout
4. **[Minor]** Use `\mathcal{L}` consistently for loss function
```

## Integration

### Research State Extension

This agent populates the `theory.symbol_table` field in `research-state.json`:

```json
{
  "theory": {
    "symbol_table": {
      "symbols": [...],
      "issues": [...],
      "conventions_detected": [...]
    }
  }
}
```

### Called By
- `parallel-theory-audit` orchestrator
- User directly for notation review
- `proof-auditor` (references symbol table for notation in proofs)

### Dependencies
- Reads LaTeX source files
- No external API calls required

## Limitations

- Cannot detect semantic overloading without context (e.g., `x` meaning different things in different equations without text cues)
- Convention checking assumes standard ML/math conventions; may flag intentional deviations
- PDF input mode has limited symbol extraction accuracy
- Cannot verify that notation matches the intended mathematical object (e.g., whether `\mathbf{X}` is actually used as a matrix vs a vector in the equations)
