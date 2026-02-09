---
name: paper-poster
description: |
  Create academic conference posters from research papers. Use when asked to
  "create poster", "make poster", "turn paper into poster", "poster for conference".
model: sonnet
metadata:
  research-domain: general
  research-phase: dissemination
  task-type: dissemination
  verification-level: none
---

# Paper to Poster Skill

> **LLM-required**: Creating poster content requires visual layout decisions and content distillation. No script alternative.

Transform ML research papers into visually compelling conference posters for venues like NeurIPS, ICML, and ICLR. Output is structured content ready for Google Slides or PowerPoint.

## Workflow

1. **Read the paper** - Understand core contribution, key results, and visual elements
2. **Extract poster content** - Identify title, authors, motivation, method, results, conclusion
3. **Plan visual layout** - Determine panel arrangement and figure placement
4. **Write concise text** - Convert paper prose to poster-friendly bullet points
5. **Specify figure requirements** - List which figures/tables to include or recreate
6. **Output structured content** - Provide content blocks ready for slide tools
7. **Provide MCP instructions** - Guide user on Google Slides integration

## Poster Structure (Standard Academic Format)

### Panel Layout (Left to Right, Top to Bottom)

```
┌─────────────────────────────────────────────────────────────┐
│                     TITLE + AUTHORS + LOGOS                  │
├───────────────────┬───────────────────┬─────────────────────┤
│    MOTIVATION     │      METHOD       │      RESULTS        │
│   (Why this?)     │   (How we do it)  │   (What we found)   │
├───────────────────┼───────────────────┼─────────────────────┤
│   KEY INSIGHT     │   MAIN FIGURE     │    CONCLUSION       │
│   or BACKGROUND   │   (Central viz)   │    + QR CODE        │
└───────────────────┴───────────────────┴─────────────────────┘
```

### Alternative: Two-Column Layout

```
┌─────────────────────────────────────────────────────────────┐
│                     TITLE + AUTHORS + LOGOS                  │
├─────────────────────────────┬───────────────────────────────┤
│         MOTIVATION          │           RESULTS             │
│         BACKGROUND          │         (Key plots)           │
├─────────────────────────────┼───────────────────────────────┤
│          METHOD             │         CONCLUSION            │
│       (Main figure)         │     TAKEAWAYS + QR CODE       │
└─────────────────────────────┴───────────────────────────────┘
```

## Content Guidelines

### Title Block
- **Title**: Same as paper, possibly shortened
- **Authors**: Full names with affiliations
- **Logos**: Institution logos (ETH, MPI, etc.)
- **Contact**: Email or QR code to paper

### Motivation Panel (WHY)
- 2-3 bullet points maximum
- State the problem clearly
- Why should the audience care?
- What gap does this fill?

Example:
```
• Current methods fail when [specific limitation]
• Real-world applications require [capability]
• No existing approach handles [challenge]
```

### Method Panel (HOW)
- Visual-first: diagram > equations > text
- 1-2 key equations if essential (large font)
- Flow diagram showing pipeline
- Highlight novel components

### Results Panel (WHAT)
- 2-3 key figures/tables
- Bold the best numbers
- Clear axis labels (larger than paper)
- Comparative results vs baselines

### Conclusion Panel
- 3-4 bullet takeaways
- Future directions (optional)
- QR code linking to:
  - Paper PDF
  - Code repository
  - Project page

## Template System

Before creating posters, check for available design templates:

```bash
# List available templates
ls ~/.claude/skills/templates/posters/
```

### Using a Template

1. **Read the style guide**: `cat templates/posters/{template-name}/STYLE.md`
2. **Copy as base**: Use the `.pptx` file as starting point
3. **Follow specs**: Match colors, fonts, and layouts from STYLE.md

### Template Location
Templates are stored in the claude-skills repo:
```
templates/
├── slides/
└── posters/
    └── {template-name}/
        ├── template.pptx   # Original file to copy
        ├── STYLE.md        # Design specifications
        └── specs.json      # Machine-readable specs
```

### Adding New Templates

```bash
# Templates are stored in the research-agora marketplace
# Clone or update the repository first, then run from its templates directory:
cd /path/to/research-agora/templates
python analyze_template.py /path/to/your/poster.pptx --output posters --name "conference-name"

# After analysis, templates are available at ~/.claude/skills/templates/posters/{template-name}/
```

## Visual Design Principles

### Typography (Override with Template)
- **Title**: 72-96pt bold
- **Section headers**: 48-60pt bold
- **Body text**: 32-40pt regular
- **Figure captions**: 24-28pt
- **Font**: Sans-serif (Helvetica, Arial, or Source Sans Pro)

### Colors
When no template is specified:
- Use institution brand colors for headers/accents
- Maintain high contrast for readability
- Colorblind-safe palettes for figures
- White or light gray background

**If template exists**: Read `STYLE.md` for exact color codes and apply them.

### Figures
- Higher resolution than paper (300+ DPI)
- Larger axis labels and legends
- Remove unnecessary detail
- Add annotations pointing to key features

## Google Slides MCP Integration

### Recommended MCP Servers

1. **google-slides-mcp** (matteoantoci)
   - GitHub: https://github.com/matteoantoci/google-slides-mcp
   - Install: `npm install -g google-slides-mcp`
   - Tools: `create_presentation`, `batch_update_presentation`

2. **Google Workspace MCP Server**
   - URL: https://workspacemcp.com/
   - Full Google Workspace integration
   - One-click DXT install for Claude Desktop

### Setup Instructions

```json
// Add to claude_desktop_config.json
{
  "mcpServers": {
    "google-slides": {
      "command": "npx",
      "args": ["-y", "google-slides-mcp"],
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id",
        "GOOGLE_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

### OAuth Setup
1. Go to Google Cloud Console
2. Create OAuth 2.0 credentials
3. Enable Google Slides API
4. Add credentials to MCP config

## Output Format

When generating poster content, provide:

```markdown
## POSTER CONTENT

### Title Block
- Title: [Paper title]
- Authors: [Author list with affiliations]
- Logos needed: [Institution names]

### Panel 1: Motivation
- Bullet 1: [Problem statement]
- Bullet 2: [Why it matters]
- Bullet 3: [Gap in literature]

### Panel 2: Method
- Key diagram: [Description of main method figure]
- Equation (if needed): [Key equation in LaTeX]
- Steps: [Numbered method steps]

### Panel 3: Results
- Figure 1: [Description + source from paper]
- Figure 2: [Description + source from paper]
- Key numbers: [Highlight metrics]

### Panel 4: Conclusion
- Takeaway 1: [Main contribution]
- Takeaway 2: [Key result]
- Takeaway 3: [Implications]
- Links: [Paper URL, Code URL]

### Figure Requirements
- [ ] Recreate Figure X at higher resolution
- [ ] Extract Table Y data for bar chart
- [ ] Create method diagram from Section Z
```

## Checklist

Before finalizing poster content:

- [ ] Title is readable from 2+ meters away
- [ ] Core message understandable in 30 seconds
- [ ] No more than 300 words total
- [ ] All figures are self-explanatory
- [ ] Contact/paper link included
- [ ] Institution branding present
- [ ] Consistent font sizes throughout
- [ ] High contrast color scheme
- [ ] QR code tested and working

## Anti-Patterns

- **Too much text**: Poster is not a paper printout
- **Small fonts**: Nothing below 24pt
- **Dense equations**: Show intuition, not derivations
- **Low-res figures**: Pixelation is unacceptable
- **Missing context**: Audience should understand without reading paper
- **No visual hierarchy**: Important things should stand out
- **Cluttered layout**: Whitespace is your friend
