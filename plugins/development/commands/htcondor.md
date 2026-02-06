---
name: htcondor
description: |
  Generate HTCondor submission files and wrapper scripts for ML research jobs.
  Use when asked to "create condor job", "submit to cluster", "write .sub file",
  "htcondor setup", "cluster job", or "batch submission". Supports GPU/CPU jobs,
  parameter sweeps, multi-seed experiments, and ablation studies.
model: sonnet
allowed-tools: Read, Write, Bash(ls *), Glob, Grep
---

# HTCondor Job Generation

> **Script-first**: This skill generates .sub files and wrapper scripts from templates. LLM assists only with adapting templates to specific project needs.

Generate production-ready HTCondor submission files (.sub) and wrapper shell scripts for ML research workflows.

## Overview

This skill creates HTCondor infrastructure for:
- GPU-accelerated deep learning experiments
- CPU-based numerical simulations
- Multi-seed reproducibility studies
- Hyperparameter sweeps and ablation studies
- Multi-dataset experiments

## Workflow

1. **Gather requirements** - Identify job type, resources, and parameters
2. **Detect project structure** - Find main scripts, requirements, venv location
3. **Generate wrapper script** - Create `run_experiment.sh` for job execution
4. **Generate submission file** - Create `.sub` file with appropriate configuration
5. **Verify** - Check generated files for correctness

## Project Structure Detection

Before generating files, check for:
```bash
# Find main entry points
ls *.py main.py train.py run.py experiment.py 2>/dev/null

# Find existing cluster directory
ls -d cluster/ scripts/ jobs/ 2>/dev/null

# Find virtual environment
ls -d venv/ .venv/ env/ 2>/dev/null

# Find requirements
ls requirements.txt pyproject.toml setup.py 2>/dev/null
```

## Submission File Templates

### GPU Job Template (Deep Learning)

```condor
# HTCondor submission file for GPU-accelerated ML experiments
# Usage: condor_submit cluster/experiment.sub

universe = vanilla
executable = cluster/run_experiment.sh

# Resource requirements
request_cpus = 4
request_memory = 32GB
request_disk = 20GB
request_gpus = 1

# GPU requirements
requirements = (TARGET.CUDACapability >= 7.0)
# Optional: require specific GPU memory
# requirements = (TARGET.CUDACapability >= 7.0) && (TARGET.CUDAGlobalMemoryMb >= 16000)

# GPU bidding (cluster-specific pricing)
# H100: +bid = 35, A100: +bid = 25, V100/RTX: +bid = 15
+bid = 15

# Environment
environment = "CUDA_VISIBLE_DEVICES=$(GPUSlot)"
getenv = True

# Job timeout (12 hours = 43200 seconds)
MaxTime = 43200
periodic_remove = (JobStatus =?= 2) && ((CurrentTime - JobCurrentStartDate) >= $(MaxTime))

# Logging
log_dir = cluster/logs
error = $(log_dir)/job_$(ClusterId)_$(ProcId).err
output = $(log_dir)/job_$(ClusterId)_$(ProcId).out
log = $(log_dir)/job_$(ClusterId)_$(ProcId).log

# File transfer (use NO for shared filesystem like Lustre/NFS)
should_transfer_files = NO

# Arguments passed to run_experiment.sh
arguments = train --config configs/default.yaml

queue
```

### CPU Job Template (Numerical Simulations)

```condor
# HTCondor submission file for CPU-based experiments
# Usage: condor_submit cluster/experiment.sub

universe = vanilla
executable = cluster/run_experiment.sh

# Resource requirements
request_cpus = 8
request_memory = 32GB
request_disk = 20GB

# Job timeout (24 hours)
MaxTime = 86400
periodic_remove = (JobStatus =?= 2) && ((CurrentTime - JobCurrentStartDate) >= $(MaxTime))

# Logging
log_dir = cluster/logs
error = $(log_dir)/job_$(ClusterId)_$(ProcId).err
output = $(log_dir)/job_$(ClusterId)_$(ProcId).out
log = $(log_dir)/job_$(ClusterId)_$(ProcId).log

# File transfer mode (for clusters without shared filesystem)
transfer_input_files = main.py, utils.py, requirements.txt
should_transfer_files = YES
when_to_transfer_output = ON_EXIT

# Arguments
arguments = run --n_samples 10000

queue
```

## Queue Patterns

### Single Job
```condor
arguments = train --seed 42
queue
```

### Multi-Variable Grid (Cartesian Product)
```condor
arguments = train --seed $(seed) --lr $(lr) --dataset $(dataset)

queue seed, lr, dataset from (
  42, 0.001, mnist
  42, 0.001, cifar10
  42, 0.01, mnist
  42, 0.01, cifar10
  123, 0.001, mnist
  123, 0.001, cifar10
  123, 0.01, mnist
  123, 0.01, cifar10
)
```

### Sequential Seed Sweep
```condor
arguments = train --seed $(seed) --config configs/default.yaml

queue seed from seq 1 100 |
```

### Multi-Phase Experiments (Different Configs per Phase)

```condor
# Phase 1: Baseline experiments (5 jobs)
arguments = train --seed $(seed) --model baseline --dataset $(dataset)
queue seed, dataset from (
  42, mnist
  42, cifar10
  123, mnist
  123, cifar10
  456, mnist
)

# Phase 2: Ablation study (4 jobs)
arguments = train --seed 42 --model $(model) --dataset mnist --ablation $(ablation)
queue model, ablation from (
  resnet, dropout
  resnet, batchnorm
  vit, dropout
  vit, batchnorm
)

# Phase 3: Hyperparameter sweep (6 jobs)
arguments = train --seed 42 --model resnet --lr $(lr) --batch_size $(bs)
queue lr, bs from (
  0.001, 32
  0.001, 64
  0.001, 128
  0.01, 32
  0.01, 64
  0.01, 128
)
```

### Conditional Parameters
```condor
# With feature enabled
feature_flag = --use_feature
queue config in (config_a, config_b)

# Without feature
feature_flag =
queue config in (config_c, config_d)
```

## Wrapper Script Template

```bash
#!/bin/bash
# run_experiment.sh - HTCondor job wrapper script
# Handles environment setup, logging, and experiment dispatch

set -e  # Exit on error

# =============================================================================
# Configuration (modify these paths for your cluster)
# =============================================================================
CLUSTER_HOME="/path/to/cluster/home"
PROJECT_NAME="my_project"
PROJECT_DIR="${CLUSTER_HOME}/${PROJECT_NAME}"

# Virtual environment (supports override via environment variable)
VENV_DIR="${PROJECT_VENV:-${PROJECT_DIR}/venv}"

# Output directory for results
OUTPUT_DIR="${PROJECT_DIR}/results"

# =============================================================================
# Environment Setup
# =============================================================================
echo "=========================================="
echo "Job started at: $(date)"
echo "Hostname: $(hostname)"
echo "Working directory: $(pwd)"
echo "=========================================="

# Activate virtual environment
if [ -d "${VENV_DIR}" ]; then
    echo "Activating virtual environment: ${VENV_DIR}"
    source "${VENV_DIR}/bin/activate"
else
    echo "ERROR: Virtual environment not found at ${VENV_DIR}"
    exit 1
fi

# Navigate to project directory
cd "${PROJECT_DIR}"

# Debug info
echo "Python: $(which python)"
echo "Python version: $(python --version)"
if command -v nvidia-smi &> /dev/null; then
    echo "GPU Info:"
    nvidia-smi --query-gpu=name,memory.total --format=csv
fi
echo "=========================================="

# =============================================================================
# Experiment Dispatch
# =============================================================================
EXPERIMENT_TYPE="$1"
shift  # Remove first argument, rest are passed to Python

case "${EXPERIMENT_TYPE}" in
    train)
        echo "Running training experiment..."
        python train.py "$@"
        ;;
    eval|evaluate)
        echo "Running evaluation..."
        python evaluate.py "$@"
        ;;
    sweep)
        echo "Running hyperparameter sweep..."
        python sweep.py "$@"
        ;;
    ablation)
        echo "Running ablation study..."
        python ablation.py "$@"
        ;;
    *)
        echo "Running default: python main.py ${EXPERIMENT_TYPE} $@"
        python main.py "${EXPERIMENT_TYPE}" "$@"
        ;;
esac

EXIT_CODE=$?

# =============================================================================
# Cleanup
# =============================================================================
echo "=========================================="
echo "Job finished at: $(date)"
echo "Exit code: ${EXIT_CODE}"
echo "=========================================="

exit ${EXIT_CODE}
```

## Resource Guidelines

### GPU Jobs (Deep Learning)

| Workload | CPUs | Memory | GPU Memory | Time |
|----------|------|--------|------------|------|
| Small model training | 4 | 16GB | 8GB | 6h |
| Medium model (ResNet/ViT) | 4-8 | 32GB | 16GB | 12h |
| Large model (LLM fine-tune) | 8-12 | 64GB | 24GB+ | 24h |
| Multi-GPU training | 8-16 | 128GB | 40GB+ × N | 48h |

### CPU Jobs (Numerical)

| Workload | CPUs | Memory | Time |
|----------|------|--------|------|
| Monte Carlo (small) | 4 | 8GB | 6h |
| Monte Carlo (large) | 8 | 32GB | 24h |
| Matrix operations | 8-16 | 64GB | 12h |
| Statistical analysis | 4 | 16GB | 6h |

### GPU Bidding Strategy

```condor
# Cluster-specific GPU pricing (check your cluster docs)
# Higher bid = access to better GPUs, but higher cost

# Budget tier: older GPUs (P100, GTX 1080)
+bid = 10

# Standard tier: V100, RTX 2080 Ti, Quadro RTX
+bid = 15

# Premium tier: A100
+bid = 25

# Top tier: H100
+bid = 35
```

## File Transfer Strategies

### Shared Filesystem (Lustre/NFS/GPFS)

```condor
# Code and data accessible from all nodes
should_transfer_files = NO
```

Advantages:
- No transfer overhead
- Access to large datasets
- Results immediately available

### File Transfer Mode

```condor
# Transfer specific files to compute node
transfer_input_files = train.py, model.py, utils.py, configs/, requirements.txt
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_output_files = results/, checkpoints/
```

Use when:
- No shared filesystem
- Small, self-contained jobs
- Datasets downloaded during job

## Log Organization

### Basic Logging
```condor
log_dir = cluster/logs
error = $(log_dir)/job_$(ClusterId)_$(ProcId).err
output = $(log_dir)/job_$(ClusterId)_$(ProcId).out
log = $(log_dir)/job_$(ClusterId)_$(ProcId).log
```

### Descriptive Logging (for sweeps)
```condor
# Include parameter values in log names
log_dir = cluster/logs
error = $(log_dir)/$(dataset)_seed$(seed)_lr$(lr).err
output = $(log_dir)/$(dataset)_seed$(seed)_lr$(lr).out
log = $(log_dir)/$(dataset)_seed$(seed)_lr$(lr).log
```

### Absolute Path Logging
```condor
# For clusters with specific log directories
log_root = /home/$(USER)/jobs/$(ClusterId)_$(ProcId)
error = $(log_root).err
output = $(log_root).out
log = $(log_root).log
```

## Common Patterns

### Multi-Seed Reproducibility Study
```condor
# Run same experiment with multiple seeds for statistical significance
arguments = train --config $(config) --seed $(seed) --output_dir results/$(config)_seed$(seed)

queue seed, config from (
  42, baseline
  123, baseline
  456, baseline
  789, baseline
  1337, baseline
  42, proposed
  123, proposed
  456, proposed
  789, proposed
  1337, proposed
)
```

### Dataset Ablation
```condor
# Same model across multiple datasets
arguments = train --model resnet50 --dataset $(dataset) --seed 42

queue dataset in (
  mnist
  fashion_mnist
  cifar10
  cifar100
  imagenet_subset
)
```

### Hyperparameter Grid Search
```condor
# Full grid over learning rate and batch size
arguments = train --lr $(lr) --batch_size $(bs) --weight_decay $(wd)

queue lr, bs, wd from (
  0.0001, 32, 0.0
  0.0001, 32, 0.01
  0.0001, 64, 0.0
  0.0001, 64, 0.01
  0.001, 32, 0.0
  0.001, 32, 0.01
  0.001, 64, 0.0
  0.001, 64, 0.01
  0.01, 32, 0.0
  0.01, 32, 0.01
  0.01, 64, 0.0
  0.01, 64, 0.01
)
```

### Progressive Training Phases
```condor
# Phase 1: Quick validation (short timeout)
MaxTime = 7200
arguments = train --epochs 5 --seed $(seed) --tag validation
queue seed in (42, 123, 456)

# Phase 2: Full training (long timeout)
MaxTime = 86400
arguments = train --epochs 100 --seed $(seed) --tag full
queue seed in (42, 123, 456)
```

## Directory Setup

Create the cluster directory structure:
```bash
mkdir -p cluster/logs
touch cluster/.gitkeep
echo "*.err" >> cluster/logs/.gitignore
echo "*.out" >> cluster/logs/.gitignore
echo "*.log" >> cluster/logs/.gitignore
```

## Submission Commands

```bash
# Submit single job
condor_submit cluster/experiment.sub

# Submit with variable override
condor_submit cluster/experiment.sub seed=42 lr=0.001

# Check job status
condor_q

# Check specific job
condor_q -hold -analyze <job_id>

# Remove job
condor_rm <job_id>

# View job history
condor_history -limit 20
```

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Job held immediately | Resource request too high | Reduce memory/GPU requirements |
| Job evicted | Exceeded MaxTime | Increase timeout or checkpoint |
| File not found | Wrong path in wrapper | Use absolute paths |
| GPU not detected | CUDA_VISIBLE_DEVICES not set | Add to environment line |
| venv not found | Wrong VENV_DIR path | Check cluster home path |

### Debug Commands
```bash
# Why is job held?
condor_q -hold -analyze <job_id>

# Check job requirements vs available slots
condor_status -constraint 'TotalGpus > 0'

# View job log
condor_history -long <job_id> | grep -E "^(ExitCode|RemoveReason)"
```

## Checklist

Before submission:
- [ ] Wrapper script has correct paths for your cluster
- [ ] Virtual environment exists and has dependencies
- [ ] Log directory exists (`mkdir -p cluster/logs`)
- [ ] Resource requests are reasonable for cluster
- [ ] File transfer settings match your cluster setup
- [ ] Arguments correctly reference queue variables

After submission:
- [ ] Jobs appear in queue (`condor_q`)
- [ ] No jobs immediately held
- [ ] Log files being written
- [ ] Results appearing in output directory
