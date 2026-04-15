# Recent Retro Lessons

## Current Focus

- This slice followed the per-file coverage floor work by lifting `sync_support.py` off the exact `80.0%` threshold.

## Repeat Traps

- Some remaining weak lines are trace-shape artifacts around imports and function signatures rather than user-visible behavior. The useful fix was not to chase those directly, but to remove wrapper repetition and cover missing behavioral branches.

## Next-Time Checklist

- workflow: when a file sits exactly on a floor, inspect whether uncovered lines are real behavior before adding tests.
- capability: the next cleanup target should be `install_tools.py`, now the weakest tracked file at `81.5%`.
- memory: shared lifecycle wrapper helpers now live in `scripts/control_plane_lifecycle_lib.py`.

## Sources

- `charness-artifacts/retro/2026-04-15-sync-support-floor-cleanup.md`
