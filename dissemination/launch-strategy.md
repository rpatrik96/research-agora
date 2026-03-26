# Research Agora Launch Strategy

## Timeline Overview

| Week | Phase | Focus |
|------|-------|-------|
| Week -2 | Pre-launch | Profile updates + first content drop |
| Week -1 | Pre-launch | Second content drop + warm outreach |
| Launch day | Launch | Twitter thread + LinkedIn carousel |
| Week +1 | Amplification | Day-two quote-tweet + benchmark follow-up |

---

## Platform Strategy

### Twitter/X — Pre-Launch Checklist

1. - [ ] Rewrite bio: `Building AI research infrastructure · Research Agora: 61 open-source skills for ML research · citation verification · adversarial review · proof auditing · ICLR 2026`
2. - [ ] Change link in bio to `rpatrik96.github.io/research-agora`
3. - [ ] Upload banner image (see `dissemination/assets/twitter-banner.png`) — 1500x500, dark background, "61 AI skills for ML research" + site URL
4. - [ ] Subscribe to X Premium if not already (6x median impression multiplier)
5. - [ ] Pin launch thread (Post 1) immediately after posting
6. - [ ] Move URL out of Post 1 body (keep only in bio + Post 6) to avoid 30-50% reach penalty
7. - [ ] Warm-up engagement 48-72h before launch: reply substantively to 5-8 ML researchers (5k-50k followers) discussing peer review or AI tools
8. - [ ] Verify the "53 papers" NeurIPS claim — cite source or soften to "dozens"

### Twitter/X — Launch Day

- **Post timing**: Tue-Thu, 9-11am ET (ML Twitter peak)
- **Post thread**: see `dissemination/twitter-thread-launch.md`
- Pin Post 1 within 5 minutes of posting
- Do NOT tag people cold in the thread

### Twitter/X — Day Two

- Quote-tweet Post 1 with a specific output example (see `dissemination/social-copy.md` for draft)
- Engage with every reply in the first 24 hours

---

### LinkedIn — Pre-Launch Checklist

1. - [ ] Rewrite headline: `ML Researcher | Building AI tools for research workflows | Research Agora — 61 open-source skills | P-AGI @ ICLR 2026`
2. - [ ] Rewrite About section opening (see `dissemination/social-copy.md` for draft)
3. - [ ] Add Research Agora to Featured section — link card with marketplace screenshot + ICLR paper as second item
4. - [ ] Update experience to reflect tool-builder identity, not just PhD student

### LinkedIn — Pre-Launch Content (2 weeks before)

Three posts, no links in post body (LinkedIn suppresses reach on external links):

1. **Week -2** — Citation hallucination problem post. Describe the failure mode concretely (LLM confidently cites a paper that doesn't exist; reviewer trusts it). End with a question to drive comments. No links.
2. **Week -1** — Evidence hierarchy post. Personal voice: "I spent six months thinking about how to grade AI claims in research. Here's the framework I landed on." Walk through L1-L6 briefly. No links.
3. **3 days before** — Teaser post: "61 skills. 6 plugins. One install command. More soon." Short, no links.

See `dissemination/social-copy.md` for full drafts.

### LinkedIn — Launch Day

- Post the PDF carousel (see `dissemination/assets/linkedin-carousel.pptx`)
- Put GitHub link + quickstart URL in **first comment**, not post body (link suppression)
- Tag 2-3 warm connections in first-comment replies after they engage
- See `dissemination/social-copy.md` for launch post text

### LinkedIn — Post-Launch (Week +1)

- Post benchmark results update: "paper-references skill: 0.89 F1 on CiteBench — here's what it misses and why"
- Reply to every comment personally

---

## Content Assets Checklist

| Asset | Path | Status |
|-------|------|--------|
| Twitter thread | `twitter-thread-launch.md` | Ready |
| Social copy (all drafts) | `social-copy.md` | Needed |
| LinkedIn carousel | `assets/linkedin-carousel.pptx` | Needed |
| Twitter banner | `assets/twitter-banner.png` | Needed |
| Launch strategy (this file) | `launch-strategy.md` | Ready |

---

## Key Metrics to Track

| Platform | Metrics |
|----------|---------|
| Twitter/X | Impressions on Post 1, profile visits, follower growth, bookmark count |
| LinkedIn | Impressions, saves, profile views, Featured section clicks |
| GitHub | Stars, clones, unique visitors in first week |
| Site | Pageviews on `quickstart.html` and `interop.html` |

Baseline: capture all metrics at T=0 (launch day, before posting). Compare at T+7 and T+14.

---

## Differentiation Messaging

**The key claim no competitor can make**: "Every verification skill ships with a benchmark. You can measure whether `/paper-references` catches hallucinations — not just whether it runs."

Other differentiators to deploy in copy:

- **Research-domain specificity**: Not generic coding assistants. Built for the NeurIPS/ICML/ICLR workflow — citation checking, rebuttal drafting, proof auditing, reviewer response.
- **Grounded evidence hierarchy**: L1-L6 claim grading (CODE_VERIFIED → ASSERTION) is formalized in the P-AGI @ ICLR 2026 position paper, not marketing copy.
- **Cross-platform**: Claude Code, Cursor, Gemini CLI, GitHub Copilot. One skill definition, multiple runtimes.
- **Federated contribution model**: Third-party repos can register skills via PR. Marketplace grows without centralized bottleneck.

---

## Outreach Notes

- Target warm connections first: researchers who've discussed peer review, reproducibility, or AI tools publicly in the last 30 days.
- Cold DMs have low ROI. If someone replies to a warm-up tweet, that's the opening.
- For the ICLR P-AGI Workshop: coordinate with workshop organizers on whether they'll retweet from the workshop account on launch day.
- Academic mailing lists (ML-News, etc.): one plain-text announcement 3-5 days post-launch, after social proof is established (star count visible).
