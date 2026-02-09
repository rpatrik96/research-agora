#!/usr/bin/env python3
"""
Scaffold a new skill file with full frontmatter template.

Usage:
    python scripts/create-skill.py --name my-skill --category academic
    python scripts/create-skill.py --name my-skill --category development --type automation --domain ml
    python scripts/create-skill.py --name my-agent --category research-agents --kind agent
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"
REGISTRY_DIR = REPO_ROOT / "registry"

VALID_CATEGORIES = ["academic", "development", "formatting", "office", "research-agents"]
VALID_KINDS = ["command", "agent", "micro-skill", "orchestrator", "helper"]


def load_categories() -> dict:
    """Load valid category values from registry/categories.json."""
    cat_path = REGISTRY_DIR / "categories.json"
    if cat_path.exists():
        with open(cat_path) as f:
            return json.load(f)
    return {
        "research-domains": ["general"],
        "task-types": ["writing"],
        "research-phases": ["paper-writing"],
        "verification-levels": ["none"],
    }


def generate_command_template(name: str, domain: str, task_type: str,
                               phase: str, verification: str, model: str) -> str:
    """Generate a command skill template."""
    return f"""---
name: {name}
description: |
  Brief description of what this skill does. Use when asked to
  "trigger phrase 1", "trigger phrase 2", "trigger phrase 3".
model: {model}
metadata:
  research-domain: {domain}
  task-type: {task_type}
  research-phase: {phase}
  verification-level: {verification}
---

# {name.replace('-', ' ').title()}

> **LLM-required / Script-first / Hybrid**: Describe whether this skill needs LLM judgment,
> can be done with scripts, or uses a hybrid approach.

Brief description of what this skill does and when to use it.

## Workflow

1. Step one
2. Step two
3. Step three

## Examples

Include concrete examples with code blocks.

## Output Format

Specify the expected output format.
"""


def generate_agent_template(name: str, domain: str, task_type: str,
                             phase: str, verification: str, model: str) -> str:
    """Generate an agent skill template."""
    return f"""---
name: {name}
description: |
  Brief description for the Task tool. Use this agent to...
  Activates when asked to "trigger 1", "trigger 2", "trigger 3".
model: {model}
color: yellow
metadata:
  research-domain: {domain}
  task-type: {task_type}
  research-phase: {phase}
  verification-level: {verification}
---

> **LLM-required**: Describe why this agent needs LLM judgment.

You are a {name.replace('-', ' ').title()} Agent. Your purpose is to...

## Workflow

1. Step one
2. Step two
3. Step three

## Output Format

Specify the expected output format.

## Principles

- Principle one
- Principle two
"""


def main():
    categories = load_categories()

    parser = argparse.ArgumentParser(description="Scaffold a new skill file")
    parser.add_argument("--name", required=True, help="Skill name (kebab-case)")
    parser.add_argument("--category", required=True, choices=VALID_CATEGORIES,
                        help="Plugin category")
    parser.add_argument("--kind", default="command", choices=VALID_KINDS,
                        help="Skill kind (default: command)")
    parser.add_argument("--domain", default="general",
                        choices=categories["research-domains"],
                        help="Research domain")
    parser.add_argument("--type", default="writing", dest="task_type",
                        choices=categories["task-types"],
                        help="Task type")
    parser.add_argument("--phase", default="paper-writing",
                        choices=categories["research-phases"],
                        help="Research phase")
    parser.add_argument("--verification", default="none",
                        choices=categories["verification-levels"],
                        help="Verification level")
    parser.add_argument("--model", default="sonnet",
                        choices=["opus", "sonnet", "haiku"],
                        help="Model tier (default: sonnet)")

    args = parser.parse_args()

    # Determine output path
    if args.category == "research-agents":
        kind_dirs = {
            "agent": "agents",
            "micro-skill": "micro-skills",
            "orchestrator": "orchestrators",
            "helper": "helpers",
            "command": "agents",  # default to agents for research-agents
        }
        subdir = kind_dirs.get(args.kind, "agents")
        output_dir = PLUGINS_DIR / "research-agents" / subdir
    else:
        output_dir = PLUGINS_DIR / args.category / "commands"

    output_path = output_dir / f"{args.name}.md"

    if output_path.exists():
        print(f"Error: {output_path.relative_to(REPO_ROOT)} already exists")
        sys.exit(1)

    # Generate template
    if args.kind in ("agent", "micro-skill", "orchestrator", "helper"):
        content = generate_agent_template(
            args.name, args.domain, args.task_type,
            args.phase, args.verification, args.model,
        )
    else:
        content = generate_command_template(
            args.name, args.domain, args.task_type,
            args.phase, args.verification, args.model,
        )

    # Write
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content)
    print(f"Created {output_path.relative_to(REPO_ROOT)}")
    print()
    print("Next steps:")
    print(f"  1. Edit {output_path.relative_to(REPO_ROOT)} with your skill instructions")
    print("  2. Run: pytest tests/")
    print("  3. Run: python scripts/generate-registry.py")


if __name__ == "__main__":
    main()
