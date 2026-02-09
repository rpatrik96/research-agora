---
name: paper-verify-experiments
description: Verify experimental claims in ML papers against source code repositories. Use when asked to "verify experiments", "check claims against code", "fact-check results", "audit experiments", or "validate paper against repo". Cross-references paper statements with actual implementation.
model: sonnet
metadata:
  research-domain: general
  research-phase: implementation
  task-type: verification
  verification-level: formal
---

# Experimental Claim Verification

Cross-reference claims in ML papers against their associated code repositories to identify discrepancies between what's written and what's implemented.

> **Hybrid**: Claim extraction from LaTeX and code parameter extraction are done via grep/scripts. LLM is used to interpret matches, assess severity, and generate the discrepancy report.

## Workflow

1. **Script: Extract claims from paper** - Grep LaTeX for numbers, hyperparameters, architecture details
2. **Script: Extract parameters from code** - Grep configs and source for actual values
3. **LLM: Cross-reference and report** - Match claims to code, assess discrepancies, generate report

## Step 1: Extract Claims from Paper (Script)

Run these on the paper's `.tex` files:

```bash
PAPER_DIR="."  # Set to paper directory

# Find experimental setup sections
grep -n "Experimental\|Implementation\|Setup\|Details" "$PAPER_DIR"/*.tex

# Extract numeric claims with context
grep -oE "[0-9]+(\.[0-9]+)?\s*(layers?|epochs?|batch|lr|learning rate|hidden|dim)" "$PAPER_DIR"/*.tex

# Extract hyperparameter mentions
grep -En "(dropout|hidden|dimension|optimizer|Adam|SGD|learning rate|weight.decay|batch.size)" "$PAPER_DIR"/*.tex

# Extract result claims
grep -En "[0-9]+\.[0-9]+.*(%|accuracy|F1|BLEU|ROUGE|AUC)" "$PAPER_DIR"/*.tex

# Extract architecture claims
grep -En "([0-9]+-layer|transformer|ResNet|LSTM|attention head)" "$PAPER_DIR"/*.tex
```

## Step 2: Extract Parameters from Code (Script)

Run these on the code repository:

```bash
CODE_DIR="."  # Set to code repository

# All-in-one extraction: find key hyperparameters across configs and source
echo "=== Optimizer settings ==="
grep -rn "optimizer\|Adam\|SGD\|learning_rate\|lr" --include="*.py" --include="*.yaml" "$CODE_DIR"

echo "=== Model dimensions ==="
grep -rn "hidden\|embed\|dim\|n_layer\|num_layer\|n_head" --include="*.py" --include="*.yaml" "$CODE_DIR"

echo "=== Batch size ==="
grep -rn "batch_size\|batch-size" --include="*.py" --include="*.yaml" "$CODE_DIR"

echo "=== Training epochs ==="
grep -rn "epochs\|max_steps\|num_train" --include="*.py" --include="*.yaml" "$CODE_DIR"

echo "=== Dropout ==="
grep -rn "dropout\|drop_rate" --include="*.py" "$CODE_DIR"

echo "=== Random seeds ==="
grep -rn "seed\|random_state\|manual_seed" --include="*.py" --include="*.yaml" "$CODE_DIR"

echo "=== Data splits ==="
grep -rn "train_split\|test_size\|val_split" --include="*.py" --include="*.yaml" "$CODE_DIR"
```

## Step 3: Cross-Reference (LLM)

After collecting script output from Steps 1 and 2, use LLM to:
- Match each paper claim to its code counterpart
- Classify match status (CONFIRMED, DISCREPANCY, MISSING)
- Assess severity and generate the verification report

## Claim Categories Reference

| Category | Examples | Where to Check |
|----------|----------|----------------|
| **Architecture** | "6-layer transformer", "hidden dim 512" | model.py, config files |
| **Training** | "Adam with lr=3e-4", "batch size 256" | train.py, configs |
| **Data** | "80/10/10 split", "ImageNet normalization" | data.py, preprocessing |
| **Hyperparameters** | "dropout 0.1", "weight decay 1e-4" | configs, model definitions |
| **Evaluation** | "5 random seeds", "best checkpoint" | eval.py, training loop |
| **Results** | "achieves 94.2% accuracy" | logs, saved results |
| **Compute** | "trained for 100 epochs", "8 V100 GPUs" | logs, scripts |

## Verification Categories

### Match Status

**CONFIRMED**: Paper claim matches code exactly
**MINOR DISCREPANCY**: Small difference (e.g., 0.1 vs 0.01)
**MAJOR DISCREPANCY**: Significant mismatch affecting reproducibility
**MISSING IN CODE**: Claim cannot be verified (feature not found)
**MISSING IN PAPER**: Code has detail not mentioned in paper
**AMBIGUOUS**: Multiple code paths, unclear which was used

### Severity Assessment

| Severity | Impact | Example |
|----------|--------|---------|
| **Critical** | Results may not reproduce | Wrong optimizer, batch size 10x different |
| **Major** | Could affect performance | Wrong LR, different architecture depth |
| **Minor** | Unlikely to affect results | Slightly different dropout, minor preprocessing |
| **Info** | No impact | Code has more features than described |

## Verification Report Format

```markdown
## Experimental Verification Report

**Paper**: [Paper title]
**Repository**: [GitHub URL]
**Verification date**: [Date]

---

### Summary

| Category | Confirmed | Discrepancies | Missing |
|----------|-----------|---------------|---------|
| Architecture | [N] | [N] | [N] |
| Training | [N] | [N] | [N] |
| Data | [N] | [N] | [N] |
| Evaluation | [N] | [N] | [N] |
| **Total** | [N] | [N] | [N] |

**Overall Consistency Score**: [X]% claims verified

---

### Architecture Claims

#### Claim: "6-layer transformer with hidden dimension 512"
**Status**: CONFIRMED
**Paper reference**: Section 4.1, line 234
**Code reference**: `models/transformer.py:45`
```python
self.layers = nn.ModuleList([
    TransformerBlock(d_model=512, ...) for _ in range(6)
])
```
**Notes**: Exact match

---

#### Claim: "8 attention heads"
**Status**: MAJOR DISCREPANCY
**Paper reference**: Section 4.1
**Code reference**: `config/base.yaml:12`
```yaml
n_heads: 16  # Paper says 8!
```
**Impact**: May affect performance characteristics
**Recommendation**: Clarify which configuration was used for reported results

---

### Training Claims

#### Claim: "Adam optimizer with learning rate 3e-4"
**Status**: CONFIRMED
**Code reference**: `train.py:89`
```python
optimizer = torch.optim.Adam(model.parameters(), lr=3e-4)
```

---

#### Claim: "trained for 100 epochs"
**Status**: MINOR DISCREPANCY
**Paper reference**: Section 4.2
**Code reference**: `config/train.yaml:8`
```yaml
max_epochs: 150  # Paper says 100
```
**Note**: Paper may report early stopping point

---

### Data Processing Claims

#### Claim: "standard ImageNet normalization"
**Status**: CONFIRMED
**Code reference**: `data/transforms.py:23`
```python
transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
```

---

### Unverifiable Claims

| Claim | Reason | Recommendation |
|-------|--------|----------------|
| "5 random seeds" | Seeds not logged | Add seed logging |
| "8 V100 GPUs" | Hardware config not in repo | Add to README |
| "best checkpoint selected" | Selection criteria unclear | Document selection |

---

### Missing from Paper

Details found in code but not documented in paper:

| Detail | Code Location | Importance |
|--------|---------------|------------|
| Gradient clipping (1.0) | train.py:102 | Medium |
| Label smoothing (0.1) | loss.py:34 | High - affects results |
| Warmup steps (1000) | scheduler.py:15 | High - affects training |

---

### Discrepancy Summary

#### Critical Issues (Must Address)
1. **Attention heads mismatch**: Paper says 8, code has 16
   - File: `config/base.yaml:12`
   - Action: Update paper or clarify configuration

#### Major Issues (Should Address)
2. **Label smoothing not mentioned**: Code uses 0.1 label smoothing
   - File: `loss.py:34`
   - Action: Add to experimental details

#### Minor Issues (Nice to Fix)
3. **Epoch count**: Paper says 100, config has 150
   - File: `config/train.yaml:8`
   - Action: Clarify if early stopping used

---

### Reproducibility Assessment

| Criterion | Status |
|-----------|--------|
| All hyperparameters documented | PARTIAL |
| Training configuration complete | YES |
| Random seeds specified | NO |
| Hardware requirements clear | NO |
| Data preprocessing documented | YES |
| Evaluation protocol clear | YES |

**Reproducibility Score**: 4/6 criteria met

---

### Recommended Actions

1. **Fix critical discrepancies**
   - [ ] Resolve attention head count mismatch

2. **Document missing details**
   - [ ] Add label smoothing to paper
   - [ ] Add gradient clipping to paper
   - [ ] Add warmup schedule to paper

3. **Improve reproducibility**
   - [ ] Add random seeds to paper
   - [ ] Document hardware configuration
   - [ ] Add expected training time
```

## Cross-Reference Patterns

### Config File Mapping

```yaml
# Common config structure → Paper section mapping
model:
  hidden_dim: 512      → "hidden dimension 512"
  num_layers: 6        → "6-layer"
  num_heads: 8         → "8 attention heads"
  dropout: 0.1         → "dropout rate 0.1"

training:
  optimizer: adam      → "Adam optimizer"
  lr: 0.0003          → "learning rate 3×10⁻⁴"
  batch_size: 256     → "batch size 256"
  epochs: 100         → "trained for 100 epochs"

data:
  train_split: 0.8    → "80/10/10 split"
  val_split: 0.1
  test_split: 0.1
```

### Code Pattern Recognition

```python
# Optimizer pattern
optimizer = Adam(params, lr=X, weight_decay=Y)
# → Paper: "Adam with learning rate X and weight decay Y"

# Architecture pattern
nn.Linear(in_features=A, out_features=B)
# → Paper: "fully connected layer mapping A to B dimensions"

# Dropout pattern
nn.Dropout(p=0.1)
# → Paper: "dropout with probability 0.1"

# Data split pattern
train_test_split(data, test_size=0.2, random_state=42)
# → Paper: "80/20 train/test split with seed 42"
```

## Automated Checks

### Quick Verification Script

```python
# Conceptual checks to perform
checks = [
    ("learning_rate", paper_lr, code_lr),
    ("batch_size", paper_batch, code_batch),
    ("hidden_dim", paper_dim, code_dim),
    ("num_layers", paper_layers, code_layers),
    ("dropout", paper_dropout, code_dropout),
    ("optimizer", paper_opt, code_opt),
    ("epochs", paper_epochs, code_epochs),
]

for name, paper_val, code_val in checks:
    if paper_val != code_val:
        print(f"MISMATCH: {name} - Paper: {paper_val}, Code: {code_val}")
```

## Output Deliverables

1. **Verification Summary Table**: Quick overview of all claims
2. **Detailed Discrepancy Report**: Full analysis of each mismatch
3. **Reproducibility Checklist**: Missing information for reproduction
4. **Recommended Paper Edits**: Specific text changes to fix issues
5. **Code Documentation Gaps**: Suggestions for repository README

## Common Discrepancy Causes

1. **Config variations**: Multiple configs, paper reports different one
2. **Iterative changes**: Code updated after paper written
3. **Default values**: Paper omits "obvious" defaults that differ
4. **Ablation confusion**: Paper reports ablated version, code has full
5. **Copy-paste errors**: Values transposed or truncated
6. **Unit confusion**: Learning rate 3e-4 vs 0.0003 formatting
