---
name: _template
description: |
  Template for creating new micro-skills. Micro-skills are atomic, parallelizable
  operations that operate on scoped input and produce structured JSON output.
  Copy this file and customize for your specific skill.
model: haiku
color: gray
---

# Micro-Skill: [Name]

> **One-line description**: [What this skill does in one sentence]

## WORKER PROTOCOL

You are a **LEAF AGENT** in a multi-agent orchestration system.

**CONSTRAINTS**:
1. **DO NOT** spawn subagents or delegate work via Task()
2. **DO NOT** ask clarifying questions—work with the input provided
3. **DO** execute your specific operation and return structured JSON
4. **DO** fail gracefully with `{"error": "...", "code": "..."}` if blocked
5. **DO** stay within your designated scope—no scope expansion

You receive scoped input. You return scoped output. Nothing more.

---

## Purpose

[2-3 sentences explaining when to use this skill and what problem it solves]

## Model Routing

This skill is configured in `config/model-routing.json`:

```json
{
  "[skill-name]": {
    "model": "haiku|sonnet|opus",
    "temperature": 0.1,
    "reason": "[Why this model was chosen]"
  }
}
```

## Parallelization Properties

| Property | Value | Notes |
|----------|-------|-------|
| **Input scope** | [Single claim / Single section / Claim batch] | What unit this operates on |
| **State requirements** | [Stateless / Needs research-state.json] | External state needed |
| **External calls** | [None / arXiv / GitHub / Other MCP] | API dependencies |
| **Typical runtime** | [<10s / 10-60s / >60s] | Expected execution time |
| **Can run in parallel** | [Yes / No / Conditional] | Safe for concurrent execution |
| **Idempotent** | [Yes / No] | Same input → same output |

## Input Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["required_field1"],
  "properties": {
    "required_field1": {
      "type": "string",
      "description": "Description of this field"
    },
    "optional_field": {
      "type": "string",
      "description": "Optional field with default",
      "default": "default_value"
    }
  }
}
```

### Example Input

```json
{
  "required_field1": "example value",
  "optional_field": "custom value"
}
```

## Output Specification

All outputs MUST follow this structure:

### Success Response

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["result", "confidence"],
  "properties": {
    "result": {
      "type": "object",
      "description": "The skill-specific result payload"
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Confidence in the result (0.0-1.0)"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "processing_time_ms": {"type": "integer"},
        "assumptions": {"type": "array", "items": {"type": "string"}},
        "warnings": {"type": "array", "items": {"type": "string"}}
      }
    }
  }
}
```

### Error Response

```json
{
  "type": "object",
  "required": ["error", "code"],
  "properties": {
    "error": {
      "type": "string",
      "description": "Human-readable error message"
    },
    "code": {
      "type": "string",
      "enum": ["INVALID_INPUT", "TIMEOUT", "SERVICE_UNAVAILABLE", "SCOPE_EXCEEDED", "CONFIDENCE_LOW", "PARTIAL_RESULT"],
      "description": "Machine-readable error code"
    },
    "details": {
      "type": "object",
      "description": "Additional error context"
    }
  }
}
```

### Example Success Output

```json
{
  "result": {
    "extracted_value": "example output"
  },
  "confidence": 0.85,
  "metadata": {
    "processing_time_ms": 150,
    "assumptions": ["Assumed standard formatting"],
    "warnings": []
  }
}
```

### Example Error Output

```json
{
  "error": "Missing required field 'section_text'",
  "code": "INVALID_INPUT",
  "details": {
    "missing_fields": ["section_text"],
    "received_fields": ["section_id"]
  }
}
```

## Algorithm

1. **Step 1: Validate Input**
   - Check all required fields present
   - Validate types match schema
   - Return `INVALID_INPUT` error if validation fails

2. **Step 2: [Core Operation]**
   - Sub-step a
   - Sub-step b

3. **Step 3: [Secondary Operation]**
   - Details...

4. **Step 4: Construct Output**
   - Build result object
   - Calculate confidence score
   - Add metadata (timing, assumptions, warnings)

## Confidence Scoring

| Condition | Confidence Impact |
|-----------|-------------------|
| [High-quality signal] | +0.2 |
| [Ambiguous input] | -0.2 |
| [Missing optional context] | -0.1 |
| [External verification successful] | +0.1 |

Base confidence: 0.7. Adjust based on conditions above. Clamp to [0.0, 1.0].

## Constraints

### DO
- ✅ Execute the specific operation defined in this skill
- ✅ Return structured JSON matching the output schema
- ✅ Include confidence scores with every result
- ✅ Document assumptions in metadata
- ✅ Fail gracefully with appropriate error codes

### DON'T
- ❌ Spawn subagents or delegate work
- ❌ Ask clarifying questions
- ❌ Expand scope beyond the input provided
- ❌ Return unstructured prose
- ❌ Hang or timeout without returning partial results
- ❌ Access resources outside your designated scope

## Error Handling

| Error Condition | Code | Response |
|-----------------|------|----------|
| Missing required input | `INVALID_INPUT` | List missing fields |
| Input type mismatch | `INVALID_INPUT` | Show expected vs actual |
| External API unavailable | `SERVICE_UNAVAILABLE` | Specify which service |
| Task exceeds time limit | `TIMEOUT` | Return partial results if possible |
| Task too large | `SCOPE_EXCEEDED` | Suggest how to split |
| Result uncertain | `CONFIDENCE_LOW` | Include result with low confidence |

## Context Requirements

This skill requires the following context to be provided by the orchestrator:

| Context Item | Required | Source | Purpose |
|--------------|----------|--------|---------|
| [Item 1] | Yes | research-state.json | [Why needed] |
| [Item 2] | No | Paper text | [Why helpful] |
| [Item 3] | No | Previous skill output | [Dependency] |

## Examples

### Example 1: [Normal Case]

**Scenario**: [Brief description of typical usage]

**Input**:
```json
{
  "required_field1": "typical value"
}
```

**Output**:
```json
{
  "result": {
    "extracted_value": "typical output"
  },
  "confidence": 0.9,
  "metadata": {
    "processing_time_ms": 100,
    "assumptions": [],
    "warnings": []
  }
}
```

**Explanation**: [Why this output is correct]

### Example 2: [Edge Case]

**Scenario**: [Brief description of edge case]

**Input**:
```json
{
  "required_field1": "edge case value"
}
```

**Output**:
```json
{
  "result": {
    "extracted_value": "handled output"
  },
  "confidence": 0.6,
  "metadata": {
    "processing_time_ms": 250,
    "assumptions": ["Assumed X due to ambiguity"],
    "warnings": ["Input was ambiguous, confidence reduced"]
  }
}
```

**Explanation**: [How edge case is handled, why confidence is lower]

### Example 3: [Error Case]

**Scenario**: [Brief description of error condition]

**Input**:
```json
{
  "wrong_field": "value"
}
```

**Output**:
```json
{
  "error": "Missing required field 'required_field1'",
  "code": "INVALID_INPUT",
  "details": {
    "missing_fields": ["required_field1"],
    "received_fields": ["wrong_field"]
  }
}
```

**Explanation**: [Why this is an error, what caller should do]

## Integration Notes

### Called By
- `parallel-audit` orchestrator (for [use case])
- `parallel-review` orchestrator (for [use case])

### Calls
- None (leaf agent—no delegation)
- MCP tools used: [list any mcp__* tools]

### State Updates
- Reads: `research-state.json` fields [list fields]
- Writes: None (orchestrator handles state updates)

### Dependencies
- Requires output from: [list prerequisite skills, if any]
- Required by: [list dependent skills, if any]

---

## Checklist for New Micro-Skills

Before submitting a new micro-skill, verify:

- [ ] Includes WORKER PROTOCOL section at the top
- [ ] Model routing specified in `config/model-routing.json`
- [ ] Input/output schemas are complete and valid JSON Schema
- [ ] At least 3 examples provided (normal, edge case, error)
- [ ] Algorithm is clear and step-by-step
- [ ] Constraints explicitly state what NOT to do
- [ ] Error handling covers all standard error codes
- [ ] Context requirements are documented
- [ ] Parallelization properties are accurate
- [ ] Confidence scoring logic is documented
- [ ] Skill has been tested manually
- [ ] No delegation/subagent spawning in implementation
