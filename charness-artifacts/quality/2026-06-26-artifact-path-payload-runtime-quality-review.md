# Quality Review
Date: 2026-06-26

## Scope

Target boundary: repeated `resolve_artifact_path.py` command launches inside
`tests/quality_gates/test_artifact_naming.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 18 artifact-naming tests.
- Ruff passed for the changed script and test file.
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
- runtime interpretation: three path-calculation tests moved from subprocess
  CLI execution to in-process `payload_for()` calls with explicit adapters; the
  three-test sample changed from visible 0.08s-0.10s call durations to all calls
  below pytest's 0.005s duration display threshold.

## Healthy

- `resolve_artifact_path.py` now exposes `payload_for()` for reuse while
  retaining `main()` as the command wrapper.
- Tests still cover record intent, rolling handoff current paths, and symlinked
  current-pointer write targets.
- Exported resolver and refresh-current-pointer tests remain CLI/subprocess
  tests, preserving packaging and command-boundary proof.

## Weak

- Three tests no longer prove parser/bootstrap behavior for
  `resolve_artifact_path.py`; command proof remains in exported resolver and
  invalid-artifact-class cases.

## Missing

- Missing before this slice: path payload construction was not directly reusable
  outside CLI execution.

## Deferred

- Do not convert exported plugin resolver or refresh-current-pointer tests
  without an equivalent package-level command proof.

## Advisory

- structural review result: direct `resolve_artifact_path.py` command launches
  in the converted tests dropped from 3 to 0.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 73
  effective candidates and 35 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — low-risk extraction with retained exported
  command proof and deterministic focused proof.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through subprocess launch count, focused pytest
  durations, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check scripts/resolve_artifact_path.py tests/quality_gates/test_artifact_naming.py`
- `python3 -m pytest -q tests/quality_gates/test_artifact_naming.py --durations=10`
- `python3 -m pytest -q tests/quality_gates/test_artifact_naming.py::test_resolve_artifact_path_reports_record_and_current_paths tests/quality_gates/test_artifact_naming.py::test_handoff_current_path_remains_docs_handoff tests/quality_gates/test_artifact_naming.py::test_current_intent_resolves_symlinked_latest_to_write_target --durations=3`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`

## Recommended Next Gates

- active none — focused artifact-naming tests and retained command smokes cover
  this conversion.
- passive because out-of-scope for this slice: leave broad read-only quality
  gate for final closeout reserve.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
