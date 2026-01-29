# iclr-poster Design Specifications

Auto-generated from `DIET_ICLR.pptx` by analyze_template.py.

## Poster Dimensions

| Property | Value |
|----------|-------|
| Width | 72.0" (182.88 cm) |
| Height | 36.0" (91.44 cm) |
| Aspect Ratio | 2:1 (landscape) |

This is a standard ICLR/NeurIPS poster size.

## Color Palette

### Background Colors
- White (`#ffffff`)

### Text Colors
- Black (`#000000`) - primary text

### Accent Colors
- `#4a8fe3` (Blue - primary accent, matches slides)
- `#d2011b` (Red - emphasis)

## Typography

### Fonts Used
| Purpose | Font(s) |
|---------|---------|
| Titles | Helvetica Neue, Helvetica Neue Light |
| Body | Helvetica Neue Light |
| All fonts | Helvetica Neue, Helvetica Neue Light |

### Font Sizes (for 72" x 36" poster)
| Element | Sizes (pt) |
|---------|-----------|
| Paper Title | 132 |
| Section Headers | 101, 90 |
| Subsection | 71 |
| Body Text | 48-60 (recommended) |
| Captions | 36-42 (recommended) |

**Note**: These sizes are for printing at full poster size. Text should be readable from ~2 meters.

## Available Layouts

| Layout Name | Use Case |
|-------------|----------|
| TITLE | Opening/title section |
| SECTION_HEADER | Major section dividers |
| TITLE_AND_BODY | Standard content block |
| TITLE_AND_TWO_COLUMNS | Side-by-side comparison |
| TITLE_ONLY | Figure-heavy sections |
| ONE_COLUMN_TEXT | Text-focused content |
| MAIN_POINT | Key takeaways |
| SECTION_TITLE_AND_DESCRIPTION | Intro sections |
| CAPTION_ONLY | Figure captions |
| BIG_NUMBER | Highlighting metrics |

## Python-PPTX Configuration

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

# Dimensions (72" x 36" poster)
SLIDE_WIDTH = Inches(72.0)
SLIDE_HEIGHT = Inches(36.0)

# Colors (as RGB tuples)
COLORS = {
    "background": (255, 255, 255),     # White
    "text_primary": (0, 0, 0),          # Black
    "accent_blue": (74, 143, 227),      # #4a8fe3
    "accent_red": (210, 1, 27),         # #d2011b
}

# Font sizes (for full-size poster)
FONT_SIZES = {
    "title": Pt(132),
    "section_header": Pt(101),
    "subsection": Pt(71),
    "body": Pt(54),
    "caption": Pt(40),
}

# Fonts
FONTS = {
    "title": "Helvetica Neue",
    "body": "Helvetica Neue Light",
}

# Panel dimensions (approximate for 3-column layout)
PANEL_WIDTH = Inches(22)  # ~22" per column with gutters
GUTTER = Inches(1)
MARGIN = Inches(1.5)
```

## Poster Layout Guide

### Recommended 3-Column Structure
```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TITLE + AUTHORS + LOGOS (full width)                  │
│                              ~6" height                                  │
├───────────────────────┬───────────────────────┬─────────────────────────┤
│      MOTIVATION       │        METHOD         │        RESULTS          │
│      BACKGROUND       │     (diagrams)        │       (figures)         │
│                       │                       │                         │
│       ~22" wide       │       ~22" wide       │        ~22" wide        │
├───────────────────────┼───────────────────────┼─────────────────────────┤
│    KEY INSIGHT /      │    MAIN FIGURE        │     CONCLUSION          │
│    RELATED WORK       │   (central viz)       │    + QR CODE            │
│                       │                       │    + CONTACT            │
└───────────────────────┴───────────────────────┴─────────────────────────┘
```

## Usage Notes

When creating posters with this style:

1. **Start from template**: Copy the original .pptx file as your base
2. **Maintain font hierarchy**: Use size relationships for visual hierarchy
3. **Keep text minimal**: Posters should be scannable in 30 seconds
4. **High-res figures**: Use 300+ DPI for print quality
5. **Match accent colors**: Use `#4a8fe3` for consistency with slides

## Institution Branding

The template includes space for:
- Institution logos (top corners)
- Conference badge (e.g., "ICLR 2025")
- QR code to paper/code (bottom right)

## Source Template

Original file: `DIET_ICLR.pptx`
Location: `/Users/patrik.reizinger/My Drive/PhD/Posters/DIET_ICLR.pptx`
