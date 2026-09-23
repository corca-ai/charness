# WI-2: executor availability probe and ordered fallback

Goal #844 slice 2 of 14. Hard dependency: WI-1 (reports through its kinds and codes; starts after WI-1 lands).

## Objective

Probe executor availability without starting a lane, report usage-limit style failures as typed `executor_unavailable` with `retry_after` (never a generic failure), and fall through an ordered `--executor codex,muse` list instead of stopping.

## Touchpoints

- `scripts/task_run/task_run_execution.py`: usage-limit detection becomes a typed failure.
- `scripts/task_run/task_run_state.py`: `executor_unavailable` kind plus exit 4 via the WI-1 map.
- `scripts/task_run/task_run.py`: `task executors` probe command (no lane start); ordered `--executor` fallback.
- New `tests/charness_cli/test_task_run_executor_probe.py`: fake-executor usage-limit string yields the typed kind, probe-without-lane, fallback-order cases.

## Acceptance

- A codex usage-limit failure yields `executor_unavailable` with `retry_after`, not a generic failure (#838).
- `charness task executors` shows availability without starting a lane (#838).
- Quota failure falls through to the next executor instead of stopping (#838).

## Out of scope

No changes to the codex/muse CLIs themselves (carrier boundary only); no new executors; no scheduling or DAG (WI-8b); no retry-policy changes beyond fallback ordering.

<!-- charness-work-item-key: wi-2-executor-probe -->
