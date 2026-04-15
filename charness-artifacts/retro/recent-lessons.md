# Recent Retro Lessons

## Current Focus

- This slice followed the handoff cleanup by simplifying exported control-plane code enough to raise the enforced per-file coverage floor from 80% to 85%.

## Repeat Traps

- No repeat traps extracted from source retro.

## Next-Time Checklist

- workflow: do not run plugin-export sync/closeout concurrently with full quality review; serialize those gates when the plugin tree is in scope.
- capability: if runtime budgets keep needing manual interpretation, replace latest-sample-only enforcement with a small report over recent samples.
- memory: next coverage cleanup targets are `support_sync_lib.py`, `upstream_release_lib.py`, and `control_plane_lib.py` near the 85% floor.

## Sources

- `charness-artifacts/retro/2026-04-15-coverage-floor-runtime-budget.md`
