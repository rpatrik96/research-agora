---
name: latex-sync
description: |
  Keep a paper's equations and the code implementing them in agreement, via the
  latex-code-sync CLI. Use when asked to "set up latex-code-sync", "link
  equations to code", "annotate functions with equations", "verify equations
  match code", "check the paper against the implementation", or "does my code
  match my math". Three modes of one workflow: **setup** bootstraps the package
  and CI, **annotate** links functions to equations with decorators, **verify**
  runs the checker and reports mismatches.
model: sonnet
disable-model-invocation: true
metadata:
  research-domain: general
  research-phase: implementation
  task-type: verification
  verification-level: formal
---

# LaTeX ↔ Code Sync

One workflow against one CLI, in the order you do it.

| They said | Mode |
|---|---|
| "set up", "initialize", "add this to my project" | **setup** |
| "link", "annotate", "tag this function" | **annotate** |
| "verify", "check", "do they match" | **verify** |

Three skills until RFC-0002, and the split bought a user nothing: nobody
annotates without having set up, and nobody verifies without having annotated.

---

## Mode: setup

> **Hybrid**: Project structure detection and file generation are scripted. LLM is used to identify equation-code correspondences.

Initialize latex-code-sync in a research project to link paper equations with code implementations.

### Setup Workflow

1. **Analyze project structure**: Determine if monorepo, separate repos, or Overleaf
2. **Identify key equations**: Find labeled equations in LaTeX, implementations in code
3. **Create equations module**: Annotated functions with `@latex` decorators
4. **Add configuration**: `latex-code-sync.toml` with project settings
5. **Set up CI**: Cross-repo verification workflow (optional)

### Project Structure Detection

#### Monorepo Pattern
```
project/
├── paper/
│   ├── main.tex
│   └── appendix.tex
├── src/
│   └── equations.py    # Create here
└── pyproject.toml
```

#### Separate Repos Pattern
```
code-repo/                    paper-repo/
├── equations.py              ├── main.tex
├── model.py                  └── appendix.tex
├── pyproject.toml
└── .github/workflows/
    └── verify-equations.yml  # Clone paper-repo in CI
```

### Step-by-Step Setup

#### 1. Add Dependency

```toml
# pyproject.toml
[project.optional-dependencies]
verify = ["latex-code-sync>=0.1.0"]

# or in requirements.txt
latex-code-sync>=0.1.0
```

#### 2. Create Equations Module

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

#### 3. Create Configuration

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

#### 4. Set Up CI (Separate Repos)

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

### Equation Discovery

#### Find LaTeX Labels
```bash
# In paper directory
grep -rn "\\\\label{eq:" *.tex
grep -rn "\\\\label{eq:" **/*.tex

# Example output:
# main.tex:45:    E = mc^2 \label{eq:energy}
# appendix.tex:123:    \beta = \int v_t \, dt \label{eq:beta-def}
```

#### Find Potential Implementations
```bash
# Look for functions that might implement equations
grep -rn "def compute_\|def calculate_\|def loss\|def energy" *.py
grep -rn "torch.mean\|torch.sum\|torch.exp" *.py
```

#### Common Equation-Function Patterns

| LaTeX Pattern | Code Pattern |
|---------------|--------------|
| `eq:loss`, `eq:*-loss` | `*_loss()`, `compute_loss()` |
| `eq:energy`, `eq:E-*` | `energy()`, `compute_energy()` |
| `eq:gradient`, `eq:grad-*` | `gradient()`, `grad_*()` |
| `eq:update`, `eq:step` | `update()`, `step()` |
| `eq:softmax`, `eq:sigmoid` | `softmax()`, `sigmoid()` |
| `eq:kl`, `eq:divergence` | `kl_divergence()`, `kl_div()` |

### Annotation Strategy

#### High Priority (Always Link)
- **Loss functions**: Core to reproducibility
- **Model equations**: Architecture definitions
- **Key metrics**: Evaluation formulas

#### Medium Priority (Link if Implemented)
- **Theoretical bounds**: May be complex
- **Update rules**: Training dynamics

#### Low Priority (Optional)
- **Standard operations**: PyTorch builtins
- **Notation definitions**: Just symbols

### Verification Modes

```python
# Explicit test cases (recommended)
@latex("eq:x", test_cases=[...])

# Property-based (for invariants)
@latex("eq:x", verify="properties", properties=["output >= 0"])

# No verification (complex implementations)
@latex("eq:x", verify="none")
```

### Output Checklist

After setup, verify:

- [ ] `equations.py` created with `@latex` decorators
- [ ] `latex-code-sync.toml` configuration file
- [ ] Dependency added to `pyproject.toml`
- [ ] CI workflow (if separate repos)
- [ ] README updated with verification instructions
- [ ] Self-test passes: `python equations.py`

---

## Mode: annotate

> **LLM-required**: Linking code functions to paper equations requires understanding mathematical semantics. No script alternative.

Add `@latex` decorators to existing Python functions to create verified links between code implementations and paper equations.

### Annotation Workflow

1. **Identify function**: Find the Python function implementing an equation
2. **Match equation**: Locate the corresponding `\label{eq:...}` in LaTeX
3. **Map notation**: Connect Python parameters to LaTeX symbols
4. **Add test cases**: Provide verification inputs/outputs
5. **Apply decorator**: Add `@latex(...)` above function

### Decorator Syntax

#### Minimal
```python
@latex("eq:loss")
def compute_loss(y, y_hat):
    return torch.mean((y - y_hat) ** 2)
```

#### With Notation Mapping
```python
@latex(
    "eq:gradient-descent",
    notation={
        "params": r"\theta",          # θ in paper
        "loss": r"\mathcal{L}",       # L in paper
        "learning_rate": r"\eta",     # η in paper
    },
)
def gradient_step(params, loss, learning_rate):
    return params - learning_rate * grad(loss, params)
```

#### With Test Cases
```python
@latex(
    "eq:softmax",
    test_cases=[
        {
            "inputs": {"logits": torch.tensor([0.0, 0.0, 0.0])},
            "expected": torch.tensor([1/3, 1/3, 1/3]),
            "tolerance": 1e-6,
        },
        {
            "inputs": {"logits": torch.tensor([1000.0, 0.0, 0.0])},
            "expected": torch.tensor([1.0, 0.0, 0.0]),
            "tolerance": 1e-4,
        },
    ],
)
def softmax(logits: torch.Tensor) -> torch.Tensor:
    exp_x = torch.exp(logits - logits.max())
    return exp_x / exp_x.sum()
```

#### With Dependencies
```python
@latex(
    "eq:elbo",
    depends=["eq:kl-divergence", "eq:reconstruction"],
    description="Evidence lower bound combines KL and reconstruction terms",
)
def elbo(x, z, mu, logvar):
    return reconstruction_loss(x, z) - kl_divergence(mu, logvar)
```

#### Without Verification
```python
@latex(
    "eq:complex-integral",
    verify="none",  # Too complex to test with simple cases
    description="Numerical integration of path measure",
)
def compute_path_integral(trajectories, potential):
    # Complex implementation...
    pass
```

### Common Notation Mappings

| Python Name | LaTeX Symbol | Example |
|-------------|--------------|---------|
| `x`, `input` | `x` | Input data |
| `y`, `target` | `y` | Target/label |
| `y_hat`, `pred` | `\hat{y}` | Prediction |
| `params`, `theta` | `\theta` | Model parameters |
| `learning_rate`, `lr` | `\eta` | Learning rate |
| `loss`, `L` | `\mathcal{L}` | Loss function |
| `grad`, `gradient` | `\nabla` | Gradient |
| `mu`, `mean` | `\mu` | Mean |
| `sigma`, `std` | `\sigma` | Standard deviation |
| `alpha`, `beta`, `gamma` | `\alpha`, `\beta`, `\gamma` | Greek letters |
| `weight`, `W` | `W` or `\mathbf{W}` | Weight matrix |
| `bias`, `b` | `b` or `\mathbf{b}` | Bias vector |
| `hidden`, `h` | `h` or `\mathbf{h}` | Hidden state |
| `epsilon`, `eps` | `\epsilon` | Small constant |
| `lambda_`, `lam` | `\lambda` | Regularization |
| `temperature`, `tau` | `\tau` | Temperature |

### Test Case Strategies

#### Numerical Functions
```python
test_cases=[
    # Zero case
    {"inputs": {"x": torch.zeros(3)}, "expected": torch.zeros(3)},
    # Identity case
    {"inputs": {"x": torch.ones(3)}, "expected": torch.ones(3)},
    # Known values
    {"inputs": {"x": torch.tensor([1.0, 2.0])}, "expected": torch.tensor([...])},
]
```

#### Loss Functions
```python
test_cases=[
    # Perfect prediction = zero loss
    {"inputs": {"y": t([1,2,3]), "y_hat": t([1,2,3])}, "expected": 0.0},
    # Known error
    {"inputs": {"y": t([0.0]), "y_hat": t([1.0])}, "expected": 1.0},
]
```

#### Probability Functions
```python
test_cases=[
    # Uniform distribution
    {"inputs": {"logits": torch.zeros(3)}, "expected": torch.tensor([1/3, 1/3, 1/3])},
    # Peaked distribution
    {"inputs": {"logits": torch.tensor([100.0, 0.0])}, "expected": torch.tensor([1.0, 0.0])},
    # Sum to 1
    {"inputs": {"logits": torch.randn(5)}, "property": "output.sum() == 1.0"},
]
```

### Batch Annotation Example

Given these equations in paper:

```latex
% main.tex
\begin{equation}\label{eq:energy}
    E_t^{(j)}(\phi, x) := \frac{\|\phi_{\Omega_x} - \sqrt{\bar\alpha_t}\varphi_j\|_2^2}{2(1-\bar\alpha_t)}
\end{equation}

\begin{equation}\label{eq:weights}
    W_t^{(j)}(\phi,x) := \frac{e^{-E_t^{(j)}}}{\sum_{\ell} e^{-E_t^{(\ell)}}}
\end{equation}

\begin{equation}\label{eq:uncertainty}
    \mathsf{U}_t(\phi,x) := 1 - \sum_{j=1}^N W_t^{(j)}(\phi,x)^2
\end{equation}
```

Create annotated functions:

```python
# equations.py
from latex_code_sync import latex
import torch

@latex(
    "eq:energy",
    notation={
        "phi_patch": r"\phi_{\Omega_x}",
        "library_patch": r"\varphi_j",
        "alpha_bar_t": r"\bar\alpha_t",
    },
    test_cases=[
        {"inputs": {"phi_patch": torch.zeros(9), "library_patch": torch.zeros(9), "alpha_bar_t": 0.5}, "expected": 0.0},
    ],
)
def els_energy(phi_patch, library_patch, alpha_bar_t):
    """ELS patch-matching energy."""
    sqrt_alpha = torch.sqrt(torch.tensor(alpha_bar_t))
    sigma_sq = 1 - alpha_bar_t
    diff = phi_patch - sqrt_alpha * library_patch
    return (diff ** 2).sum() / (2 * sigma_sq)


@latex(
    "eq:weights",
    notation={"energies": r"E_t^{(j)}"},
    depends=["eq:energy"],
)
def gibbs_weights(energies):
    """Compute Gibbs/softmax weights from energies."""
    return torch.softmax(-energies, dim=-1)


@latex(
    "eq:uncertainty",
    notation={"weights": r"W_t^{(j)}"},
    depends=["eq:weights"],
    test_cases=[
        {"inputs": {"weights": torch.tensor([1.0, 0.0, 0.0])}, "expected": 0.0},
        {"inputs": {"weights": torch.tensor([0.5, 0.5])}, "expected": 0.5},
    ],
)
def weight_uncertainty(weights):
    """Gini impurity of weight distribution."""
    return 1.0 - (weights ** 2).sum(dim=-1)
```

### Checklist for Each Annotation

- [ ] Label matches exactly: `eq:energy` not `eq:Energy`
- [ ] Notation maps all key parameters
- [ ] At least one test case (unless `verify="none"`)
- [ ] Dependencies listed if function calls other annotated functions
- [ ] Description matches paper context
- [ ] Function docstring explains the equation

---

## Mode: verify

> **Script-first**: This skill runs the latex-code-sync CLI tool. LLM assists only with interpreting failures.

Run latex-code-sync verification to ensure paper equations match their code implementations.

### Quick Verification

```bash
# Basic verification
latex-code-sync verify --latex-dir=paper/ --modules=equations

# Strict mode (fail on any issue)
latex-code-sync verify --latex-dir=paper/ --modules=equations --strict

# Verbose output
latex-code-sync verify --latex-dir=paper/ --modules=equations -v

# Multiple modules
latex-code-sync verify --latex-dir=paper/ --modules=equations,models.loss,utils.math
```

### Verification Checks

| Check | Description | Example Issue |
|-------|-------------|---------------|
| **Label exists** | `\label{eq:X}` found in LaTeX | Typo in decorator |
| **Function registered** | `@latex("eq:X")` decorator present | Missing import |
| **Test cases pass** | Test inputs produce expected outputs | Implementation bug |
| **Dependencies valid** | All `depends` labels exist | Removed equation |
| **Notation consistent** | Symbol mappings are plausible | Parameter renamed |

### Interpreting Results

#### Success
```
✓ eq:energy - PASSED (3 test cases)
✓ eq:weights - PASSED (2 test cases)
✓ eq:uncertainty - PASSED (2 test cases)

Verification complete: 3/3 equations passed
```

#### Failure
```
✗ eq:energy - FAILED
  Test case 1: Expected 0.0, got 0.5

  Inputs: phi_patch=zeros(9), library_patch=zeros(9), alpha_bar_t=0.5
  Code: equations.py:45 els_energy()
  Paper: main.tex:67 \label{eq:energy}

  Possible causes:
  - Formula mismatch: check normalization factor
  - Parameter interpretation differs
```

#### Missing Label
```
⚠ eq:beta-def - Label not found in LaTeX
  Decorator at: equations.py:89
  Searched: paper/*.tex

  Did you mean: eq:beta (found in appendix.tex:234)?
```

### Local Verification Workflow

#### 1. Quick Check (Python only)
```python
# Run the equations module directly
python equations.py

# Or in Python
import equations
from latex_code_sync import get_registry, verify_all

registry = get_registry()
results = verify_all(registry)
for label, result in results.items():
    print(f"{label}: {'PASS' if result.passed else 'FAIL'}")
```

#### 2. Full Verification (with LaTeX)
```bash
# Clone/locate paper repo
git clone https://github.com/user/paper-repo paper/

# Run verification
latex-code-sync verify --latex-dir=paper/ --modules=equations
```

#### 3. CI Verification
```bash
# Simulates CI environment
PAPER_DIR=paper/ latex-code-sync verify --modules=equations --strict
```

### Debugging Failures

#### Test Case Failures

```python
# Add debugging to test case
@latex(
    "eq:energy",
    test_cases=[{
        "inputs": {"x": torch.tensor([1.0])},
        "expected": 1.0,
        "debug": True,  # Print intermediate values
    }]
)
```

#### Manual Verification
```python
# Test function manually
from equations import els_energy
import torch

phi = torch.zeros(9)
lib = torch.zeros(9)
alpha = 0.5

result = els_energy(phi, lib, alpha)
print(f"Result: {result}")
print(f"Expected: 0.0")
print(f"Match: {abs(result - 0.0) < 1e-6}")
```

#### Compare with Paper Formula

```python
# Paper: E = ||φ - √α·lib||² / (2(1-α))
def paper_formula(phi, lib, alpha):
    diff = phi - math.sqrt(alpha) * lib
    return (diff ** 2).sum() / (2 * (1 - alpha))

# Code implementation
def code_implementation(phi, lib, alpha):
    return els_energy(phi, lib, alpha)

# Compare
phi = torch.randn(9)
lib = torch.randn(9)
alpha = 0.5

paper_result = paper_formula(phi, lib, alpha)
code_result = code_implementation(phi, lib, alpha)
print(f"Paper: {paper_result:.6f}")
print(f"Code: {code_result:.6f}")
print(f"Diff: {abs(paper_result - code_result):.2e}")
```

### Common Issues and Fixes

#### Issue: Numerical Precision
```python
# Increase tolerance
test_cases=[{
    "inputs": {...},
    "expected": 0.333333,
    "tolerance": 1e-5,  # Default is 1e-6
}]
```

#### Issue: Tensor Shape Mismatch
```python
# Ensure consistent shapes in test
test_cases=[{
    "inputs": {"x": torch.tensor([1.0, 2.0])},  # Shape: (2,)
    "expected": torch.tensor([0.5, 1.0]),       # Must match shape
}]
```

#### Issue: Random Initialization
```python
# Set seed for reproducibility
@latex("eq:x", test_cases=[...])
def func_with_randomness(x):
    torch.manual_seed(42)  # Fixed seed
    return ...
```

#### Issue: Device Mismatch
```python
# Force CPU for tests
test_cases=[{
    "inputs": {"x": torch.tensor([1.0]).cpu()},
    "expected": torch.tensor([1.0]).cpu(),
}]
```

### Generating Verification Reports

```bash
# Markdown report
latex-code-sync report --latex-dir=paper/ --modules=equations -o report.md

# JSON for CI
latex-code-sync verify --latex-dir=paper/ --modules=equations --json > results.json
```

#### Report Format
```markdown
# Equation Verification Report

## Summary
- Total equations: 12
- Passed: 10
- Failed: 1
- Skipped: 1

## Details

### eq:energy ✓
- File: equations.py:45
- Tests: 3/3 passed
- Notation: φ_Ω → phi_patch, α̅ → alpha_bar_t

### eq:weights ✗
- File: equations.py:67
- Tests: 1/2 failed
- Error: Test 2 expected [0.5, 0.5], got [0.499, 0.501]
```
