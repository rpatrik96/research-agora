#!/usr/bin/env python3
"""Research Agora feedback client (RFC-0001).

Opt-in, content-free usage capture with a mandatory review gate.
Stdlib-only; every subcommand is safe to run in a hook context.

Privacy invariants (see docs/rfcs/0001-agora-feedback-loop.md):
- Capture is OFF by default; ``enable`` is explicit.
- The spool lives in ~/.agora, outside any project root, and never
  leaves the machine.
- ``submit`` requires --confirm after the exact payload was displayed.
- AGORA_FEEDBACK=0 disables everything; the ``capture`` hook entry
  point always exits 0 so a broken pipeline never blocks a session.
"""

import argparse
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import uuid
from datetime import date, datetime
from pathlib import Path

SCHEMA_VERSION = 1
POLICY_VERSION = 1
HUB_REPO = "rpatrik96/research-agora"
ISSUE_LABEL = "skill-feedback"
SPOOL_RETENTION_DAYS = 90
INSIGHT_TYPES = (
    "bug",
    "improvement",
    "docs-gap",
    "missing-skill",
    "overlap",
    "deprecation-signal",
    "praise",
)
ERROR_CODES = (
    "INVALID_INPUT",
    "TIMEOUT",
    "SERVICE_UNAVAILABLE",
    "SCOPE_EXCEEDED",
    "CONFIDENCE_LOW",
    "PARTIAL_RESULT",
)
INSIGHT_TEXT_MAX = 500

# PII lint: block emails, home paths, and URLs carrying credential-shaped
# query parameters from ever entering a report.
PII_PATTERNS = (
    ("email address", re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")),
    ("home directory path", re.compile(r"(?:/home/|/Users/|C:\\Users\\)\S+")),
    (
        "URL with token-like query",
        re.compile(r"https?://\S*[?&](?:token|key|secret|password|auth)=", re.I),
    ),
)


def agora_home() -> Path:
    return Path(os.environ.get("AGORA_HOME", str(Path.home() / ".agora")))


def config_path() -> Path:
    return agora_home() / "config.json"


def spool_path() -> Path:
    return agora_home() / "spool" / "events.jsonl"


def archive_dir() -> Path:
    return agora_home() / "spool" / "archive"


def reports_dir() -> Path:
    return agora_home() / "reports"


def pending_report_path() -> Path:
    return reports_dir() / "pending-report.json"


def load_config() -> dict:
    try:
        with open(config_path()) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def save_config(config: dict) -> None:
    config_path().parent.mkdir(parents=True, exist_ok=True)
    with open(config_path(), "w") as f:
        json.dump(config, f, indent=2)


def kill_switch_active() -> bool:
    return os.environ.get("AGORA_FEEDBACK", "") == "0"


def submissions_disabled() -> bool:
    return os.environ.get("CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC", "") == "1"


def capture_enabled() -> bool:
    return not kill_switch_active() and load_config().get("enabled", False) is True


def known_skill_names() -> set[str] | None:
    """Skill names from the marketplace registry, best-effort.

    The script ships at plugins/development/scripts/ inside the marketplace
    checkout, so the registry sits three levels up. Returns None when the
    registry is unavailable (capture then records any Skill invocation).
    """
    index = Path(__file__).resolve().parents[3] / "registry" / "index.json"
    try:
        with open(index) as f:
            data = json.load(f)
        return {
            s["name"] for repo in data.get("repos", []) for s in repo.get("skills", [])
        }
    except (OSError, json.JSONDecodeError, KeyError):
        return None


def detect_error_code(text: str) -> str | None:
    for code in ERROR_CODES:
        if code in text:
            return code
    return None


def event_from_hook_payload(payload: dict) -> dict | None:
    """Translate a Claude Code hook payload into a spool event, or None."""
    hook_event = payload.get("hook_event_name", "")
    session = str(payload.get("session_id", ""))[:8] or "unknown"

    if hook_event == "SessionEnd":
        return {"event": "session_end", "session": session}

    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    if tool == "Skill":
        skill = tool_input.get("skill") or tool_input.get("name")
        event_type = "invocation"
    elif tool == "Task":
        skill = tool_input.get("subagent_type")
        event_type = "subagent"
    else:
        return None
    if not skill:
        return None

    skill = str(skill).split(":")[
        -1
    ]  # strip plugin prefixes like "academic:paper-review"
    known = known_skill_names()
    if known is not None and skill not in known:
        return None  # not an Agora skill; record nothing

    response = payload.get("tool_response")
    response_text = (
        json.dumps(response)
        if isinstance(response, (dict, list))
        else str(response or "")
    )
    error_code = detect_error_code(response_text)
    if isinstance(response, dict) and ("error" in response or response.get("is_error")):
        outcome = "error"
    elif error_code == "PARTIAL_RESULT":
        outcome = "partial"
    elif error_code:
        outcome = "error"
    else:
        outcome = "success"

    return {
        "event": event_type,
        "session": session,
        "skill": skill,
        "outcome": outcome,
        "error_code": error_code,
        "duration_bucket": None,
        "model": None,
    }


def cmd_capture() -> int:
    """Hook entry point. Must never fail and never block."""
    try:
        if not capture_enabled():
            return 0
        payload = json.load(sys.stdin)
        event = event_from_hook_payload(payload)
        if event is None:
            return 0
        event["ts"] = datetime.now().isoformat(timespec="seconds")
        spool_path().parent.mkdir(parents=True, exist_ok=True)
        with open(spool_path(), "a") as f:
            f.write(json.dumps(event) + "\n")
    except Exception:
        pass
    return 0


def read_spool() -> list[dict]:
    events = []
    try:
        with open(spool_path()) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except OSError:
        return []
    cutoff = datetime.now().timestamp() - SPOOL_RETENTION_DAYS * 86400
    kept = []
    for e in events:
        try:
            if datetime.fromisoformat(e["ts"]).timestamp() >= cutoff:
                kept.append(e)
        except (KeyError, ValueError):
            continue
    return kept


def aggregate_spool(events: list[dict]) -> dict:
    """Per-skill counters from spool events (day precision, content-free)."""
    skills: dict[str, dict] = {}
    sessions = set()
    days = []
    for e in events:
        sessions.add(e.get("session"))
        days.append(e["ts"][:10])
        if e.get("event") == "session_end":
            continue
        s = skills.setdefault(
            e["skill"],
            {
                "invocations": 0,
                "outcomes": {"success": 0, "partial": 0, "error": 0, "unknown": 0},
                "error_codes": {},
                "duration_buckets": {},
                "models": {},
            },
        )
        s["invocations"] += 1
        s["outcomes"][e.get("outcome", "unknown")] = (
            s["outcomes"].get(e.get("outcome", "unknown"), 0) + 1
        )
        for key, field in (
            ("error_code", "error_codes"),
            ("duration_bucket", "duration_buckets"),
            ("model", "models"),
        ):
            value = e.get(key)
            if value:
                s[field][value] = s[field].get(value, 0) + 1
    return {
        "skills": skills,
        "sessions": len(sessions),
        "from": min(days) if days else None,
        "to": max(days) if days else None,
    }


def git_short_sha(repo: Path, path: str | None = None) -> str | None:
    cmd = ["git", "-C", str(repo), "log", "-1", "--format=%h"]
    if path:
        cmd += ["--", path]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        sha = out.stdout.strip()
        return sha or None
    except (OSError, subprocess.SubprocessError):
        return None


def build_report() -> dict:
    config = load_config()
    events = read_spool()
    agg = aggregate_spool(events)
    marketplace_root = Path(__file__).resolve().parents[3]

    skill_entries = []
    for name in sorted(agg["skills"]):
        counters = agg["skills"][name]
        entry = {"skill": name, "skill_sha": None, **counters, "insights": []}
        skill_entries.append(entry)

    marketplace_sha = git_short_sha(marketplace_root)
    if marketplace_sha:
        index_path = marketplace_root / "registry" / "index.json"
        paths = {}
        try:
            with open(index_path) as f:
                for repo in json.load(f).get("repos", []):
                    for s in repo.get("skills", []):
                        paths[s["name"]] = s.get("path")
        except (OSError, json.JSONDecodeError):
            pass
        for entry in skill_entries:
            skill_file = paths.get(entry["skill"])
            if skill_file:
                entry["skill_sha"] = git_short_sha(marketplace_root, skill_file)

    return {
        "schema_version": SCHEMA_VERSION,
        "report_id": f"r-{uuid.uuid4()}",
        "created": date.today().isoformat(),
        "reporter": {
            "installation_id": config.get("installation_id"),
            "client": "claude-code",
            "marketplace_sha": marketplace_sha,
        },
        "period": {"from": agg["from"], "to": agg["to"], "sessions": agg["sessions"]},
        "consent": {
            "reviewed": False,
            "channel": config.get("sink", "github-issue"),
            "policy_version": POLICY_VERSION,
        },
        "skills": skill_entries,
        "environment": {"os": sys.platform},
    }


def pii_findings(report: dict) -> list[str]:
    findings = []
    for entry in report.get("skills", []):
        for insight in entry.get("insights", []):
            for label, pattern in PII_PATTERNS:
                if pattern.search(insight.get("text", "")):
                    findings.append(
                        f"{entry['skill']}: insight contains {label}: {insight['text'][:80]!r}"
                    )
    return findings


def load_pending() -> dict | None:
    try:
        with open(pending_report_path()) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def save_pending(report: dict) -> None:
    reports_dir().mkdir(parents=True, exist_ok=True)
    with open(pending_report_path(), "w") as f:
        json.dump(report, f, indent=2)


def cmd_enable() -> int:
    config = load_config()
    if not config.get("installation_id"):
        config["installation_id"] = secrets.token_hex(16)
    config.update(
        {
            "enabled": True,
            "sink": config.get("sink", "github-issue"),
            "created": config.get("created", date.today().isoformat()),
        }
    )
    save_config(config)
    print(
        "Agora feedback capture ENABLED (local only — nothing is ever sent automatically)."
    )
    print(f"  config: {config_path()}")
    print(f"  spool:  {spool_path()}")
    print(
        f"  installation_id: {config['installation_id']} (random; reset by deleting the config)"
    )
    return 0


def cmd_disable() -> int:
    config = load_config()
    config["enabled"] = False
    save_config(config)
    print(
        "Agora feedback capture disabled. Existing spool kept; run 'purge' to delete it."
    )
    return 0


def cmd_status() -> int:
    config = load_config()
    events = read_spool()
    print(f"enabled:            {config.get('enabled', False)}")
    print(
        f"kill switch:        {'AGORA_FEEDBACK=0 (capture disabled)' if kill_switch_active() else 'not set'}"
    )
    print(
        f"submissions:        {'disabled (CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1)' if submissions_disabled() else 'allowed after review'}"
    )
    print(f"sink:               {config.get('sink', 'github-issue')}")
    print(f"spool events:       {len(events)} ({spool_path()})")
    print(f"pending report:     {'yes' if load_pending() else 'no'}")
    return 0


def cmd_stats() -> int:
    agg = aggregate_spool(read_spool())
    if not agg["skills"]:
        print("Spool is empty — no Agora skill usage captured yet.")
        return 0
    print(
        f"Local usage {agg['from']} → {agg['to']} ({agg['sessions']} sessions). Nothing here has been sent anywhere.\n"
    )
    print(f"{'skill':<32} {'calls':>5} {'ok':>4} {'part':>4} {'err':>4}")
    for name in sorted(agg["skills"], key=lambda n: -agg["skills"][n]["invocations"]):
        o = agg["skills"][name]["outcomes"]
        print(
            f"{name:<32} {agg['skills'][name]['invocations']:>5} "
            f"{o.get('success', 0):>4} {o.get('partial', 0):>4} {o.get('error', 0):>4}"
        )
    return 0


def cmd_report() -> int:
    report = build_report()
    if not report["skills"]:
        print("Spool is empty — nothing to report.")
        return 1
    existing = load_pending()
    if existing:  # keep user-curated insights across rebuilds
        insights = {
            e["skill"]: e.get("insights", []) for e in existing.get("skills", [])
        }
        for entry in report["skills"]:
            entry["insights"] = insights.get(entry["skill"], [])
    save_pending(report)
    print(json.dumps(report, indent=2))
    print(f"\nPending report written to {pending_report_path()}", file=sys.stderr)
    print(
        "Add insights with: insight add <skill> <type> <text> [--confidence X]",
        file=sys.stderr,
    )
    return 0


def cmd_insight(args: argparse.Namespace) -> int:
    report = load_pending()
    if report is None:
        print("No pending report. Run 'report' first.")
        return 1
    if args.insight_action == "list":
        for entry in report["skills"]:
            for i, insight in enumerate(entry.get("insights", [])):
                print(f"{entry['skill']}[{i}] ({insight['type']}): {insight['text']}")
        return 0
    entries = {e["skill"]: e for e in report["skills"]}
    if args.skill not in entries:
        print(
            f"Skill '{args.skill}' is not in the pending report ({', '.join(sorted(entries))})."
        )
        return 1
    if args.insight_action == "add":
        if args.type not in INSIGHT_TYPES:
            print(f"Invalid type '{args.type}'. Valid: {', '.join(INSIGHT_TYPES)}")
            return 1
        text = args.text.strip()[:INSIGHT_TEXT_MAX]
        insight = {"type": args.type, "text": text, "confidence": args.confidence}
        entries[args.skill].setdefault("insights", []).append(insight)
        for label, pattern in PII_PATTERNS:
            if pattern.search(text):
                print(
                    f"WARNING: insight text contains a possible {label} — submit will block on it."
                )
    elif args.insight_action == "remove":
        insights = entries[args.skill].get("insights", [])
        if not 0 <= args.index < len(insights):
            print(f"No insight at index {args.index} for '{args.skill}'.")
            return 1
        insights.pop(args.index)
    save_pending(report)
    print("Pending report updated.")
    return 0


def archive_spool() -> None:
    if spool_path().exists():
        archive_dir().mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        shutil.move(str(spool_path()), str(archive_dir() / f"events-{stamp}.jsonl"))


def issue_body(report: dict) -> str:
    return (
        "Automated skill-feedback report (RFC-0001). Reviewed and submitted by the reporter.\n\n"
        "```json\n" + json.dumps(report, indent=2) + "\n```\n"
    )


def cmd_submit(confirm: bool, allow_pii: bool) -> int:
    report = load_pending()
    if report is None:
        print("No pending report. Run 'report' first, review it, then submit.")
        return 1

    findings = pii_findings(report)
    if findings and not allow_pii:
        print("Submission BLOCKED — possible personal data in insights:")
        for finding in findings:
            print(f"  - {finding}")
        print(
            "Edit the insights (insight remove/add) or re-run with --allow-pii to override."
        )
        return 1

    report["consent"]["reviewed"] = True
    print("=== EXACT PAYLOAD TO BE SUBMITTED ===")
    print(json.dumps(report, indent=2))
    print("=====================================")

    if not confirm:
        print(
            "\nNothing was sent. Review the payload above; to send it, re-run: submit --confirm"
        )
        return 0
    if submissions_disabled():
        print("Submission refused: CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 is set.")
        return 1
    if kill_switch_active():
        print("Submission refused: AGORA_FEEDBACK=0 is set.")
        return 1

    save_pending(report)
    body = issue_body(report)
    title = f"[Feedback] {report['report_id']} ({report['period']['from']} → {report['period']['to']})"
    try:
        result = subprocess.run(
            [
                "gh",
                "issue",
                "create",
                "--repo",
                HUB_REPO,
                "--title",
                title,
                "--label",
                ISSUE_LABEL,
                "--body",
                body,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        result = None

    if result is not None and result.returncode == 0:
        receipt = result.stdout.strip()
        print(f"Submitted: {receipt}")
    else:
        manual = reports_dir() / f"submit-{report['report_id']}.md"
        manual.write_text(body)
        print("Could not submit via the GitHub CLI (gh). Manual fallback:")
        print(
            f"  1. Open https://github.com/{HUB_REPO}/issues/new?template=skill-feedback.yml"
        )
        print(f"  2. Paste the contents of {manual}")
        print(
            "The spool was NOT archived; re-run submit --confirm after posting, or archive manually."
        )
        return 1

    archive_spool()
    submitted = reports_dir() / f"submitted-{report['report_id']}.json"
    shutil.move(str(pending_report_path()), str(submitted))
    print(f"Spool archived; report stored at {submitted}")
    return 0


def cmd_purge() -> int:
    removed = []
    for path in (spool_path().parent, reports_dir()):
        if path.exists():
            shutil.rmtree(path)
            removed.append(str(path))
    print("Purged: " + (", ".join(removed) if removed else "nothing to remove"))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("capture", "enable", "disable", "status", "stats", "report", "purge"):
        sub.add_parser(name)
    submit = sub.add_parser("submit")
    submit.add_argument("--confirm", action="store_true")
    submit.add_argument("--allow-pii", action="store_true")
    insight = sub.add_parser("insight")
    insight_sub = insight.add_subparsers(dest="insight_action", required=True)
    insight_sub.add_parser("list")
    add = insight_sub.add_parser("add")
    add.add_argument("skill")
    add.add_argument("type")
    add.add_argument("text")
    add.add_argument("--confidence", type=float, default=0.5)
    remove = insight_sub.add_parser("remove")
    remove.add_argument("skill")
    remove.add_argument("index", type=int)

    args = parser.parse_args(argv)
    if args.command == "capture":
        return cmd_capture()
    if args.command == "enable":
        return cmd_enable()
    if args.command == "disable":
        return cmd_disable()
    if args.command == "status":
        return cmd_status()
    if args.command == "stats":
        return cmd_stats()
    if args.command == "report":
        return cmd_report()
    if args.command == "insight":
        return cmd_insight(args)
    if args.command == "submit":
        return cmd_submit(confirm=args.confirm, allow_pii=args.allow_pii)
    if args.command == "purge":
        return cmd_purge()
    return 2


if __name__ == "__main__":
    sys.exit(main())
