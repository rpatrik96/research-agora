#!/usr/bin/env python3
"""
Generate static site from registry/index.json.

Reads the registry index and categories, renders Jinja2 templates,
and outputs a static site to site/output/.
"""

import json
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

# Skill → Group mapping (centralized, not in frontmatter)
SKILL_GROUP_MAP = {
    # Paper Drafting
    "paper-abstract": "paper-drafting",
    "paper-introduction": "paper-drafting",
    "paper-discussion": "paper-drafting",
    "paper-experiments": "paper-drafting",
    "paper-title": "paper-drafting",

    # Quality & Verification
    "paper-review": "quality-verification",
    "paper-references": "quality-verification",
    "paper-verify-experiments": "quality-verification",
    "claim-auditor": "quality-verification",
    "evidence-checker": "quality-verification",
    "statistical-validator": "quality-verification",

    # Theory Tools
    "proof-auditor": "theory-tools",
    "bounds-analyst": "theory-tools",
    "counterexample-searcher": "theory-tools",
    "intuition-formalizer": "theory-tools",
    "notation-consistency-checker": "theory-tools",
    "proof-strategy-advisor": "theory-tools",
    "theorem-dependency-mapper": "theory-tools",
    "theory-connector": "theory-tools",

    # Literature & Discovery
    "literature-synthesizer": "literature-discovery",
    "benchmark-scout": "literature-discovery",
    "experiment-tracker": "literature-discovery",
    "perspective-synthesizer": "literature-discovery",
    "devils-advocate": "literature-discovery",

    # Writing Polish
    "clarity-optimizer": "writing-polish",
    "latex-debugger": "writing-polish",
    "latex-consistency": "writing-polish",
    "latex-sync-annotate": "writing-polish",
    "latex-sync-setup": "writing-polish",
    "latex-sync-verify": "writing-polish",
    "audience-checker": "writing-polish",

    # Dissemination
    "paper-poster": "dissemination",
    "paper-slides": "dissemination",
    "paper-twitter": "dissemination",
    "science-gif": "dissemination",
    "figure-storyteller": "dissemination",
    "discussion-monitor": "dissemination",

    # Submission & Rebuttal
    "paper-rebuttal": "submission-rebuttal",
    "reviewer-response-generator": "submission-rebuttal",
    "openreview-submission": "submission-rebuttal",
    "co-author-sync": "submission-rebuttal",
    "artifact-packager": "submission-rebuttal",

    # Development & Automation
    "commit": "development",
    "code-simplify": "development",
    "pr-automation": "development",
    "python-docs": "development",
    "python-cicd": "development",
    "htcondor": "development",

    # Documents & Figures
    "pptx-create": "documents-figures",
    "docx-create": "documents-figures",
    "xlsx-create": "documents-figures",
    "publication-figures": "documents-figures",
    "tikz-figures": "documents-figures",
}

# Display order for groups
GROUP_ORDER = [
    "paper-drafting",
    "quality-verification",
    "theory-tools",
    "literature-discovery",
    "writing-polish",
    "dissemination",
    "submission-rebuttal",
    "development",
    "documents-figures",
]


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

    # Assign skills to groups
    ungrouped = []
    for skill in skills:
        group_id = SKILL_GROUP_MAP.get(skill["name"])
        if group_id and group_id in grouped:
            grouped[group_id]["skills"].append(skill)
        else:
            ungrouped.append(skill)

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

    # Collect all skills from all repos
    all_skills = []
    for repo in registry.get("repos", []):
        repo_url = f"https://github.com/{repo['repo']}"
        for skill in repo.get("skills", []):
            skill["repo_url"] = repo_url
            skill["source_url"] = f"{repo_url}/blob/main/{skill.get('path', '')}"
            all_skills.append(skill)

    # Split by visibility
    public_skills = [s for s in all_skills if s.get("visibility", "public") == "public"]
    internal_skills = [s for s in all_skills if s.get("visibility", "public") == "internal"]

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

    # Build stats for display
    public_stats = {
        "public_skills": len(public_skills),
        "internal_skills": len(internal_skills),
        "total_skills": len(all_skills),
        "groups": len(grouped_skills),
        "plugins": len(plugins),
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

    # Load benchmarks
    benchmarks_path = REGISTRY_DIR / "benchmarks.json"
    results_path = REGISTRY_DIR / "results.json"

    benchmarks = []
    all_results = []

    if benchmarks_path.exists():
        with open(benchmarks_path) as f:
            benchmarks_data = json.load(f)
        benchmarks = benchmarks_data.get("benchmarks", [])

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
    print(f"  Open {OUTPUT_DIR / 'index.html'} to preview")


if __name__ == "__main__":
    main()
