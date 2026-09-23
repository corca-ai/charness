# WI-3: mid-run steer channel plus same-candidate scope amend

Goal #844 slice 3 of 14. Hard dependency: WI-1 (steer accept/nack dispositions are recorded in the typed envelope).

## Objective

Let the integrator steer a running lane: `task steer` writes a message file into the lane runtime dir, the guard poll delivers it at the next turn boundary, and the result lists steer messages with timestamps. Same-candidate scope amend re-validates without relaunch where resume applies (#831/#834 stay fixed).

## Touchpoints

- `scripts/task_run/task_run_progress.py`: guard poll reads the steer queue; timestamp entries.
- `scripts/task_run/task_run_lane_runner.py`: inject steer text at the next turn boundary.
- `scripts/task_run/task_run_scope.py`: scope amend re-validates the same candidate.
- `scripts/task_run/task_run.py`: `task steer` subcommand.
- New `tests/charness_cli/test_task_run_steer.py`: transcript-before-next-edit, timestamped result list, amend-vs-relaunch cases.

## Acceptance

- A message steered into a running codex or muse lane appears in the lane transcript before its next edit (#837).
- The result YAML lists the steer messages with timestamps (#837).

## Out of scope

No relaunch path where steer or resume applies; no rewrite of the original brief; no lesson injection (WI-6) or decision ledger (WI-9); no executor-side changes.

<!-- charness-work-item-key: wi-3-steer -->
