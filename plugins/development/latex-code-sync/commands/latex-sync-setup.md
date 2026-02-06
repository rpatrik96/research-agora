---
name: latex-sync-setup
description: Initialize latex-code-sync in a project. Use when asked to "set up equation verification", "link paper to code", "initialize latex-code-sync", or "set up paper-code synchronization". Creates equations module, configuration, and optionally CI workflow.
model: sonnet
---

# LaTeX-Code Sync Setup

> **Hybrid**: Project structure detection and file generation are scripted. LLM is used to identify equation-code correspondences.

Initialize latex-code-sync in a research project to link paper equations with code implementations.

## Setup Workflow

1. **Analyze project structure**: Determine if monorepo, separate repos, or Overleaf
2. **Identify key equations**: Find labeled equations in LaTeX, implementations in code
3. **Create equations module**: Annotated functions with `@latex` decorators
4. **Add configuration**: `latex-code-sync.toml` with project settings
5. **Set up CI**: Cross-repo verification workflow (optional)

## Project Structure Detection

### Monorepo Pattern
```
project/
├── paper/
│   ├── main.tex
│   └── appendix.tex
├── src/
│   └── equations.py    # Create here
└── pyproject.toml
```

### Separate Repos Pattern
```
code-repo/                    paper-repo/
├── equations.py              ├── main.tex
├── model.py                  └── appendix.tex
├── pyproject.toml
└── .github/workflows/
    └── verify-equations.yml  # Clone paper-repo in CI
```

## Step-by-Step Setup

### 1. Add Dependency

```toml
# pyproject.toml
[project.optional-dependencies]
verify = ["latex-code-sync>=0.1.0"]

# or in requirements.txt
latex-code-sync>=0.1.0
```

### 2. Create Equations Module

```python
# equations.py
"""
LaTeX-Code Sync: Linking paper equations to implementations.

Equation Registry:
- eq:loss      -> loss_function()
- eq:gradient  -> gradient_step()
"""

from __future__ import annotations
import torch

try:
    from latex_code_sync import latex, VerifyStrategy
except ImportError:
    def latex(*args, **kwargs):
        def decorator(func): return func
        return decorator
    class VerifyStrategy:
        NONE = "none"
        TEST_CASES = "test_cases"


@latex(
    "eq:loss",
    notation={"y": "y", "y_hat": r"\hat{y}"},
    description="Loss function (Eq. X in paper)",
    test_cases=[
        {"inputs": {"y": torch.tensor([1.0]), "y_hat": torch.tensor([1.0])}, "expected": 0.0},
    ],
)
def loss_function(y: torch.Tensor, y_hat: torch.Tensor) -> torch.Tensor:
    """Compute loss."""
    return torch.mean((y - y_hat) ** 2)


if __name__ == "__main__":
    print("Testing equations...")
    # Quick self-test
```

### 3. Create Configuration

```toml
# latex-code-sync.toml
[latex-code-sync]
latex_dir = "paper/"
modules = ["equations"]
strict = true
warn_unlabeled = true

[paper]
repository = "user/paper-repo"  # For separate repos
branch = "main"
```

### 4. Set Up CI (Separate Repos)

```yaml
# .github/workflows/verify-equations.yml
name: Verify Equations
on:
  push:
    branches: [main]
    paths: ['equations.py', '*.py']
  pull_request:
    paths: ['equations.py', '*.py']
  schedule:
    - cron: '0 6 * * *'  # Daily check
  workflow_dispatch:

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/checkout@v4
        with:
          repository: ${{ github.repository_owner }}/paper-repo
          path: paper
          
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - run: pip install -e ".[verify]" torch --index-url https://download.pytorch.org/whl/cpu
      
      - name: List equations
        run: |
          python -c "
          import equations
          from latex_code_sync import get_registry
          for label, spec in get_registry().equations.items():
              print(f'{label}: {spec.function.__name__ if spec.function else \"N/A\"}')"
              
      - name: Verify
        run: latex-code-sync verify --latex-dir=paper/ --modules=equations --strict
```

## Equation Discovery

### Find LaTeX Labels
```bash
# In paper directory
grep -rn "\\\\label{eq:" *.tex
grep -rn "\\\\label{eq:" **/*.tex

# Example output:
# main.tex:45:    E = mc^2 \label{eq:energy}
# appendix.tex:123:    \beta = \int v_t \, dt \label{eq:beta-def}
```

### Find Potential Implementations
```bash
# Look for functions that might implement equations
grep -rn "def compute_\|def calculate_\|def loss\|def energy" *.py
grep -rn "torch.mean\|torch.sum\|torch.exp" *.py
```

### Common Equation-Function Patterns

| LaTeX Pattern | Code Pattern |
|---------------|--------------|
| `eq:loss`, `eq:*-loss` | `*_loss()`, `compute_loss()` |
| `eq:energy`, `eq:E-*` | `energy()`, `compute_energy()` |
| `eq:gradient`, `eq:grad-*` | `gradient()`, `grad_*()` |
| `eq:update`, `eq:step` | `update()`, `step()` |
| `eq:softmax`, `eq:sigmoid` | `softmax()`, `sigmoid()` |
| `eq:kl`, `eq:divergence` | `kl_divergence()`, `kl_div()` |

## Annotation Strategy

### High Priority (Always Link)
- **Loss functions**: Core to reproducibility
- **Model equations**: Architecture definitions
- **Key metrics**: Evaluation formulas

### Medium Priority (Link if Implemented)
- **Theoretical bounds**: May be complex
- **Update rules**: Training dynamics

### Low Priority (Optional)
- **Standard operations**: PyTorch builtins
- **Notation definitions**: Just symbols

## Verification Modes

```python
# Explicit test cases (recommended)
@latex("eq:x", test_cases=[...])

# Property-based (for invariants)
@latex("eq:x", verify="properties", properties=["output >= 0"])

# No verification (complex implementations)
@latex("eq:x", verify="none")
```

## Output Checklist

After setup, verify:

- [ ] `equations.py` created with `@latex` decorators
- [ ] `latex-code-sync.toml` configuration file
- [ ] Dependency added to `pyproject.toml`
- [ ] CI workflow (if separate repos)
- [ ] README updated with verification instructions
- [ ] Self-test passes: `python equations.py`
