"""Synthetic user personas for LLM-based user testing.

Each persona represents a distinct user archetype with specific goals,
background knowledge, and success criteria. Derived from Research Agora's
target audience segments (docs.html pathway cards).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Persona:
    """A synthetic user persona for testing."""

    name: str
    role: str
    background: str
    goal: str
    expected_pages: list[str] = field(default_factory=list)
    search_terms: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)
    max_actions: int = 20

    def system_prompt(self) -> str:
        """Generate the system prompt that establishes this persona for Claude."""
        return (
            f"You are simulating a user named {self.name}.\n"
            f"Role: {self.role}\n"
            f"Background: {self.background}\n"
            f"Goal: {self.goal}\n\n"
            "You are browsing a website. At each step you will receive the page's "
            "accessibility tree (a structured list of interactive elements). "
            "Decide what action to take next based on your goal. "
            "Think about what a real person in your role would do — scan headings, "
            "look for relevant links, try search, click buttons that seem relevant.\n\n"
            "If you have accomplished your goal or are stuck, conclude the session."
        )


PERSONAS: dict[str, Persona] = {
    "prof_stein": Persona(
        name="Prof. Stein",
        role="Principal Investigator at a mid-size ML lab (6 researchers)",
        background=(
            "Runs an ML lab at a European university. Evaluates tools for the group. "
            "Cares about verification rigor, data privacy (GDPR), and whether adoption "
            "is worth the onboarding cost. Not a Claude Code user yet."
        ),
        goal=(
            "Determine whether Research Agora is worth adopting for the lab. "
            "Specifically: understand what skills are available, how verification works, "
            "and what the privacy implications are."
        ),
        expected_pages=["index.html", "docs.html", "verification.html", "privacy.html"],
        search_terms=["verification", "GDPR", "policy"],
        success_criteria=[
            "Found the install command",
            "Reached the verification policy page",
            "Reached the privacy/GDPR page",
            "Understood how many skills are available",
        ],
    ),
    "maya": Persona(
        name="Maya",
        role="Second-year PhD student, first encounter with Claude Code plugins",
        background=(
            "Working on her first NeurIPS submission. Uses Claude Code daily but has "
            "never installed a plugin. Heard about Research Agora from a labmate. "
            "Wants something to help with paper writing, especially abstracts and "
            "literature reviews."
        ),
        goal=(
            "Install Research Agora and identify a skill to help write her paper abstract. "
            "Follow the quickstart path to get set up within 5 minutes."
        ),
        expected_pages=["index.html", "quickstart.html", "examples.html"],
        search_terms=["abstract", "write paper", "latex"],
        success_criteria=[
            "Found the install command",
            "Reached the quickstart page",
            "Identified a relevant skill for paper writing",
            "Found a try-this example or starter prompt",
        ],
    ),
    "dr_chen": Persona(
        name="Dr. Chen",
        role="Postdoc, experienced Claude Code and Research Agora user",
        background=(
            "Has been using Research Agora for 3 months. Familiar with paper-writing "
            "skills. Now wants to explore verification and theory tools for a new "
            "paper that makes formal claims about convergence bounds."
        ),
        goal=(
            "Find skills related to proof verification, bounds analysis, and claim "
            "auditing. Use the intent filters and search to narrow down options."
        ),
        expected_pages=["index.html", "benchmarks.html"],
        search_terms=["proof", "bounds", "claim", "theorem"],
        success_criteria=[
            "Used intent button 'Verify my paper'",
            "Found theory-tools or quality-verification group",
            "Identified at least 2 relevant skills",
            "Reached the benchmarks page",
        ],
    ),
    "alex": Persona(
        name="Alex",
        role="ML engineer using Cursor IDE, evaluating cross-platform compatibility",
        background=(
            "Works at a startup using Cursor as primary IDE. Interested in Research "
            "Agora's skills but needs to know if they work outside Claude Code. "
            "Technical enough to follow conversion instructions."
        ),
        goal=(
            "Determine whether Research Agora skills work with Cursor. Find the "
            "interoperability documentation and understand the conversion process."
        ),
        expected_pages=["index.html", "docs.html", "interop.html"],
        search_terms=["cursor", "interop", "platform"],
        success_criteria=[
            "Found the interop page",
            "Understood the AgentSkills.io standard",
            "Found Cursor-specific instructions",
            "Assessed feasibility of using skills outside Claude Code",
        ],
    ),
    "prof_nakamura": Persona(
        name="Prof. Nakamura",
        role="Senior researcher reviewing citation hallucination detection methods",
        background=(
            "Expert in scientific integrity and automated verification. Heard about "
            "HALLMARK benchmark at a workshop. Wants to evaluate the methodology "
            "and see how different approaches compare."
        ),
        goal=(
            "Find the HALLMARK benchmark page, understand the scoring methodology, "
            "and compare the built-in baselines and leaderboard results."
        ),
        expected_pages=["index.html", "benchmarks.html"],
        search_terms=["hallucination", "citation", "benchmark", "HALLMARK"],
        success_criteria=[
            "Reached the benchmarks page",
            "Understood the difficulty tiers (easy/medium/hard)",
            "Found the leaderboard or baseline results",
            "Identified the number of annotated entries (2525)",
        ],
    ),
}
