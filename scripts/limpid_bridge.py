#!/usr/bin/env python3
"""Optional bridge to the limpid CLI for the editorial writing skills.

limpid (github.com/rpatrik96/limpid) is a deterministic prose-quality engine
for LaTeX and Markdown. Where it is installed, it does the mechanical half of
`writing-verify` and `writing-diagnosis` better than `writing_verify.py` can:
it scores the same dimensions against a rubric drawn from Orwell, Strunk, the
Economist, Gopen & Swan and Pinker, it returns line-anchored findings rather
than document totals, and it carries voice guards that suppress false
positives a flat counter cannot (`guard.scope-hedging-is-a-virtue`,
`guard.em-dash-and-colon-payoff`, `guard.clause-stacking-resolves`,
`guard.terms-of-art-are-not-zombies`).

**limpid is optional and always will be.** It is not on npm and ships as a
`.vsix` plus a CLI in a release bundle, so a marketplace user who ran one
install command will not have it. Every function here fails soft: no CLI, a
bad exit status, malformed JSON, or a timeout all return `available=False`
with a reason, and the caller falls back to `writing_verify.py` unchanged.

Resolution order:
  1. `$LIMPID_CLI` — a path to the CLI entry point (`.js` is run under node).
  2. `limpid` on `PATH`.

Usage:
    python3 scripts/limpid_bridge.py draft.tex --register paper
    python3 scripts/limpid_bridge.py --check          # is limpid available?
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from typing import Any, Optional

REGISTERS = ("paper", "blog", "grant", "sop")
DEFAULT_TIMEOUT = 60

# limpid rule ids -> the writing-diagnosis pattern they are evidence for.
#
# Direction of the port matters here: `writing-diagnosis.md`'s Pattern Library
# is the source, and limpid's `packages/rubric/src/patterns.ts` says so in its
# own header ("Verbatim-in-spirit from writing-diagnosis.md's Pattern
# Library"). So this maps limpid's mechanical findings back onto the patterns
# that already exist, rather than importing a second vocabulary. Only the seven
# patterns limpid marks `detectableBy: "hybrid"` can be evidenced this way; the
# five marked `"llm"` (Idea Soup, Buried Lede, Orphan Transition, Scale
# Mismatch, Jargon Cliff) still need a reader model and are left to the skill.
RULE_TO_PATTERN: dict[str, str] = {
    "strunk.expletive-openers": "Throat Clearing",
    "strunk.the-fact-that": "Throat Clearing",
    "strunk.omit-needless-words": "Throat Clearing",
    "orwell.cut-needless-words": "Throat Clearing",
    "economist.redundant-temporals": "Throat Clearing",
    "voice.hedges": "Hedge Stacking",
    "voice.hedge-phrases": "Hedge Stacking",
    "strunk.active-voice": "Zombie Sentence",
    "orwell.active-voice": "Zombie Sentence",
    "writersdiet.nominalizations": "Zombie Sentence",
    "writersdiet.be-verbs": "Abstraction Fog",
    "writersdiet.adjectives": "Abstraction Fog",
    "writersdiet.prepositions": "Abstraction Fog",
    "orwell.no-jargon": "Abstraction Fog",
    "economist.read-twice": "Cognitive Overload",
    "gopen.subject-verb-proximity": "Cognitive Overload",
    "gopen.stress-position": "Cognitive Overload",
    "voice.cliches": "Echo Chamber",
    "orwell.no-dead-metaphors": "Echo Chamber",
    "economist.so-called": "Echo Chamber",
}

# Findings limpid reports that are real but map to no named pattern. Surfaced
# separately so the skill does not silently drop them.
UNMAPPED_KEPT = ("voice.hype", "voice.boosters", "economist.acronym-penalty")


def resolve_cli() -> Optional[list[str]]:
    """Return the argv prefix that runs limpid, or None if it is not here."""
    env = os.environ.get("LIMPID_CLI", "").strip()
    if env:
        if not os.path.exists(env):
            return None
        return ["node", env] if env.endswith(".js") else [env]

    found = shutil.which("limpid")
    return [found] if found else None


def unavailable(reason: str) -> dict[str, Any]:
    return {"available": False, "reason": reason}


def run_limpid(
    path: str,
    register: str = "paper",
    timeout: int = DEFAULT_TIMEOUT,
    rules: Optional[str] = None,
) -> dict[str, Any]:
    """Score one file with limpid. Never raises; returns available=False instead."""
    if register not in REGISTERS:
        return unavailable(f"unknown register {register!r}; expected one of {REGISTERS}")
    if not os.path.exists(path):
        return unavailable(f"file not found: {path}")

    cli = resolve_cli()
    if cli is None:
        return unavailable(
            "limpid CLI not found (set $LIMPID_CLI to its cli.js, or put `limpid` on PATH)"
        )

    argv = [*cli, path, "--register", register, "--json"]
    if rules:
        argv += ["--rules", rules]

    try:
        proc = subprocess.run(
            argv, capture_output=True, text=True, timeout=timeout, check=False
        )
    except subprocess.TimeoutExpired:
        return unavailable(f"limpid timed out after {timeout}s")
    except OSError as exc:
        return unavailable(f"could not execute limpid: {exc}")

    if not proc.stdout.strip():
        err = (proc.stderr or "").strip().splitlines()
        return unavailable(f"limpid produced no output{': ' + err[-1] if err else ''}")

    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return unavailable(f"limpid output was not JSON: {exc}")

    # The CLI reports an array, one entry per file.
    if isinstance(payload, list):
        if not payload:
            return unavailable("limpid returned no results for this file")
        result = payload[0]
    else:
        result = payload

    return normalize(result)


def normalize(result: dict[str, Any]) -> dict[str, Any]:
    """Reshape a limpid result into what the editorial skills consume."""
    findings = result.get("findings") or []

    by_pattern: dict[str, list[dict[str, Any]]] = {}
    unmapped: list[dict[str, Any]] = []
    for f in findings:
        rule = f.get("ruleId", "")
        entry = {
            "ruleId": rule,
            "message": f.get("message", ""),
            "line": f.get("line"),
            "excerpt": f.get("excerpt", ""),
            "category": f.get("category", ""),
            "severity": f.get("severity", ""),
        }
        pattern = RULE_TO_PATTERN.get(rule)
        if pattern:
            by_pattern.setdefault(pattern, []).append(entry)
        elif rule.startswith("house.") or rule in UNMAPPED_KEPT:
            unmapped.append(entry)

    return {
        "available": True,
        "grade": result.get("grade"),
        "metrics": result.get("metrics", {}),
        "finding_count": result.get("findingCount", len(findings)),
        "failed": result.get("failed", False),
        "violations": result.get("violations", []),
        # Evidence for the seven mechanically-detectable patterns, keyed by the
        # pattern name writing-diagnosis already uses.
        "pattern_evidence": by_pattern,
        # Real findings with no named pattern (hype, boosters, house rules).
        "other_findings": unmapped,
        "patterns_needing_judgment": [
            "Idea Soup",
            "Buried Lede",
            "Orphan Transition",
            "Scale Mismatch",
            "Jargon Cliff",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", help="File to score (.tex or .md)")
    parser.add_argument("--register", default="paper", choices=list(REGISTERS))
    parser.add_argument("--rules", help="Path to a rules file (else limpid discovers one)")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report whether limpid is available and exit",
    )
    args = parser.parse_args()

    if args.check:
        cli = resolve_cli()
        print(json.dumps({"available": cli is not None, "cli": cli}, indent=2))
        sys.exit(0)

    if not args.path:
        parser.error("path is required unless --check is given")

    out = run_limpid(
        args.path, register=args.register, timeout=args.timeout, rules=args.rules
    )
    print(json.dumps(out, indent=2))
    # Exit 0 even when limpid is absent: the caller falls back, it is not an error.
    sys.exit(0)


if __name__ == "__main__":
    main()
