#!/usr/bin/env python3
"""Compile a LaTeX project with latexmk and prove the PDF on disk is fresh.

A build that exits 0 is not a build that produced a new PDF. latexmk skips work
when it believes nothing changed, `-outdir` sends output somewhere other than the
source directory, and picking the wrong root file compiles a document nobody
asked for. Each of those returns success while leaving a stale PDF in place, so
this script compares the PDF's mtime against every file the build actually read
and reports `fresh: false` when the PDF did not move.

Usage:
    python build_latex.py paper.tex
    python build_latex.py paper_dir/ --engine xelatex --json
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Engine mapping
# ---------------------------------------------------------------------------

ENGINE_FLAGS = {
    "pdflatex": "-pdf",
    "xelatex": "-pdfxe",
    "lualatex": "-pdflua",
}

# Packages whose entries need a separate makeglossaries pass unless the document
# loads them with the `automake` option (which makes latexmk handle it).
GLOSSARY_PACKAGES = ("glossaries", "acronym", "glossaries-extra")

SOURCE_SUFFIXES = {".tex", ".bib", ".sty", ".cls", ".bst", ".bbx", ".cbx"}

# Directories that never hold hand-edited sources.
SKIP_DIRS = {".git", ".github", "node_modules", "__pycache__", ".venv", "venv"}


@dataclass
class BuildResult:
    """Everything a caller needs to decide whether the build really happened."""

    root: str
    engine: str
    exit_code: int
    pdf_path: Optional[str] = None
    pdf_mtime: Optional[float] = None
    newest_dep: Optional[str] = None
    newest_dep_mtime: Optional[float] = None
    fresh: bool = False
    pages: Optional[int] = None
    glossary_pass: bool = False
    dep_source: str = "none"
    errors: list = field(default_factory=list)
    undefined_refs: list = field(default_factory=list)
    undefined_cites: list = field(default_factory=list)
    rerun_limit_hit: bool = False
    warnings: list = field(default_factory=list)
    diagnosis: Optional[str] = None


# ---------------------------------------------------------------------------
# Root detection
# ---------------------------------------------------------------------------


def _iter_tex_files(directory: Path):
    for path in sorted(directory.rglob("*.tex")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def _included_names(text: str) -> set:
    """Names pulled in by \\input / \\include / \\subfile, without extension."""
    names = set()
    for match in re.finditer(r"\\(?:input|include|subfile)\s*\{([^}]*)\}", text):
        raw = match.group(1).strip()
        if raw:
            names.add(Path(raw).with_suffix("").name)
    return names


def detect_root(target: Path) -> Optional[Path]:
    """Return the .tex file that owns the document.

    A root declares \\documentclass and is not itself pulled in by another file.
    Standalone figure sources declare \\documentclass too, which is why the
    inclusion check matters.
    """
    if target.is_file():
        return target

    candidates = []
    included = set()
    for path in _iter_tex_files(target):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        included |= _included_names(text)
        if re.search(r"^\s*\\documentclass", text, re.MULTILINE):
            candidates.append(path)

    roots = [c for c in candidates if c.with_suffix("").name not in included]
    if not roots:
        roots = candidates
    if not roots:
        return None
    # A \documentclass{standalone} file is a TikZ figure, not the paper. Drop
    # those unless nothing else is left.
    non_standalone = [
        c
        for c in roots
        if not re.search(
            r"\\documentclass\s*(?:\[[^\]]*\])?\s*\{standalone\}",
            c.read_text(encoding="utf-8", errors="replace"),
        )
    ]
    if non_standalone:
        roots = non_standalone
    if len(roots) == 1:
        return roots[0]
    # Prefer a root at the top level, then the conventional names.
    roots.sort(key=lambda p: (len(p.relative_to(target).parts), p.name))
    for preferred in ("main.tex", "paper.tex"):
        for candidate in roots:
            if candidate.name == preferred:
                return candidate
    return roots[0]


# ---------------------------------------------------------------------------
# Output directory
# ---------------------------------------------------------------------------


def resolve_out_dir(root: Path) -> Path:
    """Honour `$out_dir` in a .latexmkrc so freshness is checked on the real PDF."""
    for rc_name in (".latexmkrc", "latexmkrc"):
        rc = root.parent / rc_name
        if not rc.is_file():
            continue
        try:
            text = rc.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        match = re.search(
            r"^\s*\$out_dir\s*=\s*[\"']([^\"']+)[\"']", text, re.MULTILINE
        )
        if match:
            return (root.parent / match.group(1)).resolve()
    return root.parent.resolve()


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------


def deps_from_fls(fls: Path, project_root: Path) -> list:
    """Read the files latexmk recorded as INPUT during the build.

    This beats globbing every .tex in the tree: a source file that is present but
    never \\input would otherwise look like a dependency and report a false stale.
    """
    try:
        lines = fls.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []

    # Relative INPUT paths are relative to the PWD header, which is the directory
    # latexmk ran in — not the directory holding the .fls. They differ whenever
    # -outdir is in play.
    base = fls.parent
    for line in lines:
        if line.startswith("PWD "):
            candidate_base = Path(line[4:].strip())
            if candidate_base.is_dir():
                base = candidate_base
            break

    deps = []
    for line in lines:
        if not line.startswith("INPUT "):
            continue
        candidate = Path(line[6:].strip())
        if not candidate.is_absolute():
            candidate = (base / candidate).resolve()
        if candidate.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        if not candidate.is_file():
            continue
        try:
            candidate.relative_to(project_root)
        except ValueError:
            continue  # TeX distribution file, not a project source
        deps.append(candidate)
    return sorted(set(deps))


def deps_from_glob(project_root: Path) -> list:
    deps = []
    for suffix in SOURCE_SUFFIXES:
        for path in project_root.rglob(f"*{suffix}"):
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            deps.append(path)
    return sorted(set(deps))


def newest(paths: list):
    best, best_mtime = None, -1.0
    for path in paths:
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        if mtime > best_mtime:
            best, best_mtime = path, mtime
    return best, best_mtime


# ---------------------------------------------------------------------------
# Log parsing
# ---------------------------------------------------------------------------


def parse_log(log_path: Path) -> dict:
    """Extract evidence from the log. Classification is deliberately not done here.

    The skill hands these verbatim lines to the reader (or to latex-debugger);
    inventing an error taxonomy in two places is how the two drift apart.
    """
    out = {
        "errors": [],
        "undefined_refs": [],
        "undefined_cites": [],
        "pages": None,
        "rerun_limit_hit": False,
        "warnings": [],
    }
    try:
        text = log_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return out

    lines = text.splitlines()
    seen = set()
    for index, line in enumerate(lines):
        # With -file-line-error the compiler writes "./main.tex:4: message" and
        # drops the leading "!", so matching only "!" misses every real error.
        file_line = re.match(
            r"^(\.?/?[^:\s][^:]*\.(?:tex|sty|cls|bib)):(\d+):\s*(.+)$", line
        )
        if file_line:
            entry = {
                "file": file_line.group(1),
                "line": int(file_line.group(2)),
                "text": file_line.group(3).strip(),
            }
        elif line.startswith("!"):
            # Without -file-line-error, "l.42 \foo" a few lines down carries it.
            source_line = None
            for follow in lines[index : index + 6]:
                match = re.match(r"^l\.(\d+)", follow)
                if match:
                    source_line = int(match.group(1))
                    break
            entry = {
                "file": str(log_path.name),
                "line": source_line,
                "text": line.lstrip("! ").strip(),
            }
        else:
            continue

        key = (entry["file"], entry["line"], entry["text"])
        if key not in seen:
            seen.add(key)
            out["errors"].append(entry)

    out["undefined_refs"] = sorted(
        set(re.findall(r"Reference `([^']+)' on page \d+ undefined", text))
    )
    out["undefined_cites"] = sorted(
        set(re.findall(r"Citation `([^']+)' on page \d+ undefined", text))
    )

    pages = re.findall(r"Output written on .*?\((\d+) pages?", text)
    if pages:
        out["pages"] = int(pages[-1])

    if "Rerun to get" in text:
        out["rerun_limit_hit"] = True
    if re.search(r"^! *LaTeX Error", text, re.MULTILINE):
        out["warnings"].append("LaTeX Error present in log")
    if "Overfull \\hbox" in text:
        out["warnings"].append("overfull hbox warnings present")

    return out


def needs_glossary_pass(root: Path) -> bool:
    try:
        text = root.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    for package in GLOSSARY_PACKAGES:
        match = re.search(
            r"\\usepackage\s*(?:\[([^\]]*)\])?\s*\{[^}]*\b"
            + re.escape(package)
            + r"\b[^}]*\}",
            text,
        )
        if match:
            options = match.group(1) or ""
            if "automake" not in options:
                return True
    return False


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def run(cmd: list, cwd: Path, timeout: int):
    try:
        proc = subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return 124, "", f"timed out after {timeout}s"
    except FileNotFoundError:
        return 127, "", f"{cmd[0]} not found on PATH"


def build(
    target: Path, engine: str, timeout: int, out_dir_override: Optional[str] = None
) -> BuildResult:
    root = detect_root(target)
    if root is None:
        return BuildResult(
            root=str(target),
            engine=engine,
            exit_code=2,
            diagnosis="no .tex file declaring \\documentclass found",
        )
    root = root.resolve()
    project_root = root.parent.resolve()
    result = BuildResult(root=str(root), engine=engine, exit_code=0)

    if shutil.which("latexmk") is None:
        result.exit_code = 127
        result.diagnosis = (
            "latexmk not on PATH. Install a TeX distribution (TeX Live, MacTeX, "
            "or MiKTeX); latexmk ships with all three."
        )
        return result

    out_dir = (
        (project_root / out_dir_override).resolve()
        if out_dir_override
        else resolve_out_dir(root)
    )

    cmd = [
        "latexmk",
        ENGINE_FLAGS[engine],
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-recorder",  # emits the .fls used for the dependency set
        "-file-line-error",
    ]
    if out_dir_override:
        cmd.append(f"-outdir={out_dir_override}")
    cmd.append(root.name)

    code, _, stderr = run(cmd, project_root, timeout)
    result.exit_code = code
    if code == 127:
        result.diagnosis = stderr.strip()
        return result

    stem = root.with_suffix("").name
    log_path = out_dir / f"{stem}.log"
    if not log_path.is_file():
        log_path = project_root / f"{stem}.log"

    if code == 0 and needs_glossary_pass(root):
        if shutil.which("makeglossaries") is not None:
            gcode, _, _ = run(["makeglossaries", stem], out_dir, timeout)
            if gcode == 0:
                result.glossary_pass = True
                code, _, _ = run(cmd, project_root, timeout)
                result.exit_code = code
        else:
            result.warnings.append(
                "document loads a glossary package without `automake` and "
                "makeglossaries is not on PATH; glossary entries may be missing"
            )

    parsed = parse_log(log_path)
    result.errors = parsed["errors"]
    result.undefined_refs = parsed["undefined_refs"]
    result.undefined_cites = parsed["undefined_cites"]
    result.pages = parsed["pages"]
    result.rerun_limit_hit = parsed["rerun_limit_hit"]
    result.warnings.extend(parsed["warnings"])

    pdf_path = out_dir / f"{stem}.pdf"
    if not pdf_path.is_file():
        pdf_path = project_root / f"{stem}.pdf"
    if not pdf_path.is_file():
        result.fresh = False
        result.diagnosis = (
            f"no PDF at {out_dir / (stem + '.pdf')}. Check -outdir, the root file, "
            "and the errors below."
        )
        return result

    result.pdf_path = str(pdf_path)
    result.pdf_mtime = pdf_path.stat().st_mtime

    fls = out_dir / f"{stem}.fls"
    if not fls.is_file():
        fls = project_root / f"{stem}.fls"
    deps = deps_from_fls(fls, project_root)
    result.dep_source = "fls"
    if not deps:
        deps = deps_from_glob(project_root)
        result.dep_source = "glob"
    dep, dep_mtime = newest(deps)
    if dep is not None:
        result.newest_dep = str(dep)
        result.newest_dep_mtime = dep_mtime
        result.fresh = result.pdf_mtime >= dep_mtime
    else:
        result.fresh = result.exit_code == 0

    if not result.fresh:
        result.diagnosis = (
            f"PDF is older than {result.newest_dep}. latexmk may have skipped the "
            "run, written to a different -outdir, or compiled a different root."
        )
    return result


def open_pdf(pdf_path: str) -> bool:
    """Best-effort viewer launch. Headless environments are a no-op, not an error."""
    if sys.platform == "darwin":
        opener = "open"
    elif os.name == "nt":
        opener = "start"
    else:
        if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
            return False
        opener = "xdg-open"
    if shutil.which(opener) is None and opener != "start":
        return False
    try:
        subprocess.Popen(
            [opener, pdf_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=(opener == "start"),
        )
        return True
    except OSError:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compile a LaTeX project with latexmk and verify PDF freshness."
    )
    parser.add_argument("target", help="Root .tex file or a directory to search")
    parser.add_argument(
        "--engine", choices=sorted(ENGINE_FLAGS), default="pdflatex", help="TeX engine"
    )
    parser.add_argument("--outdir", help="Override the output directory")
    parser.add_argument("--timeout", type=int, default=600, help="Per-pass timeout (s)")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--open", action="store_true", help="Open the PDF when fresh")
    args = parser.parse_args()

    target = Path(args.target).expanduser()
    if not target.exists():
        print(f"error: {target} does not exist", file=sys.stderr)
        sys.exit(2)

    result = build(target, args.engine, args.timeout, args.outdir)

    if args.open and result.fresh and result.pdf_path:
        open_pdf(result.pdf_path)

    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        status = "OK" if (result.exit_code == 0 and result.fresh) else "FAILED"
        print(f"{status}  root={result.root}  engine={result.engine}")
        if result.pdf_path:
            print(f"  pdf: {result.pdf_path} ({result.pages or '?'} pages)")
        print(f"  fresh: {result.fresh}  (deps from {result.dep_source})")
        if result.newest_dep:
            print(f"  newest source: {result.newest_dep}")
        if result.diagnosis:
            print(f"  diagnosis: {result.diagnosis}")
        for error in result.errors:
            location = f" (line {error['line']})" if error["line"] else ""
            print(f"  ! {error['text']}{location}")
        if result.undefined_refs:
            print(f"  undefined refs: {', '.join(result.undefined_refs)}")
        if result.undefined_cites:
            print(f"  undefined citations: {', '.join(result.undefined_cites)}")
        for warning in result.warnings:
            print(f"  warning: {warning}")

    sys.exit(0 if (result.exit_code == 0 and result.fresh) else 1)


if __name__ == "__main__":
    main()
