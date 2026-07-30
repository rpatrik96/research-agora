"""
Tests for the RFC-0001 feedback pipeline: registry/feedback.json structure,
Wilson scoring, report validation, aggregation end-to-end, and the client
capture script's privacy invariants (off by default, kill switch, PII lint).
"""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
REGISTRY_DIR = REPO_ROOT / "registry"
AGGREGATE_SCRIPT = REPO_ROOT / "scripts" / "aggregate-feedback.py"
CLIENT_SCRIPT = REPO_ROOT / "plugins" / "development" / "scripts" / "agora_feedback.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


aggregate_mod = _load_module("aggregate_feedback", AGGREGATE_SCRIPT)
client_mod = _load_module("agora_feedback_client", CLIENT_SCRIPT)


@pytest.fixture(scope="session")
def feedback_data():
    path = REGISTRY_DIR / "feedback.json"
    if not path.exists():
        pytest.skip("registry/feedback.json not found")
    with open(path) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def registry_skill_names():
    path = REGISTRY_DIR / "index.json"
    if not path.exists():
        pytest.skip("registry/index.json not found")
    with open(path) as f:
        data = json.load(f)
    names = set()
    for repo in data.get("repos", []):
        for skill in repo.get("skills", []):
            names.add(skill["name"])
    return names


def make_report(
    skill: str,
    report_id="r-test-0001",
    installation="inst-a" * 8,
    success=9,
    partial=0,
    error=1,
    insights=None,
):
    return {
        "schema_version": 1,
        "report_id": report_id,
        "created": "2026-07-30",
        "reporter": {
            "installation_id": installation,
            "client": "claude-code",
            "marketplace_sha": None,
        },
        "period": {"from": "2026-07-01", "to": "2026-07-30", "sessions": 5},
        "consent": {"reviewed": True, "channel": "github-issue", "policy_version": 1},
        "skills": [
            {
                "skill": skill,
                "skill_sha": None,
                "invocations": success + partial + error,
                "outcomes": {"success": success, "partial": partial, "error": error},
                "error_codes": {},
                "insights": insights or [],
            }
        ],
        "environment": {"os": "linux"},
    }


class TestFeedbackJson:
    """Structure of the canonical aggregate, mirroring test_benchmarks.py."""

    def test_has_version_and_schema(self, feedback_data):
        assert "version" in feedback_data
        assert feedback_data["schema_version"] == 1

    def test_has_stats_and_skills(self, feedback_data):
        assert "stats" in feedback_data
        assert isinstance(feedback_data["skills"], dict)

    def test_skills_exist_in_registry(self, feedback_data, registry_skill_names):
        for name in feedback_data["skills"]:
            assert name in registry_skill_names, (
                f"feedback.json references unknown skill: {name}"
            )

    def test_scores_and_status_valid(self, feedback_data):
        valid_status = {"candidate", "active", "established", "flagged"}
        for name, skill in feedback_data["skills"].items():
            assert 0.0 <= skill["wilson_lb"] <= 1.0, f"{name}: wilson_lb out of bounds"
            assert skill["status"] in valid_status, f"{name}: invalid status"


class TestWilsonScore:
    def test_zero_observations(self):
        assert aggregate_mod.wilson_lower_bound(0, 0) == 0.0

    def test_perfect_small_n_is_conservative(self):
        lb = aggregate_mod.wilson_lower_bound(10, 10)
        assert 0.72 < lb < 0.73  # 10/10 successes only earns ~0.72

    def test_more_evidence_raises_bound(self):
        assert aggregate_mod.wilson_lower_bound(
            90, 100
        ) > aggregate_mod.wilson_lower_bound(9, 10)

    def test_bounds(self):
        for s, n in [(0, 10), (5, 10), (10, 10), (1, 2)]:
            assert 0.0 <= aggregate_mod.wilson_lower_bound(s, n) <= 1.0


class TestReportValidation:
    def test_valid_report_passes(self, registry_skill_names):
        skill = sorted(registry_skill_names)[0]
        assert aggregate_mod.validate_report(make_report(skill)) == []

    def test_missing_installation_id_fails(self, registry_skill_names):
        report = make_report(sorted(registry_skill_names)[0])
        del report["reporter"]["installation_id"]
        assert aggregate_mod.validate_report(report)

    def test_wrong_schema_version_fails(self, registry_skill_names):
        report = make_report(sorted(registry_skill_names)[0])
        report["schema_version"] = 99
        assert aggregate_mod.validate_report(report)

    def test_invalid_insight_type_fails(self, registry_skill_names):
        report = make_report(
            sorted(registry_skill_names)[0],
            insights=[{"type": "rant", "text": "not a valid type", "confidence": 0.5}],
        )
        assert aggregate_mod.validate_report(report)

    def test_oversized_insight_text_fails(self, registry_skill_names):
        report = make_report(
            sorted(registry_skill_names)[0],
            insights=[{"type": "bug", "text": "x" * 501, "confidence": 0.5}],
        )
        assert aggregate_mod.validate_report(report)


class TestAggregationEndToEnd:
    def test_aggregate_dedup_and_referential_integrity(
        self, tmp_path, registry_skill_names
    ):
        known = sorted(registry_skill_names)[:2]
        reports = [
            make_report(known[0], report_id="r-a", installation="i" * 32),
            make_report(
                known[0], report_id="r-a", installation="i" * 32
            ),  # duplicate id
            make_report(
                known[1], report_id="r-b", installation="j" * 32, success=2, error=8
            ),
            make_report("no-such-skill-xyz", report_id="r-c", installation="k" * 32),
        ]
        input_dir = tmp_path / "reports"
        input_dir.mkdir()
        for i, report in enumerate(reports):
            (input_dir / f"{i}.json").write_text(json.dumps(report))
        output = tmp_path / "feedback.json"

        rc = aggregate_mod.main(
            ["--input-dir", str(input_dir), "--output", str(output)]
        )
        assert rc == 0

        result = json.loads(output.read_text())
        assert result["stats"]["reports"] == 3  # duplicate dropped
        assert known[0] in result["skills"]
        assert known[1] in result["skills"]
        assert "no-such-skill-xyz" not in result["skills"]  # unknown skill dropped
        assert result["skills"][known[0]]["report_count"] == 1
        assert result["skills"][known[0]]["unique_installations"] == 1
        # 9 success / 1 error scores well above 2 success / 8 error
        assert (
            result["skills"][known[0]]["wilson_lb"]
            > result["skills"][known[1]]["wilson_lb"]
        )

    def test_empty_input_produces_valid_aggregate(self, tmp_path):
        input_dir = tmp_path / "empty"
        input_dir.mkdir()
        output = tmp_path / "feedback.json"
        assert (
            aggregate_mod.main(["--input-dir", str(input_dir), "--output", str(output)])
            == 0
        )
        result = json.loads(output.read_text())
        assert result["stats"]["reports"] == 0
        assert result["skills"] == {}


def run_client(args, tmp_home, stdin_data=None, extra_env=None):
    env = {**os.environ, "AGORA_HOME": str(tmp_home)}
    env.pop("AGORA_FEEDBACK", None)
    env.update(extra_env or {})
    return subprocess.run(
        [sys.executable, str(CLIENT_SCRIPT), *args],
        input=stdin_data,
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )


def skill_hook_payload(skill_name):
    return json.dumps(
        {
            "hook_event_name": "PostToolUse",
            "session_id": "abcdef1234567890",
            "tool_name": "Skill",
            "tool_input": {"skill": skill_name},
            "tool_response": {"ok": True},
        }
    )


class TestCaptureClient:
    """Privacy invariants of the client (RFC-0001 §6, §8)."""

    def test_capture_off_by_default(self, tmp_path, registry_skill_names):
        skill = sorted(registry_skill_names)[0]
        result = run_client(["capture"], tmp_path, stdin_data=skill_hook_payload(skill))
        assert result.returncode == 0
        assert not (tmp_path / "spool" / "events.jsonl").exists()

    def test_capture_after_enable(self, tmp_path, registry_skill_names):
        skill = sorted(registry_skill_names)[0]
        assert run_client(["enable"], tmp_path).returncode == 0
        config = json.loads((tmp_path / "config.json").read_text())
        assert config["enabled"] is True
        assert len(config["installation_id"]) == 32

        result = run_client(["capture"], tmp_path, stdin_data=skill_hook_payload(skill))
        assert result.returncode == 0
        events = (tmp_path / "spool" / "events.jsonl").read_text().strip().splitlines()
        assert len(events) == 1
        event = json.loads(events[0])
        assert event["skill"] == skill
        assert event["outcome"] == "success"

    def test_kill_switch_beats_enable(self, tmp_path, registry_skill_names):
        skill = sorted(registry_skill_names)[0]
        run_client(["enable"], tmp_path)
        result = run_client(
            ["capture"],
            tmp_path,
            stdin_data=skill_hook_payload(skill),
            extra_env={"AGORA_FEEDBACK": "0"},
        )
        assert result.returncode == 0
        assert not (tmp_path / "spool" / "events.jsonl").exists()

    def test_non_agora_skills_not_recorded(self, tmp_path):
        run_client(["enable"], tmp_path)
        result = run_client(
            ["capture"],
            tmp_path,
            stdin_data=skill_hook_payload("some-other-marketplace-skill"),
        )
        assert result.returncode == 0
        assert not (tmp_path / "spool" / "events.jsonl").exists()

    def test_capture_never_fails_on_garbage(self, tmp_path):
        run_client(["enable"], tmp_path)
        assert (
            run_client(["capture"], tmp_path, stdin_data="not json at all").returncode
            == 0
        )

    def test_report_validates_against_aggregator(self, tmp_path, registry_skill_names):
        skill = sorted(registry_skill_names)[0]
        run_client(["enable"], tmp_path)
        run_client(["capture"], tmp_path, stdin_data=skill_hook_payload(skill))
        result = run_client(["report"], tmp_path)
        assert result.returncode == 0
        report = json.loads((tmp_path / "reports" / "pending-report.json").read_text())
        assert aggregate_mod.validate_report(report) == []

    def test_submit_without_confirm_sends_nothing(self, tmp_path, registry_skill_names):
        skill = sorted(registry_skill_names)[0]
        run_client(["enable"], tmp_path)
        run_client(["capture"], tmp_path, stdin_data=skill_hook_payload(skill))
        run_client(["report"], tmp_path)
        result = run_client(["submit"], tmp_path)
        assert result.returncode == 0
        assert "EXACT PAYLOAD" in result.stdout
        assert "Nothing was sent" in result.stdout
        assert (tmp_path / "reports" / "pending-report.json").exists()  # not archived

    def test_pii_lint_blocks_submission(self, tmp_path, registry_skill_names):
        skill = sorted(registry_skill_names)[0]
        run_client(["enable"], tmp_path)
        run_client(["capture"], tmp_path, stdin_data=skill_hook_payload(skill))
        run_client(["report"], tmp_path)
        run_client(
            ["insight", "add", skill, "bug", "contact me at someone@example.com"],
            tmp_path,
        )
        result = run_client(["submit", "--confirm"], tmp_path)
        assert result.returncode == 1
        assert "BLOCKED" in result.stdout

    def test_traffic_kill_switch_blocks_submit(self, tmp_path, registry_skill_names):
        skill = sorted(registry_skill_names)[0]
        run_client(["enable"], tmp_path)
        run_client(["capture"], tmp_path, stdin_data=skill_hook_payload(skill))
        run_client(["report"], tmp_path)
        result = run_client(
            ["submit", "--confirm"],
            tmp_path,
            extra_env={"CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"},
        )
        assert result.returncode == 1
        assert "refused" in result.stdout

    def test_purge_removes_everything(self, tmp_path, registry_skill_names):
        skill = sorted(registry_skill_names)[0]
        run_client(["enable"], tmp_path)
        run_client(["capture"], tmp_path, stdin_data=skill_hook_payload(skill))
        run_client(["report"], tmp_path)
        assert run_client(["purge"], tmp_path).returncode == 0
        assert not (tmp_path / "spool").exists()
        assert not (tmp_path / "reports").exists()


class TestPiiLint:
    def test_detects_email_and_paths(self):
        report = make_report(
            "x",
            insights=[
                {
                    "type": "bug",
                    "text": "fails for me at /Users/jane/project",
                    "confidence": 0.5,
                },
            ],
        )
        findings = client_mod.pii_findings(report)
        assert len(findings) == 1

    def test_clean_insights_pass(self):
        report = make_report(
            "x",
            insights=[
                {
                    "type": "improvement",
                    "text": "the skill should mention cleveref",
                    "confidence": 0.5,
                },
            ],
        )
        assert client_mod.pii_findings(report) == []


class TestValidationHardening:
    """Hostile-input hardening: reports come from a public issue inbox, so a
    malformed or adversarial report must be rejected — never crash the run."""

    def test_insights_not_a_list_rejected_not_crash(self, registry_skill_names):
        report = make_report(sorted(registry_skill_names)[0])
        report["skills"][0]["insights"] = "surprise, a string"
        assert aggregate_mod.validate_report(report)

    def test_non_numeric_confidence_rejected(self, registry_skill_names):
        report = make_report(
            sorted(registry_skill_names)[0],
            insights=[{"type": "bug", "text": "meh", "confidence": "high"}],
        )
        assert aggregate_mod.validate_report(report)

    def test_out_of_range_confidence_rejected(self, registry_skill_names):
        report = make_report(
            sorted(registry_skill_names)[0],
            insights=[{"type": "bug", "text": "meh", "confidence": 7.0}],
        )
        assert aggregate_mod.validate_report(report)

    def test_unknown_outcome_keys_rejected(self, registry_skill_names):
        report = make_report(sorted(registry_skill_names)[0])
        report["skills"][0]["outcomes"]["<script>alert(1)</script>"] = 1
        assert aggregate_mod.validate_report(report)

    def test_unknown_error_codes_rejected(self, registry_skill_names):
        report = make_report(sorted(registry_skill_names)[0])
        report["skills"][0]["error_codes"] = {"@everyone pwned": 1}
        assert aggregate_mod.validate_report(report)

    def test_control_chars_in_insight_rejected(self, registry_skill_names):
        report = make_report(
            sorted(registry_skill_names)[0],
            insights=[{"type": "bug", "text": "line1\x00\x1bline2", "confidence": 0.5}],
        )
        assert aggregate_mod.validate_report(report)

    def test_markdown_hostile_installation_id_rejected(self, registry_skill_names):
        report = make_report(
            sorted(registry_skill_names)[0],
            installation="@everyone [click](https://evil.example)",
        )
        assert aggregate_mod.validate_report(report)

    def test_absurd_invocation_count_rejected(self, registry_skill_names):
        report = make_report(sorted(registry_skill_names)[0])
        report["skills"][0]["invocations"] = 10**12
        assert aggregate_mod.validate_report(report)

    def test_hostile_report_never_kills_the_run(self, tmp_path, registry_skill_names):
        known = sorted(registry_skill_names)[0]
        hostile = make_report(known, report_id="r-hostile", installation="h" * 32)
        hostile["skills"][0]["insights"] = {"not": "a list"}
        good = make_report(known, report_id="r-good", installation="g" * 32)
        input_dir = tmp_path / "reports"
        input_dir.mkdir()
        (input_dir / "hostile.json").write_text(json.dumps(hostile))
        (input_dir / "good.json").write_text(json.dumps(good))
        (input_dir / "not-even-json.json").write_text("}{")
        output = tmp_path / "feedback.json"

        rc = aggregate_mod.main(
            ["--input-dir", str(input_dir), "--output", str(output)]
        )
        assert rc == 0
        result = json.loads(output.read_text())
        assert result["stats"]["reports"] == 1  # only the good one survives
        assert known in result["skills"]
