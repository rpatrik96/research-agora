---
name: paper-experiments
description: Write experimental details sections for ML papers with GitHub repository integration. Use when asked to "write experiments section", "document experimental setup", "describe methodology", "write reproducibility details", or "experimental details". Extracts information from code to ensure accuracy.
model: sonnet
metadata:
  research-domain: general
  research-phase: implementation
  task-type: writing
  verification-level: heuristic
---

# Experimental Details Section

Generate comprehensive experimental details for ML conference papers (NeurIPS, ICML, ICLR) by extracting information from the associated GitHub repository.

> **Hybrid**: All parameter extraction from configs and code is done via scripts (grep/find/python one-liners). LLM is used only to compose the extracted data into LaTeX prose.

## Workflow

1. **Script: Discover and extract** - Find configs, parse hyperparameters, model definitions
2. **Script: Collect all values** - Produce structured summary of all experimental parameters
3. **LLM: Write LaTeX** - Compose extracted values into experimental section prose

## Step 1: Automated Extraction (Script)

Run this comprehensive extraction script on the code repository:

```bash
REPO_DIR="."  # Set to code repository path

echo "=== Configuration Files ==="
find "$REPO_DIR" \( -name "*.yaml" -o -name "*.yml" -o -name "*.json" \) | grep -v node_modules | head -20

echo "=== Training Hyperparameters ==="
grep -rn "learning_rate\|lr\|batch_size\|epochs\|weight_decay\|warmup" --include="*.py" --include="*.yaml" "$REPO_DIR"

echo "=== Model Architecture ==="
grep -rn "class.*Model\|class.*Network\|nn.Module\|hidden\|n_layer\|num_head\|dropout" --include="*.py" "$REPO_DIR"

echo "=== Optimizer ==="
grep -rn "optim\.\|Adam\|SGD\|AdamW\|scheduler\|CosineAnnealing\|StepLR" --include="*.py" "$REPO_DIR"

echo "=== Data Processing ==="
grep -rn "Dataset\|DataLoader\|transforms\.\|Normalize\|train_split\|test_size" --include="*.py" "$REPO_DIR"

echo "=== Evaluation ==="
grep -rn "def eval\|def test\|accuracy\|f1_score\|metrics" --include="*.py" "$REPO_DIR"

echo "=== Random Seeds ==="
grep -rn "seed\|manual_seed\|random_state" --include="*.py" --include="*.yaml" "$REPO_DIR"

echo "=== Requirements ==="
cat "$REPO_DIR"/requirements.txt 2>/dev/null || cat "$REPO_DIR"/pyproject.toml 2>/dev/null | head -30
```

For YAML configs, extract structured values:
```bash
# Parse a Hydra/YAML config into a flat key=value list
python3 -c "
import yaml, sys
def flatten(d, prefix=''):
    for k, v in d.items():
        key = f'{prefix}.{k}' if prefix else k
        if isinstance(v, dict): flatten(v, key)
        else: print(f'{key} = {v}')
flatten(yaml.safe_load(open(sys.argv[1])))
" configs/train.yaml
```

## Step 2: Compose LaTeX (LLM)

Using the extracted values, compose the experimental section. The LLM should not guess any values - only use what was extracted by the scripts above.

## Experimental Section Structure

```latex
\section{Experiments}
\label{sec:experiments}

\subsection{Experimental Setup}
\label{sec:setup}

\paragraph{Datasets}
We evaluate on [datasets]:
\begin{itemize}
    \item \textbf{[Dataset 1]} \citep{ref}: [description, size, task]
    \item \textbf{[Dataset 2]} \citep{ref}: [description, size, task]
\end{itemize}
We use the standard train/validation/test splits [or describe custom splits].

\paragraph{Baselines}
We compare against the following methods:
\begin{itemize}
    \item \textbf{[Baseline 1]} \citep{ref}: [brief description]
    \item \textbf{[Baseline 2]} \citep{ref}: [brief description]
\end{itemize}
For fair comparison, we [ensure X / use official implementations / tune Y].

\paragraph{Evaluation Metrics}
We report [metrics], following standard practice in [area].
[If non-standard metrics, explain and justify.]

\paragraph{Implementation Details}
We implement our method in PyTorch [version].
[Model architecture summary - layers, dimensions, activations].
We train using [optimizer] with learning rate [lr] and [schedule].
Training uses batch size [B] for [N] epochs on [hardware].
We select the best checkpoint based on [validation criterion].

All experiments use [N] random seeds; we report mean and standard deviation.
Code is available at \url{https://github.com/[user]/[repo]}.

\subsection{Main Results}
\label{sec:results}

[Results section - typically handled separately]

\subsection{Ablation Studies}
\label{sec:ablations}

[Ablations section - typically handled separately]
```

## Appendix: Extended Details

```latex
\section{Extended Experimental Details}
\label{appx:experiments}

\subsection{Hyperparameters}
\label{appx:hyperparams}

\cref{tab:hyperparams} lists all hyperparameters used in our experiments.

\begin{table}[h]
\centering
\caption{Hyperparameter settings.}
\label{tab:hyperparams}
\begin{tabular}{@{}ll@{}}
\toprule
\textbf{Hyperparameter} & \textbf{Value} \\
\midrule
Optimizer & Adam \\
Learning rate & $3 \times 10^{-4}$ \\
LR schedule & Cosine decay \\
Batch size & 256 \\
Epochs & 100 \\
Weight decay & $10^{-4}$ \\
Dropout & 0.1 \\
Hidden dimension & 512 \\
Number of layers & 6 \\
Attention heads & 8 \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Dataset Details}
\label{appx:datasets}

[Extended dataset descriptions, preprocessing details, statistics]

\subsection{Compute Resources}
\label{appx:compute}

All experiments were conducted on [hardware description].
Training [method] takes approximately [time] on [GPU type].
Total compute: approximately [GPU hours].

\subsection{Licenses}
\label{appx:licenses}

\begin{itemize}
    \item [Dataset 1]: [License]
    \item [Dataset 2]: [License]
    \item Code: [License]
\end{itemize}
```

## Code-to-LaTeX Mapping

### Common Patterns

```python
# PyTorch optimizer → LaTeX
optimizer = torch.optim.Adam(params, lr=3e-4, weight_decay=1e-4)
# → "Adam optimizer with learning rate $3 \times 10^{-4}$ and weight decay $10^{-4}$"

# Learning rate scheduler → LaTeX
scheduler = CosineAnnealingLR(optimizer, T_max=100)
# → "cosine annealing schedule over 100 epochs"

# Model architecture → LaTeX
nn.Linear(512, 256), nn.ReLU(), nn.Dropout(0.1)
# → "fully-connected layers with dimensions [512, 256], ReLU activations, and dropout rate 0.1"

# Data transforms → LaTeX
transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
# → "ImageNet normalization (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])"
```

### Hydra/YAML Config → LaTeX

```yaml
# config.yaml
model:
  hidden_dim: 512
  num_layers: 6
  dropout: 0.1
training:
  lr: 0.0003
  batch_size: 256
  epochs: 100
```

→

```latex
We use a model with hidden dimension 512, 6 layers, and dropout 0.1.
Training uses learning rate $3 \times 10^{-4}$, batch size 256, for 100 epochs.
```

## Reproducibility Checklist

Based on NeurIPS/ICML reproducibility requirements:

### Must Include
- [ ] All hyperparameters with exact values
- [ ] Random seed(s) used
- [ ] Number of runs for statistical significance
- [ ] Hardware used (GPU type, count)
- [ ] Training time
- [ ] Dataset versions and splits
- [ ] Code availability statement

### Should Include
- [ ] Hyperparameter search procedure
- [ ] Sensitivity analysis
- [ ] Compute budget
- [ ] Data preprocessing steps
- [ ] Evaluation protocol details

### Nice to Include
- [ ] Docker/conda environment
- [ ] Pre-trained model weights
- [ ] Expected results variance
- [ ] Known failure modes

## Extraction Commands

When analyzing a repository, run:

```bash
# Find all config files
find . -name "*.yaml" -o -name "*.yml" -o -name "*.json" | head -20

# Search for hyperparameters
grep -r "learning_rate\|lr\|batch_size\|epochs" --include="*.py" --include="*.yaml"

# Find model definitions
grep -r "class.*Model\|class.*Network\|nn.Module" --include="*.py"

# Find training loop
grep -r "def train\|def fit\|optimizer.step" --include="*.py"

# Find dataset loading
grep -r "Dataset\|DataLoader\|load_data" --include="*.py"
```

## Output Format

Generate:

### 1. Extracted Information
```markdown
## Repository Analysis: [repo-name]

### Model Architecture
- Type: [Transformer/CNN/MLP/etc.]
- Parameters: [count]
- Key components: [list]

### Training Config
- Optimizer: [name] (lr=[value], wd=[value])
- Schedule: [type]
- Batch size: [value]
- Epochs: [value]

### Datasets
- [Dataset 1]: [details]
- [Dataset 2]: [details]

### Hardware
- [GPU type] × [count]
- Training time: [estimate]
```

### 2. LaTeX Output
```latex
% Main paper experimental setup
\subsection{Experimental Setup}
...

% Appendix extended details
\section{Extended Experimental Details}
...
```

### 3. Hyperparameter Table
```latex
\begin{table}[h]
...
\end{table}
```

### 4. Reproducibility Checklist Status
```markdown
## Reproducibility Coverage
- [x] Hyperparameters documented
- [x] Random seeds specified
- [ ] Missing: Training time estimate
- [ ] Missing: Exact dataset version
```
