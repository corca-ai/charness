# Quality Review
Date: 2026-06-26

## Scope

Target script path: `scripts/check_skill_surface_preflight.py` and the checked-in
`plugins/charness` mirror.

Ambient repo findings: broad non-release pytest identified
`test_run_checks_reports_all_portable_package_gates_on_real_repo` as the slowest
standing test; the underlying `--run-checks` path ran independent read-only
validators sequentially.

## Current Gates

- Ruff passed for the changed root script and test file.
- Focused skill-surface preflight tests passed.
- Focused run-checks integration tests passed.
- Boundary-bypass ratchet passed with no count regression.
- Plugin mirror drift check passed after syncing generated surfaces.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`, plus focused pytest and direct script
  wall-time samples from this slice.
- runtime hot spots: focused `test_skill_surface_preflight.py` dropped from
  9.71s to 6.88s; the slow integration call dropped from 7.10s to 4.26s in
  local samples.
- coverage gate: ruff, focused pytest, focused integration pytest,
  boundary-bypass ratchet, and staged mirror-drift check passed.
- evaluator depth: deterministic gates only; no evaluator-backed behavior was
  in scope.
- runtime interpretation: `--run-checks` now runs the same read-only portable
  package validators concurrently while preserving report order.

## Healthy

- The preflight still reports all portable-package checks in a deterministic
  order.
- Each validator keeps its own stdout/stderr tail and return code.
- The plugin mirror was regenerated.

## Weak

- Parallel read-only checks can increase short burst CPU load; this is bounded to
  six existing validators in an opt-in preflight path.

## Missing

- Missing before this slice: independent read-only package validators were paid
  sequentially even though the proof only needs their combined statuses.

## Deferred

- If future package validators mutate state, mark them nonparallel or split them
  out of this preflight set.

## Advisory

- profiling command: focused pytest showed
  `test_run_checks_reports_all_portable_package_gates_on_real_repo` at 7.10s
  before the change and 4.26s after the change.
- mirror command: `python3 scripts/check_staged_mirror_drift.py --repo-root .`
  passed after `python3 scripts/sync_root_plugin_manifests.py --repo-root .`.

## Delegated Review

- Delegated Review: not_applicable — bounded script-speed change with retained
  integration proof and mirror drift proof.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through pytest durations and the direct
  `--run-checks` script sample.

## Commands Run

- `python3 -m ruff check scripts/check_skill_surface_preflight.py tests/quality_gates/test_skill_surface_preflight.py`
- `pytest -q tests/quality_gates/test_skill_surface_preflight.py --durations=10`
- `pytest -q tests/quality_gates/test_skill_surface_preflight.py::test_run_checks_reports_all_portable_package_gates_on_real_repo tests/quality_gates/test_skill_surface_preflight.py::test_check_commands_cover_full_portable_package_gate_set --durations=5`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- `python3 scripts/check_staged_mirror_drift.py --repo-root .`

## Recommended Next Gates

- active none because focused preflight proof and mirror proof passed.
- passive because closeout is near: final broad read-only and release gates
  should run before push/release.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
