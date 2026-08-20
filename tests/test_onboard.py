"""Tests for scripts/onboard.py — tier classification, skill recommendations,
CLAUDE.md generation, project detection, and JSON output."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Add scripts/ to path so we can import onboard directly
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from onboard import (
    DEFAULT_SKILLS,
    classify_tier,
    detect_project,
    generate_claude_md,
    get_skill_recommendations,
)

# ---------------------------------------------------------------------------
# Tier classification
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "cli, ai, languages, expected_tier",
    [
        # Tier 0: CLI a + AI a (no language)
        ("a", "a", "", 0),
        ("a", "b", "", 0),
        ("b", "a", "", 0),
        ("b", "b", "", 0),
        # Tier 1: CLI b/c + AI b/c + has language
        # Note: cli=b (level 1) + ai=b (level 1) hits the "cli<=1 and ai<=1" branch
        # first and returns tier 0 regardless of language — tier 1 needs cli OR ai > 1.
        ("c", "b", "R", 1),
        ("b", "c", "Julia", 1),
        ("c", "c", "Python", 1),
        # Tier 2: CLI c + AI c (no mcp/agent signal, or no language for tier-1 path)
        ("c", "c", "", 2),
        ("d", "c", "", 2),
        ("c", "d", "", 2),
        # Tier 3: CLI d + AI d
        ("d", "d", "", 3),
    ],
)
def test_tier_classification(cli, ai, languages, expected_tier):
    answers = {"cli": cli, "ai": ai, "languages": languages}
    assert classify_tier(answers) == expected_tier


def test_tier_0_missing_keys():
    """Missing cli/ai keys default to 'a' (level 0) → tier 0."""
    assert classify_tier({}) == 0


def test_tier_0_explicit_no_language():
    """cli=b, ai=b, no language → tier 0 (fails the langs check)."""
    assert classify_tier({"cli": "b", "ai": "b", "languages": ""}) == 0


def test_tier_0_b_b_with_language():
    """cli=b (level 1), ai=b (level 1): first branch 'cli<=1 and ai<=1' fires
    before the tier-1 language check, so tier is 0 even with a language."""
    assert classify_tier({"cli": "b", "ai": "b", "languages": "Python"}) == 0


def test_tier_1_requires_language():
    """cli=c, ai=c but no language still falls through to tier 2, not 1."""
    tier = classify_tier({"cli": "c", "ai": "c", "languages": ""})
    assert tier == 2


def test_tier_default_fallback():
    """High CLI but low AI → default lower tier (1)."""
    answers = {"cli": "d", "ai": "a", "languages": "Python"}
    # cli=3, ai=0: first branch (cli<=1 and ai<=1) is False;
    # second branch (cli<=2 and ai<=2 and langs) is False (cli=3>2);
    # third branch (cli>=2 and ai>=2) is False (ai=0);
    # falls to default return 1
    assert classify_tier(answers) == 1


def test_tier_high_cli_low_ai_no_language():
    """High CLI (d), low AI (a), no language → default 1."""
    assert classify_tier({"cli": "d", "ai": "a", "languages": ""}) == 1


def test_tier_3_cli_d_ai_b():
    """cli=d but ai=b → does not reach tier 3."""
    answers = {"cli": "d", "ai": "b", "languages": "Python"}
    assert classify_tier(answers) < 3


# ---------------------------------------------------------------------------
# Skill recommendations
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "task, tier, expected_skill",
    [
        # Literature at tier 1 and 2
        ("a", 1, "/paper-references"),
        ("a", 2, "/benchmark-scout"),
        # Writing at tier 1 and 2
        ("d", 1, "/paper-abstract"),
        ("d", 2, "/writing-diagnosis"),
    ],
)
def test_skill_recommendations_contain_expected(task, tier, expected_skill):
    skills = get_skill_recommendations(task, tier)
    names = [name for name, _ in skills]
    assert expected_skill in names, f"Expected {expected_skill} in skills for task={task}, tier={tier}: {names}"


def test_skill_recommendations_unknown_task_returns_defaults():
    skills = get_skill_recommendations("z", 2)
    assert skills == DEFAULT_SKILLS


def test_skill_recommendations_unknown_task_tier_0_returns_defaults():
    """Unknown task at any tier → DEFAULT_SKILLS."""
    assert get_skill_recommendations("z", 0) == DEFAULT_SKILLS


def test_skill_recommendations_task_a_tier_1_length():
    skills = get_skill_recommendations("a", 1)
    assert len(skills) >= 1


def test_skill_recommendations_task_d_tier_2_has_more_than_tier_1():
    """Tier 2 writing recommendations should be at least as long as tier 1."""
    t1 = get_skill_recommendations("d", 1)
    t2 = get_skill_recommendations("d", 2)
    assert len(t2) >= len(t1)


def test_skill_recommendations_returns_tuples():
    skills = get_skill_recommendations("a", 1)
    for item in skills:
        assert isinstance(item, tuple)
        assert len(item) == 2


def test_skill_recommendations_tier_0_falls_back_to_defaults():
    """Tier 0 has no entry in SKILL_TABLE for task 'a'; loop descends to -1 and
    returns DEFAULT_SKILLS (the loop is range(0, -1, -1) = [0], finds nothing)."""
    skills = get_skill_recommendations("a", 0)
    assert skills == DEFAULT_SKILLS


# ---------------------------------------------------------------------------
# CLAUDE.md generation
# ---------------------------------------------------------------------------


def test_claude_md_latex_build_commands_present():
    answers = {"writing_tool": "LaTeX", "domain": "ML", "languages": ""}
    md = generate_claude_md(answers, tier=1)
    assert "latexmk -pdf" in md


def test_claude_md_latex_via_overleaf_keyword():
    """'Overleaf' in writing_tool should also trigger LaTeX build commands."""
    answers = {"writing_tool": "Overleaf", "domain": "Physics", "languages": ""}
    md = generate_claude_md(answers, tier=2)
    assert "latexmk -pdf" in md


def test_claude_md_no_latex_build_when_word():
    answers = {"writing_tool": "Word", "domain": "Biology", "languages": ""}
    md = generate_claude_md(answers, tier=1)
    assert "latexmk" not in md


def test_claude_md_python_build_commands_present():
    answers = {"languages": "Python", "domain": "ML", "writing_tool": ""}
    md = generate_claude_md(answers, tier=2)
    assert "pytest" in md
    assert "ruff check" in md


def test_claude_md_no_python_build_when_language_is_r():
    answers = {"languages": "R", "domain": "Stats", "writing_tool": ""}
    md = generate_claude_md(answers, tier=2)
    assert "pytest" not in md


def test_claude_md_git_safety_section_tier_0():
    answers = {"git": "y", "domain": "ML", "languages": "", "writing_tool": ""}
    md = generate_claude_md(answers, tier=0)
    assert "Git Safety Net" in md


def test_claude_md_git_safety_section_tier_1():
    answers = {"git": "y", "domain": "ML", "languages": "", "writing_tool": ""}
    md = generate_claude_md(answers, tier=1)
    assert "Git Safety Net" in md


def test_claude_md_no_git_safety_section_tier_2():
    answers = {"git": "y", "domain": "ML", "languages": "", "writing_tool": ""}
    md = generate_claude_md(answers, tier=2)
    assert "Git Safety Net" not in md


def test_claude_md_no_git_safety_section_tier_3():
    answers = {"git": "y", "domain": "ML", "languages": "", "writing_tool": ""}
    md = generate_claude_md(answers, tier=3)
    assert "Git Safety Net" not in md


def test_claude_md_git_safety_appears_when_no_git_regardless_of_tier():
    """No git (git=n) at tier 2 still triggers the safety section."""
    answers = {"git": "n", "domain": "ML", "languages": "", "writing_tool": ""}
    md = generate_claude_md(answers, tier=2)
    assert "Git Safety Net" in md


def test_claude_md_verification_tier_0_is_manual():
    answers = {"domain": "ML", "languages": "", "writing_tool": "", "git": "y"}
    md = generate_claude_md(answers, tier=0)
    assert "Google Scholar" in md


def test_claude_md_verification_tier_1_is_manual():
    answers = {"domain": "ML", "languages": "", "writing_tool": "", "git": "y"}
    md = generate_claude_md(answers, tier=1)
    assert "Google Scholar" in md


def test_claude_md_verification_tier_2_references_skill():
    answers = {"domain": "ML", "languages": "", "writing_tool": "", "git": "y"}
    md = generate_claude_md(answers, tier=2)
    assert "/paper-references" in md


def test_claude_md_verification_tier_3_references_bibtexupdater():
    answers = {"domain": "ML", "languages": "", "writing_tool": "", "git": "y"}
    md = generate_claude_md(answers, tier=3)
    assert "bibtexupdater" in md


def test_claude_md_contains_domain():
    answers = {"domain": "Neuroscience", "languages": "", "writing_tool": "", "git": "y"}
    md = generate_claude_md(answers, tier=1)
    assert "Neuroscience" in md


# ---------------------------------------------------------------------------
# Project detection
# ---------------------------------------------------------------------------


def test_detect_empty_directory(tmp_path):
    result = detect_project(str(tmp_path))
    assert result.get("languages", "") == ""
    assert result.get("writing_tool", "") == ""


def test_detect_tex_files(tmp_path):
    (tmp_path / "main.tex").write_text(r"\documentclass{article}")
    result = detect_project(str(tmp_path))
    assert result.get("writing_tool") == "LaTeX"


def test_detect_python_files(tmp_path):
    (tmp_path / "train.py").write_text("import torch")
    result = detect_project(str(tmp_path))
    assert "Python" in result.get("languages", "")


def test_detect_git_directory(tmp_path):
    (tmp_path / ".git").mkdir()
    result = detect_project(str(tmp_path))
    assert result.get("git") == "y"


def test_detect_no_git_directory(tmp_path):
    result = detect_project(str(tmp_path))
    assert result.get("git") == "n"


def test_detect_python_and_tex(tmp_path):
    (tmp_path / "main.tex").write_text(r"\documentclass{article}")
    (tmp_path / "model.py").write_text("import torch")
    result = detect_project(str(tmp_path))
    assert "Python" in result.get("languages", "")
    assert result.get("writing_tool") == "LaTeX"


def test_detect_bib_file(tmp_path):
    (tmp_path / "refs.bib").write_text("@article{key, title={T}}")
    result = detect_project(str(tmp_path))
    assert result.get("ref_manager") == "BibTeX"


def test_detect_git_with_python_sets_cli_comfort(tmp_path):
    """git + python present → cli inferred as 'c'."""
    (tmp_path / ".git").mkdir()
    (tmp_path / "model.py").write_text("x = 1")
    result = detect_project(str(tmp_path))
    assert result.get("cli") == "c"


# ---------------------------------------------------------------------------
# JSON output mode
# ---------------------------------------------------------------------------


def test_json_output_is_valid(tmp_path):
    """--tier 1 --json must produce parseable JSON with required keys."""
    result = subprocess.run(
        [sys.executable, "scripts/onboard.py", "--tier", "1", "--json"],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    data = json.loads(result.stdout)
    assert data["tier"] == 1
    assert "tier_name" in data
    assert "skills" in data
    assert "claude_md" in data
    assert "five_minute_win" in data
    assert isinstance(data["skills"], list)


@pytest.mark.parametrize("tier", [0, 1, 2, 3])
def test_json_output_all_tiers(tier):
    result = subprocess.run(
        [sys.executable, "scripts/onboard.py", "--tier", str(tier), "--json"],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["tier"] == tier


def test_json_skills_have_name_and_description():
    result = subprocess.run(
        [sys.executable, "scripts/onboard.py", "--tier", "2", "--task", "d", "--json"],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    data = json.loads(result.stdout)
    for skill in data["skills"]:
        assert "name" in skill
        assert "description" in skill
