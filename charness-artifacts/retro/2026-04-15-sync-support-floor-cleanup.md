# Session Retro: Sync Support Floor Cleanup

## Mode

session

## Context

This slice followed the per-file coverage floor work by lifting `sync_support.py`
off the exact `80.0%` threshold. The change reduced repeated lifecycle wrapper
code by moving `tool_id` selection and status printing into
`control_plane_lifecycle_lib.py`, then exercised the real skip and human-output
branches.

## Evidence Summary

- `check-coverage` reports `sync_support.py` at `86.5%`, up from `80.0%`.
- `./scripts/run-quality.sh --review` passed with `36 passed, 0 failed`.
- `python3 scripts/run_slice_closeout.py --repo-root .` passed all planned sync
  and verify commands.

## Waste

- Some remaining weak lines are trace-shape artifacts around imports and
  function signatures rather than user-visible behavior. The useful fix was not
  to chase those directly, but to remove wrapper repetition and cover missing
  behavioral branches.

## Critical Decisions

- Keep `sync_support.py` as a thin CLI wrapper rather than moving all behavior
  out of it.
- Share selection and status output across install/update/sync wrappers so the
  next lifecycle CLI does not repeat the same boilerplate.

## Expert Counterfactuals

- John Ousterhout lens: keep the abstraction tiny and mechanical; broad helper
  frameworks would add more surface than the three repeated lines justify.
- Kent Beck lens: cover the concrete skipped-support and human-output branches
  after the refactor, because those are the behavior users can observe.

## Next Improvements

- workflow: when a file sits exactly on a floor, inspect whether uncovered lines
  are real behavior before adding tests.
- capability: the next cleanup target should be `install_tools.py`, now the
  weakest tracked file at `81.5%`.
- memory: shared lifecycle wrapper helpers now live in
  `scripts/control_plane_lifecycle_lib.py`.

## Persisted

yes `charness-artifacts/retro/2026-04-15-sync-support-floor-cleanup.md`
