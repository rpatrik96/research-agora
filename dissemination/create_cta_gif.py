#!/usr/bin/env python3
"""
Create an animated GIF call-to-action for Research Agora.
"""

import matplotlib.animation as animation
import matplotlib.pyplot as plt

# Dark theme colors (conference poster aesthetic)
BG_COLOR = '#1a1a2e'  # Dark navy
PRIMARY = '#16213e'   # Darker blue
ACCENT1 = '#5ba3d9'   # Medium blue (readable on dark bg)
ACCENT2 = '#6db8e8'   # Light blue (readable on dark bg)
ACCENT3 = '#bbe1fa'   # Very light blue
TEXT_COLOR = '#e8e8e8'
HIGHLIGHT = '#00d4ff'  # Cyan

# Create figure with dark background
fig = plt.figure(figsize=(10, 6), facecolor=BG_COLOR)
ax = fig.add_subplot(111)
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis('off')

def clear_frame():
    """Clear the current frame."""
    ax.clear()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

def draw_frame_1():
    """Frame 1: Hook - Problem statement."""
    clear_frame()

    ax.text(5, 4.5, 'Tired of annoying', ha='center', va='center',
            fontsize=36, color=TEXT_COLOR, weight='bold', family='sans-serif')
    ax.text(5, 3.7, 'research tasks?*', ha='center', va='center',
            fontsize=36, color=TEXT_COLOR, weight='bold', family='sans-serif')

    examples = [
        '• Formatting LaTeX',
        '• Verifying citations',
        '• Tracking experiments'
    ]

    y_start = 2.6
    for i, example in enumerate(examples):
        ax.text(5, y_start - i*0.45, example, ha='center', va='center',
                fontsize=16, color=ACCENT3, family='sans-serif', style='italic')

    # Asterisk footnote
    ax.text(5, 0.4, '*no cryptic cluster error messages included', ha='center', va='center',
            fontsize=11, color=ACCENT2, family='sans-serif', style='italic')

def draw_frame_2():
    """Frame 2: Introduce Research Agora + agent types."""
    clear_frame()

    ax.text(5, 5.2, 'Research Agora', ha='center', va='center',
            fontsize=42, color=HIGHLIGHT, weight='bold', family='sans-serif')

    ax.text(5, 4.4, 'Open-source AI skills for ML research', ha='center', va='center',
            fontsize=20, color=TEXT_COLOR, family='sans-serif')

    ax.text(5, 3.6, 'Built with coding agents. Works across AI platforms.',
            ha='center', va='center',
            fontsize=16, color=ACCENT3, family='sans-serif', style='italic')

    # Agent types — symmetric two-column layout
    ax.text(5, 2.6, 'Agents for every step:', ha='center', va='center',
            fontsize=16, color=TEXT_COLOR, weight='bold', family='sans-serif')

    left_agents = [
        'Evidence Checker',
        'Claim Auditor',
        'Statistical Validator',
    ]
    right_agents = [
        "Devil's Advocate",
        'Reviewer Response',
        'Literature Synthesizer',
    ]

    # Symmetric columns: left at x=1.8, right at x=5.5
    for i, name in enumerate(left_agents):
        ax.text(1.8, 2.0 - i*0.4, f'•  {name}', ha='left', va='center',
                fontsize=13, color=ACCENT2, family='sans-serif')

    for i, name in enumerate(right_agents):
        ax.text(5.5, 2.0 - i*0.4, f'•  {name}', ha='left', va='center',
                fontsize=13, color=ACCENT2, family='sans-serif')

def draw_frame_3():
    """Frame 3: CTA - Call to action."""
    clear_frame()

    ax.text(5, 5.0, 'Join the Community', ha='center', va='center',
            fontsize=36, color=HIGHLIGHT, weight='bold', family='sans-serif')

    ctas = [
        ('Try it', 'Install and use', 3.8),
        ('Suggest', 'Request new skills', 2.8),
        ('Contribute', 'Build for others', 1.8),
    ]

    for action, description, y in ctas:
        ax.text(5, y, f'• {action}:', ha='center', va='center',
                fontsize=22, color=TEXT_COLOR, weight='bold', family='sans-serif')
        ax.text(5, y-0.45, description, ha='center', va='center',
                fontsize=16, color=ACCENT3, family='sans-serif', style='italic')

def draw_frame_4():
    """Frame 4: Get started."""
    clear_frame()

    ax.text(5, 5.0, 'Get Started', ha='center', va='center',
            fontsize=36, color=TEXT_COLOR, weight='bold', family='sans-serif')

    # Website
    ax.text(5, 3.8, 'https://research-agora.github.io', ha='center', va='center',
            fontsize=22, color=ACCENT2, family='monospace', weight='bold')

    # GitHub
    ax.text(5, 2.8, 'github.com/rpatrik96/research-agora', ha='center', va='center',
            fontsize=18, color=TEXT_COLOR, family='monospace')

    # Tagline
    ax.text(5, 1.5, 'By researchers, for researchers.',
            ha='center', va='center',
            fontsize=20, color=HIGHLIGHT, family='sans-serif', style='italic',
            weight='bold')

# Animation: 4 frames
frames_functions = [
    draw_frame_1,  # Hook (1.5s)
    draw_frame_1,
    draw_frame_1,
    draw_frame_2,  # Intro + agents (2.5s)
    draw_frame_2,
    draw_frame_2,
    draw_frame_2,
    draw_frame_2,
    draw_frame_3,  # CTA (2s)
    draw_frame_3,
    draw_frame_3,
    draw_frame_3,
    draw_frame_4,  # Get started (2s)
    draw_frame_4,
    draw_frame_4,
    draw_frame_4,
]

def animate(frame_num):
    """Animate function called by FuncAnimation."""
    frames_functions[frame_num]()

# Create animation
anim = animation.FuncAnimation(fig, animate, frames=len(frames_functions),
                               interval=500, repeat=True)

# Save as GIF
output_path = '/Users/patrik.reizinger/Documents/GitHub/research-agora/dissemination/research-agora-cta.gif'
print("Generating GIF animation... (this may take a minute)")
anim.save(output_path, writer='pillow', fps=2, dpi=100)
print(f"✓ Saved to: {output_path}")

plt.close()
