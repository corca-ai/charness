# Quality Review
Date: 2026-08-05
Title: Issue #502 Quality Summary Owner

## Scope

Target boundary: the `run-quality.sh` quality-summary contract and its runner
tests. The question is whether semantic receipt fields, rather than copied
presentation prose, are the owned test seam.

Ambient repo findings: runtime/test-economics inventories report 481 test files,
195 standing files with nested CLI fan-out, a 798-code-line warn-band runner test,
and six stale unbudgeted runtime samples. These are not bundled into #502.

## Current Gates

- Focused contract suite: 72 passed — runner, aggregate, tail-delivery, and
  proof-receipt tests.
- Broad `./scripts/run-quality.sh --read-only`: 85 passed, 0 failed, 50.3s.
- Debug seam-risk index refreshed and validated after adding the issue artifact.
- No Cautilus evaluation run; deterministic gates are sufficient for this test
  contract migration.

## Runtime Signals

- runtime source: `python3 skills/public/quality/scripts/render_runtime_summary.py
  --repo-root . --summary` over `.charness/quality/runtime-signals.json`, rendered by
  the cited summary helper.
- runtime hot spots: `run-quality-read-only` latest 50,311ms, recent median
  80,393ms, budget 420,000ms; rendered by
  `render_runtime_summary.py`; no target-slice runtime regression was found.
- coverage gate: focused and broad deterministic suites pass after the repair.
- evaluator depth: deterministic-gates-only; Cautilus was not authorized or
  needed for a local receipt/test ownership change.

## Healthy

- `scripts/run-quality.sh` owns receipt argument assembly and
  `scripts/proof_receipt.py:209-224` owns quality-summary rendering.
- `tests/quality_gates/support.py` now gives runner tests one structured seam for
  surface, status, counts, exit code, adverse subjects, and unproven subjects.
- Exact renderer/CLI format and real final-line truncation behavior remain
  intentionally covered in their delivery-boundary tests.

## Weak

- Before this slice, runner tests asserted historical summary prose in many
  modules even though the production renderer was already centralized. That
  made a format change look like hand-edited test sanding.
- The helper is a checked-in convention, not a new validator; future tests could
  still bypass it, so the broad suite remains the enforcement backstop.

## Missing

- No missing proof remains for #502's local boundary. External CI/log-viewer
  truncation behavior is not claimed by local tests and remains outside scope.

## Deferred

- Do not change `run_slice_closeout.py` in this slice. Its closeout renderer has
  a separate focused verdict test and the causal sibling review found no same
  defect.
- Runtime/test-economics optimization is deferred until a measured proof-path
  comparison justifies a structural move.

## Advisory

- structural review result (command: `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root .`): target capability is maintainer ability to change a
  verdict surface without editing copied prose consumers; the generative
  sequence applies because owner -> structured consumer -> delivery proof is the
  uncertainty-reducing order. Existing centers are `proof_receipt.py`, the tail
  probe, and the quality runner; the strengthened center is the shared receipt
  assertion helper.
- prose review result (artifact: `charness-artifacts/debug/2026-08-05-issue-502-quality-summary-owner.md`): helper ownership is appropriate in the test support seam;
  renderer format remains an intentional presentation contract, and closeout is
  a separate surface. No skill-core or progressive-disclosure issue is in scope.
- inventory evidence: `inventory_standing_gate_verbosity.py --summary` reports
  the runner's phase and failure diagnostics healthy; `inventory_structural_waste.py
  --summary` finds no duplicate-discovery candidate for this slice.

## Delegated Review

- Delegated Review: executed — high-leverage fresh-eye reviewer returned Pass,
  confirmed structured receipt coverage across success/failure/unproven cases,
  found no blockers, and accepted closeout/runtime scope disposition. Parent
  boundary verification for window `issue-502-quality` was clean.
- Reviewer tier evidence: requested `gpt-5.6-terra` / medium; fields sent;
  host application is not independently exposed by the tool.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): not re-delegated; the issue is a narrow contract migration,
  and the standing quality inventory is advisory evidence only.

## Commands Run

- `python3 skills/public/quality/scripts/resolve_adapter.py --repo-root .`
- `python3 skills/public/quality/scripts/bootstrap_adapter.py --repo-root .`
- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root .`
- required quality primer references under `skills/public/quality/references/`
- `pytest -q tests/quality_gates/test_quality_runner.py tests/quality_gates/test_quality_runner_runtime_aggregate.py tests/quality_gates/test_gate_summary_names_failures.py tests/quality_gates/test_proof_receipt.py`
- quality inventories: standing gate verbosity, standing test economics,
  structural waste, and runtime summary.
- `./scripts/run-quality.sh --read-only` redirected to a full report; 85/85,
  50.3s.
- `python3 scripts/build_debug_seam_risk_index.py --repo-root . --write`
- `python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing`

## Recommended Next Quality Moves

- active capability_needed=maintainers need one semantic test contract for
  quality verdicts; next_center=tests/quality_gates/support.py;
  transformation=keep new runner assertions on `assert_quality_receipt` and
  reserve prose assertions for renderer/delivery tests;
  proof_boundary=focused 72 plus broad 85/0;
  enforcement_posture=existing-gate-reuse.
- passive capability_needed=standing test cost evidence because the current
  finding is advisory; next_center=runtime
  test-economics inventory; transformation=measure proof-preserving startup and
  nested-CLI alternatives before any pruning; proof_boundary=quality inventory
  plus a comparison card;
  enforcement_posture=no-gate because it is ambient to #502.

## History

- [Issue #503 runtime budget quality review](2026-08-05-issue-503-runtime-budget.md)
- [Standing quality review history](history/2026-07-14-open-issue-resolution-proof.md)
- [Issue #502 debug record](../debug/2026-08-05-issue-502-quality-summary-owner.md)
