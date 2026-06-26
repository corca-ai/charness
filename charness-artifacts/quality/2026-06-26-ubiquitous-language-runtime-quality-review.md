# Quality Review
Date: 2026-06-26

## Scope

Target boundary: duplicate `inventory_ubiquitous_language.py` subprocess calls
in `tests/quality_gates/test_quality_ubiquitous_language.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 5 ubiquitous-language tests.
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
- runtime interpretation: `inventory_ubiquitous_language.py` subprocess calls
  in the changed file dropped from 5 to 2 while retaining unconfigured and
  current-repo CLI smokes.

## Healthy

- Contract-backed synthetic scanner fixtures now call
  `inventory_ubiquitous_language.main()` in-process through pytest-scoped
  `sys.argv` and captured output.
- Real CLI proof remains for unconfigured adapter behavior.
- Real CLI proof remains for the current repo contract baseline.

## Weak

- This conversion leaves JSON mode CLI proof split across two retained smokes
  rather than every fixture.
- File-level boundary-bypass counts do not change because retained CLI smokes
  remain in the same test file.

## Missing

- Missing before this slice: three contract-backed synthetic fixtures paid full
  process startup despite using no distinct CLI mode.

## Deferred

- No additional conversion is planned in this file; retained subprocesses cover
  script bootstrap for unconfigured and current-repo states.

## Advisory

- structural review result: command:
  `git show HEAD:tests/quality_gates/test_quality_ubiquitous_language.py | rg -c "run_script\\("`
  returned 5; current `rg -c "run_script\\(" tests/quality_gates/test_quality_ubiquitous_language.py`
  returned 2.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 77
  effective candidates and 40 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — low-risk synthetic scanner conversion with
  retained unconfigured/current-repo CLI smokes and deterministic focused proof.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through within-file subprocess call count,
  focused pytest, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_quality_ubiquitous_language.py`
- `python3 -m pytest -q tests/quality_gates/test_quality_ubiquitous_language.py`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- `git show HEAD:tests/quality_gates/test_quality_ubiquitous_language.py | rg -c "run_script\\("`
- `rg -c "run_script\\(" tests/quality_gates/test_quality_ubiquitous_language.py`

## Recommended Next Gates

- active none — retained CLI smokes plus focused tests cover this conversion.
- passive because out-of-scope for this slice: leave current-repo scanner smokes
  as subprocess-backed proof.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
