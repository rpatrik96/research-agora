---
name: science-gif
description: |
  Create animated GIFs to communicate ML research visually for Twitter/X, GitHub READMEs, and project
  websites. Use when asked to "create science gif", "animate results", "make animated figure",
  "gif for twitter", "animate method", "visualize algorithm".
model: sonnet
metadata:
  research-domain: general
  research-phase: dissemination
  task-type: dissemination
  verification-level: none
---

# Science GIF Skill

> **Hybrid**: LLM reads the paper/package and designs a storyboard; script generates the GIF via `matplotlib.animation` + Pillow.

Create short, looping animated GIFs that communicate one key idea from ML research. Optimized for social media (Twitter/X), GitHub READMEs, and project websites.

## Workflow

1. **Read the input** - Paper PDF, package docs, dataset description, or concept explanation
2. **Identify the key message** - One idea only; if it takes more than 5 seconds to understand, simplify
3. **Select GIF type** - Choose from the 6 supported types below
4. **Design storyboard** - Frame-by-frame plan as a structured table (see template)
5. **Generate Python script** - Self-contained script using matplotlib.animation or Pillow
6. **Run script** - Execute to produce the GIF file
7. **Optimize** - Reduce file size if above 5 MB target

## Output Constraints

| Parameter | Value |
|-----------|-------|
| Duration | 3-10 s, looping |
| Resolution | 800x600 (landscape) or 1080x1080 (square) |
| File size | < 5 MB |
| Frame rate | 15-30 FPS |
| Format | GIF primary, MP4 fallback for large animations |

## GIF Types

### 1. Method Walkthrough
Step-by-step build-up of a method diagram. Components appear sequentially with labels.
- **Use for**: Architecture diagrams, pipeline overviews, model components
- **Pacing**: 1-2 seconds per component, pause on final complete view

### 2. Results Animation
Training curves drawing progressively, bar charts growing, metrics improving.
- **Use for**: Learning curves, ablation comparisons, scaling results
- **Pacing**: Smooth drawing over 3-5 seconds, hold final frame 2 seconds

### 3. Architecture Reveal
Neural network layers or model blocks appearing one at a time with connections.
- **Use for**: Transformer blocks, encoder-decoder structures, novel layers
- **Pacing**: 0.5-1 second per layer, connections animate after blocks

### 4. Before/After Comparison
Alternating between baseline and proposed method results.
- **Use for**: Generated samples, denoising, style transfer, any visual improvement
- **Pacing**: 1.5-2 seconds per view, clear labels for each state

### 5. Algorithm Visualization
Step-by-step execution of an algorithm on a small example.
- **Use for**: Optimization steps, attention mechanisms, graph algorithms
- **Pacing**: 1-2 seconds per step, highlight active elements

### 6. Data Showcase
Cycling through dataset samples, augmentations, or distribution shifts.
- **Use for**: Dataset previews, augmentation pipelines, domain shifts
- **Pacing**: 0.5-1 second per sample, smooth transitions

## Storyboard Template

Before writing code, plan the animation in this format:

```markdown
## Storyboard: [GIF Title]

**Type**: [Method Walkthrough | Results Animation | Architecture Reveal | Before/After | Algorithm Viz | Data Showcase]
**Duration**: [X seconds]
**Resolution**: [800x600 | 1080x1080]
**FPS**: [15-30]
**Loop**: [yes/no, seamless/restart]

| Frame Range | Time (s) | Visual Description | Text/Labels |
|-------------|----------|--------------------|-------------|
| 1-15        | 0-1      | Blank canvas, title fades in | "Our Method" |
| 16-45       | 1-3      | First component draws | "Encoder" |
| 46-75       | 3-5      | Second component draws | "Decoder" |
| 76-90       | 5-6      | Connections appear | Arrow labels |
| 91-120      | 6-8      | Full diagram holds | All labels |
```

## Style Setup

```python
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from pathlib import Path

# Colorblind-safe palette (from publication-figures skill)
COLORS = {
    "blue": "#0072B2",
    "orange": "#E69F00",
    "green": "#009E73",
    "red": "#D55E00",
    "purple": "#CC79A7",
    "cyan": "#56B4E9",
    "yellow": "#F0E442",
}

def setup_gif_style():
    """Configure matplotlib for animated GIFs (screen-optimized)."""
    plt.rcParams.update({
        # No LaTeX for portability and speed
        "text.usetex": False,
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],

        # Figure size
        "figure.figsize": (8, 6),
        "figure.dpi": 100,
        "figure.facecolor": "white",

        # Larger fonts for screen readability
        "font.size": 14,
        "axes.titlesize": 18,
        "axes.labelsize": 14,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "legend.fontsize": 12,

        # Thicker lines for visibility
        "axes.linewidth": 1.5,
        "lines.linewidth": 2.5,
        "lines.markersize": 8,

        # Clean spines
        "axes.spines.top": False,
        "axes.spines.right": False,

        # Subtle grid
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.linewidth": 0.5,

        # Layout
        "figure.constrained_layout.use": True,
    })

setup_gif_style()
```

## Code Examples

### Example 1: Training Curves (FuncAnimation)

Progressive drawing of training curves comparing methods.

```python
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# --- Style setup (see above) ---
setup_gif_style()

# --- Simulated data ---
steps = np.linspace(0, 100, 200)
ours = 0.95 * (1 - np.exp(-steps / 20)) + np.random.normal(0, 0.01, 200)
baseline = 0.80 * (1 - np.exp(-steps / 30)) + np.random.normal(0, 0.01, 200)

fig, ax = plt.subplots()
ax.set_xlim(0, 100)
ax.set_ylim(0, 1.05)
ax.set_xlabel("Epoch")
ax.set_ylabel("Accuracy")
ax.set_title("Training Progress")

line_ours, = ax.plot([], [], color=COLORS["blue"], label="Ours")
line_base, = ax.plot([], [], color=COLORS["orange"], label="Baseline")
ax.legend(loc="lower right", frameon=False)

def init():
    line_ours.set_data([], [])
    line_base.set_data([], [])
    return line_ours, line_base

def animate(i):
    # Draw progressively, 4 data points per frame
    idx = min(i * 4, len(steps))
    line_ours.set_data(steps[:idx], ours[:idx])
    line_base.set_data(steps[:idx], baseline[:idx])
    return line_ours, line_base

# 50 frames for the draw + 30 frames holding the final view
total_draw_frames = 50
hold_frames = 30

def animate_with_hold(i):
    if i < total_draw_frames:
        return animate(i)
    return line_ours, line_base  # hold final frame

anim = animation.FuncAnimation(
    fig, animate_with_hold, init_func=init,
    frames=total_draw_frames + hold_frames, interval=100, blit=True
)
anim.save("training_curves.gif", writer="pillow", fps=15)
plt.close(fig)
print(f"Saved: training_curves.gif")
```

### Example 2: Architecture Reveal (Pillow Frame-by-Frame)

Diagram components appearing sequentially, built frame-by-frame.

```python
from PIL import Image, ImageDraw, ImageFont
import io

WIDTH, HEIGHT = 800, 600
BG_COLOR = (255, 255, 255)
FONT_SIZE = 24

def hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

BLUE = hex_to_rgb("#0072B2")
ORANGE = hex_to_rgb("#E69F00")
GREEN = hex_to_rgb("#009E73")
GRAY = (200, 200, 200)

# Try to load a clean font, fall back to default
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONT_SIZE)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
except OSError:
    font = ImageFont.load_default()
    font_small = font

# Define components: (label, x, y, w, h, color)
components = [
    ("Input", 100, 250, 120, 60, GRAY),
    ("Encoder", 280, 250, 120, 60, BLUE),
    ("Latent z", 460, 250, 120, 60, ORANGE),
    ("Decoder", 640, 250, 120, 60, GREEN),
]

# Define arrows between consecutive components
arrows = [(220, 280, 280, 280), (400, 280, 460, 280), (580, 280, 640, 280)]

frames = []
fps = 10
hold_seconds = 2

# Build-up: add one component per stage
for stage in range(len(components) + 1):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Title
    draw.text((WIDTH // 2 - 100, 40), "VAE Architecture", fill=(0, 0, 0), font=font)

    # Draw visible components
    for i in range(stage):
        label, x, y, w, h, color = components[i]
        draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=10, fill=color, outline=(0, 0, 0), width=2)
        bbox = draw.textbbox((0, 0), label, font=font_small)
        tw = bbox[2] - bbox[0]
        draw.text((x + (w - tw) // 2, y + 18), label, fill=(0, 0, 0), font=font_small)

    # Draw arrows between visible components
    for i in range(min(stage, len(arrows))):
        if i + 1 < stage:
            x1, y1, x2, y2 = arrows[i]
            draw.line([(x1, y1), (x2, y2)], fill=(0, 0, 0), width=3)
            draw.polygon([(x2, y2 - 6), (x2, y2 + 6), (x2 + 10, y2)], fill=(0, 0, 0))

    # Each stage shows for 1 second
    for _ in range(fps):
        frames.append(img.copy())

# Hold final frame
for _ in range(fps * hold_seconds):
    frames.append(frames[-1].copy())

frames[0].save(
    "architecture_reveal.gif",
    save_all=True,
    append_images=frames[1:],
    duration=1000 // fps,
    loop=0,
)
print(f"Saved: architecture_reveal.gif ({len(frames)} frames)")
```

### Example 3: Before/After Comparison (Hybrid)

Alternating between baseline and proposed results with clear labels.

```python
import matplotlib.pyplot as plt
from PIL import Image
import io
import numpy as np

setup_gif_style()

def render_comparison_frame(data, title, color):
    """Render a single comparison state to a PIL Image."""
    fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
    ax.imshow(data, cmap="viridis")
    ax.set_title(title, fontsize=22, fontweight="bold", color=color, pad=15)
    ax.axis("off")
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGB")

# --- Simulated data (replace with real images) ---
np.random.seed(42)
clean = np.random.rand(64, 64)
noisy = clean + np.random.normal(0, 0.3, clean.shape)

baseline_result = noisy * 0.7 + clean * 0.3  # poor denoising
ours_result = noisy * 0.1 + clean * 0.9      # good denoising

frame_baseline = render_comparison_frame(baseline_result, "Baseline", "#D55E00")
frame_ours = render_comparison_frame(ours_result, "Ours", "#0072B2")

# Resize to match
size = (800, 600)
frame_baseline = frame_baseline.resize(size, Image.LANCZOS)
frame_ours = frame_ours.resize(size, Image.LANCZOS)

# Build alternating GIF: 1.5s each view, 4 cycles
fps = 15
frames_per_view = int(1.5 * fps)
cycles = 4
frames = []

for _ in range(cycles):
    frames.extend([frame_baseline] * frames_per_view)
    frames.extend([frame_ours] * frames_per_view)

frames[0].save(
    "before_after.gif",
    save_all=True,
    append_images=frames[1:],
    duration=1000 // fps,
    loop=0,
)
print(f"Saved: before_after.gif ({len(frames)} frames, {len(frames)/fps:.1f}s)")
```

## Platform Guidelines

### Twitter/X
- **Max GIF size**: 15 MB (target < 5 MB for fast loading)
- **Aspect ratio**: 16:9 (800x450) or 1:1 (1080x1080) preferred
- **Auto-play**: GIFs auto-play in feed, so make the first frame count
- **Alt text**: Always provide alt text describing what the animation shows

### GitHub README
- **Max display width**: ~800px in rendered markdown
- **Embedding**: `![Description](path/to/animation.gif)`
- **File size**: Keep under 5 MB; GitHub renders but may slow page load
- **Fallback**: Add a static thumbnail linking to the GIF for slow connections

### Project Website
- **Format**: Consider MP4 with `<video autoplay loop muted>` for smaller files
- **Lazy loading**: Use `loading="lazy"` to avoid blocking page load
- **Resolution**: Can go higher (1080p) since bandwidth is less constrained

## File Size Optimization

If the GIF exceeds 5 MB, apply these techniques in order:

```bash
# 1. Reduce FPS (often the biggest win)
# In code: change fps=15 to fps=10

# 2. Reduce resolution
# In code: change figsize or resize frames to 600x450

# 3. Reduce color count with gifsicle
gifsicle --colors 128 --optimize=3 input.gif -o optimized.gif

# 4. Reduce duration (fewer frames)
# In code: reduce hold_frames or total_draw_frames

# 5. Convert to MP4 as fallback (10x smaller)
ffmpeg -i input.gif -movflags faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" output.mp4
```

```python
# Programmatic optimization: reduce colors with Pillow
from PIL import Image

img = Image.open("large.gif")
frames = []
try:
    while True:
        frames.append(img.copy().quantize(colors=128, method=Image.MEDIANCUT))
        img.seek(img.tell() + 1)
except EOFError:
    pass

frames[0].save(
    "optimized.gif",
    save_all=True,
    append_images=frames[1:],
    duration=img.info.get("duration", 100),
    loop=0,
)
```

## Checklist

Before delivering the GIF:

- [ ] Single key message — viewer gets it in under 5 seconds
- [ ] Looping is seamless or has a clear restart point
- [ ] Text is readable at the target display size
- [ ] Colorblind-safe palette used
- [ ] File size under 5 MB (or MP4 fallback provided)
- [ ] First frame is meaningful (not blank) for auto-play previews
- [ ] Frame rate is smooth (no stuttering from too few frames)
- [ ] Duration is 3-10 seconds (not too fast, not tedious)
- [ ] Alt text written for accessibility

## Anti-Patterns

- **Too many ideas**: One GIF = one concept. Split into multiple GIFs if needed
- **Text-heavy frames**: If you need a paragraph, it is not a GIF — use a figure
- **Tiny text**: Font size must be readable at 400px display width minimum
- **No hold frame**: Always pause on the final state so viewers can absorb it
- **Jarring loops**: Fade out or design the end state to flow back to the start
- **Huge file size**: Unoptimized GIFs over 15 MB will not upload to Twitter
- **Missing context**: Add a title or brief label so the GIF makes sense without surrounding text
- **Too fast**: Err on the side of slower; viewers can always replay but cannot pause
- **No fallback**: Always offer MP4 conversion instructions for large animations
