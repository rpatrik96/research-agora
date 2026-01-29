# Research Agent Configuration

This directory contains configuration files for the research agent orchestration system.

## Files

| File | Purpose |
|------|---------|
| `model-routing.json` | Model assignment and execution mode configuration |
| `WORKER_PREAMBLE.md` | Protocol for leaf agents (prevents runaway delegation) |

## Model Routing

The `model-routing.json` file controls which Claude model handles each skill:

```
┌─────────────────────────────────────────────────────────────────┐
│                    TASK COMPLEXITY SPECTRUM                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  HAIKU (Fast, Cheap)         SONNET (Balanced)      OPUS (Deep) │
│  ────────────────────       ─────────────────      ──────────── │
│  • claim-extractor          • evidence-grader      • cross-ref  │
│  • claim-classifier         • novelty-checker      • orchestrat │
│  • evidence-locator         • assumption-surfacer  • thorough   │
│  • citation-verifier        • context-compactor      reviews    │
│  • batch-arxiv              • state-generator                   │
│                                                                  │
│  Pattern matching           Judgment required       Synthesis    │
│  Fixed taxonomies           Nuanced comparison      Coordination │
│  Mechanical lookup          Implicit reasoning      High stakes  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Cost Implications

| Model | Typical Task Cost | Use When |
|-------|-------------------|----------|
| Haiku | ~$0.01 | Deterministic operations, no judgment |
| Sonnet | ~$0.05 | Quality judgment, semantic comparison |
| Opus | ~$0.15 | Complex coordination, holistic analysis |

### Execution Modes

Four predefined modes balance speed, cost, and quality:

| Mode | Concurrent Agents | Model Strategy | Best For |
|------|-------------------|----------------|----------|
| `parallel` | 5 | Default routing | Large papers, time pressure |
| `pipeline` | Stage-dependent | Default routing | Methodical, thorough analysis |
| `eco` | 3 | Downgrade to Haiku | Budget constraints, drafts |
| `thorough` | 3 | Upgrade to Opus | Final reviews, critical papers |

### Usage

Orchestrators read the config at startup:

```python
import json
from pathlib import Path

config_path = Path(__file__).parent / "config" / "model-routing.json"
with open(config_path) as f:
    routing_config = json.load(f)

# Get model for a skill
def get_model_for_skill(skill_name: str, mode: str = "parallel") -> str:
    rules = routing_config["routing_rules"]

    # Find skill in any category
    for category in ["micro-skills", "orchestrators", "helpers"]:
        if skill_name in rules.get(category, {}):
            default_model = rules[category][skill_name]["model"]

            # Check for mode override
            mode_config = routing_config["execution_modes"].get(mode, {})
            overrides = mode_config.get("model_overrides", {})

            return overrides.get(skill_name, default_model)

    return "sonnet"  # Fallback
```

## Worker Preamble Protocol

The `WORKER_PREAMBLE.md` file defines the protocol that prevents infinite delegation chains.

### Problem Solved

Without the protocol:
```
orchestrator → executor → "hmm, complex" → spawns architect → spawns researcher → ...
```

With the protocol:
```
orchestrator → [claim-extractor, evidence-grader, novelty-checker] (all leaf nodes)
            ↓
       merge results
```

### Key Rules

1. **Leaf agents don't spawn**: Workers execute and return, never delegate
2. **No clarification questions**: Work with provided input or fail gracefully
3. **Structured output only**: JSON matching schema, no prose
4. **Graceful failure**: Return error JSON, don't hang

### Integration

All micro-skills must include this section after frontmatter:

```markdown
## WORKER PROTOCOL

You are a **LEAF AGENT** in a multi-agent orchestration system.

**CONSTRAINTS**:
1. **DO NOT** spawn subagents or delegate work via Task()
2. **DO NOT** ask clarifying questions—work with the input provided
3. **DO** execute your specific operation and return structured JSON
4. **DO** fail gracefully with `{"error": "...", "code": "..."}` if blocked
```

## Inspiration

This configuration system is inspired by [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode):

- **Model routing**: Adapted from their complexity-based Haiku/Sonnet/Opus routing
- **Worker preamble**: Based on their `wrapWithPreamble()` pattern
- **Execution modes**: Similar to their Ultrapilot/Ecomode/Pipeline concepts

Key differences for research tasks:
- Operation-based skills (not role-based agents)
- Structured intermediate state (`research-state.json`)
- Research-specific primitives (claims, evidence, citations)

## Schema Validation

The `model-routing.json` file is validated against `schemas/model-routing.schema.json`:

```bash
# Validate config
python -c "
import json
from jsonschema import validate

with open('schemas/model-routing.schema.json') as f:
    schema = json.load(f)
with open('plugins/research-agents/config/model-routing.json') as f:
    config = json.load(f)
validate(instance=config, schema=schema)
print('✓ Config is valid')
"
```

## Modifying Configuration

### Adding a New Skill

1. Add routing rule to `model-routing.json`:
   ```json
   "micro-skills": {
     "new-skill": {
       "model": "haiku",
       "temperature": 0.1,
       "reason": "Why this model"
     }
   }
   ```

2. Include WORKER PROTOCOL in the skill's markdown file

3. Add to pipeline stages if applicable

### Changing Execution Modes

1. Modify `execution_modes` in `model-routing.json`
2. Test with sample papers across modes
3. Update cost multipliers if model mix changes

### Overriding for Specific Tasks

Orchestrators can override at runtime:

```python
# Force thorough mode for this paper
result = await parallel_audit(
    paper_path="important_paper.tex",
    mode="thorough",
    model_override={"cross-referencer": "opus"}  # Extra override
)
```
