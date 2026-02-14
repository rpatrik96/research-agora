---
name: register-translator
description: Translate writing between registers — paper to blog, blog to book chapter, academic to conversational. Use when asked to "convert this for blog", "make this more conversational", "translate register", "paper to blog", "blog to book", or "adapt for audience". Performs structural transformation, not just tone adjustment.
model: opus
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: writing
  verification-level: heuristic
---

# Register Translator

Translate writing between registers by transforming structure, detail level, examples, person, paragraph length, and jargon density — not just tone.

> **LLM-required**: Register translation requires understanding both source and target conventions — sentence structure expectations, jargon norms, rhetorical moves, and audience assumptions. No script alternative.

## Core Philosophy

This is NOT "make it more casual." Register translation is a structural transformation that changes:

- **Person**: Third-person passive to first-person active (or vice versa)
- **Structure**: Dense subsections to headers + short paragraphs (or vice versa)
- **Detail level**: Full hyperparameters to "standard settings" (or vice versa)
- **Examples**: Abstract/mathematical to concrete/relatable (or vice versa)
- **Jargon density**: Dense with definitions to minimal inline glosses (or vice versa)
- **Citation style**: Formal references to hyperlinks (or vice versa)

The goal is to preserve every technical claim while completely restructuring how those claims are delivered. Accuracy is non-negotiable. If a simplification loses precision, flag it.

## Supported Register Translations

### 1. Paper to Blog

**Source conventions**: Third-person passive, dense paragraphs (150-300 words), full hyperparameters for reproducibility, equations as primary explanatory tool, formal citations [Author, Year], moderate hedging.

**Target conventions**: First-person active ("I" or "we"), short paragraphs (50-100 words), essential details only, intuitive explanations replacing equations, hyperlinks replacing citations, confident voice with minimal hedging.

**Key transformations**:
- "The proposed method achieves..." becomes "Our method gets..."
- Equations become intuitive descriptions with optional "for the math-inclined" callouts
- Related work becomes a paragraph of context with links
- Full ablation tables become "we tried X, Y, Z — here's what mattered"
- Academic hedging ("our results suggest") becomes direct claims ("this works because")

### 2. Blog to Book Chapter

**Source conventions**: Standalone post, assumes no prior reading, self-contained examples, conversational hooks, 800-1500 words.

**Target conventions**: Chapter within a sequence, callbacks to previous chapters, foreshadowing of later ones, expanded examples from illustrative to immersive, deeper treatment that a 1000-word post cannot fit.

**Key transformations**:
- Add connective tissue: "In Chapter 3, we saw X. Now we extend that to..."
- Expand examples from one-paragraph illustrations to multi-paragraph narratives
- Add depth: the blog post says "X works"; the chapter explains why, when it doesn't, and what alternatives exist
- Remove redundant context-setting that earlier chapters already covered
- Add reflection sections that a blog post's pacing can't accommodate

### 3. Paper to General Audience

**Source conventions**: All jargon defined in intro but used freely thereafter, formulas as core communication, leads with "what we did", assumes domain familiarity.

**Target conventions**: Strip all jargon or define inline on every use, replace formulas with analogies, lead with "why this matters" not "what we did", add real-world examples that connect to the reader's experience.

**Key transformations**:
- "We minimize the KL divergence between the posterior and prior" becomes "We make the model's guesses match reality as closely as possible"
- Method sections become "how it works" with everyday analogies
- Results become "what this means for [concrete application]"
- Every claim gets a "why should you care?" framing

### 4. Blog to Paper

**Source conventions**: First-person, anecdotal evidence, conversational tone, no citations, practical framing, assertions without formal evidence.

**Target conventions**: Third-person (mostly), evidence-based claims, formal structure (intro/method/results/discussion), proper citations, tightened claims scoped to what the evidence supports, passive voice where actor is irrelevant.

**Key transformations**:
- Anecdotes become formal experiments or case studies with methodology
- "I found that X works" becomes "Empirical evaluation demonstrates that X achieves [metric] on [benchmark]"
- Add related work section contextualizing the claims
- Tighten every claim to what the evidence actually supports
- Remove first-person where possible (keep it for explicit author decisions: "We chose X because...")

### 5. Any to Grant

**Source conventions**: Varies.

**Target conventions**: Frame everything as "broader impact," connect technical work to societal outcomes, use funding agency language ("advance the state of the art," "enable new capabilities"), first-person plural ("we propose"), structured around aims/plan/impact.

**Key transformations**:
- Technical contributions become "aims" with measurable milestones
- Results become "preliminary data" that de-risks the proposal
- Future work becomes the core proposal with timeline and deliverables
- Add explicit "broader impact" and "intellectual merit" framing
- Connect every technical detail to a societal or scientific outcome

## Translation Dimensions Reference

| Dimension | Paper | Blog | Book | Grant |
|-----------|-------|------|------|-------|
| Person | 3rd/passive | 1st + 2nd | 1st | 1st plural |
| Paragraph length | 150-300 words | 50-100 words | 100-200 words | 100-200 words |
| Jargon | Dense, defined in intro | Minimal, defined inline | Progressive, defined early | Minimal, audience-aware |
| Examples | Abstract/mathematical | Concrete/relatable | Narrative/immersive | Impact-focused |
| Structure | Section/subsection | Headers + short paras | Chapter/scene/reflection | Aims/plan/impact |
| Citations | [Author, Year] | Links | Endnotes | Standard |
| Detail level | Full (reproducibility) | Essential only | Selective (for narrative) | Strategic (for persuasion) |
| Hedging | Moderate (standard academic) | Minimal (confident voice) | Minimal (authoritative) | Minimal (assertive) |

## Workflow

1. **Detect source register**: Analyze the input text's person, paragraph length, jargon density, structure, and citation style. Classify it as paper, blog, book, grant, or other. If ambiguous, ask the user.
2. **User specifies target register**: Confirm the desired output register. If not provided, ask.
3. **Analyze source structure**: Identify every transformable element — each paragraph's person, jargon terms, example types, hedges, citation formats, structural markers.
4. **Apply translation rules per dimension**: Systematically transform each dimension from source to target conventions using the reference table above.
5. **Verify technical accuracy**: Ensure every factual claim, number, and result survives the transformation intact. Flag any simplification that loses precision.
6. **Output translated version with annotations**: Show the translated text alongside a change log explaining what changed and why.

## Output Format

```markdown
## Register Translation

**Source**: [Register] → **Target**: [Register]
**Word count**: [Source N] → [Target M]

### Translation Plan

| Dimension | Source | Target | Changes Needed |
|-----------|--------|--------|---------------|
| Person | 3rd passive | 1st active | Rewrite all sentences |
| Jargon | 12 technical terms | 3 max | Define/replace 9 |
| Paragraph length | Avg 200 words | Avg 75 words | Split most paragraphs |
| Examples | 2 mathematical | 2 concrete | Replace with analogies |
| Citations | 8 formal | 8 links | Convert format |
| Hedging | 6 hedges | 1 max | Remove 5 |

### Translated Text

[Full translated version]

### Change Log

- [Line X]: Changed "The model was trained" → "I trained the model" (person shift)
- [Line Y]: Expanded "ELBO" to full explanation (jargon removal)
- [Paragraph Z]: Split into 3 shorter paragraphs (structure shift)
- [Paragraph W]: Replaced equation with analogy (detail level shift)
- [Line V]: Removed "our results suggest that it is possible that" → "this works because" (hedge removal)

### Accuracy Check

- [x] Technical claims preserved
- [x] Numbers/results unchanged
- [x] Method description faithful to original
- [ ] ⚠️ Simplification in para 3 loses nuance about [X] — consider adding footnote
```

## Common Pitfalls

### Losing technical precision during simplification
The biggest risk. "We minimize the KL divergence" contains precise information. "We make the model learn better" does not. Every simplification must preserve the core technical claim, even if the surface form changes. When precision must be sacrificed for accessibility, flag it explicitly in the accuracy check.

### Blog to book: not adding enough connective tissue
The most common failure. Authors paste blog posts into chapters and call it done. A book chapter needs forward and backward references, transitional paragraphs, and awareness of what the reader already knows from prior chapters. If the translated chapter reads like a standalone post, it hasn't been translated — it's been reformatted.

### Paper to blog: keeping academic hedging
Academic papers hedge because reviewers demand it. Blog readers interpret hedging as uncertainty. "Our results suggest that the method may potentially improve performance" reads as "we're not sure this works" to a blog audience. Translate hedges into confident claims (where the evidence supports them) or honest limitations (where it doesn't).

### Over-casualizing
Adding forced humor, strained analogies, or a "fellow kids" voice. Register translation changes structure, not personality. A serious researcher writing a blog post should sound like a serious researcher writing accessibly — not like a comedian doing a science bit.

### Grant to paper or blog
Grant language is persuasion-optimized. Phrases like "transformative potential" and "paradigm shift" that work in grants sound like hype in papers and blogs. Strip funding-speak when translating out of grant register.

## Cross-references

- For **blog to book**: Use `content-archaeologist` first to determine which posts become which chapters, identify themes, and find gaps. Then use this skill to translate individual pieces into chapter register.
- For **audience alignment checking**: Use `audience-checker` after translation to verify the output matches the target audience's expectations.
- For **prose quality**: Use `writing-diagnosis` to check the translated output for structural writing issues (idea soup, buried ledes, etc.) that may have been introduced during translation.

## Constraints

- **Never invent claims.** The translation adds no new technical content. Every claim in the output must trace to a claim in the input.
- **Flag precision loss.** If a simplification loses nuance, say so explicitly. Let the author decide whether the tradeoff is acceptable.
- **Respect register conventions.** Don't produce a "blog post" with 200-word paragraphs and formal citations. If the output doesn't follow target register conventions, it hasn't been translated.
- **One register at a time.** Translate to one target register per invocation. A paper-to-blog translation is different from a paper-to-grant translation; don't blend them.
