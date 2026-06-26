# Quality Review
Date: 2026-06-26

## Scope

Target boundary: duplicate `check_test_repo_copy_invariants.py` subprocess calls
in `tests/quality_gates/test_repo_copy_invariants.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 11 repo-copy invariant tests.
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
- runtime interpretation: `check_test_repo_copy_invariants.py` subprocess calls
  in the changed file dropped from 5 to 1 while retaining a real current-repo
  CLI smoke.

## Healthy

- Synthetic drift fixtures now call `check_test_repo_copy_invariants.main()`
  in-process through pytest-scoped `sys.argv` and captured output.
- Real CLI proof remains for the current repo invariant check.

## Weak

- This reduces process-launch overhead for synthetic fixtures only.
- File-level boundary-bypass counts do not change because the retained CLI
  smoke remains in the same test file.

## Missing

- Missing before this slice: four synthetic repo-copy invariant fixtures paid
  full process startup despite no distinct CLI mode.

## Deferred

- No additional conversion is planned in this file; the remaining subprocess is
  the intended current-repo script-bootstrap smoke.

## Advisory

- structural review result: command:
  `git show HEAD:tests/quality_gates/test_repo_copy_invariants.py | rg -c "run_script\\("`
  returned 5; current `rg -c "run_script\\(" tests/quality_gates/test_repo_copy_invariants.py`
  returned 1.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 77
  effective candidates and 40 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — low-risk synthetic-fixture conversion with
  retained current-repo CLI smoke and deterministic focused proof.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through within-file subprocess call count,
  focused pytest, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_repo_copy_invariants.py`
- `python3 -m pytest -q tests/quality_gates/test_repo_copy_invariants.py`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- `git show HEAD:tests/quality_gates/test_repo_copy_invariants.py | rg -c "run_script\\("`
- `rg -c "run_script\\(" tests/quality_gates/test_repo_copy_invariants.py`

## Recommended Next Gates

- active none — retained current-repo CLI smoke plus focused tests cover this
  conversion.
- passive because out-of-scope for this slice: avoid converting tests that
  intentionally prove copy-heavy release-only behavior through broader gates.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
