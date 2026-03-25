"""Scenario: PhD student's first encounter with Research Agora.

Maya is a 2nd-year PhD student who heard about Research Agora from a labmate.
She wants to install it and find a skill to help write her paper abstract.

Tests: onboarding banner, quickstart link, try-this sections, install command.
"""

from __future__ import annotations

import pytest

from synthetic.scenarios.test_marketplace_browse import run_persona_journey


@pytest.mark.synthetic
def test_student_onboarding_path(
    browser_page, claude_client, student_persona, site_server
):
    """Maya follows the quickstart path from landing to first skill."""
    action_history, pages_visited, _, evaluation = run_persona_journey(
        browser_page, claude_client, student_persona, site_server
    )

    assert len(action_history) >= 1, (
        f"Student only took {len(action_history)} actions"
    )
    assert evaluation.findability_score >= 3, (
        f"Findability {evaluation.findability_score}/5 too low for a student. "
        f"Assessment: {evaluation.overall_assessment}"
    )


@pytest.mark.synthetic
def test_onboarding_banner_visible(browser_page, site_server):
    """The onboarding banner should be immediately visible to new visitors."""
    browser_page.goto(f"{site_server}/index.html", timeout=10000)
    browser_page.wait_for_load_state("domcontentloaded")

    page_text = browser_page.text_content("body")
    has_quickstart_link = "quickstart" in (page_text or "").lower()
    assert has_quickstart_link, (
        "Landing page should contain a visible link/reference to quickstart"
    )


@pytest.mark.synthetic
def test_quickstart_page_accessible(browser_page, site_server):
    """Quickstart page should load and contain setup instructions."""
    browser_page.goto(f"{site_server}/quickstart.html", timeout=10000)
    browser_page.wait_for_load_state("domcontentloaded")

    title = browser_page.title()
    assert title, "Quickstart page should have a title"

    page_text = browser_page.text_content("body")
    assert page_text and "install" in page_text.lower(), (
        "Quickstart page should contain installation instructions"
    )
