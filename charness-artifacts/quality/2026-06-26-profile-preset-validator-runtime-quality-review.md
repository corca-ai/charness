# Quality Review
Date: 2026-06-26

## Scope

Target boundary: simple `validate_profiles.py` and `validate_presets.py`
subprocess assertions inside
`tests/quality_gates/test_profile_and_preset_validation.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 18 profile/preset validation tests.
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
- runtime interpretation: three pure profile/preset validator subprocesses were
  replaced with direct validator function calls; the file's dominant runtime
  remains adapter validation, which this slice deliberately left untouched.

## Healthy

- Missing-skill, organization-scope, and product-slice exposure failures now
  call the real validator functions and assert the same error messages.
- Gitignored-file checks and adapter validation subprocesses remain command
  tests.

## Weak

- Runtime reduction is modest because the slowest tests in the file are
  adapter-validation command tests.

## Missing

- Missing before this slice: simple validator error checks paid process startup
  cost despite direct validation functions being available.

## Deferred

- Adapter validation remains a larger, boundary-sensitive target for a later
  slice with its own proof plan.

## Advisory

- structural review command: `rg -n "run_script\\(" tests/quality_gates/test_profile_and_preset_validation.py`
  shows three pure profile/preset validator subprocesses removed while
  gitignored and adapter command checks remain.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 73
  effective candidates and 35 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — small direct validator conversion with
  retained command-boundary tests in the same file.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through subprocess launch count, focused pytest
  durations, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_profile_and_preset_validation.py`
- `python3 -m pytest -q tests/quality_gates/test_profile_and_preset_validation.py --durations=10`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`

## Recommended Next Gates

- active none — focused profile/preset tests cover this conversion.
- passive because out-of-scope for this slice: leave broad read-only quality
  gate for final closeout reserve.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
