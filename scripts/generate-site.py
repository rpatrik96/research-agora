#!/usr/bin/env python3
"""
Generate static site from registry/index.json.

Reads the registry index and categories, renders Jinja2 templates,
and outputs a static site to site/output/.
"""

import json
import re
import shutil
import sys
from collections import OrderedDict
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    Environment = None
    FileSystemLoader = None

REPO_ROOT = Path(__file__).parent.parent
REGISTRY_DIR = REPO_ROOT / "registry"
SITE_DIR = REPO_ROOT / "site"
TEMPLATE_DIR = SITE_DIR / "templates"
STATIC_DIR = SITE_DIR / "static"
OUTPUT_DIR = SITE_DIR / "output"

# Groups derive from plugin membership (RFC-0002). There is no hand-maintained
# skill→group table any more, so a retired skill cannot leave a mapping entry
# behind — the failure that left 34 dangling references after the February 2026
# consolidation and that test_no_orphan_group_map_entries had to guard against.
# Community feedback badges render only at or above this many unique
# installations (k-anonymity floor, RFC-0001 §11).
FEEDBACK_MIN_INSTALLATIONS = 3

# The four plugins, in the order a researcher meets them.
GROUP_ORDER = [
    "discover",
    "write",
    "verify",
    "toolkit",
]


def skill_group(skill: dict) -> str:
    """A skill's browse group is its plugin."""
    return skill["plugin"]


# Within a group, skills sort into bands by what they actually run — taken from
# the `tools` the registry detected at invocation sites, not from self-declared
# metadata. Deriving this from `verification-level` put `intuition-formalizer`
# under "checks against ground truth" because it was `layered`; the band now
# answers a question with a checkable answer: does this skill invoke anything?
VERIFICATION_BANDS = [
    (
        "runs-a-tool",
        "Runs a tool and checks against its output",
        "Invokes a real program and compares against what it returns.",
    ),
    (
        "reads-sources",
        "Reads your files and reports",
        "Extracts from your own source with a script. No external tool.",
    ),
    (
        "judges",
        "Reads your work and judges it",
        "Applies a stated standard. Nothing is executed — you are the oracle.",
    ),
]

_SCRIPT_FENCE = re.compile(r"```(?:bash|sh|shell|console|python)\n(.*?)```", re.S)
_SCRIPT_CMD = re.compile(r"\b(grep|rg|awk|sed|find|jq)\b")


def skill_band(skill: dict) -> str:
    """Return the band id from what the skill invokes."""
    if skill.get("tools"):
        return "runs-a-tool"
    path = REPO_ROOT / skill.get("path", "")
    if path.exists():
        body = path.read_text()
        if any(_SCRIPT_CMD.search(b) for b in _SCRIPT_FENCE.findall(body)):
            return "reads-sources"
    return "judges"


def load_registry() -> dict:
    """Load registry/index.json."""
    index_path = REGISTRY_DIR / "index.json"
    if not index_path.exists():
        print("Error: registry/index.json not found. Run scripts/generate-registry.py first.")
        sys.exit(1)
    with open(index_path) as f:
        return json.load(f)


def load_categories() -> dict:
    """Load registry/categories.json."""
    cat_path = REGISTRY_DIR / "categories.json"
    if not cat_path.exists():
        print("Error: registry/categories.json not found.")
        sys.exit(1)
    with open(cat_path) as f:
        return json.load(f)


def load_feedback() -> dict:
    """Load registry/feedback.json (RFC-0001); empty aggregate if absent."""
    feedback_path = REGISTRY_DIR / "feedback.json"
    if not feedback_path.exists():
        return {"stats": {}, "skills": {}}
    with open(feedback_path) as f:
        return json.load(f)


def verification_badge_class(level: str) -> str:
    """Return CSS class for verification level badge."""
    return {
        "formal": "badge-formal",
        "heuristic": "badge-heuristic",
        "layered": "badge-layered",
        "none": "badge-none",
    }.get(level, "badge-none")


def model_badge_class(model: str) -> str:
    """Return CSS class for model badge."""
    return {
        "opus": "badge-opus",
        "sonnet": "badge-sonnet",
        "haiku": "badge-haiku",
    }.get(model, "badge-sonnet")


def _unique_sorted(skills: list, key: str) -> list:
    """Extract sorted unique values for a metadata key from skills list."""
    return sorted(set(s.get(key, "") for s in skills if s.get(key)))


def group_skills(skills: list, groups_meta: dict) -> OrderedDict:
    """Group skills by their assigned group, respecting GROUP_ORDER."""
    grouped = OrderedDict()

    for group_id in GROUP_ORDER:
        meta = groups_meta.get(group_id, {})
        grouped[group_id] = {
            "label": meta.get("label", group_id),
            "description": meta.get("description", ""),
            "icon": meta.get("icon", ""),
            "skills": [],
        }

    # Assign skills to groups by plugin, then band them within the group.
    ungrouped = []
    for skill in skills:
        group_id = skill_group(skill)
        if group_id in grouped:
            grouped[group_id]["skills"].append(skill)
        else:
            ungrouped.append(skill)

    band_order = {b[0]: i for i, b in enumerate(VERIFICATION_BANDS)}
    for group in grouped.values():
        group["skills"].sort(
            key=lambda s: (band_order.get(skill_band(s), 99), s["name"])
        )
        group["bands"] = [
            {
                "id": bid,
                "label": label,
                "blurb": blurb,
                "skills": [s for s in group["skills"] if skill_band(s) == bid],
            }
            for bid, label, blurb in VERIFICATION_BANDS
        ]
        group["bands"] = [b for b in group["bands"] if b["skills"]]

    # Remove empty groups
    grouped = OrderedDict(
        (k, v) for k, v in grouped.items() if v["skills"]
    )

    # Add ungrouped skills if any
    if ungrouped:
        grouped["other"] = {
            "label": "Other",
            "description": "Additional skills",
            "icon": "puzzle",
            "skills": ungrouped,
        }

    return grouped


def main():
    if Environment is None:
        print("Error: jinja2 required. Install with: pip install jinja2")
        sys.exit(1)

    print("Generating static site...")

    registry = load_registry()
    categories = load_categories()
    groups_meta = categories.get("groups", {})
    feedback = load_feedback()
    feedback_skills = feedback.get("skills", {})

    # Collect all skills from all repos
    all_skills = []
    for repo in registry.get("repos", []):
        repo_url = f"https://github.com/{repo['repo']}"
        for skill in repo.get("skills", []):
            skill["repo_url"] = repo_url
            skill["source_url"] = f"{repo_url}/blob/main/{skill.get('path', '')}"
            fb = feedback_skills.get(skill["name"])
            if fb and fb.get("unique_installations", 0) >= FEEDBACK_MIN_INSTALLATIONS:
                skill["feedback"] = {
                    "score": round(fb.get("wilson_lb", 0.0) * 100),
                    "installations": fb["unique_installations"],
                    "status": fb.get("status", "active"),
                }
            all_skills.append(skill)

    # Split by visibility. A deprecated skill still works for anyone who has it
    # installed, but the site is where people go to pick something to start
    # with -- so it is not listed at all. The CHANGELOG's Deprecated section
    # and /whats-new are what reach the people who already run it.
    live_skills = [s for s in all_skills if not s.get("deprecated")]
    public_skills = [s for s in live_skills if s.get("visibility", "public") == "public"]
    internal_skills = [s for s in live_skills if s.get("visibility", "public") == "internal"]
    deprecated_count = len(all_skills) - len(live_skills)

    # Group public skills
    grouped_skills = group_skills(public_skills, groups_meta)

    # Collect unique values for filters (from public skills only)
    plugins = _unique_sorted(public_skills, "plugin")
    task_types = _unique_sorted(public_skills, "task-type")
    verification_levels = _unique_sorted(public_skills, "verification-level")

    # Setup Jinja2
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=True,
    )
    env.filters["verification_badge"] = verification_badge_class
    env.filters["model_badge"] = model_badge_class

    # Load benchmarks early so count is available for stats
    benchmarks_path = REGISTRY_DIR / "benchmarks.json"
    benchmarks = []
    if benchmarks_path.exists():
        with open(benchmarks_path) as f:
            benchmarks_data = json.load(f)
        benchmarks = benchmarks_data.get("benchmarks", [])

    # Build stats for display
    public_stats = {
        # public_skills is already deprecation-filtered here (see live_skills
        # above); active_public_skills is the same number under the name the
        # registry and the docs use, so the site and the badge cannot disagree.
        "public_skills": len(public_skills),
        "active_public_skills": len(public_skills),
        "internal_skills": len(internal_skills),
        "total_skills": len(all_skills),
        "deprecated_skills": deprecated_count,
        "groups": len(grouped_skills),
        "plugins": len(plugins),
        "benchmarks": len(benchmarks),
        "feedback_reports": feedback.get("stats", {}).get("reports", 0),
    }

    # Render index page
    template = env.get_template("index.html.j2")
    html = template.render(
        grouped_skills=grouped_skills,
        internal_skills=internal_skills,
        all_skills=all_skills,
        stats=public_stats,
        plugins=plugins,
        task_types=task_types,
        verification_levels=verification_levels,
        categories=categories,
        groups_meta=groups_meta,
        generated=registry.get("generated", ""),
    )

    # Write output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "index.html").write_text(html)

    # Load results (benchmarks already loaded above for stats)
    results_path = REGISTRY_DIR / "results.json"
    all_results = []

    if results_path.exists():
        with open(results_path) as f:
            results_data = json.load(f)
        for r in results_data.get("results", []):
            all_results.extend(r.get("entries", []))

    # Render benchmarks page
    try:
        bench_template = env.get_template("benchmarks.html.j2")
        bench_html = bench_template.render(
            benchmarks=benchmarks,
            results=all_results,
            generated=registry.get("generated", ""),
        )
        (OUTPUT_DIR / "benchmarks.html").write_text(bench_html)
        print(f"  {len(benchmarks)} benchmarks indexed")
    except Exception as e:
        print(f"  Warning: Could not generate benchmarks page: {e}")

    # Render docs page
    try:
        docs_template = env.get_template("docs.html.j2")
        docs_html = docs_template.render(
            generated=registry.get("generated", ""),
        )
        (OUTPUT_DIR / "docs.html").write_text(docs_html)
        print("  Documentation page generated")
    except Exception as e:
        print(f"  Warning: Could not generate docs page: {e}")

    # Copy static files
    if STATIC_DIR.exists():
        for static_file in STATIC_DIR.iterdir():
            if static_file.is_file():
                shutil.copy2(static_file, OUTPUT_DIR / static_file.name)

    print(f"Site generated at {OUTPUT_DIR.relative_to(REPO_ROOT)}/")
    print(f"  {len(public_skills)} public skills in {len(grouped_skills)} groups")
    print(f"  {len(internal_skills)} internal skills (hidden by default)")
    if deprecated_count:
        print(f"  {deprecated_count} deprecated skills (not listed)")
    print(f"  Open {OUTPUT_DIR / 'index.html'} to preview")


if __name__ == "__main__":
    main()
