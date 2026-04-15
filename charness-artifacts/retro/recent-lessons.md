# Recent Retro Lessons

## Current Focus

- This slice accepted the user's request to do the three remaining candidates: make runtime budgets robust to runner variance, continue near-floor production cleanup, and exercise the release/update path.

## Repeat Traps

- No repeat traps extracted from source retro.

## Next-Time Checklist

- workflow: when a gate is flaky, first inspect whether the measurement rule is wrong before loosening the number.
- capability: runtime budget output now has enough fields to build a future ratchet report without rereading raw JSON.
- memory: next cleanup targets are `upstream_release_lib.py`, `control_plane_lib.py`, and `install_tools.py` near the 85% floor.

## Sources

- `charness-artifacts/retro/2026-04-15-runtime-budget-update-proof.md`
