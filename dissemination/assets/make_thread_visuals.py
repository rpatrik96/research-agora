"""Generate Twitter thread visuals for Research Agora launch."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).parent
DPI = 200
# Twitter image: 1200x675 recommended
FIG_W, FIG_H = 6, 3.375

# Brand colors (from spiral logo segments)
COLORS = {
    "bg_dark": "#1a1a2e",
    "bg_card": "#16213e",
    "accent1": "#e94560",  # red
    "accent2": "#0f3460",  # blue
    "accent3": "#533483",  # purple
    "green": "#2ecc71",
    "red": "#e74c3c",
    "orange": "#f39c12",
    "text": "#ffffff",
    "text_dim": "#8899aa",
    "text_dark": "#1a1a2e",
}


def save(fig, name):
    fig.savefig(OUT / name, dpi=DPI, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    print(f"  {name}")


def post2_discoverability():
    """Scattered tools with no connections."""
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    fig.patch.set_facecolor(COLORS["bg_dark"])
    ax.set_facecolor(COLORS["bg_dark"])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    # Scattered tool labels — isolated, no connections
    tools = [
        (1.2, 4.8, "prompt A"),
        (3.5, 1.2, "agent X"),
        (7.8, 4.5, "workflow Z"),
        (5.5, 3.0, "script B"),
        (1.8, 2.0, "plugin C"),
        (8.2, 1.5, "bot Y"),
        (4.2, 5.0, "tool D"),
        (6.8, 2.2, "agent W"),
        (2.5, 3.5, "skill E"),
        (9.0, 3.5, "util F"),
    ]
    for x, y, label in tools:
        box = FancyBboxPatch(
            (x - 0.55, y - 0.25), 1.1, 0.5,
            boxstyle="round,pad=0.1",
            facecolor=COLORS["bg_card"],
            edgecolor=COLORS["text_dim"],
            linewidth=0.8,
            alpha=0.7,
        )
        ax.add_patch(box)
        ax.text(x, y, label, ha="center", va="center",
                fontsize=7, color=COLORS["text_dim"], family="monospace")

    # Big question mark in the center
    ax.text(5, 3.0, "?", ha="center", va="center",
            fontsize=72, color=COLORS["accent1"], alpha=0.3,
            fontweight="bold")

    ax.text(5, 0.3, "No search. No taxonomy. No way to compare.",
            ha="center", va="center", fontsize=10,
            color=COLORS["text"], style="italic")

    save(fig, "thread-post2-discoverability.png")


def post3_verification():
    """AI text with hidden errors highlighted."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, FIG_H))
    fig.patch.set_facecolor(COLORS["bg_dark"])

    for ax in (ax1, ax2):
        ax.set_facecolor(COLORS["bg_card"])
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis("off")

    # Left: "looks right"
    ax1.set_title("What you see", color=COLORS["text"], fontsize=11, pad=10)
    lines_ok = [
        "Smith et al. (2024) showed",
        "that transformers converge",
        "in O(n log n) steps, as",
        "confirmed by Lee & Park",
        "(2023, NeurIPS).",
    ]
    for i, line in enumerate(lines_ok):
        ax1.text(0.5, 8 - i * 1.4, line, fontsize=8, color=COLORS["text"],
                 family="monospace", transform=ax1.transData)
    ax1.text(5, 0.8, "Looks correct", ha="center", fontsize=10,
             color=COLORS["green"], fontweight="bold")

    # Right: errors revealed
    ax2.set_title("What's actually there", color=COLORS["text"], fontsize=11, pad=10)
    lines_err = [
        ("Smith et al. (2024) showed", None),
        ("that transformers converge", None),
        ("in O(n log n) steps, as", "O(n\u00b2) in the actual paper"),
        ("confirmed by Lee & Park", "This paper doesn't exist"),
        ("(2023, NeurIPS).", "Published at ICML, not NeurIPS"),
    ]
    for i, (line, err) in enumerate(lines_err):
        color = COLORS["red"] if err else COLORS["text"]
        ax1_y = 8 - i * 1.4
        ax2.text(0.5, ax1_y, line, fontsize=8, color=color,
                 family="monospace", transform=ax2.transData)
        if err:
            ax2.text(0.5, ax1_y - 0.6, f"\u2190 {err}", fontsize=6,
                     color=COLORS["orange"], family="monospace",
                     transform=ax2.transData)

    ax2.text(5, 0.8, "3 errors hidden in plain sight", ha="center",
             fontsize=10, color=COLORS["red"], fontweight="bold")

    plt.tight_layout(w_pad=2)
    save(fig, "thread-post3-verification.png")


def post4_benchmarking():
    """Vibes vs. numbers contrast."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, FIG_H))
    fig.patch.set_facecolor(COLORS["bg_dark"])

    for ax in (ax1, ax2):
        ax.set_facecolor(COLORS["bg_card"])
        ax.axis("off")

    # Left: vibes
    ax1.set_title("Without benchmarks", color=COLORS["text_dim"], fontsize=11, pad=10)
    ax1.text(0.5, 0.55, "???", ha="center", va="center",
             fontsize=48, color=COLORS["text_dim"],
             transform=ax1.transAxes)
    ax1.text(0.5, 0.2, '"Seems to work"', ha="center", va="center",
             fontsize=11, color=COLORS["text_dim"], style="italic",
             transform=ax1.transAxes)

    # Right: numbers
    ax2.set_title("With benchmarks", color=COLORS["green"], fontsize=11, pad=10)
    metrics = [
        ("Precision", "0.94"),
        ("Recall", "0.88"),
        ("F1", "0.91"),
    ]
    for i, (label, val) in enumerate(metrics):
        y = 0.7 - i * 0.2
        ax2.text(0.25, y, label, ha="left", va="center",
                 fontsize=12, color=COLORS["text_dim"],
                 transform=ax2.transAxes)
        ax2.text(0.75, y, val, ha="center", va="center",
                 fontsize=14, color=COLORS["green"], fontweight="bold",
                 family="monospace", transform=ax2.transAxes)
    ax2.text(0.5, 0.12, "Measured. Reproducible.", ha="center", va="center",
             fontsize=11, color=COLORS["green"],
             transform=ax2.transAxes)

    plt.tight_layout(w_pad=2)
    save(fig, "thread-post4-benchmarking.png")


def post6_coevolution():
    """Coevolution loop: tool <-> benchmark."""
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    fig.patch.set_facecolor(COLORS["bg_dark"])
    ax.set_facecolor(COLORS["bg_dark"])
    ax.set_xlim(-3, 3)
    ax.set_ylim(-2, 2)
    ax.set_aspect("equal")
    ax.axis("off")

    # Two boxes
    tool_box = FancyBboxPatch(
        (-2.6, -0.4), 2.0, 0.8,
        boxstyle="round,pad=0.15",
        facecolor=COLORS["accent2"],
        edgecolor=COLORS["text"],
        linewidth=1.5,
    )
    bench_box = FancyBboxPatch(
        (0.6, -0.4), 2.0, 0.8,
        boxstyle="round,pad=0.15",
        facecolor=COLORS["accent3"],
        edgecolor=COLORS["text"],
        linewidth=1.5,
    )
    ax.add_patch(tool_box)
    ax.add_patch(bench_box)

    ax.text(-1.6, 0, "bibtexupdater", ha="center", va="center",
            fontsize=11, color=COLORS["text"], fontweight="bold")
    ax.text(1.6, 0, "HALLMARK", ha="center", va="center",
            fontsize=11, color=COLORS["text"], fontweight="bold")

    # Curved arrows
    # Top arrow: tool -> benchmark
    ax.annotate(
        "", xy=(0.55, 0.35), xytext=(-0.55, 0.35),
        arrowprops=dict(
            arrowstyle="->", color=COLORS["green"],
            connectionstyle="arc3,rad=0.3", lw=2,
        ),
    )
    ax.text(0, 1.05, "tool reveals benchmark gaps",
            ha="center", va="center", fontsize=8,
            color=COLORS["green"], style="italic")

    # Bottom arrow: benchmark -> tool
    ax.annotate(
        "", xy=(-0.55, -0.35), xytext=(0.55, -0.35),
        arrowprops=dict(
            arrowstyle="->", color=COLORS["orange"],
            connectionstyle="arc3,rad=0.3", lw=2,
        ),
    )
    ax.text(0, -1.05, "benchmark reveals tool weaknesses",
            ha="center", va="center", fontsize=8,
            color=COLORS["orange"], style="italic")

    ax.text(0, 1.65, "Skills and benchmarks coevolve",
            ha="center", va="center", fontsize=13,
            color=COLORS["text"], fontweight="bold")

    save(fig, "thread-post6-coevolution.png")


def post8_mapping():
    """3-column problem -> solution mapping."""
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    fig.patch.set_facecolor(COLORS["bg_dark"])
    ax.set_facecolor(COLORS["bg_dark"])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    ax.text(5, 5.5, "Three problems \u2192 Three solutions",
            ha="center", va="center", fontsize=14,
            color=COLORS["text"], fontweight="bold")

    rows = [
        ("Discoverability", "Searchable skill registry", COLORS["accent1"]),
        ("Verification", "Evidence hierarchy (L1\u2013L6)", COLORS["orange"]),
        ("Benchmarking", "Shipped benchmarks", COLORS["green"]),
    ]

    for i, (problem, solution, color) in enumerate(rows):
        y = 3.8 - i * 1.3

        # Problem box
        pb = FancyBboxPatch(
            (0.3, y - 0.35), 3.2, 0.7,
            boxstyle="round,pad=0.1",
            facecolor=COLORS["bg_card"],
            edgecolor=color,
            linewidth=1.5,
        )
        ax.add_patch(pb)
        ax.text(1.9, y, problem, ha="center", va="center",
                fontsize=10, color=color, fontweight="bold")

        # Arrow
        ax.text(4.3, y, "\u2192", ha="center", va="center",
                fontsize=16, color=COLORS["text_dim"])

        # Solution box
        sb = FancyBboxPatch(
            (5.0, y - 0.35), 4.5, 0.7,
            boxstyle="round,pad=0.1",
            facecolor=COLORS["bg_card"],
            edgecolor=color,
            linewidth=1.5,
        )
        ax.add_patch(sb)
        ax.text(7.25, y, solution, ha="center", va="center",
                fontsize=10, color=COLORS["text"])

    save(fig, "thread-post8-mapping.png")


if __name__ == "__main__":
    print("Generating thread visuals...")
    post2_discoverability()
    post3_verification()
    post4_benchmarking()
    post6_coevolution()
    post8_mapping()
    print("Done!")
