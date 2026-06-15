# Quality Review
Date: 2026-06-16
## Scope

Operator-requested test-speed-first repair, third slice.

Goal: remove the remaining duplicate slow broad pytest closeout path. The
repo-python surface, `run-quality.sh`, broad pytest lock/cache detection, and
mutation coverage instrumentation now share `scripts/run_standing_pytest.py`.

## Current Gates

- Standing pytest runner:
  `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only`:
  **3138 passed in 30.23s** standalone; **3138 passed in 21.53s** inside locked
  slice closeout.
- `run-quality` pytest label:
  `CHARNESS_QUALITY_LABELS=pytest ./scripts/run-quality.sh --read-only`:
  **PASS pytest 32.3s**, **Quality summary: 1 passed, 0 failed, total 32.5s**.
- Focused contract pytest:
  runner tests, quality-runner env tests, surface ordering tests, broad detector
  tests, mutation producer instrumentation tests, and plugin preamble smoke:
  **20 passed in 5.44s**.
- Static gates:
  `ruff check` on changed Python files: **passed**.
  `./scripts/check-shell.sh`: **passed**.
  `python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing`:
  **passed for 807 files** with the existing `run_slice_closeout.py` advisory.
  `python3 scripts/plugin_preamble.py --repo-root . --json`:
  `root_install_surface.ok: true`.
- Packaging mirror:
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .`: **ran**.
  `python3 scripts/validate_packaging_committed.py --repo-root .`: **passed**.
- Locked slice closeout with focused mutation coverage producer: **completed**.
  Broad runner proof elapsed **22.4s**; focused producer elapsed **8.3s** and
  emitted `reports/mutation/test-coverage.json` <!-- reproduction-source -->.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py` via `scripts/record_quality_runtime.py`;
  profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 65.7s latest / 66.6s median;
  `pytest` 27.6s latest / 22.3s median, budget 140.0s; previous closeout broad
  pytest path was **247.0s** because repo-python surface still owned a duplicate
  serial pytest string.
- coverage gate: closeout producer refreshed `reports/mutation/test-coverage.json` <!-- reproduction-source -->.
  Post-commit changed-line consumer must still be rerun because HEAD excludes
  uncommitted mutation-pool changes.
- evaluator depth: deterministic gates only. Cautilus planner returned
  `next_action: none`; the required public-skill review was handled as a
  dogfood contract decision, not an evaluator run.
- Current `run-quality` pytest label: **32.3s**. The small delta is quality
  harness overhead, not a second broad pytest implementation.

## Standing Test Economics

- `scripts/run_standing_pytest.py` is now the single source for standing pytest
  targets, release-only exclusion, quiet pytest flags, xdist detection, outside
  repo basetemp behavior, success cleanup, and `CHARNESS_QUALITY_MODE`.
- `run-quality.sh` gets its target list and temp-root value from the runner, so
  early fixture-budget checks and pytest execution share the same temp contract.
- The repo-python closeout command is now
  `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only`.
- The runner still falls back to serial pytest when pytest-xdist is unavailable,
  with an explicit warning.

## Healthy

- Broad pytest lock/cache policy still applies because
  `slice_closeout_broad_gate.is_broad_pytest_command()` recognizes the standing
  runner and excludes print-only helper calls.
- Mutation coverage producer instrumentation accepts the standing runner under
  `coverage run`, preserving producer proof behavior when broad runner coverage
  is selected.
- `quality` standing-gate verbosity inventory treats the standing runner as a
  quiet pytest runner because the runner itself pins `-q`.
- Checked-in plugin exports were resynced.

## Weak

- `scripts/run_slice_closeout.py` remains in the advisory length band at 465
  Python code lines; this slice avoided adding more code there.
- Changed-line mutation coverage consumer must be rerun after commit; the
  pre-commit probe warned that uncommitted mutation-pool changes are excluded
  from `HEAD`.

## Missing

- No deterministic enforcement gap is known for this slice after focused and
  standing proofs.

## Deferred

- Keep future broad pytest behavior changes routed through
  `scripts/run_standing_pytest.py`; do not add surface-local pytest strings.
- Extract closeout producer planning from `run_slice_closeout.py` before adding
  more closeout behavior there.

## Advisory

- The earlier 247.0s broad pytest advisory was real because it measured a duplicate
  serial surface command, not the canonical `run-quality` pytest path; evidence:
  prior `charness-artifacts/quality/latest.md` closeout command payload.
- `quality` public-skill dogfood review command: consulted
  `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`;
  the existing consumer contract still applies.

## Delegated Review

- Fresh-eye critique executed through the repo-authorized bounded subagent path
  for the standing pytest speed diff.
- Slow-gate lenses covered: fixture-economics, parallel-critical-path, and
  duplicated-proof.
- Findings fixed before closeout: expanded standing targets for
  `check-test-completeness`, and rejected standing-runner helper modes from
  broad pytest and mutation coverage proof classification.

## Commands Run

- `python3 /home/hwidong/.codex/plugins/cache/local/charness/0.50.1/skills/find-skills/scripts/list_capabilities.py --repo-root . --recommend-for-task "broad pytest runtime speed" --summary`.
- `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only`.
- `CHARNESS_QUALITY_LABELS=pytest ./scripts/run-quality.sh --read-only`.
- Focused contract pytest command listed in Current Gates.
- `ruff check` on changed Python files.
- `./scripts/check-shell.sh`.
- `python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing`.
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`.
- `python3 scripts/plugin_preamble.py --repo-root . --json`.
- `python3 scripts/validate_packaging_committed.py --repo-root .`.
- Locked `run_slice_closeout.py --verification-lock --produce-mutation-coverage`.

## Recommended Next Gates

- active commit this slice, then rerun changed-line mutation coverage consumer
  because the consumer excludes uncommitted mutation-pool changes from `HEAD`.

## History

- [2026-06-12 quality review](history/2026-06-12-quality-review.md)
