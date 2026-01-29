"""Tests for research state generation and LaTeX parsing."""

import json
import sys
from pathlib import Path

import pytest

# Add the project root to sys.path for importing scripts
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestLatexParser:
    """Tests for the LaTeX parser script."""

    @pytest.fixture
    def sample_latex(self, tmp_path: Path) -> Path:
        """Create a sample LaTeX file for testing."""
        content = r"""
\documentclass{article}
\title{Test Paper: A Novel Approach}
\author{Test Author}

\begin{document}

\begin{abstract}
We propose a novel method that achieves 95\% accuracy.
This is the first approach to solve this problem efficiently.
\end{abstract}

\section{Introduction}
Deep learning has revolutionized machine learning.
We show that our method outperforms baselines.

\section{Methodology}
\subsection{Model Architecture}
Our model uses attention mechanisms.

\begin{equation}
\label{eq:attention}
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
\end{equation}

\subsection{Training}
We train using Adam optimizer.

\begin{algorithm}
\caption{Training Procedure}
\begin{algorithmic}
\STATE Initialize weights
\FOR{epoch in epochs}
\STATE Update weights
\ENDFOR
\end{algorithmic}
\end{algorithm}

\section{Experiments}

\begin{table}[h]
\caption{Main results on benchmark datasets}
\begin{tabular}{lcc}
Method & Accuracy & F1 \\
\hline
Baseline & 90.0 ± 0.5 & 88.0 \\
Ours & 95.0 ± 0.3 & 93.5 \\
\end{tabular}
\end{table}

\begin{figure}[h]
\caption{Model architecture overview}
\includegraphics{architecture.pdf}
\end{figure}

Table 1 shows our results. Our method achieves 95\% accuracy.

\section{Conclusion}
We presented a novel approach.

\begin{thebibliography}{9}
\bibitem{vaswani2017} Vaswani et al. Attention Is All You Need. NeurIPS 2017.
\end{thebibliography}

\end{document}
"""
        paper_file = tmp_path / "paper.tex"
        paper_file.write_text(content)
        return paper_file

    def test_parser_extracts_title(self, sample_latex: Path) -> None:
        """Parser should extract paper title."""
        from scripts.parse_latex import LaTeXParser

        content = sample_latex.read_text()
        parser = LaTeXParser(content, str(sample_latex))
        result = parser.parse_all()

        assert result["metadata"]["title"] == "Test Paper: A Novel Approach"

    def test_parser_extracts_sections(self, sample_latex: Path) -> None:
        """Parser should extract all sections and subsections."""
        from scripts.parse_latex import LaTeXParser

        content = sample_latex.read_text()
        parser = LaTeXParser(content, str(sample_latex))
        result = parser.parse_all()

        sections = result["structure"]["sections"]
        section_titles = [s["title"] for s in sections]

        assert "Abstract" in section_titles
        assert "Introduction" in section_titles
        assert "Methodology" in section_titles
        assert "Model Architecture" in section_titles
        assert "Experiments" in section_titles
        assert "Conclusion" in section_titles

    def test_parser_extracts_tables(self, sample_latex: Path) -> None:
        """Parser should extract tables with captions."""
        from scripts.parse_latex import LaTeXParser

        content = sample_latex.read_text()
        parser = LaTeXParser(content, str(sample_latex))
        result = parser.parse_all()

        tables = result["structure"]["tables"]
        assert len(tables) == 1
        assert "Main results" in tables[0]["caption"]
        assert tables[0]["has_error_bars"] is True  # Contains ±

    def test_parser_extracts_figures(self, sample_latex: Path) -> None:
        """Parser should extract figures with captions."""
        from scripts.parse_latex import LaTeXParser

        content = sample_latex.read_text()
        parser = LaTeXParser(content, str(sample_latex))
        result = parser.parse_all()

        figures = result["structure"]["figures"]
        assert len(figures) == 1
        assert "architecture" in figures[0]["caption"].lower()

    def test_parser_extracts_equations(self, sample_latex: Path) -> None:
        """Parser should extract labeled equations."""
        from scripts.parse_latex import LaTeXParser

        content = sample_latex.read_text()
        parser = LaTeXParser(content, str(sample_latex))
        result = parser.parse_all()

        equations = result["structure"]["equations"]
        assert len(equations) >= 1
        assert any(e["label"] == "eq:attention" for e in equations)

    def test_parser_extracts_algorithms(self, sample_latex: Path) -> None:
        """Parser should extract algorithm blocks."""
        from scripts.parse_latex import LaTeXParser

        content = sample_latex.read_text()
        parser = LaTeXParser(content, str(sample_latex))
        result = parser.parse_all()

        algorithms = result["structure"]["algorithms"]
        assert len(algorithms) >= 1

    def test_parser_extracts_citations(self, sample_latex: Path) -> None:
        """Parser should extract bibliography entries."""
        from scripts.parse_latex import LaTeXParser

        content = sample_latex.read_text()
        parser = LaTeXParser(content, str(sample_latex))
        result = parser.parse_all()

        citations = result["citations"]
        assert len(citations) >= 1
        assert any("vaswani" in c["key"].lower() for c in citations)

    def test_parser_computes_hash(self, sample_latex: Path) -> None:
        """Parser should compute consistent SHA256 hash."""
        from scripts.parse_latex import LaTeXParser

        content = sample_latex.read_text()
        parser1 = LaTeXParser(content, str(sample_latex))
        parser2 = LaTeXParser(content, str(sample_latex))

        assert parser1.compute_hash() == parser2.compute_hash()
        assert len(parser1.compute_hash()) == 64  # SHA256 hex length

    def test_parser_counts_words(self, sample_latex: Path) -> None:
        """Parser should count words excluding LaTeX commands."""
        from scripts.parse_latex import LaTeXParser

        content = sample_latex.read_text()
        parser = LaTeXParser(content, str(sample_latex))
        result = parser.parse_all()

        # Should have reasonable word count
        assert result["metadata"]["word_count"] > 50
        assert result["metadata"]["word_count"] < 10000

    def test_parser_section_hierarchy(self, sample_latex: Path) -> None:
        """Parser should correctly identify section hierarchy."""
        from scripts.parse_latex import LaTeXParser

        content = sample_latex.read_text()
        parser = LaTeXParser(content, str(sample_latex))
        result = parser.parse_all()

        sections = result["structure"]["sections"]

        # Find methodology and its subsections
        methodology = next((s for s in sections if s["title"] == "Methodology"), None)
        model_arch = next(
            (s for s in sections if s["title"] == "Model Architecture"), None
        )

        assert methodology is not None
        assert model_arch is not None
        assert methodology["level"] == 1
        assert model_arch["level"] == 2


class TestResearchStateSchema:
    """Tests for research state schema validation."""

    @pytest.fixture
    def schema(self) -> dict:
        """Load the research state schema."""
        schema_path = Path("schemas/research-state.schema.json")
        if not schema_path.exists():
            pytest.skip("Schema file not found")
        return json.loads(schema_path.read_text())

    def test_schema_is_valid_json_schema(self, schema: dict) -> None:
        """Schema should be valid JSON Schema draft-07."""
        assert schema.get("$schema") == "http://json-schema.org/draft-07/schema#"
        assert "title" in schema
        assert "properties" in schema

    def test_schema_requires_core_fields(self, schema: dict) -> None:
        """Schema should require metadata, structure, and claims."""
        assert "required" in schema
        assert "metadata" in schema["required"]
        assert "structure" in schema["required"]
        assert "claims" in schema["required"]

    def test_claim_schema_structure(self, schema: dict) -> None:
        """Claim schema should have proper structure."""
        claims_schema = schema["properties"]["claims"]["items"]

        assert "id" in claims_schema["properties"]
        assert "text" in claims_schema["properties"]
        assert "type" in claims_schema["properties"]
        assert "location" in claims_schema["properties"]

        # Check claim types enum
        type_enum = claims_schema["properties"]["type"]["enum"]
        assert "empirical" in type_enum
        assert "theoretical" in type_enum
        assert "novelty" in type_enum


class TestStateGeneratorIntegration:
    """Integration tests for state generator with LaTeX parser."""

    @pytest.fixture
    def complex_paper(self, tmp_path: Path) -> Path:
        """Create a more complex paper for integration testing."""
        content = r"""
\documentclass{article}
\title{Transformers for Everything: A Comprehensive Study}
\author{Alice Smith and Bob Jones}

\begin{document}

\begin{abstract}
We present TransEverything, a novel transformer architecture that achieves
state-of-the-art results on 10 benchmarks. Our key contribution is a new
attention mechanism that runs in O(n) time complexity. Experiments show
a 15\% improvement over BERT on GLUE tasks.
\end{abstract}

\section{Introduction}
Large language models have transformed NLP \cite{devlin2019bert}.
We propose TransEverything, the first unified transformer for all tasks.

\section{Related Work}
BERT \cite{devlin2019bert} introduced bidirectional pretraining.
GPT-3 \cite{brown2020gpt3} showed the power of scale.

\section{Method}

\begin{theorem}
Under Assumptions 1-3, our attention mechanism computes exact attention
in O(n) time.
\end{theorem}

\begin{proof}
We prove by construction...
\end{proof}

\section{Experiments}

\begin{table}[h]
\caption{Results on GLUE benchmark}
\label{tab:glue}
\begin{tabular}{lccccc}
Model & MNLI & QQP & SST-2 & Avg \\
\hline
BERT & 84.6 ± 0.2 & 91.1 ± 0.1 & 93.5 ± 0.3 & 89.7 \\
Ours & 87.2 ± 0.3 & 92.3 ± 0.2 & 95.1 ± 0.2 & 91.5 \\
\end{tabular}
\end{table}

As shown in Table~\ref{tab:glue}, our method achieves 91.5\% average score.

\section{Conclusion}
We presented TransEverything with O(n) attention.

\end{document}
"""
        paper_file = tmp_path / "paper.tex"
        paper_file.write_text(content)
        return paper_file

    def test_full_parsing_pipeline(self, complex_paper: Path) -> None:
        """Test complete parsing pipeline produces valid state."""
        from scripts.parse_latex import LaTeXParser

        content = complex_paper.read_text()
        parser = LaTeXParser(content, str(complex_paper))
        result = parser.parse_all()

        # Check metadata
        assert "Transformers" in result["metadata"]["title"]
        assert result["metadata"]["source_hash"]

        # Check structure
        assert len(result["structure"]["sections"]) >= 5
        assert len(result["structure"]["tables"]) == 1
        assert len(result["structure"]["theorems"]) >= 1

        # Check citations
        assert len(result["citations"]) >= 2

        # Check processing log
        assert len(result["processing_log"]) == 1
        assert result["processing_log"][0]["agent"] == "parse_latex.py"

    def test_caching_behavior(self, complex_paper: Path, tmp_path: Path) -> None:
        """Test that caching works correctly."""
        import subprocess

        # First run - should generate
        subprocess.run(
            [sys.executable, "scripts/parse_latex.py", str(complex_paper)],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
            check=True,
        )

        state_file = complex_paper.parent / "research-state.json"
        assert state_file.exists()

        # Second run - should use cache
        result2 = subprocess.run(
            [sys.executable, "scripts/parse_latex.py", str(complex_paper)],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        assert "Cache hit" in result2.stdout or "up to date" in result2.stdout

        # Force regeneration
        result3 = subprocess.run(
            [sys.executable, "scripts/parse_latex.py", str(complex_paper), "--force"],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        assert "Parsing" in result3.stderr or "Wrote" in result3.stderr
