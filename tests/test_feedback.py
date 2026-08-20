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
CLIENT_SCRIPT = REPO_ROOT / "plugins" / "toolkit" / "scripts" / "agora_feedback.py"


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


def make_reports(skill: str, count: int, **kwargs):
    """One report per distinct installation for `skill`.

    Publication is gated on unique installations (RFC-0001 §11), so a test
    that expects a skill in the aggregate has to supply enough of them.
    """
    return [
        make_report(
            skill,
            report_id=f"r-{skill}-{i}",
            installation=f"installation-{i:04d}",
            **kwargs,
        )
        for i in range(count)
    ]


def run_aggregate(tmp_path, reports):
    """Run the aggregator over `reports` and return (parsed aggregate, path)."""
    input_dir = tmp_path / "reports"
    input_dir.mkdir(exist_ok=True)
    for i, report in enumerate(reports):
        (input_dir / f"{i}.json").write_text(json.dumps(report))
    output = tmp_path / "feedback.json"
    assert (
        aggregate_mod.main(["--input-dir", str(input_dir), "--output", str(output)])
        == 0
    )
    return json.loads(output.read_text()), output


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
        k = aggregate_mod.MIN_INSTALLATIONS_PUBLISH
        reports = [
            *make_reports(known[0], k),
            make_report(  # duplicate id
                known[0], report_id=f"r-{known[0]}-0", installation="installation-0000"
            ),
            *make_reports(known[1], k, success=2, error=8),
            *make_reports("no-such-skill-xyz", k),
        ]
        result, _ = run_aggregate(tmp_path, reports)

        assert result["stats"]["reports"] == 3 * k  # duplicate dropped
        assert known[0] in result["skills"]
        assert known[1] in result["skills"]
        assert "no-such-skill-xyz" not in result["skills"]  # unknown skill dropped
        assert result["skills"][known[0]]["report_count"] == k
        assert result["skills"][known[0]]["unique_installations"] == k
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


class TestKAnonymityFloor:
    """Per-skill breakdowns stay unpublished below k installations (RFC-0001 §11).

    The aggregate is committed to a public repository, so the threshold has to
    hold in the data the aggregator writes rather than in the site renderer
    alone: below three unique installations, the counters and the free-text
    insights of a skill are one installation's usage profile, which §9.3 rules
    out publishing.
    """

    INSIGHTS = [
        {
            "type": "bug",
            "text": "sentinel insight text that must never reach the aggregate",
            "confidence": 0.9,
        }
    ]

    def test_threshold_is_three(self):
        """§11 fixes k = 3; §12.2 documents the same floor for the HTTP sink."""
        assert aggregate_mod.MIN_INSTALLATIONS_PUBLISH == 3

    def test_site_renderer_shares_the_threshold(self):
        """One source of truth: the renderer's guard must not drift from it."""
        site_mod = _load_module(
            "generate_site", REPO_ROOT / "scripts" / "generate-site.py"
        )
        assert (
            site_mod.FEEDBACK_MIN_INSTALLATIONS
            == aggregate_mod.MIN_INSTALLATIONS_PUBLISH
        )

    def test_one_installation_is_suppressed(self, tmp_path, registry_skill_names):
        skill = sorted(registry_skill_names)[0]
        result, output = run_aggregate(tmp_path, make_reports(skill, 1))

        assert result["skills"] == {}
        assert result["stats"]["skills_suppressed"] == 1
        assert result["stats"]["reports"] == 1  # ingestion stays transparent
        assert skill not in output.read_text()

    def test_two_installations_are_suppressed(self, tmp_path, registry_skill_names):
        skill = sorted(registry_skill_names)[0]
        result, output = run_aggregate(tmp_path, make_reports(skill, 2))

        assert result["skills"] == {}
        assert result["stats"]["skills_suppressed"] == 1
        assert skill not in output.read_text()

    def test_three_installations_are_published(self, tmp_path, registry_skill_names):
        skill = sorted(registry_skill_names)[0]
        result, _ = run_aggregate(
            tmp_path,
            make_reports(
                skill, aggregate_mod.MIN_INSTALLATIONS_PUBLISH, insights=self.INSIGHTS
            ),
        )

        published = result["skills"][skill]
        assert published["unique_installations"] == 3
        assert published["invocations"] == 30
        assert published["outcomes"]["success"] == 27
        assert published["top_insights"][0]["text"] == self.INSIGHTS[0]["text"]
        assert result["stats"]["skills_suppressed"] == 0

    def test_insights_are_never_published_below_threshold(
        self, tmp_path, registry_skill_names
    ):
        """Free text is the sharpest disclosure in a report; it goes first."""
        skill = sorted(registry_skill_names)[0]
        for installations in (1, 2):
            run_dir = tmp_path / f"k{installations}"
            run_dir.mkdir()
            result, output = run_aggregate(
                run_dir, make_reports(skill, installations, insights=self.INSIGHTS)
            )

            assert self.INSIGHTS[0]["text"] not in output.read_text()
            assert result["skills"] == {}

    def test_all_below_threshold_still_produces_schema_valid_aggregate(
        self, tmp_path, registry_skill_names
    ):
        """An all-suppressed window writes an empty but well-formed aggregate,
        so consumers keep reading the same shape."""
        known = sorted(registry_skill_names)[:2]
        result, _ = run_aggregate(
            tmp_path,
            [*make_reports(known[0], 1), *make_reports(known[1], 2)],
        )

        assert result["version"] == "1.0.0"
        assert result["schema_version"] == 1
        assert isinstance(result["skills"], dict) and result["skills"] == {}
        assert set(result["window"]) == {"from", "to"}
        assert result["stats"]["reports"] == 3
        assert result["stats"]["skills_with_feedback"] == 0
        assert result["stats"]["skills_suppressed"] == 2

    def test_digest_counts_suppressed_skills_without_naming_them(
        self, tmp_path, registry_skill_names, capsys
    ):
        """The digest becomes a public PR body, so it withholds the names too."""
        published, suppressed = sorted(registry_skill_names)[:2]
        run_aggregate(
            tmp_path,
            [
                *make_reports(published, aggregate_mod.MIN_INSTALLATIONS_PUBLISH),
                *make_reports(suppressed, 1, insights=self.INSIGHTS),
            ],
        )
        digest = capsys.readouterr().out

        assert published in digest
        assert suppressed not in digest
        assert self.INSIGHTS[0]["text"] not in digest
        assert "publication floor (names withheld" in digest


def run_client(args, tmp_home, stdin_data=None, extra_env=None, script=None):
    env = {**os.environ, "AGORA_HOME": str(tmp_home)}
    env.pop("AGORA_FEEDBACK", None)
    env.update(extra_env or {})
    return subprocess.run(
        [sys.executable, str(script or CLIENT_SCRIPT), *args],
        input=stdin_data,
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )


def install_client_in_cache_layout(root, ship_manifest=True, ship_plugin_manifest=None):
    """Copy the client where Claude Code actually runs it from.

    ~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/scripts/ contains
    plugin directories only — no marketplace root above the script — which is
    where the original registry lookup silently found nothing. The two shipped
    manifests are the layout's only name sources, and each can be withheld on
    its own to check that capture fails closed without it.
    """
    if ship_plugin_manifest is None:
        ship_plugin_manifest = ship_manifest
    scripts = (
        root
        / "plugins"
        / "cache"
        / "research-agora"
        / "development"
        / "1.1.0"
        / "scripts"
    )
    scripts.mkdir(parents=True)
    installed = scripts / CLIENT_SCRIPT.name
    installed.write_text(CLIENT_SCRIPT.read_text())
    if ship_manifest:
        manifest = CLIENT_SCRIPT.parent / client_mod.SKILL_NAMES_FILE
        (scripts / client_mod.SKILL_NAMES_FILE).write_text(manifest.read_text())
    if ship_plugin_manifest:
        manifest = CLIENT_SCRIPT.parent / client_mod.PLUGIN_NAMES_FILE
        (scripts / client_mod.PLUGIN_NAMES_FILE).write_text(manifest.read_text())
    return installed


def skill_payload(skill_name, plugin="toolkit"):
    """A Skill-tool PostToolUse payload, as the hook receives it.

    Real invocations name the owning plugin ("toolkit:code-simplify"); pass
    plugin=None for the bare form, which capture cannot attribute.
    """
    qualified = f"{plugin}:{skill_name}" if plugin else skill_name
    return {
        "hook_event_name": "PostToolUse",
        "session_id": "abcdef1234567890",
        "tool_name": "Skill",
        "tool_input": {"skill": qualified},
        "tool_response": {"ok": True},
    }


def skill_hook_payload(skill_name, plugin="toolkit"):
    return json.dumps(skill_payload(skill_name, plugin))


@pytest.fixture
def direct_skill_names(tmp_path, monkeypatch):
    manifest = tmp_path / "skill-names.json"
    manifest.write_text(json.dumps({"names": ["devils-advocate"]}))
    monkeypatch.setenv("AGORA_SKILL_NAMES_FILE", str(manifest))
    monkeypatch.setattr(client_mod, "_KNOWN_SKILLS", None)
    monkeypatch.setattr(client_mod, "_KNOWN_PLUGINS", None)


@pytest.fixture
def colliding_skill_names(tmp_path, monkeypatch):
    """Registry names that collide with the personal and third-party skills
    seen in real transcripts, so every rejection below is the provenance rule
    rather than a name mismatch."""
    manifest = tmp_path / "skill-names.json"
    manifest.write_text(
        json.dumps(
            {
                "names": [
                    "audience-checker",
                    "brainstorming",
                    "commit",
                    "devils-advocate",
                    "obsidian-markdown",
                    "ship",
                ]
            }
        )
    )
    monkeypatch.setenv("AGORA_SKILL_NAMES_FILE", str(manifest))
    monkeypatch.setattr(client_mod, "_KNOWN_SKILLS", None)
    monkeypatch.setattr(client_mod, "_KNOWN_PLUGINS", None)


def subagent_hook_payload(tool_name, subagent_type):
    return {
        "hook_event_name": "PostToolUse",
        "session_id": "abcdef1234567890",
        "tool_name": tool_name,
        "tool_input": {"subagent_type": subagent_type},
        "tool_response": {"ok": True},
    }


class TestHookPayloadEvents:
    def test_agent_dispatch_produces_subagent_event(self, direct_skill_names):
        event = client_mod.event_from_hook_payload(
            subagent_hook_payload(
                "Agent", "verify:devils-advocate"
            )
        )

        assert event["event"] == "subagent"
        assert event["skill"] == "devils-advocate"

    def test_task_dispatch_remains_backward_compatible(self, direct_skill_names):
        event = client_mod.event_from_hook_payload(
            subagent_hook_payload(
                "Task", "verify:devils-advocate"
            )
        )
        agent_event = client_mod.event_from_hook_payload(
            subagent_hook_payload(
                "Agent", "verify:devils-advocate"
            )
        )

        assert event == agent_event
        assert event["event"] == "subagent"
        assert event["skill"] == "devils-advocate"

    def test_unknown_agent_subagent_type_is_rejected(self, direct_skill_names):
        event = client_mod.event_from_hook_payload(
            subagent_hook_payload("Agent", "other-plugin:unknown-agent")
        )

        assert event is None


class TestSkillProvenance:
    """Attribution comes from the plugin prefix, not from the bare name.

    Matching the tail alone recorded a user's own ~/.claude/commands/commit.md
    as the toolkit plugin's `code-simplify`, which is how personal usage could
    reach a public issue — the collision variant of the leak hardened in
    issue #25. Every name below is a value observed in real hook payloads.
    """

    def test_agora_prefixed_skill_is_captured(self, colliding_skill_names):
        event = client_mod.event_from_hook_payload(
            skill_payload("commit", plugin="toolkit")
        )

        assert event["event"] == "invocation"
        assert event["skill"] == "commit"

    def test_bare_colliding_name_is_not_captured(self, colliding_skill_names):
        """`commit` and `ship` are both registry names and personal commands."""
        for name in ("commit", "ship"):
            assert (
                client_mod.event_from_hook_payload(skill_payload(name, plugin=None))
                is None
            )

    def test_foreign_prefix_is_not_captured(self, colliding_skill_names):
        for plugin, name in (
            ("superpowers", "brainstorming"),
            ("obsidian", "obsidian-markdown"),
            ("someplugin", "commit"),
        ):
            assert (
                client_mod.event_from_hook_payload(skill_payload(name, plugin=plugin))
                is None
            )

    def test_agora_prefixed_agent_dispatch_is_captured(self, colliding_skill_names):
        for name in ("devils-advocate", "audience-checker"):
            event = client_mod.event_from_hook_payload(
                subagent_hook_payload("Agent", f"verify:{name}")
            )

            assert event["event"] == "subagent"
            assert event["skill"] == name

    def test_bare_subagent_type_is_not_captured(self, colliding_skill_names):
        for name in ("general-purpose", "Explore", "fork"):
            assert (
                client_mod.event_from_hook_payload(subagent_hook_payload("Agent", name))
                is None
            )

    def test_personal_wrapper_does_not_suppress_the_agents_it_dispatches(
        self, colliding_skill_names
    ):
        """Capture decides per invocation, never per session: a personal
        command that dispatches Agora agents is itself bare and dropped, while
        the prefixed dispatches it makes stay attributable."""
        assert (
            client_mod.event_from_hook_payload(
                skill_payload("critical-eval", plugin=None)
            )
            is None
        )
        dispatched = [
            client_mod.event_from_hook_payload(
                subagent_hook_payload("Agent", f"verify:{name}")
            )
            for name in ("devils-advocate", "audience-checker")
        ]

        assert [e["skill"] for e in dispatched] == [
            "devils-advocate",
            "audience-checker",
        ]


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

    def test_skill_names_manifest_matches_registry(self, registry_skill_names):
        manifest = CLIENT_SCRIPT.parent / client_mod.SKILL_NAMES_FILE
        assert manifest.exists(), "run scripts/generate-registry.py"
        names = set(json.loads(manifest.read_text())["names"])
        assert names == registry_skill_names

    def test_plugin_names_manifest_matches_marketplace(self):
        manifest = CLIENT_SCRIPT.parent / client_mod.PLUGIN_NAMES_FILE
        assert manifest.exists(), "run scripts/generate-registry.py"
        names = set(json.loads(manifest.read_text())["names"])
        marketplace = json.loads(
            (REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text()
        )
        assert names == {p["name"] for p in marketplace["plugins"]}

    def test_plugin_cache_layout_filters_unknown_skills(
        self, tmp_path, registry_skill_names
    ):
        """The layout that leaked: no registry resolves above the script."""
        installed = install_client_in_cache_layout(tmp_path / "claude")
        home = tmp_path / "agora"
        run_client(["enable"], home, script=installed)

        run_client(
            ["capture"],
            home,
            stdin_data=skill_hook_payload("critical-eval"),
            script=installed,
        )
        assert not (home / "spool" / "events.jsonl").exists()

        skill = sorted(registry_skill_names)[0]
        run_client(
            ["capture"], home, stdin_data=skill_hook_payload(skill), script=installed
        )
        events = (home / "spool" / "events.jsonl").read_text().strip().splitlines()
        assert [json.loads(e)["skill"] for e in events] == [skill]

    def test_plugin_cache_layout_reaches_sibling_marketplace_registry(self, tmp_path):
        claude = tmp_path / "claude"
        installed = install_client_in_cache_layout(claude, ship_manifest=False)
        checkout = claude / "plugins" / "marketplaces" / "research-agora"
        (checkout / "registry").mkdir(parents=True)
        (checkout / "registry" / "index.json").write_text(
            json.dumps({"repos": [{"skills": [{"name": "only-known-skill"}]}]})
        )
        (checkout / ".claude-plugin").mkdir()
        (checkout / ".claude-plugin" / "marketplace.json").write_text(
            json.dumps({"plugins": [{"name": "only-known-plugin"}]})
        )
        home = tmp_path / "agora"
        run_client(["enable"], home, script=installed)

        run_client(
            ["capture"],
            home,
            stdin_data=skill_hook_payload(
                "only-known-skill", plugin="only-known-plugin"
            ),
            script=installed,
        )
        events = (home / "spool" / "events.jsonl").read_text().strip().splitlines()
        assert json.loads(events[0])["skill"] == "only-known-skill"

    def test_plugin_cache_layout_applies_the_provenance_rule(self, tmp_path):
        """Prefix, bare, and foreign names resolve the same in every layout."""
        installed = install_client_in_cache_layout(tmp_path / "claude")
        home = tmp_path / "agora"
        run_client(["enable"], home, script=installed)

        for payload in (
            skill_hook_payload("code-simplify", plugin="toolkit"),
            skill_hook_payload("code-simplify", plugin=None),
            skill_hook_payload("code-simplify", plugin="someplugin"),
            skill_hook_payload("brainstorming", plugin="superpowers"),
            json.dumps(
                subagent_hook_payload("Agent", "verify:devils-advocate")
            ),
            json.dumps(subagent_hook_payload("Agent", "general-purpose")),
        ):
            run_client(["capture"], home, stdin_data=payload, script=installed)

        events = (home / "spool" / "events.jsonl").read_text().strip().splitlines()
        assert [json.loads(e)["skill"] for e in events] == [
            "code-simplify",
            "devils-advocate",
        ]

    def test_fails_closed_without_any_skill_list(self, tmp_path, registry_skill_names):
        """No name list means record nothing — never record everything."""
        installed = install_client_in_cache_layout(
            tmp_path / "claude", ship_manifest=False
        )
        home = tmp_path / "agora"
        run_client(["enable"], home, script=installed)
        run_client(
            ["capture"],
            home,
            stdin_data=skill_hook_payload(sorted(registry_skill_names)[0]),
            script=installed,
        )
        assert not (home / "spool" / "events.jsonl").exists()

    def test_fails_closed_without_a_plugin_name_list(
        self, tmp_path, registry_skill_names
    ):
        """Known skill names alone cannot attribute an invocation."""
        installed = install_client_in_cache_layout(
            tmp_path / "claude", ship_plugin_manifest=False
        )
        home = tmp_path / "agora"
        run_client(["enable"], home, script=installed)
        run_client(
            ["capture"],
            home,
            stdin_data=skill_hook_payload(sorted(registry_skill_names)[0]),
            script=installed,
        )
        assert not (home / "spool" / "events.jsonl").exists()

    def test_purge_unknown_skills_keeps_the_rest(self, tmp_path, registry_skill_names):
        skill = sorted(registry_skill_names)[0]
        run_client(["enable"], tmp_path)
        run_client(["capture"], tmp_path, stdin_data=skill_hook_payload(skill))
        spool = tmp_path / "spool" / "events.jsonl"
        with open(spool, "a") as f:
            for name in ("critical-eval", "brainstorming"):
                f.write(
                    json.dumps(
                        {
                            "event": "invocation",
                            "session": "deadbeef",
                            "skill": name,
                            "outcome": "success",
                            "ts": "2026-08-01T09:00:00",
                        }
                    )
                    + "\n"
                )
            f.write(
                json.dumps(
                    {
                        "event": "session_end",
                        "session": "deadbeef",
                        "ts": "2026-08-01T09:30:00",
                    }
                )
                + "\n"
            )

        result = run_client(["purge", "--unknown-skills"], tmp_path)
        assert result.returncode == 0
        assert "critical-eval" in result.stdout and "brainstorming" in result.stdout
        events = [json.loads(line) for line in spool.read_text().splitlines()]
        assert [e.get("skill") for e in events] == [skill, None]

    def test_purge_unknown_skills_refuses_without_a_name_list(self, tmp_path):
        installed = install_client_in_cache_layout(
            tmp_path / "claude", ship_manifest=False
        )
        home = tmp_path / "agora"
        run_client(["enable"], home, script=installed)
        result = run_client(["purge", "--unknown-skills"], home, script=installed)
        assert result.returncode == 1
        assert "refusing to purge" in result.stdout

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
        # Enough installations to clear the k-anonymity floor, so the run's
        # survival is visible in the published skills and not masked by §11.
        good = make_reports(known, aggregate_mod.MIN_INSTALLATIONS_PUBLISH)
        input_dir = tmp_path / "reports"
        input_dir.mkdir()
        (input_dir / "hostile.json").write_text(json.dumps(hostile))
        for i, report in enumerate(good):
            (input_dir / f"good-{i}.json").write_text(json.dumps(report))
        (input_dir / "not-even-json.json").write_text("}{")
        output = tmp_path / "feedback.json"

        rc = aggregate_mod.main(
            ["--input-dir", str(input_dir), "--output", str(output)]
        )
        assert rc == 0
        result = json.loads(output.read_text())
        assert result["stats"]["reports"] == len(good)  # only the good ones survive
        assert known in result["skills"]
