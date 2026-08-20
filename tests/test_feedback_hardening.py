"""Hardening regression tests for the RFC-0001 feedback client.

One test per audited defect in plugins/toolkit/scripts/agora_feedback.py:

- finding 2: the URL PII pattern missed compound credential parameter names
  (``?access_token=``, ``?api_key=``, ``?client_secret=``, ``?auth_token=``).
- finding 3: control characters reached the public issue, because only the
  weekly aggregation rejected them.
- finding 4: the preview-then-confirm consent gate was prose only, so a bare
  ``submit --confirm`` printed the payload and sent it in one invocation.
- finding 5: the home-directory PII pattern hardcoded drive C and was
  case-sensitive.
- finding 6: the 90-day retention was applied at read time only; the spool
  file itself grew without bound.
- finding 7: a successful submit archived the whole spool, sweeping events
  captured after the report was built.

Every test runs the client as a subprocess with AGORA_HOME pointed at a temp
directory, so ~/.agora is never touched, and any submission path resolves to
a stub ``gh`` that records its arguments instead of reaching the network.

Helpers come from tests/test_feedback.py rather than being redefined here.
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from test_feedback import client_mod, make_report, run_client, skill_hook_payload

# One log line per invocation: the payload argument spans many lines, so the
# stub records only the leading arguments.
GH_STUB = """#!/bin/sh
printf 'gh %s %s\\n' "$1" "$2" >> "$GH_STUB_LOG"
echo https://github.com/example/research-agora/issues/1
"""


class GhStub:
    """A fake GitHub CLI on PATH. Records calls; never touches the network."""

    def __init__(self, bin_dir: Path, log: Path):
        self.log = log
        self.env = {
            "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}",
            "GH_STUB_LOG": str(log),
        }

    @property
    def calls(self) -> list[str]:
        if not self.log.exists():
            return []
        return [line for line in self.log.read_text().splitlines() if line.strip()]


@pytest.fixture
def gh_stub(tmp_path) -> GhStub:
    bin_dir = tmp_path / "stub-bin"
    bin_dir.mkdir()
    script = bin_dir / "gh"
    script.write_text(GH_STUB)
    script.chmod(0o755)
    return GhStub(bin_dir, tmp_path / "gh-calls.log")


@pytest.fixture(scope="session")
def known_skill() -> str:
    """A skill name capture accepts, resolved the way the client resolves it."""
    names = client_mod.known_skill_names()
    if not names:
        pytest.skip("no skill name list resolved from the checkout")
    return sorted(names)[0]


@pytest.fixture
def home(tmp_path, known_skill) -> Path:
    """An enabled installation with one captured event and a pending report."""
    path = tmp_path / "agora-home"
    run_client(["enable"], path)
    run_client(["capture"], path, stdin_data=skill_hook_payload(known_skill))
    run_client(["report"], path)
    return path


def spool_events(home: Path) -> list[dict]:
    spool = home / "spool" / "events.jsonl"
    if not spool.exists():
        return []
    return [json.loads(line) for line in spool.read_text().splitlines() if line.strip()]


def append_event(home: Path, skill: str, ts: datetime) -> None:
    """Append a spool line in the shape cmd_capture writes.

    Used where a test needs an event at a controlled time: spool timestamps
    have second precision, so two real captures in the same second cannot be
    ordered against a cutoff.
    """
    event = {
        "event": "invocation",
        "session": "beefcafe",
        "skill": skill,
        "outcome": "success",
        "error_code": None,
        "duration_bucket": None,
        "model": None,
        "ts": ts.isoformat(timespec="seconds"),
    }
    spool = home / "spool" / "events.jsonl"
    spool.parent.mkdir(parents=True, exist_ok=True)
    with open(spool, "a") as f:
        f.write(json.dumps(event) + "\n")


def insight_report(text: str) -> dict:
    return make_report("x", insights=[{"type": "bug", "text": text, "confidence": 0.5}])


class TestCredentialQueryParameters:
    """Finding 2: the lint must catch the parameter names OAuth and API
    providers actually use, not only a bare ``?token=``."""

    @pytest.mark.parametrize(
        "url",
        [
            "https://api.example.com/v1/me?access_token=abc123",
            "https://api.example.com/v1/me?api_key=abc123",
            "https://api.example.com/v1/me?client_secret=abc123",
            "https://api.example.com/v1/me?auth_token=abc123",
            "https://api.example.com/v1/me?token=abc123",
            "https://api.example.com/v1/me?page=2&refresh_token=abc123",
            "http://api.example.com/v1/me?X-Api-Key=abc123",
        ],
    )
    def test_credential_query_is_flagged(self, url):
        findings = client_mod.pii_findings(insight_report(f"broke on {url}"))
        assert len(findings) == 1, f"unflagged credential URL: {url}"

    @pytest.mark.parametrize(
        "url",
        [
            "https://example.com/docs?page=2",
            "https://example.com/skills/paper-references",
        ],
    )
    def test_benign_urls_still_pass(self, url):
        assert client_mod.pii_findings(insight_report(f"see {url}")) == []

    def test_submit_blocks_on_a_credential_url(self, home, known_skill, gh_stub):
        run_client(
            [
                "insight",
                "add",
                known_skill,
                "bug",
                "auth breaks on https://api.example.com/v1?api_key=abc123",
            ],
            home,
        )
        result = run_client(["submit", "--confirm"], home, extra_env=gh_stub.env)

        assert result.returncode == 1
        assert "BLOCKED" in result.stdout
        assert "URL with token-like query" in result.stdout
        assert gh_stub.calls == []


class TestHomeDirectoryPaths:
    """Finding 5: any drive letter, either case."""

    @pytest.mark.parametrize(
        "path",
        [
            r"D:\Users\jane\project",
            r"C:\Users\jane\project",
            r"d:\users\jane\project",
            "/users/jane/project",
            "/Users/jane/project",
            "/home/jane/project",
            "/HOME/jane/project",
        ],
    )
    def test_home_path_is_flagged(self, path):
        findings = client_mod.pii_findings(insight_report(f"fails at {path}"))
        assert len(findings) == 1, f"unflagged home path: {path}"

    def test_ordinary_text_still_passes(self):
        assert (
            client_mod.pii_findings(insight_report("the skill should cite cleveref"))
            == []
        )


class TestControlCharacters:
    """Finding 3: the client, not only the weekly aggregation, must refuse
    control characters — an accepted insight sits in a live public issue
    until the aggregator next runs, and `insight list` prints it raw."""

    def test_findings_report_where_the_characters_are(self):
        report = insight_report("line1\x00\x1bline2")
        findings = client_mod.control_char_findings(report)

        assert len(findings) == 1
        assert "insights[0].text" in findings[0]

    def test_clean_payload_has_no_findings(self):
        assert client_mod.control_char_findings(insight_report("plain text")) == []

    def test_insight_add_rejects_control_characters(self, home, known_skill):
        result = run_client(
            ["insight", "add", known_skill, "bug", "red \x1b[31malert\x1b[0m"],
            home,
        )

        assert result.returncode == 1
        assert "control characters" in result.stdout
        report = json.loads((home / "reports" / "pending-report.json").read_text())
        assert [e["insights"] for e in report["skills"]] == [[]]

    def test_submit_blocks_control_characters_in_the_payload(
        self, home, known_skill, gh_stub
    ):
        """A hand-edited pending report bypasses the insight-add check."""
        report_path = home / "reports" / "pending-report.json"
        report = json.loads(report_path.read_text())
        report["skills"][0]["insights"] = [
            {"type": "bug", "text": "escape \x1b]0;pwned\x07 here", "confidence": 0.5}
        ]
        report_path.write_text(json.dumps(report, indent=2))

        preview = run_client(["submit"], home, extra_env=gh_stub.env)
        assert preview.returncode == 1
        assert "BLOCKED" in preview.stdout

        result = run_client(
            ["submit", "--confirm", "--allow-pii"], home, extra_env=gh_stub.env
        )
        assert result.returncode == 1
        assert "BLOCKED" in result.stdout
        assert gh_stub.calls == []


class TestSubmitConsentGate:
    """Finding 4: two invocations, structurally. A confirmation is honoured
    only against a token committing to the exact payload a previous, separate
    invocation printed for review."""

    def test_bare_submit_sends_nothing(self, home, gh_stub):
        result = run_client(["submit"], home, extra_env=gh_stub.env)

        assert result.returncode == 0
        assert "EXACT PAYLOAD" in result.stdout
        assert "Nothing was sent" in result.stdout
        assert gh_stub.calls == []
        assert (home / "reports" / "pending-report.json").exists()
        assert (home / "spool" / "events.jsonl").exists()  # not archived

    def test_confirm_without_a_preview_refuses(self, home, gh_stub):
        result = run_client(["submit", "--confirm"], home, extra_env=gh_stub.env)

        assert result.returncode == 1
        assert "no reviewed payload on record" in result.stdout
        assert gh_stub.calls == []
        assert (home / "reports" / "pending-report.json").exists()
        assert (home / "spool" / "events.jsonl").exists()

    def test_preview_then_confirm_submits(self, home, gh_stub):
        assert run_client(["submit"], home, extra_env=gh_stub.env).returncode == 0
        result = run_client(["submit", "--confirm"], home, extra_env=gh_stub.env)

        assert result.returncode == 0
        assert "Submitted: https://github.com/example" in result.stdout
        assert len(gh_stub.calls) == 1
        assert not (home / "reports" / "pending-report.json").exists()
        assert not (home / "reports" / "submit-token.json").exists()  # single use

    def test_the_token_commits_to_the_payload_that_was_shown(
        self, home, known_skill, gh_stub
    ):
        """An insight added after the preview changes the payload, so the
        earlier consent cannot carry it."""
        run_client(["submit"], home, extra_env=gh_stub.env)
        run_client(
            ["insight", "add", known_skill, "praise", "saved me an afternoon"], home
        )
        result = run_client(["submit", "--confirm"], home, extra_env=gh_stub.env)

        assert result.returncode == 1
        assert "changed after it was reviewed" in result.stdout
        assert gh_stub.calls == []

    def test_a_rebuilt_report_needs_a_new_preview(self, home, gh_stub):
        run_client(["submit"], home, extra_env=gh_stub.env)
        run_client(["report"], home)  # fresh report_id
        result = run_client(["submit", "--confirm"], home, extra_env=gh_stub.env)

        assert result.returncode == 1
        assert "different report" in result.stdout
        assert gh_stub.calls == []

    def test_a_stale_preview_refuses(self, home, gh_stub):
        run_client(["submit"], home, extra_env=gh_stub.env)
        token_path = home / "reports" / "submit-token.json"
        token = json.loads(token_path.read_text())
        token["issued"] = int(time.time()) - client_mod.SUBMIT_TOKEN_TTL_SECONDS - 60
        token_path.write_text(json.dumps(token))

        result = run_client(["submit", "--confirm"], home, extra_env=gh_stub.env)

        assert result.returncode == 1
        assert "stale" in result.stdout
        assert gh_stub.calls == []

    def test_a_tampered_token_refuses(self, home, gh_stub):
        run_client(["submit"], home, extra_env=gh_stub.env)
        token_path = home / "reports" / "submit-token.json"
        token = json.loads(token_path.read_text())
        token["payload_sha256"] = "0" * 64
        token_path.write_text(json.dumps(token))

        result = run_client(["submit", "--confirm"], home, extra_env=gh_stub.env)

        assert result.returncode == 1
        assert gh_stub.calls == []

    @pytest.mark.parametrize(
        "kill_switch",
        [
            {"AGORA_FEEDBACK": "0"},
            {"CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"},
        ],
    )
    def test_kill_switches_still_block_a_reviewed_payload(
        self, home, gh_stub, kill_switch
    ):
        run_client(["submit"], home, extra_env=gh_stub.env)
        result = run_client(
            ["submit", "--confirm"], home, extra_env={**gh_stub.env, **kill_switch}
        )

        assert result.returncode == 1
        assert "refused" in result.stdout
        assert gh_stub.calls == []
        assert (home / "reports" / "pending-report.json").exists()


class TestSpoolRetention:
    """Finding 6: the 90-day window must hold on disk, not only in memory."""

    def test_capture_prunes_expired_events(self, tmp_path, known_skill):
        home = tmp_path / "agora-home"
        run_client(["enable"], home)
        append_event(
            home, known_skill, datetime.now() - timedelta(days=200)
        )  # long expired
        append_event(home, known_skill, datetime.now() - timedelta(days=10))

        result = run_client(
            ["capture"], home, stdin_data=skill_hook_payload(known_skill)
        )

        assert result.returncode == 0
        stamps = [e["ts"] for e in spool_events(home)]
        assert len(stamps) == 2  # the 200-day-old event is gone from the file
        cutoff = datetime.now() - timedelta(days=client_mod.SPOOL_RETENTION_DAYS)
        assert all(datetime.fromisoformat(ts) >= cutoff for ts in stamps)

    def test_pruning_is_throttled_and_never_breaks_the_hook(
        self, tmp_path, known_skill
    ):
        """One rewrite per interval keeps retention off the hot path of every
        skill invocation; the hook exits 0 either way."""
        home = tmp_path / "agora-home"
        run_client(["enable"], home)
        run_client(["capture"], home, stdin_data=skill_hook_payload(known_skill))
        append_event(home, known_skill, datetime.now() - timedelta(days=200))

        result = run_client(
            ["capture"], home, stdin_data=skill_hook_payload(known_skill)
        )

        assert result.returncode == 0
        assert len(spool_events(home)) == 3  # prune already ran this interval

    def test_capture_exits_zero_on_a_corrupt_spool(self, tmp_path, known_skill):
        home = tmp_path / "agora-home"
        run_client(["enable"], home)
        spool = home / "spool" / "events.jsonl"
        spool.parent.mkdir(parents=True, exist_ok=True)
        spool.write_text("}{ not json\n" + json.dumps({"event": "invocation"}) + "\n")

        result = run_client(
            ["capture"], home, stdin_data=skill_hook_payload(known_skill)
        )

        assert result.returncode == 0
        events = spool_events(home)
        assert [e["skill"] for e in events] == [known_skill]

    def test_disable_prunes_expired_events(self, tmp_path, known_skill):
        """The hook is the throttled pruner and it stops running at disable."""
        home = tmp_path / "agora-home"
        run_client(["enable"], home)
        append_event(home, known_skill, datetime.now() - timedelta(days=200))
        append_event(home, known_skill, datetime.now())

        assert run_client(["disable"], home).returncode == 0
        assert len(spool_events(home)) == 1

    def test_status_prunes_expired_events(self, tmp_path, known_skill):
        home = tmp_path / "agora-home"
        run_client(["enable"], home)
        append_event(home, known_skill, datetime.now() - timedelta(days=200))
        append_event(home, known_skill, datetime.now())

        result = run_client(["status"], home)

        assert result.returncode == 0
        assert len(spool_events(home)) == 1
        assert "spool events:       1" in result.stdout


class TestArchiveCoverage:
    """Finding 7: archive what the report covered, leave later arrivals."""

    def test_events_captured_after_the_report_stay_live(
        self, home, known_skill, gh_stub
    ):
        append_event(home, known_skill, datetime.now() + timedelta(hours=1))

        run_client(["submit"], home, extra_env=gh_stub.env)
        result = run_client(["submit", "--confirm"], home, extra_env=gh_stub.env)
        assert result.returncode == 0

        remaining = spool_events(home)
        assert len(remaining) == 1  # only the post-report event
        assert remaining[0]["session"] == "beefcafe"
        archived = sorted((home / "spool" / "archive").glob("*.jsonl"))
        assert len(archived) == 1
        assert len(archived[0].read_text().strip().splitlines()) == 1

    def test_the_next_report_still_counts_the_later_event(
        self, home, known_skill, gh_stub
    ):
        """The under-count this fix removes: the swept event never reached a
        report at all."""
        append_event(home, known_skill, datetime.now() + timedelta(hours=1))
        run_client(["submit"], home, extra_env=gh_stub.env)
        run_client(["submit", "--confirm"], home, extra_env=gh_stub.env)

        assert run_client(["report"], home).returncode == 0
        report = json.loads((home / "reports" / "pending-report.json").read_text())
        assert [e["invocations"] for e in report["skills"]] == [1]

    def test_missing_cutoff_falls_back_to_archiving_everything(
        self, home, known_skill, gh_stub
    ):
        """A pending report from an older client carries no coverage mark."""
        append_event(home, known_skill, datetime.now() + timedelta(hours=1))
        (home / "reports" / "pending-cutoff.json").unlink()

        run_client(["submit"], home, extra_env=gh_stub.env)
        assert (
            run_client(["submit", "--confirm"], home, extra_env=gh_stub.env).returncode
            == 0
        )
        assert not (home / "spool" / "events.jsonl").exists()

    def test_a_failed_submission_archives_nothing(self, home, tmp_path):
        """No gh on PATH: the report is not lost and the spool stays put."""
        empty_bin = tmp_path / "empty-bin"
        empty_bin.mkdir()
        env = {"PATH": str(empty_bin)}
        run_client(["submit"], home, extra_env=env)
        result = run_client(["submit", "--confirm"], home, extra_env=env)

        assert result.returncode == 1
        assert "Manual fallback" in result.stdout
        assert (home / "spool" / "events.jsonl").exists()
        assert (home / "reports" / "pending-report.json").exists()
