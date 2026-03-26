import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ── Spiral geometry (inlined from branding/generate_spiral_final.py) ──────────

TEAL = "#4ecdc4"
DARK_BG = "#1a1a2e"

SPIRAL_COLORS = [
    "#4A90D9",  # academic       (outermost)
    "#50C878",  # development
    "#E8855A",  # editorial
    "#9B7FD4",  # formatting
    "#F5C242",  # office
    "#E05A7A",  # research-agents (innermost)
]

THETA_START = math.pi / 2
TURNS = 2.0
THETA_END = THETA_START + TURNS * 2 * math.pi
R_MAX = 0.78

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


def _arc_lengths(pts):
    d = np.diff(pts, axis=0)
    return np.concatenate([[0.0], np.cumsum(np.hypot(d[:, 0], d[:, 1]))])


def _color_segments(pts, colors):
    arcs = _arc_lengths(pts)
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


def draw_spiral(ax, lw=4.0):
    """Draw the multi-color Archimedean spiral mark centered at (0, 0)."""
    pts = archimedean_pts()
    segs = _color_segments(pts[::-1], SPIRAL_COLORS)
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
    # White center dot
    dot = plt.Circle((0, 0), 0.028, color="white", zorder=8)
    ax.add_patch(dot)


# ── Banner: 1500×500 px at 150 dpi = 10 × 3.333 inches ───────────────────────

DPI = 150
WIDTH_PX, HEIGHT_PX = 1500, 500
fig_w = WIDTH_PX / DPI   # 10.0
fig_h = HEIGHT_PX / DPI  # 3.333...

fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=DPI)
fig.patch.set_facecolor(DARK_BG)
ax.set_facecolor(DARK_BG)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_aspect("auto")
ax.axis("off")
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

# ── Subtle dot grid background ────────────────────────────────────────────────
rng = np.random.default_rng(42)
n_dots = 140
xs = rng.uniform(0.30, 1.0, n_dots)
ys = rng.uniform(0.08, 0.92, n_dots)
sizes = rng.uniform(1.5, 4.0, n_dots)
ax.scatter(xs, ys, s=sizes, color=TEAL, alpha=0.10, zorder=1)

# ── Thin teal bottom line ─────────────────────────────────────────────────────
ax.axhline(y=0.04, xmin=0, xmax=1, color=TEAL, linewidth=2.0, zorder=5)

# ── Spiral mark: left ~38% of figure ─────────────────────────────────────────
# add_axes([left, bottom, width, height]) in figure-fraction coordinates.
# The banner is 3:1 aspect, so a 0.38-wide square sub-axes sits left of center.
mark_ax = fig.add_axes([0.01, 0.06, 0.38, 0.90])
mark_ax.set_xlim(-1.1, 1.1)
mark_ax.set_ylim(-1.1, 1.1)
mark_ax.set_aspect("equal")
mark_ax.axis("off")
mark_ax.set_facecolor("none")
draw_spiral(mark_ax, lw=4.0)

# ── Text: center-right (x from ~0.46 onward) ─────────────────────────────────
tx = 0.46

# "Research Agora" title
ax.text(
    tx, 0.66,
    "Research Agora",
    color="white",
    fontsize=28,
    fontweight="bold",
    va="center",
    ha="left",
    fontfamily="DejaVu Sans",
    zorder=10,
)

# Tagline
ax.text(
    tx, 0.42,
    "61 AI Skills for ML Research",
    color="#ccccdd",
    fontsize=13,
    fontweight="normal",
    va="center",
    ha="left",
    fontfamily="DejaVu Sans",
    zorder=10,
)

# URL in teal
ax.text(
    tx, 0.20,
    "rpatrik96.github.io/research-agora",
    color=TEAL,
    fontsize=11,
    fontweight="bold",
    va="center",
    ha="left",
    fontfamily="DejaVu Sans",
    zorder=10,
)

# ── Save ──────────────────────────────────────────────────────────────────────
out = Path(__file__).parent / "twitter-banner.png"
fig.savefig(out, dpi=DPI, facecolor=fig.get_facecolor())
print(f"Saved: {out}")
