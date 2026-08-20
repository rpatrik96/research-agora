#!/usr/bin/env python3
"""Research Agora onboarding script.

Interactive CLI that interviews users, classifies their tier, generates a
personalized CLAUDE.md, and recommends skills + a 5-minute first win.

Runs standalone (no LLM needed). Can also be invoked by the /onboard skill
for optional LLM-based personalization on top.

Usage:
    python3 scripts/onboard.py                # interactive interview
    python3 scripts/onboard.py --detect       # auto-detect from project
    python3 scripts/onboard.py --tier 2       # skip interview, use tier directly
    python3 scripts/onboard.py --json         # output structured JSON (for skill wrapper)
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from textwrap import dedent

# ---------------------------------------------------------------------------
# Interview questions
# ---------------------------------------------------------------------------

QUESTIONS = {
    "cli": {
        "prompt": "What's your command line comfort level?",
        "options": {
            "a": "I avoid it entirely",
            "b": "I can cd and ls but that's about it",
            "c": "Comfortable — I use git, run scripts, install packages",
            "d": "It's my primary interface",
        },
    },
    "ai": {
        "prompt": "How do you currently use AI tools?",
        "options": {
            "a": "I haven't really",
            "b": "ChatGPT/Claude in the browser, mostly chat",
            "c": "Regularly — browser + some IDE integration (Copilot, Cursor)",
            "d": "Extensively — agentic coding, custom prompts, MCP tools, API access",
        },
    },
    "domain": {
        "prompt": "What's your research domain?",
        "free_text": True,
        "hint": "e.g., ML/AI, neuroscience, physics, biology, social sciences",
    },
    "task": {
        "prompt": "What research task is bothering you most right now?",
        "options": {
            "a": "Literature review / finding and managing papers",
            "b": "Data analysis or experiment pipelines",
            "c": "Writing code for research",
            "d": "Writing papers (drafting, editing, structuring)",
            "e": "Admin, grant writing, email, teaching prep",
            "f": "Something else",
        },
    },
    "languages": {
        "prompt": "What programming languages do you use? (skip if none)",
        "free_text": True,
        "hint": "e.g., Python, R, Julia, MATLAB",
        "optional": True,
    },
    "writing_tool": {
        "prompt": "What do you write in?",
        "free_text": True,
        "hint": "e.g., LaTeX, Overleaf, Word, Markdown",
        "optional": True,
    },
    "ref_manager": {
        "prompt": "Do you use a reference manager?",
        "free_text": True,
        "hint": "e.g., Zotero, Mendeley, BibTeX directly, none",
        "optional": True,
    },
    "git": {
        "prompt": "Is your project under version control (git)?",
        "options": {"y": "Yes", "n": "No", "s": "Skip"},
        "optional": True,
    },
}

# ---------------------------------------------------------------------------
# Tier classification
# ---------------------------------------------------------------------------

LEVEL_MAP = {"a": 0, "b": 1, "c": 2, "d": 3}


def classify_tier(answers: dict) -> int:
    """Rule-based tier classification from interview answers."""
    cli = LEVEL_MAP.get(answers.get("cli", "a"), 0)
    ai = LEVEL_MAP.get(answers.get("ai", "a"), 0)
    langs = answers.get("languages", "").strip()

    if cli <= 1 and ai <= 1:
        return 0  # Browser-only
    if cli <= 2 and ai <= 2 and langs:
        return 1  # CLI-ready, AI-curious
    if cli >= 2 and ai >= 2:
        # Check for power-user signals
        ai_text = answers.get("ai", "")
        if cli >= 3 and (ai >= 3 or "mcp" in ai_text.lower() or "agent" in ai_text.lower()):
            return 3  # Power user
        return 2  # Regular user wanting systematic workflows
    return 1  # Default


# ---------------------------------------------------------------------------
# Skill recommendations
# ---------------------------------------------------------------------------

SKILL_TABLE = {
    "a": {  # Literature
        1: [
            ("/paper-references", "Verify citations against arXiv, Crossref, DBLP"),
            ("/literature-synthesizer", "Discover literature and build a verified bibliography"),
        ],
        2: [
            ("/paper-references", "Verify citations against arXiv, Crossref, DBLP"),
            ("/literature-synthesizer", "Discover literature and build a verified bibliography"),
            ("/benchmark-scout", "Find relevant benchmarks and baselines"),
        ],
    },
    "b": {  # Data/experiments
        1: [
            ("/experiment-tracker", "Sync experiment results to paper tables"),
            ("/commit", "Write clean, conventional commits"),
        ],
        2: [
            ("/paper-verify-experiments", "Check paper claims against source code"),
            ("/experiment-tracker", "Sync experiment results to paper tables"),
            ("/benchmark-scout", "Find relevant benchmarks and baselines"),
        ],
    },
    "c": {  # Code
        1: [
            ("/commit", "Write clean, conventional commits"),
            ("/paper-verify-experiments", "Check paper claims against source code"),
        ],
        2: [
            ("/paper-verify-experiments", "Check paper claims against source code"),
            ("/experiment-tracker", "Sync experiment results to paper tables"),
        ],
    },
    "d": {  # Writing
        1: [
            ("/paper-abstract", "Diagnose an abstract you wrote"),
            ("/paper-review", "Simulate skeptical reviewer feedback"),
            ("/argument-autopsy", "Map the paper's claim-evidence structure"),
        ],
        2: [
            ("/paper-abstract", "Diagnose an abstract you wrote"),
            ("/paper-review", "Simulate skeptical reviewer feedback"),
            ("/paper-references", "Verify citations before submission"),
            ("/editorial-brain", "Context-aware editorial feedback"),
        ],
    },
    "e": {  # Admin
        1: [
            ("/paper-slides", "Generate presentation slides from paper"),
            ("/paper-poster", "Generate conference poster from paper"),
        ],
        2: [
            ("/review-triage", "Organize and prioritize reviewer comments"),
            ("/paper-slides", "Generate presentation slides"),
            ("/openreview-submission", "Format and submit to OpenReview"),
        ],
    },
}

# Default fallback for any task
DEFAULT_SKILLS = [
    ("/paper-review", "Simulate skeptical reviewer feedback"),
    ("/paper-references", "Verify citations before submission"),
    ("/choose-skill", "Interactive skill finder for your task"),
]


def get_skill_recommendations(task: str, tier: int) -> list[tuple[str, str]]:
    """Return skill recommendations based on task and tier."""
    task_skills = SKILL_TABLE.get(task, {})
    # Find best tier match (exact or lower)
    for t in range(min(tier, 3), -1, -1):
        if t in task_skills:
            return task_skills[t]
    return DEFAULT_SKILLS


# ---------------------------------------------------------------------------
# 5-minute win
# ---------------------------------------------------------------------------

FIVE_MINUTE_WINS = {
    0: dedent("""\
        Paste this into Claude.ai or ChatGPT — it's a structured prompt
        that shows what the Research Agora skills do under the hood:

        ---
        I'm writing a paper about [TOPIC] in [DOMAIN]. Diagnose my abstract:
        - Does it have all 5 parts? (context, problem, approach, results, impact)
        - Are claims specific or vague?
        - What's the weakest sentence and how would you fix it?

        [PASTE YOUR ABSTRACT]
        ---

        When you're ready to move to the CLI, come back and run /onboard again."""),
    1: dedent("""\
        Run your first skill — pick one based on your task:

          # Literature/references:
          claude "/paper-references"

          # Writing:
          claude "/paper-review"

          # Code:
          claude "/commit"

        That's it. One command, one result you can evaluate."""),
    2: dedent("""\
        Set up a verification pipeline:

          # 1. Snapshot your work
          git add -A && git commit -m "Before verification run"

          # 2. Run citation verification
          claude "/paper-references"

          # 3. Check paper-code consistency
          claude "/paper-verify-experiments"

          # 4. Get a simulated review
          claude "/paper-review"

        Before your next submission, run steps 2-4."""),
    3: dedent("""\
        You know the tools. Here's what scales:

        - Package one of your existing workflows as a skill and submit a PR
        - Explore research-agents: 22 agents for parallel claim verification,
          devil's advocate analysis, audience checking
        - Use CLAUDE.md as a governance document — encode your lab's standards"""),
}


# ---------------------------------------------------------------------------
# CLAUDE.md generation
# ---------------------------------------------------------------------------


def generate_claude_md(answers: dict, tier: int) -> str:
    """Generate a personalized CLAUDE.md from interview answers."""
    domain = answers.get("domain", "Research")
    langs = answers.get("languages", "")
    writing_tool = answers.get("writing_tool", "")
    ref_manager = answers.get("ref_manager", "")
    uses_git = answers.get("git", "y") in ("y", "Y", "yes")
    task = answers.get("task", "d")
    skills = get_skill_recommendations(task, tier)

    # Build sections
    sections = []

    sections.append(f"# {domain} Project — CLAUDE.md\n")
    sections.append("## Project Overview\n")
    sections.append("[One-line description of this project's contribution]\n")

    # Domain & conventions
    conventions = [f"- **Field**: {domain}"]
    if writing_tool:
        conventions.append(f"- **Writing format**: {writing_tool}")
    if ref_manager:
        conventions.append(f"- **Citation manager**: {ref_manager}")
    if langs:
        conventions.append(f"- **Languages**: {langs}")
    sections.append("## Domain & Conventions\n")
    sections.append("\n".join(conventions) + "\n")

    # Build commands
    build_cmds = []
    if writing_tool and any(
        t in writing_tool.lower() for t in ("latex", "overleaf", "tex")
    ):
        build_cmds.append("### Paper\n```bash\nlatexmk -pdf main.tex\n```\n")
    if langs:
        lang_lower = langs.lower()
        if "python" in lang_lower:
            build_cmds.append(
                "### Code\n```bash\npytest --tb=short -q\nruff check .\n```\n"
            )
        elif "r" in lang_lower.split(",")[0].strip().split()[0]:
            build_cmds.append("### Code\n```bash\nRscript run_analysis.R\n```\n")
        elif "julia" in lang_lower:
            build_cmds.append("### Code\n```bash\njulia --project=. main.jl\n```\n")
    if build_cmds:
        sections.append("## Build Commands\n")
        sections.extend(build_cmds)

    # Git safety net (Tier 0-1)
    if tier <= 1 or not uses_git:
        sections.append("## Git Safety Net\n")
        sections.append(dedent("""\
            Before running any AI agent on your project, take a snapshot:

            ```bash
            git add -A && git commit -m "Snapshot before agent session"
            ```

            After a session, review what changed: `git diff HEAD`
            Undo everything if needed: `git restore .`
            """))

    # Verification requirements (tier-appropriate)
    sections.append("## Verification Requirements\n")
    if tier <= 1:
        sections.append(dedent("""\
            - Check AI-generated citations against Google Scholar before including them
            - Read AI-drafted text critically — treat it as a first draft from a hasty coauthor
            """))
    elif tier == 2:
        sections.append(dedent("""\
            - Run `/paper-references` on bibliography before submission
            - Use `/paper-verify-experiments` to check claims against code
            - Cross-reference AI-generated literature claims with actual papers
            """))
    else:
        sections.append(dedent("""\
            - All citations verified via `bibtexupdater` before merge
            - Experiment-paper sync via `/experiment-tracker`
            - Code-paper consistency checked in CI
            """))

    # Skill recommendations
    sections.append("## Recommended Skills\n")
    skill_rows = [
        f"| `{name}` | {desc} |" for name, desc in skills
    ]
    sections.append("| Skill | What it does |\n|-------|-------------|")
    sections.append("\n".join(skill_rows) + "\n")

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Project detection (--detect mode)
# ---------------------------------------------------------------------------


def detect_project(project_dir: str = ".") -> dict:
    """Auto-detect project characteristics from file structure."""
    p = Path(project_dir)
    answers = {}

    # Detect domain from CLAUDE.md
    claude_md = p / "CLAUDE.md"
    if claude_md.exists():
        content = claude_md.read_text(errors="ignore")
        if "ml" in content.lower() or "machine learning" in content.lower():
            answers["domain"] = "Machine Learning"
        elif "neuro" in content.lower():
            answers["domain"] = "Neuroscience"

    # Detect programming languages
    langs = []
    if list(p.rglob("*.py"))[:1]:
        langs.append("Python")
    if list(p.rglob("*.R"))[:1] or list(p.rglob("*.Rmd"))[:1]:
        langs.append("R")
    if list(p.rglob("*.jl"))[:1]:
        langs.append("Julia")
    if langs:
        answers["languages"] = ", ".join(langs)

    # Detect writing tool
    if list(p.rglob("*.tex"))[:1]:
        answers["writing_tool"] = "LaTeX"
    elif list(p.rglob("*.docx"))[:1]:
        answers["writing_tool"] = "Word"
    elif list(p.rglob("*.md"))[:1]:
        answers["writing_tool"] = "Markdown"

    # Detect reference manager
    if list(p.rglob("*.bib"))[:1]:
        answers["ref_manager"] = "BibTeX"

    # Detect git
    answers["git"] = "y" if (p / ".git").exists() else "n"

    # Infer CLI comfort and AI usage from what's present
    if (p / ".git").exists() and langs:
        answers["cli"] = "c"
        answers["ai"] = "b"  # conservative default
    elif langs:
        answers["cli"] = "b"
        answers["ai"] = "b"

    # Default task
    if list(p.rglob("*.tex"))[:1]:
        answers["task"] = "d"  # writing
    elif langs:
        answers["task"] = "c"  # code

    return answers


# ---------------------------------------------------------------------------
# Interactive interview
# ---------------------------------------------------------------------------


def ask_question(key: str, q: dict) -> str:
    """Ask a single question and return the answer."""
    print(f"\n{q['prompt']}")

    if q.get("free_text"):
        hint = q.get("hint", "")
        if hint:
            print(f"  ({hint})")
        if q.get("optional"):
            print("  [press Enter to skip]")
        answer = input("> ").strip()
        return answer

    # Multiple choice
    for letter, text in q["options"].items():
        print(f"  ({letter}) {text}")
    if q.get("optional"):
        print("  [press Enter to skip]")

    while True:
        answer = input("> ").strip().lower()
        if not answer and q.get("optional"):
            return ""
        if answer in q["options"]:
            return answer
        print(f"  Please enter one of: {', '.join(q['options'].keys())}")


def run_interview() -> dict:
    """Run the full interactive interview."""
    print("=" * 60)
    print("  Welcome to the Research Agora")
    print("  Let's get you set up.")
    print("=" * 60)

    answers = {}
    # Core questions (always ask)
    for key in ["cli", "ai", "domain", "task"]:
        answers[key] = ask_question(key, QUESTIONS[key])

    # Follow-up questions (conditional)
    cli_level = LEVEL_MAP.get(answers.get("cli", "a"), 0)

    if cli_level >= 1:
        answers["languages"] = ask_question("languages", QUESTIONS["languages"])

    answers["writing_tool"] = ask_question("writing_tool", QUESTIONS["writing_tool"])
    answers["ref_manager"] = ask_question("ref_manager", QUESTIONS["ref_manager"])

    if cli_level >= 1:
        answers["git"] = ask_question("git", QUESTIONS["git"])

    return answers


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

TIER_NAMES = {
    0: "Browser-Only User",
    1: "CLI-Ready, AI-Curious",
    2: "Regular User — Systematic Workflows",
    3: "Power User — Ready to Scale",
}


def print_results(answers: dict, tier: int, output_json: bool = False) -> None:
    """Print the onboarding results."""
    task = answers.get("task", "d")
    skills = get_skill_recommendations(task, tier)
    claude_md = generate_claude_md(answers, tier)
    five_min = FIVE_MINUTE_WINS.get(tier, FIVE_MINUTE_WINS[1])

    if output_json:
        result = {
            "tier": tier,
            "tier_name": TIER_NAMES[tier],
            "answers": answers,
            "skills": [{"name": n, "description": d} for n, d in skills],
            "claude_md": claude_md,
            "five_minute_win": five_min,
        }
        print(json.dumps(result, indent=2))
        return

    print("\n" + "=" * 60)
    print(f"  Your profile: {TIER_NAMES[tier]}")
    print("=" * 60)

    print("\n--- Your personalized CLAUDE.md ---\n")
    print("Save this to your project root:\n")
    print(claude_md)

    print("\n--- Your 5-minute win ---\n")
    print(five_min)

    print("\n--- Recommended skills ---\n")
    for name, desc in skills:
        print(f"  {name:30s} {desc}")

    print("\n--- What's next ---\n")
    if tier == 0:
        print("  1. Try the structured prompts above")
        print("  2. Install Claude Code when ready: https://docs.anthropic.com/en/docs/claude-code")
        print("  3. Set up git as a safety net")
        print("  4. Run /onboard again once you have Claude Code")
    elif tier == 1:
        print("  1. Save your CLAUDE.md to your project root")
        print("  2. Set up git if you haven't already")
        print("  3. Try 2-3 skills this week")
        print("  4. Explore verification workflows when comfortable")
    elif tier == 2:
        print("  1. Save your CLAUDE.md and commit it")
        print("  2. Integrate verification into pre-submission checklist")
        print("  3. Explore MCP tools: Zotero, arXiv, GitHub")
        print("  4. Customize CLAUDE.md as you learn what works")
    else:
        print("  1. Audit your workflows — which ones are skill-shaped?")
        print("  2. Package one workflow as a skill and submit a PR")
        print("  3. Explore research-agents: 22 specialized agents")
        print("  4. Use CLAUDE.md to encode lab standards across projects")

    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Research Agora onboarding — generate a personalized setup"
    )
    parser.add_argument(
        "--detect",
        action="store_true",
        help="Auto-detect project characteristics instead of interviewing",
    )
    parser.add_argument(
        "--tier",
        type=int,
        choices=[0, 1, 2, 3],
        help="Skip interview and use this tier directly",
    )
    parser.add_argument(
        "--domain",
        type=str,
        help="Research domain (used with --tier)",
    )
    parser.add_argument(
        "--task",
        type=str,
        choices=["a", "b", "c", "d", "e", "f"],
        help="Primary task (used with --tier)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output structured JSON instead of formatted text",
    )
    parser.add_argument(
        "--dir",
        type=str,
        default=".",
        help="Project directory to analyze (default: current)",
    )
    args = parser.parse_args()

    if args.detect:
        answers = detect_project(args.dir)
        if not answers.get("domain"):
            answers["domain"] = args.domain or "Research"
        if not answers.get("task"):
            answers["task"] = args.task or "d"
        tier = classify_tier(answers)
    elif args.tier is not None:
        answers = {
            "cli": ["a", "b", "c", "d"][min(args.tier, 3)],
            "ai": ["a", "b", "c", "d"][min(args.tier, 3)],
            "domain": args.domain or "Research",
            "task": args.task or "d",
            "languages": "Python" if args.tier >= 1 else "",
            "writing_tool": "LaTeX" if args.tier >= 1 else "",
            "git": "y" if args.tier >= 1 else "n",
        }
        tier = args.tier
    else:
        answers = run_interview()
        tier = classify_tier(answers)

    print_results(answers, tier, output_json=args.json)


if __name__ == "__main__":
    main()
