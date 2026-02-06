---
name: pptx-create
description: Create and edit PowerPoint presentations using python-pptx
model: haiku
version: 1.0.0
triggers:
  - presentation
  - powerpoint
  - pptx
  - slides
  - slide deck
dependencies:
  - python-pptx>=0.6.21
  - Pillow>=9.0.0
---

# PowerPoint Creation Skill

> **Script-first**: This skill generates presentations via python-pptx scripts. No LLM generation needed.

Create professional PowerPoint presentations programmatically using python-pptx.

## Installation

```bash
pip install python-pptx Pillow
```

## Core Concepts

### Presentation Structure
```
Presentation
├── Slides (collection)
│   ├── Slide 1
│   │   ├── Shapes (text boxes, images, charts)
│   │   └── Placeholders (title, content, etc.)
│   └── Slide 2...
├── Slide Layouts (templates for slide types)
└── Slide Master (global styling)
```

### Standard Slide Layouts (by index)
| Index | Layout Name | Use Case |
|-------|-------------|----------|
| 0 | Title Slide | Opening slide |
| 1 | Title and Content | Most common, bullet points |
| 2 | Section Header | Chapter dividers |
| 3 | Two Content | Side-by-side comparison |
| 4 | Comparison | With headers for each side |
| 5 | Title Only | For custom content/images |
| 6 | Blank | Full creative control |
| 7 | Content with Caption | Image + description |
| 8 | Picture with Caption | Large image focus |

## Template System

Before creating presentations, check for available design templates that define colors, fonts, and layouts:

```bash
# List available templates
ls ~/.claude/skills/templates/slides/

# Read a template's style guide
cat ~/.claude/skills/templates/slides/{template-name}/STYLE.md
```

### Using a Template

```python
from pptx import Presentation
import json
from pathlib import Path

# Load template as base
template_dir = Path.home() / ".claude/skills/templates/slides/{template-name}"
prs = Presentation(template_dir / "template.pptx")

# Load specs for programmatic access
with open(template_dir / "specs.json") as f:
    specs = json.load(f)

# Use template colors
accent_color = specs["colors"]["accents"][0]  # e.g., "#0066CC"
```

### Adding New Templates

```bash
# Templates are stored in the research-agora marketplace
# Clone or update the repository first, then run from its templates directory:
cd /path/to/research-agora/templates
python analyze_template.py /path/to/your/template.pptx --output slides --name "template-name"

# After analysis, templates are available at ~/.claude/skills/templates/slides/{template-name}/
```

This extracts colors, fonts, sizes, and layouts into `STYLE.md` and `specs.json`.

## Quick Reference

### Create Basic Presentation

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RgbColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# Create presentation (16:9 aspect ratio)
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Add title slide
title_layout = prs.slide_layouts[0]
slide = prs.slides.add_slide(title_layout)
title = slide.shapes.title
subtitle = slide.placeholders[1]

title.text = "Presentation Title"
subtitle.text = "Author Name • Conference 2025"

# Save
prs.save("presentation.pptx")
```

### Add Content Slide with Bullets

```python
# Title and Content layout
bullet_layout = prs.slide_layouts[1]
slide = prs.slides.add_slide(bullet_layout)

slide.shapes.title.text = "Key Findings"

# Access body placeholder
body = slide.placeholders[1]
tf = body.text_frame

# First bullet (level 0)
tf.text = "First main point"

# Additional bullets
p = tf.add_paragraph()
p.text = "Second main point"
p.level = 0

# Sub-bullet (level 1)
p = tf.add_paragraph()
p.text = "Supporting detail"
p.level = 1
```

### Add Image

```python
from pptx.util import Inches

# Title Only layout for custom positioning
slide = prs.slides.add_slide(prs.slide_layouts[5])
slide.shapes.title.text = "Results Visualization"

# Add image with position and size
left = Inches(1)
top = Inches(2)
width = Inches(8)  # Height auto-calculated to maintain aspect ratio

slide.shapes.add_picture("figure.png", left, top, width=width)
```

### Add Table

```python
from pptx.util import Inches, Pt

slide = prs.slides.add_slide(prs.slide_layouts[5])
slide.shapes.title.text = "Experimental Results"

# Define table dimensions
rows, cols = 4, 3
left, top = Inches(1), Inches(2)
width, height = Inches(10), Inches(3)

table = slide.shapes.add_table(rows, cols, left, top, width, height).table

# Set column widths
table.columns[0].width = Inches(3)
table.columns[1].width = Inches(3.5)
table.columns[2].width = Inches(3.5)

# Header row
headers = ["Method", "Accuracy", "F1 Score"]
for i, header in enumerate(headers):
    cell = table.cell(0, i)
    cell.text = header
    cell.text_frame.paragraphs[0].font.bold = True
    cell.text_frame.paragraphs[0].font.size = Pt(14)

# Data rows
data = [
    ["Baseline", "0.82", "0.79"],
    ["Ours (w/o aug)", "0.89", "0.86"],
    ["Ours (full)", "0.94", "0.92"],
]
for row_idx, row_data in enumerate(data, start=1):
    for col_idx, value in enumerate(row_data):
        table.cell(row_idx, col_idx).text = value
```

### Add Chart

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

slide = prs.slides.add_slide(prs.slide_layouts[5])
slide.shapes.title.text = "Performance Comparison"

# Prepare chart data
chart_data = CategoryChartData()
chart_data.categories = ["Model A", "Model B", "Model C"]
chart_data.add_series("Accuracy", (0.82, 0.89, 0.94))
chart_data.add_series("F1 Score", (0.79, 0.86, 0.92))

# Add chart
x, y = Inches(1), Inches(2)
cx, cy = Inches(10), Inches(5)
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data
).chart

# Style chart
chart.has_legend = True
chart.legend.include_in_layout = False
```

### Text Formatting

```python
from pptx.util import Pt
from pptx.dml.color import RgbColor
from pptx.enum.text import PP_ALIGN

# Access paragraph
para = shape.text_frame.paragraphs[0]
para.alignment = PP_ALIGN.CENTER

# Access run (text segment)
run = para.runs[0]
run.font.name = "Arial"
run.font.size = Pt(24)
run.font.bold = True
run.font.italic = False
run.font.color.rgb = RgbColor(0x00, 0x66, 0xCC)  # Blue
```

### Custom Text Box

```python
from pptx.util import Inches, Pt
from pptx.enum.text import MSO_ANCHOR

# Add text box
left, top = Inches(1), Inches(5)
width, height = Inches(4), Inches(1)
txBox = slide.shapes.add_textbox(left, top, width, height)

tf = txBox.text_frame
tf.word_wrap = True
tf.auto_size = None  # Fixed size

p = tf.paragraphs[0]
p.text = "Custom annotation or caption"
p.font.size = Pt(12)
p.font.italic = True
```

## Academic/Research Templates

### Conference Presentation Template

```python
def create_conference_presentation(
    title: str,
    authors: str,
    affiliation: str,
    sections: list[dict],
    output_path: str
):
    """
    Create a conference-style presentation.

    Args:
        title: Presentation title
        authors: Author names
        affiliation: Institution/affiliation
        sections: List of {"title": str, "bullets": list[str]} or
                        {"title": str, "image": str, "caption": str}
        output_path: Where to save the .pptx file
    """
    from pptx import Presentation
    from pptx.util import Inches, Pt

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Title slide
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = title
    slide.placeholders[1].text = f"{authors}\n{affiliation}"

    # Content slides
    for section in sections:
        if "bullets" in section:
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            slide.shapes.title.text = section["title"]
            tf = slide.placeholders[1].text_frame
            tf.text = section["bullets"][0]
            for bullet in section["bullets"][1:]:
                p = tf.add_paragraph()
                p.text = bullet
                p.level = 0

        elif "image" in section:
            slide = prs.slides.add_slide(prs.slide_layouts[5])
            slide.shapes.title.text = section["title"]
            slide.shapes.add_picture(
                section["image"],
                Inches(2), Inches(1.8),
                width=Inches(9)
            )
            if "caption" in section:
                txBox = slide.shapes.add_textbox(
                    Inches(2), Inches(6.5), Inches(9), Inches(0.5)
                )
                txBox.text_frame.paragraphs[0].text = section["caption"]

    # Thank you slide
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    txBox = slide.shapes.add_textbox(
        Inches(4), Inches(3), Inches(5), Inches(1.5)
    )
    tf = txBox.text_frame
    tf.paragraphs[0].text = "Thank You"
    tf.paragraphs[0].font.size = Pt(44)
    tf.paragraphs[0].font.bold = True

    prs.save(output_path)
    return output_path
```

### Method/Results Slide Pattern

```python
def create_method_results_slide(prs, method_name: str,
                                 diagram_path: str,
                                 key_points: list[str]):
    """Create a slide with method diagram and key points side by side."""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = method_name

    # Left: diagram
    slide.shapes.add_picture(
        diagram_path,
        Inches(0.5), Inches(1.5),
        width=Inches(6)
    )

    # Right: key points
    txBox = slide.shapes.add_textbox(
        Inches(7), Inches(1.5), Inches(5.5), Inches(5)
    )
    tf = txBox.text_frame
    tf.word_wrap = True

    for i, point in enumerate(key_points):
        if i == 0:
            tf.paragraphs[0].text = f"• {point}"
        else:
            p = tf.add_paragraph()
            p.text = f"• {point}"
        tf.paragraphs[i].font.size = Pt(18)

    return slide
```

## Working with Existing Presentations

### Open and Modify

```python
prs = Presentation("existing.pptx")

# Iterate slides
for slide in prs.slides:
    for shape in slide.shapes:
        if shape.has_text_frame:
            print(shape.text)

# Modify specific slide
slide = prs.slides[2]  # 0-indexed
slide.shapes.title.text = "Updated Title"

prs.save("modified.pptx")
```

### Delete Slide

```python
def delete_slide(prs, index):
    """Delete slide at given index."""
    rId = prs.slides._sldIdLst[index].rId
    prs.part.drop_rel(rId)
    del prs.slides._sldIdLst[index]
```

## Common Patterns

### Consistent Styling Helper

```python
def apply_title_style(shape, font_size=32, bold=True, color=(0, 0, 0)):
    """Apply consistent title styling."""
    for para in shape.text_frame.paragraphs:
        para.font.size = Pt(font_size)
        para.font.bold = bold
        para.font.color.rgb = RgbColor(*color)
        para.font.name = "Arial"
```

### Add Slide Numbers

```python
def add_slide_numbers(prs, start_from=2):
    """Add slide numbers starting from specified slide."""
    from pptx.util import Inches, Pt

    for i, slide in enumerate(prs.slides):
        if i < start_from - 1:
            continue
        txBox = slide.shapes.add_textbox(
            Inches(12.5), Inches(7), Inches(0.5), Inches(0.3)
        )
        tf = txBox.text_frame
        tf.paragraphs[0].text = str(i + 1)
        tf.paragraphs[0].font.size = Pt(10)
```

## Output

Always save presentations to a user-accessible location:
- Working directory for project files
- Explicit path if user specifies
- Use `.pptx` extension

```python
# Good practice
output_path = "presentation_name.pptx"
prs.save(output_path)
print(f"Presentation saved to: {output_path}")
```
