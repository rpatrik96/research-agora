#!/usr/bin/env python3
"""Aggregate skill-feedback reports into registry/feedback.json (RFC-0001).

Deterministic, script-first: parse -> validate -> dedup -> cap -> quarantine
-> score (Wilson 95% lower bound) -> suppress below the k-anonymity floor
-> write. Safe to re-run (idempotent).

Inputs (one of):
  --input-dir DIR    read report JSON files (*.json) from a directory
  --from-github      fetch open issues labeled 'skill-feedback' via the gh CLI

Output: --output (default registry/feedback.json), plus a human-readable
digest on stdout (used as the body of the aggregation PR).
"""

import argparse
import json
import math
import re
import statistics
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
REGISTRY_DIR = REPO_ROOT / "registry"
HUB_REPO = "rpatrik96/research-agora"
ISSUE_LABEL = "skill-feedback"

SCHEMA_VERSION = 1
MAX_REPORTS_PER_INSTALLATION = 8
MAX_SKILLS_PER_REPORT = 200
MAX_INVOCATIONS_PER_ENTRY = 100_000
MAX_INSIGHTS_PER_SKILL = 10
INSIGHT_TEXT_MAX = 500
OUTLIER_SIGMA = 3.0
# k-anonymity floor (RFC-0001 §11): a per-skill breakdown is published only at
# or above three unique installations. This is the single source of truth for
# the threshold; scripts/generate-site.py keeps its own copy as a rendering
# guard, and tests/test_feedback.py asserts the two agree.
MIN_INSTALLATIONS_PUBLISH = 3
MIN_INSTALLATIONS_CANDIDATE = 5
ESTABLISHED_WILSON = 0.7
FLAGGED_WILSON = 0.5
FLAGGED_MIN_INVOCATIONS = 10
INSIGHT_TYPES = {
    "bug",
    "improvement",
    "docs-gap",
    "missing-skill",
    "overlap",
    "deprecation-signal",
    "praise",
}
OUTCOME_KEYS = {"success", "partial", "error", "unknown"}
ERROR_CODES = {
    "INVALID_INPUT",
    "TIMEOUT",
    "SERVICE_UNAVAILABLE",
    "SCOPE_EXCEEDED",
    "CONFIDENCE_LOW",
    "PARTIAL_RESULT",
}

FENCED_JSON = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)
# Reports come from a public inbox: every identifier that can end up in
# feedback.json or the digest PR body is charset-constrained here so
# attacker-chosen strings cannot smuggle markdown/mentions/control chars.
REPORT_ID_RE = re.compile(r"^r-[A-Za-z0-9-]{1,64}$")
INSTALLATION_ID_RE = re.compile(r"^[A-Za-z0-9-]{8,64}$")
SKILL_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")


def wilson_lower_bound(successes: float, n: float, z: float = 1.96) -> float:
    """Wilson score interval lower bound for a Bernoulli proportion."""
    if n <= 0:
        return 0.0
    p = successes / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, (centre - margin) / denom)


def registry_skill_names() -> set:
    index_path = REGISTRY_DIR / "index.json"
    with open(index_path) as f:
        data = json.load(f)
    return {s["name"] for repo in data.get("repos", []) for s in repo.get("skills", [])}


def _valid_count(value, upper: int = MAX_INVOCATIONS_PER_ENTRY) -> bool:
    return (
        isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= upper
    )


def validate_report(report: dict) -> list[str]:
    """Return a list of validation errors; empty list means valid.

    Defensive by design: reports arrive from a public issue inbox, so every
    field is type- and charset-checked before it can reach feedback.json,
    the digest PR body, or any arithmetic.
    """
    errors = []
    if not isinstance(report, dict):
        return ["report is not a JSON object"]
    if report.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {report.get('schema_version')!r}")
    report_id = report.get("report_id")
    if not isinstance(report_id, str) or not REPORT_ID_RE.match(report_id):
        errors.append("missing or malformed report_id")
    reporter = report.get("reporter")
    installation = (
        reporter.get("installation_id") if isinstance(reporter, dict) else None
    )
    if not isinstance(installation, str) or not INSTALLATION_ID_RE.match(installation):
        errors.append("missing or malformed reporter.installation_id")
    created = report.get("created")
    if not isinstance(created, str) or not DATE_RE.match(created):
        errors.append("missing or malformed created date (expected YYYY-MM-DD)")
    skills = report.get("skills")
    if not isinstance(skills, list) or not skills:
        errors.append("missing or empty skills list")
        return errors
    if len(skills) > MAX_SKILLS_PER_REPORT:
        return [f"too many skill entries ({len(skills)} > {MAX_SKILLS_PER_REPORT})"]
    for entry in skills:
        if not isinstance(entry, dict):
            errors.append("skill entry is not an object")
            continue
        name = entry.get("skill")
        if not isinstance(name, str) or not SKILL_NAME_RE.match(name):
            errors.append(f"missing or malformed skill name: {name!r}")
            continue
        if not _valid_count(entry.get("invocations")):
            errors.append(f"{name}: invalid invocations")
        outcomes = entry.get("outcomes")
        if (
            not isinstance(outcomes, dict)
            or not set(outcomes) <= OUTCOME_KEYS
            or not all(_valid_count(v) for v in outcomes.values())
        ):
            errors.append(f"{name}: invalid outcomes")
        error_codes = entry.get("error_codes") or {}
        if (
            not isinstance(error_codes, dict)
            or not set(error_codes) <= ERROR_CODES
            or not all(_valid_count(v) for v in error_codes.values())
        ):
            errors.append(f"{name}: invalid error_codes")
        insights = entry.get("insights", [])
        if not isinstance(insights, list) or len(insights) > MAX_INSIGHTS_PER_SKILL:
            errors.append(
                f"{name}: insights must be a list of at most {MAX_INSIGHTS_PER_SKILL}"
            )
            continue
        for insight in insights:
            if not isinstance(insight, dict):
                errors.append(f"{name}: insight is not an object")
                continue
            if insight.get("type") not in INSIGHT_TYPES:
                errors.append(f"{name}: invalid insight type {insight.get('type')!r}")
            text = insight.get("text", "")
            if (
                not isinstance(text, str)
                or not text
                or len(text) > INSIGHT_TEXT_MAX
                or CONTROL_CHARS_RE.search(text)
            ):
                errors.append(
                    f"{name}: insight text missing, over {INSIGHT_TEXT_MAX} chars, "
                    "or contains control characters"
                )
            confidence = insight.get("confidence", 0.5)
            if (
                not isinstance(confidence, (int, float))
                or isinstance(confidence, bool)
                or not 0 <= confidence <= 1
            ):
                errors.append(f"{name}: insight confidence must be a number in [0, 1]")
    return errors


def load_reports_from_dir(input_dir: Path) -> list[dict]:
    reports = []
    for path in sorted(input_dir.glob("*.json")):
        try:
            with open(path) as f:
                reports.append(json.load(f))
        except (OSError, json.JSONDecodeError) as e:
            print(f"warning: skipping unreadable {path.name}: {e}", file=sys.stderr)
    return reports


def load_reports_from_github() -> list[dict]:
    result = subprocess.run(
        [
            "gh",
            "issue",
            "list",
            "--repo",
            HUB_REPO,
            "--label",
            ISSUE_LABEL,
            "--state",
            "open",
            "--limit",
            "500",
            "--json",
            "number,body",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        print(f"error: gh issue list failed: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    reports = []
    for issue in json.loads(result.stdout):
        match = FENCED_JSON.search(issue.get("body") or "")
        if not match:
            print(
                f"warning: issue #{issue['number']}: no fenced JSON payload",
                file=sys.stderr,
            )
            continue
        try:
            report = json.loads(match.group(1))
            report["_issue"] = issue["number"]
            reports.append(report)
        except json.JSONDecodeError:
            print(
                f"warning: issue #{issue['number']}: malformed JSON payload",
                file=sys.stderr,
            )
    return reports


def filter_reports(reports: list[dict]) -> tuple[list[dict], dict]:
    """Validate, dedup, cap per installation, quarantine volume outliers."""
    log = {"invalid": [], "duplicates": 0, "capped": 0, "quarantined": []}

    valid = []
    seen_ids = set()
    for report in reports:
        try:
            errors = validate_report(report)
        except Exception as e:  # one hostile report must never kill the run
            errors = [f"unvalidatable report structure: {type(e).__name__}"]
        if errors:
            log["invalid"].append(
                {"report_id": report.get("report_id"), "errors": errors}
            )
            continue
        if report["report_id"] in seen_ids:
            log["duplicates"] += 1
            continue
        seen_ids.add(report["report_id"])
        valid.append(report)

    by_installation: dict[str, list[dict]] = {}
    for report in valid:
        by_installation.setdefault(report["reporter"]["installation_id"], []).append(
            report
        )
    capped = []
    for installation_reports in by_installation.values():
        installation_reports.sort(
            key=lambda r: (r.get("created", ""), r["report_id"]), reverse=True
        )
        log["capped"] += max(
            0, len(installation_reports) - MAX_REPORTS_PER_INSTALLATION
        )
        capped.extend(installation_reports[:MAX_REPORTS_PER_INSTALLATION])

    volumes = {
        installation: sum(e["invocations"] for r in reps for e in r["skills"])
        for installation, reps in by_installation.items()
    }
    kept = capped
    if len(volumes) >= 4:
        values = list(volumes.values())
        median = statistics.median(values)
        stdev = statistics.pstdev(values)
        if stdev > 0:
            outliers = {
                i for i, v in volumes.items() if v > median + OUTLIER_SIGMA * stdev
            }
            if outliers:
                log["quarantined"] = sorted(outliers)
                kept = [
                    r
                    for r in capped
                    if r["reporter"]["installation_id"] not in outliers
                ]

    kept.sort(key=lambda r: r["report_id"])
    return kept, log


def status_for(wilson: float, installations: int, invocations: int) -> str:
    if installations < MIN_INSTALLATIONS_CANDIDATE:
        return "candidate"
    if wilson >= ESTABLISHED_WILSON:
        return "established"
    if wilson < FLAGGED_WILSON and invocations >= FLAGGED_MIN_INVOCATIONS:
        return "flagged"
    return "active"


def aggregate(reports: list[dict], known_skills: set) -> tuple[dict, list[str]]:
    """Roll validated reports up into the canonical aggregate.

    Skills below MIN_INSTALLATIONS_PUBLISH unique installations are counted but
    not written out (RFC-0001 §11 k-anonymity). The gate lives here, in the data
    layer, because registry/feedback.json is the canonical artifact (§4.1) and
    is committed to a public repository: a breakdown drawn from one or two
    installations is that installation's usage profile — invocation counts,
    outcome and error counters, and free-text insights — which §9.3 rules out
    publishing. Gating only the site renderer would leave the profile readable
    in the file and in git history for anyone who clones the repo.
    """
    unknown = []
    skills: dict[str, dict] = {}
    for report in reports:
        installation = report["reporter"]["installation_id"]
        for entry in report["skills"]:
            name = entry["skill"]
            if name not in known_skills:
                unknown.append(name)
                continue
            agg = skills.setdefault(
                name,
                {
                    "report_count": 0,
                    "installations": set(),
                    "invocations": 0,
                    "outcomes": {},
                    "error_codes": {},
                    "insights": [],
                },
            )
            agg["report_count"] += 1
            agg["installations"].add(installation)
            agg["invocations"] += entry["invocations"]
            for field in ("outcomes", "error_codes"):
                for key, value in (entry.get(field) or {}).items():
                    agg[field][key] = agg[field].get(key, 0) + value
            for insight in entry.get("insights", []):
                agg["insights"].append(
                    {
                        "type": insight["type"],
                        "text": insight["text"],
                        "confidence": float(insight.get("confidence", 0.5)),
                    }
                )

    out_skills = {}
    suppressed = 0
    for name in sorted(skills):
        agg = skills[name]
        if len(agg["installations"]) < MIN_INSTALLATIONS_PUBLISH:
            # Nothing about the skill is emitted below the floor: not the
            # name, not the counters, not the insights. The name alone would
            # leak which skills a lone reporter used, and the aggregate stays
            # self-consistent this way: every entry present is publishable, so
            # a consumer that forgets the threshold cannot leak.
            suppressed += 1
            continue
        outcomes = agg["outcomes"]
        n = (
            outcomes.get("success", 0)
            + outcomes.get("partial", 0)
            + outcomes.get("error", 0)
        )
        successes = outcomes.get("success", 0) + 0.5 * outcomes.get("partial", 0)
        wilson = round(wilson_lower_bound(successes, n), 4)
        installations = len(agg["installations"])
        insights = sorted(agg["insights"], key=lambda i: -i["confidence"])[
            :MAX_INSIGHTS_PER_SKILL
        ]
        out_skills[name] = {
            "report_count": agg["report_count"],
            "unique_installations": installations,
            "invocations": agg["invocations"],
            "outcomes": dict(sorted(outcomes.items())),
            "error_codes": dict(sorted(agg["error_codes"].items())),
            "wilson_lb": wilson,
            "status": status_for(wilson, installations, agg["invocations"]),
            "top_insights": insights,
        }

    all_installations = {r["reporter"]["installation_id"] for r in reports}
    dates = [r.get("created") for r in reports if r.get("created")]
    result = {
        "version": "1.0.0",
        "schema_version": SCHEMA_VERSION,
        "generated": date.today().isoformat(),
        "window": {
            "from": min(dates) if dates else None,
            "to": max(dates) if dates else None,
        },
        "stats": {
            "reports": len(reports),
            "unique_installations": len(all_installations),
            "skills_with_feedback": len(out_skills),
            "skills_suppressed": suppressed,
        },
        "skills": out_skills,
    }
    return result, sorted(set(unknown))


def print_digest(result: dict, log: dict, unknown: list[str]) -> None:
    print("## Feedback aggregation digest\n")
    stats = result["stats"]
    print(
        f"- Reports ingested: {stats['reports']} from {stats['unique_installations']} installation(s)"
    )
    print(f"- Skills with feedback: {stats['skills_with_feedback']}")
    if stats.get("skills_suppressed"):
        # Count only: the digest becomes the body of a PR on a public repo, so
        # naming the skills here would republish exactly what the k-anonymity
        # floor withholds from feedback.json (RFC-0001 §11).
        print(
            f"- Skills held below the k = {MIN_INSTALLATIONS_PUBLISH} publication "
            f"floor (names withheld, RFC-0001 §11): {stats['skills_suppressed']}"
        )
    print(
        f"- Invalid reports skipped: {len(log['invalid'])}; duplicates: {log['duplicates']}; "
        f"over-cap dropped: {log['capped']}"
    )
    if log["quarantined"]:
        print(
            f"- Quarantined installations (volume outliers, excluded pending review): "
            f"{', '.join(log['quarantined'])}"
        )
    if unknown:
        print(
            f"- Unknown skills dropped (not in registry/index.json): {', '.join(unknown)}"
        )
    lifecycle = {
        n: s["status"] for n, s in result["skills"].items() if s["status"] == "flagged"
    }
    if lifecycle:
        print("\n### Lifecycle triggers (open a lifecycle-review issue per skill)\n")
        for name in lifecycle:
            skill = result["skills"][name]
            print(
                f"- `{name}`: wilson_lb={skill['wilson_lb']} over {skill['invocations']} invocations"
            )
    if result["skills"]:
        print("\n### Per-skill summary\n")
        print("| skill | reports | installations | invocations | wilson_lb | status |")
        print("|-------|---------|---------------|-------------|-----------|--------|")
        for name, skill in result["skills"].items():
            print(
                f"| {name} | {skill['report_count']} | {skill['unique_installations']} "
                f"| {skill['invocations']} | {skill['wilson_lb']} | {skill['status']} |"
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--input-dir", type=Path)
    source.add_argument("--from-github", action="store_true")
    parser.add_argument("--output", type=Path, default=REGISTRY_DIR / "feedback.json")
    args = parser.parse_args(argv)

    if args.input_dir:
        reports = load_reports_from_dir(args.input_dir)
    elif args.from_github:
        reports = load_reports_from_github()
    else:
        reports = []

    for report in reports:
        report.pop("_issue", None)

    kept, log = filter_reports(reports)
    result, unknown = aggregate(kept, registry_skill_names())

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(result, f, indent=2, sort_keys=False)
        f.write("\n")

    print_digest(result, log, unknown)
    print(f"\nWrote {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
