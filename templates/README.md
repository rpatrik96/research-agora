# Presentation Templates

This directory contains tools for analyzing and adding design templates for slides and posters. Claude Code uses these templates to maintain consistent branding when creating new presentations.

## Directory Structure

Templates are stored within their respective plugin directories:

```
research-agora/
├── templates/
│   ├── analyze_template.py    # Script to extract design specs from PPTX
│   ├── add-template.sh        # Helper script
│   └── README.md              # This file
├── plugins/
│   ├── office/templates/slides/       # Slide presentation templates
│   │   └── {template-name}/
│   │       ├── template.pptx  # Original PPTX file
│   │       ├── STYLE.md       # Extracted design specifications
│   │       └── specs.json     # Machine-readable specs
│   └── academic/templates/posters/    # Poster templates
│       └── {template-name}/
│           ├── template.pptx
│           ├── STYLE.md
│           └── specs.json
```

## Adding a New Template

### Quick Method

```bash
cd /path/to/research-agora/templates

# For slides (outputs to plugins/office/templates/slides/)
python analyze_template.py /path/to/your/template.pptx --output slides --name "My Template"

# For posters (outputs to plugins/academic/templates/posters/)
python analyze_template.py /path/to/your/poster.pptx --output posters --name "Conference Poster"
```

This will:
1. Copy the template to the appropriate directory
2. Extract colors, fonts, sizes, and layouts
3. Generate `STYLE.md` with human-readable specs
4. Generate `specs.json` for programmatic access

### Manual Method

1. Create directory: `plugins/office/templates/slides/{template-name}/` (or `plugins/academic/templates/posters/`)
2. Copy your `.pptx` file there
3. Create `STYLE.md` with design notes (see example below)

## Template STYLE.md Format

```markdown
# Template Name

Brief description of when to use this template.

## Dimensions
- Width: 13.33"
- Height: 7.5"
- Aspect Ratio: 16:9

## Color Palette
- Primary: #003366 (Dark blue)
- Secondary: #0066CC (Light blue)
- Accent: #FF9900 (Orange)
- Background: #FFFFFF (White)
- Text: #333333 (Dark gray)

## Typography
- Title Font: Arial Bold, 44pt
- Subtitle Font: Arial, 32pt
- Body Font: Arial, 24pt
- Caption Font: Arial, 14pt

## Layouts
1. Title Slide - For opening
2. Section Header - For chapter breaks
3. Content - Standard bullet points
4. Two Column - Side-by-side content
5. Image with Caption - Figure-focused

## Usage Notes
- Keep logos in top-right corner
- Use accent color for emphasis only
- Maintain 1" margins on all sides
```

## Using Templates in Claude Code

When asked to create slides or posters, Claude will:

1. Check `~/.claude/skills/templates/slides/` or `~/.claude/skills/templates/posters/` for templates
2. Read the `STYLE.md` to understand design specifications
3. Apply colors, fonts, and layouts consistently
4. Optionally copy the original `.pptx` as a starting point

### Example Prompt

```
Create a presentation for my NeurIPS paper using the "iem-talk" template.
```

Claude will read the template's STYLE.md and follow those specifications.

## Best Practices

1. **Use descriptive names**: `neurips-2024` not `template1`
2. **Include the original**: Keep the `.pptx` for reference
3. **Document special elements**: Note any custom shapes, logos, animations
4. **Test the extraction**: Verify `STYLE.md` captured the key design elements
5. **Update skills**: Add template references to `paper-slides` and `paper-poster` skills

## Supported Formats

| Format | Support |
|--------|---------|
| `.pptx` | Full support (analyze_template.py) |
| `.ppt` | Convert to .pptx first |
| `.key` | Export as .pptx first |
| Google Slides | Download as .pptx first |

## Requirements

```bash
pip install python-pptx
```
