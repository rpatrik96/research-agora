---
name: figures
description: |
  Make publication figures for ML papers, in TikZ or matplotlib. Use when asked
  to "create a figure", "make a plot", "visualize results", "draw a neural
  network", "make a diagram in LaTeX", "TikZ flowchart", "architecture diagram",
  "publication figure", "style matplotlib", or "format figures for a
  conference". **tikz** draws diagrams whose content you describe; **plot**
  renders data you supply, read from real files rather than invented.
model: sonnet
disable-model-invocation: true
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: formatting
  verification-level: none
---

# Figures

Two renderers, one house style.

| They said | Mode |
|---|---|
| "draw", "diagram", "architecture", "flowchart", "graphical model" | **tikz** |
| "plot", "chart", "visualize these results", "style my matplotlib" | **plot** |

The palette and column widths below govern both. They were duplicated across
two skills until RFC-0002, with `figures` carrying the comment
`% Colorblind-safe colors matching figure-storyteller` — a sync between two
files maintained by hand. One table cannot drift from itself.

**`plot` never invents data.** Read the file the user points at, or ask for it.
A figure containing plausible numbers is a fabricated result.

## The palette

Wong's colorblind-safe eight. Both modes use these and nothing else, unless the
user names a specific journal scheme.

| Name | Hex | Typical use |
|---|---|---|
| black | `#000000` | text, axes, baseline series |
| orange | `#E69F00` | second series |
| sky | `#56B4E9` | inputs, third series |
| green | `#009E73` | success, fourth series |
| yellow | `#F0E442` | highlight, fifth series |
| blue | `#0072B2` | primary, hidden layers |
| red | `#D55E00` | outputs, error, ablation |
| pink | `#CC79A7` | sixth series |

```python
WONG = ['#000000', '#E69F00', '#56B4E9', '#009E73',
        '#F0E442', '#0072B2', '#D55E00', '#CC79A7']
```

```latex
\definecolor{tikzblack}{HTML}{000000}
\definecolor{tikzorange}{HTML}{E69F00}
\definecolor{tikzsky}{HTML}{56B4E9}
\definecolor{tikzgreen}{HTML}{009E73}
\definecolor{tikzyellow}{HTML}{F0E442}
\definecolor{tikzblue}{HTML}{0072B2}
\definecolor{tikzred}{HTML}{D55E00}
\definecolor{tikzpink}{HTML}{CC79A7}

% Semantic aliases for network diagrams
\colorlet{inputcolor}{tikzsky}
\colorlet{hiddencolor}{tikzblue}
\colorlet{outputcolor}{tikzred}
\definecolor{annotationcolor}{HTML}{666666}
```

## Column widths

| Venue | Text width | Column width | Layout |
|---|---|---|---|
| NeurIPS / ICML / ICLR | 5.5in | 5.5in | single column |
| CVPR / ICCV | 7.0in | 3.25in | two column |
| AAAI | 7.0in | 3.3in | two column |
| ACL | 6.3in | 3.05in | two column |

Export vector PDF, never raster, unless the figure contains a photograph.

---

## Mode: tikz

> **LLM-required**: Designing TikZ diagrams requires creative visual composition and understanding of the concepts being illustrated. No script alternative.

Create publication-ready vector diagrams using TikZ/PGF for ML conference submissions.

### When to Use TikZ

- Neural network architectures
- Method flowcharts and pipelines
- Causal graphs and Bayesian networks
- Algorithm visualizations
- Conceptual diagrams
- Coordinate systems and geometric illustrations

Prefer matplotlib/seaborn for data plots (learning curves, bar charts, heatmaps).

### Preamble Setup

```latex
\usepackage{tikz}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}

% Essential TikZ libraries
\usetikzlibrary{
    arrows.meta,        % Modern arrow tips
    positioning,        % Relative positioning
    shapes.geometric,   % Rectangles, circles, etc.
    shapes.misc,        % Rounded rectangles
    fit,                % Fit nodes around others
    backgrounds,        % Background layers
    calc,               % Coordinate calculations
    decorations.pathreplacing,  % Braces
    patterns,           % Fill patterns
    matrix,             % Matrix of nodes
    chains,             % Sequential nodes
}

% Optional: for neural network diagrams
\usetikzlibrary{3d}
```

### Common TikZ Styles

```latex
\tikzset{
    % Node styles
    block/.style={
        rectangle, draw, rounded corners=2pt,
        minimum height=2em, minimum width=3em,
        fill=white, line width=0.5pt
    },
    neuron/.style={
        circle, draw, minimum size=1.5em,
        fill=white, line width=0.5pt
    },
    operation/.style={
        circle, draw, minimum size=1.2em,
        fill=gray!20, line width=0.5pt,
        font=\scriptsize
    },
    % Arrow styles
    arrow/.style={
        ->, >=Stealth, line width=0.5pt
    },
    dataarrow/.style={
        ->, >=Stealth, line width=0.8pt, tikzblue
    },
    % Text styles
    annot/.style={
        font=\footnotesize, text=annotationcolor
    },
    mathlabel/.style={
        font=\small
    },
}
```

### Neural Network Diagrams

#### Simple MLP

```latex
\begin{tikzpicture}[
    neuron/.style={circle, draw, minimum size=1.5em, line width=0.5pt},
    input neuron/.style={neuron, fill=inputcolor!30},
    hidden neuron/.style={neuron, fill=hiddencolor!30},
    output neuron/.style={neuron, fill=outputcolor!30},
]
    % Input layer
    \foreach \i in {1,...,3} {
        \node[input neuron] (I\i) at (0, -\i) {};
    }

    % Hidden layer
    \foreach \i in {1,...,4} {
        \node[hidden neuron] (H\i) at (2, -\i + 0.5) {};
    }

    % Output layer
    \foreach \i in {1,...,2} {
        \node[output neuron] (O\i) at (4, -\i - 0.5) {};
    }

    % Connections
    \foreach \i in {1,...,3} {
        \foreach \j in {1,...,4} {
            \draw[->] (I\i) -- (H\j);
        }
    }
    \foreach \i in {1,...,4} {
        \foreach \j in {1,...,2} {
            \draw[->] (H\i) -- (O\j);
        }
    }

    % Labels
    \node[annot, above=0.5em of I1] {Input};
    \node[annot, above=0.5em of H1] {Hidden};
    \node[annot, above=0.5em of O1] {Output};
\end{tikzpicture}
```

#### Convolutional Layer

```latex
\begin{tikzpicture}[
    cube/.style={draw, thick, fill=tikzblue!20},
]
    % Input tensor
    \draw[cube] (0,0) rectangle (1,2);
    \draw[cube] (0.1,0.1) rectangle (1.1,2.1);
    \draw[cube] (0.2,0.2) rectangle (1.2,2.2);
    \node[below] at (0.6,0) {\scriptsize $H \times W \times C$};

    % Arrow
    \draw[->, >=Stealth, thick] (1.5,1) -- (2.5,1)
        node[midway, above] {\scriptsize Conv};

    % Output tensor
    \draw[cube, fill=tikzorange!20] (3,0.2) rectangle (3.8,1.8);
    \draw[cube, fill=tikzorange!20] (3.1,0.3) rectangle (3.9,1.9);
    \draw[cube, fill=tikzorange!20] (3.2,0.4) rectangle (4.0,2.0);
    \draw[cube, fill=tikzorange!20] (3.3,0.5) rectangle (4.1,2.1);
    \node[below] at (3.6,0.2) {\scriptsize $H' \times W' \times C'$};
\end{tikzpicture}
```

### Flowcharts and Pipelines

#### Method Pipeline

```latex
\begin{tikzpicture}[
    node distance=1.5cm,
    block/.style={rectangle, draw, rounded corners,
                  minimum height=2.5em, minimum width=4em,
                  fill=white, line width=0.5pt, align=center},
    arrow/.style={->, >=Stealth, line width=0.6pt},
]
    % Nodes
    \node[block, fill=inputcolor!20] (input) {Input\\$\myvec{x}$};
    \node[block, fill=hiddencolor!20, right=of input] (encoder) {Encoder\\$f_\theta$};
    \node[block, fill=hiddencolor!20, right=of encoder] (latent) {Latent\\$\myvec{z}$};
    \node[block, fill=hiddencolor!20, right=of latent] (decoder) {Decoder\\$g_\phi$};
    \node[block, fill=outputcolor!20, right=of decoder] (output) {Output\\$\hat{\myvec{x}}$};

    % Arrows
    \draw[arrow] (input) -- (encoder);
    \draw[arrow] (encoder) -- (latent);
    \draw[arrow] (latent) -- (decoder);
    \draw[arrow] (decoder) -- (output);

    % Loss annotation
    \draw[arrow, dashed, tikzred] (output) -- ++(0,-1) -| (input)
        node[pos=0.25, below] {\scriptsize $\mathcal{L}_\text{recon}$};
\end{tikzpicture}
```

#### Branching Diagram

```latex
\begin{tikzpicture}[
    node distance=1cm and 2cm,
    block/.style={rectangle, draw, rounded corners,
                  minimum height=2em, minimum width=5em,
                  fill=white, line width=0.5pt},
    arrow/.style={->, >=Stealth},
]
    \node[block] (input) {Input};
    \node[block, above right=of input] (branch1) {Branch A};
    \node[block, below right=of input] (branch2) {Branch B};
    \node[block, right=2cm of input] (merge) {Merge};

    \draw[arrow] (input) -- (branch1);
    \draw[arrow] (input) -- (branch2);
    \draw[arrow] (branch1) -- (merge);
    \draw[arrow] (branch2) -- (merge);
\end{tikzpicture}
```

### Graphs and Networks

#### Directed Acyclic Graph (Causal)

```latex
\begin{tikzpicture}[
    node distance=1.5cm,
    var/.style={circle, draw, minimum size=2em, line width=0.5pt},
    observed/.style={var, fill=gray!20},
    latent/.style={var, fill=white},
    arrow/.style={->, >=Stealth, line width=0.5pt},
]
    % Nodes
    \node[latent] (Z) {$Z$};
    \node[observed, below left=of Z] (X) {$X$};
    \node[observed, below right=of Z] (Y) {$Y$};

    % Edges
    \draw[arrow] (Z) -- (X);
    \draw[arrow] (Z) -- (Y);
    \draw[arrow] (X) -- (Y);
\end{tikzpicture}
```

#### Graphical Model with Plates

```latex
\begin{tikzpicture}[
    var/.style={circle, draw, minimum size=1.8em, line width=0.5pt},
    observed/.style={var, fill=gray!20},
    latent/.style={var},
    plate/.style={draw, rectangle, rounded corners,
                  inner sep=0.3cm, fit=#1},
    arrow/.style={->, >=Stealth},
]
    % Variables
    \node[latent] (theta) {$\theta$};
    \node[latent, below=of theta] (z) {$z_n$};
    \node[observed, below=of z] (x) {$x_n$};

    % Plate
    \node[plate=(z)(x), label=below right:$N$] {};

    % Edges
    \draw[arrow] (theta) -- (z);
    \draw[arrow] (z) -- (x);
\end{tikzpicture}
```

### Attention Mechanism

```latex
\begin{tikzpicture}[
    box/.style={rectangle, draw, minimum width=2em, minimum height=1.5em,
                line width=0.5pt},
    matmul/.style={circle, draw, minimum size=1.5em, fill=gray!10,
                   font=\scriptsize},
]
    % Q, K, V boxes
    \node[box, fill=tikzblue!20] (Q) {$Q$};
    \node[box, fill=tikzorange!20, right=1cm of Q] (K) {$K$};
    \node[box, fill=tikzgreen!20, right=1cm of K] (V) {$V$};

    % MatMul nodes
    \node[matmul, below=1cm of $(Q)!0.5!(K)$] (mm1) {$\times$};
    \node[matmul, below=0.8cm of mm1] (scale) {$\div$};
    \node[box, below=0.8cm of scale, fill=tikzpurple!20] (soft) {Softmax};
    \node[matmul, below=0.8cm of soft] (mm2) {$\times$};
    \node[box, below=0.8cm of mm2, fill=outputcolor!20] (out) {Output};

    % Connections
    \draw[->] (Q) |- (mm1);
    \draw[->] (K) |- (mm1);
    \draw[->] (mm1) -- (scale) node[midway, right] {\scriptsize $\sqrt{d_k}$};
    \draw[->] (scale) -- (soft);
    \draw[->] (soft) -- (mm2);
    \draw[->] (V) |- (mm2);
    \draw[->] (mm2) -- (out);
\end{tikzpicture}
```

### Transformer Block

```latex
\begin{tikzpicture}[
    node distance=0.6cm,
    block/.style={rectangle, draw, minimum width=4cm, minimum height=1.5em,
                  rounded corners=2pt, line width=0.5pt},
    add/.style={circle, draw, minimum size=1.2em, font=\scriptsize},
]
    % Main blocks
    \node[block, fill=tikzblue!15] (attn) {Multi-Head Attention};
    \node[add, right=0.5cm of attn] (add1) {$+$};
    \node[block, fill=tikzorange!15, above=of attn] (norm1) {Layer Norm};
    \node[block, fill=tikzgreen!15, above=of norm1] (ffn) {Feed Forward};
    \node[add, right=0.5cm of ffn] (add2) {$+$};
    \node[block, fill=tikzorange!15, above=of ffn] (norm2) {Layer Norm};

    % Residual connections
    \draw[->] (attn) -- (add1);
    \draw[->] (add1) -- ++(0.5,0) |- (norm1);
    \draw[->] (norm1) -- (ffn);
    \draw[->] (ffn) -- (add2);
    \draw[->] (add2) -- ++(0.5,0) |- (norm2);

    % Skip connections
    \draw[->] (attn.south) -- ++(0,-0.3) -| (add1);
    \draw[->] (norm1.east) -| ([xshift=0.8cm]add1.north) -- (add2);
\end{tikzpicture}
```

### Mathematical Illustrations

#### Coordinate System

```latex
\begin{tikzpicture}
    \draw[->] (-0.5,0) -- (3,0) node[right] {$x$};
    \draw[->] (0,-0.5) -- (0,2.5) node[above] {$y$};

    % Function curve
    \draw[thick, tikzblue, domain=0:2.5, samples=50]
        plot (\x, {0.5*\x*\x}) node[right] {$f(x)$};

    % Point annotation
    \filldraw[tikzred] (1.5, 1.125) circle (2pt);
    \draw[dashed, tikzred] (1.5,0) -- (1.5, 1.125) -- (0, 1.125);
    \node[below] at (1.5, 0) {\scriptsize $x_0$};
\end{tikzpicture}
```

#### Loss Landscape

```latex
\begin{tikzpicture}
    \begin{axis}[
        width=5cm, height=4cm,
        view={45}{30},
        xlabel={$\theta_1$}, ylabel={$\theta_2$}, zlabel={$\mathcal{L}$},
        colormap/viridis,
    ]
    \addplot3[surf, samples=20, domain=-2:2]
        {x^2 + y^2 + 0.5*sin(deg(x*y))};
    \end{axis}
\end{tikzpicture}
```

### Best Practices

#### Font Consistency
```latex
% Match document fonts in TikZ
\tikzset{every node/.style={font=\small}}

% Use same math macros as main document
\node {$\myvec{x} \in \reals^d$};
```

#### Alignment
```latex
% Use positioning library for clean layouts
\node[right=of A] (B) {...};
\node[below=1cm of A] (C) {...};

% Or explicit coordinates
\node at (2, 1) (D) {...};
```

#### Export as Standalone
```latex
% figures/architecture.tikz
\begin{tikzpicture}
    % ... figure content ...
\end{tikzpicture}

% In main document
\input{figures/architecture.tikz}
```

#### Reusable Components
```latex
% Define in preamble
\newcommand{\neuronlayer}[3]{
    % #1: x position, #2: number of neurons, #3: color
    \foreach \i in {1,...,#2} {
        \node[neuron, fill=#3] at (#1, -\i) {};
    }
}
```

### Checklist

- [ ] Colorblind-safe palette used
- [ ] Font size readable at print scale (test at 50% zoom)
- [ ] Line widths consistent (0.5pt for details, 0.8pt for emphasis)
- [ ] Node sizes consistent across similar elements
- [ ] Math notation matches main document macros
- [ ] Arrows use modern `Stealth` tip
- [ ] Exported as PDF or included via `\input{}`
- [ ] No overlapping labels or elements
- [ ] White/light backgrounds for readability
- [ ] Positioned using `positioning` library (not manual coordinates)

### Troubleshooting

**Package conflicts**: Load TikZ before hyperref.

**Slow compilation**: Use `\tikzexternalize` for complex figures:
```latex
\usetikzlibrary{external}
\tikzexternalize[prefix=tikz-cache/]
```

**Positioning issues**: Use `node distance` and `positioning` library instead of manual coordinates.

**Arrow tips not showing**: Ensure `arrows.meta` library is loaded and use `>=Stealth`.

---

## Mode: plot

> **LLM-required**: Crafting figure narratives requires understanding visual communication. No script alternative.

You are a Figure Design Specialist - an expert in transforming research data into compelling visual narratives for ML publications. Your mission is to create figures that communicate findings clearly, meet publication standards (NeurIPS, ICML, ICLR), and remain accessible to all readers including those with color vision deficiencies.

**YOUR CORE MISSION:**
Transform raw experimental data and results into publication-ready figures that tell a clear story. You prioritize readability at print size, colorblind accessibility, and narrative clarity. Every figure you create should answer a specific question and guide the reader to the intended conclusion.

### WORKFLOW

1. **Understand the Narrative**: Ask what story the figure should tell. What is the one takeaway?
2. **Assess Data Type**: Determine whether data is categorical, continuous, time-series, or relational
3. **Select Figure Type**: Match data and narrative to the optimal visualization (see selection guide)
4. **Gather Data**: Read data files or accept inline data from the user
5. **Design Layout**: Plan panels, annotations, and visual hierarchy
6. **Apply Style**: Use publication-ready styling (conference-specific sizing, colorblind-safe palettes, LaTeX typography)
7. **Generate Code**: Write matplotlib/seaborn code with all styling applied using the setup template
8. **Create Figure**: Execute code and save as PDF for vector graphics
9. **Write Caption**: Draft a complete caption following the caption guide
10. **Verify Quality**: Run through the verification checklist before delivery

### PUBLICATION STYLE SETUP

Always begin figure generation with this setup function to ensure conference standards:

```python
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def setup_publication_style(venue="neurips"):
    """Configure matplotlib for ML conference figures.

    Args:
        venue: "neurips", "icml", "iclr", or "aaai" (default: neurips)
    """
    # Venue-specific sizing (see Conference Specifications below)
    sizes = {
        "neurips": (3.25, 2.5),
        "icml": (3.25, 2.5),
        "iclr": (3.25, 2.5),
        "aaai": (3.3, 2.5),
    }

    plt.rcParams.update({
        # LaTeX rendering
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["Computer Modern Roman"],

        # Figure size (single column)
        "figure.figsize": sizes.get(venue.lower(), (3.25, 2.5)),
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

# Call at the start of any figure generation
setup_publication_style()
```

### FIGURE TYPE SELECTION GUIDE

| Data Type | Narrative Goal | Recommended Figure |
|-----------|---------------|-------------------|
| Categorical comparison | Compare discrete groups | Bar chart with error bars |
| Continuous vs continuous | Show relationship | Scatter plot with regression |
| Time series / training | Show progression | Line plot (learning curves) |
| Matrix / correlations | Show pairwise relationships | Heatmap with annotations |
| Distribution | Show spread of values | Violin plot or histogram |
| Part-to-whole | Show proportions | Stacked bar (avoid pie charts) |
| Multiple metrics | Compare methods holistically | Radar/spider chart |
| Hierarchical | Show structure | Dendrogram or tree |
| High-dimensional | Show clusters/embeddings | t-SNE/UMAP scatter |
| Ablation study | Show component contributions | Grouped bar chart |

### MATPLOTLIB/SEABORN TEMPLATES

#### Bar Chart with Error Bars (Method Comparison)

```python
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# WONG: the eight hex values from the palette table above

def plot_method_comparison(methods, means, stds, metric_name, filename, venue="neurips"):
    """Bar chart comparing methods with error bars.

    Args:
        methods: List of method names
        means: List of mean values
        stds: List of standard deviations
        metric_name: Y-axis label
        filename: Output path (PDF recommended)
        venue: Target conference ("neurips", "icml", "iclr", "aaai")
    """
    # Apply publication style (handles figsize, fonts, etc.)
    setup_publication_style(venue=venue)

    fig, ax = plt.subplots()

    x = np.arange(len(methods))
    bars = ax.bar(x, means, yerr=stds, capsize=2, width=0.6,
                  color=WONG[1:len(methods)+1],
                  edgecolor='black', linewidth=0.5,
                  error_kw={'linewidth': 0.5})

    ax.set_xticks(x)
    ax.set_xticklabels(methods)
    ax.set_ylabel(metric_name)

    # Add value labels on bars
    for bar, mean, std in zip(bars, means, stds):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + std + 0.01,
                f'{mean:.2f}', ha='center', va='bottom', fontsize=6)

    fig.savefig(filename, format='pdf')
    plt.close(fig)
    return filename

# Example usage:
# plot_method_comparison(['Ours', 'Baseline A', 'Baseline B'],
#                        [0.85, 0.72, 0.68], [0.02, 0.03, 0.04],
#                        'Accuracy', 'comparison.pdf')
```

#### Learning Curves (Training Progress)

```python
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# WONG: the eight hex values from the palette table above

def plot_learning_curves(steps, curves_dict, ylabel, filename, venue="neurips", log_scale=False):
    """Plot training/validation curves for multiple methods.

    Args:
        steps: Array of x-axis values (epochs, steps, etc.)
        curves_dict: {'Method Name': {'mean': [...], 'std': [...]}, ...}
        ylabel: Y-axis label
        filename: Output path (PDF recommended)
        venue: Target conference
        log_scale: Use log scale for y-axis
    """
    setup_publication_style(venue=venue)

    fig, ax = plt.subplots()

    for idx, (name, data) in enumerate(curves_dict.items()):
        mean = np.array(data['mean'])
        std = np.array(data.get('std', np.zeros_like(mean)))
        color = WONG[idx % len(WONG)]

        ax.plot(steps, mean, label=name, color=color)
        ax.fill_between(steps, mean - std, mean + std, alpha=0.2, color=color)

    ax.set_xlabel('Training Steps')
    ax.set_ylabel(ylabel)
    if log_scale:
        ax.set_yscale('log')
    ax.legend(frameon=False, loc='best')

    fig.savefig(filename, format='pdf')
    plt.close(fig)
    return filename

# Example usage:
# steps = np.arange(0, 10000, 100)
# curves = {'Ours': {'mean': [...], 'std': [...]}, 'Baseline': {'mean': [...], 'std': [...]}}
# plot_learning_curves(steps, curves, 'Validation Loss', 'learning_curves.pdf', log_scale=True)
```

#### Heatmap (Correlation/Confusion Matrix)

```python
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def plot_heatmap(matrix, labels, filename, venue="neurips", cmap='viridis'):
    """Plot annotated heatmap for correlation or confusion matrices.

    Args:
        matrix: 2D numpy array
        labels: List of labels for both axes
        filename: Output path (PDF recommended)
        venue: Target conference
        cmap: Colormap ('viridis', 'cividis' for sequential; 'RdBu_r' for diverging)
    """
    setup_publication_style(venue=venue)

    # Square figure for matrices
    sizes = {"neurips": 3.25, "icml": 3.25, "iclr": 3.25, "aaai": 3.3}
    size = sizes.get(venue.lower(), 3.25)
    fig, ax = plt.subplots(figsize=(size, size))

    im = ax.imshow(matrix, cmap=cmap, aspect='auto')

    # Ticks and labels
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_yticklabels(labels)

    # Annotations
    for i in range(len(labels)):
        for j in range(len(labels)):
            color = 'white' if matrix[i, j] > matrix.max()/2 else 'black'
            ax.text(j, i, f'{matrix[i,j]:.2f}',
                   ha='center', va='center', color=color, fontsize=6)

    fig.colorbar(im, ax=ax, shrink=0.8)
    fig.savefig(filename, format='pdf')
    plt.close(fig)
    return filename

# Example usage:
# matrix = np.random.rand(5, 5)
# labels = ['A', 'B', 'C', 'D', 'E']
# plot_heatmap(matrix, labels, 'heatmap.pdf', cmap='viridis')
```

#### Scatter Plot with Regression

```python
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from pathlib import Path

# WONG: the eight hex values from the palette table above

def plot_scatter_regression(x, y, xlabel, ylabel, filename, venue="neurips", groups=None, group_labels=None):
    """Scatter plot with optional grouping and regression line.

    Args:
        x, y: Data arrays
        xlabel, ylabel: Axis labels
        filename: Output path (PDF recommended)
        venue: Target conference
        groups: Optional array of group assignments
        group_labels: Labels for each group
    """
    setup_publication_style(venue=venue)

    # Square-ish figure for scatter plots
    sizes = {"neurips": (3.25, 3.0), "icml": (3.25, 3.0), "iclr": (3.25, 3.0), "aaai": (3.3, 3.0)}
    fig, ax = plt.subplots(figsize=sizes.get(venue.lower(), (3.25, 3.0)))

    if groups is None:
        ax.scatter(x, y, alpha=0.6, s=20, color=WONG[1], edgecolor='white', linewidth=0.3)
        # Add regression line
        slope, intercept, r, p, se = stats.linregress(x, y)
        x_line = np.linspace(min(x), max(x), 100)
        ax.plot(x_line, slope * x_line + intercept, color=WONG[0],
                label=f'$R^2$={r**2:.3f}')
    else:
        for idx, (grp, label) in enumerate(zip(np.unique(groups), group_labels)):
            mask = groups == grp
            ax.scatter(x[mask], y[mask], alpha=0.6, s=20, color=WONG[idx+1],
                      edgecolor='white', linewidth=0.3, label=label)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False)

    fig.savefig(filename, format='pdf')
    plt.close(fig)
    return filename

# Example usage:
# x, y = np.random.rand(50), np.random.rand(50) * 2 + np.random.rand(50)
# plot_scatter_regression(x, y, 'Model Size (M params)', 'Accuracy (\%)', 'scatter.pdf')
```

### TYPOGRAPHY SETTINGS

#### LaTeX Integration for Publication Quality (Recommended)

Use the `setup_publication_style()` function above, which automatically configures LaTeX rendering. For manual control:

```python
import matplotlib.pyplot as plt

# Enable LaTeX rendering (requires LaTeX installation)
plt.rcParams.update({
    'text.usetex': True,
    'font.family': 'serif',
    'font.serif': ['Computer Modern Roman'],
    'font.size': 8,           # Conference standard
    'axes.labelsize': 8,
    'axes.titlesize': 9,
    'legend.fontsize': 7,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'figure.dpi': 150,        # Preview
    'savefig.dpi': 300,       # Publication
    'savefig.format': 'pdf',
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.02,
})
```

#### LaTeX Typography in Labels

```python
# Math in labels
ax.set_xlabel(r"Learning rate $\alpha$")
ax.set_ylabel(r"Loss $\mathcal{L}(\theta)$")

# Method names with small caps
ax.legend([r"\textsc{Ours}", r"\textsc{Baseline}"])

# Bold for emphasis
ax.set_title(r"\textbf{Comparison}")
```

#### Non-LaTeX Fallback (Faster, for rapid prototyping)

```python
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'font.size': 8,
    'mathtext.fontset': 'dejavusans',
})
```

#### Figure Sizing for Two-Column Papers

| Figure Type | Width (inches) | Height (inches) | Use Case |
|-------------|---------------|-----------------|----------|
| Single column | 3.25-3.5 | 2.5-3.0 | Standard plots |
| Full width | 6.75-7.0 | 3.0-4.0 | Multi-panel figures |
| Square (heatmap) | 3.25-3.5 | 3.0-3.5 | Matrices, correlations |

**Note:** Use exact conference specifications from the table above when possible.

### CAPTION WRITING GUIDE

#### Caption Structure

1. **Title sentence**: What the figure shows (bold or italicized in paper)
2. **Description**: How to read the figure, what each element represents
3. **Key finding**: The main takeaway (may reference specific values)
4. **Details**: Error bars, number of runs, statistical tests if applicable

#### Caption Template

```
**[Figure Type] showing [main relationship/comparison].** [Description of axes,
colors, markers]. [Key finding with specific numbers]. [Methodology note:
"Error bars show standard deviation across N=5 runs" or "Shaded regions
indicate 95% confidence intervals"].
```

#### Example Captions

**Good:**
> **Comparison of validation accuracy across methods.** Our method (orange)
> achieves 85.2% accuracy compared to Baseline A (blue, 72.1%) and Baseline B
> (green, 68.4%). Error bars indicate standard deviation across 5 random seeds.
> All differences are statistically significant (p < 0.01, paired t-test).

**Bad:**
> Figure 1. Results.

#### Caption Checklist

- [ ] Starts with what the figure shows
- [ ] Explains all visual encodings (colors, markers, line styles)
- [ ] States key numerical findings
- [ ] Documents error bars or confidence intervals
- [ ] Mentions statistical significance if claiming differences
- [ ] Self-contained (reader can understand without main text)

### OUTPUT FORMAT

When delivering a figure, provide:

```markdown
## Figure: [Descriptive Title]

### Narrative
[1-2 sentences: What story does this figure tell?]

### Code
[Complete Python code to generate the figure]

### Generated Files
- `[filename].pdf` - Vector graphics for publication
- `[filename].png` - Preview image (300 DPI)

### Suggested Caption
[Complete caption following the caption guide]

### Integration Notes
- LaTeX: `\includegraphics[width=\columnwidth]{figures/[filename]}`
- Recommended placement: [Section suggestion]
```

### MCP INTEGRATION

Use filesystem tools to manage figure files:


**Workflow:**
1. Read data files from the project
2. Generate and execute plotting code
3. Save figures to `figures/` directory
4. Provide LaTeX inclusion code

### EXPORT CHECKLIST

Before delivering any figure, verify all items:

#### Publication Quality
- [ ] **PDF format** for vector graphics (never raster for line plots/bar charts)
- [ ] **Fonts embedded** (use `text.usetex: True`)
- [ ] **300 DPI** for raster elements (if any)
- [ ] **Colorblind-safe palette** (Wong primary colors or viridis/cividis)
- [ ] **Readable at print size** (check at 50% zoom in PDF viewer)
- [ ] **No title** in the figure itself (use caption in paper instead)
- [ ] **Consistent style** across all figures in the paper

#### Readability
- [ ] Readable at target size (single column = 3.25 inches wide)
- [ ] Axis labels and tick marks are legible (minimum 7pt font)
- [ ] Legend does not obscure data
- [ ] All text is horizontal or at 45° max (no vertical text)

#### Accessibility
- [ ] Colorblind-safe palette used (Wong or viridis/cividis)
- [ ] Colors supplemented with markers or patterns when needed
- [ ] Sufficient contrast between elements
- [ ] Would be interpretable in grayscale

#### Technical Quality
- [ ] Vector format (PDF) for publication
- [ ] Appropriate aspect ratio for the data
- [ ] No chartjunk (unnecessary gridlines, 3D effects, shadows)
- [ ] Top/right spines removed (cleaner look)

#### Data Integrity
- [ ] Error bars or confidence intervals shown where applicable
- [ ] Axes start at appropriate values (not misleading)
- [ ] Sample sizes documented in caption
- [ ] Statistical significance noted for comparisons
- [ ] Units specified in axis labels

#### Publication Standards
- [ ] Meets venue figure guidelines (see Conference Specifications)
- [ ] Font matches paper (Computer Modern Roman for LaTeX papers)
- [ ] Resolution sufficient (300 DPI minimum)
- [ ] Caption is complete and self-contained
- [ ] Axis labels have units where applicable

#### Troubleshooting

**LaTeX errors**: Install texlive
```bash
# Ubuntu/Debian
apt install texlive-latex-extra texlive-fonts-recommended dvipng cm-super

# macOS
brew install --cask mactex
```

**Font warnings**: Add preamble to rcParams
```python
plt.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}\usepackage{amssymb}'
```

**Tight margins cut off labels**: Increase padding
```python
plt.savefig('figure.pdf', bbox_inches='tight', pad_inches=0.05)
```

### IMPORTANT PRINCIPLES

1. **One figure, one message**: Every figure should answer exactly one question
2. **Data-ink ratio**: Maximize data, minimize decoration
3. **Accessibility first**: Design for colorblind readers from the start
4. **Print-ready**: Design for grayscale printing even if color is available
5. **Reproducible**: Always provide complete code that regenerates the figure
6. **Context-aware**: Match the visual style to the target venue
7. **Story-driven**: Design the narrative first, then choose the visualization
8. **Publication-ready from start**: Apply conference styling from the beginning (use `setup_publication_style()`)

### INTEGRATED WORKFLOW: NARRATIVE + PUBLICATION QUALITY

This agent combines two complementary strengths:

1. **Narrative Design** (existing workflow): Understanding what story the figure tells and selecting the right visualization to communicate it clearly
2. **Publication Styling** (absorbed from publication-figures): Applying conference-specific formatting, colorblind-safe palettes, LaTeX typography, and proper sizing

**Execute both aspects together:**
- Start with narrative (what's the takeaway?)
- Match data to visualization type
- Apply `setup_publication_style(venue="neurips")` immediately
- Use Wong palette for categorical data, viridis/cividis for sequential
- Generate figures that are both scientifically compelling AND publication-ready

Your goal is to transform data into visual stories that enhance the reader's understanding. A great figure should be immediately comprehensible, memorable, and ready for submission without additional formatting.
