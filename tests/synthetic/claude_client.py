"""LLM client for synthetic user testing.

Supports both Anthropic and OpenAI backends. Provider is auto-detected
from the client type passed in.

Two call patterns:
1. Action selection — decides what the persona does next given the a11y tree.
2. Page evaluation — scores findability/clarity, lists issues and suggestions.

Also provides MockClaudeClient (replay) and RecordingClient (capture)
for CI determinism.

SECURITY: No litellm dependency. Uses anthropic or openai SDK directly.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from synthetic.personas import Persona

# Models per provider — no litellm
OPENAI_ACTION_MODEL = "gpt-4o-mini"
OPENAI_EVAL_MODEL = "gpt-4o"
ANTHROPIC_ACTION_MODEL = "claude-sonnet-4-20250514"
ANTHROPIC_EVAL_MODEL = "claude-sonnet-4-20250514"


# ── Data structures ──


@dataclass
class Action:
    """An action the synthetic user wants to take."""

    type: str  # click, type, scroll, navigate, conclude
    selector: str | None = None
    value: str | None = None
    reasoning: str = ""


@dataclass
class Issue:
    """A UX issue found during evaluation."""

    severity: str  # critical, major, minor
    page: str
    element: str
    description: str
    suggestion: str


@dataclass
class PageEvaluation:
    """Structured evaluation of a page from a persona's perspective."""

    findability_score: int  # 1-5
    clarity_score: int  # 1-5
    issues: list[Issue] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    goal_progress: dict[str, bool] = field(default_factory=dict)
    overall_assessment: str = ""


# ── Tool schemas (Anthropic format) ──

_ACTION_PARAMS = {
    "type": "object",
    "properties": {
        "type": {
            "type": "string",
            "enum": ["click", "type", "scroll", "navigate", "conclude"],
            "description": (
                "Action type. 'click' an element, 'type' text, "
                "'scroll' the page, 'navigate' to URL, "
                "'conclude' to end (goal reached or stuck)."
            ),
        },
        "selector": {
            "type": "string",
            "description": (
                "For click/type: element from accessibility tree "
                "(e.g., 'button \"I\\'m writing a paper\"'). "
                "For navigate: target URL path."
            ),
        },
        "value": {
            "type": "string",
            "description": "For type actions: the text to enter.",
        },
        "reasoning": {
            "type": "string",
            "description": "Why you chose this action (1-2 sentences).",
        },
    },
    "required": ["type", "reasoning"],
}

_EVAL_PARAMS = {
    "type": "object",
    "properties": {
        "findability_score": {
            "type": "integer",
            "description": "How easy to find what needed? (1=impossible, 5=trivial)",
        },
        "clarity_score": {
            "type": "integer",
            "description": "How clear is content/navigation? (1=confusing, 5=crystal clear)",
        },
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "severity": {"type": "string", "enum": ["critical", "major", "minor"]},
                    "page": {"type": "string"},
                    "element": {"type": "string"},
                    "description": {"type": "string"},
                    "suggestion": {"type": "string"},
                },
                "required": ["severity", "page", "element", "description", "suggestion"],
            },
        },
        "suggestions": {
            "type": "array",
            "items": {"type": "string"},
        },
        "goal_progress": {
            "type": "object",
            "additionalProperties": {"type": "boolean"},
        },
        "overall_assessment": {"type": "string"},
    },
    "required": [
        "findability_score",
        "clarity_score",
        "issues",
        "suggestions",
        "goal_progress",
        "overall_assessment",
    ],
}

# Anthropic format
ANTHROPIC_ACTION_TOOLS = [
    {"name": "take_action", "description": "Next action for the persona.", "input_schema": _ACTION_PARAMS}
]
ANTHROPIC_EVAL_TOOLS = [
    {"name": "submit_evaluation", "description": "Submit journey evaluation.", "input_schema": _EVAL_PARAMS}
]

# OpenAI format
OPENAI_ACTION_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "take_action",
            "description": "Next action for the persona.",
            "parameters": _ACTION_PARAMS,
        },
    }
]
OPENAI_EVAL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "submit_evaluation",
            "description": "Submit journey evaluation.",
            "parameters": _EVAL_PARAMS,
        },
    }
]


def _is_openai(client: Any) -> bool:
    """Detect if client is OpenAI (vs Anthropic or Mock)."""
    return type(client).__module__.startswith("openai")


# ── Action selection ──


def get_next_action(
    client: Any,
    persona: Persona,
    a11y_tree: str,
    action_history: list[dict],
) -> Action:
    """Ask the LLM what the persona would do next."""
    history_text = ""
    if action_history:
        steps = []
        for i, a in enumerate(action_history, 1):
            result = a.get("result", "ok")
            steps.append(f"  Step {i}: {a['type']} {a.get('selector', '')} -> {result}")
        history_text = "Previous actions:\n" + "\n".join(steps) + "\n\n"

    user_message = (
        f"{history_text}"
        f"Current page state:\n{a11y_tree}\n\n"
        f"What would {persona.name} do next? Use the take_action tool."
    )

    if _is_openai(client):
        return _openai_action(client, persona, user_message)
    else:
        return _anthropic_action(client, persona, user_message)


def _anthropic_action(client: Any, persona: Persona, user_message: str) -> Action:
    response = client.messages.create(
        model=ANTHROPIC_ACTION_MODEL,
        max_tokens=500,
        temperature=0,
        system=persona.system_prompt(),
        messages=[{"role": "user", "content": user_message}],
        tools=ANTHROPIC_ACTION_TOOLS,
        tool_choice={"type": "tool", "name": "take_action"},
    )
    for block in response.content:
        if block.type == "tool_use" and block.name == "take_action":
            return Action(
                type=block.input["type"],
                selector=block.input.get("selector"),
                value=block.input.get("value"),
                reasoning=block.input.get("reasoning", ""),
            )
    return Action(type="conclude", reasoning="No action returned by model")


def _openai_action(client: Any, persona: Persona, user_message: str) -> Action:
    response = client.chat.completions.create(
        model=OPENAI_ACTION_MODEL,
        max_tokens=500,
        temperature=0,
        messages=[
            {"role": "system", "content": persona.system_prompt()},
            {"role": "user", "content": user_message},
        ],
        tools=OPENAI_ACTION_TOOLS,
        tool_choice={"type": "function", "function": {"name": "take_action"}},
    )
    msg = response.choices[0].message
    if msg.tool_calls:
        args = json.loads(msg.tool_calls[0].function.arguments)
        return Action(
            type=args["type"],
            selector=args.get("selector"),
            value=args.get("value"),
            reasoning=args.get("reasoning", ""),
        )
    return Action(type="conclude", reasoning="No action returned by model")


# ── Journey evaluation ──


def evaluate_journey(
    client: Any,
    persona: Persona,
    a11y_tree: str,
    action_history: list[dict],
    pages_visited: list[str],
) -> PageEvaluation:
    """Evaluate the overall journey from the persona's perspective."""
    steps_text = "\n".join(
        f"  {i}. [{a['type']}] {a.get('selector', '')} -- {a.get('reasoning', '')}"
        for i, a in enumerate(action_history, 1)
    )
    criteria_text = "\n".join(f"  - {c}" for c in persona.success_criteria)

    user_message = (
        f"You just simulated {persona.name} ({persona.role}) browsing a website.\n\n"
        f"Goal: {persona.goal}\n\n"
        f"Pages visited: {', '.join(pages_visited)}\n\n"
        f"Actions taken:\n{steps_text}\n\n"
        f"Final page state:\n{a11y_tree}\n\n"
        f"Success criteria to evaluate:\n{criteria_text}\n\n"
        "Evaluate this journey using the submit_evaluation tool. Be specific "
        "about issues -- reference exact elements and pages."
    )

    eval_system = (
        "You are a UX researcher evaluating a website from the perspective "
        "of a specific user persona. Be honest and specific."
    )

    if _is_openai(client):
        return _openai_eval(client, eval_system, user_message)
    else:
        return _anthropic_eval(client, eval_system, user_message)


def _anthropic_eval(client: Any, system: str, user_message: str) -> PageEvaluation:
    response = client.messages.create(
        model=ANTHROPIC_EVAL_MODEL,
        max_tokens=2000,
        temperature=0,
        system=system,
        messages=[{"role": "user", "content": user_message}],
        tools=ANTHROPIC_EVAL_TOOLS,
        tool_choice={"type": "tool", "name": "submit_evaluation"},
    )
    for block in response.content:
        if block.type == "tool_use" and block.name == "submit_evaluation":
            return _parse_evaluation(block.input)
    return PageEvaluation(findability_score=0, clarity_score=0, overall_assessment="Evaluation failed.")


def _openai_eval(client: Any, system: str, user_message: str) -> PageEvaluation:
    response = client.chat.completions.create(
        model=OPENAI_EVAL_MODEL,
        max_tokens=2000,
        temperature=0,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
        tools=OPENAI_EVAL_TOOLS,
        tool_choice={"type": "function", "function": {"name": "submit_evaluation"}},
    )
    msg = response.choices[0].message
    if msg.tool_calls:
        args = json.loads(msg.tool_calls[0].function.arguments)
        return _parse_evaluation(args)
    return PageEvaluation(findability_score=0, clarity_score=0, overall_assessment="Evaluation failed.")


def _parse_evaluation(data: dict) -> PageEvaluation:
    return PageEvaluation(
        findability_score=data["findability_score"],
        clarity_score=data["clarity_score"],
        issues=[Issue(**i) for i in data.get("issues", [])],
        suggestions=data.get("suggestions", []),
        goal_progress=data.get("goal_progress", {}),
        overall_assessment=data.get("overall_assessment", ""),
    )


# ── Mock / Recording clients for CI ──


def _hash_request(model: str, messages: list, tools: list | None = None) -> str:
    key = json.dumps({"model": model, "messages": messages, "tools": tools}, sort_keys=True)
    return hashlib.sha256(key.encode()).hexdigest()[:16]


class MockClaudeClient:
    """Replays cached responses for deterministic CI runs."""

    def __init__(self, fixtures_path: Path):
        self.fixtures_path = Path(fixtures_path)
        self._responses: dict[str, Any] = {}
        if self.fixtures_path.exists():
            self._responses = json.loads(self.fixtures_path.read_text())
        self.messages = _MockMessages(self._responses)


class _MockMessages:
    def __init__(self, responses: dict[str, Any]):
        self._responses = responses
        self._call_index = 0

    def create(self, **kwargs) -> Any:
        request_hash = _hash_request(
            kwargs.get("model", ""),
            kwargs.get("messages", []),
            kwargs.get("tools"),
        )
        if request_hash in self._responses:
            return _MockResponse(self._responses[request_hash])

        self._call_index += 1
        return _MockResponse(
            {
                "content": [
                    {
                        "type": "tool_use",
                        "name": kwargs.get("tool_choice", {}).get("name", "take_action"),
                        "input": {
                            "type": "conclude",
                            "reasoning": f"Mock fallback ({request_hash})",
                            "findability_score": 3,
                            "clarity_score": 3,
                            "issues": [],
                            "suggestions": [],
                            "goal_progress": {},
                            "overall_assessment": "Mock evaluation.",
                        },
                    }
                ]
            }
        )


class _MockResponse:
    def __init__(self, data: dict):
        self.content = [_MockBlock(b) for b in data.get("content", [])]


class _MockBlock:
    def __init__(self, data: dict):
        self.type = data.get("type", "text")
        self.name = data.get("name", "")
        self.input = data.get("input", {})
        self.text = data.get("text", "")


class RecordingClient:
    """Wraps a real client and records responses for later replay."""

    def __init__(self, real_client: Any, fixtures_path: Path):
        self._real = real_client
        self.fixtures_path = Path(fixtures_path)
        self._recorded: dict[str, Any] = {}
        if self.fixtures_path.exists():
            self._recorded = json.loads(self.fixtures_path.read_text())
        self.messages = _RecordingMessages(self._real, self._recorded, self.fixtures_path)


class _RecordingMessages:
    def __init__(self, real_client: Any, recorded: dict, fixtures_path: Path):
        self._real = real_client
        self._recorded = recorded
        self._fixtures_path = fixtures_path

    def create(self, **kwargs) -> Any:
        response = self._real.messages.create(**kwargs)
        request_hash = _hash_request(
            kwargs.get("model", ""),
            kwargs.get("messages", []),
            kwargs.get("tools"),
        )
        content = []
        for block in response.content:
            if block.type == "tool_use":
                content.append({"type": "tool_use", "name": block.name, "input": block.input})
            elif block.type == "text":
                content.append({"type": "text", "text": block.text})
        self._recorded[request_hash] = {"content": content}
        self._fixtures_path.parent.mkdir(parents=True, exist_ok=True)
        self._fixtures_path.write_text(json.dumps(self._recorded, indent=2))
        return response
