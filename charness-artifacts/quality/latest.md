# Quality Review
Date: 2026-06-16

## Scope

Operator-requested test-speed-first repair. Routing: `find-skills` -> `quality`
with implementation through the existing repo gate surface. Scope stayed on the
standing local test/runtime hot spot, especially `check-coverage`.

## Current Gates

- Focused proof: `pytest -q tests/quality_gates/test_check_coverage_inventory.py
  tests/quality_gates/test_repo_copy_invariants.py`: **17 passed**.
- Lint proof: `ruff check scripts/check_coverage.py
  tests/quality_gates/test_check_coverage_inventory.py
  tests/quality_gates/test_repo_copy_invariants.py tests/repo_copy.py`:
  **passed**.
- `CHARNESS_QUALITY_LABELS=check-coverage ./scripts/run-quality.sh --read-only`:
  **1 passed, 0 failed, `check-coverage` 16.7s**.
- Full `./scripts/run-quality.sh --read-only` after mirror sync and artifact
  fixes: **78 passed, 0 failed, total 45.0s**.
- Locked closeout producer:
  `python3 scripts/run_slice_closeout.py --repo-root . --verification-lock
  --produce-mutation-coverage`: **completed**; broad pytest under coverage
  passed in **462.9s** and refreshed `reports/mutation/test-coverage.json` <!-- reproduction-source -->
  plus its freshness marker.
- Earlier full run before mirror sync/ruff fix: **75 passed, 3 failed, total
  45.1s**; failures were expected drift/formatting from the live diff and were
  fixed before final full gate.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 65.7s latest / 66.6s
  median; `check-coverage` 47.1s latest / 46.6s median; `pytest` 23.0s latest /
  22.2s median.
- coverage gate: `check-coverage` passed after repair in 16.7s through a focused
  `run-quality` label run and 20.0s inside the final full read-only gate;
  coverage JSON diff against the pre-`ignoredirs` run was empty.
- evaluator depth: deterministic gates only; no log-backed behavior failure or
  Cautilus planner-triggering request was present.
- direct baseline during repair: `python3 scripts/check_coverage.py --repo-root .
  --json` was **38.2s** after the `reports` copy-ignore change alone.
- implemented repair: exclude generated `reports/` from repo-copy fixtures and
  pass Python runtime stdlib/site-package directories as `trace.Trace`
  `ignoredirs`, while filtering out any runtime dir that would contain the repo
  root.
- direct proof after repair: `python3 scripts/check_coverage.py --repo-root .
  --json` was **16.6s**; JSON diff against the pre-`ignoredirs` run was empty.
- label proof after repair: `check-coverage` passed through `run-quality` in
  **16.7s**.

## Standing Test Economics

- `inventory_standing_test_economics.py --json`: `test_file_count=309`,
  `nested_cli_file_count=136`, and 6.4GB allocated pytest temp retention across
  2 retained sessions.
- `runner_snippets` showed the standing `run-quality` pytest command still uses
  the fixed broad target set, so this slice avoided pruning tests or changing
  selection semantics.
- The selected repair avoided pruning tests or weakening proof. It reduces
  tracer overhead inside the existing control-plane coverage gate.

## Healthy

- The coverage summary output stayed identical across the tracer narrowing.
- Fresh-eye code critique found no `Act Before Ship` concerns.
- The plugin mirror was refreshed with
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .`.

## Weak

- Full read-only closeout must be rerun after sync/critique artifact updates; the
  first full run intentionally exposed the unsynced plugin mirror.
- The coverage gate still performs broad scripted scenarios; this slice reduces
  tracer overhead but does not restructure duplicated proof inside the scenario
  set.

## Missing

- No missing repo-local enforcement was found for this slice.

## Deferred

- Centralizing duplicate repo-copy ignore lists is valid but deferred; this slice
  only added `reports` to the existing surfaces and pinned behavior with tests.
- A future intentional checked-in `reports/` fixture would need an explicit
  exemption or fixture shape change.

## Advisory

- `inventory_ci_recoverable_gates.py --json`: `check-coverage` remains
  `keep-local`; CI does not fully backstop this proof.
- `check-changed-line-mutation-coverage`: warned that uncommitted eligible
  Python changes are not analyzed before commit. Final closeout must refresh
  mutation coverage for the locked diff if the slice remains mutation-pool
  eligible.
- `run_slice_closeout.py`: emitted a gate-baseline runtime advisory because the
  instrumented broad pytest producer took 462.9s; this is accepted for the locked
  producer path, not as a new local speed win.

## Delegated Review

- Delegated Review: executed. Bounded fresh-eye code critique used three angle
  reviewers plus one counterweight reviewer through the repo-authorized
  subagent path. Reviewer tier requested: `high-leverage`; requested spawn
  fields sent: `model=gpt-5.5, reasoning_effort=medium, service_tier=priority`;
  host exposure state: `requested_fields_sent`; application state:
  `unverified-by-host`.
- Findings: no `Act Before Ship`; helper tests and repo-under-runtime guard were
  bundled and implemented; duplicate ignore-list centralization deferred.
- Slow-gate lenses named for this runtime/test review: fixture-economics,
  parallel-critical-path, duplicated-proof.

## Commands Run

- `python3 /home/hwidong/.codex/plugins/cache/local/charness/0.50.1/skills/find-skills/scripts/list_capabilities.py --repo-root . --recommend-for-task "테스트 속도 개선" --summary`.
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root .
  --json`; `inventory_standing_test_economics.py --json`;
  `inventory_ci_recoverable_gates.py --json`.
- `python3 scripts/check_coverage.py --repo-root . --json` before and after the
  tracer narrowing; JSON diff was empty.
- Focused pytest, touched-file ruff, `CHARNESS_QUALITY_LABELS=check-coverage
  ./scripts/run-quality.sh --read-only`, full `./scripts/run-quality.sh
  --read-only`, `python3 scripts/run_slice_closeout.py --repo-root .
  --verification-lock --produce-mutation-coverage`, and
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .`.

## Recommended Next Gates

- active none — the immediate deterministic speed repair is implemented.
- passive rerun full read-only closeout after artifacts/mirror changes lock because the first full run intentionally caught pre-sync drift.
- passive evaluate deeper test-economics cleanup with a candidate scorecard before pruning nested CLI tests because nested CLI fanout is advisory evidence, not proof that any specific test is waste.

## History

- [2026-06-12 quality review](history/2026-06-12-quality-review.md)
