# WI-6: lessons-ledger injection into lane prompts

Goal #844 slice 6 of 14. Soft dependencies: WI-1 (result block follows its shape at merge), WI-3 (shared `task_run_lane_runner.py` edits merge, not block).

## Objective

Inject ledger lessons matching the lane's `--scope` paths or tags into the lane prompt automatically, under a byte budget with a pointer to the full ledger, and record injected lesson ids in the result so a review can tell a failed lesson from a failed injection.

## Touchpoints

- `scripts/task_run/task_run_lane_runner.py`: prompt assembly plus budgeted injection.
- `scripts/task_run/task_run_completion.py`: injected-ids result block (WI-1 shape at merge).
- New `tests/charness_cli/test_task_run_lesson_inject.py`: scope-match injects, budget cap, ids-in-result cases.

## Acceptance

- A lane scoped to paths matching a lesson's tags receives that lesson in its prompt (#842).
- The result YAML lists the injected lesson ids (#842).
- Budget plus full-ledger pointer present, so reviews can judge lesson-failed versus injection-failed (#842).

## Out of scope

No ledger-format migration or new ledger store; no post-compaction re-injection (WI-11); no ranking or ML matching (scope/tag match only); no prompt changes beyond the injected block.

<!-- charness-work-item-key: wi-6-lesson-inject -->
