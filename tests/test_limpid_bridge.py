"""Tests for the optional limpid bridge.

The bridge's whole contract is that it never breaks the caller: limpid is not
on npm and most marketplace users will not have it, so every failure path has
to return available=False rather than raise. These tests run without limpid
installed, which is the case that matters.
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
BRIDGE_PATH = REPO_ROOT / "scripts" / "limpid_bridge.py"


@pytest.fixture(scope="module")
def bridge():
    spec = importlib.util.spec_from_file_location("limpid_bridge", BRIDGE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestResolution:
    def test_bridge_exists(self) -> None:
        assert BRIDGE_PATH.exists()

    def test_missing_env_path_resolves_to_none(self, bridge, monkeypatch) -> None:
        """A LIMPID_CLI pointing at nothing must not be returned as runnable."""
        monkeypatch.setenv("LIMPID_CLI", "/nonexistent/limpid/cli.js")
        assert bridge.resolve_cli() is None

    def test_js_entry_point_runs_under_node(self, bridge, monkeypatch, tmp_path) -> None:
        cli = tmp_path / "cli.js"
        cli.write_text("// stub")
        monkeypatch.setenv("LIMPID_CLI", str(cli))
        assert bridge.resolve_cli() == ["node", str(cli)]

    def test_binary_entry_point_runs_directly(self, bridge, monkeypatch, tmp_path) -> None:
        cli = tmp_path / "limpid"
        cli.write_text("#!/bin/sh\n")
        monkeypatch.setenv("LIMPID_CLI", str(cli))
        assert bridge.resolve_cli() == [str(cli)]


class TestFailSoft:
    """Every one of these must return available=False, never raise."""

    def test_absent_cli_is_not_an_error(self, bridge, monkeypatch, tmp_path) -> None:
        monkeypatch.setenv("LIMPID_CLI", "")
        monkeypatch.setattr(bridge.shutil, "which", lambda _: None)
        draft = tmp_path / "draft.md"
        draft.write_text("# Title\n\nSome prose.\n")
        out = bridge.run_limpid(str(draft))
        assert out["available"] is False
        assert "not found" in out["reason"]

    def test_missing_file_reports_reason(self, bridge) -> None:
        out = bridge.run_limpid("/nonexistent/draft.tex")
        assert out["available"] is False
        assert "file not found" in out["reason"]

    def test_unknown_register_rejected(self, bridge, tmp_path) -> None:
        draft = tmp_path / "draft.md"
        draft.write_text("text")
        out = bridge.run_limpid(str(draft), register="thesis")
        assert out["available"] is False
        assert "register" in out["reason"]

    def test_non_json_output_reports_reason(self, bridge, monkeypatch, tmp_path) -> None:
        draft = tmp_path / "draft.md"
        draft.write_text("text")
        monkeypatch.setattr(bridge, "resolve_cli", lambda: ["/bin/echo"])
        monkeypatch.setattr(
            bridge.subprocess,
            "run",
            lambda *a, **k: subprocess.CompletedProcess(a, 0, "not json at all", ""),
        )
        out = bridge.run_limpid(str(draft))
        assert out["available"] is False
        assert "not JSON" in out["reason"]

    def test_empty_output_reports_reason(self, bridge, monkeypatch, tmp_path) -> None:
        draft = tmp_path / "draft.md"
        draft.write_text("text")
        monkeypatch.setattr(bridge, "resolve_cli", lambda: ["/bin/true"])
        monkeypatch.setattr(
            bridge.subprocess,
            "run",
            lambda *a, **k: subprocess.CompletedProcess(a, 1, "", "boom"),
        )
        out = bridge.run_limpid(str(draft))
        assert out["available"] is False
        assert "no output" in out["reason"]

    def test_timeout_reports_reason(self, bridge, monkeypatch, tmp_path) -> None:
        draft = tmp_path / "draft.md"
        draft.write_text("text")
        monkeypatch.setattr(bridge, "resolve_cli", lambda: ["/bin/sleep"])

        def _timeout(*a, **k):
            raise subprocess.TimeoutExpired(cmd="limpid", timeout=1)

        monkeypatch.setattr(bridge.subprocess, "run", _timeout)
        out = bridge.run_limpid(str(draft), timeout=1)
        assert out["available"] is False
        assert "timed out" in out["reason"]


class TestNormalize:
    SAMPLE = {
        "file": "draft.md",
        "grade": "B-",
        "metrics": {"passiveFraction": 0.333, "fk": 9.4, "words": 85},
        "findingCount": 4,
        "findings": [
            {
                "ruleId": "voice.hedges",
                "category": "precision",
                "severity": "suggestion",
                "message": 'Hedge words: "arguably".',
                "line": 3,
                "excerpt": "arguably",
            },
            {
                "ruleId": "strunk.active-voice",
                "category": "clarity",
                "severity": "suggestion",
                "message": 'Use the active voice: "been proposed".',
                "line": 3,
                "excerpt": "been proposed",
            },
            {
                "ruleId": "voice.hype",
                "category": "precision",
                "severity": "suggestion",
                "message": 'Hype adjectives: "novel".',
                "line": 5,
                "excerpt": "novel",
            },
            {
                "ruleId": "house.punch-verbs",
                "category": "voice",
                "severity": "warning",
                "message": 'House rule: "binds".',
                "line": 7,
                "excerpt": "binds",
            },
        ],
    }

    def test_maps_rules_onto_pattern_names(self, bridge) -> None:
        out = bridge.normalize(self.SAMPLE)
        assert out["available"] is True
        assert "Hedge Stacking" in out["pattern_evidence"]
        assert "Zombie Sentence" in out["pattern_evidence"]
        assert out["pattern_evidence"]["Hedge Stacking"][0]["line"] == 3

    def test_keeps_unmapped_findings_rather_than_dropping_them(self, bridge) -> None:
        """Hype and house-rule hits map to no pattern but are still real."""
        out = bridge.normalize(self.SAMPLE)
        rules = {f["ruleId"] for f in out["other_findings"]}
        assert "voice.hype" in rules
        assert "house.punch-verbs" in rules

    def test_reports_grade_and_metrics(self, bridge) -> None:
        out = bridge.normalize(self.SAMPLE)
        assert out["grade"] == "B-"
        assert out["metrics"]["fk"] == 9.4

    def test_names_the_patterns_no_script_can_find(self, bridge) -> None:
        out = bridge.normalize(self.SAMPLE)
        assert set(out["patterns_needing_judgment"]) == {
            "Idea Soup",
            "Buried Lede",
            "Orphan Transition",
            "Scale Mismatch",
            "Jargon Cliff",
        }


class TestPatternMapAgreesWithSkill:
    """Every pattern the map targets must exist in writing-diagnosis.md.

    writing-diagnosis.md is the source of record for the pattern library, so a
    mapping that names a pattern the skill does not define would produce
    evidence filed under a heading no one can look up.
    """

    def test_mapped_patterns_exist_in_the_skill(self, bridge) -> None:
        skill = (
            REPO_ROOT / "plugins" / "write" / "commands" / "writing-diagnosis.md"
        ).read_text()
        missing = sorted(
            {p for p in bridge.RULE_TO_PATTERN.values() if p not in skill}
        )
        assert not missing, f"Patterns not defined in writing-diagnosis.md: {missing}"

    def test_judgment_only_patterns_exist_in_the_skill(self, bridge) -> None:
        skill = (
            REPO_ROOT / "plugins" / "write" / "commands" / "writing-diagnosis.md"
        ).read_text()
        out = bridge.normalize({"findings": []})
        missing = [p for p in out["patterns_needing_judgment"] if p not in skill]
        assert not missing, f"Patterns not defined in writing-diagnosis.md: {missing}"


class TestCli:
    def test_check_flag_reports_availability_and_exits_zero(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(BRIDGE_PATH), "--check"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0
        payload = json.loads(proc.stdout)
        assert "available" in payload

    def test_absent_limpid_still_exits_zero(self, tmp_path) -> None:
        """The caller falls back; absence is not a failure."""
        draft = tmp_path / "draft.md"
        draft.write_text("# T\n\nSome prose here.\n")
        # An empty PATH would hide the interpreter too, so point PATH at a
        # real but limpid-free directory.
        empty_bin = tmp_path / "bin"
        empty_bin.mkdir()
        proc = subprocess.run(
            [sys.executable, str(BRIDGE_PATH), str(draft)],
            capture_output=True,
            text=True,
            check=False,
            env={"PATH": str(empty_bin), "LIMPID_CLI": ""},
        )
        assert proc.returncode == 0
        assert "available" in json.loads(proc.stdout)
