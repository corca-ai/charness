<!-- charness-work-item-key: runtime-root-retention -->

## Objective

The per-repo runtime root owned by `scripts/runtime_bootstrap.py` stops nesting other repos' runtime roots inside its own `xdg-cache` and gains a retention policy for its own subtrees and for top-level keys. Measured 2026-09-03: this repo's key 50 GB (`xdg-cache` 41 GB holding 23,401 nested keys; `pytest-tmp` 4.5 GB; `pycache` 2.4 GB; `coverage` 2.1 GB); `charness/runtime/` 1,871 keys, 340 GB.

## Owned scope

- `scripts/runtime_bootstrap.py::_runtime_root`: on a `CHARNESS_RUNTIME_REPO_KEY` mismatch, derive the base from the parent's configured base (the parent of `charness/runtime/<key>`), not from the parent's exported `XDG_CACHE_HOME`; regression test seeds the mismatch and asserts sibling keys. Grep tests for `xdg-cache` and `runtime_root(` first and name any live-tree assumption.
- Retention, beside `standing_pytest_basetemp.py`'s existing sweep or in a sibling: `pycache`, `coverage`, `xdg-cache/charness/runtime/<nested>` under the dead-key rule; top-level keys under `prune_dead_repo_keys` extended from `pytest-tmp` to the whole key; a report mode that lists what would be removed with bytes and reason, and a skipped list (active lock, fresh entry, recorded repo root present).
- The deleting sweep refuses to run unless a report-mode output younger than a stated window exists at the path it writes its own log to, and deletes only the keys that report named; a test seeds the missing report and reads the refusal. First run in report mode; the operator reads the report; then the deleting run. Both outputs recorded under `charness-artifacts/goal-runs/<parent>/runtime-root-sweep.md`.
- `docs/development.md` cache table: rows for the runtime root's own subtrees and for keys.

## Acceptance

- A child bootstrapped for a second repo root from this repo's environment lands at `charness/runtime/<other key>`, a sibling, and the test proves it.
- The deleting sweep with no fresh report is refused (seeded test); report-mode and deleting-run counts recorded side by side and matching; `du` on the repo key before and after.
- Nothing outside `charness/runtime/` touched; `git status` clean of runtime paths.

## Focused verification

Standing lane on `tests/test_runtime_bootstrap*.py` and the basetemp tests, then the standing runner.

## Dependencies

none

## Non-claims

Does not change `TMPDIR` placement, the pytest basetemp contract, or the seed and support-skill caches' own rules.
