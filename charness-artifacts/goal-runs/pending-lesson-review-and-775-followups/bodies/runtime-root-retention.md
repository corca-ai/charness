<!-- charness-work-item-key: runtime-root-retention -->

## Objective

The per-repo runtime root owned by `scripts/runtime_bootstrap.py` stops nesting other repos' runtime roots inside its own `xdg-cache`, `task run` stops keeping a finished lane's worktree and runtime, and the tree gains a retention policy for its own subtrees and for top-level keys. Measured 2026-09-03: `charness/runtime/` 1,871 keys, 340 GB. The installed plugin's key holds 271 GB, of which 250 GB is the ceal repo's `task-run/` (254 finished lanes, each a 1.4 GB worktree plus a 1.1 GB runtime beside a 60 KB `result.json`) and 16 GB this repo's `task-run/`; this repo's key holds 50 GB (`xdg-cache` 41 GB holding 23,401 nested fixture-repo keys; `pytest-tmp` 4.5 GB; `pycache` 2.4 GB; `coverage` 2.1 GB).

## Owned scope

- `scripts/runtime_bootstrap.py::_runtime_root`: on a `CHARNESS_RUNTIME_REPO_KEY` mismatch, derive the base from the parent's configured base (the parent of `charness/runtime/<key>`), not from the parent's exported `XDG_CACHE_HOME`; regression test seeds the mismatch and asserts sibling keys. Grep tests for `xdg-cache` and `runtime_root(` first and name any live-tree assumption.
- `scripts/task_run/`: at completion, once `result.json` is published, the lane's `worktree/` and `runtime/` are removed; `result.json` and the codex logs stay. A test proves the removal and that the result is intact.
- Retention, beside `standing_pytest_basetemp.py`'s existing sweep or in a sibling: finished `task-run/<id>/` records reduced to result and logs; `pycache` and `coverage` bounded by size or age; `xdg-cache/charness/runtime/<nested>` removed; top-level keys under `prune_dead_repo_keys` extended from `pytest-tmp` to the whole key. The sweep runs directly (operator, 2026-09-03: no report-first step), skips anything with an active lock, a fresh entry, or a recorded repo root that still exists, and writes what it removed and skipped with bytes and reason to its log; `--dry-run` is an ordinary flag. The first run's log and `du` before and after recorded under `charness-artifacts/goal-runs/<parent>/runtime-root-sweep.md`.
- `docs/development.md` cache table: rows for the runtime root's own subtrees and for keys.

## Acceptance

- A child bootstrapped for a second repo root from this repo's environment lands at `charness/runtime/<other key>`, a sibling, and the test proves it.
- A finished lane keeps only `result.json` and logs (test); the first sweep's log recorded with `du` before and after on the installed plugin's key and this repo's key.
- Nothing outside `charness/runtime/` touched; no lane `result.json` or log removed; `git status` clean of runtime paths.

## Focused verification

Standing lane on `tests/test_runtime_bootstrap*.py`, the basetemp tests, and `tests/test_task_run*.py`, then the standing runner.

## Dependencies

none

## Non-claims

Does not change `TMPDIR` placement, the pytest basetemp contract, or the seed and support-skill caches' own rules.
