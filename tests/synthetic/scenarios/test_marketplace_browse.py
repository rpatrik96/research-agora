"""Scenario: PI evaluates the skills marketplace.

Prof. Stein lands on index.html and explores the catalog to determine
whether Research Agora is worth adopting for a 6-person ML lab.

Tests: search, intent buttons, skill cards, copy-to-clipboard, navigation.
"""

from __future__ import annotations

import time

import pytest

from synthetic.accessibility import extract_a11y_tree
from synthetic.actions import execute_action
from synthetic.claude_client import evaluate_journey, get_next_action
from synthetic.reporter import save_scenario_report


def run_persona_journey(
    browser_page, claude_client, persona, site_server, scenario_name="journey"
):
    """Core perceive-reason-act loop shared across scenarios.

    Saves a JSON report to tests/synthetic/reports/ after each run.

    Returns:
        Tuple of (action_history, pages_visited, final_a11y_tree, evaluation).
    """
    start_time = time.monotonic()
    browser_page.goto(f"{site_server}/index.html", timeout=10000)
    browser_page.wait_for_load_state("domcontentloaded")

    action_history: list[dict] = []
    pages_visited: list[str] = [browser_page.url]

    for _step in range(persona.max_actions):
        a11y_tree = extract_a11y_tree(browser_page)

        action = get_next_action(
            client=claude_client,
            persona=persona,
            a11y_tree=a11y_tree,
            action_history=action_history,
        )

        if action.type == "conclude":
            action_history.append(
                {
                    "type": "conclude",
                    "reasoning": action.reasoning,
                    "result": "session ended",
                }
            )
            break

        result = execute_action(browser_page, action)

        action_entry = {
            "type": action.type,
            "selector": action.selector,
            "value": action.value,
            "reasoning": action.reasoning,
            "result": result.description if result.success else f"FAILED: {result.error}",
        }
        action_history.append(action_entry)

        if result.new_url and result.new_url not in pages_visited:
            pages_visited.append(result.new_url)

    final_tree = extract_a11y_tree(browser_page)
    evaluation = evaluate_journey(
        client=claude_client,
        persona=persona,
        a11y_tree=final_tree,
        action_history=action_history,
        pages_visited=pages_visited,
    )

    duration = time.monotonic() - start_time

    # Save JSON report
    report_path = save_scenario_report(
        scenario_name=scenario_name,
        persona_name=persona.name,
        action_history=action_history,
        pages_visited=pages_visited,
        evaluation=evaluation,
        duration_seconds=duration,
    )
    print(
        f"\n  Report: {report_path.name} | "
        f"{persona.name}: findability={evaluation.findability_score}/5 "
        f"clarity={evaluation.clarity_score}/5 "
        f"issues={len(evaluation.issues)} actions={len(action_history)}"
    )

    return action_history, pages_visited, final_tree, evaluation


@pytest.mark.synthetic
def test_pi_evaluates_marketplace(browser_page, claude_client, pi_persona, site_server):
    """Prof. Stein lands on index.html and evaluates the skill catalog."""
    action_history, pages_visited, _, evaluation = run_persona_journey(
        browser_page, claude_client, pi_persona, site_server,
        scenario_name="marketplace_browse",
    )

    assert len(action_history) >= 1, (
        f"Persona only took {len(action_history)} actions — expected engagement "
        f"with the page. Actions: {action_history}"
    )
    assert len(pages_visited) >= 1, "Persona should visit at least the landing page"

    assert evaluation.findability_score >= 3, (
        f"Findability score {evaluation.findability_score}/5 is too low. "
        f"Assessment: {evaluation.overall_assessment}"
    )
    assert evaluation.clarity_score >= 3, (
        f"Clarity score {evaluation.clarity_score}/5 is too low. "
        f"Assessment: {evaluation.overall_assessment}"
    )


@pytest.mark.synthetic
def test_pi_finds_install_command(browser_page, site_server):
    """The install command should be visible on the landing page."""
    browser_page.goto(f"{site_server}/index.html", timeout=10000)
    browser_page.wait_for_load_state("domcontentloaded")

    install_text = browser_page.locator(".install-command, code").all_text_contents()
    has_install = any("/plugin" in t or "marketplace" in t for t in install_text)
    assert has_install, "Install command should be visible on the landing page"

    copy_buttons = browser_page.get_by_role("button", name="Copy").count()
    assert copy_buttons >= 1, "Copy button for install command should exist"
