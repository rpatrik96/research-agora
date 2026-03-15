#!/usr/bin/env python3
"""
Create a terminal-style demo GIF for Research Agora.

Generates a polished animated GIF simulating a Claude Code session
using Research Agora skills. Designed for GitHub README, website, and X.com.

Output: research-agora-demo.gif (800x450, <5MB, ~11s)
"""

import matplotlib.animation as animation
import matplotlib.pyplot as plt

# ── Colors (GitHub dark theme) ──────────────────────────────────────
BG = "#0d1117"
TEXT = "#e6edf3"
GREEN = "#3fb950"
RED = "#f85149"
YELLOW = "#d29922"
BLUE = "#58a6ff"
GRAY = "#8b949e"
DIM = "#484f58"

# ── Layout ──────────────────────────────────────────────────────────
FIG_W, FIG_H = 8.0, 4.5  # inches → 800x450 at dpi=100
FONT = "monospace"
LINE_H = 0.048  # line height as fraction of figure height
LEFT_MARGIN = 0.05
TOP_START = 0.90

# ── Timing ──────────────────────────────────────────────────────────
FPS = 10  # frames per second
# Characters typed per frame (controls typewriter speed)
CHARS_PER_FRAME = 3

# ── Scene definitions ──────────────────────────────────────────────
# Each scene: list of (text, color, delay_frames_after, is_typed)
# delay_frames_after: pause after this line appears (in frames)
# is_typed: if True, use typewriter animation; if False, appear instantly

SCENE_1 = {
    "duration_s": 2.5,
    "lines": [
        {"text": "", "color": TEXT, "size": 10},
        {"text": "", "color": TEXT, "size": 10},
        {"text": "       R E S E A R C H   A G O R A", "color": BLUE, "size": 16},
        {"text": "", "color": TEXT, "size": 10},
        {"text": "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "color": DIM, "size": 9},
        {"text": "", "color": TEXT, "size": 10},
        {"text": "  AI skills for ML research", "color": TEXT, "size": 11},
        {"text": "  Plug into Claude Code · Open source · MIT License", "color": GRAY, "size": 9},
    ],
}

SCENE_2 = {
    "duration_s": 2.5,
    "lines": [
        {
            "text": "$ ", "color": GREEN, "size": 10,
            "rest": "claude /install academic@research-agora",
            "rest_color": TEXT,
        },
        {"text": "", "color": TEXT, "size": 10},
        {"text": "  ✓ Installed academic skills:", "color": GREEN, "size": 10},
        {"text": "    paper-review, paper-abstract, literature-synthesizer,", "color": TEXT, "size": 9},
        {"text": "    citation-verification, paper-references, rebuttal, ...", "color": TEXT, "size": 9},
    ],
}

SCENE_3 = {
    "duration_s": 3.0,
    "lines": [
        {"text": "$ ", "color": GREEN, "size": 10, "rest": "claude /paper-review", "rest_color": TEXT},
        {"text": "  Analyzing draft... ████████████████ Done", "color": GRAY, "size": 10},
        {"text": "", "color": TEXT, "size": 10},
        {"text": "  ⚠ Weaknesses found:", "color": YELLOW, "size": 10},
        {"text": "    • Claim on L.42 lacks citation", "color": TEXT, "size": 9},
        {"text": "    • Table 3 inconsistent with Fig.2", "color": TEXT, "size": 9},
        {"text": "    • Statistical test inappropriate for n<30", "color": TEXT, "size": 9},
        {"text": "", "color": TEXT, "size": 10},
        {"text": "  ✓ 3 critical, 5 minor issues flagged", "color": GREEN, "size": 10},
    ],
}

SCENE_4 = {
    "duration_s": 2.5,
    "lines": [
        {"text": "$ ", "color": GREEN, "size": 10, "rest": "claude /paper-references", "rest_color": TEXT},
        {"text": "  Checking citations against CrossRef, DBLP...", "color": GRAY, "size": 10},
        {"text": "", "color": TEXT, "size": 10},
        {"text": "  ✗ 2 hallucinated citations detected", "color": RED, "size": 10},
        {"text": '    → "Smith et al. 2024" — DOI not found', "color": RED, "size": 9},
        {"text": '    → "Lee & Park 2023" — title mismatch', "color": RED, "size": 9},
        {"text": "  ✓ Remaining citations verified", "color": GREEN, "size": 10},
    ],
}

SCENE_5 = {
    "duration_s": 2.0,
    "lines": [
        {"text": "", "color": TEXT, "size": 10},
        {"text": "  rpatrik96.github.io/research-agora", "color": BLUE, "size": 12},
        {"text": "  github.com/rpatrik96/research-agora", "color": BLUE, "size": 10},
        {"text": "", "color": TEXT, "size": 10},
        {"text": "  Open source · MIT License", "color": GRAY, "size": 10},
        {"text": "  By researchers, for researchers", "color": TEXT, "size": 10},
    ],
}

SCENES = [SCENE_1, SCENE_2, SCENE_3, SCENE_4, SCENE_5]


def build_frames():
    """
    Pre-compute all frames as lists of drawable elements.

    Each frame is a list of dicts: {x, y, text, color, size}
    We use typewriter effect for command lines (lines with "$ " prompt)
    and instant reveal with staggered timing for output lines.
    """
    all_frames = []

    for scene in SCENES:
        duration_frames = int(scene["duration_s"] * FPS)
        lines = scene["lines"]
        num_lines = len(lines)

        # Compute how many frames to spend revealing lines
        # Reserve last 30% of scene duration as hold time
        reveal_frames = max(int(duration_frames * 0.65), num_lines)
        hold_frames = duration_frames - reveal_frames

        # Frames per line reveal
        frames_per_line = max(1, reveal_frames // max(num_lines, 1))

        for f in range(duration_frames):
            frame_elements = []
            # How many lines should be visible at frame f
            lines_visible = min(num_lines, (f // frames_per_line) + 1)

            for li in range(lines_visible):
                line = lines[li]
                y = TOP_START - li * LINE_H * 2.2
                text = line["text"]
                color = line["color"]
                size = line.get("size", 10)

                # For command lines with prompt + rest, do typewriter on the rest
                if "rest" in line:
                    # Frame when this line first appeared
                    line_start_frame = li * frames_per_line
                    elapsed = f - line_start_frame
                    chars_shown = min(len(line["rest"]), elapsed * CHARS_PER_FRAME)

                    # Prompt
                    frame_elements.append({
                        "x": LEFT_MARGIN, "y": y,
                        "text": line["text"],
                        "color": line["color"], "size": size,
                    })
                    # Typed portion
                    typed = line["rest"][:chars_shown]
                    if typed:
                        # Calculate x offset for typed text after prompt
                        frame_elements.append({
                            "x": LEFT_MARGIN + len(line["text"]) * 0.0095,
                            "y": y,
                            "text": typed,
                            "color": line.get("rest_color", TEXT),
                            "size": size,
                        })
                    # Cursor blink
                    cursor_x = LEFT_MARGIN + (len(line["text"]) + chars_shown) * 0.0095
                    if chars_shown < len(line["rest"]) and elapsed % 2 == 0:
                        frame_elements.append({
                            "x": cursor_x, "y": y,
                            "text": "█", "color": TEXT, "size": size,
                        })
                else:
                    frame_elements.append({
                        "x": LEFT_MARGIN, "y": y,
                        "text": text, "color": color, "size": size,
                    })

            all_frames.append(frame_elements)

        # Add hold frames (full scene visible)
        if all_frames:
            for _ in range(hold_frames):
                all_frames.append(all_frames[-1])

    return all_frames


def main():
    # Build all frame data
    frames_data = build_frames()
    total_frames = len(frames_data)
    print(f"Total frames: {total_frames}, duration: {total_frames/FPS:.1f}s")

    # Create figure
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), facecolor=BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_facecolor(BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Add subtle terminal chrome
    def draw_chrome():
        """Draw terminal window title bar."""
        # Title bar background
        ax.axhspan(0.95, 1.0, color="#161b22", zorder=0)
        # Window dots
        for i, c in enumerate(["#f85149", "#d29922", "#3fb950"]):
            ax.plot(0.025 + i * 0.018, 0.975, "o", color=c, markersize=5, zorder=2)
        # Title
        ax.text(0.5, 0.975, "claude — research-agora", ha="center", va="center",
                fontsize=8, color=GRAY, family=FONT, zorder=2)

    def animate(frame_idx):
        ax.clear()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.set_facecolor(BG)
        fig.patch.set_facecolor(BG)

        draw_chrome()

        elements = frames_data[frame_idx]
        for el in elements:
            ax.text(
                el["x"], el["y"], el["text"],
                color=el["color"],
                fontsize=el["size"],
                family=FONT,
                verticalalignment="top",
                transform=ax.transAxes,
                zorder=1,
            )

    anim = animation.FuncAnimation(
        fig, animate, frames=total_frames, interval=1000 // FPS, repeat=True
    )

    output_path = "/Users/patrik.reizinger/Documents/GitHub/research-agora/dissemination/research-agora-demo.gif"
    print("Generating GIF...")
    anim.save(output_path, writer="pillow", fps=FPS, dpi=100)

    # Report file size
    import os
    size_bytes = os.path.getsize(output_path)
    size_mb = size_bytes / (1024 * 1024)
    print(f"Saved to: {output_path}")
    print(f"File size: {size_mb:.2f} MB")

    if size_mb > 5:
        print("WARNING: File exceeds 5MB X.com limit. Consider reducing FPS or duration.")
    else:
        print("File size OK for X.com (<5MB).")

    plt.close()


if __name__ == "__main__":
    main()
