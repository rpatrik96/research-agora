---
name: onboard
description: Personalized Research Agora setup via scripts/onboard.py
model: haiku
disable-model-invocation: true
metadata:
  research-domain: general
  task-type: automation
  research-phase: implementation
  verification-level: none
---

Run `python3 scripts/onboard.py --detect --json --dir .` via Bash. Present the JSON results conversationally. If detection is insufficient, ask the user their CLI comfort (a-d), AI usage (a-d), domain, and primary task (a-f) in ONE message, then run `python3 scripts/onboard.py --tier N --domain "X" --task T --json`.
