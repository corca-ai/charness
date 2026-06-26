# Quality Review
Date: 2026-06-26

## Scope

Target boundary: duplicate `seed_usage_episodes_adapter.py` subprocess calls in
`tests/quality_gates/test_setup_seed_usage_episodes.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 6 setup usage-episodes tests.
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
- runtime interpretation: `seed_usage_episodes_adapter.py` subprocess calls in
  the changed file dropped from 5 to 3 while retaining write/refusal CLI proof.

## Healthy

- Dry-run schema validation and force-overwrite behavior now call
  `seed_usage_episodes_adapter.main()` in-process through pytest-scoped
  `sys.argv` and captured output.
- Real CLI proof remains for initial adapter write.
- Real CLI proof remains for refusing overwrite without `--force`.

## Weak

- The retained subprocess calls still cover the important file-write boundary,
  so file-level boundary-bypass counts do not change.
- This is a small cumulative reduction rather than a broad suite speedup by
  itself.

## Missing

- Missing before this slice: two non-unique setup cases paid full process
  startup despite using an import-safe `main()` seam.

## Deferred

- Additional conversion is deferred because adapter writes and overwrite
  refusal are the meaningful shipped CLI behavior in this file.

## Advisory

- structural review result: command:
  `git show HEAD:tests/quality_gates/test_setup_seed_usage_episodes.py | rg -c "run_script\\("`
  returned 5; current `rg -c "run_script\\(" tests/quality_gates/test_setup_seed_usage_episodes.py`
  returned 3.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 77
  effective candidates and 40 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — low-risk two-call conversion with retained
  write/refusal CLI smokes and deterministic focused proof.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through within-file subprocess call count,
  focused pytest, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_setup_seed_usage_episodes.py`
- `python3 -m pytest -q tests/quality_gates/test_setup_seed_usage_episodes.py`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- `git show HEAD:tests/quality_gates/test_setup_seed_usage_episodes.py | rg -c "run_script\\("`
- `rg -c "run_script\\(" tests/quality_gates/test_setup_seed_usage_episodes.py`

## Recommended Next Gates

- active none — retained write/refusal CLI smokes plus focused tests cover this
  conversion.
- passive because out-of-scope for this slice: review seed_dependencies.py
  separately because recommendation-based discovery has different inputs.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
