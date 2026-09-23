# WI-10b: content-addressed test-result cache

Goal #844 slice 12 of 14. Integration gates: WI-1 and WI-8a (the skip decision reads the frozen kind/exit codes and verify outcomes; starts after both land).

## Objective

Skip re-verification when nothing changed: a test file whose content hash plus its import-closure hash matches a previous green run is skipped. A skip is an optimization only and never asserts completion; failed provider readback stays `unverified`.

## Touchpoints

- New `scripts/task_run/task_run_test_cache.py`: hash-keyed cache plus skip decision.
- `scripts/task_run/task_run_changed_line.py`: cache-skip hook at verification.
- New `tests/charness_cli/test_task_run_test_cache.py`: hash-hit skip, content-change rerun, closure-change invalidation cases.

## Acceptance

- A test file with matching content and import-closure hashes against a prior green run is skipped; any hash change re-runs (#843-14).
- Re-verification after main moves, the largest share of integration lead time, shrinks to hash comparison for unchanged files (#843-14).

## Out of scope

No train integration beyond consuming verify outcomes (WI-8a); no cache invalidation beyond the two hashes; verdict-logic edits need changed-line and mutation proof.

<!-- charness-work-item-key: wi-10b-test-cache -->
