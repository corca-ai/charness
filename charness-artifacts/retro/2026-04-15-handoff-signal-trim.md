# Session Retro: Handoff Signal Trim

## Mode

session

## Context

The user pointed out that `docs/handoff.md` was preserving too much process
history. The handoff skill says to pass the next pickup path, not a diary, so
this was a real workflow miss.

## Evidence Summary

- `docs/handoff.md` had grown to 94 lines and carried time-ordered quality
  deltas, runtime details, and debug history.
- After review, it was rewritten to 58 lines focused on current invariants,
  next actions, open decisions, and references.

## Waste

The handoff repeated details already owned by `quality/latest.md`, debug
artifacts, and retro records. That forced future readers to distinguish live
instructions from completed history.

## Critical Decisions

- Kept gate facts and the next cleanup target in handoff.
- Moved historical deltas and runtime detail back to quality/retro/debug
  references.
- Recorded that the handoff skill should push harder toward signal-only baton
  passes, because the current size gate is too permissive.

## Expert Counterfactuals

- Christopher Alexander's sequence lens would ask what the next operator must
  do first, then keep only facts that shape that sequence.
- Gary Klein's premortem lens would flag the likely failure: a future agent
  overreads old deltas as current priorities and starts the wrong cleanup.

## Next Improvements

- workflow: before updating handoff, delete any completed history that does not
  change the next action.
- capability: tighten the handoff skill or its references to prefer a smaller
  practical target than the current broad 200-line size gate.
- memory: keep `install_tools.py` and `support_sync_lib.py` as the next cleanup
  targets while avoiding detailed process replay in handoff.

## Persisted

yes: `charness-artifacts/retro/2026-04-15-handoff-signal-trim.md`
