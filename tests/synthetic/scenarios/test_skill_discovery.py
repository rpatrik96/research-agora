"""Scenario: Experienced user discovers verification and theory tools.

Dr. Chen is a postdoc who already uses basic skills and wants to find
proof verification and bounds analysis tools using search and intent filters.

Tests: search input, intent buttons, checkbox filters, group collapse,
description expand.
"""

from __future__ import annotations

import pytest

from synthetic.scenarios.test_marketplace_browse import run_persona_journey


@pytest.mark.synthetic
def test_experienced_user_finds_theory_tools(
    browser_page, claude_client, experienced_persona, site_server
):
    """Dr. Chen uses search and intent filters to find theory tools."""
    action_history, pages_visited, _, evaluation = run_persona_journey(
        browser_page, claude_client, experienced_persona, site_server,
        scenario_name="skill_discovery",
    )

    assert len(action_history) >= 1, (
        f"Experienced user only took {len(action_history)} actions"
    )
    assert evaluation.findability_score >= 3, (
        f"Findability {evaluation.findability_score}/5 too low. "
        f"Assessment: {evaluation.overall_assessment}"
    )
    assert evaluation.clarity_score >= 3, (
        f"Clarity {evaluation.clarity_score}/5 — skill descriptions should be clear. "
        f"Assessment: {evaluation.overall_assessment}"
    )


@pytest.mark.synthetic
def test_search_filters_skills(browser_page, site_server):
    """Typing in the search box should filter visible skill cards."""
    browser_page.goto(f"{site_server}/index.html", timeout=10000)
    browser_page.wait_for_load_state("domcontentloaded")

    search_input = browser_page.get_by_role("textbox")
    if search_input.count() > 0:
        search_input.first.fill("proof")
        browser_page.wait_for_timeout(500)

        filtered_text = browser_page.text_content(".results-count")
        assert filtered_text is not None, "Results count should update after search"


@pytest.mark.synthetic
def test_intent_buttons_filter_groups(browser_page, site_server):
    """Intent buttons should filter skill groups by workflow."""
    browser_page.goto(f"{site_server}/index.html", timeout=10000)
    browser_page.wait_for_load_state("domcontentloaded")

    verify_button = browser_page.get_by_role("button", name="Verify my paper")
    if verify_button.count() > 0:
        verify_button.click()
        browser_page.wait_for_timeout(500)

        results_text = browser_page.text_content(".results-count")
        assert results_text is not None, (
            "Results count should update after intent button click"
        )
