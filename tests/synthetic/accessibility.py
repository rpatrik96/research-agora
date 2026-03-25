"""Accessibility tree extraction for synthetic user testing.

Uses Playwright's modern `aria_snapshot()` API to extract a compact YAML-like
representation of the page's accessibility tree. This provides a semantic view
of interactive elements (~50x smaller than raw HTML) suitable for LLM
consumption in the perceive-reason-act loop.
"""

from __future__ import annotations

from playwright.sync_api import Page


def extract_a11y_tree(page: Page) -> str:
    """Extract the page's accessibility tree as compact text.

    Uses Playwright's `aria_snapshot()` which returns a YAML-like string with:
    - Interactive elements (buttons, links, inputs) with roles and names
    - Headings for document structure
    - Hierarchy via indentation

    Also includes page context (URL, title, scroll position).
    """
    try:
        snapshot = page.locator(":root").aria_snapshot()
    except Exception:
        snapshot = "[empty page -- no accessibility tree available]"

    url = page.url
    title = page.title()
    scroll_y = page.evaluate("window.scrollY")
    scroll_height = page.evaluate("document.documentElement.scrollHeight")
    viewport_height = page.evaluate("window.innerHeight")

    max_scroll = scroll_height - viewport_height
    if max_scroll <= 0:
        scroll_pos = "top"
    elif scroll_y < 100:
        scroll_pos = "top"
    elif scroll_y >= max_scroll - 100:
        scroll_pos = "bottom"
    else:
        scroll_pos = "middle"

    context_lines = [
        f"Page: {title}",
        f"URL: {url}",
        f"Scroll: {scroll_y}/{max(max_scroll, 0)} ({scroll_pos})",
        "",
        "Accessibility Tree:",
        snapshot,
    ]

    return "\n".join(context_lines)


def get_visible_text_stats(page: Page) -> dict:
    """Get statistics about visible text on the page."""
    return page.evaluate(
        """() => {
        const visible = document.querySelectorAll(':not(.hidden)');
        const cards = document.querySelectorAll('.skill-card:not(.hidden)');
        const groups = document.querySelectorAll('.skill-group:not(.hidden)');
        return {
            visibleElements: visible.length,
            visibleCards: cards.length,
            visibleGroups: groups.length,
        };
    }"""
    )
