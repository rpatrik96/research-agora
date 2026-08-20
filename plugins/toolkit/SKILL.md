# Toolkit

The machinery around the paper: LaTeX build/debug/lint, equation-to-code sync, publication figures, rebuttal triage and response, experiment tracking, cluster submission, artifact packaging.

```bash
/plugin install toolkit@research-agora
```

## Checks against ground truth

Runs a tool or script and compares against something outside itself.

| Skill | Description |
|-------|-------------|
| `/code-simplify` | Analyze and refactor Python codebases to remove dead code, eliminate duplication, and simplify complexity |
| `/latex` | Build, debug and lint a LaTeX paper |
| `/latex-sync` | Keep a paper's equations and the code implementing them in agreement, via the latex-code-sync CLI |
| `/rebuttal` | Decode what reviewers actually want, then write the response |

## Checks against a rubric

Applies a stated standard. You are the oracle.

| Skill | Description |
|-------|-------------|
| `/agora-feedback` | Opt-in, review-gated usage feedback for Research Agora skills (RFC-0001) |
| `/artifact-packager` | Use this agent to prepare ML code/data/models for public release with comprehensive checklists. Activates when asked to "package artifacts", "prepare release", "reproducibility checklist", "code release", or "prepare camera ready" |
| `/audit-my-setup` | Health check for the user's Research Agora configuration. Reads CLAUDE.md files, checks installed plugins, MCP servers, hooks, and privacy settings |

## Produces something for you to check

Generates an artifact or a candidate. Verifying it is your job.

| Skill | Description |
|-------|-------------|
| `/experiment-tracker` | Sync ML experiment results to paper drafts |
| `/figures` | Make publication figures for ML papers, in TikZ or matplotlib |
| `/htcondor` | Generate HTCondor submission files and wrapper scripts for ML research jobs |

## License

MIT
