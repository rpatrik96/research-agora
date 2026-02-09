---
name: experiment-tracker
description: |
  Sync ML experiment results to paper drafts. Use when asked to "update results",
  "sync experiments", "pull latest metrics", "update tables from code",
  "experiment to paper", "refresh results", or "sync paper with repo".
  Extracts metrics from code/logs and updates paper sections.
model: sonnet
metadata:
  research-domain: general
  research-phase: experiment-design
  task-type: automation
  verification-level: none
---

# Experiment Tracker Agent

Synchronize ML experiment results from code repositories to paper drafts. This agent bridges the gap between your experiment logs and your LaTeX paper.

> **Hybrid**: Artifact discovery, metric extraction, and CSV/JSON/YAML parsing are done via scripts. LLM is used for mapping metrics to paper sections and generating update diffs.

## Workflow

1. **Script: Discover artifacts** - Find configs, logs, results files via find/glob
2. **Script: Extract metrics** - Parse CSV/JSON/YAML with shell commands or Python one-liners
3. **Script: Find paper tables** - Grep for `\label{tab:}` and placeholder values in LaTeX
4. **LLM: Map and generate updates** - Match metrics to tables/figures, produce diffs
5. **Present diff**: Show before/after for user approval
6. **Apply changes**: Update paper with approved changes

## Before Starting

Gather the following information:
- Path to the code repository
- Path to the paper LaTeX files
- Which experiment runs to use (latest, best, specific run ID)
- Target tables/figures to update

## Step 1: Artifact Discovery (Script)

Run these commands to discover all experiment artifacts:

```bash
REPO_DIR="."  # Set to code repository path

# Find all experiment artifacts at once
echo "=== Config files ==="
find "$REPO_DIR" -name "*.yaml" -o -name "*.yml" | grep -v node_modules | head -20

echo "=== Result files ==="
find "$REPO_DIR" \( -name "results*" -o -name "metrics*" \) \( -name "*.csv" -o -name "*.json" \) | head -20

echo "=== W&B runs ==="
ls -la "$REPO_DIR"/wandb/*/files/wandb-summary.json 2>/dev/null

echo "=== MLflow runs ==="
ls -la "$REPO_DIR"/mlruns/*/meta.yaml 2>/dev/null

echo "=== CSV headers ==="
find "$REPO_DIR" -name "*.csv" -exec sh -c 'echo "--- {} ---"; head -1 "{}"' \;
```

## Step 2: Extract Metrics (Script)

Use these one-liners to parse metrics from discovered artifacts:

```bash
# Extract from CSV (last row = final metrics, or sort by a column for best)
tail -1 results/metrics.csv
# Best accuracy row
sort -t',' -k4 -rn results/metrics.csv | head -1

# Extract from JSON (W&B summary)
python3 -c "import json; d=json.load(open('wandb/latest-run/files/wandb-summary.json')); print({k:v for k,v in d.items() if not k.startswith('_')})"

# Extract from YAML config
python3 -c "import yaml; c=yaml.safe_load(open('configs/train.yaml')); print(f'lr={c[\"training\"][\"lr\"]}, bs={c[\"training\"][\"batch_size\"]}, epochs={c[\"training\"][\"epochs\"]}')"
```

## Step 3: Find Paper Placeholders (Script)

```bash
PAPER_DIR="."  # Set to paper directory

# Find tables with placeholder values (XX or 0.XX)
grep -n 'XX\|0\.XX\|TBD\|TODO' "$PAPER_DIR"/*.tex

# Find all table labels
grep -n '\\label{tab:' "$PAPER_DIR"/*.tex

# Find inline result claims
grep -n 'achieves\|accuracy\|F1\|performance' "$PAPER_DIR"/*.tex | grep -i 'XX\|TBD'
```

After running all script steps, use LLM to map extracted metrics to paper placeholders and generate update diffs.

## Common Artifact Locations Reference

```bash
# Weights & Biases
wandb/*/files/wandb-summary.json
wandb/*/files/config.yaml

# MLflow
mlruns/*/meta.yaml
mlruns/*/metrics/

# Results files
results/*.csv
results/*.json
outputs/*.csv

# Configuration
configs/*.yaml
config/*.json
hydra/conf/*.yaml
```

## Metric Extraction

### Weights & Biases

```python
# wandb-summary.json structure
{
    "best_val_accuracy": 0.943,
    "final_train_loss": 0.0234,
    "best_epoch": 87,
    "_runtime": 14523.4,
    "_step": 10000
}

# config.yaml structure
learning_rate: 0.001
batch_size: 256
model:
  hidden_dim: 512
  num_layers: 6
```

### CSV Results

```csv
# Typical results.csv
epoch,train_loss,val_loss,val_acc,test_acc
1,2.34,2.45,0.12,0.11
...
100,0.02,0.15,0.94,0.93
```

Extract:
- Final row values
- Best values (argmax/argmin)
- Summary statistics (mean, std)

### Config Files

```yaml
# Hydra config example
model:
  name: transformer
  hidden_dim: 512
  num_layers: 6
  num_heads: 8
  dropout: 0.1

training:
  optimizer: adam
  lr: 0.0003
  batch_size: 256
  epochs: 100
  weight_decay: 0.01
```

## Paper Section Mapping

### Table Detection

Find tables in LaTeX and match to metrics:

```latex
% Table pattern to detect
\begin{table}
\caption{Main results on [Dataset]}
\label{tab:main_results}
\begin{tabular}{lcc}
\toprule
Method & Accuracy & F1 \\
\midrule
Baseline & 0.85 & 0.82 \\
Ours & \textbf{0.XX} & \textbf{0.XX} \\  % <- Update these
\bottomrule
\end{tabular}
\end{table}
```

### Metric Matching

| Paper Reference | Code Source | Extraction |
|-----------------|-------------|------------|
| "achieves 94.3% accuracy" | wandb-summary.json | `best_val_accuracy * 100` |
| "trained for 100 epochs" | config.yaml | `training.epochs` |
| "learning rate of 3e-4" | config.yaml | `training.lr` |
| "batch size 256" | config.yaml | `training.batch_size` |
| Table cell "0.943" | results.csv | Last row, val_acc column |

## Update Generation

### Table Updates

```latex
% BEFORE
Ours & 0.XX & 0.XX \\

% AFTER (with extracted values)
Ours & \textbf{0.943} & \textbf{0.912} \\
```

### Text Updates

```latex
% BEFORE
Our method achieves XX\% accuracy on the test set.

% AFTER
Our method achieves 93.2\% accuracy on the test set.
```

### Experimental Details Updates

```latex
% BEFORE
We train for XX epochs with a learning rate of XX.

% AFTER
We train for 100 epochs with a learning rate of $3 \times 10^{-4}$.
```

## Diff Presentation

Present changes clearly for approval:

```markdown
## Proposed Updates

### 1. Table: Main Results (experiments.tex:45)

**Before:**
| Method | Accuracy | F1 |
|--------|----------|-----|
| Ours | 0.XX | 0.XX |

**After:**
| Method | Accuracy | F1 |
|--------|----------|-----|
| Ours | **0.943** | **0.912** |

*Source: wandb/run-20240115_143022/files/wandb-summary.json*

---

### 2. Text Update (experiments.tex:78)

**Before:**
> Our method achieves XX% accuracy...

**After:**
> Our method achieves 93.2% accuracy...

*Source: results/test_metrics.csv, row 100*

---

### 3. Training Details (method.tex:112)

**Before:**
> We use a learning rate of XX with batch size XX.

**After:**
> We use a learning rate of $3 \times 10^{-4}$ with batch size 256.

*Source: configs/train.yaml*

---

## Approval

- [ ] Apply update 1 (Main Results table)
- [ ] Apply update 2 (Accuracy claim)
- [ ] Apply update 3 (Training details)

Any updates to skip or modify?
```

## MCP Integration

### Required MCPs

| MCP | Tools Used | Purpose |
|-----|------------|---------|
| **github** | get_file_contents, search_code | Access repository files |
| **filesystem** | (built-in) | Read local experiment outputs |

### Tool Usage

```python
# Read W&B summary
content = mcp__github__get_file_contents(
    owner="user",
    repo="project",
    path="wandb/latest-run/files/wandb-summary.json"
)

# Search for config files
configs = mcp__github__search_code(
    query="learning_rate repo:user/project",
    language="yaml"
)
```

## Output Deliverables

1. **Discovery Report**: All found artifacts with locations
2. **Extracted Metrics**: Parsed values from each source
3. **Mapping Table**: Paper references -> Code sources
4. **Diff View**: Before/after for each proposed change
5. **Verification Checklist**: Sources for each update

## Verification Checklist

Before applying updates:

- [ ] Metrics extracted from correct run (check run ID/timestamp)
- [ ] Values match expected ranges (no off-by-one, unit errors)
- [ ] All sources documented for reproducibility
- [ ] No accidental inclusion of intermediate/debug results
- [ ] Formatting matches paper conventions (%, decimals)
- [ ] Bold/emphasis applied correctly for best results

## Common Issues

| Issue | Solution |
|-------|----------|
| Multiple runs found | Ask user to specify run ID or use latest/best |
| Metric name mismatch | Create mapping dictionary (val_acc -> accuracy) |
| Unit conversion needed | Apply conversion (0.943 -> 94.3%) |
| Missing metrics | Flag as "NOT FOUND" and ask user |
| Stale results | Warn if run timestamp is old |

## Formatting Conventions

### Number Formatting

```latex
% Percentages
94.3\%           % One decimal for accuracy
0.943            % Three decimals for raw values

% Scientific notation for small numbers
$3 \times 10^{-4}$  % Learning rates
0.0003              % Alternative inline

% Large numbers
1.2M parameters     % Millions
256                 % Batch sizes (no formatting)
```

### Table Formatting

```latex
% Use booktabs
\toprule, \midrule, \bottomrule

% Bold best results
\textbf{0.943}

% Standard deviation
$0.943 \pm 0.012$

% Multiple runs
$0.943_{\pm 0.012}$
```

## Skill Dependencies

This agent extends and can invoke:
- `paper-verify-experiments` - For consistency checking
- `paper-experiments` - For writing experimental details sections
