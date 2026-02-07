---
name: python-cicd
description: Set up Python CI/CD with GitHub Actions, pre-commit hooks, and code quality tools. Use when asked to "set up CI/CD", "add pre-commit hooks", "configure GitHub Actions", "add linting", or "set up testing pipeline". Configures Black, isort, flake8, and pytest for Python 3.11.
model: haiku
---

# Python CI/CD Setup

> **Script-first**: This skill generates config files from templates. No LLM generation needed.

Configure GitHub Actions CI/CD pipeline with pre-commit hooks for Python projects.

## Stack

- **Python**: 3.11
- **Formatter**: Black
- **Import sorting**: isort (Black-compatible)
- **Linter**: flake8
- **Testing**: pytest

## Quick Setup

1. Run `scripts/setup_cicd.sh` from skill directory
2. Commit generated files
3. Install pre-commit: `pre-commit install`

## Generated Files

### `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
```

### `pyproject.toml` additions

```toml
[tool.black]
line-length = 88
target-version = ["py311"]

[tool.isort]
profile = "black"
line_length = 88

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

### `setup.cfg` (flake8 config)

```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,build,dist,.venv
per-file-ignores =
    __init__.py:F401
```

### `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          pip install black isort flake8
      - name: Check Black
        run: black --check .
      - name: Check isort
        run: isort --check-only .
      - name: Flake8
        run: flake8

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: coverage.xml
        continue-on-error: true
```

## Customization

### Add type checking (optional)

Add mypy to pre-commit:
```yaml
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

### Matrix testing (multiple Python versions)

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
```

## Workflow

1. Create `.pre-commit-config.yaml`
2. Add tool configs to `pyproject.toml`
3. Create `setup.cfg` for flake8
4. Create `.github/workflows/ci.yml`
5. Run `pre-commit install`
6. Run `pre-commit run --all-files` to verify
