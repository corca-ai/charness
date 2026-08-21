# Quality Review
Date: 2026-08-21
Title: Fresh-eye, retro basis, and parallel coverage handoff

## Scope

The `critique`/`prove` fresh-eye consumer contract, retro planner change-basis
packet, installed planner path, reviewer-boundary snapshot continuation, and
parallel focused-coverage producer output ownership.

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
- A focused producer report is not allowed to use a shared public path when the
  quality runner can execute beside another producer; the runner owns an
  external per-run report namespace and the producer derives its runtime files
  from that report path.
- The mapped changed-line pool must be clean before the release candidate is
  rebound.

## Runtime Signals

- Current direct changed-line command returned `status: clean`, base
  `33e556043174ce6e32d25da51e8397e18e941613`, resolved HEAD
  `abaf886822a851c1081ec889f6733c02b627e525`, 1/1 mapped pool files, and
  `blocking_targets: {}`; standing pytest passed.
- While that direct producer ran, `CHARNESS_QUALITY_LABELS=check-changed-line-mutation-coverage
  ./scripts/run-quality.sh --read-only` returned `1 passed, 0 failed` in
  `230.3s`; its report was under an external per-run temp namespace and did not
  collide with the direct producer's default report/runtime paths.
- The subsequent committed-tree broad `./scripts/run-quality.sh --read-only`
  returned `97 passed, 0 failed` in `300.8s`; its standing pytest passed in
  `149.9s` and its full changed-line producer passed in `275.9s`.
- Focused current runner/mutation/prepush/staged-plan bundle: 107 passed before
  the test-module split; final post-split focused bundle: 38 passed. Commit
  preflight for `abaf88682`: passed.
- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; focused producer stdout and the
  generated focused-coverage receipt are supplementary.
- runtime hot spots: direct changed-line producer runtime was 71.8 seconds;
  the concurrent runner-owned focused lane was 230.3 seconds; the committed
  broad run was 300.8 seconds end to end.
- coverage gate: exact-base changed-line coverage is clean for 1/1 mapped file
  with no blocking targets; the current-head proof from base `b6567606e` was
  `status: noop` because no eligible mutation-pool file changed.
- evaluator depth: deterministic focused gates only; Cautilus was not run.

## Healthy

- Source/plugin mirrors are byte-identical for the changed skill and shared
  surfaces.
- Each runner process owns a distinct focused coverage report stem under the
  external temp root; direct invocation retains the documented public default.
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
  wrong quality-validator flag, guessed handoff checker path, and an attempted
  `validate_handoff_artifact.py --path` flag were corrected by file inventory/help
  before treating any result as evidence.
- The direct producer emitted coverage's `already-imported` warning for its
  default sitecustomize path. Its typed gate payload was still `status: clean`,
  and the concurrently run quality lane used a distinct external namespace with
  no shared-path warning; retain the direct warning as an advisory runtime smell,
  not as approval or as a silent failure.

## Delegated Review

- Delegated Review: not_applicable for a new round because the active
  verdict-surface two-round cap was already consumed.
- No new fresh-eye approval is claimed. Post-round repairs are
  `accepted-unreviewed-under-round-cap`, and the consumer still requires a
  typed successful receipt/report join before approval eligibility.

## Commands Run

- `python3 -m pytest -q` focused runner/mutation/prepush/staged-plan bundle:
  107 passed before the test-module split; final post-split focused bundle:
  38 passed.
- `python3 scripts/run_slice_closeout.py --repo-root . --predict-commit
  --paths ... --skip-broad-pytest`: 23 pre-commit commands passed.
- `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root .
  --base-sha 33e556043174ce6e32d25da51e8397e18e941613`: clean.
- `CHARNESS_QUALITY_LABELS=check-changed-line-mutation-coverage
  ./scripts/run-quality.sh --read-only`: `1 passed, 0 failed` while the direct
  producer ran concurrently; no shared-path collision/no-verdict occurred.

## Recommended Next Quality Moves

- active requalify the five current-open post-lock exceptions against this committed
  candidate, then bind the semantic release packet before version mutation.

## History

- [Fresh-eye delivery boundary spec](../spec/2026-08-21-fresh-eye-delivery-boundary.md)
- [Portable proof-path learning review](history/2026-07-19-portable-proof-path-learning-review.md)
