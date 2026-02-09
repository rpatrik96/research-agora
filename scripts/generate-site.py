#!/usr/bin/env python3
"""
Generate static site from registry/index.json.

Reads the registry index and categories, renders Jinja2 templates,
and outputs a static site to site/output/.
"""

import json
import shutil
import sys
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("Error: jinja2 required. Install with: pip install jinja2")
    sys.exit(1)

REPO_ROOT = Path(__file__).parent.parent
REGISTRY_DIR = REPO_ROOT / "registry"
SITE_DIR = REPO_ROOT / "site"
TEMPLATE_DIR = SITE_DIR / "templates"
STATIC_DIR = SITE_DIR / "static"
OUTPUT_DIR = SITE_DIR / "output"


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


def main():
    print("Generating static site...")

    registry = load_registry()
    categories = load_categories()

    # Collect all skills from all repos
    all_skills = []
    for repo in registry.get("repos", []):
        repo_url = f"https://github.com/{repo['repo']}"
        for skill in repo.get("skills", []):
            skill["repo_url"] = repo_url
            skill["source_url"] = f"{repo_url}/blob/main/{skill.get('path', '')}"
            all_skills.append(skill)

    # Collect unique values for filters
    plugins = _unique_sorted(all_skills, "plugin")
    types = _unique_sorted(all_skills, "type")
    domains = _unique_sorted(all_skills, "research-domain")
    task_types = _unique_sorted(all_skills, "task-type")
    phases = _unique_sorted(all_skills, "research-phase")
    verification_levels = _unique_sorted(all_skills, "verification-level")

    # Setup Jinja2
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=True,
    )
    env.filters["verification_badge"] = verification_badge_class
    env.filters["model_badge"] = model_badge_class

    # Render index page
    template = env.get_template("index.html.j2")
    html = template.render(
        skills=all_skills,
        stats=registry.get("stats", {}),
        plugins=plugins,
        types=types,
        domains=domains,
        task_types=task_types,
        phases=phases,
        verification_levels=verification_levels,
        categories=categories,
        generated=registry.get("generated", ""),
    )

    # Write output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "index.html").write_text(html)

    # Copy static files
    if STATIC_DIR.exists():
        for static_file in STATIC_DIR.iterdir():
            if static_file.is_file():
                shutil.copy2(static_file, OUTPUT_DIR / static_file.name)

    print(f"Site generated at {OUTPUT_DIR.relative_to(REPO_ROOT)}/")
    print(f"  {len(all_skills)} skills indexed")
    print(f"  Open {OUTPUT_DIR / 'index.html'} to preview")


if __name__ == "__main__":
    main()
