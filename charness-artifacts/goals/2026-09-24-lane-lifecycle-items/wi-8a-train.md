# WI-8a: generic merge-train core plus repo verify profile

Goal #844 slice 8 of 14. Soft dependency: WI-1 (reads outcome vocabulary; reconciles with the extension at merge).

## Objective

Build the generic multi-lane integration core: stack queued branches on main, verify the stacked tip once with a repo-declared verify profile (commands plus a known-failure baseline), land everything on green; on red, bisect the queue to name the first bad branch and land the good prefix; refuse to land and re-queue when main moves mid-verification. The decision core (queue plus outcomes, then the next action) stays pure and unit-testable. Re-derived against this repo's tests, not a verbatim import of any consumer prototype.

## Touchpoints

- New `scripts/task_run/task_run_train.py`: decision core plus verify-profile loader.
- `scripts/task_run/task_run.py`: `train` command surface.
- New `tests/charness_cli/test_task_run_train.py`: one-verify-lands-N, first-red naming, main-move re-queue cases.

## Acceptance

- One verify run lands N non-conflicting branches (#841).
- A red train names the first failing branch and lands the green prefix (#841).
- If main moves during a train, the train refuses to land and re-queues (#841).
- The repo supplies only the verify profile (#841).

## Out of scope

No DAG queue (WI-8b); no review trigger inside the train (WI-7 consumes the landed range); no test cache (WI-10b consumes verify outcomes separately).

<!-- charness-work-item-key: wi-8a-train -->
