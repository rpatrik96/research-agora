"""Report generation for synthetic user tests.

Produces two output formats:
- JSON: per-scenario structured data (action log, scores, issues)
- Markdown: cross-scenario summary table with critical issues and recommendations
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from synthetic.claude_client import PageEvaluation

REPORTS_DIR = Path(__file__).parent / "reports"


def save_scenario_report(
    scenario_name: str,
    persona_name: str,
    action_history: list[dict],
    pages_visited: list[str],
    evaluation: PageEvaluation,
    duration_seconds: float = 0.0,
) -> Path:
    """Save a JSON report for a single scenario run.

    Returns the path to the saved report file.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{scenario_name}.json"
    path = REPORTS_DIR / filename

    report = {
        "scenario": scenario_name,
        "persona": persona_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": round(duration_seconds, 1),
        "actions_taken": len(action_history),
        "pages_visited": pages_visited,
        "evaluation": asdict(evaluation),
        "action_log": action_history,
    }

    path.write_text(json.dumps(report, indent=2))
    return path


def generate_summary_report(report_paths: list[Path]) -> Path:
    """Generate a Markdown summary from multiple scenario JSON reports.

    Returns the path to the summary file.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    summary_path = REPORTS_DIR / f"{timestamp}_summary.md"

    reports = []
    for rp in report_paths:
        if rp.exists():
            reports.append(json.loads(rp.read_text()))

    if not reports:
        summary_path.write_text("# Synthetic User Test Report\n\nNo reports found.\n")
        return summary_path

    lines = [
        f"# Synthetic User Test Report — {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "",
        "## Summary",
        "",
        "| Scenario | Persona | Findability | Clarity | Actions | Issues | Duration |",
        "|----------|---------|-------------|---------|---------|--------|----------|",
    ]

    all_issues = []
    all_suggestions = []

    for r in reports:
        ev = r.get("evaluation", {})
        issues = ev.get("issues", [])
        all_issues.extend(issues)
        all_suggestions.extend(ev.get("suggestions", []))

        lines.append(
            f"| {r['scenario']} | {r['persona']} | "
            f"{ev.get('findability_score', '?')}/5 | "
            f"{ev.get('clarity_score', '?')}/5 | "
            f"{r['actions_taken']} | "
            f"{len(issues)} | "
            f"{r['duration_seconds']}s |"
        )

    # Critical issues section
    critical = [i for i in all_issues if i.get("severity") == "critical"]
    major = [i for i in all_issues if i.get("severity") == "major"]
    minor = [i for i in all_issues if i.get("severity") == "minor"]

    if critical or major:
        lines.extend(["", "## Critical and Major Issues", ""])
        for i, issue in enumerate(critical + major, 1):
            lines.append(
                f"{i}. **[{issue['severity'].upper()}] [{issue['page']}]** "
                f"{issue['description']}"
            )
            lines.append(f"   - Element: `{issue['element']}`")
            lines.append(f"   - Suggestion: {issue['suggestion']}")
            lines.append("")

    if minor:
        lines.extend(["## Minor Issues", ""])
        for i, issue in enumerate(minor, 1):
            lines.append(f"{i}. [{issue['page']}] {issue['description']}")

    # Deduplicated suggestions
    if all_suggestions:
        unique_suggestions = list(dict.fromkeys(all_suggestions))
        lines.extend(["", "## Recommendations", ""])
        for i, s in enumerate(unique_suggestions, 1):
            lines.append(f"{i}. {s}")

    # Goal completion summary
    lines.extend(["", "## Goal Completion", ""])
    for r in reports:
        ev = r.get("evaluation", {})
        progress = ev.get("goal_progress", {})
        if progress:
            met = sum(1 for v in progress.values() if v)
            total = len(progress)
            lines.append(f"**{r['persona']}** ({r['scenario']}): {met}/{total} criteria met")
            for criterion, achieved in progress.items():
                mark = "x" if achieved else " "
                lines.append(f"  - [{mark}] {criterion}")
            lines.append("")

    lines.append("")
    summary_path.write_text("\n".join(lines))
    return summary_path
