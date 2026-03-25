"""Pytest fixtures for synthetic user testing.

Provides:
- Local HTTP server for the static site
- Playwright browser and page instances (sync API)
- Claude client (real or mock)
- Persona fixtures
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

# Add tests/ to sys.path so synthetic subpackage can be imported as 'synthetic.*'
_TESTS_DIR = Path(__file__).parent.parent
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

REPO_ROOT = _TESTS_DIR.parent
SITE_OUTPUT = REPO_ROOT / "site" / "output"


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def site_server():
    """Serve site/output/ on localhost via Python's http.server."""
    if not SITE_OUTPUT.exists():
        pytest.skip(f"Site output directory not found: {SITE_OUTPUT}")

    port = _find_free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "-d", str(SITE_OUTPUT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    base_url = f"http://localhost:{port}"

    for _ in range(50):
        try:
            with socket.create_connection(("localhost", port), timeout=0.1):
                break
        except OSError:
            time.sleep(0.1)
    else:
        proc.kill()
        pytest.fail("Site server did not start within 5 seconds")

    yield base_url

    proc.terminate()
    proc.wait(timeout=5)


@pytest.fixture(scope="session")
def browser():
    """Launch Playwright Chromium browser (sync API)."""
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=True)
    yield browser
    browser.close()
    pw.stop()


@pytest.fixture
def browser_page(browser, site_server):
    """Fresh browser page with clean state for each test."""
    context = browser.new_context(viewport={"width": 1280, "height": 720})
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture(scope="session")
def claude_client():
    """Anthropic client for LLM-based evaluation.

    Modes (controlled by environment variables):
    - Default: real Anthropic API (requires ANTHROPIC_API_KEY)
    - SYNTHETIC_MOCK_LLM=1: mock client replaying cached responses
    - SYNTHETIC_RECORD_RESPONSES=1: real client that also records responses
    """
    if os.environ.get("SYNTHETIC_MOCK_LLM"):
        from synthetic.claude_client import MockClaudeClient

        fixtures_path = Path(__file__).parent / "fixtures" / "mock_responses.json"
        return MockClaudeClient(fixtures_path)

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if not anthropic_key and not openai_key:
        pytest.skip("Neither ANTHROPIC_API_KEY nor OPENAI_API_KEY set and SYNTHETIC_MOCK_LLM not enabled")

    if openai_key:
        import openai

        client = openai.OpenAI()
    else:
        import anthropic

        client = anthropic.Anthropic()

    if os.environ.get("SYNTHETIC_RECORD_RESPONSES"):
        from synthetic.claude_client import RecordingClient

        fixtures_path = Path(__file__).parent / "fixtures" / "mock_responses.json"
        return RecordingClient(client, fixtures_path)

    return client


# -- Persona fixtures --


@pytest.fixture
def pi_persona():
    from synthetic.personas import PERSONAS

    return PERSONAS["prof_stein"]


@pytest.fixture
def student_persona():
    from synthetic.personas import PERSONAS

    return PERSONAS["maya"]


@pytest.fixture
def experienced_persona():
    from synthetic.personas import PERSONAS

    return PERSONAS["dr_chen"]


@pytest.fixture
def cursor_user_persona():
    from synthetic.personas import PERSONAS

    return PERSONAS["alex"]


@pytest.fixture
def benchmark_persona():
    from synthetic.personas import PERSONAS

    return PERSONAS["prof_nakamura"]
