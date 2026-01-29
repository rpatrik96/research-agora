---
name: paper-twitter
description: |
  Create Twitter/X threads to announce and explain research papers. Use when asked to
  "write twitter thread", "create tweet thread", "announce paper on twitter", "paper tweet".
model: sonnet
---

# Paper to Twitter Thread Skill

Transform ML research papers into engaging Twitter/X threads for paper announcements, reaching broader audiences and increasing research visibility.

## Workflow

1. **Read the paper** - Understand contribution, key results, and visual appeal
2. **Identify the hook** - What makes this paper interesting/surprising?
3. **Plan thread structure** - Outline the narrative (8-15 tweets)
4. **Write tweets** - Craft each tweet with character limits in mind
5. **Select visuals** - Identify figures/GIFs to include
6. **Add engagement elements** - Links, mentions, hashtags
7. **Review and refine** - Ensure thread flows and fits character limits

## Thread Structure

### Standard Paper Announcement Thread

```
1. 🔥 Hook tweet (announce paper + key claim)
2. 🎯 Problem/motivation
3-4. 💡 Key insight / method overview
5-7. 📊 Main results (with figures)
8. 🤔 Why this matters / implications
9. 👥 Credits + acknowledgments
10. 🔗 Links (paper, code, project page)
```

### Tweet-by-Tweet Breakdown

#### Tweet 1: The Hook
- Start with attention grabber
- State the main contribution
- Include paper title
- Add 1-2 relevant emojis

**Format:**
```
🔥 New paper: "[Title]"

[One-sentence summary of what you achieved]

[Optional: surprising number or claim]

🧵 Thread 👇
```

**Example:**
```
🔥 New paper: "Disentangling Identifiability"

We prove that VAEs can provably recover true latent factors without supervision!

Spoiler: geometry is the key 📐

🧵 Thread 👇
```

#### Tweet 2: The Problem
- What problem are you solving?
- Why should people care?
- Keep accessible

**Format:**
```
🎯 The problem:

[2-3 sentences explaining the challenge in plain language]

[Optional: why existing approaches fail]
```

#### Tweets 3-4: The Solution
- High-level method overview
- Key insight that makes it work
- Avoid jargon, use intuition

**Format:**
```
💡 Our key insight:

[Plain language explanation of the core idea]

[Optional: simple analogy]
```

#### Tweets 5-7: Results
- Lead with most impressive result
- Include figures (crucial for engagement)
- Explain what the figure shows

**Format:**
```
📊 Results:

[Key finding in plain language]

[Specific numbers if impressive]

[Figure attached]
```

#### Tweet 8: Why It Matters
- Broader implications
- Potential applications
- Future directions

#### Tweet 9: Credits
- Co-authors (tag them!)
- Advisors/mentors
- Funding acknowledgment (if required)

#### Tweet 10: Links
- arXiv link
- Code repository
- Project page
- Blog post (if exists)

## Writing Guidelines

### Character Limits
- **Standard tweet**: 280 characters
- **With media**: 280 characters (media doesn't count)
- **Thread indicator**: Include "🧵" or "(1/n)" sparingly

### Tone
- **Accessible**: Write for smart non-experts
- **Enthusiastic**: Show genuine excitement
- **Humble**: Avoid overclaiming
- **Personal**: "We" not "The authors"

### Language Tips
- Use active voice
- Short sentences
- One idea per tweet
- Define jargon or avoid it

**Good:** "We show that X leads to Y"
**Bad:** "It has been demonstrated that X is correlated with Y"

### Emojis (Use Sparingly)
- 🔥 New/exciting work
- 🎯 Problem/goal
- 💡 Key insight
- 📊 Results/data
- 🤔 Implications
- 👥 People/team
- 🔗 Links
- 📄 Paper
- 💻 Code
- 🧵 Thread

### Hashtags (End of Thread)
- #MachineLearning or #ML
- Conference tag: #NeurIPS2024, #ICML2024, #ICLR2025
- Topic tags: #DeepLearning, #CausalML, #Representation

## Visual Content

### What to Include
1. **Main result figure** - Most impactful visualization
2. **Method diagram** - Simplified pipeline
3. **Comparison plot** - Your method vs baselines
4. **GIF/animation** - For dynamic results (optional)

### Image Guidelines
- High contrast, readable on mobile
- Add annotations if needed
- Alt text for accessibility
- 16:9 or 1:1 aspect ratio preferred

### Creating Thread Images
If paper figures need adaptation:
- Increase font sizes
- Simplify legends
- Add "Our method" labels
- Use brand colors

## Engagement Strategies

### Mentions
- Tag co-authors: "@coauthor"
- Tag lab/institution: "@LabAccount"
- Tag relevant researchers (sparingly, if work builds on theirs)

### Timing
- Post when your audience is active
- ML Twitter: Weekday mornings (US time zones)
- Conference announcements: When acceptances are public

### Follow-up
- Reply to questions
- Quote-tweet with additional insights
- Pin the thread to profile

## Output Format

```markdown
## TWITTER THREAD: [Paper Title]

---

**Tweet 1/10** (Hook)
🔥 New paper: "[Title]"

[Hook sentence]

🧵👇

[Characters: X/280]

---

**Tweet 2/10** (Problem)
🎯 The problem:

[Problem description]

[Characters: X/280]

---

**Tweet 3/10** (Insight)
💡 Key insight:

[Core idea]

[Characters: X/280]
[FIGURE: method_diagram.png]

---

... [continue for all tweets]

---

**Tweet 10/10** (Links)
📄 Paper: [arXiv URL]
💻 Code: [GitHub URL]
🌐 Project: [Project page URL]

#MachineLearning #NeurIPS2024

[Characters: X/280]

---

## ALT TEXT FOR IMAGES

**Image 1 (Tweet 3):**
[Detailed description for accessibility]

**Image 2 (Tweet 5):**
[Detailed description for accessibility]
```

## Checklist

Before posting:

- [ ] Hook tweet is compelling (would you click?)
- [ ] Each tweet stands alone but flows in sequence
- [ ] All tweets under 280 characters
- [ ] Figures are mobile-readable
- [ ] Co-authors tagged correctly
- [ ] Links are correct and working
- [ ] Alt text provided for images
- [ ] Hashtags at end, not overdone
- [ ] No typos or broken threads
- [ ] Tone is enthusiastic but accurate

## Anti-Patterns

- **Overclaiming**: "We solved AGI" when you improved a benchmark
- **Wall of text**: Long dense tweets lose readers
- **Too technical**: "We optimize the ELBO" means nothing to most
- **No visuals**: Text-only threads get less engagement
- **Forgetting links**: Always include paper link
- **Thread too long**: 8-12 tweets is ideal, 15+ loses people
- **Self-promotion only**: Engage with the community, not just broadcast
- **Ignoring replies**: Respond to genuine questions

## Examples of Great ML Threads

Study successful paper threads from:
- @kaborojevic (visual, accessible)
- @poolio (technical depth)
- @ylaboratory (clear explanations)
- @random_forests (engaging hooks)

## Platform Notes

### Twitter/X
- Primary platform for ML community
- Quote-tweets help visibility
- Threads can be edited after posting

### Alternative: LinkedIn
- More professional tone
- Single long post often better than thread
- Include paper PDF preview

### Alternative: Threads (Meta)
- Growing ML presence
- Similar format to Twitter
- Cross-post for reach
