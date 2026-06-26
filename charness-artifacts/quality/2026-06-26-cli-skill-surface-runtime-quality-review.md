# Quality Review
Date: 2026-06-26

## Scope

Target boundary: duplicate `scripts/check_cli_skill_surface.py` subprocess calls
in `tests/quality_gates/test_cli_skill_surface.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 9 CLI-skill-surface tests.
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
- runtime interpretation: `check_cli_skill_surface.py` subprocess calls in the
  changed file dropped from 9 to 3 while retaining probe-execution smokes.

## Healthy

- Static adapter-rule behavior tests now call `check_cli_skill_surface.main()`
  in-process through pytest-scoped `sys.argv` and captured output.
- Real CLI proof remains for basic `--repo-root --json` not-applicable output.
- Real CLI proof remains for `--run-probes --json` success and actual command
  execution.
- Real CLI proof remains for probe timeout behavior through a real subprocess.

## Weak

- Converted static-rule tests no longer prove script bootstrap individually;
  that proof is intentionally consolidated into three representative subprocess
  smokes.
- File-level boundary-bypass counts do not change because retained CLI smokes
  remain in the same test file.

## Missing

- Missing before this slice: six static adapter-rule assertions paid full
  Python process startup despite using no external probe execution.

## Deferred

- No additional conversion is planned for the two `--run-probes` tests because
  they prove subprocess command execution and timeout behavior.

## Advisory

- structural review result: command:
  `git show HEAD:tests/quality_gates/test_cli_skill_surface.py | rg -c "run_script\\("`
  returned 9; current `rg -c "run_script\\(" tests/quality_gates/test_cli_skill_surface.py`
  returned 3.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 77
  effective candidates and 40 clean-convertible files.

## Delegated Review

- Delegated Review: executed — bounded fresh-eye reviewer
  `019f017d-a9c5-7f11-96a1-1d3e2f1ab86c` found no blocking issue. It confirmed
  retained subprocess proof for basic bootstrap, `--run-probes` success, and
  timeout probe execution; it noted `--changed-path` remains covered through
  in-process argparse and is not boundary-critical here.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through within-file subprocess call count,
  focused pytest, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_cli_skill_surface.py`
- `python3 -m pytest -q tests/quality_gates/test_cli_skill_surface.py`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- `git show HEAD:tests/quality_gates/test_cli_skill_surface.py | rg -c "run_script\\("`
- `rg -c "run_script\\(" tests/quality_gates/test_cli_skill_surface.py`

## Recommended Next Gates

- active none — retained subprocess smokes cover bootstrap, probe execution,
  and timeout behavior.
- passive because out-of-scope for this slice: inspect remaining validator
  fanout only when external probe execution can stay on a real subprocess path.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
