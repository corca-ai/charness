# Session Retro
Date: 2026-04-20

## Context

The process-boundary hardening slice landed, but I still let pre-push discover
that the new debug artifact heading and section order were invalid. The user
correctly pointed out that `debug` should have helped earlier.

## Evidence Summary

- user correction in the current thread
- `scripts/validate-debug-artifact.py`
- `skills/public/debug/SKILL.md`

## Waste

- I used the `debug` skill without consulting its validator-backed artifact
  contract early enough.
- The current skill text named the sections, but it did not give a direct
  scaffold/validator path in bootstrap, so a plausible-but-wrong draft slipped
  through until pre-push.

## Critical Decisions

- treat this as a `debug` skill ergonomics gap, not just a one-off authoring miss
- add a repo-owned scaffold helper instead of relying on prose memory

## Expert Counterfactuals

- Gary Klein: ask "what would fail at closeout?" before drafting the artifact.
  Here the likely answer was the debug validator, so the validator contract
  should have been checked first.
- Atul Gawande-style checklist lens: if a repo ships a standing artifact
  validator, bootstrap should point to it explicitly rather than assuming the
  author will remember the exact shape.

## Next Improvements

- workflow: when a skill has a standing artifact validator, consult it or its
  scaffold helper before drafting a new durable artifact
- capability: `debug` now ships `scaffold_debug_artifact.py` and names the
  validator command in bootstrap
- memory: keep this lesson durable so future sessions treat validator-backed
  artifact shape as an up-front contract, not a late gate

## Persisted

- yes: `charness-artifacts/retro/2026-04-20-debug-artifact-contract-late-discovery.md`
