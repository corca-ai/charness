# Runtime-root retention: first mechanism run, 2026-09-03 (#787)

The one-off hand sweep earlier the same day (`runtime-sweep-2026-09-03.md`)
took `~/.cache/tmp/charness/runtime/` from 340 GB across 1,871 keys to about
25 GB. This record is the first run of the mechanism that replaces it:
`scripts/gates_support/runtime_root_retention.py`, invoked by the standing
pytest runner at the start of every run and by hand.

## Root cause fixed first

`runtime_bootstrap._runtime_root` derived a child's base from the inherited
`XDG_CACHE_HOME`, which a bootstrapped parent exports as `<its key>/xdg-cache`,
so a child for another repo landed at `<parent key>/xdg-cache/charness/runtime/<child key>`.
Now an inherited base that is a bootstrap's own `xdg-cache` export inside a
`charness/runtime` tree is hoisted to the base above that tree, so keys are
siblings. Proven by `tests/test_runtime_root_retention.py::test_a_child_bootstrapped_from_a_key_lands_beside_it_not_inside_it`
for the three inherited shapes (auto key env, the `task run` preview env, a
lane's private runtime). Live-tree assumption named while writing it: pytest's
`tmp_path` sits under this run's own key, so a cache home a test points there
must be used as given; only the bootstrap's own export is rewritten.

## Before (read 2026-09-03 17:5x, after the hand sweep and a day of test runs)

| Surface | Value |
| --- | --- |
| tree | 16 GB, 263 keys (the hand sweep left 5; today's test runs created the rest, 1.4 MB each, all touched today) |
| this repo's key `811b9f8f8a808bfa` | 11 GB: `pytest-tmp` 4.5, `pycache` 2.4, `coverage` 2.1, `xdg-cache` 1.4 holding 1,108 nested fixture keys created before the fix |
| installed plugin's key `a349c5fc98dc0a12` | 4.8 GB |
| disk | `/home` 750 GB used, 1.1 TB free |

Dry run by hand before the hook was wired: 598 `would-remove`, all finished
fixture-repo lanes' `runtime/` directories inside nested keys (`result.json`
and logs kept), 1,287 skipped as touched within the one-day active window;
0.6 s wall.

## First real run

`<key>/retention/sweep-1788425968.json`, written at 17:59:28 by the standing
runner hook on the first focused test run after wiring: `removed 598`
(4 MiB; the same 598 lane runtimes), `skipped 1287`. Eight later runs the same
hour: `skipped` only, nothing to do. The by-hand run recorded for this slice
(`sweep-1788426234.json`): `skipped 1368` (1,108 nested keys and 258 sibling
keys touched within the active window, 2 unmarked keys with entries newer than
14 days), `removed 0`.

## After

Unchanged on disk at this granularity: tree 16 GB, this key 11 GB, installed
plugin key 4.8 GB, `/home` 750 GB used. Everything still present was touched
today; under the written rule the 1,108 nested keys and the 258 fixture keys
become removable after `ACTIVE_WINDOW_DAYS` (1 day), and `pycache`/`coverage`
after `SUBTREE_MAX_AGE_DAYS` (14). The seeded tests prove each removal class
against an idle tree; this record proves the mechanism runs on the live tree,
skips a live tree with a reason per entry, and touches nothing outside
`charness/runtime/`.

## Lanes at completion

`task run` now releases a `completed` commit-only lane's `worktree/` and
`runtime/` at completion (`retention` in the receipt names `branch@sha`);
any other finished lane is retained until the sweep salvages its uncommitted
edits beside `result.json`. Proven by `tests/charness_cli/test_task_run.py::test_task_run_assigns_distinct_lane_runtime_roots_and_releases_finished_lanes`
and `..._a_worktree_only_candidate_keeps_its_lane_worktree`.
