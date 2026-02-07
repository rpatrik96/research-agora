---
name: tikz-figures
description: |
  Create TikZ/PGF figures for ML papers including neural networks, flowcharts, diagrams, and graphs.
  Use when asked to "create TikZ figure", "draw neural network", "make diagram in LaTeX",
  "TikZ flowchart", or "create architecture diagram".
model: sonnet
---

# TikZ Figures for ML Papers

> **LLM-required**: Designing TikZ diagrams requires creative visual composition and understanding of the concepts being illustrated. No script alternative.

Create publication-ready vector diagrams using TikZ/PGF for ML conference submissions.

## When to Use TikZ

- Neural network architectures
- Method flowcharts and pipelines
- Causal graphs and Bayesian networks
- Algorithm visualizations
- Conceptual diagrams
- Coordinate systems and geometric illustrations

Prefer matplotlib/seaborn for data plots (learning curves, bar charts, heatmaps).

## Preamble Setup

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

## Color Palette (Colorblind-Safe)

```latex
% Colorblind-safe colors matching publication-figures
\definecolor{tikzblue}{HTML}{0072B2}
\definecolor{tikzorange}{HTML}{E69F00}
\definecolor{tikzgreen}{HTML}{009E73}
\definecolor{tikzred}{HTML}{D55E00}
\definecolor{tikzpurple}{HTML}{CC79A7}
\definecolor{tikzcyan}{HTML}{56B4E9}

% Semantic colors
\definecolor{inputcolor}{HTML}{56B4E9}
\definecolor{hiddencolor}{HTML}{0072B2}
\definecolor{outputcolor}{HTML}{D55E00}
\definecolor{annotationcolor}{HTML}{666666}
```

## Conference Sizing

```latex
% NeurIPS/ICML/ICLR column widths
\newlength{\figwidth}
\setlength{\figwidth}{3.25in}      % Single column
\newlength{\fullfigwidth}
\setlength{\fullfigwidth}{6.75in}  % Full width

% Usage in figure environment
\begin{figure}[t]
    \centering
    \resizebox{\columnwidth}{!}{%
        \input{figures/architecture.tikz}
    }
    \caption{\textbf{Model architecture.} Description.}
    \label{fig:architecture}
\end{figure}
```

## Common TikZ Styles

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

## Neural Network Diagrams

### Simple MLP

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

### Convolutional Layer

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

## Flowcharts and Pipelines

### Method Pipeline

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

### Branching Diagram

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

## Graphs and Networks

### Directed Acyclic Graph (Causal)

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

### Graphical Model with Plates

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

## Attention Mechanism

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

## Transformer Block

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

## Mathematical Illustrations

### Coordinate System

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

### Loss Landscape

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

## Best Practices

### Font Consistency
```latex
% Match document fonts in TikZ
\tikzset{every node/.style={font=\small}}

% Use same math macros as main document
\node {$\myvec{x} \in \reals^d$};
```

### Alignment
```latex
% Use positioning library for clean layouts
\node[right=of A] (B) {...};
\node[below=1cm of A] (C) {...};

% Or explicit coordinates
\node at (2, 1) (D) {...};
```

### Export as Standalone
```latex
% figures/architecture.tikz
\begin{tikzpicture}
    % ... figure content ...
\end{tikzpicture}

% In main document
\input{figures/architecture.tikz}
```

### Reusable Components
```latex
% Define in preamble
\newcommand{\neuronlayer}[3]{
    % #1: x position, #2: number of neurons, #3: color
    \foreach \i in {1,...,#2} {
        \node[neuron, fill=#3] at (#1, -\i) {};
    }
}
```

## Checklist

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

## Troubleshooting

**Package conflicts**: Load TikZ before hyperref.

**Slow compilation**: Use `\tikzexternalize` for complex figures:
```latex
\usetikzlibrary{external}
\tikzexternalize[prefix=tikz-cache/]
```

**Positioning issues**: Use `node distance` and `positioning` library instead of manual coordinates.

**Arrow tips not showing**: Ensure `arrows.meta` library is loaded and use `>=Stealth`.
