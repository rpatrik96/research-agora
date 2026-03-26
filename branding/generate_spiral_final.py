#!/usr/bin/env python3
"""
Research Agora — Final Spiral Logo Generator

Two options for comparison:
  Option A: Pure spiral + circle boundary, white dot at center (simplicity wins)
  Option B: Same spiral + circle boundary, upright "RA" at center (identity anchor)

Both generate: mark (dark/light/transparent), favicon-32, social-preview, og-image.

Usage:
    python branding/generate_spiral_final.py
"""

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np

# ── Brand Constants ───────────────────────────────────────────────────────────

DARK_BG = "#1a1a2e"
LIGHT_BG = "#f8f6f0"
TEAL = "#4ecdc4"

SPIRAL_COLORS = [
    "#4A90D9",  # academic       (outermost)
    "#50C878",  # development
    "#E8855A",  # editorial
    "#9B7FD4",  # formatting
    "#F5C242",  # office
    "#E05A7A",  # research-agents (innermost)
]

# ── Geometry ──────────────────────────────────────────────────────────────────

THETA_START = math.pi / 2
TURNS = 2.0
THETA_END = THETA_START + TURNS * 2 * math.pi
R_MAX = 0.78  # spiral fills 78% of unit canvas half-width

# Archimedean: r = a + b * (theta - theta_start)
_raw_a = 0.04
_raw_b = 0.12
_raw_rmax = _raw_a + _raw_b * (THETA_END - THETA_START)
_scale = R_MAX / _raw_rmax
A = _raw_a * _scale
B = _raw_b * _scale


def archimedean_pts(cx=0, cy=0, n=2500):
    """Generate Archimedean spiral points. pts[0]=inner, pts[-1]=outer."""
    theta = np.linspace(THETA_START, THETA_END, n)
    r = A + B * (theta - THETA_START)
    x = cx + r * np.cos(theta)
    y = cy + r * np.sin(theta)
    return np.column_stack([x, y])


def arc_lengths(pts):
    """Cumulative arc length along polyline."""
    d = np.diff(pts, axis=0)
    return np.concatenate([[0.0], np.cumsum(np.hypot(d[:, 0], d[:, 1]))])


def color_segments(pts, colors):
    """Split polyline into equal-arc-length segments with assigned colors."""
    arcs = arc_lengths(pts)
    total = arcs[-1]
    n = len(colors)
    segs = []
    for i, color in enumerate(colors):
        lo = total * i / n
        hi = total * (i + 1) / n
        mask = (arcs >= lo) & (arcs <= hi)
        idx = np.where(mask)[0]
        if len(idx) < 2:
            continue
        s = max(0, idx[0] - 1)
        e = min(len(pts) - 1, idx[-1] + 1)
        segs.append((pts[s : e + 1], color))
    return segs


# ── Drawing ───────────────────────────────────────────────────────────────────


def draw_spiral(ax, lw=4.0, circle_border=False, center_mode="dot"):
    """Draw the spiral mark.

    center_mode: "dot" = white circle, "ra" = upright RA text, "none" = nothing
    """
    pts = archimedean_pts()

    # Color segments — outermost first (reverse so outer = colors[0])
    segs = color_segments(pts[::-1], SPIRAL_COLORS)
    for seg_pts, color in segs:
        ax.plot(
            seg_pts[:, 0],
            seg_pts[:, 1],
            color=color,
            linewidth=lw,
            solid_capstyle="round",
            solid_joinstyle="round",
            zorder=4,
        )

    # Circle boundary
    if circle_border:
        border = plt.Circle(
            (0, 0),
            R_MAX + 0.06,
            fill=False,
            edgecolor="white",
            linewidth=lw * 0.35,
            alpha=0.7,
            zorder=2,
        )
        ax.add_patch(border)

    # Center element
    if center_mode == "dot":
        dot = plt.Circle((0, 0), 0.028, color="white", zorder=8)
        ax.add_patch(dot)
    elif center_mode == "ra":
        # Compute font size relative to axes
        fig = ax.get_figure()
        ax_w = ax.get_position().width * fig.get_figwidth()
        xlim = ax.get_xlim()
        data_range = xlim[1] - xlim[0]
        # RA should fit within the inner spiral loop (~0.15 data units radius)
        inner_r_inches = (0.26 / data_range) * ax_w
        fontsize = inner_r_inches * 72 * 0.55

        ax.text(
            0,
            0,
            "RA",
            color="white",
            fontsize=fontsize,
            fontweight="bold",
            fontfamily="Helvetica",
            ha="center",
            va="center",
            zorder=8,
            path_effects=[
                pe.withStroke(linewidth=fontsize * 0.04, foreground=(0, 0, 0, 0.35)),
            ],
        )


def make_mark(size_in, dpi, bg, center_mode="dot", circle_border=False):
    """Create a figure with the spiral mark."""
    fig, ax = plt.subplots(figsize=(size_in, size_in), dpi=dpi)
    if bg == "transparent":
        fig.patch.set_alpha(0)
        ax.set_facecolor("none")
    else:
        fig.patch.set_facecolor(bg)
        ax.set_facecolor(bg)

    half = 1.05
    ax.set_xlim(-half, half)
    ax.set_ylim(-half, half)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    lw = max(2.0, size_in * dpi * 0.003)
    draw_spiral(ax, lw=lw, circle_border=circle_border, center_mode=center_mode)
    return fig


def make_social_preview(width, height, dpi, center_mode="dot"):
    """Social preview with spiral mark on left + text on right."""
    fig_w = width / dpi
    fig_h = height / dpi
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("auto")
    ax.axis("off")

    # Spiral mark on left
    mark_ax = fig.add_axes([0.03, 0.12, 0.32, 0.76])
    mark_ax.set_xlim(-1.1, 1.1)
    mark_ax.set_ylim(-1.1, 1.1)
    mark_ax.set_aspect("equal")
    mark_ax.axis("off")
    mark_ax.set_facecolor("none")
    draw_spiral(mark_ax, lw=2.5, circle_border=False, center_mode=center_mode)

    # Text on right
    tx = 0.42
    ax.text(tx, 0.62, "Research Agora", color="white", fontsize=36,
            fontweight="bold", va="center", ha="left", fontfamily="DejaVu Sans")
    ax.text(tx, 0.42, "AI skills for researchers, by researchers.",
            color="#a1a1aa", fontsize=16, va="center", ha="left",
            fontfamily="DejaVu Sans")
    ax.text(tx, 0.25, "61 skills  ·  6 plugins  ·  10 workflows",
            color=TEAL, fontsize=13, fontweight="bold", va="center",
            ha="left", fontfamily="DejaVu Sans")

    ax.axhline(y=0.08, xmin=0.03, xmax=0.97, color=TEAL, linewidth=1.5, alpha=0.4)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig


def make_hero_mark():
    """Generate a hero-sized spiral with transparent bg and thicker stroke.

    Output: branding/spiral-hero.png (copied to site/static/spiral-hero.png)
    Size: 6 inches @ 300 dpi = 1800 x 1800 px
    """
    import shutil

    size_in = 6
    dpi = 300
    lw = 10.0

    fig, ax = plt.subplots(figsize=(size_in, size_in), dpi=dpi)
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    half = 1.05
    ax.set_xlim(-half, half)
    ax.set_ylim(-half, half)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    draw_spiral(ax, lw=lw, circle_border=False, center_mode="dot")

    out = Path(__file__).parent / "spiral-hero.png"
    fig.savefig(out, transparent=True, dpi=dpi)
    plt.close(fig)
    print(f"  Hero mark: {out}")

    site = out.parent.parent / "site" / "static"
    if site.exists():
        shutil.copy2(out, site / "spiral-hero.png")
        print("  Copied to site/static: spiral-hero.png")

    return out


def _save(fig, path):
    """Save and close figure."""
    if "transparent" in str(path) or "mark.png" in str(path):
        fig.savefig(path, transparent=True)
    else:
        fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)


# ── Generate All Assets ──────────────────────────────────────────────────────


def generate_option(out, prefix, center_mode):
    """Generate full asset suite for one option."""
    print(f"\n  === {prefix.upper()} (center={center_mode}) ===")

    # High-res mark — dark bg
    fig = make_mark(8, 300, DARK_BG, center_mode=center_mode)
    p = out / f"{prefix}-mark-dark.png"
    _save(fig, p)
    print(f"  Mark (dark): {p.name}")

    # Light bg
    fig = make_mark(8, 300, LIGHT_BG, center_mode=center_mode)
    p = out / f"{prefix}-mark-light.png"
    _save(fig, p)
    print(f"  Mark (light): {p.name}")

    # Transparent
    fig = make_mark(8, 300, "transparent", center_mode=center_mode)
    p = out / f"{prefix}-mark.png"
    fig.savefig(p, transparent=True)
    plt.close(fig)
    print(f"  Mark (transparent): {p.name}")

    # Favicon 32
    fig = make_mark(1, 32, DARK_BG, center_mode=center_mode)
    p = out / f"{prefix}-favicon-32.png"
    _save(fig, p)
    print(f"  Favicon 32: {p.name}")

    # Social preview
    fig = make_social_preview(1280, 640, 150, center_mode=center_mode)
    p = out / f"{prefix}-social-preview.png"
    _save(fig, p)
    print(f"  Social preview: {p.name}")

    # OG image
    fig = make_social_preview(1200, 630, 150, center_mode=center_mode)
    p = out / f"{prefix}-og-image.png"
    _save(fig, p)
    print(f"  OG image: {p.name}")


def main():
    out = Path(__file__).parent
    out.mkdir(parents=True, exist_ok=True)
    print("Generating final spiral logo options...")

    generate_option(out, "spiral-pure", center_mode="dot")
    generate_option(out, "spiral-ra", center_mode="ra")

    # Copy winner candidates to site/static for easy preview
    site = out.parent / "site" / "static"
    if site.exists():
        import shutil

        for f in ["spiral-pure-favicon-32.png", "spiral-pure-og-image.png",
                   "spiral-pure-mark.png"]:
            src = out / f
            if src.exists():
                shutil.copy2(src, site / f)
                print(f"  Copied to site/static: {f}")

    print("\nDone! Compare:")
    print(f"  Option A (pure):  {out}/spiral-pure-mark-dark.png")
    print(f"  Option B (RA):    {out}/spiral-ra-mark-dark.png")


if __name__ == "__main__":
    main()
