"""Scenario: PI navigates documentation via pathway cards.

Prof. Stein uses the docs page pathway cards (PI, Researcher, Student)
to find the verification policy documentation.

Tests: pathway card visibility, routing to correct pages, doc nav tabs.
"""

from __future__ import annotations

import pytest

from synthetic.accessibility import extract_a11y_tree
from synthetic.actions import execute_action
from synthetic.claude_client import evaluate_journey, get_next_action


@pytest.mark.synthetic
def test_pathway_cards_route_correctly(
    browser_page, claude_client, pi_persona, site_server
):
    """PI clicks the PI pathway card and reaches verification page."""
    browser_page.goto(f"{site_server}/docs.html", timeout=10000)
    browser_page.wait_for_load_state("domcontentloaded")

    action_history: list[dict] = []
    pages_visited: list[str] = [browser_page.url]

    for _ in range(10):
        a11y_tree = extract_a11y_tree(browser_page)
        action = get_next_action(
            client=claude_client,
            persona=pi_persona,
            a11y_tree=a11y_tree,
            action_history=action_history,
        )

        if action.type == "conclude":
            action_history.append(
                {"type": "conclude", "reasoning": action.reasoning, "result": "ended"}
            )
            break

        result = execute_action(browser_page, action)
        action_history.append(
            {
                "type": action.type,
                "selector": action.selector,
                "reasoning": action.reasoning,
                "result": result.description if result.success else f"FAILED: {result.error}",
            }
        )
        if result.new_url and result.new_url not in pages_visited:
            pages_visited.append(result.new_url)

    final_tree = extract_a11y_tree(browser_page)
    evaluation = evaluate_journey(
        client=claude_client,
        persona=pi_persona,
        a11y_tree=final_tree,
        action_history=action_history,
        pages_visited=pages_visited,
    )

    assert evaluation.findability_score >= 3, (
        f"PI couldn't navigate docs (findability={evaluation.findability_score}). "
        f"Assessment: {evaluation.overall_assessment}"
    )


@pytest.mark.synthetic
def test_docs_page_has_pathway_cards(browser_page, site_server):
    """Docs page should present role-based pathway cards."""
    browser_page.goto(f"{site_server}/docs.html", timeout=10000)
    browser_page.wait_for_load_state("domcontentloaded")

    page_text = browser_page.text_content("body")
    page_lower = (page_text or "").lower()

    assert "principal investigator" in page_lower or "pi" in page_lower, (
        "Docs page should have a PI pathway card"
    )
    assert "researcher" in page_lower, "Docs page should have a Researcher pathway card"
    assert "student" in page_lower, "Docs page should have a Student pathway card"


@pytest.mark.synthetic
def test_docs_links_to_subpages(browser_page, site_server):
    """Docs page should link to all sub-documentation pages."""
    browser_page.goto(f"{site_server}/docs.html", timeout=10000)
    browser_page.wait_for_load_state("domcontentloaded")

    expected_targets = ["quickstart", "concepts", "verification", "privacy", "examples"]
    links = browser_page.locator("a[href]").all()
    hrefs = [link.get_attribute("href") or "" for link in links]

    for target in expected_targets:
        found = any(target in href for href in hrefs)
        assert found, f"Docs page should link to {target}.html"
