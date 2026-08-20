# Write

Produce and diagnose the draft. These read what you wrote and tell you where it breaks — against venue limits, against your own results, against what a skeptical reviewer will say. They do not write your claims for you: no oracle exists for novelty or framing, so that judgment stays with the author.

```bash
/plugin install write@research-agora
```

## Checks against ground truth

Runs a tool or script and compares against something outside itself.

| Skill | Description |
|-------|-------------|
| `/argument-autopsy` | Visualize the logical skeleton of a paper's argument as a claim-evidence DAG |
| `/paper-review` | Generate critical reviews of ML paper drafts simulating a skeptical reviewer |
| `/writing-verify` | Quantitative writing quality verification for scientific papers |

## Checks against a rubric

Applies a stated standard. You are the oracle.

| Skill | Description |
|-------|-------------|
| `/audience-checker` | Use this agent to evaluate papers, presentations, posters, or communications for target audience alignment. Impersonates different reader personas (reviewers, industry engineers, students, experts) to identify jargon, unclear explanations, and narrative gaps |
| `/paper-abstract` | Diagnose abstracts for ML conference papers against structure, venue word limits, specificity, and claim support |
| `/paper-experiments` | Write experimental details sections for ML papers with GitHub repository integration |
| `/voice-drift-detector` | Use this agent to detect voice inconsistency across chapters, blog posts, or documents. Activates when asked to "check voice consistency", "tone drift", "does this sound like me", "voice fingerprint", or "style consistency check". Quantifies rhythm, formality, person, and metaphor density to flag unintentional drift |
| `/writing-diagnosis` | Diagnose root causes of bad writing at the paragraph level |

## License

MIT
