---
name: latex-sync-annotate
description: Add @latex decorators to existing functions to link them with paper equations. Use when asked to "annotate functions", "link functions to equations", "add equation decorators", or "connect code to LaTeX".
model: sonnet
metadata:
  research-domain: general
  research-phase: implementation
  task-type: analysis
  verification-level: none
---

# Annotate Functions with LaTeX Links

> **LLM-required**: Linking code functions to paper equations requires understanding mathematical semantics. No script alternative.

Add `@latex` decorators to existing Python functions to create verified links between code implementations and paper equations.

## Annotation Workflow

1. **Identify function**: Find the Python function implementing an equation
2. **Match equation**: Locate the corresponding `\label{eq:...}` in LaTeX
3. **Map notation**: Connect Python parameters to LaTeX symbols
4. **Add test cases**: Provide verification inputs/outputs
5. **Apply decorator**: Add `@latex(...)` above function

## Decorator Syntax

### Minimal
```python
@latex("eq:loss")
def compute_loss(y, y_hat):
    return torch.mean((y - y_hat) ** 2)
```

### With Notation Mapping
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

### With Test Cases
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

### With Dependencies
```python
@latex(
    "eq:elbo",
    depends=["eq:kl-divergence", "eq:reconstruction"],
    description="Evidence lower bound combines KL and reconstruction terms",
)
def elbo(x, z, mu, logvar):
    return reconstruction_loss(x, z) - kl_divergence(mu, logvar)
```

### Without Verification
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

## Common Notation Mappings

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

## Test Case Strategies

### Numerical Functions
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

### Loss Functions
```python
test_cases=[
    # Perfect prediction = zero loss
    {"inputs": {"y": t([1,2,3]), "y_hat": t([1,2,3])}, "expected": 0.0},
    # Known error
    {"inputs": {"y": t([0.0]), "y_hat": t([1.0])}, "expected": 1.0},
]
```

### Probability Functions
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

## Batch Annotation Example

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

## Checklist for Each Annotation

- [ ] Label matches exactly: `eq:energy` not `eq:Energy`
- [ ] Notation maps all key parameters
- [ ] At least one test case (unless `verify="none"`)
- [ ] Dependencies listed if function calls other annotated functions
- [ ] Description matches paper context
- [ ] Function docstring explains the equation
