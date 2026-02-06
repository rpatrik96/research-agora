---
name: code-simplify
description: Analyze and refactor Python codebases to remove dead code, eliminate duplication, and simplify complexity. Use when asked to "simplify code", "remove dead code", "find duplicates", "refactor", "clean up codebase", or "reduce complexity".
model: sonnet
---

# Code Simplification

Analyze and refactor Python code to reduce complexity, remove dead code, and eliminate duplication.

> **Script-first**: Run static analysis tools first to produce concrete, actionable findings. Use LLM only to interpret results and plan refactorings that tools cannot automate.

## Workflow

1. **Run all analysis tools** - Collect script-based findings first
2. **Review tool output** - Present findings to user
3. **LLM analysis** - Identify patterns tools miss, plan refactorings
4. **Apply changes** - Refactor with test verification

## Step 1: Run Analysis Tools

Run these commands first to gather concrete data before any manual analysis:

```bash
# Install tools if needed
pip install flake8 vulture pylint radon 2>/dev/null

# === Dead Code Detection ===
flake8 --select=F401,F841,F811 .        # Unused imports, variables, redefined
vulture src/ --min-confidence 80         # Comprehensive dead code detection

# === Duplication Detection ===
pylint --disable=all --enable=duplicate-code src/

# === Complexity Measurement ===
radon cc src/ -a -s   # Cyclomatic complexity
radon mi src/ -s       # Maintainability index
```

## Step 2: Interpret Tool Output

Present tool findings directly to user. Only supplement with manual inspection for patterns tools miss:

- Conditional branches that never execute (`if False:`, `if DEBUG:` in prod)
- Exception handlers that catch impossible exceptions
- Commented-out code blocks
- TODO/FIXME markers with stale code

### Duplication patterns (for LLM-assisted refactoring)

| Pattern | Refactoring |
|---------|-------------|
| Similar functions with minor differences | Extract common logic, use parameters |
| Repeated validation logic | Create validator decorator/function |
| Copy-pasted class methods | Extract base class or mixin |
| Repeated try/except blocks | Create context manager |
| Similar data transformations | Create generic transform function |

## Complexity Thresholds

- **Cyclomatic complexity**: ≤10 per function (refactor if >15)
- **Function length**: ≤50 lines (refactor if >100)
- **Parameters**: ≤5 per function (use dataclass/config if more)
- **Nesting depth**: ≤3 levels (refactor if >4)

### Simplification patterns

```python
# BEFORE: Deep nesting
def process(data):
    if data:
        if data.valid:
            if data.ready:
                return transform(data)
    return None

# AFTER: Guard clauses
def process(data):
    if not data or not data.valid or not data.ready:
        return None
    return transform(data)
```

```python
# BEFORE: Complex conditional
if (a and b) or (a and c) or (a and d):
    ...

# AFTER: Factored
if a and (b or c or d):
    ...
```

```python
# BEFORE: Repeated attribute access
result = obj.data.items.first.value + obj.data.items.second.value

# AFTER: Local variable
items = obj.data.items
result = items.first.value + items.second.value
```

## Refactoring Checklist

### Before refactoring
- [ ] Ensure tests exist and pass
- [ ] Commit current state
- [ ] Identify scope of changes

### During refactoring
- [ ] Make one logical change at a time
- [ ] Run tests after each change
- [ ] Keep commits atomic

### Common refactorings
- **Extract function**: Pull repeated code into function
- **Extract variable**: Name complex expressions
- **Inline function**: Remove trivial wrappers
- **Rename**: Improve clarity
- **Move**: Relocate to appropriate module
- **Replace conditional with polymorphism**: Use strategy pattern

## Output Format

When analyzing code, provide:

```markdown
## Dead Code Found
- `module.py:45` - Function `unused_helper` never called
- `utils.py:12-30` - Class `LegacyParser` not instantiated

## Duplications
- `api.py:20-35` ≈ `handlers.py:45-60` (90% similar)
  Recommendation: Extract to `common.validate_request()`

## High Complexity
- `process.py:main_handler` - CC=18 (target: ≤10)
  Recommendation: Split into `parse_input`, `transform`, `format_output`

## Recommended Actions
1. Remove `unused_helper` (safe, no usages)
2. Extract validation logic to reduce duplication
3. Refactor `main_handler` using guard clauses
```
