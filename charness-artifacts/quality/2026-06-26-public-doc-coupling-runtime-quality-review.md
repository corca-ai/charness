# Quality Review
Date: 2026-06-26

## Scope

Target boundary: duplicate `check_public_doc_coupling.py` subprocess calls in
`tests/quality_gates/test_check_public_doc_coupling.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 8 public-doc-coupling tests.
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
- runtime interpretation: `check_public_doc_coupling.py` subprocess calls in
  the changed file dropped from 5 to 2 while retaining text-output CLI smokes.

## Healthy

- JSON advisory fixture tests now call `check_public_doc_coupling.main()`
  in-process through pytest-scoped `sys.argv` and captured output.
- Real CLI proof remains for clean human text output.
- Real CLI proof remains for advisory human text output naming the policy owner.

## Weak

- JSON mode no longer has file-local subprocess proof, but it is still exercised
  through argparse and stdout in-process.
- File-level boundary-bypass counts do not change because retained CLI smokes
  remain in the same test file.

## Missing

- Missing before this slice: three JSON advisory fixtures paid full process
  startup despite no distinct script bootstrap requirement.

## Deferred

- No additional conversion is planned in this file; retained subprocesses are
  the text-output delivery smokes.

## Advisory

- structural review result: command:
  `git show HEAD:tests/quality_gates/test_check_public_doc_coupling.py | rg -c "run_script\\("`
  returned 5; current `rg -c "run_script\\(" tests/quality_gates/test_check_public_doc_coupling.py`
  returned 2.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 77
  effective candidates and 40 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — low-risk advisory scanner conversion with
  retained text-output CLI smokes and deterministic focused proof.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through within-file subprocess call count,
  focused pytest, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_check_public_doc_coupling.py`
- `python3 -m pytest -q tests/quality_gates/test_check_public_doc_coupling.py`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- `git show HEAD:tests/quality_gates/test_check_public_doc_coupling.py | rg -c "run_script\\("`
- `rg -c "run_script\\(" tests/quality_gates/test_check_public_doc_coupling.py`

## Recommended Next Gates

- active none — retained text-output CLI smokes plus focused tests cover this
  conversion.
- passive because out-of-scope for this slice: keep looking for JSON-only
  advisory fixtures with retained text CLI proof.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
