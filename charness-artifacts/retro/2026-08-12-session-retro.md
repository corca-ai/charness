# Session Retro
Date: 2026-08-12

## Context

This retrospective reviews the completed handoff/ownership-gate work that led to
the current ledger-and-graduation contract, before implementing its first slice.
The durable contract is the strongest source for the next move; commit history,
the handoff, the recent-lesson digest, and the prepared packet bound the review.

## Window

The reviewed work spans the 2026-08-11 six-rulings and ownership-gate repairs
through HEAD (`58e48ea5`); the working tree was clean when the retro packet was
prepared.

## Evidence Summary

- `docs/handoff.md` identifies the ledger/register contract as the first next-session item.
- `charness-artifacts/spec/2026-08-12-lesson-ledger-and-contract-register.md` fixes the
  ledger state, append-only transition, and graduation constraints for the first slice.
- `charness-artifacts/retro/recent-lessons.md` records repeated baseline-edit and
  terminal-green trust traps.
- `skills/public/retro/scripts/mine_closeout_telemetry.py --repo-root . --detail` read
  1,643 local records and found four recurring costs; this is local-stream evidence only.
- Packet Consumed: `charness-artifacts/retro/2026-08-12-001027-packet.md`.

## Waste

- **strong**: Hand-editing a generated ratchet baseline created three repair cycles; the
  existing rebuild path was the missing first move, not a missing rule.
- **strong**: The telemetry stream reports 16 over-budget full-pytest observations
  (mean 391.07s against 120s) and 64 recurring over-slice runs. These are recurring
  cost signals, not permission to weaken proof. The runtime work already has a
  durable owner in closed issue #505 / D51; the over-slice signal needs a later,
  separately scoped owner rather than being added to this implementation slice.

## Critical Decisions

- Build durable ledger state and its append-only transition gate before ranking,
  scoring, or presentation. That preserves a testable state boundary and avoids
  inventing a ranking over ephemeral data.
- Treat graduation as a review-bound proposal, not an automated contract edit.
  The contract's budget/displacement rule remains an acceptance boundary for the
  later seam, not a license to change `AGENTS.md` in this slice.

## Trends vs Last Retro

The current digest repeats the same two operational risks: hand-edited derived
state and terminal trust in a single green signal. The ledger design responds by
making state transitions cited and append-only; it does not claim that the new
mechanism has changed agent behaviour yet.

## North Star Alignment

P1 holds: the first slice keeps normal ledger work reversible and uses judgment
for wording rather than adding a content classifier. P4/P5 hold at the
graduation boundary: a script may compute candidates, but moving a rule into a
standing contract remains a proposal behind distinct review. The failure
signature to avoid is treating a passing ledger gate or a proposed graduation as
terminal completion; neither establishes that the contract change was warranted.

## Expert Counterfactuals

- Engelbart's system-improving-itself lens would require the tool (ledger), the
  working method (retro scoring/citation), and the language (contract units) to
  evolve together. Therefore this slice writes only the state seam and keeps the
  uncertain register counter as an explicit probe.
- A decision-quality counterfactual would demand a concrete displacement before
  any graduation, rather than rewarding a plausible new rule merely because it
  sounds useful.

## Sibling Search

- same layer: `scripts/recent_lessons_lib.py` rebuild gate | decision: same waste, fix now | proof: first-slice contract requires derived candidate extraction to remain rebuild-checked.
- abstraction up: `docs/conventions/implementation-discipline.md` | decision: intentional boundary | proof: contract changes stay review-bound; no contract text is edited in this slice.
- specialization down: `charness-artifacts/retro/recent-lessons.md` | decision: diagnostic-only | proof: it remains a generated digest until ledger selection replaces it in a later slice.
- mental-model siblings: closeout telemetry over-slice advisory | decision: valid follow-up outside the slice | proof: 64 recurring occurrences from the local stream | follow-up: deferred docs/handoff.md#next-session.

## Portable Candidate

Not portable — the ledger key is this repository's author-declared
`recurrence-class` marker and its consumer surfaces are charness-local.

## Next Improvements

- workflow: establish the graduation proposal's evidence and displacement before any contract-surface mutation (recurrence-class: graduation-is-proposal).
- capability: implement the ledger state file, append-only cited transitions, seed migration, and focused gate before selection or scoring reads it (recurrence-class: durable-lesson-ledger-first).
- memory: keep the current slice and register probes in the canonical ledger/register spec; do not promote this retro's conclusions into a standing rule.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-12-session-retro.md
