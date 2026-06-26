# Quality Review
Date: 2026-06-26

## Scope

Target boundary: duplicate `seed_dependencies.py` subprocess calls in
`tests/quality_gates/test_setup_seed_dependencies.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 5 setup dependency seed tests.
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
- runtime interpretation: `seed_dependencies.py` subprocess calls in the
  changed file dropped from 7 to 5 while retaining write/refusal/error CLI
  proof.

## Healthy

- Recommendation seeding and force-overwrite payload checks now call
  `seed_dependencies.main()` in-process through pytest-scoped `sys.argv`,
  captured output, and `SystemExit` handling.
- Real CLI proof remains for initial explicit dependency write.
- Real CLI proof remains for overwrite refusal without `--force`.
- Real CLI proof remains for mutually-exclusive explicit/recommendation input.

## Weak

- The retained subprocess setup call inside the force-overwrite test means the
  raw call-count reduction is intentionally small.
- File-level boundary-bypass counts do not change because retained CLI smokes
  remain in the same test file.

## Missing

- Missing before this slice: recommendation and force payload checks paid full
  process startup even though the script exposes an import-safe `main()` seam.

## Deferred

- Additional conversion is deferred because the remaining subprocess calls
  prove write, refusal, and invalid-input behavior.

## Advisory

- structural review result: command:
  `git show HEAD:tests/quality_gates/test_setup_seed_dependencies.py | rg -n "run_script\\("`
  showed 7 calls; current `rg -n "run_script\\(" tests/quality_gates/test_setup_seed_dependencies.py`
  shows 5 calls.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 77
  effective candidates and 40 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — low-risk two-behavior conversion with
  retained write/refusal/error CLI smokes and deterministic focused proof.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through within-file subprocess call count,
  focused pytest, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_setup_seed_dependencies.py`
- `python3 -m pytest -q tests/quality_gates/test_setup_seed_dependencies.py`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- `git show HEAD:tests/quality_gates/test_setup_seed_dependencies.py | rg -n "run_script\\("`
- `rg -n "run_script\\(" tests/quality_gates/test_setup_seed_dependencies.py`

## Recommended Next Gates

- active none — retained write/refusal/error CLI smokes plus focused tests cover
  this conversion.
- passive because out-of-scope for this slice: larger seed-script conversion
  should first separate setup calls from behavior assertions.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
