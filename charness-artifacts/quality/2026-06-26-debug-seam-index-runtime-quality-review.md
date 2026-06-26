# Quality Review
Date: 2026-06-26

## Scope

Target boundary: duplicate `build_debug_seam_risk_index.py` subprocess calls in
`tests/quality_gates/test_debug_seam_risk_index.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed both debug seam-risk index tests.
- Ruff passed for the changed test file.
- Boundary-bypass ratchet passed with one fewer effective candidate.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  budget 90.0s; `pytest` 27.1s latest / 25.8s median, budget 140.0s.
- coverage gate: focused pytest, ruff, and boundary-bypass ratchet passed;
  broad read-only closeout remains reserved for the bundled boundary.
- evaluator depth: deterministic gates only; no evaluator-backed behavior seam
  was in scope.
- runtime interpretation: `run_script(...)` calls in the changed file dropped
  from 2 to 1 while retaining the write-mode CLI smoke.

## Healthy

- The stale-index check now calls `build_debug_seam_risk_index.main()` in-process
  and maps `ValidationError` to the same stderr/return-code shape as the script
  wrapper.
- The retained subprocess still proves the write path, JSON stdout, and index
  file creation through the command entrypoint.
- The boundary-bypass ratchet reflects the conversion as a real candidate-count
  reduction.

## Weak

- The converted helper mirrors the `__main__` exception wrapper locally; future
  script-wrapper behavior changes should update this helper if needed.

## Missing

- Missing before this slice: stale-index rejection paid full process startup
  despite not requiring separate command bootstrap proof.

## Deferred

- Do not convert the write-mode subprocess without adding a different command
  smoke for JSON output and file creation.

## Advisory

- structural review result: command:
  `git show HEAD:tests/quality_gates/test_debug_seam_risk_index.py | rg -c "run_script\\("`
  returned 2; current
  `rg -c "run_script\\(" tests/quality_gates/test_debug_seam_risk_index.py`
  returned 1.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 74
  effective candidates and 37 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — low-risk stale-check conversion with a
  retained write-mode CLI smoke and deterministic focused proof.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through helper call count, focused pytest, and the
  boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_debug_seam_risk_index.py`
- `python3 -m pytest -q tests/quality_gates/test_debug_seam_risk_index.py`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- `git show HEAD:tests/quality_gates/test_debug_seam_risk_index.py | rg -c "run_script\\("`
- `rg -c "run_script\\(" tests/quality_gates/test_debug_seam_risk_index.py`

## Recommended Next Gates

- active none — retained write-mode CLI proof plus focused tests cover this
  conversion.
- passive because out-of-scope for this slice: leave broader read-only quality
  gate for final closeout reserve.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
