import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Figure: 1500x500 px at 150 dpi = 10 x 3.333 inches
fig, ax = plt.subplots(figsize=(10, 10/3), dpi=150)
fig.patch.set_facecolor('#1a1a2e')
ax.set_facecolor('#1a1a2e')
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# --- subtle dot grid background ---
rng = np.random.default_rng(42)
n_dots = 120
xs = rng.uniform(0.0, 1.0, n_dots)
ys = rng.uniform(0.08, 0.92, n_dots)
sizes = rng.uniform(1.5, 4.0, n_dots)
ax.scatter(xs, ys, s=sizes, color='#4ecdc4', alpha=0.10, zorder=1)

# --- geometric accent: faint circle top-right ---
circle = plt.Circle((0.88, 0.65), 0.28, color='#4ecdc4', fill=False,
                     linewidth=0.8, alpha=0.08, zorder=2)
ax.add_patch(circle)
circle2 = plt.Circle((0.88, 0.65), 0.18, color='#4ecdc4', fill=False,
                      linewidth=0.5, alpha=0.06, zorder=2)
ax.add_patch(circle2)

# --- thin teal bottom line (3 px equivalent at 150 dpi ~ 0.015 in fraction) ---
line_y = 0.035
ax.axhline(y=line_y, xmin=0, xmax=1, color='#4ecdc4', linewidth=2.0, zorder=5)

# --- left third: "Research Agora" ---
ax.text(0.04, 0.62, 'Research Agora',
        color='white', fontsize=30, fontweight='bold',
        va='center', ha='left', zorder=10,
        fontfamily='DejaVu Sans')

# tagline below main title
ax.text(0.04, 0.32, 'A Claude Code Plugin Marketplace',
        color='#ccccdd', fontsize=11, fontweight='normal',
        va='center', ha='left', zorder=10)

# --- center: skill count ---
ax.text(0.50, 0.60, '61 AI Skills',
        color='white', fontsize=22, fontweight='bold',
        va='center', ha='center', zorder=10)
ax.text(0.50, 0.35, 'for ML Research Workflows',
        color='#aaaacc', fontsize=12,
        va='center', ha='center', zorder=10)

# --- right third: URL in teal ---
ax.text(0.96, 0.55, 'rpatrik96.github.io',
        color='#4ecdc4', fontsize=11, fontweight='bold',
        va='center', ha='right', zorder=10)
ax.text(0.96, 0.38, '/research-agora',
        color='#4ecdc4', fontsize=11, fontweight='bold',
        va='center', ha='right', zorder=10)

# --- thin vertical separator between left and center ---
ax.axvline(x=0.36, ymin=0.12, ymax=0.88, color='#4ecdc4', linewidth=0.6, alpha=0.3, zorder=3)

out = '/Users/patrik.reizinger/Documents/GitHub/research-agora/dissemination/assets/twitter-banner.png'
# Remove bbox_inches='tight' so the figure is saved at exactly figsize*dpi pixels
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
fig.savefig(out, dpi=150, facecolor=fig.get_facecolor())
print(f"Saved: {out}")
