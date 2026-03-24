# Quickstart: First 5 Minutes with Research Agora

Here's how to get this running. It takes 5 minutes.

---

## Choose Your Path

| Path | Setup time | What you get |
|------|-----------|--------------|
| **Browser (Claude.ai)** | 0 min | Chat interface, no file access, no installation |
| **Claude Code (CLI)** | 5–10 min | Full agent: reads/writes files, runs code, executes skills |

If you just want to see citation verification work right now, the browser path gets you there in 3 steps. The CLI path unlocks the full Research Agora skill library and runs against your actual project files.

---

## Browser Path (0 min setup)

You don't need to install anything. Open [Claude.ai](https://claude.ai) in a browser tab.

**Step 1.** Go to [claude.ai](https://claude.ai) and sign in (free tier works).

**Step 2.** Paste this prompt:

```
You are a BibTeX librarian.
Objective: Check each entry in the following BibTeX snippet against Semantic Scholar.
Flag entries where the title, authors, or year don't match any known publication.
Output: Table with columns — cite key, status (verified / unverified / mismatch), details.

[paste 3–5 entries from your .bib file here]
```

**Step 3.** Review the table. Any row marked `mismatch` or `unverified` is a potential hallucination. Fix or remove it before submission.

That's it. The browser path has no file access — you paste content in manually. For automated verification against your full `.bib` file, use the CLI path below.

---

## CLI Path (5–10 min setup)

**Prerequisites:** Node.js installed, a Claude subscription (Pro or API key).

**Install Claude Code:**

```bash
npm install -g @anthropic-ai/claude-code
```

**Navigate to your project:**

```bash
cd /path/to/your/project
```

**Start your first session:**

```bash
claude
```

On first run, Claude Code opens a browser tab to authenticate. Follow the prompts. Once authenticated, you're at the interactive agent prompt.

---

## The 5-Minute Win: Run `/paper-references` on Your .bib File

This is the fastest way to see what Research Agora actually does.

**Step 1.** Install the Research Agora academic plugin:

```bash
claude mcp add research-agora
```

Or manually: follow the [installation instructions in README.md](../README.md).

**Step 2.** Navigate to a project that has a `.bib` file:

```bash
cd /path/to/project-with-references.bib
claude
```

**Step 3.** Run the citation verification skill:

```
/paper-references
```

**Step 4.** Read the output. You'll see something like:

```
Checking 47 entries against Semantic Scholar and CrossRef...

✓ vaswani2017attention       — verified (Vaswani et al., 2017, NeurIPS)
✓ lecun1989backprop          — verified (LeCun et al., 1989, Neural Computation)
⚠ smith2023efficiency        — MISMATCH: title found but year differs (paper is 2022, not 2023)
✗ johnson2024emergent        — NOT FOUND: no matching publication on any indexed source
✓ goodfellow2016deep         — verified (Goodfellow et al., 2016, MIT Press)
...

Summary: 44 verified, 2 mismatches, 1 not found
```

That task cost approximately **$0.10–0.30** in API tokens depending on bibliography size.

**Fallback — no .bib file?** Paste this sample into a file called `demo.bib` in your current directory:

```bibtex
@inproceedings{vaswani2017attention,
  title={Attention is all you need},
  author={Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and others},
  booktitle={NeurIPS},
  year={2017}
}

@article{invented2024hallucination,
  title={Emergent reasoning through chain-of-thought distillation at scale},
  author={Chen, Wei and Park, Soo-Jin and Mueller, Hans},
  journal={ICML},
  year={2024}
}
```

The second entry is fabricated. Watch the agent catch it.

**Fallback — no CLI yet?** Run the browser-path version above. You paste your BibTeX manually; it checks the same way, just one entry at a time.

---

## What Just Happened

The agent read your `.bib` file, extracted each citation's title, authors, and year, then queried Semantic Scholar and CrossRef to find matching records. For each entry it compared the metadata against what's actually indexed. Entries that don't resolve to a real publication — hallucinated references, typos, or year errors — are flagged. This is the same check a careful human reviewer would do manually, run programmatically against scholarly databases in under a minute. The agent didn't guess: it verified against ground truth.

---

## Setup Time Reference

| Component | First-time setup | Ongoing overhead |
|-----------|-----------------|------------------|
| Claude Code installation | 5–10 min (one command + login) | Auto-updates |
| CLAUDE.md for a project | 20–45 min (or 5 min via `/init`) | 5–10 min every few weeks |
| MCP server (e.g., GitHub) | 5–15 min per server | None once configured |
| Custom skill | 10–30 min for a first skill | Minutes to update |
| Per-session startup | Automatic (~10 sec) | Context management via `/clear`, `/compact` |

**Total initial investment:** 1–2 hours for a full setup (Claude Code + CLAUDE.md + 2–3 MCP servers + a first skill). After that, per-session overhead is under 5 minutes.

---

## What's Next

- **[concepts.md](concepts.md)** — How AI agents actually work: the five-level ladder from Chat to Skills, what to delegate vs. protect, where Research Agora fits.
- **[verification.md](verification.md)** — The full verification hierarchy: formal checks, automated heuristics, manual review. When to use each and why ideation gets verified 7× less than code.
- **`/onboard`** — Run this skill in your project directory. It reads your codebase and drafts a `CLAUDE.md` tailored to your project in under 2 minutes.

For a CLAUDE.md template you can copy and customize, see [templates/CLAUDE.md.researcher](../templates/CLAUDE.md.researcher).
