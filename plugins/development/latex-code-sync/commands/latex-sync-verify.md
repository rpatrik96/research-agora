---
name: latex-sync-verify
description: Run verification between paper equations and code implementations. Use when asked to "verify equations", "check paper-code consistency", "run equation tests", or "validate implementations match paper".
model: sonnet
---

# Verify Equation-Code Consistency

> **Script-first**: This skill runs the latex-code-sync CLI tool. LLM assists only with interpreting failures.

Run latex-code-sync verification to ensure paper equations match their code implementations.

## Quick Verification

```bash
# Basic verification
latex-code-sync verify --latex-dir=paper/ --modules=equations

# Strict mode (fail on any issue)
latex-code-sync verify --latex-dir=paper/ --modules=equations --strict

# Verbose output
latex-code-sync verify --latex-dir=paper/ --modules=equations -v

# Multiple modules
latex-code-sync verify --latex-dir=paper/ --modules=equations,models.loss,utils.math
```

## Verification Checks

| Check | Description | Example Issue |
|-------|-------------|---------------|
| **Label exists** | `\label{eq:X}` found in LaTeX | Typo in decorator |
| **Function registered** | `@latex("eq:X")` decorator present | Missing import |
| **Test cases pass** | Test inputs produce expected outputs | Implementation bug |
| **Dependencies valid** | All `depends` labels exist | Removed equation |
| **Notation consistent** | Symbol mappings are plausible | Parameter renamed |

## Interpreting Results

### Success
```
✓ eq:energy - PASSED (3 test cases)
✓ eq:weights - PASSED (2 test cases)
✓ eq:uncertainty - PASSED (2 test cases)

Verification complete: 3/3 equations passed
```

### Failure
```
✗ eq:energy - FAILED
  Test case 1: Expected 0.0, got 0.5
  
  Inputs: phi_patch=zeros(9), library_patch=zeros(9), alpha_bar_t=0.5
  Code: equations.py:45 els_energy()
  Paper: main.tex:67 \label{eq:energy}
  
  Possible causes:
  - Formula mismatch: check normalization factor
  - Parameter interpretation differs
```

### Missing Label
```
⚠ eq:beta-def - Label not found in LaTeX
  Decorator at: equations.py:89
  Searched: paper/*.tex
  
  Did you mean: eq:beta (found in appendix.tex:234)?
```

## Local Verification Workflow

### 1. Quick Check (Python only)
```python
# Run the equations module directly
python equations.py

# Or in Python
import equations
from latex_code_sync import get_registry, verify_all

registry = get_registry()
results = verify_all(registry)
for label, result in results.items():
    print(f"{label}: {'PASS' if result.passed else 'FAIL'}")
```

### 2. Full Verification (with LaTeX)
```bash
# Clone/locate paper repo
git clone https://github.com/user/paper-repo paper/

# Run verification
latex-code-sync verify --latex-dir=paper/ --modules=equations
```

### 3. CI Verification
```bash
# Simulates CI environment
PAPER_DIR=paper/ latex-code-sync verify --modules=equations --strict
```

## Debugging Failures

### Test Case Failures

```python
# Add debugging to test case
@latex(
    "eq:energy",
    test_cases=[{
        "inputs": {"x": torch.tensor([1.0])},
        "expected": 1.0,
        "debug": True,  # Print intermediate values
    }]
)
```

### Manual Verification
```python
# Test function manually
from equations import els_energy
import torch

phi = torch.zeros(9)
lib = torch.zeros(9)
alpha = 0.5

result = els_energy(phi, lib, alpha)
print(f"Result: {result}")
print(f"Expected: 0.0")
print(f"Match: {abs(result - 0.0) < 1e-6}")
```

### Compare with Paper Formula

```python
# Paper: E = ||φ - √α·lib||² / (2(1-α))
def paper_formula(phi, lib, alpha):
    diff = phi - math.sqrt(alpha) * lib
    return (diff ** 2).sum() / (2 * (1 - alpha))

# Code implementation
def code_implementation(phi, lib, alpha):
    return els_energy(phi, lib, alpha)

# Compare
phi = torch.randn(9)
lib = torch.randn(9)
alpha = 0.5

paper_result = paper_formula(phi, lib, alpha)
code_result = code_implementation(phi, lib, alpha)
print(f"Paper: {paper_result:.6f}")
print(f"Code: {code_result:.6f}")
print(f"Diff: {abs(paper_result - code_result):.2e}")
```

## Common Issues and Fixes

### Issue: Numerical Precision
```python
# Increase tolerance
test_cases=[{
    "inputs": {...},
    "expected": 0.333333,
    "tolerance": 1e-5,  # Default is 1e-6
}]
```

### Issue: Tensor Shape Mismatch
```python
# Ensure consistent shapes in test
test_cases=[{
    "inputs": {"x": torch.tensor([1.0, 2.0])},  # Shape: (2,)
    "expected": torch.tensor([0.5, 1.0]),       # Must match shape
}]
```

### Issue: Random Initialization
```python
# Set seed for reproducibility
@latex("eq:x", test_cases=[...])
def func_with_randomness(x):
    torch.manual_seed(42)  # Fixed seed
    return ...
```

### Issue: Device Mismatch
```python
# Force CPU for tests
test_cases=[{
    "inputs": {"x": torch.tensor([1.0]).cpu()},
    "expected": torch.tensor([1.0]).cpu(),
}]
```

## Generating Verification Reports

```bash
# Markdown report
latex-code-sync report --latex-dir=paper/ --modules=equations -o report.md

# JSON for CI
latex-code-sync verify --latex-dir=paper/ --modules=equations --json > results.json
```

### Report Format
```markdown
# Equation Verification Report

## Summary
- Total equations: 12
- Passed: 10
- Failed: 1
- Skipped: 1

## Details

### eq:energy ✓
- File: equations.py:45
- Tests: 3/3 passed
- Notation: φ_Ω → phi_patch, α̅ → alpha_bar_t

### eq:weights ✗
- File: equations.py:67
- Tests: 1/2 failed
- Error: Test 2 expected [0.5, 0.5], got [0.499, 0.501]
```
