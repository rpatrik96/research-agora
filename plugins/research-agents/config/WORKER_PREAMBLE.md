# Worker Preamble Protocol

> **Inspired by**: oh-my-claudecode's Worker Preamble Protocol
> **Purpose**: Ensure clean execution without runaway delegation chains

This preamble MUST be included in all micro-skills and worker agents. It establishes the contract that workers are **leaf nodes** in the orchestration tree.

## The Protocol

```markdown
## WORKER PROTOCOL

You are a **LEAF AGENT** in a multi-agent orchestration system.

### CONSTRAINTS

1. **NO DELEGATION**: Do NOT spawn subagents or use Task() to delegate work.
   - You receive a scoped task
   - You execute that task directly
   - You return structured output

2. **NO CLARIFICATION**: Do NOT ask clarifying questions.
   - Work with the input you receive
   - If input is ambiguous, make reasonable assumptions
   - Document assumptions in your output

3. **SCOPED EXECUTION**: Stay within your designated scope.
   - If asked to grade evidence for claim C1, grade ONLY C1
   - Do not proactively analyze other claims
   - Do not expand scope without explicit instruction

4. **STRUCTURED OUTPUT**: Always return JSON matching your output schema.
   - Success: `{"result": ..., "confidence": 0.X, ...}`
   - Failure: `{"error": "description", "code": "ERROR_CODE"}`
   - Never return unstructured prose

5. **FAIL GRACEFULLY**: If blocked, return error JSON, don't hang.
   - Timeout approaching? Return partial results with `"partial": true`
   - Missing input? Return `{"error": "Missing required field X", "code": "INVALID_INPUT"}`
   - External service down? Return `{"error": "arXiv unavailable", "code": "SERVICE_UNAVAILABLE"}`

### WHAT YOU RECEIVE

- **Scoped input**: Only the data needed for your specific task
- **Context**: Minimal context from research-state.json (not full paper)
- **Timeout**: You have limited time; optimize for completion

### WHAT YOU RETURN

- **Structured JSON**: Matching your skill's output schema
- **Confidence score**: 0.0-1.0 indicating certainty
- **Metadata**: Processing stats, assumptions made, warnings
```

## Implementation

### For Micro-Skills

Add this section to every micro-skill markdown file after the frontmatter:

```markdown
---
name: claim-extractor
model: haiku
---

# Claim Extractor

[Description...]

## WORKER PROTOCOL

You are a **LEAF AGENT**. Your constraints:

1. **DO NOT** spawn subagents or delegate work
2. **DO NOT** ask clarifying questions—work with what you have
3. **DO** execute your specific operation and return structured JSON
4. **DO** fail gracefully with `{"error": "...", "code": "..."}` if blocked

You receive scoped input. You return scoped output. Nothing more.

---

[Rest of skill definition...]
```

### For Orchestrators

Orchestrators should wrap tasks with the preamble when delegating:

```python
def wrap_with_preamble(task_description: str) -> str:
    """Wrap a task description with the worker preamble."""
    preamble = """
IMPORTANT: You are a LEAF AGENT executing a scoped task.
- Do NOT spawn subagents or delegate
- Do NOT ask questions—execute with given input
- Return structured JSON only
- Fail gracefully if blocked

YOUR TASK:
"""
    return preamble + task_description
```

## Rationale

### Why prevent sub-spawning?

Without this constraint:
```
orchestrator → executor → "hmm, complex" → spawns architect
                                         → architect → "needs research" → spawns researcher
                                                                        → researcher → ...
```

This creates:
1. **Unpredictable costs**: Each spawn multiplies token usage
2. **Lost context**: Sub-sub-agents lack original context
3. **Infinite loops**: Circular delegation possible
4. **Timeout failures**: Deep chains exceed time limits

With the protocol:
```
orchestrator → [claim-extractor, evidence-grader, novelty-checker] → merge results
               └── each is a LEAF, returns directly to orchestrator
```

### Why no clarification?

Research micro-skills receive pre-processed, scoped input. If a claim-extractor receives section text, it should extract claims—not ask "what kind of claims?" The orchestrator already made that decision.

Clarification questions:
1. Break the parallel execution model (waiting for human input)
2. Indicate insufficient context (orchestrator's job to provide)
3. Slow down the pipeline

### Why structured output?

Orchestrators must merge results from multiple subagents. Unstructured prose cannot be:
- Programmatically parsed
- Validated against schema
- Merged with other results
- Cached for reuse

## Error Codes

Standard error codes for micro-skills:

| Code | Meaning | Orchestrator Action |
|------|---------|---------------------|
| `INVALID_INPUT` | Missing or malformed input | Log, skip this task |
| `TIMEOUT` | Task took too long | Retry once, then skip |
| `SERVICE_UNAVAILABLE` | External API down (arXiv, etc.) | Retry with backoff |
| `SCOPE_EXCEEDED` | Task too large for single skill | Split and re-delegate |
| `CONFIDENCE_LOW` | Result uncertain | Flag for human review |
| `PARTIAL_RESULT` | Incomplete due to constraints | Merge what's available |

## Verification

Orchestrators should verify worker compliance:

```python
def verify_worker_response(response: dict, skill_name: str) -> bool:
    """Verify that a worker response follows the protocol."""
    # Must be valid JSON (already parsed if we're here)

    # Must have either result or error
    if "result" not in response and "error" not in response:
        log_warning(f"{skill_name} returned neither result nor error")
        return False

    # If error, must have code
    if "error" in response and "code" not in response:
        log_warning(f"{skill_name} error missing code")
        return False

    # Should have confidence for successful results
    if "result" in response and "confidence" not in response:
        log_warning(f"{skill_name} missing confidence score")
        # Don't fail, just warn

    return True
```

## References

- oh-my-claudecode: `wrapWithPreamble()` in `src/agents/preamble.ts`
- Claude Code sub-agent architecture documentation
- Multi-agent orchestration best practices
