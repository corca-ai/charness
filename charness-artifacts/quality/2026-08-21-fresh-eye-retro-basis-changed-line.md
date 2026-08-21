# Quality Review
Date: 2026-08-21
Title: Fresh-eye and retro basis handoff

## Scope

The `critique`/`prove` fresh-eye consumer contract, retro planner change-basis
packet, installed planner path, and reviewer-boundary snapshot continuation.

## Surface Contract Review

- semantic coverage: partial — typed consumer contracts and mapped planner pool;
  host delivery and public release are not.
- surface: standalone `critique`, `prove` closeout binding, retro planner, and
  reviewer-boundary snapshot receipt.
- owner: critique owns fresh-eye execution/delivery; prove binds it; retro owns
  trigger basis; the boundary helper owns verify continuation fields.
- projections: skill guidance, adapter mode/backend, typed worker report,
  planner packet, YAML receipt, and source/plugin export.
- state scope: one bounded review/retro slice and one reviewer boundary window.
- transitions: packet preparation, worker receipt, findings delivery, approval
  eligibility, trigger evaluation, snapshot, and verify continuation.
- proof boundary: focused tests, pre-commit, exact-base changed-line proof, and
  local packaging/parity; no host/public/install proof.
- unexamined axes: typed host-subagent delivery, Windows host behavior, managed
  install/update, hosted readback, issue closure, and Cautilus.

## Current Gates

- A process exit, non-empty output, `delivery_complete`, or bare post-commit
  trigger invocation cannot render fresh-eye approval or trigger evaluation.
- The mapped changed-line pool must be clean before the release candidate is
  rebound.

## Runtime Signals

- Exact-base changed-line command returned `status: clean`, base
  `a1e69e8125b9fac962fdf1f4d0b32aa0cc4f9647`, resolved HEAD
  `33e556043174ce6e32d25da51e8397e18e941613`, 3/3 mapped pool files, and
  `blocking_targets: {}`; standing pytest passed.
- Focused related tests: 175 passed. Commit preflight: 23 commands passed.
- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; focused producer stdout and the
  generated focused-coverage receipt are supplementary.
- runtime hot spots: exact changed-line producer runtime was 55.5 seconds;
  broad quality was run separately and its receipt is still being inspected.
- coverage gate: exact-base changed-line coverage is clean for 3/3
  mapped files with no blocking targets.
- evaluator depth: deterministic focused gates only; Cautilus was not run.

## Healthy

- Source/plugin mirrors are byte-identical for the changed skill and shared
  surfaces.
- Planner packets carry explicit paths or `HEAD^..HEAD` basis and basis-less
  plans remain `not-established`.
- Snapshot receipts expose `verify_before` and exact `verify_args`.

## Weak

- The two touched Python owners remain in the advisory length band and should
  be split again on the next substantive change rather than shaved.

## Missing

- No runtime evidence establishes the Codex interrupted-delivery host path or a
  typed host-subagent result reaching the parent context.

## Deferred

- Current-open post-lock issue requalification and release-candidate rebinding
  remain the next R2/R3 work.

## Advisory

- command-boundary smell: guessed ledger path, missing required `--ledger` flag,
  wrong quality-validator flag, and guessed handoff checker path were corrected
  by file inventory/help before treating any result as evidence.

## Delegated Review

- Delegated Review: not_applicable for a new round because the active
  verdict-surface two-round cap was already consumed.
- No new fresh-eye approval is claimed. Post-round repairs are
  `accepted-unreviewed-under-round-cap`, and the consumer still requires a
  typed successful receipt/report join before approval eligibility.

## Commands Run

- `python3 -m pytest -q` focused critique/prove/worker/report/fingerprint/retro
  suites: 175 passed.
- `python3 scripts/run_slice_closeout.py --repo-root . --predict-commit
  --paths ... --skip-broad-pytest`: 23 pre-commit commands passed.
- `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root .
  --base-sha a1e69e8125b9fac962fdf1f4d0b32aa0cc4f9647`: clean.

## Recommended Next Quality Moves

- active requalify the five current-open post-lock exceptions against this committed
  candidate, then bind the semantic release packet before version mutation.

## History

- [Fresh-eye delivery boundary spec](../spec/2026-08-21-fresh-eye-delivery-boundary.md)
- [Portable proof-path learning review](history/2026-07-19-portable-proof-path-learning-review.md)
