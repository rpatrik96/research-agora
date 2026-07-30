#!/usr/bin/env python3
"""Render dissemination/feedback-loop.gif — the RFC-0001 pipeline, animated.

Deterministic (no randomness, no timestamps in the output) so re-running
produces the same animation. Requires matplotlib + pillow:

    pip install matplotlib pillow
    python3 scripts/generate_feedback_gif.py
"""

import io
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from PIL import Image

REPO_ROOT = Path(__file__).parent.parent
OUTPUT = REPO_ROOT / "dissemination" / "feedback-loop.gif"

# Okabe-Ito colorblind-safe palette
BLUE = "#0072B2"
SKY = "#56B4E9"
ORANGE = "#E69F00"
GREEN = "#009E73"
VERMILLION = "#D55E00"
PURPLE = "#CC79A7"
GREY = "#999999"
INK = "#1a1a2e"
PAPER = "#fafaf7"

# (x, y, w, h, title, subtitle, accent)
BOXES = [
    (0.03, 0.56, 0.17, 0.22, "Skill runs", "/paper-references\nin Claude Code", BLUE),
    (
        0.24,
        0.56,
        0.17,
        0.22,
        "Hook captures",
        "counters only —\nnever prompts/paths",
        BLUE,
    ),
    (0.45, 0.56, 0.17, 0.22, "Local spool", "~/.agora/  (opt-in,\nnothing sent)", SKY),
    (
        0.66,
        0.56,
        0.19,
        0.22,
        "Review gate",
        "/agora-feedback:\nuser inspects exact\npayload, confirms",
        ORANGE,
    ),
    (
        0.66,
        0.14,
        0.19,
        0.22,
        "GitHub issue",
        "label: skill-feedback\n(public, attributable)",
        PURPLE,
    ),
    (
        0.45,
        0.14,
        0.17,
        0.22,
        "Weekly Action",
        "validate · dedup ·\ncap · Wilson score",
        GREEN,
    ),
    (
        0.24,
        0.14,
        0.17,
        0.22,
        "Bot PR",
        "human reviews digest,\nmerges feedback.json",
        GREEN,
    ),
    (
        0.03,
        0.14,
        0.17,
        0.22,
        "Skills improve",
        "site badges · flags ·\nnew-skill proposals",
        VERMILLION,
    ),
]

# (from_box, to_box) index pairs, drawn in stage order
ARROWS = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 0)]

CAPTIONS = [
    "1/8  A skill runs — the loop starts with ordinary usage",
    "2/8  A PostToolUse hook records skill name + outcome. Content-free by design",
    "3/8  Events spool locally, outside any project root. Off by default",
    "4/8  Nothing leaves the machine until the user reviews the exact payload",
    "5/8  Submission = a public GitHub issue (or the spec'd HTTP sink)",
    "6/8  A scheduled Action validates, dedups, caps, and scores (Wilson LB)",
    "7/8  Updates arrive as a bot PR — a human reviews and merges, never auto-push",
    "8/8  Badges, lifecycle flags, and proposals close the loop: skills improve",
]


def box_edge(i: int, side: str) -> tuple[float, float]:
    x, y, w, h = BOXES[i][:4]
    return {
        "left": (x, y + h / 2),
        "right": (x + w, y + h / 2),
        "top": (x + w / 2, y + h),
        "bottom": (x + w / 2, y),
    }[side]


def arrow_endpoints(a: int, b: int) -> tuple[tuple[float, float], tuple[float, float]]:
    ax_, ay = BOXES[a][0], BOXES[a][1]
    bx, by = BOXES[b][0], BOXES[b][1]
    if abs(ay - by) < 0.01:  # same row
        if bx > ax_:
            return box_edge(a, "right"), box_edge(b, "left")
        return box_edge(a, "left"), box_edge(b, "right")
    if by < ay:  # downward
        return box_edge(a, "bottom"), box_edge(b, "top")
    return box_edge(a, "top"), box_edge(b, "bottom")


def draw_frame(stage: int) -> Image.Image:
    """Stages 0..7 highlight boxes/arrows progressively; 8 = full loop."""
    fig, ax = plt.subplots(figsize=(12, 5.4), dpi=80)
    fig.patch.set_facecolor(PAPER)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.5,
        0.95,
        "Research Agora — self-improvement feedback loop (RFC-0001)",
        ha="center",
        va="center",
        fontsize=15,
        fontweight="bold",
        color=INK,
    )
    ax.text(
        0.115,
        0.845,
        "YOUR MACHINE",
        ha="center",
        fontsize=8.5,
        color=GREY,
        fontweight="bold",
    )
    ax.text(
        0.115,
        0.42,
        "GITHUB (public, PR-gated)",
        ha="left",
        fontsize=8.5,
        color=GREY,
        fontweight="bold",
    )
    ax.axhline(y=0.5, xmin=0.02, xmax=0.98, color=GREY, lw=0.6, ls=(0, (4, 4)))

    for i, (x, y, w, h, title, subtitle, accent) in enumerate(BOXES):
        active = i <= stage
        face = accent if active else "#e8e8e4"
        alpha = 0.18 if active else 0.5
        edge = accent if active else GREY
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle="round,pad=0.012",
                facecolor=face,
                alpha=alpha,
                edgecolor=edge,
                linewidth=2.2 if i == stage else 1.2,
            )
        )
        color = INK if active else GREY
        ax.text(
            x + w / 2,
            y + h - 0.045,
            title,
            ha="center",
            va="center",
            fontsize=11.5,
            fontweight="bold",
            color=color,
        )
        ax.text(
            x + w / 2,
            y + h / 2 - 0.045,
            subtitle,
            ha="center",
            va="center",
            fontsize=8.2,
            color=color,
            linespacing=1.4,
        )

    for j, (a, b) in enumerate(ARROWS):
        if j > stage:
            continue
        start, end = arrow_endpoints(a, b)
        current = j == stage
        connection = "arc3,rad=0.0"
        if (a, b) == (7, 0):  # closing arrow, left edge upward
            start, end = box_edge(7, "top"), box_edge(0, "bottom")
        ax.add_patch(
            FancyArrowPatch(
                start,
                end,
                connectionstyle=connection,
                arrowstyle="-|>",
                mutation_scale=16,
                linewidth=2.4 if current else 1.4,
                color=BOXES[b][6] if current else GREY,
                alpha=1.0 if current else 0.7,
            )
        )

    caption = (
        CAPTIONS[min(stage, 7)]
        if stage < 8
        else "The loop, closed: usage evidence — reviewed by users, aggregated by scripts, decided by humans"
    )
    ax.add_patch(
        FancyBboxPatch(
            (0.03, 0.008),
            0.94,
            0.075,
            boxstyle="round,pad=0.008",
            facecolor=INK,
            alpha=0.85,
            edgecolor="none",
        )
    )
    ax.text(0.5, 0.045, caption, ha="center", va="center", fontsize=10.5, color="white")

    buf = io.BytesIO()
    fig.savefig(
        buf,
        format="png",
        facecolor=fig.get_facecolor(),
        bbox_inches="tight",
        pad_inches=0.1,
    )
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("P", palette=Image.ADAPTIVE, colors=128)


def main() -> int:
    frames = [draw_frame(stage) for stage in range(9)]
    durations = [1600] * 8 + [4000]  # ms per stage; hold the closed loop
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    size_kb = OUTPUT.stat().st_size / 1024
    print(
        f"Wrote {OUTPUT.relative_to(REPO_ROOT)} ({size_kb:.0f} KB, {len(frames)} frames)"
    )
    if size_kb > 950:
        print("warning: approaching the 1000 KB pre-commit size limit", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
