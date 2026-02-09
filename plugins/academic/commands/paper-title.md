---
name: paper-title
description: |
  Brainstorm compelling titles for academic papers. Use when asked to
  "brainstorm titles", "suggest paper titles", "title ideas", "name my paper",
  or "help with paper title". Generates diverse options using proven patterns.
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: writing
  verification-level: none
---

# Paper Title Brainstorming

> **LLM-required**: Title generation requires creative brainstorming and understanding of paper contributions. No script alternative.

Generate compelling, memorable titles for ML conference papers (NeurIPS, ICML, ICLR, AAAI).

## Workflow

1. **Understand the contribution**: Read abstract, intro, and method to identify the core idea
2. **Extract key elements**: Method name, problem domain, key property, main result
3. **Identify the hook**: What makes this work surprising, novel, or important?
4. **Generate diverse candidates**: Produce 10-15 titles across different patterns
5. **Evaluate and refine**: Score titles on clarity, memorability, and accuracy
6. **Present top options**: Offer 5-7 best candidates with rationale

## Before Brainstorming

Gather these elements from the paper:
- **Method name** (if coined): e.g., "FlashAttention", "LoRA", "DPO"
- **Core problem**: What task or challenge does this address?
- **Key insight**: What's the main idea or observation?
- **Main result**: What's the strongest empirical or theoretical claim?
- **Domain/application**: Where does this apply?

## Title Patterns

### Pattern 1: Method Name + Descriptive Subtitle
Most common for papers introducing a named method.

```
[Method Name]: [What It Does/Achieves]
```

**Examples:**
- "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness"
- "LoRA: Low-Rank Adaptation of Large Language Models"
- "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding"
- "Adam: A Method for Stochastic Optimization"

**When to use:** You have a catchy acronym or memorable method name.

### Pattern 2: Descriptive Statement
Direct description of what the paper does.

```
[Verb-ing] [Object] [with/via/through] [Approach]
```

**Examples:**
- "Scaling Language Models: Methods, Analysis & Insights from Training Gopher"
- "Training Compute-Optimal Large Language Models"
- "Learning Transferable Visual Models From Natural Language Supervision"
- "Reducing Activation Recomputation in Large Transformer Models"

**When to use:** The contribution is clear and doesn't need a method name.

### Pattern 3: Question Title
Poses a research question the paper answers.

```
[Can/Do/Does/Is] [Subject] [Action/Property]?
```

**Examples:**
- "Do Vision Transformers See Like Convolutional Neural Networks?"
- "Are Emergent Abilities of Large Language Models a Mirage?"
- "Can Large Language Models Reason and Plan?"
- "Is Attention All You Need?"

**When to use:** Paper challenges assumptions or investigates a fundamental question.

### Pattern 4: [X] is All You Need
The iconic Transformer pattern (use sparingly).

```
[Simple Thing] is All You Need
```

**Examples:**
- "Attention Is All You Need"
- "Patches Are All You Need"
- "Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets"

**When to use:** You prove something surprisingly simple works well. Avoid if overused in your subfield.

### Pattern 5: Surprising/Counterintuitive Claim
States a finding that challenges expectations.

```
[Counterintuitive Statement]
```

**Examples:**
- "Scaling Laws for Neural Language Models"
- "Deep Double Descent: Where Bigger Models and More Data Can Hurt"
- "The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks"
- "Why Does Deep and Cheap Learning Work So Well?"

**When to use:** Your main finding is surprising or goes against conventional wisdom.

### Pattern 6: Towards/Beyond/Rethinking
Frames work as progress toward a goal or paradigm shift.

```
[Towards/Beyond/Rethinking] [Goal/Current Practice]
```

**Examples:**
- "Towards Robust and Reproducible Active Learning Using Neural Networks"
- "Beyond Accuracy: Behavioral Testing of NLP Models with CheckList"
- "Rethinking the Inception Architecture for Computer Vision"
- "On the Dangers of Stochastic Parrots"

**When to use:** Paper proposes a new direction or critiques current practices.

### Pattern 7: X meets Y / X for Y
Combines two domains or applies technique to new area.

```
[Technique/Domain A] for [Domain/Task B]
```

**Examples:**
- "Diffusion Models for Video Prediction and Infilling"
- "Transformers for Image Recognition at Scale"
- "Language Models are Few-Shot Learners"
- "Neural Machine Translation by Jointly Learning to Align and Translate"

**When to use:** Applying known technique to new domain or combining approaches.

### Pattern 8: Metaphorical/Creative
Uses analogy or creative framing.

```
[Evocative Metaphor]: [Grounding Description]
```

**Examples:**
- "Distilling the Knowledge in a Neural Network"
- "Playing Atari with Deep Reinforcement Learning"
- "Mastering Chess and Shogi by Self-Play"
- "Constitutional AI: Harmlessness from AI Feedback"

**When to use:** A strong metaphor captures the essence of the work.

## Title Quality Criteria

### Must Have
- **Accurate**: Reflects actual contribution (don't oversell)
- **Specific**: Distinguishes from related work
- **Searchable**: Contains keywords people would search for

### Should Have
- **Memorable**: Easy to recall and cite
- **Pronounceable**: Acronyms should be sayable (avoid XYZQKL)
- **Reasonable length**: 8-15 words typical, avoid very long titles

### Avoid
- **Clickbait**: "You Won't Believe What This Model Can Do"
- **Excessive jargon**: Unless standard in the subfield
- **Generic**: "A Novel Approach to Deep Learning"
- **Overclaiming**: "Solving AGI" when you improved benchmark by 2%

## Acronym Design Tips

Good acronyms are:
- **Pronounceable**: BERT, CLIP, GPT, not BFGSDQ
- **Memorable**: Ideally relate to function (CLIP for images+text)
- **Short**: 3-5 characters ideal
- **Unique**: Google it first to check for conflicts

**Backronym technique**: Start with a good word, then fit the meaning.
- BERT = Bidirectional Encoder Representations from Transformers
- CLIP = Contrastive Language-Image Pre-training
- DALL-E = Combination of WALL-E + Dali

## Output Format

Present titles in ranked order:

```markdown
## Top Title Candidates

### Recommended
1. **[Title]**
   - Pattern: [which pattern]
   - Strengths: [why it works]

2. **[Title]**
   - Pattern: [which pattern]
   - Strengths: [why it works]

### Alternative Options
3. **[Title]** - [brief rationale]
4. **[Title]** - [brief rationale]
5. **[Title]** - [brief rationale]

### If You Want Something Different
6. **[Title]** - [more creative/risky option]
7. **[Title]** - [question format / provocative]
```

## Checklist

Before finalizing:
- [ ] Title accurately represents the paper's contribution
- [ ] Keywords are present for searchability (task, method type, domain)
- [ ] Not too similar to existing famous papers (unless intentional)
- [ ] Acronym (if any) is pronounceable and not taken
- [ ] Length is appropriate (typically under 15 words)
- [ ] Would look good on a CV and in citations
- [ ] Passes the "coffee chat" test: can you say it naturally?

## Examples by Subfield

### Computer Vision
- "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale"
- "Segment Anything"
- "DreamBooth: Fine Tuning Text-to-Image Diffusion Models"

### NLP
- "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"
- "Constitutional AI: Harmlessness from AI Feedback"
- "Direct Preference Optimization: Your Language Model is Secretly a Reward Model"

### Reinforcement Learning
- "Proximal Policy Optimization Algorithms"
- "Decision Transformer: Reinforcement Learning via Sequence Modeling"
- "Offline Reinforcement Learning as One Big Sequence Modeling Problem"

### Theory
- "Understanding Deep Learning Requires Rethinking Generalization"
- "On the Expressive Power of Deep Neural Networks"
- "Neural Tangent Kernel: Convergence and Generalization in Neural Networks"
