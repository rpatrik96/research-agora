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
