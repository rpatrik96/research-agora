---
name: writing-diagnosis
description: Diagnose root causes of bad writing at the paragraph level. Use when asked to "diagnose this paragraph", "why does this suck", "what's wrong with this", "writing diagnosis", or "debug my writing". Identifies patterns like cognitive overload, buried ledes, idea soup, and monotonous rhythm — then teaches the fix.
model: opus
metadata:
  research-domain: general
  research-phase: paper-writing
  task-type: diagnosis
  verification-level: heuristic
---

# Writing Diagnosis

Identify the root cause of why a passage fails, name the pattern, and teach the author to recognize it in future writing.

> **LLM-required**: Diagnosing writing requires nuanced judgment about reader cognition, rhetorical intent, and prose rhythm. No script alternative.

## Core Philosophy

Fixes alone don't improve writers. Diagnosis teaches pattern recognition. When you name a failure mode ("this is Idea Soup"), the author gains a mental label they can apply to their own drafts. The educational output matters more than the rewrite.

Every diagnosis should answer three questions:
1. What pattern is causing the failure?
2. Why does this pattern fail (cognitively)?
3. How do I spot it myself next time?

## Workflow

1. **Identify format context**: Is this from a paper, blog post, book chapter, or grant proposal? Each has different norms.
2. **Read the passage**: Read the full passage without judgment first. Understand what the author is trying to say.
3. **Identify the root cause**: Symptoms are surface-level ("this sentence is long"). Root causes are structural ("you packed three claims into one sentence because you haven't decided which claim this paragraph is about").
4. **Name the pattern**: Use the pattern library below. Named patterns stick in memory.
5. **Explain why it fails**: Connect to reader cognition. "The reader holds your first sentence as the topic frame. When sentence 3 contradicts that frame, they re-read from the top."
6. **Show the fix**: Before/after with minimal changes. Don't rewrite from scratch — show what moves.
7. **Teach the transferable lesson**: One sentence the author can carry to their next paragraph.

## Pattern Library

### 1. Idea Soup

**Definition**: Multiple unrelated points crammed into one paragraph. The reader cannot summarize it in five words.

**How to spot it**: Try to write a topic sentence for the paragraph. If you can't, it's Idea Soup.

**Cognitive failure**: Working memory holds one paragraph-level idea. Two ideas in one paragraph means one gets dropped.

**Fix**: Split into separate paragraphs, each with a single controlling idea.

### 2. Buried Lede

**Definition**: The main point appears in sentence 3 or 4 instead of sentence 1. The paragraph "warms up" before saying the thing.

**How to spot it**: Cover sentences 1-2. Does the paragraph still make sense? If yes, sentences 1-2 are throat-clearing.

**Cognitive failure**: Readers use sentence 1 as a frame for interpreting everything that follows. Wrong frame = misinterpretation or re-reading.

**Fix**: Move the key claim to sentence 1. Use the former opening as support or cut it.

### 3. Cognitive Overload

**Definition**: A sentence exceeds ~40 words with nested subordinate clauses. The reader loses the grammatical thread before reaching the verb.

**How to spot it**: Count words. If you can't parse the sentence structure on first read, neither can the reader.

**Cognitive failure**: Working memory for syntactic structure is limited. Nested clauses force the reader to maintain a stack of incomplete structures.

**Fix**: Break at natural clause boundaries. One clause per sentence. If a sentence needs a semicolon and two commas, it's probably two sentences.

### 4. Monotonous Rhythm

**Definition**: Every sentence has the same length and structure ("Subject verb object. Subject verb object. Subject verb object."). Creates a droning effect.

**How to spot it**: Read aloud. If it sounds like a metronome, the rhythm is flat.

**Cognitive failure**: Rhythm variation signals emphasis. Flat rhythm means nothing stands out, so nothing gets remembered.

**Fix**: Vary sentence length deliberately. Follow a long sentence with a short one. Use fragments for emphasis. Break the pattern.

### 5. Hedge Stacking

**Definition**: Multiple hedges piled onto one claim: "might possibly suggest that it could potentially indicate..."

**How to spot it**: Count qualifiers per sentence. More than one hedge per claim signals the problem.

**Cognitive failure**: Each hedge dilutes confidence. Three hedges on one claim tells the reader "I don't believe this either."

**Fix**: One hedge per claim, maximum. Choose the most accurate qualifier and commit to it. "Our results suggest X" is fine. "Our results might possibly suggest X could potentially be true" is not.

### 6. Orphan Transition

**Definition**: A new paragraph begins with no connection to the previous one. The reader experiences topic whiplash.

**How to spot it**: Read the last sentence of paragraph N and the first sentence of paragraph N+1 back-to-back. If they feel like they're from different documents, that's an orphan transition.

**Cognitive failure**: Readers build a narrative thread across paragraphs. Breaking it forces them to reset context, which costs comprehension.

**Fix**: Add a bridging phrase or restructure so the new paragraph follows logically. The bridge can be as simple as "Beyond accuracy, we also consider efficiency" before switching topics.

### 7. Abstraction Fog

**Definition**: Abstract nouns doing the work of concrete verbs. "The optimization of the parameters" instead of "We optimize the parameters." "The utilization of the framework" instead of "We use the framework."

**How to spot it**: Look for "-tion" and "-ment" nouns that could be verbs. Count prepositional phrases ("of the", "for the", "in the").

**Cognitive failure**: Abstract nouns hide the actor and the action. The reader must mentally reconstruct who did what.

**Fix**: Find the hidden verb and the hidden actor. Make the actor the subject and the verb the predicate.

### 8. Zombie Sentence

**Definition**: Passive voice hiding the actor when the actor matters. "It was found that..." "The model was trained..." "Experiments were conducted..."

**How to spot it**: Ask "by whom?" If the answer matters and is missing, it's a zombie sentence.

**Cognitive failure**: Readers need agents to build a mental model of what happened. Agentless sentences float without anchoring.

**Fix**: Name the actor. "We found..." "We train the model..." Note: passive voice is fine when the actor genuinely doesn't matter ("The dataset was collected in 2019").

### 9. Echo Chamber

**Definition**: The same word or phrase repeated 3+ times in close proximity. "The model uses the model architecture to model the distribution."

**How to spot it**: Read aloud. Repeated words create an audible stutter.

**Cognitive failure**: Repetition signals emphasis. Unintentional repetition creates false emphasis and makes prose feel unpolished.

**Fix**: Use pronouns, synonyms, or restructure to avoid repetition. But don't swap in obscure synonyms — clarity beats variety.

### 10. Throat Clearing

**Definition**: Opening with filler before saying the actual thing. "It is important to note that..." "It should be mentioned that..." "As we all know..."

**How to spot it**: Delete the opening phrase. If the sentence still works, it was throat clearing.

**Cognitive failure**: The reader allocates attention to the opening. Wasting it on filler means less attention for the actual content.

**Fix**: Delete the throat-clearing phrase. Start with the content.

### 11. Scale Mismatch

**Definition**: A paragraph-level claim supported by sentence-level evidence, or vice versa. "Deep learning has transformed computer vision" supported by "our model gets 92% on CIFAR-10."

**How to spot it**: Check if the scope of the claim matches the scope of the evidence. Grand claims need broad evidence. Narrow evidence supports narrow claims.

**Cognitive failure**: The reader notices the gap between claim and evidence, even subconsciously. It erodes trust.

**Fix**: Either narrow the claim to match the evidence, or provide evidence at the appropriate scale.

### 12. Jargon Cliff

**Definition**: Technical density spikes without warning. The reader falls off a comprehension cliff because three undefined terms appeared in one sentence.

**How to spot it**: Read as someone one expertise level below the target audience. If a sentence requires three mental lookups, it's a jargon cliff.

**Cognitive failure**: Each unknown term consumes working memory. Three at once exhausts it.

**Fix**: Introduce technical terms one at a time. Define or gloss terms on first use. Build up to dense passages.

## Pattern Interactions

Patterns rarely appear in isolation. Common combinations and their compounding effects:

- **Idea Soup + Buried Lede**: The paragraph has multiple ideas AND none of them appear first. Reader abandonment is almost guaranteed.
- **Cognitive Overload + Jargon Cliff**: A 50-word sentence full of undefined terms. The reader must parse complex syntax and decode unfamiliar vocabulary simultaneously.
- **Hedge Stacking + Zombie Sentence**: "It was found that results might possibly suggest..." The combination of hidden actor and stacked hedges makes the claim feel both unauthored and unbelieved.
- **Monotonous Rhythm + Throat Clearing**: Every sentence starts with the same filler structure. Amplifies the droning effect.
- **Abstraction Fog + Echo Chamber**: "The utilization of the optimization for the optimization of the utilization..." Abstract nouns multiplied by repetition creates impenetrable prose.

When patterns compound, diagnose the root cause first. Fixing Idea Soup often resolves the co-occurring Buried Lede, because once the paragraph has one idea, its placement becomes obvious.

## Output Format

```markdown
## Writing Diagnosis

**Text**: [First 50 characters of the passage...]
**Format detected**: [paper / blog / book / grant]
**Word count**: [N]

### Root Cause
**Pattern**: [Named pattern from library]
**Severity**: [Blocks comprehension / Hurts flow / Style issue]

### Evidence
- [Specific sentence or phrase with explanation of why it fails]
- [Second instance if multiple symptoms of same root cause]

### Why This Fails
[1-2 sentences explaining the cognitive/reader experience. Connect to how real readers process text.]

### Fix
**Before**: [Original passage or sentence]
**After**: [Rewritten version with minimal changes]
**What changed**: [Brief explanation of the specific moves made]

### Pattern to Learn
[One transferable sentence the author can carry to future writing. Frame as a rule of thumb.]
```

### When Multiple Patterns Are Present

If the passage has more than one pattern, diagnose all of them but prioritize:

1. **Comprehension blockers first** (Idea Soup, Cognitive Overload, Jargon Cliff)
2. **Flow issues second** (Buried Lede, Orphan Transition, Scale Mismatch)
3. **Style issues last** (Monotonous Rhythm, Echo Chamber, Throat Clearing)

Label each pattern separately with its own evidence, explanation, and fix.

## Quick Mode

For rapid iteration (when the author is revising and wants fast feedback), use the compressed format:

```markdown
**Pattern**: [Name] | **Severity**: [Level]
**Where**: [Sentence or phrase]
**Fix**: [One-line suggestion]
```

Activate quick mode when the author says "quick diagnosis", "just the pattern", or is clearly iterating on multiple paragraphs in sequence.

## Constraints

- **Never sacrifice technical accuracy for readability.** If a precise term is needed, keep it. Flag it if undefined, but don't replace "stochastic gradient descent" with "training step" for the sake of simplicity.
- **Diagnose, don't rewrite.** The rewrite in the Fix section is a demonstration, not a deliverable. The author should apply the lesson themselves.
- **Respect the author's voice.** The goal is to fix structural failures, not impose a single prose style. An author who writes in long, flowing sentences is not wrong — unless those sentences exceed comprehension limits.
- **Name the pattern.** The educational value comes from the label. An unnamed fix is forgotten by next week. A named pattern ("oh, this is Idea Soup again") is remembered for years.
