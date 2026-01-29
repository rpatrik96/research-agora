#!/usr/bin/env python3
"""
LaTeX Parser for Research State Generation

Extracts structural elements from LaTeX source files:
- Sections and subsections
- Figures with captions
- Tables with captions
- Equations with labels
- Algorithms
- Theorems, lemmas, propositions
- Citations/bibliography

Usage:
    python parse_latex.py paper.tex [--output research-state.json]
    python parse_latex.py paper_dir/ [--output research-state.json]
"""

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class Section:
    id: str
    title: str
    level: int
    start_line: int
    end_line: int = 0
    word_count: int = 0
    summary: str = ""


@dataclass
class Figure:
    id: str
    caption: str
    section: str = ""
    referenced_by: list = field(default_factory=list)


@dataclass
class Table:
    id: str
    caption: str
    section: str = ""
    columns: list = field(default_factory=list)
    row_count: int = 0
    has_error_bars: bool = False
    referenced_by: list = field(default_factory=list)


@dataclass
class Equation:
    id: str
    label: Optional[str]
    section: str = ""
    latex: str = ""


@dataclass
class Algorithm:
    id: str
    caption: str = ""
    section: str = ""


@dataclass
class Theorem:
    id: str
    type: str  # theorem, lemma, proposition, corollary, definition
    statement: str = ""
    section: str = ""
    has_proof: bool = False


@dataclass
class Citation:
    key: str
    title: str = ""
    authors: str = ""
    year: Optional[int] = None
    venue: str = ""
    arxiv_id: Optional[str] = None
    doi: Optional[str] = None


class LaTeXParser:
    """Parser for extracting structural elements from LaTeX source."""

    def __init__(self, content: str, source_path: str):
        self.content = content
        self.lines = content.split("\n")
        self.source_path = source_path

        # Counters for generating IDs
        self.fig_counter = 0
        self.tab_counter = 0
        self.eq_counter = 0
        self.alg_counter = 0
        self.thm_counter = 0
        self.lem_counter = 0
        self.prop_counter = 0
        self.cor_counter = 0
        self.sec_counters = [0, 0, 0, 0]  # section, subsection, subsubsection, paragraph

        # Parsed elements
        self.sections: list[Section] = []
        self.figures: list[Figure] = []
        self.tables: list[Table] = []
        self.equations: list[Equation] = []
        self.algorithms: list[Algorithm] = []
        self.theorems: list[Theorem] = []
        self.citations: list[Citation] = []

        # Current section tracking
        self.current_section = ""

    def compute_hash(self) -> str:
        """Compute SHA256 hash of content."""
        return hashlib.sha256(self.content.encode("utf-8")).hexdigest()

    def extract_title(self) -> str:
        """Extract paper title from \\title{...}."""
        match = re.search(r"\\title\s*\{([^}]+)\}", self.content, re.DOTALL)
        if match:
            title = match.group(1)
            # Clean up LaTeX commands
            title = re.sub(r"\\[a-zA-Z]+\s*", "", title)
            title = re.sub(r"\s+", " ", title).strip()
            return title
        return "Untitled"

    def count_words(self, text: str) -> int:
        """Count words in text, excluding LaTeX commands."""
        # Remove LaTeX commands
        text = re.sub(r"\\[a-zA-Z]+\*?\s*(\[[^\]]*\])?\s*(\{[^}]*\})?", " ", text)
        # Remove math mode
        text = re.sub(r"\$[^$]+\$", " ", text)
        text = re.sub(r"\\\[[^\]]+\\\]", " ", text)
        # Count words
        words = re.findall(r"\b[a-zA-Z]+\b", text)
        return len(words)

    def parse_sections(self) -> None:
        """Parse section structure."""
        section_pattern = re.compile(
            r"\\(section|subsection|subsubsection|paragraph)\*?\s*\{([^}]+)\}"
        )

        # Handle abstract separately
        abstract_match = re.search(
            r"\\begin\{abstract\}(.*?)\\end\{abstract\}",
            self.content,
            re.DOTALL,
        )
        if abstract_match:
            start_line = self.content[: abstract_match.start()].count("\n") + 1
            end_line = self.content[: abstract_match.end()].count("\n") + 1
            abstract_text = abstract_match.group(1)
            self.sections.append(
                Section(
                    id="abstract",
                    title="Abstract",
                    level=0,
                    start_line=start_line,
                    end_line=end_line,
                    word_count=self.count_words(abstract_text),
                )
            )

        current_positions = []  # Stack of (section, start_pos)

        for match in section_pattern.finditer(self.content):
            sec_type = match.group(1)
            title = match.group(2).strip()
            start_line = self.content[: match.start()].count("\n") + 1

            level_map = {"section": 1, "subsection": 2, "subsubsection": 3, "paragraph": 4}
            level = level_map.get(sec_type, 1)

            # Update counters
            if level == 1:
                self.sec_counters[0] += 1
                self.sec_counters[1:] = [0, 0, 0]
                sec_id = f"sec{self.sec_counters[0]}"
            elif level == 2:
                self.sec_counters[1] += 1
                self.sec_counters[2:] = [0, 0]
                sec_id = f"sec{self.sec_counters[0]}.{self.sec_counters[1]}"
            elif level == 3:
                self.sec_counters[2] += 1
                self.sec_counters[3] = 0
                sec_id = f"sec{self.sec_counters[0]}.{self.sec_counters[1]}.{self.sec_counters[2]}"
            else:
                self.sec_counters[3] += 1
                c = self.sec_counters
                sec_id = f"sec{c[0]}.{c[1]}.{c[2]}.{c[3]}"

            # Close previous sections at same or higher level
            while current_positions and current_positions[-1][0].level >= level:
                prev_section, prev_start = current_positions.pop()
                prev_section.end_line = start_line - 1
                # Calculate word count
                section_text = "\n".join(
                    self.lines[prev_section.start_line - 1 : prev_section.end_line]
                )
                prev_section.word_count = self.count_words(section_text)

            section = Section(
                id=sec_id,
                title=title,
                level=level,
                start_line=start_line,
            )
            self.sections.append(section)
            current_positions.append((section, match.end()))
            self.current_section = sec_id

        # Close remaining open sections
        total_lines = len(self.lines)
        while current_positions:
            section, _ = current_positions.pop()
            section.end_line = total_lines
            section_text = "\n".join(self.lines[section.start_line - 1 : section.end_line])
            section.word_count = self.count_words(section_text)

    def parse_figures(self) -> None:
        """Parse figure environments."""
        figure_pattern = re.compile(
            r"\\begin\{figure\*?\}(.*?)\\end\{figure\*?\}",
            re.DOTALL,
        )

        for match in figure_pattern.finditer(self.content):
            self.fig_counter += 1
            fig_content = match.group(1)

            # Extract caption
            caption_match = re.search(r"\\caption\s*\{([^}]+)\}", fig_content)
            caption = caption_match.group(1).strip() if caption_match else ""

            # Determine section
            pos = match.start()
            section = self._find_section_at_pos(pos)

            self.figures.append(
                Figure(
                    id=f"fig{self.fig_counter}",
                    caption=caption,
                    section=section,
                )
            )

    def parse_tables(self) -> None:
        """Parse table environments."""
        table_pattern = re.compile(
            r"\\begin\{table\*?\}(.*?)\\end\{table\*?\}",
            re.DOTALL,
        )

        for match in table_pattern.finditer(self.content):
            self.tab_counter += 1
            tab_content = match.group(1)

            # Extract caption
            caption_match = re.search(r"\\caption\s*\{([^}]+)\}", tab_content)
            caption = caption_match.group(1).strip() if caption_match else ""

            # Check for error bars (± or \pm)
            has_error_bars = "±" in tab_content or r"\pm" in tab_content

            # Count rows in tabular
            row_count = tab_content.count(r"\\") - tab_content.count(r"\\hline")

            # Extract column headers from tabular
            tabular_match = re.search(r"\\begin\{tabular\}\{([^}]+)\}", tab_content)
            columns = []
            if tabular_match:
                col_spec = tabular_match.group(1)
                # Simple column count from l, c, r, p
                columns = re.findall(r"[lcr]|p\{[^}]+\}", col_spec)

            section = self._find_section_at_pos(match.start())

            self.tables.append(
                Table(
                    id=f"tab{self.tab_counter}",
                    caption=caption,
                    section=section,
                    columns=columns,
                    row_count=max(1, row_count),
                    has_error_bars=has_error_bars,
                )
            )

    def parse_equations(self) -> None:
        """Parse labeled equations."""
        # equation environment
        eq_pattern = re.compile(
            r"\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}",
            re.DOTALL,
        )

        for match in eq_pattern.finditer(self.content):
            self.eq_counter += 1
            eq_content = match.group(1).strip()

            label_match = re.search(r"\\label\{([^}]+)\}", eq_content)
            label = label_match.group(1) if label_match else None

            # Remove label from latex
            latex = re.sub(r"\\label\{[^}]+\}", "", eq_content).strip()

            section = self._find_section_at_pos(match.start())

            self.equations.append(
                Equation(
                    id=f"eq{self.eq_counter}",
                    label=label,
                    section=section,
                    latex=latex,
                )
            )

        # Also parse align environments
        align_pattern = re.compile(
            r"\\begin\{align\*?\}(.*?)\\end\{align\*?\}",
            re.DOTALL,
        )

        for match in align_pattern.finditer(self.content):
            # Each line in align can be a separate equation
            align_content = match.group(1)
            labels = re.findall(r"\\label\{([^}]+)\}", align_content)

            for label in labels:
                self.eq_counter += 1
                section = self._find_section_at_pos(match.start())
                self.equations.append(
                    Equation(
                        id=f"eq{self.eq_counter}",
                        label=label,
                        section=section,
                        latex="",  # Full align block
                    )
                )

    def parse_algorithms(self) -> None:
        """Parse algorithm environments."""
        alg_patterns = [
            r"\\begin\{algorithm\*?\}(.*?)\\end\{algorithm\*?\}",
            r"\\begin\{algorithmic\}(.*?)\\end\{algorithmic\}",
        ]

        for pattern in alg_patterns:
            for match in re.finditer(pattern, self.content, re.DOTALL):
                self.alg_counter += 1
                alg_content = match.group(1)

                caption_match = re.search(r"\\caption\s*\{([^}]+)\}", alg_content)
                caption = caption_match.group(1).strip() if caption_match else ""

                section = self._find_section_at_pos(match.start())

                self.algorithms.append(
                    Algorithm(
                        id=f"alg{self.alg_counter}",
                        caption=caption,
                        section=section,
                    )
                )

    def parse_theorems(self) -> None:
        """Parse theorem-like environments."""
        theorem_types = {
            "theorem": ("thm", "thm_counter"),
            "lemma": ("lem", "lem_counter"),
            "proposition": ("prop", "prop_counter"),
            "corollary": ("cor", "cor_counter"),
            "definition": ("def", "def_counter"),
        }

        for thm_type, (prefix, _) in theorem_types.items():
            pattern = re.compile(
                rf"\\begin\{{{thm_type}\}}(.*?)\\end\{{{thm_type}\}}",
                re.DOTALL,
            )

            counter = 0
            for match in pattern.finditer(self.content):
                counter += 1
                content = match.group(1).strip()

                # Check for proof
                proof_start = match.end()
                proof_text = self.content[proof_start : proof_start + 500]
                has_proof = r"\begin{proof}" in proof_text

                section = self._find_section_at_pos(match.start())

                self.theorems.append(
                    Theorem(
                        id=f"{prefix}{counter}",
                        type=thm_type,
                        statement=content[:500],  # Truncate long statements
                        section=section,
                        has_proof=has_proof,
                    )
                )

    def parse_citations(self) -> None:
        """Parse bibliography entries."""
        # Parse .bib style entries
        bibitem_pattern = re.compile(
            r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}(.*?)(?=\\bibitem|\\end\{thebibliography\})",
            re.DOTALL,
        )

        for match in bibitem_pattern.finditer(self.content):
            key = match.group(1)
            entry = match.group(2).strip()

            # Try to extract structured info
            self.citations.append(
                Citation(
                    key=key,
                    title=entry[:200] if entry else "",
                )
            )

        # Also try to find \cite{} references for keys we haven't seen
        cite_pattern = re.compile(r"\\cite[pt]?\{([^}]+)\}")
        cited_keys = set()
        for match in cite_pattern.finditer(self.content):
            keys = match.group(1).split(",")
            for k in keys:
                cited_keys.add(k.strip())

        existing_keys = {c.key for c in self.citations}
        for key in cited_keys - existing_keys:
            self.citations.append(Citation(key=key))

    def _find_section_at_pos(self, pos: int) -> str:
        """Find which section a position falls into."""
        line_num = self.content[:pos].count("\n") + 1

        for section in reversed(self.sections):
            if section.start_line <= line_num:
                if section.end_line == 0 or section.end_line >= line_num:
                    return section.id
        return ""

    def parse_all(self) -> dict:
        """Parse all elements and return research state dict."""
        self.parse_sections()
        self.parse_figures()
        self.parse_tables()
        self.parse_equations()
        self.parse_algorithms()
        self.parse_theorems()
        self.parse_citations()

        return {
            "metadata": {
                "title": self.extract_title(),
                "arxiv_id": None,
                "venue_target": "other",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "source_path": self.source_path,
                "source_hash": self.compute_hash(),
                "word_count": self.count_words(self.content),
                "page_count": max(1, self.count_words(self.content) // 800),
            },
            "structure": {
                "sections": [
                    {
                        "id": s.id,
                        "title": s.title,
                        "level": s.level,
                        "start_line": s.start_line,
                        "end_line": s.end_line,
                        "word_count": s.word_count,
                    }
                    for s in self.sections
                ],
                "figures": [
                    {
                        "id": f.id,
                        "caption": f.caption,
                        "section": f.section,
                        "referenced_by": f.referenced_by,
                    }
                    for f in self.figures
                ],
                "tables": [
                    {
                        "id": t.id,
                        "caption": t.caption,
                        "section": t.section,
                        "columns": t.columns,
                        "row_count": t.row_count,
                        "has_error_bars": t.has_error_bars,
                        "referenced_by": t.referenced_by,
                    }
                    for t in self.tables
                ],
                "equations": [
                    {
                        "id": e.id,
                        "label": e.label,
                        "section": e.section,
                        "latex": e.latex,
                    }
                    for e in self.equations
                ],
                "algorithms": [
                    {
                        "id": a.id,
                        "caption": a.caption,
                        "section": a.section,
                    }
                    for a in self.algorithms
                ],
                "theorems": [
                    {
                        "id": t.id,
                        "type": t.type,
                        "statement": t.statement,
                        "section": t.section,
                        "has_proof": t.has_proof,
                    }
                    for t in self.theorems
                ],
            },
            "claims": [],  # Claims require LLM extraction
            "evidence_map": {},
            "citations": [
                {
                    "key": c.key,
                    "title": c.title,
                    "authors": c.authors,
                    "year": c.year,
                    "venue": c.venue,
                    "arxiv_id": c.arxiv_id,
                    "doi": c.doi,
                }
                for c in self.citations
            ],
            "terminology": {},
            "assumptions": [],
            "processing_log": [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "agent": "parse_latex.py",
                    "action": "structure_extraction",
                    "details": {
                        "sections": len(self.sections),
                        "figures": len(self.figures),
                        "tables": len(self.tables),
                        "equations": len(self.equations),
                        "algorithms": len(self.algorithms),
                        "theorems": len(self.theorems),
                        "citations": len(self.citations),
                    },
                }
            ],
        }


def find_main_tex(directory: Path) -> Optional[Path]:
    """Find the main .tex file in a directory."""
    tex_files = list(directory.glob("*.tex"))

    if not tex_files:
        return None

    # Prefer files with common main file names
    main_names = ["main.tex", "paper.tex", "article.tex", "manuscript.tex"]
    for name in main_names:
        main_file = directory / name
        if main_file.exists():
            return main_file

    # Look for file with \documentclass
    for tex_file in tex_files:
        content = tex_file.read_text(errors="ignore")
        if r"\documentclass" in content:
            return tex_file

    # Fall back to first .tex file
    return tex_files[0]


def resolve_inputs(main_tex: Path, content: str) -> str:
    """Resolve \\input{} and \\include{} commands."""
    input_pattern = re.compile(r"\\(?:input|include)\{([^}]+)\}")

    def replace_input(match: re.Match) -> str:
        filename = match.group(1)
        if not filename.endswith(".tex"):
            filename += ".tex"

        input_path = main_tex.parent / filename
        if input_path.exists():
            return input_path.read_text(errors="ignore")
        return match.group(0)  # Keep original if file not found

    # Resolve up to 3 levels of nesting
    for _ in range(3):
        new_content = input_pattern.sub(replace_input, content)
        if new_content == content:
            break
        content = new_content

    return content


def main():
    parser = argparse.ArgumentParser(
        description="Parse LaTeX files and extract structure for research state"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="LaTeX file or directory containing .tex files",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Output JSON file (default: research-state.json in input directory)",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force regeneration even if cache exists",
    )

    args = parser.parse_args()

    # Find input file
    if args.input.is_dir():
        main_tex = find_main_tex(args.input)
        if not main_tex:
            print(f"Error: No .tex files found in {args.input}", file=sys.stderr)
            sys.exit(1)
    elif args.input.exists():
        main_tex = args.input
    else:
        print(f"Error: {args.input} not found", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = main_tex.parent / "research-state.json"

    # Check cache
    if output_path.exists() and not args.force:
        existing = json.loads(output_path.read_text())
        content = main_tex.read_text(errors="ignore")
        current_hash = hashlib.sha256(content.encode()).hexdigest()

        if existing.get("metadata", {}).get("source_hash") == current_hash:
            print(f"Cache hit: {output_path} is up to date")
            print(json.dumps(existing, indent=2))
            return

    # Parse
    print(f"Parsing {main_tex}...", file=sys.stderr)
    content = main_tex.read_text(errors="ignore")

    # Resolve includes
    content = resolve_inputs(main_tex, content)

    parser_obj = LaTeXParser(content, str(main_tex))
    result = parser_obj.parse_all()

    # Write output
    output_path.write_text(json.dumps(result, indent=2))
    print(f"Wrote {output_path}", file=sys.stderr)

    # Print summary
    structure = result["structure"]
    print(
        "\nExtracted:",
        f"\n  Sections: {len(structure['sections'])}",
        f"\n  Figures: {len(structure['figures'])}",
        f"\n  Tables: {len(structure['tables'])}",
        f"\n  Equations: {len(structure['equations'])}",
        f"\n  Algorithms: {len(structure['algorithms'])}",
        f"\n  Theorems: {len(structure['theorems'])}",
        f"\n  Citations: {len(result['citations'])}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
