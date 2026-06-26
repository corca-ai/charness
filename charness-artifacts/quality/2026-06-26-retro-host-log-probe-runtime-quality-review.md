# Quality Review
Date: 2026-06-26

## Scope

Target boundary: duplicate `probe_host_logs.py` subprocess calls in
`tests/quality_gates/test_retro_host_log_probe.py`.

Ambient repo findings: the already-published `v0.56.1` state remains unchanged;
this is a local-only continuation slice.

## Current Gates

- Focused pytest passed all 17 retro host-log probe tests.
- Ruff passed for the changed test file.
- Boundary-bypass ratchet passed with no effective count regression.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  budget 90.0s; `pytest` 27.1s latest / 25.8s median, budget 140.0s.
- coverage gate: focused pytest, ruff, and boundary-bypass ratchet passed;
  broad read-only closeout remains reserved for the bundled boundary.
- evaluator depth: deterministic gates only; no evaluator-backed behavior seam
  was in scope.
- runtime interpretation: `probe_host_logs.py` subprocess calls in the changed
  test file dropped from 9 to 3 while retaining representative real CLI proof.

## Healthy

- Behavior assertions for invalid/empty host-log payloads now call
  `probe_host_logs.main()` in-process through pytest-scoped `sys.argv` and
  captured output.
- Real CLI proof remains for basic `--home` JSON output.
- Real CLI proof remains for `--home --repo-root --goal-path` goal-window
  success.
- Real CLI proof remains for the named `--claude-session-file` path.

## Weak

- File-level boundary-bypass counts do not change because retained CLI smokes
  remain in the same test file.
- This reduces process-launch overhead, not the underlying host-log parsing
  complexity.

## Missing

- Missing before this slice: six payload/behavior checks paid full subprocess
  startup even though the script exposes an import-safe `main()` seam.

## Deferred

- `measure_startup_probes.py` timeout tests remain deferred because their value
  depends on real process timeout and return-code behavior.

## Advisory

- structural review result: command:
  `rg -n "run_script\\(" tests/quality_gates/test_retro_host_log_probe.py`
  shows 3 retained real subprocess calls after conversion.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 77
  effective candidates and 40 clean-convertible files.

## Delegated Review

- Delegated Review: executed — bounded fresh-eye reviewer
  `019f0173-450d-7fc0-bc2e-9cdc55de4774` found no issues. It confirmed the
  remaining subprocess tests cover script bootstrap plus the important option
  families and that converted cases are payload/behavior checks.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through within-file subprocess call count,
  focused pytest, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_retro_host_log_probe.py`
- `python3 -m pytest -q tests/quality_gates/test_retro_host_log_probe.py`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- `rg -n "run_script\\(" tests/quality_gates/test_retro_host_log_probe.py`

## Recommended Next Gates

- active none — retained subprocess smokes plus focused tests cover this
  conversion.
- passive because out-of-scope for this slice: inspect larger validator fanout
  only when each retained CLI boundary can be named before conversion.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
