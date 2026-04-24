# Session Retro: Runtime Profile and Subagent Review
Date: 2026-04-24

## Context

This session optimized `./scripts/run-quality.sh`, added profile-aware runtime
budget design, and tightened `quality`/`init-repo` guidance around delegated
review.

## Waste

- The first runtime-optimization passes used direct local exploration before
  applying the repo rule that task-completing `quality` and `init-repo` reviews
  should run bounded delegated review.
- That delayed two useful facts: runtime budgets were machine-profile blind,
  and only the final runtime-budget phase has a real ordering dependency.

## Critical Decisions

- Treat runtime budgets as named runner profiles selected by
  `CHARNESS_RUNTIME_PROFILE`, not automatic hardware fingerprints.
- Make delegated slow-gate review explicit in the public quality guidance:
  fixture economics, parallel critical path, duplicated proof, adapter/runtime
  budget policy, and operator signal.

## Expert Counterfactuals

- Gary Klein-style premortem would have asked which quality review invariant
  was already mandated by the repo before the first local-only optimization.
- Daniel Kahneman-style base-rate check would have separated "pytest is slow"
  from runner/profile variance and phase-barrier effects earlier.

## Next Improvements

- Workflow: when `quality` or `init-repo` scope is broad and task-completing,
  spawn bounded reviewers before finalizing the diagnosis.
- Capability: keep runtime-budget contracts profile-aware so samples from
  different machines do not share one hard threshold.
- Memory: this retro records the missed sequencing so future slow-gate work
  starts with delegated lenses instead of adding them after user correction.

## Persisted

yes `charness-artifacts/retro/2026-04-24-runtime-profile-subagent-review.md`
