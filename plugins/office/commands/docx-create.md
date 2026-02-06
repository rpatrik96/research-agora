---
name: docx-create
description: Create and edit Word documents using python-docx
model: haiku
version: 1.0.0
triggers:
  - document
  - word
  - docx
  - report
  - manuscript
dependencies:
  - python-docx>=0.8.11
  - Pillow>=9.0.0
---

# Word Document Creation Skill

> **Script-first**: This skill generates documents via python-docx scripts. No LLM generation needed.

Create professional Word documents programmatically using python-docx.

## Installation

```bash
pip install python-docx Pillow
```

## Core Concepts

### Document Structure
```
Document
├── Sections (page layout containers)
│   └── Section
│       ├── Headers/Footers
│       └── Page settings (margins, orientation)
├── Paragraphs
│   └── Runs (text with consistent formatting)
├── Tables
├── Images (inline shapes)
└── Styles (named formatting presets)
```

### Built-in Styles
| Style Name | Use Case |
|------------|----------|
| `Title` | Document title |
| `Heading 1-9` | Section headings |
| `Normal` | Body text |
| `List Bullet` | Bulleted lists |
| `List Number` | Numbered lists |
| `Quote` | Block quotes |
| `Caption` | Figure/table captions |
| `TOC Heading` | Table of contents |

## Quick Reference

### Create Basic Document

```python
from docx import Document
from docx.shared import Inches, Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

# Create document
doc = Document()

# Add title
doc.add_heading("Document Title", level=0)

# Add paragraphs
doc.add_paragraph("This is the introduction paragraph.")

# Add heading
doc.add_heading("Section 1", level=1)
doc.add_paragraph("Content for section 1.")

# Save
doc.save("document.docx")
```

### Text Formatting

```python
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Add paragraph with formatting
para = doc.add_paragraph()
para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

# Add formatted run
run = para.add_run("Bold and italic text")
run.bold = True
run.italic = True
run.font.size = Pt(12)
run.font.name = "Times New Roman"
run.font.color.rgb = RGBColor(0x00, 0x00, 0x80)  # Navy

# Add more text to same paragraph
run2 = para.add_run(" followed by normal text.")
run2.font.size = Pt(12)
```

### Paragraph Spacing

```python
from docx.shared import Pt

para = doc.add_paragraph("Text with custom spacing")
para_format = para.paragraph_format

para_format.space_before = Pt(12)  # Space before paragraph
para_format.space_after = Pt(12)   # Space after paragraph
para_format.line_spacing = 1.5     # Line spacing multiplier
para_format.first_line_indent = Inches(0.5)  # First line indent
```

### Lists

```python
# Bullet list
doc.add_paragraph("First bullet point", style="List Bullet")
doc.add_paragraph("Second bullet point", style="List Bullet")
doc.add_paragraph("Third bullet point", style="List Bullet")

# Numbered list
doc.add_paragraph("First item", style="List Number")
doc.add_paragraph("Second item", style="List Number")
doc.add_paragraph("Third item", style="List Number")

# Nested list (manual indentation)
p = doc.add_paragraph("Main point", style="List Bullet")
p = doc.add_paragraph("Sub-point", style="List Bullet")
p.paragraph_format.left_indent = Inches(0.5)
```

### Add Table

```python
from docx.shared import Inches, Pt
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# Create table
table = doc.add_table(rows=4, cols=3)
table.style = "Table Grid"
table.alignment = WD_TABLE_ALIGNMENT.CENTER

# Set column widths
for row in table.rows:
    row.cells[0].width = Inches(2)
    row.cells[1].width = Inches(2)
    row.cells[2].width = Inches(2)

# Header row
headers = ["Method", "Accuracy", "F1 Score"]
header_row = table.rows[0]
for i, header in enumerate(headers):
    cell = header_row.cells[i]
    cell.text = header
    # Bold header
    cell.paragraphs[0].runs[0].bold = True

# Data rows
data = [
    ["Baseline", "0.82", "0.79"],
    ["Ours (ablation)", "0.89", "0.86"],
    ["Ours (full)", "0.94", "0.92"],
]
for row_idx, row_data in enumerate(data):
    row = table.rows[row_idx + 1]
    for col_idx, value in enumerate(row_data):
        row.cells[col_idx].text = value

# Add caption below table
doc.add_paragraph("Table 1: Comparison of methods", style="Caption")
```

### Add Image

```python
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Add image with specific width (height auto-scaled)
doc.add_picture("figure.png", width=Inches(5))

# Center the image
last_para = doc.paragraphs[-1]
last_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Add caption
caption = doc.add_paragraph("Figure 1: Results visualization", style="Caption")
caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
```

### Page Setup

```python
from docx.shared import Inches, Cm
from docx.enum.section import WD_ORIENT

# Access current section
section = doc.sections[0]

# Page size (Letter: 8.5x11, A4: 21x29.7cm)
section.page_width = Inches(8.5)
section.page_height = Inches(11)

# Margins
section.top_margin = Inches(1)
section.bottom_margin = Inches(1)
section.left_margin = Inches(1)
section.right_margin = Inches(1)

# Orientation
section.orientation = WD_ORIENT.PORTRAIT  # or LANDSCAPE
```

### Headers and Footers

```python
from docx.enum.text import WD_ALIGN_PARAGRAPH

section = doc.sections[0]

# Header
header = section.header
header_para = header.paragraphs[0]
header_para.text = "Document Title"
header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Footer with page number
footer = section.footer
footer_para = footer.paragraphs[0]
footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Add page number field
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

run = footer_para.add_run()
fldChar1 = OxmlElement('w:fldChar')
fldChar1.set(qn('w:fldCharType'), 'begin')

instrText = OxmlElement('w:instrText')
instrText.text = "PAGE"

fldChar2 = OxmlElement('w:fldChar')
fldChar2.set(qn('w:fldCharType'), 'end')

run._r.append(fldChar1)
run._r.append(instrText)
run._r.append(fldChar2)
```

### Table of Contents (placeholder)

```python
def add_toc(doc):
    """Add Table of Contents placeholder.

    Note: Actual TOC is generated by Word when document is opened.
    User needs to right-click and 'Update Field' to populate.
    """
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    para = doc.add_paragraph()
    run = para.add_run()

    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')

    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'TOC \\o "1-3" \\h \\z \\u'

    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')

    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')

    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)

    # Add note for user
    doc.add_paragraph(
        "(Right-click and select 'Update Field' to generate TOC)",
        style="Caption"
    )
```

## Academic/Research Templates

### Research Report Template

```python
def create_research_report(
    title: str,
    authors: list[str],
    abstract: str,
    sections: dict[str, str],
    references: list[str],
    output_path: str
):
    """
    Create an academic-style research report.

    Args:
        title: Report title
        authors: List of author names
        abstract: Abstract text
        sections: Dict of {section_title: content}
        references: List of reference strings
        output_path: Where to save
    """
    from docx import Document
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()

    # Page setup
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    # Title
    title_para = doc.add_heading(title, level=0)
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Authors
    authors_para = doc.add_paragraph(", ".join(authors))
    authors_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Abstract
    doc.add_heading("Abstract", level=1)
    abstract_para = doc.add_paragraph(abstract)
    abstract_para.paragraph_format.first_line_indent = Inches(0)

    # Main sections
    for section_title, content in sections.items():
        doc.add_heading(section_title, level=1)

        # Split content by paragraphs
        for para_text in content.split("\n\n"):
            if para_text.strip():
                para = doc.add_paragraph(para_text.strip())
                para.paragraph_format.first_line_indent = Inches(0.5)

    # References
    doc.add_heading("References", level=1)
    for i, ref in enumerate(references, 1):
        ref_para = doc.add_paragraph(f"[{i}] {ref}")
        ref_para.paragraph_format.first_line_indent = Inches(-0.5)
        ref_para.paragraph_format.left_indent = Inches(0.5)

    doc.save(output_path)
    return output_path
```

### Technical Documentation Template

```python
def create_technical_doc(
    title: str,
    version: str,
    sections: list[dict],
    output_path: str
):
    """
    Create technical documentation.

    Args:
        title: Document title
        version: Version string
        sections: List of {
            "heading": str,
            "level": int (1-3),
            "content": str | list[str],
            "code": str (optional)
        }
        output_path: Output file path
    """
    from docx import Document
    from docx.shared import Pt, Inches
    from docx.enum.style import WD_STYLE_TYPE

    doc = Document()

    # Title page
    doc.add_heading(title, level=0)
    doc.add_paragraph(f"Version: {version}")
    doc.add_page_break()

    # Add TOC placeholder
    doc.add_heading("Table of Contents", level=1)
    add_toc(doc)
    doc.add_page_break()

    # Content sections
    for section in sections:
        doc.add_heading(section["heading"], level=section["level"])

        content = section["content"]
        if isinstance(content, list):
            for item in content:
                doc.add_paragraph(item, style="List Bullet")
        else:
            doc.add_paragraph(content)

        # Code block (if present)
        if "code" in section:
            code_para = doc.add_paragraph()
            code_run = code_para.add_run(section["code"])
            code_run.font.name = "Courier New"
            code_run.font.size = Pt(10)
            code_para.paragraph_format.left_indent = Inches(0.5)

    doc.save(output_path)
    return output_path
```

## Working with Existing Documents

### Open and Modify

```python
doc = Document("existing.docx")

# Iterate paragraphs
for para in doc.paragraphs:
    print(para.text)
    print(f"  Style: {para.style.name}")

# Modify text
doc.paragraphs[0].text = "New first paragraph"

# Find and replace (simple)
for para in doc.paragraphs:
    if "OLD_TEXT" in para.text:
        para.text = para.text.replace("OLD_TEXT", "NEW_TEXT")

doc.save("modified.docx")
```

### Extract Text

```python
def extract_text(docx_path: str) -> str:
    """Extract all text from a Word document."""
    doc = Document(docx_path)
    full_text = []

    for para in doc.paragraphs:
        full_text.append(para.text)

    # Also extract from tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                full_text.append(cell.text)

    return "\n".join(full_text)
```

## Common Patterns

### Consistent Styling

```python
def set_document_font(doc, font_name="Times New Roman", font_size=12):
    """Set default font for entire document."""
    from docx.shared import Pt

    style = doc.styles["Normal"]
    font = style.font
    font.name = font_name
    font.size = Pt(font_size)
```

### Add Hyperlink

```python
def add_hyperlink(paragraph, text, url):
    """Add a hyperlink to a paragraph."""
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    part = paragraph.part
    r_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True
    )

    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)

    new_run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")

    # Blue underlined text
    c = OxmlElement("w:color")
    c.set(qn("w:val"), "0000FF")
    rPr.append(c)

    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rPr.append(u)

    new_run.append(rPr)
    new_run.text = text
    hyperlink.append(new_run)

    paragraph._p.append(hyperlink)
    return hyperlink
```

### Footnotes

```python
def add_footnote(paragraph, footnote_text):
    """Add a footnote to a paragraph.

    Note: python-docx has limited footnote support.
    This creates a superscript reference; full footnote
    functionality requires manual XML manipulation.
    """
    run = paragraph.add_run()
    run.font.superscript = True
    run.text = "*"

    # Add footnote text at end of document
    # (Simplified - real footnotes need XML work)
    return run
```

## Output Best Practices

```python
# Always use .docx extension
output_path = "report.docx"
doc.save(output_path)
print(f"Document saved to: {output_path}")

# For large documents, save incrementally
import os
temp_path = output_path + ".tmp"
doc.save(temp_path)
os.replace(temp_path, output_path)  # Atomic replace
```

## Limitations

- **No direct PDF export**: Use LibreOffice or Word for PDF conversion
- **Limited style editing**: Complex styles may need XML manipulation
- **No tracked changes**: python-docx can't create/read track changes
- **Image positioning**: Only inline images, no floating/anchor support
