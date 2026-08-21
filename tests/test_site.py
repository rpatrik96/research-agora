"""Behavioral tests for the generated skill index."""

import importlib.util
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent


def _site_module():
    spec = importlib.util.spec_from_file_location(
        "generate_site", REPO_ROOT / "scripts" / "generate-site.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _IndexParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.band_titles: list[str | None] = []
        self.card_count = 0
        self.verification_badges: list[dict[str, str]] = []
        self._verification_badge: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())
        if tag == "h3" and "band-label" in classes:
            self.band_titles.append(attributes.get("title"))
        if tag == "article" and "skill-card" in classes:
            self.card_count += 1
        if tag == "span" and classes & {
            "badge-formal",
            "badge-heuristic",
            "badge-layered",
            "badge-none",
        }:
            self._verification_badge = {"title": attributes.get("title") or ""}

    def handle_data(self, data: str) -> None:
        if self._verification_badge is not None:
            self._verification_badge["level"] = data.strip()

    def handle_endtag(self, tag: str) -> None:
        if tag == "span" and self._verification_badge is not None:
            self.verification_badges.append(self._verification_badge)
            self._verification_badge = None


@pytest.fixture(scope="module")
def registry_skills() -> list:
    """Every skill in the registry, deprecated ones included."""
    import json

    index_path = REPO_ROOT / "registry" / "index.json"
    if not index_path.exists():
        pytest.skip("registry/index.json not found — run scripts/generate-registry.py first")
    data = json.loads(index_path.read_text())
    return [s for repo in data["repos"] for s in repo["skills"]]


@pytest.fixture(scope="module")
def generated_index() -> str:
    pytest.importorskip("jinja2")
    proc = subprocess.run(
        [sys.executable, "scripts/generate-site.py"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, (
        f"generate-site.py failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}"
    )
    return (REPO_ROOT / "site" / "output" / "index.html").read_text()


# `onboard` runs onboard.py and verifies nothing. It is the case that separates
# "invokes a program" from "checks the result", and the band label used to
# collapse the two: it read "Runs a tool and checks against its output".
CLAIMS_VERIFICATION = ("check", "verif", "ground truth", "validat", "confirm")


def test_no_band_label_claims_verification() -> None:
    module = _site_module()
    overclaiming = [
        label
        for _, label, _ in module.VERIFICATION_BANDS
        if any(word in label.lower() for word in CLAIMS_VERIFICATION)
    ]
    assert not overclaiming, (
        f"Band labels claiming verification: {overclaiming}. The band answers "
        "whether a program runs; the per-skill badge carries the claim."
    )


def test_every_band_carries_a_tooltip() -> None:
    module = _site_module()
    missing = [bid for bid, _, tooltip in module.VERIFICATION_BANDS if not tooltip]
    assert not missing, f"Bands with no tooltip: {missing}"


def test_unverified_tool_skills_are_not_labelled_as_checked(
    registry_skills: list,
) -> None:
    """A skill that runs a program but verifies nothing must not read as checked."""
    module = _site_module()
    labels = {bid: label for bid, label, _ in module.VERIFICATION_BANDS}
    unverified_tool_skills = [
        s
        for s in registry_skills
        if s.get("verification-level") == "none" and module.skill_band(s) == "runs-a-tool"
    ]
    assert unverified_tool_skills, "Expected onboard and kin in this class"
    for skill in unverified_tool_skills:
        label = labels["runs-a-tool"].lower()
        assert not any(word in label for word in CLAIMS_VERIFICATION), (
            f"'{skill['name']}' is verification-level none but sits under "
            f"'{labels['runs-a-tool']}'"
        )
        assert "not verified" in module.verification_tooltip(
            skill["verification-level"]
        ).lower()


def test_verification_tooltips_cover_the_hierarchy_and_unknown_levels() -> None:
    module = _site_module()
    tooltip = getattr(module, "verification_tooltip", None)
    assert tooltip is not None, "generate-site.py must expose verification_tooltip"
    expected = {
        "formal": "Formal — checked automatically against ground truth (DOI resolution, unit tests, tool output).",
        "heuristic": "Heuristic — rule-based check (compilation, counts, grep). Catches classes of error, not correctness.",
        "layered": "Layered — automated checks plus a review step you have to complete.",
        "none": "Not verified — the output is yours to check. The skill may still run a program.",
        "unknown": "Not verified — the output is yours to check. The skill may still run a program.",
    }
    assert {level: tooltip(level) for level in expected} == expected


def test_generated_index_uses_tooltips_instead_of_repeated_band_blurbs(
    generated_index: str,
) -> None:
    parser = _IndexParser()
    parser.feed(generated_index)

    assert "band-blurb" not in generated_index
    assert "checks against its output" not in generated_index
    assert parser.band_titles and all(parser.band_titles)

    module = _site_module()
    assert len(parser.verification_badges) == parser.card_count
    assert all(
        badge["title"] == module.verification_tooltip(badge["level"])
        for badge in parser.verification_badges
    )


def test_filtering_hides_empty_bands_and_updates_group_count(tmp_path: Path) -> None:
    if shutil.which("node") is None:
        pytest.skip("node not available")
    harness = tmp_path / "filter-harness.js"
    search_js = REPO_ROOT / "site" / "static" / "search.js"
    harness.write_text(
        """
const fs = require('fs');
const vm = require('vm');

class ClassList {
    constructor() { this.values = new Set(); }
    add(value) { this.values.add(value); }
    remove(value) { this.values.delete(value); }
    contains(value) { return this.values.has(value); }
    toggle(value, force) {
        if (force === undefined) force = !this.values.has(value);
        if (force) this.values.add(value); else this.values.delete(value);
    }
}

function control(extra = {}) {
    return Object.assign({
        value: '', checked: false, dataset: {}, classList: new ClassList(),
        textContent: '', listeners: {},
        addEventListener(event, callback) { this.listeners[event] = callback; },
        querySelectorAll() { return []; },
        querySelector() { return null; },
    }, extra);
}

const alpha = control({dataset: {name: 'alpha', description: '', plugin: 'write', taskType: 'draft', verification: 'formal'}});
const beta = control({dataset: {name: 'beta', description: '', plugin: 'write', taskType: 'draft', verification: 'none'}});
const alphaBand = control({
    querySelector(selector) { return selector === '.skill-card:not(.hidden)' && !alpha.classList.contains('hidden') ? alpha : null; },
});
const betaBand = control({
    querySelector(selector) { return selector === '.skill-card:not(.hidden)' && !beta.classList.contains('hidden') ? beta : null; },
});
const groupCount = control({textContent: '2'});
const group = control({
    dataset: {group: 'write'},
    querySelectorAll(selector) {
        if (selector === '.skill-card') return [alpha, beta];
        if (selector === '.band-section') return [alphaBand, betaBand];
        return [];
    },
    querySelector(selector) { return selector === '.group-count' ? groupCount : null; },
});
const search = control();
const content = control({
    querySelectorAll(selector) { return selector === '.skill-group .skill-card' ? [alpha, beta] : []; },
});
const elements = {
    search,
    'skills-content': content,
    'results-count': control(),
    'reset-filters': control(),
    'show-internal': control(),
    'internal-section': control(),
};
const document = {
    getElementById(id) { return elements[id]; },
    querySelectorAll(selector) {
        if (selector === '.skill-group') return [group];
        return [];
    },
    querySelector() { return null; },
    addEventListener() {},
};

vm.runInNewContext(fs.readFileSync(process.argv[2], 'utf8'), {document});
search.value = 'alpha';
search.listeners.input();
if (alphaBand.classList.contains('hidden')) throw new Error('matching band was hidden');
if (!betaBand.classList.contains('hidden')) throw new Error('empty band stayed visible');
if (String(groupCount.textContent) !== '1') throw new Error('group count did not update to 1');

search.value = 'missing';
search.listeners.input();
if (!alphaBand.classList.contains('hidden') || !betaBand.classList.contains('hidden')) throw new Error('empty bands stayed visible');
if (!group.classList.contains('hidden')) throw new Error('empty group stayed visible');
if (String(groupCount.textContent) !== '0') throw new Error('group count did not update to 0');
"""
    )
    proc = subprocess.run(
        ["node", str(harness), str(search_js)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
