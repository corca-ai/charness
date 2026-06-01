# Session Retro: #273 + #261 Mutation Gate Recovery

## Context

This work bundled the live #273 mutation regression with the #261 survivor
policy boundary. It fixed the live changed-line/survivor surfaces and left #261
open intentionally.

## Evidence Summary

- Goal: `charness-artifacts/goals/2026-06-01-273-261-mutation-regression-and-survivors.md`
- Debug: `charness-artifacts/debug/2026-06-01-273-mutation-gate-helper-coverage.md`
- Critique: `charness-artifacts/critique/2026-06-01-273-261-mutation-gate-recovery-resolution.md`
- Final local quality: `./scripts/run-quality.sh --read-only` passed 69/69.

## Waste

The main waste was closeout-shape iteration: the carrier initially missed the
exact `Critique:` line and the debug artifact initially missed the validator's
required shape. The validators caught this before publication.

## Critical Decisions

- Fix #273 with focused helper tests and branch simplification rather than
  chasing older sampled files.
- Leave #261 open because its remaining work is equivalent/low-value survivor
  policy, not a missing #273 coverage fix.
- Use the gate-owned changed-line classifier for proof instead of a plain pytest
  shortcut.

## Expert Counterfactuals

Gary Klein would have asked for the carrier validation checklist before writing
the final issue artifact, reducing the closeout-shape iteration. A skeptical
release engineer would have kept remote CI as an explicit non-claim until after
push.

## Next Improvements

- workflow: validate the issue carrier immediately after adding required fields,
  before expanding final artifact prose.
- memory: keep the debug-artifact section contract visible when a debug file is
  used as issue closeout evidence.

## Sibling Search

The transferable pattern is closeout evidence shape drift, not a new code
sibling. Existing validators cover debug artifacts, critique artifacts, and
issue closeout ledgers; no new sibling change is needed.

## Persisted

Persisted by `persist_retro_artifact.py`.
