# Pending workflows

Workflow files staged here because the authoring session's GitHub token
lacked the `workflow` scope required to write to `.github/workflows/`.

To install (one move + commit, done by a human with normal push rights):

```bash
git mv .github/workflows-pending/aggregate-feedback.yml .github/workflows/
git commit -m "chore(feedback): install weekly aggregation workflow"
```

| File | Purpose |
|------|---------|
| `aggregate-feedback.yml` | RFC-0001 M2: weekly roll-up of `skill-feedback` issues into `registry/feedback.json` via a bot PR |

## Required repo setup (one-time, maintainer)

1. **Branch protection on `main`** (Settings → Branches): require a pull
   request before merging and require status checks. The workflow never
   pushes to `main` by construction, but branch protection is the hard
   enforcement that *nothing* can — including a compromised token or a
   future workflow bug.
2. **`skill-feedback` label**: the workflow bootstraps it on first run
   (`gh label create ... || true`); creating it manually earlier means
   issue-form submissions get labeled from day one (GitHub silently drops
   labels that don't exist yet).

## Operational notes

- **Bot PRs do not trigger CI.** PRs opened with the default `GITHUB_TOKEN`
  never start other workflows (GitHub's anti-recursion rule), so `ci.yml`
  stays silent on aggregation PRs. Compensation: the workflow runs
  `tests/test_feedback.py` itself before opening the PR. If you want full CI
  on these PRs, close and reopen them, or switch the workflow to a PAT.
- **Scheduled workflows auto-disable after ~60 days without repo activity**
  (public repos). Nothing is lost — reports queue as open issues and the
  aggregator is idempotent — but re-enable the workflow under the Actions
  tab after a quiet period.
