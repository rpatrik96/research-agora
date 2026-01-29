---
name: paper-slides
description: |
  Create presentation slides from research papers for talks and seminars. Use when asked to
  "create slides", "make presentation", "turn paper into slides", "prepare talk".
model: sonnet
---

# Paper to Slides Skill

Transform ML research papers into engaging presentation slides for conference talks, seminars, and group meetings. Output is structured content ready for Google Slides or PowerPoint.

## Workflow

1. **Understand the context** - Ask about talk duration, audience, and emphasis
2. **Read the paper thoroughly** - Identify narrative arc and key contributions
3. **Create slide outline** - Plan the story structure
4. **Write slide content** - Generate text, identify figures, note animations
5. **Specify visual requirements** - List diagrams to create or adapt
6. **Output structured content** - Provide slide-by-slide content
7. **Provide MCP instructions** - Guide user on Google Slides integration

## Talk Duration Guidelines

| Duration | Slides | Content Focus |
|----------|--------|---------------|
| 5 min (spotlight) | 5-7 | Problem + Key result only |
| 15 min (contributed) | 12-18 | Full story, streamlined |
| 20-25 min (oral) | 18-25 | Complete with some depth |
| 45-60 min (invited) | 35-50 | Deep dive, background |

Rule of thumb: **1-2 minutes per slide** (excluding title/backup)

## Slide Structure

### Standard ML Talk Structure

```
1. Title Slide
2-3. Motivation / Problem Setup
4-5. Background / Related Work (brief)
6-10. Method / Approach
11-14. Experiments / Results
15-16. Conclusion / Takeaways
17. Thank You + Questions
[Backup slides as needed]
```

### Detailed Breakdown

#### 1. Title Slide
- Paper title (can be shortened for talk)
- Authors (highlight presenter)
- Affiliations + logos
- Conference/venue + date
- Optional: One compelling figure

#### 2-3. Motivation Slides
- **Slide 2**: Problem statement with visual example
- **Slide 3**: "Why is this hard?" / Current limitations
- Hook the audience in first 2 minutes

#### 4-5. Background (Optional)
- Only include if audience needs it
- Define key concepts briefly
- Reference prior work without deep diving
- Skip for expert audiences

#### 6-10. Method Slides
- **Build up gradually**: Simple → Complex
- One main idea per slide
- Heavy use of diagrams
- Equations: show intuition, derive in backup
- Animation suggestions for complex processes

#### 11-14. Results Slides
- Lead with the most impressive result
- Highlight key numbers (bold, color)
- Explain what the plot shows before showing it
- Compare to baselines clearly
- Include ablations for important design choices

#### 15-16. Conclusion
- **Slide 15**: Summary of contributions (3-4 bullets)
- **Slide 16**: Limitations + Future work (honest)
- End on a strong note

#### 17. Thank You Slide
- "Questions?" or "Thank you"
- Contact info, paper link, code link
- QR codes for paper/project page

#### Backup Slides
- Detailed derivations
- Additional experiments
- Ablation studies
- Implementation details
- Related work deep dive

## Template System

Before creating slides, check for available design templates:

```bash
# List available templates
ls ~/.claude/skills/templates/slides/
```

### Using a Template

1. **Read the style guide**: `cat templates/slides/{template-name}/STYLE.md`
2. **Copy as base**: Use the `.pptx` file as starting point
3. **Follow specs**: Match colors, fonts, and layouts from STYLE.md

### Template Location
Templates are stored in the claude-skills repo:
```
templates/
├── slides/
│   └── {template-name}/
│       ├── template.pptx   # Original file to copy
│       ├── STYLE.md        # Design specifications
│       └── specs.json      # Machine-readable specs
└── posters/
```

### Adding New Templates

```bash
# Templates are stored in the research-agora marketplace
# Clone or update the repository first, then run from its templates directory:
cd /path/to/research-agora/templates
python analyze_template.py /path/to/your/template.pptx --output slides --name "template-name"

# After analysis, templates are available at ~/.claude/skills/templates/slides/{template-name}/
```

## Slide Design Principles

### Typography (Override with Template)
- **Title**: 36-44pt bold
- **Body bullets**: 24-32pt
- **Minimal text**: Max 6 lines per slide
- **Font**: Sans-serif (match template)

### Visual Hierarchy
```
[Title - 10% of slide]
[Main content - 80% of slide]
[Footer/page number - 10% of slide]
```

### Colors & Style
When no template is specified, use:
- Clean, minimal design
- Consistent accent color for highlights
- White/light background for readability
- Dark text for contrast
- Institution colors for branding

**If template exists**: Read `STYLE.md` for exact color codes and apply them.

---

## IEM Template Style Guide

When using the `iem-talk/IEM_intuitive.pptx` template, apply these exact specifications:

### Slide Dimensions
- **Format**: Widescreen 16:9
- **Size**: 13.33" × 7.50" (960 × 540 px at 72 dpi)

### Color Palette

| Color | Hex Code | Usage |
|-------|----------|-------|
| **Primary Blue** | `#4A8FE3` | Titles, underlines, footer bar, emphasis text, buttons |
| **Success Green** | `#00B050` | Positive results, checkmarks, correct answers |
| **Error Red** | `#D1011B` | Negative results, warnings, incorrect items |
| **Bright Red** | `#FF0000` | Strong emphasis, critical highlights |
| **Navy Dark** | `#21366D` | Rarely used, secondary accent |
| **Text Black** | Default | Body text, bullet points |
| **Background** | White | All slides |

### Typography

| Element | Font | Size | Color | Weight |
|---------|------|------|-------|--------|
| **Slide title** | Helvetica Neue Medium | 32pt | `#4A8FE3` | Medium |
| **Title slide title** | Helvetica Neue Medium | 40pt | `#4A8FE3` | Medium |
| **Body text** | Helvetica Neue Light | 20-24pt | Black | Light |
| **Captions/Labels** | Helvetica Neue Light | 14pt | Black or `#4A8FE3` | Light |
| **Slide number** | Helvetica Neue Light | 14pt | Black | Light |
| **Button/Tag text** | Helvetica Neue Light | 20pt | White | Light |

### Layout Specifications

```
+------------------------------------------------------------------+
|  TITLE (32pt, #4A8FE3)                            top: 0.22"     |
|  left: 0.12"   width: 12.94"   height: 0.64"                     |
+------------------------------------------------------------------+
|  BLUE UNDERLINE (full width, #4A8FE3)             top: 0.98"     |
|  left: 0.00"   width: 13.33"   thickness: ~2pt                   |
+==================================================================+
|                                                                  |
|                        CONTENT AREA                               |
|                     (top: 1.0" to 7.0")                           |
|                                                                  |
|                                                                  |
+------------------------------------------------------------------+
|  FOOTER BAR (solid #4A8FE3)                       top: 7.00"     |
|  left: 0.00"   width: 13.33"   height: 0.50"                     |
|                                    SLIDE NUMBER → (12.59", 7.11")|
+------------------------------------------------------------------+
```

### Key Visual Elements

#### 1. Slide Title
- Position: (0.12", 0.22")
- Size: 12.94" × 0.64"
- Font: Helvetica Neue Medium, 32pt, `#4A8FE3`
- Left-aligned

#### 2. Title Underline
- Full-width blue horizontal line
- Position: (0.00", 0.98")
- Color: `#4A8FE3`
- Separates title from content

#### 3. Footer Bar
- Full-width solid blue rectangle
- Position: (0.00", 7.00")
- Size: 13.33" × 0.50"
- Color: `#4A8FE3` solid fill

#### 4. Slide Number
- Position: (12.59", 7.11") — bottom-right corner
- Size: 0.31" × 0.34" text box
- Font: Helvetica Neue Light, 14pt, Black
- Sits on top of the blue footer bar

#### 5. Buttons/Tags (optional)
- Rounded rectangle with solid `#4A8FE3` fill
- White text inside (Helvetica Neue Light, 20pt)
- Typical size: ~2.28" × 0.54"
- Used for section labels, category markers

### Title Slide Layout

The title slide has a different layout:
- **Title**: Helvetica Neue Medium, 40pt, `#4A8FE3`, centered or left-aligned
- **Position**: (0.20", 2.82") — vertically centered
- **Authors**: Helvetica Neue Light, 24pt, `#4A8FE3`
- **Date**: Bottom-right, Helvetica Neue Light, 14pt
- **Logos**: Institution logos near bottom
- **Footer bar**: Same as content slides (full width at bottom)

### Emphasis Styles

| Purpose | Style |
|---------|-------|
| **Highlight key terms** | Blue text (`#4A8FE3`) |
| **Strong emphasis** | Bold (same color) |
| **Positive results** | Green text (`#00B050`) |
| **Negative/warning** | Red text (`#D1011B`) |
| **Code/technical** | Monospace font, smaller size |

### Arrows and Connectors
- Color: `#4A8FE3` (blue)
- Style: Straight or curved arrows matching content flow
- Used to connect concepts in diagrams

---

### Figures
- One main figure per slide (large)
- Annotations and highlights
- Build-up animations for complex figures
- Consistent style across all figures

## Content Writing Guidelines

### Bullet Points
- Start with action verb or key noun
- Max 7 words per bullet
- Parallel structure
- No full sentences

**Good:**
```
• Disentangles latent factors
• Scales to high dimensions
• Requires no supervision
```

**Bad:**
```
• Our method is able to disentangle latent factors effectively
• The approach can scale to higher dimensional settings
• No supervision is required for training
```

### Transitions
Use verbal transitions, not written ones:
- "Now let's look at..."
- "The key insight is..."
- "This leads to..."

### Equations
- Show only essential equations
- Build up step by step
- Highlight key terms with color
- Keep backup slides for full derivations

## Animation Suggestions

For complex concepts, suggest animations:

```markdown
### Slide: Method Overview
[Animation: Build]
1. First show input data
2. Add encoder block
3. Add latent space
4. Add decoder block
5. Show full pipeline with arrows
```

## Google Slides MCP Integration

### Recommended MCP Servers

1. **google-slides-mcp** (matteoantoci)
   - GitHub: https://github.com/matteoantoci/google-slides-mcp
   - Tools: `create_presentation`, `batch_update_presentation`, `get_presentation`

2. **Google Workspace MCP Server**
   - URL: https://workspacemcp.com/
   - Full suite including Slides, Docs, Drive

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

## Output Format

When generating slide content, provide:

```markdown
## PRESENTATION: [Paper Title]
Duration: [X minutes]
Audience: [Conference/Seminar/Group meeting]

---

### Slide 1: Title
**Title:** [Talk title]
**Subtitle:** [Conference, Date]
**Authors:** [List with affiliations]
**Visual:** [Optional figure description]

---

### Slide 2: The Problem
**Title:** [Slide title]
**Bullets:**
- [Point 1]
- [Point 2]
- [Point 3]
**Visual:** [Figure description or "None"]
**Speaker notes:** [What to say]

---

### Slide 3: Why Is This Hard?
...

---

### Backup Slides

#### B1: Derivation of Equation 3
...
```

## Checklist

Before finalizing slides:

- [ ] Story flows naturally without paper reference
- [ ] One main idea per slide
- [ ] No slide has >6 bullet points
- [ ] All figures are self-explanatory
- [ ] Backup slides cover anticipated questions
- [ ] Timing checked (1-2 min/slide)
- [ ] Speaker notes included for key slides
- [ ] Contact info and links on final slide
- [ ] Consistent formatting throughout

## Anti-Patterns

- **Reading slides verbatim**: Slides support speech, not replace it
- **Wall of text**: If you can't see it from back row, remove it
- **Dense equations**: Build up, don't dump
- **Too many slides**: Quality over quantity
- **No narrative**: Slides should tell a story
- **Skipping motivation**: Audience needs to care first
- **Rushing results**: Your best work deserves time
- **No backup slides**: Be prepared for questions

## Audience Adaptation

### Expert Audience (Conference Talk)
- Minimal background
- Focus on technical novelty
- Assume familiarity with domain

### General ML Audience (Seminar)
- Brief background section
- Intuition before formalism
- Broader context

### Non-Expert (Invited Talk)
- Extended motivation
- Visual explanations
- Minimize equations
- Real-world applications
