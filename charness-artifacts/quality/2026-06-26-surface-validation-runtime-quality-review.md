# Quality Review
Date: 2026-06-26

## Scope

Target boundary: selected `validate_surfaces.py` subprocess assertions inside
`tests/quality_gates/test_surface_obligations.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 25 surface-obligation tests.
- Ruff passed for the changed test file.
- Boundary-bypass ratchet passed with no count regression.

## Runtime Signals

- runtime source: focused pytest duration output from this slice plus structured
  metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  budget 90.0s; `pytest` 27.1s latest / 25.8s median, budget 140.0s.
- coverage gate: focused pytest with `--durations=10`, ruff, and
  boundary-bypass ratchet passed; broad read-only closeout remains reserved for
  the bundled boundary.
- evaluator depth: deterministic gates only; no evaluator-backed behavior seam
  was in scope.
- runtime interpretation: three surface-manifest validation subprocesses were
  replaced with direct `load_surfaces()` calls; focused file runtime sample
  dropped from 4.21s to 4.04s.

## Healthy

- Recursive glob footgun cases now call the exact `load_surfaces()` validator
  and assert `SurfaceError` message fragments directly.
- Duplicate-id failure and bare-recursive success command smokes remain.
- The command-heavy check/select surface routing tests remain subprocess tests.

## Weak

- Runtime impact is modest because the file mostly tests command routing
  behavior that should stay at the CLI boundary.

## Missing

- Missing before this slice: pure manifest validation cases paid command startup
  cost despite direct validator access.

## Deferred

- Do not convert the check_changed_surfaces/select_verifiers tests without a
  separate command-routing proof plan.

## Advisory

- structural review command: `rg -n "validate_surfaces|run_script\\(" tests/quality_gates/test_surface_obligations.py`
  shows three selected validate_surfaces subprocesses removed while command
  routing smokes remain.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 73
  effective candidates and 35 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — small direct manifest-validator conversion
  with retained CLI routing tests.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through subprocess launch count, focused pytest
  durations, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_surface_obligations.py`
- `python3 -m pytest -q tests/quality_gates/test_surface_obligations.py --durations=10`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`

## Recommended Next Gates

- active none — focused surface-obligation tests cover this conversion.
- passive because out-of-scope for this slice: leave broad read-only quality
  gate for final closeout reserve.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
