# Quality Review
Date: 2026-06-16

## Scope

Operator-requested continuation of test-speed optimization and structural
prevention after the standing pytest runner slice.

This slice removed two avoidable broad-gate costs:

- `check-test-completeness` no longer runs duplicate pytest collection.
- `check-current-pointer-writes` no longer AST-parses every Python file when a
  cheap text prefilter proves the file cannot write `latest.md`/`latest.json`.

## Current Gates

- Full read-only quality:
  `./scripts/run-quality.sh --read-only`: **78 passed, 0 failed, total 38.1s**.
- Focused pytest:
  python3 -m pytest -q tests/quality_gates/test_current_pointer_writes.py
  tests/quality_gates/test_check_test_completeness.py
  tests/quality_gates/test_quality_runner.py::test_run_quality_passes_expanded_targets_to_test_completeness
  tests/quality_gates/test_quality_runner.py::test_run_quality_enforces_current_pointer_write_scan:
  **25 passed in 3.81s**.
- `check-test-completeness` latest full run: **PASS 76ms**.
- `check-current-pointer-writes` latest full run: **PASS 480ms**.
- Boundary-bypass ratchet:
  `python3 scripts/check_boundary_bypass_ratchet.py --repo-root .`:
  **OK**.
- Packaging mirror:
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .`: **ran**.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `skills/public/quality/scripts/render_runtime_summary.py` and
  recorded by `scripts/record_quality_runtime.py`.
- runtime hot spots: `run-quality-read-only` **38.1s** latest; `pytest`
  **22.0s** latest / **22.5s** median; `check-coverage` **19.6s** latest /
  **43.8s** median, budget **55.0s**.
- coverage gate: full read-only quality passed; closeout producer refreshed
  `reports/mutation/test-coverage.json` <!-- reproduction-source -->.
- evaluator depth: deterministic gates only; no Cautilus evaluator run was
  requested or required for this optimization slice.
- direct speed probes: `check-current-pointer-writes` dropped from **7.72s** to
  **0.40s**; `check-test-completeness` quality label measured **61ms**.

## Root Causes

- `check-test-completeness` paid for `pytest --collect-only` twice even though
  `run-quality` had already expanded the standing pytest targets.
- `check-current-pointer-writes` scanned 490 visible Python files with AST
  parsing. Only 8 files contained both a current-pointer filename and a write
  token, so most parsing was provably irrelevant.
- The earlier multi-hundred-second pytest path was a separate duplicate surface:
  closeout owned a serial broad pytest string instead of the canonical standing
  runner. That was already fixed by routing broad pytest through
  `scripts/run_standing_pytest.py`.

## Structural Prevention

- Standing pytest target coverage is now file-based and deterministic.
- Current-pointer write scanning now has an explicit candidate predicate:
  files must contain `latest.md`/`latest.json` and a write/open token before AST
  parsing is allowed.
- Tests cover target completeness, missing-file reporting, current-pointer
  detection, and non-candidate prefilter behavior.
- Generated plugin mirrors were resynced so the exported plugin carries the same
  gate behavior.

## Healthy

- `check-current-pointer-writes` still detects direct `write_text`,
  `write_bytes`, `Path.open("w")`, builtin `open(..., "w")`, simple filename
  constants, and shadowed local constants.
- `check-test-completeness` still fails when a discoverable pytest file under
  `tests/` is not included by the standing target list.
- `check-coverage` remains meaningful and was not weakened; its current cost is
  tied to traced control-plane scenario coverage, not cheap duplicate scanning.

## Weak

- `scripts/run_slice_closeout.py` remains in the advisory length band at 465
  Python code lines.
- Full read-only quality still warns before commit because uncommitted
  mutation-pool files are excluded from `HEAD`; closeout producer was refreshed.
- `latest.md` current-pointer semantics remain inconsistent across artifact
  directories; tracked as GitHub issue #377.

## Missing

- No deterministic enforcement gap is known for this slice after focused tests,
  boundary ratchet, packaging sync, and full read-only quality.

## Deferred

- Do not optimize `check-coverage` by weakening trace coverage. If it needs a
  speed slice, split scenario setup or fixture-copy cost under a separate
  coverage-preserving design.
- Resolve issue #377 before changing broad current-pointer artifact behavior
  across skills.

## Advisory

- The speed gain is legitimate because it removed duplicate discovery/parsing,
  not proof obligations. The remaining large costs are intentional proof paths.

## Delegated Review

- executed: bounded fresh-eye subagent reviewed the uncommitted diff read-only.
  Slow-gate lenses: fixture-economics, parallel-critical-path, duplicated-proof.
  Blocking artifact-shape finding was fixed here; no blocking script issue was
  reported.

## Commands Run

- python3 -m pytest -q ... focused current-pointer/completeness runner tests.
- `CHARNESS_QUALITY_LABELS=check-test-completeness ./scripts/run-quality.sh --read-only`.
- `CHARNESS_QUALITY_LABELS=check-current-pointer-writes ./scripts/run-quality.sh --read-only`.
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root .`.
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`.
- `./scripts/run-quality.sh --read-only`.
- `python3 scripts/record_quality_runtime.py --repo-root . --label run-quality-read-only --elapsed-ms 38100 --status pass`.
- locked `run_slice_closeout.py --verification-lock --produce-mutation-coverage`.

## Recommended Next Gates

- active Commit this slice, then rerun the changed-line mutation coverage
  consumer against committed `HEAD`.

## History

- [2026-06-12 quality review](history/2026-06-12-quality-review.md)
