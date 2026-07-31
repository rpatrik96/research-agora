# Research Agora RFCs

Design documents for significant changes to the Agora platform. PLATFORM.md
describes the *accepted* design; RFCs are where changes to it get proposed,
discussed, and decided. The governance model (PLATFORM.md, Phase 3) anticipates
an RFC process — this directory bootstraps it.

## Process

1. Copy the structure of an existing RFC into `NNNN-kebab-title.md` (next free
   number) with `Status: Draft`.
2. Open a PR. Discussion happens on the PR thread.
3. The maintainer (BDFL phase) or the governance council (Phase 3) accepts,
   requests changes, or declines. Acceptance = PR merge with `Status: Accepted`.
4. When the described work ships, update the status to `Implemented`.

## Statuses

| Status | Meaning |
|--------|---------|
| Draft | Under discussion; nothing in it is binding |
| Accepted | Design agreed; implementation may proceed |
| Implemented | Shipped; the RFC is the design record |
| Withdrawn | Abandoned; kept for the record |

## Index

| RFC | Title | Status |
|-----|-------|--------|
| [0001](0001-agora-feedback-loop.md) | Agora Self-Improvement Feedback Loop | Draft (MVP implemented) |
