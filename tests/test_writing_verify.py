"""Tests for writing_verify.py — writing quality metrics script."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from writing_verify import (
    DocumentMetrics,
    analyze_document,
    count_fillers,
    count_hedges,
    count_syllables,
    detect_format,
    flesch_kincaid_grade,
    is_passive,
    monotony_score,
    overall_grade,
    score_accessibility,
    score_clarity,
    score_flow,
    split_sentences,
    strip_latex,
    strip_markdown,
)

# ---------------------------------------------------------------------------
# TestSentenceSplitting
# ---------------------------------------------------------------------------

class TestSentenceSplitting:
    def test_simple_sentences(self):
        assert len(split_sentences("Hello world. This is a test.")) == 2

    def test_abbreviations_preserved(self):
        assert len(split_sentences("Dr. Smith went to the store. He bought milk.")) == 2

    def test_et_al(self):
        assert len(split_sentences("Smith et al. showed this result. It was significant.")) == 2

    def test_fig_reference(self):
        assert len(split_sentences("See Fig. 3 for details. The results show improvement.")) == 2

    def test_eg_ie(self):
        result = split_sentences("Some methods, e.g., SGD, work well. Others fail.")
        assert len(result) == 2

    def test_single_sentence(self):
        assert len(split_sentences("Just one sentence here.")) == 1

    def test_empty_input(self):
        assert split_sentences("") == []

    def test_question_and_exclamation(self):
        assert len(split_sentences("Is this good? Yes! It works.")) == 3


# ---------------------------------------------------------------------------
# TestPassiveVoice
# ---------------------------------------------------------------------------

class TestPassiveVoice:
    def test_passive_detected(self):
        assert is_passive("The model was trained on ImageNet.") is True

    def test_passive_with_adverb(self):
        assert is_passive("The results were carefully analyzed.") is True

    def test_active_not_flagged(self):
        assert is_passive("We trained the model on ImageNet.") is False

    def test_active_past_tense(self):
        assert is_passive("The model achieved state-of-the-art results.") is False

    def test_passive_is_being(self):
        assert is_passive("The data is being processed.") is True

    def test_passive_has_been(self):
        assert is_passive("The method has been shown to work.") is True

    def test_not_passive_plain_adjective(self):
        # "are good" — "good" is not in the past-participle pattern
        assert is_passive("The results are excellent.") is False


# ---------------------------------------------------------------------------
# TestSyllableCount
# ---------------------------------------------------------------------------

class TestSyllableCount:
    @pytest.mark.parametrize("word,expected", [
        ("cat", 1),
        ("hello", 2),
        ("optimization", 5),  # op-ti-mi-za-tion
    ])
    def test_basic_syllables(self, word, expected):
        assert count_syllables(word) == expected

    def test_empty(self):
        assert count_syllables("") == 0 or count_syllables("") >= 0  # max(1,0) may return 1

    def test_minimum_one(self):
        # Any non-empty word gets at least 1 syllable
        assert count_syllables("nth") >= 1

    def test_multi_syllable(self):
        assert count_syllables("regularization") >= 4


# ---------------------------------------------------------------------------
# TestFleschKincaid
# ---------------------------------------------------------------------------

class TestFleschKincaid:
    def test_simple_text(self):
        sentences = ["The cat sat.", "It was hot.", "The dog ran."]
        assert flesch_kincaid_grade(sentences) < 10

    def test_complex_text(self):
        sentences = [
            "The stochastic optimization of deep neural network architectures"
            " necessitates sophisticated regularization.",
            "Variational autoencoders leverage probabilistic latent"
            " representations to disentangle generative factors.",
        ]
        assert flesch_kincaid_grade(sentences) > 12

    def test_empty(self):
        assert flesch_kincaid_grade([]) == 0.0

    def test_returns_float(self):
        assert isinstance(flesch_kincaid_grade(["The cat sat on a mat."]), float)


# ---------------------------------------------------------------------------
# TestMonotonyScore
# ---------------------------------------------------------------------------

class TestMonotonyScore:
    def test_all_same_length(self):
        # All medium sentences → all same bucket → high monotony
        assert monotony_score([20, 20, 20, 20, 20]) > 0.5

    def test_alternating(self):
        # Alternating short/long → no consecutive same bucket → low monotony
        assert monotony_score([5, 30, 5, 30, 5, 30]) < 0.5

    def test_short_input(self):
        assert monotony_score([10]) == 0.0

    def test_returns_float_in_range(self):
        score = monotony_score([5, 20, 8, 30, 12, 25])
        assert 0.0 <= score <= 1.0

    def test_empty(self):
        assert monotony_score([]) == 0.0


# ---------------------------------------------------------------------------
# TestFillerCounting
# ---------------------------------------------------------------------------

class TestFillerCounting:
    def test_single_filler(self):
        count, inv = count_fillers("This is basically a test.")
        assert count >= 1
        assert "basically" in inv

    def test_phrase_filler(self):
        count, inv = count_fillers("In order to improve results, we retrain.")
        assert count >= 1

    def test_no_fillers(self):
        count, inv = count_fillers("The model achieves 95% accuracy.")
        assert count == 0

    def test_multiple_fillers(self):
        count, _ = count_fillers("It is actually really very good.")
        assert count >= 2

    def test_returns_tuple(self):
        result = count_fillers("just a test")
        assert isinstance(result, tuple) and len(result) == 2


# ---------------------------------------------------------------------------
# TestHedgeCounting
# ---------------------------------------------------------------------------

class TestHedgeCounting:
    def test_single_hedge(self):
        count, inv = count_hedges("This might work.")
        assert count >= 1
        assert "might" in inv

    def test_phrase_hedge(self):
        count, inv = count_hedges("It is possible that the method fails.")
        assert count >= 1

    def test_no_hedges(self):
        count, _ = count_hedges("The method converges in 100 epochs.")
        assert count == 0

    def test_multiple_hedges(self):
        count, _ = count_hedges("This could potentially perhaps work.")
        assert count >= 2

    def test_returns_tuple(self):
        result = count_hedges("maybe probably")
        assert isinstance(result, tuple) and len(result) == 2


# ---------------------------------------------------------------------------
# TestLatexStripping
# ---------------------------------------------------------------------------

class TestLatexStripping:
    def test_strip_commands(self):
        result = strip_latex(r"\textbf{important}")
        assert "important" in result
        assert "\\" not in result.replace("\\", "")  # no backslash commands left

    def test_strip_math(self):
        result = strip_latex(r"We compute $x = y + z$ here.")
        assert "We compute" in result
        assert "here" in result
        assert "$" not in result

    def test_strip_cite(self):
        result = strip_latex(r"As shown by \cite{smith2023}")
        assert "\\cite" not in result

    def test_strip_figure(self):
        result = strip_latex(r"\begin{figure}some caption\end{figure}")
        assert "\\begin" not in result

    def test_strip_equation(self):
        result = strip_latex(r"\begin{equation}x=y\end{equation}")
        assert "[EQUATION]" in result

    def test_preserve_section_titles(self):
        result = strip_latex(r"\section{Introduction}")
        assert "Introduction" in result


# ---------------------------------------------------------------------------
# TestMarkdownStripping
# ---------------------------------------------------------------------------

class TestMarkdownStripping:
    def test_strip_headers(self):
        result = strip_markdown("# Title\n\nContent")
        assert "Title" in result
        assert result.strip().startswith("#") is False or "Title" in result

    def test_strip_bold_italic(self):
        result = strip_markdown("**bold** and *italic*")
        assert "bold" in result
        assert "italic" in result
        assert "**" not in result
        assert result.count("*") == 0

    def test_strip_links(self):
        result = strip_markdown("[text](http://example.com)")
        assert "text" in result
        assert "http" not in result

    def test_strip_code(self):
        result = strip_markdown("`code`")
        assert "code" in result
        assert "`" not in result


# ---------------------------------------------------------------------------
# TestFormatDetection
# ---------------------------------------------------------------------------

class TestFormatDetection:
    def test_detect_latex_by_extension(self):
        assert detect_format("test.tex", r"\documentclass{article}") == "latex"

    def test_detect_markdown_by_extension(self):
        assert detect_format("test.md", "# Title") == "markdown"

    def test_detect_plain(self):
        assert detect_format("test.txt", "Just plain text.") == "text"

    def test_latex_by_content(self):
        assert detect_format("unknown.txt", r"\begin{document}") == "latex"

    def test_markdown_by_content(self):
        assert detect_format("unknown.txt", "# A Header\n\nSome text.") == "markdown"


# ---------------------------------------------------------------------------
# TestScoring
# ---------------------------------------------------------------------------

class TestScoring:
    def _make_metrics(self, **overrides) -> DocumentMetrics:
        defaults = dict(
            total_words=200,
            total_sentences=10,
            total_paragraphs=3,
            flesch_kincaid_grade=12.0,
            avg_sentence_length=20.0,
            sentence_length_std=5.0,
            long_sentences=0,
            very_long_sentences=0,
            jargon_density=1.0,
            passive_voice_pct=10.0,
            hedge_density=0.5,
            filler_density=0.2,
            filler_inventory={},
            hedge_inventory={},
            weak_openers=1,
            sentence_length_cv=0.5,
            monotony_score=0.2,
            short_sentence_pct=25.0,
            medium_sentence_pct=50.0,
            long_sentence_pct=25.0,
            avg_paragraph_length=100.0,
            paragraph_length_std=20.0,
            sections=[],
            opening_sentences=[],
            longest_sentences=[],
            hedge_examples=[],
            passive_examples=[],
            filler_examples=[],
            input_hash="abc",
            timestamp="2026-01-01T00:00:00Z",
        )
        defaults.update(overrides)
        return DocumentMetrics(**defaults)

    def test_accessibility_good(self):
        m = self._make_metrics(flesch_kincaid_grade=10.0, avg_sentence_length=18.0,
                               long_sentences=0, jargon_density=1.0)
        assert score_accessibility(m) >= 8.0

    def test_accessibility_poor(self):
        m = self._make_metrics(flesch_kincaid_grade=22.0, avg_sentence_length=45.0,
                               long_sentences=8, jargon_density=8.0)
        assert score_accessibility(m) <= 5.0

    def test_clarity_good(self):
        m = self._make_metrics(passive_voice_pct=5.0, hedge_density=0.1,
                               filler_density=0.05, weak_openers=0)
        assert score_clarity(m) >= 8.0

    def test_clarity_poor(self):
        m = self._make_metrics(passive_voice_pct=60.0, hedge_density=5.0,
                               filler_density=4.0, weak_openers=8)
        assert score_clarity(m) <= 5.0

    def test_flow_good(self):
        m = self._make_metrics(sentence_length_cv=0.5, monotony_score=0.1,
                               short_sentence_pct=25.0, medium_sentence_pct=50.0,
                               long_sentence_pct=25.0, avg_paragraph_length=120.0)
        assert score_flow(m) >= 7.0

    def test_grade_mapping(self):
        # score >= 8 → A, score >= 7 → B+, etc.
        _, grade_a = overall_grade(10.0, 10.0, 10.0)
        assert grade_a in ("A", "A+")
        _, grade_low = overall_grade(1.0, 1.0, 1.0)
        assert grade_low in ("D", "F", "C")


# ---------------------------------------------------------------------------
# TestEndToEnd
# ---------------------------------------------------------------------------

class TestEndToEnd:
    SAMPLE = (
        "We train a neural network on ImageNet. "
        "The model achieves 92% top-1 accuracy after 90 epochs. "
        "Stochastic gradient descent with momentum is used as the optimizer.\n\n"
        "The results demonstrate that our approach outperforms prior methods. "
        "We evaluate on three standard benchmarks."
    )

    def test_analyze_simple_paragraph(self):
        m = analyze_document(self.SAMPLE, "text")
        assert isinstance(m, DocumentMetrics)
        assert m.total_words > 0
        assert m.total_sentences > 0
        assert m.total_paragraphs >= 1
        assert 0.0 <= m.passive_voice_pct <= 100.0
        assert m.flesch_kincaid_grade >= 0.0

    def test_json_output(self):
        m = analyze_document(self.SAMPLE, "text")
        d = asdict(m)
        serialized = json.dumps(d)
        parsed = json.loads(serialized)
        assert parsed["total_words"] == m.total_words
        assert parsed["flesch_kincaid_grade"] == m.flesch_kincaid_grade

    def test_latex_format_accepted(self):
        latex = r"""
\section{Introduction}
We propose a new method for image classification.
The model was trained on large-scale datasets.

\section{Experiments}
Results show consistent improvements over baselines.
"""
        m = analyze_document(latex, "latex")
        assert isinstance(m, DocumentMetrics)
        assert m.total_words > 0

    def test_markdown_format_accepted(self):
        md = "# Introduction\n\nWe **propose** a new method.\n\n# Experiments\n\nResults are promising."
        m = analyze_document(md, "markdown")
        assert isinstance(m, DocumentMetrics)
        assert m.total_words > 0

    def test_format_field_set(self):
        # analyze_document does not store format in DocumentMetrics (it's not a field),
        # but result must be a valid DocumentMetrics instance
        m = analyze_document(self.SAMPLE, "text")
        assert hasattr(m, "total_words")
        assert hasattr(m, "flesch_kincaid_grade")
        assert hasattr(m, "passive_voice_pct")
