---
name: onboard
description: |
  Personalized onboarding for the Research Agora. Use when asked to "get started",
  "onboard me", "set up my project", "what should I use", "how do I start",
  "configure my workflow", "help me get set up", or "I'm new here".
  Interviews the user, determines their tier, generates a personalized CLAUDE.md,
  and recommends a 5-minute first win.
model: sonnet
disable-model-invocation: true
metadata:
  research-domain: general
  task-type: automation
  research-phase: implementation
  verification-level: none
---

# Research Agora Onboarding

> **Script-first**: Core onboarding logic lives in `scripts/onboard.py` (stdlib Python, no dependencies). This skill runs the script and optionally personalizes the output.

## Workflow

1. Run `scripts/onboard.py --detect --json` to auto-detect project and generate structured output
2. If detection is insufficient, run `scripts/onboard.py --json` for interactive interview
3. Present the script's output to the user with light LLM personalization

## Step 1: Run the Script

Use the Bash tool to run the onboarding script from the Research Agora repo root:

```bash
# Try auto-detect first (no user input needed)
python3 scripts/onboard.py --detect --json --dir .
```

If the JSON output has insufficient information (empty domain, no languages detected), fall back to asking the user directly — but keep it to ONE message with all questions, then run the script with explicit flags:

```bash
python3 scripts/onboard.py --tier <N> --domain "<domain>" --task <letter> --json
```

## Step 2: Present Results

Parse the JSON output and present it conversationally:

1. **Profile summary**: One line confirming what was detected/classified
2. **CLAUDE.md**: Show the generated content in a code block, offer to save it
3. **5-minute win**: Present the tier-appropriate first task
4. **Skill recommendations**: Show the recommended skills table
5. **What's next**: List the next steps

## Step 3: Personalize (Optional)

If context allows, enhance the script output:

- Add domain-specific notes (e.g., "Since you use Zotero, the Zotero MCP can connect Claude Code directly to your library")
- Adjust tone based on the user's communication style
- Suggest skills not in the script's lookup table if they match the user's stated needs

## Tone Guide

- **Warm but not saccharine.** "Let me help you get set up" not "We're SO EXCITED to have you!!!"
- **Direct but not curt.** Explain the why, skip the filler.
- **Practitioner voice.** You've used these tools. Share what works honestly.
- **Respect expertise.** A biologist who doesn't use the CLI is an expert in their domain.

## Standalone Usage

Users can also run the script directly without Claude Code:

```bash
python3 scripts/onboard.py                # interactive interview
python3 scripts/onboard.py --detect       # auto-detect from project files
python3 scripts/onboard.py --tier 2       # skip interview, specify tier
python3 scripts/onboard.py --json         # structured output for automation
```
