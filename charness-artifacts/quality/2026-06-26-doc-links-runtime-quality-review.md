# Quality Review
Date: 2026-06-26

## Scope

Target boundary: duplicate `scripts/check_doc_links.py` subprocess calls in
`tests/quality_gates/test_check_doc_links.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 18 check-doc-links tests.
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
- runtime interpretation: `check_doc_links.py` subprocess calls in the changed
  file dropped from 18 to 3 while retaining representative real CLI proof.

## Healthy

- Link-rule behavior tests now call `check_doc_links.main()` in-process through
  pytest-scoped `sys.argv`, captured output, and the same `ValidationError`
  wrapper as the script entrypoint.
- Real CLI proof remains for an absolute-link failure.
- Real CLI proof remains for a successful normal scan.
- Real CLI proof remains for explicit `--require-git-file-listing` with
  gitignored markdown.

## Weak

- The converted tests no longer prove script bootstrap individually; that proof
  is intentionally consolidated into three representative subprocess smokes.
- File-level boundary-bypass counts do not change because retained CLI smokes
  remain in the same test file.

## Missing

- Missing before this slice: fifteen doc-link rule assertions paid full Python
  process startup even though the validator exposes an import-safe `main()` seam.

## Deferred

- No additional check-doc-links conversion is planned in this file; the three
  retained subprocess calls are the intended boundary smokes.

## Advisory

- structural review result: command:
  `git show HEAD:tests/quality_gates/test_check_doc_links.py | rg -c "run_script\\("`
  returned 18; current `rg -c "run_script\\(" tests/quality_gates/test_check_doc_links.py`
  returned 3.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 77
  effective candidates and 40 clean-convertible files.

## Delegated Review

- Delegated Review: executed — bounded fresh-eye reviewer
  `019f017a-9b2e-74b0-8f58-7603a89697c2` found no blocking issue. It confirmed
  the helper mirrors the script wrapper and that retained subprocess smokes
  cover failure, success, and the argument surface; its `--require-git-file-listing`
  caveat was fixed before commit.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through within-file subprocess call count,
  focused pytest, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_check_doc_links.py`
- `python3 -m pytest -q tests/quality_gates/test_check_doc_links.py`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- `git show HEAD:tests/quality_gates/test_check_doc_links.py | rg -c "run_script\\("`
- `rg -c "run_script\\(" tests/quality_gates/test_check_doc_links.py`

## Recommended Next Gates

- active none — retained subprocess smokes cover failure, success, and the
  explicit `--require-git-file-listing` mode.
- passive because out-of-scope for this slice: inspect other validator fanout
  only after naming retained subprocess proof per CLI mode.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
