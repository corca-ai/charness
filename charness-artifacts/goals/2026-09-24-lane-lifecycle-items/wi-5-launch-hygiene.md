# WI-5: launch hygiene (freshness, skeleton, primitives, size)

Goal #844 slice 5 of 14. Soft dependencies: WI-1 (reconcile vocabulary at merge), WI-8b (only the skeleton-ordering half reads the DAG).

## Objective

Own launch-time hygiene as warnings and refusals: base freshness against the dependency tip (refuse or warn, never auto-rebase); shared-seam interfaces, builders, and simulators landing before sibling fan-out; grep-before-create shared-primitive rule with candidate reporting; declared lane size with a split suggestion past the calibrated limit. Verified with a standalone preflight-warn fixture that needs no DAG.

## Touchpoints

- `scripts/task_run/task_run_git.py`: base-vs-tip freshness check.
- `scripts/task_run/task_run_plan.py`: skeleton-first ordering, size calibration plus split suggestion.
- `scripts/task_run/task_run_lane_runner.py`: primitive-rule directive plus shared-primitive-candidate reporting.
- New `tests/charness_cli/test_task_run_launch_hygiene.py`: stale-base refuse/warn, oversize split suggestion, candidate-report cases.

## Acceptance

- A lane on a stale base is refused or warned; dependents stack on the predecessor tip (#843-4).
- Shared seams land before sibling fan-out (#843-5).
- Briefs grep before creating shared primitives; new ones are reported as candidates (#843-6).
- Briefs declare lane size; past the calibrated limit warns with a split suggestion (#843-7).

## Out of scope

No DAG or scheduler ownership (WI-8b); no premise verdicts (WI-4); no metric persistence (WI-10a).

<!-- charness-work-item-key: wi-5-launch-hygiene -->
