# LaTeX-Code Sync Skill

Keep paper equations synchronized with code implementations. Ensures LaTeX notation in academic papers matches the actual Python/PyTorch implementations through decorator-based linking and automated verification.

## Philosophy

The core problem: **Notation drift**. Paper says `β = ∫v_t dt`, code says `beta = sum(v_t) * dt`. Six months later, you change the code and forget to update the paper. Reviewer #2 notices.

Solution: Explicit linking via decorators + CI verification.

```python
@latex("eq:beta-def", notation={"beta": r"\beta"})
def compute_beta(v_t_values, dt):
    return sum(v_t_values) * dt
```

## When to Use

| Use Case | Trigger |
|----------|---------|
| **New paper** | "Set up equation verification for my paper" |
| **Existing project** | "Link my code implementations to paper equations" |
| **Pre-submission** | "Verify all equations match between paper and code" |
| **Post-review** | "Check if code changes broke paper consistency" |
| **Handoff** | "Document which functions implement which equations" |

## Available Commands

| Command | Description |
|---------|-------------|
| `/latex-sync-setup` | Initialize latex-code-sync in a project |
| `/latex-sync-annotate` | Add @latex decorators to existing functions |
| `/latex-sync-verify` | Run verification between paper and code |
| `/latex-sync-report` | Generate equation-code mapping report |
| `/latex-sync-ci` | Set up CI workflow for cross-repo verification |

## Quick Start

### 1. Install
```bash
pip install latex-code-sync
# or
uv add latex-code-sync
```

### 2. Annotate Functions
```python
from latex_code_sync import latex

@latex(
    "eq:mse",
    notation={"y": "y", "y_hat": r"\hat{y}"},
    test_cases=[
        {"inputs": {"y": [1,2], "y_hat": [1,2]}, "expected": 0.0},
    ]
)
def mse_loss(y, y_hat):
    return torch.mean((y - y_hat) ** 2)
```

### 3. Verify
```bash
latex-code-sync verify --latex-dir=paper/ --modules=equations
```

## Workflow Patterns

### Pattern A: Monorepo (paper + code together)
```
my-project/
├── paper/
│   └── main.tex          # \label{eq:loss}
├── src/
│   └── equations.py      # @latex("eq:loss")
└── pyproject.toml        # latex-code-sync in dev deps
```

### Pattern B: Separate Repos with Cross-Repo CI
```yaml
# .github/workflows/verify-equations.yml
- uses: actions/checkout@v4  # Code repo
- uses: actions/checkout@v4
  with:
    repository: user/paper-repo
    path: paper
- run: latex-code-sync verify --latex-dir=paper/ --modules=equations
```

### Pattern C: Overleaf + GitHub Code
```
# Clone paper from Overleaf Git sync
git clone https://git.overleaf.com/PROJECT_ID paper
latex-code-sync verify --latex-dir=paper/ --modules=equations
```

## Annotation Reference

### Basic Linking
```python
@latex("eq:energy")
def compute_energy(x):
    return x ** 2
```

### With Notation Mapping
```python
@latex(
    "eq:gradient",
    notation={
        "params": r"\theta",
        "loss": r"\mathcal{L}",
        "learning_rate": r"\eta",
    }
)
def gradient_step(params, loss, learning_rate):
    return params - learning_rate * grad(loss, params)
```

### With Test Cases
```python
@latex(
    "eq:softmax",
    test_cases=[
        {"inputs": {"x": [0, 0, 0]}, "expected": [1/3, 1/3, 1/3]},
        {"inputs": {"x": [1000, 0, 0]}, "expected": [1.0, 0.0, 0.0]},
    ]
)
def softmax(x):
    exp_x = torch.exp(x - x.max())
    return exp_x / exp_x.sum()
```

### With Dependencies
```python
@latex("eq:elbo", depends=["eq:kl", "eq:reconstruction"])
def elbo(x, z, mu, sigma):
    return reconstruction(x, z) - kl_divergence(mu, sigma)
```

## Verification Strategies

| Strategy | When to Use | Example |
|----------|-------------|---------|
| `test_cases` | Explicit input/output pairs | Loss functions |
| `properties` | Property-based testing | "output >= 0" |
| `roundtrip` | Symbolic equivalence | Simple math expressions |
| `none` | Just link, no verification | Complex implementations |

## CI Integration

### GitHub Actions (Cross-Repo)
```yaml
name: Verify Equations
on: [push, pull_request]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/checkout@v4
        with:
          repository: owner/paper-repo
          path: paper
      - run: pip install -e ".[verify]"
      - run: latex-code-sync verify --latex-dir=paper/ --modules=equations --strict
```

### Pre-commit Hook
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: latex-code-sync
        name: Verify equations
        entry: latex-code-sync verify --latex-dir=paper/ --modules=equations
        language: system
        pass_filenames: false
```

## Configuration

### pyproject.toml
```toml
[project.optional-dependencies]
verify = ["latex-code-sync>=0.1.0"]
```

### latex-code-sync.toml
```toml
[latex-code-sync]
latex_dir = "paper/"
modules = ["equations", "models.loss"]
strict = true

[paper]
repository = "user/paper-repo"
branch = "main"
```

## CLI Reference

```bash
# Verify all equations
latex-code-sync verify --latex-dir=paper/ --modules=equations

# Strict mode (fail on any mismatch)
latex-code-sync verify --latex-dir=paper/ --modules=equations --strict

# List all registered equations
latex-code-sync list --modules=equations

# Check for unlabeled equations in LaTeX
latex-code-sync check-labels --latex-dir=paper/

# Generate mapping report
latex-code-sync report --latex-dir=paper/ --modules=equations --output=mapping.md
```

## Troubleshooting

### "Label not found in LaTeX"
- Check label spelling: `\label{eq:loss}` vs `eq:Loss`
- Ensure label is in `.tex` files, not just comments
- Check all input files (`\input{sections/methods}`)

### "Function not registered"
- Import the module before verification
- Check decorator syntax: `@latex("eq:x")` not `@latex(eq:x)`

### "Test case failed"
- Numerical precision: use `torch.allclose()` with tolerance
- Shape mismatches: ensure test inputs have correct dimensions

## Integration with Existing Workflows

### With Hydra Configs
```python
@latex_config("training.learning_rate", r"\eta")
def get_lr(cfg):
    return cfg.training.learning_rate
```

### With W&B Logging
```python
# Log equation parameters alongside metrics
wandb.config.update({
    "beta": compute_beta(),  # Links to eq:beta-def
})
```

## License

MIT
