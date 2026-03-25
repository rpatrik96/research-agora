"""Scenario: Cursor user evaluates cross-platform interoperability.

Alex is an ML engineer using Cursor IDE who needs to determine whether
Research Agora skills work outside Claude Code.

Tests: multi-page navigation, interop content, back-button behavior.
"""

from __future__ import annotations

import pytest

from synthetic.scenarios.test_marketplace_browse import run_persona_journey


@pytest.mark.synthetic
def test_cursor_user_finds_interop(
    browser_page, claude_client, cursor_user_persona, site_server
):
    """Alex navigates from landing page through docs to interop."""
    action_history, pages_visited, _, evaluation = run_persona_journey(
        browser_page, claude_client, cursor_user_persona, site_server
    )

    assert len(pages_visited) >= 1, "Cursor user should visit the landing page"
    assert evaluation.findability_score >= 2, (
        f"Findability {evaluation.findability_score}/5 — interop info should "
        f"be discoverable. Assessment: {evaluation.overall_assessment}"
    )


@pytest.mark.synthetic
def test_benchmark_reviewer_journey(
    browser_page, claude_client, benchmark_persona, site_server
):
    """Prof. Nakamura evaluates the HALLMARK benchmark."""
    action_history, pages_visited, _, evaluation = run_persona_journey(
        browser_page, claude_client, benchmark_persona, site_server
    )

    assert len(action_history) >= 1, (
        f"Benchmark reviewer only took {len(action_history)} actions"
    )
    assert evaluation.findability_score >= 3, (
        f"Findability {evaluation.findability_score}/5 — benchmark info should "
        f"be easy to find. Assessment: {evaluation.overall_assessment}"
    )


@pytest.mark.synthetic
def test_interop_page_has_cursor_instructions(browser_page, site_server):
    """Interop page should contain Cursor-specific instructions."""
    browser_page.goto(f"{site_server}/interop.html", timeout=10000)
    browser_page.wait_for_load_state("domcontentloaded")

    page_text = browser_page.text_content("body")
    assert "cursor" in (page_text or "").lower(), (
        "Interop page should mention Cursor as a supported platform"
    )


@pytest.mark.synthetic
def test_benchmarks_page_has_leaderboard(browser_page, site_server):
    """Benchmarks page should display HALLMARK results."""
    browser_page.goto(f"{site_server}/benchmarks.html", timeout=10000)
    browser_page.wait_for_load_state("domcontentloaded")

    page_text = browser_page.text_content("body")
    page_lower = (page_text or "").lower()

    assert "hallmark" in page_lower, "Benchmarks page should reference HALLMARK"
    assert "2,525" in (page_text or "") or "2525" in (page_text or ""), (
        "Benchmarks page should display the annotated entry count"
    )
