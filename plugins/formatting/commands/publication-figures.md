---
name: publication-figures
description: Create publication-ready figures for ML conferences (NeurIPS, ICML, ICLR, AAAI) using matplotlib/seaborn with LaTeX typography. Use when asked to "create plots", "make figures publication ready", "format for conference", "style matplotlib", or "improve figure quality".
model: haiku
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: formatting
  verification-level: heuristic
---

# Publication-Ready Figures

> **Script-first**: This skill generates figures via matplotlib/seaborn scripts. LLM assists only with choosing plot types and interpreting data.

Generate matplotlib/seaborn figures meeting ML conference standards.

## Quick Setup

```python
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def setup_publication_style():
    """Configure matplotlib for ML conference figures."""
    plt.rcParams.update({
        # LaTeX rendering
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["Computer Modern Roman"],

        # Figure size (column width for NeurIPS/ICML)
        "figure.figsize": (3.25, 2.5),  # Single column
        "figure.dpi": 150,

        # Font sizes
        "font.size": 8,
        "axes.titlesize": 9,
        "axes.labelsize": 8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 7,

        # Line widths
        "axes.linewidth": 0.5,
        "grid.linewidth": 0.3,
        "lines.linewidth": 1.0,
        "lines.markersize": 3,

        # Remove top/right spines
        "axes.spines.top": False,
        "axes.spines.right": False,

        # Grid
        "axes.grid": True,
        "grid.alpha": 0.3,

        # Tight layout
        "figure.constrained_layout.use": True,

        # Save settings
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
    })

setup_publication_style()
```

## Conference Specifications

| Venue | Column width | Full width | Max height |
|-------|-------------|------------|------------|
| NeurIPS | 3.25 in | 6.75 in | 9 in |
| ICML | 3.25 in | 6.75 in | 9 in |
| ICLR | 3.25 in | 6.75 in | 9 in |
| AAAI | 3.3 in | 7 in | 9.5 in |

## Color Palettes

```python
# Colorblind-safe palette (preferred)
COLORS = {
    "blue": "#0072B2",
    "orange": "#E69F00",
    "green": "#009E73",
    "red": "#D55E00",
    "purple": "#CC79A7",
    "cyan": "#56B4E9",
    "yellow": "#F0E442",
}

# Sequential for heatmaps
SEQUENTIAL = "viridis"  # or "cividis" for colorblind safety

# Diverging for difference plots
DIVERGING = "RdBu_r"
```

## Common Figure Types

### Line plot with confidence intervals

```python
def plot_learning_curve(results: dict, save_path: Path):
    """Plot learning curves with std shading."""
    fig, ax = plt.subplots()

    for name, data in results.items():
        mean = data["mean"]
        std = data["std"]
        steps = data["steps"]

        ax.plot(steps, mean, label=name)
        ax.fill_between(steps, mean - std, mean + std, alpha=0.2)

    ax.set_xlabel("Training Steps")
    ax.set_ylabel("Accuracy")
    ax.legend(frameon=False)

    fig.savefig(save_path, format="pdf")
    plt.close(fig)
```

### Bar chart with error bars

```python
def plot_comparison(methods: list, scores: list, errors: list, save_path: Path):
    """Bar chart comparing methods."""
    fig, ax = plt.subplots()

    x = range(len(methods))
    bars = ax.bar(x, scores, yerr=errors, capsize=2, width=0.6,
                  color=list(COLORS.values())[:len(methods)], edgecolor="black", linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(methods)
    ax.set_ylabel("Score")

    # Add value labels
    for bar, score in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{score:.2f}", ha="center", va="bottom", fontsize=6)

    fig.savefig(save_path, format="pdf")
    plt.close(fig)
```

### Heatmap/confusion matrix

```python
def plot_heatmap(matrix: np.ndarray, labels: list, save_path: Path):
    """Plot annotated heatmap."""
    fig, ax = plt.subplots(figsize=(3.25, 3.0))

    im = ax.imshow(matrix, cmap=SEQUENTIAL)

    # Ticks
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels)

    # Annotations
    for i in range(len(labels)):
        for j in range(len(labels)):
            color = "white" if matrix[i, j] > matrix.max()/2 else "black"
            ax.text(j, i, f"{matrix[i,j]:.2f}", ha="center", va="center",
                   color=color, fontsize=6)

    fig.colorbar(im, ax=ax, shrink=0.8)
    fig.savefig(save_path, format="pdf")
    plt.close(fig)
```

## LaTeX Typography

```python
# Math in labels
ax.set_xlabel(r"Learning rate $\alpha$")
ax.set_ylabel(r"Loss $\mathcal{L}(\theta)$")

# Method names
ax.legend([r"\textsc{Ours}", r"\textsc{Baseline}"])

# Bold for emphasis
ax.set_title(r"\textbf{Comparison}")
```

## Export Checklist

- [ ] PDF format for vector graphics
- [ ] Fonts embedded (use `text.usetex: True`)
- [ ] Colorblind-safe palette
- [ ] Readable at print size (check at 50% zoom)
- [ ] Legend doesn't overlap data
- [ ] Axis labels have units
- [ ] No title (use figure caption in paper instead)
- [ ] Consistent style across all figures

## Troubleshooting

**LaTeX errors**: Install texlive: `apt install texlive-latex-extra texlive-fonts-recommended dvipng cm-super`

**Font warnings**: Add `"text.latex.preamble": r"\usepackage{amsmath}\usepackage{amssymb}"`

**Tight margins cut off labels**: Use `plt.tight_layout(pad=0.5)` or increase `savefig.pad_inches`
