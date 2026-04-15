# Session Retro: Coverage Floor and Runtime Budget Ratchet

## Mode

session

## Context

This slice followed the handoff cleanup by simplifying exported control-plane
code enough to raise the enforced per-file coverage floor from 80% to 85%.
It also exposed that the runtime budget gate was using latest-sample thresholds
that were tighter than normal full-review variance.

## Evidence Summary

- Changed files hit `checked-in-plugin-export` and
  `integrations-and-control-plane`, which triggered auto-retro.
- `./scripts/run-quality.sh --review` now passes with `36 passed, 0 failed`,
  total `43.0s`.
- `check-coverage` reports `89.7%` aggregate control-plane coverage and zero
  files below the `85.0%` per-file floor.

## Waste

Running full quality in parallel with closeout created a false packaging/import
failure because one process read the checked-in plugin tree while another was
resyncing it. The first full review also showed that latest-sample runtime
budgets can create noise when the budget is below observed full-review variance.

## Critical Decisions

- Raised the per-file control-plane floor to `85.0%` only after every tracked
  file cleared it through production simplification and focused scenario
  coverage.
- Removed support-sync branches that no current manifest contract needed, rather
  than preserving them and compensating with more tests.
- Rebased runtime budgets on observed variance so the gate still catches real
  regressions without failing normal full-review samples.

## Expert Counterfactuals

- Gary Klein's premortem lens would have asked how a parallel closeout and full
  review could invalidate each other's observations before trusting either
  failure.
- W. Edwards Deming's variation lens would have treated one slow runtime sample
  as process data first, then adjusted the control limit instead of asking
  operators to rerun until green.

## Next Improvements

- workflow: do not run plugin-export sync/closeout concurrently with full
  quality review; serialize those gates when the plugin tree is in scope.
- capability: if runtime budgets keep needing manual interpretation, replace
  latest-sample-only enforcement with a small report over recent samples.
- memory: next coverage cleanup targets are `support_sync_lib.py`,
  `upstream_release_lib.py`, and `control_plane_lib.py` near the 85% floor.

## Persisted

yes: `charness-artifacts/retro/2026-04-15-coverage-floor-runtime-budget.md`
