# iem-talk Design Specifications

Auto-generated from `IEM_intuitive.pptx` by analyze_template.py.

## Slide Dimensions

| Property | Value |
|----------|-------|
| Width | 13.33" |
| Height | 7.5" |
| Aspect Ratio | 16:9 |

## Color Palette

### Background Colors
- Not detected (likely white/transparent)

### Text Colors
- `#4a8fe3` (Blue - primary)
- `#d1011b` (Red - emphasis)
- `#00b050` (Green - positive)

### Accent Colors
- `#4a8fe3` (Blue - primary accent)
- `#21366d` (Dark blue - headers)
- `#ff0000` (Red - alerts)
- `#d1011b` (Dark red)

## Typography

### Fonts Used
| Purpose | Font(s) |
|---------|---------|
| Titles | Helvetica Neue Medium |
| Body | Helvetica Neue Light, Helvetica Neue Medium |
| All fonts | Helvetica Neue Light, Helvetica Neue Medium |

### Font Sizes
| Element | Sizes (pt) |
|---------|-----------|
| Titles | 40 |
| Body | 32, 28, 24, 20 |
| Captions | 16, 14, 12 |

## Available Layouts

| Layout Name | Placeholders |
|-------------|--------------|
| Title Slide | CENTER_TITLE (3), SUBTITLE (4), DATE (16), FOOTER (15) |
| Title and Content | TITLE (1), OBJECT (7), DATE (16), FOOTER (15) |
| Section Header | TITLE (1), BODY (2), DATE (16), FOOTER (15) |
| Two Content | TITLE (1), OBJECT (7), OBJECT (7), DATE (16) |
| Comparison | TITLE (1), BODY (2), OBJECT (7), BODY (2) |
| Title Only | TITLE (1), DATE (16), FOOTER (15), SLIDE_NUMBER (13) |
| Blank | DATE (16), FOOTER (15), SLIDE_NUMBER (13) |
| Content with Caption | TITLE (1), OBJECT (7), BODY (2), DATE (16) |
| Picture with Caption | TITLE (1), PICTURE (18), BODY (2), DATE (16) |
| Title and Vertical Text | TITLE (1), BODY (2), DATE (16), FOOTER (15) |


## Python-PPTX Configuration

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

# Dimensions
SLIDE_WIDTH = Inches(13.33)
SLIDE_HEIGHT = Inches(7.5)

# Colors (as RGB tuples)
COLORS = {
    "background": (255, 255, 255),
    "text_primary": (74, 143, 227),    # #4a8fe3
    "text_dark": (33, 54, 109),        # #21366d
    "accent_red": (209, 1, 27),        # #d1011b
    "accent_green": (0, 176, 80),      # #00b050
}

# Font sizes
FONT_SIZES = {
    "title": Pt(40),
    "subtitle": Pt(32),
    "body": Pt(32),
    "body_small": Pt(24),
    "caption": Pt(16),
}

# Fonts
FONTS = {
    "title": "Helvetica Neue Medium",
    "body": "Helvetica Neue Light",
}
```

## Usage Notes

When creating presentations with this style:

1. **Start from template**: Copy the original .pptx file as your base
2. **Use slide layouts**: Prefer built-in layouts over manual positioning
3. **Match colors exactly**: Use the hex codes above for consistency
4. **Font hierarchy**: Maintain the size relationships for visual hierarchy
5. **Aspect ratio**: Ensure new slides match 16:9

## Source Template

Original file: `IEM_intuitive.pptx` (136 slides)
Location: `/Users/patrik.reizinger/My Drive/PhD/Presentations/IEM_intuitive.pptx`
