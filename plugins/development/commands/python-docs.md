---
name: python-docs
description: Generate NumPy-style docstrings with type hints for Python code. Use when asked to document Python functions, classes, modules, or entire codebases. Triggers on requests like "document this code", "add docstrings", "generate documentation", or "add type hints".
model: sonnet
---

# Python Documentation Generator

Generate comprehensive NumPy-style docstrings with type hints in both signatures and docstrings.

## Docstring Format

```python
def function_name(
    param1: str,
    param2: int = 10,
    *args: tuple[Any, ...],
    **kwargs: dict[str, Any],
) -> ReturnType:
    """Short one-line summary (imperative mood).

    Extended description if needed. Explain what the function does,
    not how it does it.

    Parameters
    ----------
    param1 : str
        Description of param1.
    param2 : int, default=10
        Description of param2.
    *args : tuple[Any, ...]
        Description of variable positional arguments.
    **kwargs : dict[str, Any]
        Description of keyword arguments.

    Returns
    -------
    ReturnType
        Description of return value.

    Raises
    ------
    ValueError
        When param1 is empty.
    TypeError
        When param2 is not an integer.

    Examples
    --------
    >>> function_name("hello", 5)
    ExpectedOutput

    Notes
    -----
    Optional section for implementation notes or algorithms.

    See Also
    --------
    related_function : Brief description.
    """
```

## Class Docstring Format

```python
class ClassName:
    """Short summary of class purpose.

    Extended description of class behavior and usage.

    Parameters
    ----------
    param1 : type
        Description (for __init__ parameters).

    Attributes
    ----------
    attr1 : type
        Description of instance attribute.
    attr2 : type
        Description of instance attribute.

    Examples
    --------
    >>> obj = ClassName(param1)
    >>> obj.method()
    """
```

## Workflow

1. **Analyze** - Parse the code to identify functions, classes, methods
2. **Infer types** - Determine types from usage, defaults, and context
3. **Generate docstrings** - Create NumPy-style docstrings
4. **Add type hints** - Add hints to signatures (use `from __future__ import annotations` for forward refs)
5. **Validate** - Ensure docstrings match actual parameters

## Type Hint Guidelines

- Use `from __future__ import annotations` at module top for forward references
- Use `typing` module types: `Optional`, `Union`, `Callable`, `TypeVar`, etc.
- Use `collections.abc` for abstract types: `Sequence`, `Mapping`, `Iterable`
- Prefer `X | None` over `Optional[X]` (Python 3.10+)
- Use `TypeAlias` for complex type definitions
- Add `-> None` explicitly for functions that return nothing

## Section Order

1. Short summary (required)
2. Extended summary (optional)
3. Parameters (if any)
4. Returns / Yields (if applicable)
5. Raises (if any)
6. Examples (recommended)
7. Notes (optional)
8. See Also (optional)
9. References (optional)

## Common Patterns

### Properties
```python
@property
def name(self) -> str:
    """str: Short description of the property."""
    return self._name
```

### Generators
```python
def generate_items(n: int) -> Iterator[Item]:
    """Generate n items.

    Yields
    ------
    Item
        The next item in sequence.
    """
```

### Context Managers
```python
def open_resource(path: str) -> ContextManager[Resource]:
    """Open a resource for processing.

    Yields
    ------
    Resource
        The opened resource, automatically closed on exit.
    """
```
