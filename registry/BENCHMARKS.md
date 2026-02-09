# Benchmark Integration

## Overview

The Research Agora hosts leaderboards for external benchmarks that evaluate AI research skills. Benchmarks live in their own repositories; the Agora provides discovery, comparison, and result aggregation.

## Registered Benchmarks

| Benchmark | Task | Repo | Primary Metric |
|-----------|------|------|----------------|
| CiteBench | Citation hallucination detection | [rpatrik96/citebench](https://github.com/rpatrik96/citebench) | F1 |

## Registering a New Benchmark

To register your benchmark with the Research Agora:

1. **Create your benchmark repo** with:
   - Public dev set for development
   - Hidden test set (in a private repo or held-out split)
   - Evaluation script that produces standardized metrics
   - `README.md` documenting the task, dataset, and evaluation protocol

2. **Open a PR** adding your benchmark to `registry/benchmarks.json`:
   ```json
   {
     "id": "your-benchmark-id",
     "name": "Human-readable name",
     "repo": "org/repo",
     "homepage": "https://github.com/org/repo",
     "description": "What this benchmark evaluates",
     "task": "One-sentence task description",
     "metrics": ["precision", "recall", "f1"],
     "primary-metric": "f1",
     "categories": ["category1", "category2"],
     "submission-format": "jsonl",
     "dev-set": true,
     "hidden-test-set": true,
     "refresh-cadence": "quarterly",
     "relevant-skills": ["skill-name-1", "skill-name-2"],
     "tags": ["tag1", "tag2"]
   }
   ```

3. **CI validates** that:
   - The repo exists and is public
   - Required fields are present
   - `relevant-skills` reference actual skills in `registry/index.json`

## Submitting Results

To submit results to a benchmark leaderboard:

1. **Run the benchmark** following the repo's evaluation protocol
2. **Create a results file** in JSONL format:
   ```jsonl
   {"benchmark-id": "citebench", "skill": "paper-references", "model": "sonnet", "version": "1.0.0", "date": "2026-02-09", "metrics": {"precision": 0.92, "recall": 0.87, "f1": 0.89, "accuracy": 0.91}, "category-breakdown": {"non-existent": {"f1": 0.95}, "wrong-authors": {"f1": 0.82}}, "notes": "Using bibtexupdater + arXiv MCP fallback", "reproduction": "python eval.py --skill paper-references --split test"}
   ```
3. **Open a PR** adding your entry to `registry/results.json`
4. **Include reproduction instructions** so others can verify your results

### Results Schema

| Field | Required | Description |
|-------|----------|-------------|
| `benchmark-id` | Yes | Must match an ID in `benchmarks.json` |
| `skill` | Yes | Skill name from `registry/index.json` |
| `model` | Yes | Model used (opus/sonnet/haiku) |
| `version` | Yes | Skill version or commit hash |
| `date` | Yes | Evaluation date (ISO 8601) |
| `metrics` | Yes | Object with metric name → value pairs |
| `category-breakdown` | No | Per-category metric breakdown |
| `notes` | No | Implementation notes |
| `reproduction` | Yes | Command to reproduce results |

## Anti-Gaming Measures

- **Hidden test sets**: Evaluation against held-out data prevents overfitting
- **Quarterly refresh**: Test sets are refreshed to prevent memorization
- **Temporal segmentation**: New entries use post-training-cutoff data (inspired by LiveCodeBench)
- **Reproduction required**: All submissions must include reproduction commands
- **Version pinning**: Results are tied to specific skill versions/commits
