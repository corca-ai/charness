# Session Retro: Runtime Budget and Update Proof

## Mode

session

## Context

This slice accepted the user's request to do the three remaining candidates:
make runtime budgets robust to runner variance, continue near-floor production
cleanup, and exercise the release/update path.

## Evidence Summary

- Changed files hit `checked-in-plugin-export` and
  `integrations-and-control-plane`, which triggered auto-retro.
- `./scripts/run-quality.sh --review` passed with `36 passed, 0 failed`, total
  `43.6s`.
- Clean temp-home `charness update` propagation and Cautilus support-sync proofs
  passed.

## Waste

The previous runtime-budget fix widened budgets before changing the decision
rule. That made the gate quieter, but less precise than necessary. The better
sequence was to change the statistic first, then restore tighter budgets.

## Critical Decisions

- Changed runtime budget enforcement from latest-sample failure to
  recent-median failure with latest spikes reported separately.
- Centralized the upstream support skill-root invariant in
  `_resolve_upstream_source_path`, deleting a later duplicate file-check branch.
- Recorded release/update proof in `charness-artifacts/release/latest.md`
  without claiming the remaining real-host Cautilus binary install was done.

## Expert Counterfactuals

- W. Edwards Deming's variation lens would start from the process statistic:
  distinguish common-cause runtime variation from special-cause regression
  before changing thresholds.
- John Ousterhout's complexity lens favors moving the skill-root invariant to
  the first boundary where source paths are resolved, rather than checking it
  again after resolution.

## Next Improvements

- workflow: when a gate is flaky, first inspect whether the measurement rule is
  wrong before loosening the number.
- capability: runtime budget output now has enough fields to build a future
  ratchet report without rereading raw JSON.
- memory: next cleanup targets are `upstream_release_lib.py`,
  `control_plane_lib.py`, and `install_tools.py` near the 85% floor.

## Persisted

yes: `charness-artifacts/retro/2026-04-15-runtime-budget-update-proof.md`
