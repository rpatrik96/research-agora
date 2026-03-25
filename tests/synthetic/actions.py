"""Playwright action primitives for synthetic user testing.

Translates Claude's structured Action decisions into Playwright calls.
Uses accessible locators (get_by_role, get_by_text) for robustness
rather than CSS selectors.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeout

from synthetic.claude_client import Action


@dataclass
class ActionResult:
    """Result of executing a Playwright action."""

    success: bool
    description: str
    new_url: str | None = None
    error: str | None = None


# Pattern: 'button "I\'m writing a paper"' -> role=button, name=I'm writing a paper
_SELECTOR_PATTERN = re.compile(r'^(\w+)\s+"(.+)"$')

_ROLE_MAP = {
    "button": "button",
    "link": "link",
    "textbox": "textbox",
    "checkbox": "checkbox",
    "radio": "radio",
    "heading": "heading",
    "tab": "tab",
    "combobox": "combobox",
    "searchbox": "searchbox",
    "menuitem": "menuitem",
}


def _resolve_locator(page: Page, selector: str):
    """Resolve an a11y-tree-style selector to a Playwright locator."""
    if not selector:
        return None

    # Strategy 1: parse role + name
    match = _SELECTOR_PATTERN.match(selector)
    if match:
        role, name = match.group(1), match.group(2)
        aria_role = _ROLE_MAP.get(role)
        if aria_role:
            locator = page.get_by_role(aria_role, name=name)
            if locator.count() > 0:
                return locator.first

    # Strategy 2: text match
    locator = page.get_by_text(selector, exact=False)
    if locator.count() > 0:
        return locator.first

    # Strategy 3: CSS selector fallback
    try:
        locator = page.locator(selector)
        if locator.count() > 0:
            return locator.first
    except Exception:
        pass

    return None


def execute_action(page: Page, action: Action) -> ActionResult:
    """Execute a Playwright action and return the result."""
    try:
        if action.type == "click":
            return _execute_click(page, action)
        elif action.type == "type":
            return _execute_type(page, action)
        elif action.type == "scroll":
            return _execute_scroll(page, action)
        elif action.type == "navigate":
            return _execute_navigate(page, action)
        elif action.type == "conclude":
            return ActionResult(success=True, description="Session concluded")
        else:
            return ActionResult(
                success=False,
                description=f"Unknown action type: {action.type}",
                error=f"Unsupported action type: {action.type}",
            )
    except PlaywrightTimeout as e:
        return ActionResult(
            success=False,
            description=f"Timeout executing {action.type} on {action.selector}",
            error=str(e),
        )
    except Exception as e:
        return ActionResult(
            success=False,
            description=f"Error executing {action.type}: {e}",
            error=str(e),
        )


def _execute_click(page: Page, action: Action) -> ActionResult:
    locator = _resolve_locator(page, action.selector or "")
    if locator is None:
        return ActionResult(
            success=False,
            description=f"Could not find element: {action.selector}",
            error=f"Element not found: {action.selector}",
        )

    url_before = page.url
    locator.click(timeout=5000)
    page.wait_for_load_state("domcontentloaded", timeout=3000)

    new_url = page.url if page.url != url_before else None
    desc = f"Clicked {action.selector}"
    if new_url:
        desc += f" -> navigated to {new_url}"
    return ActionResult(success=True, description=desc, new_url=new_url)


def _execute_type(page: Page, action: Action) -> ActionResult:
    locator = _resolve_locator(page, action.selector or "")
    if locator is None:
        return ActionResult(
            success=False,
            description=f"Could not find input: {action.selector}",
            error=f"Input not found: {action.selector}",
        )

    locator.fill(action.value or "", timeout=5000)
    page.wait_for_timeout(300)
    return ActionResult(
        success=True,
        description=f"Typed '{action.value}' into {action.selector}",
    )


def _execute_scroll(page: Page, action: Action) -> ActionResult:
    direction = (action.selector or "down").lower()
    pixels = -500 if direction == "up" else 500
    page.evaluate(f"window.scrollBy(0, {pixels})")
    page.wait_for_timeout(200)
    return ActionResult(
        success=True,
        description=f"Scrolled {direction} by {abs(pixels)}px",
    )


def _execute_navigate(page: Page, action: Action) -> ActionResult:
    url = action.selector or action.value or ""
    if not url:
        return ActionResult(
            success=False,
            description="No URL provided for navigate action",
            error="Missing URL",
        )

    if url.startswith("/") or not url.startswith("http"):
        base = page.url.rsplit("/", 1)[0]
        url = f"{base}/{url.lstrip('/')}"

    page.goto(url, timeout=10000)
    page.wait_for_load_state("domcontentloaded", timeout=5000)
    return ActionResult(
        success=True,
        description=f"Navigated to {url}",
        new_url=page.url,
    )
