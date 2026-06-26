# Quality Review
Date: 2026-06-26

## Scope

Target boundary: `tests/quality_gates/test_hitl_report_mode.py` repeated
subprocess calls into `skills/public/hitl/scripts/render_report.py`.

Ambient repo findings: file-level boundary-bypass inventory does not improve
because the same test file still intentionally retains real CLI proof.

## Current Gates

- Focused pytest passed all 12 HITL report-mode tests.
- Ruff passed for the changed test file.
- Boundary-bypass ratchet passed with no effective count regression.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  budget 90.0s; `pytest` 25.9s latest / 25.7s median, budget 140.0s.
- coverage gate: focused pytest, ruff, and boundary-bypass ratchet passed;
  broad read-only closeout remains final-bundle proof.
- evaluator depth: deterministic gates only; no evaluator-backed behavior seam
  was in scope.
- runtime interpretation: the file-level ratchet is unchanged, but local command
  evidence shows `run_script(` occurrences dropped from 14 to 4 while preserving
  one handled-error real CLI proof.

## Healthy

- Report behavior tests now call `render_report.main()` in-process through a
  pytest-scoped argv/capture helper.
- Real CLI proof remains for stdout indentation, argparse required-argument
  behavior, and handled `ReportModeError` process exit behavior.
- Error-path behavior still asserts stderr text and non-zero return codes
  through the same `main()` exception handling used by the script.

## Weak

- The boundary-bypass inventory is file/key based, so it cannot show this
  within-file reduction directly.
- The helper pattern still monkeypatches `sys.argv`; it should remain
  test-local and not become global fixture state.

## Missing

- Missing before this slice: most HITL report rendering behavior paid a Python
  subprocess even though the script already had an import-safe `main()` seam.

## Deferred

- No production `hitl` behavior changed.
- No public skill prose or release surface changed in this slice.

## Advisory

- structural review result: command:
  `rg -c "run_script\\(" tests/quality_gates/test_hitl_report_mode.py` compared
  against `git show HEAD:...` shows 4 current calls vs 14 at the slice base.
- ratchet result: command: `check_boundary_bypass_ratchet.py --repo-root .`
  passed with 77 effective candidates and 40 clean-convertible files.

## Delegated Review

- Delegated Review: executed — bounded fresh-eye reviewer
  `019f0163-21e9-7c40-9fff-21702c8405cf` found one Medium issue: handled-error
  CLI exit proof had been weakened. The slice restored one duplicate-id
  subprocess smoke, leaving 4 real CLI calls instead of 3, and focused pytest
  passed afterward.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through within-file subprocess call count,
  focused pytest, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_hitl_report_mode.py`
- `python3 -m pytest -q tests/quality_gates/test_hitl_report_mode.py`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root .`
- `rg -c "run_script\\(" tests/quality_gates/test_hitl_report_mode.py`
- `git show HEAD:tests/quality_gates/test_hitl_report_mode.py | rg -c "run_script\\("`

## Recommended Next Gates

- active none — the existing focused tests and retained CLI smokes cover this
  conversion.
- passive teach the boundary-bypass inventory a within-file subprocess-call metric because file-level counts cannot show this runtime improvement.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
