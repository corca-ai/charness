# Standing Suite Cutover Regression Debug Review
Date: 2026-08-27

## Problem

The first `#546` changed-line proof attempt could not complete because the
incremental producer's standing run failed after the issue-native Goal
Run/provider cutover. This left the child without a changed-line verdict even
though its focused runtime-budget tests passed.

## Correct Behavior

The focused producer must run the standing tests that map to the changed pool,
and the final changed-line consumer must distinguish a failed producer from a
clean changed-line result. Cutover-owned tests, documentation, and installed
fixtures must describe the same current boundary; obsolete contracts should be
removed or rewritten rather than silently treated as implementation failures.

## Observed Facts

- `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_runtime_budget_universe.py` passed: 32 tests.
- The first `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --base-sha b2a88e808fdc53efaab10e264dab4f10ab52601d --refuse-unestablished` run took 200.2 seconds: 10,226 passed and 11 failed, then returned `status: no-verdict`, `reason: focused producer failed`.
- The 11 failures split across closeout call-count expectations, Goal Run lifecycle prose, issue/critique contract references, plugin-path wording, length-gate return semantics, stale ownership allowlist, and the installed handoff issue-source fixture.
- Reconciliation added the missing dependent contracts, excluded ephemeral `.charness/` output from durable closeout path collection, and kept shipped plugin documentation consumer-visible.
- The repaired broad standing run completed with `11,432 passed`; its consumer still refused the dirty parent range because 8 changed files had uncovered lines and 16 mutation-pool files had no standing-test mapping. No parent-range changed-line green was claimed.
- An isolated clean proof of the `#546` source change completed with `status: clean`, `consumer_returncode: 0`, `blocking: []`, and `unmapped_changed_pool_files: []`; the durable receipt is `charness-artifacts/goal-runs/724/observations/goal-run-546-changed-line-proof-20260827.md`.

## Reproduction

The first command remains the focused child check. The second command is the
historical reproduction of the initial cutover regression; after reconciliation
it reaches the standing producer, while the dirty parent range remains a
deliberate non-verdict. The isolated clean proof is recorded in the receipt
named above.

## Candidate Causes

- A transient pytest or environment failure.
- The producer selected an unrelated broad test population.
- The cutover changed ownership/return contracts without reconciling dependent
  tests, docs, allowlists, and installed-layout fixtures.
- Dirty-tree artifacts or source/plugin skew made the aggregate bundle invalid.

## Hypothesis

The cutover's dependent surfaces are stale or incompletely synchronized, so the
aggregate standing run fails before coverage can be consumed. If true, the
11 tests will either pass after their owning contract is reconciled or expose a
real cutover defect; the `#546` focused suite will remain green.
disconfirmer: run each named failure directly and compare its expectation with
`HEAD` and the current source/plugin/installed owner.

## Verification

Confirmed and repaired. Direct rerun reproduced the original 11 failures.
Source inspection separated intentional current changes such as post-close
readback (five backend calls), aggregate hard-length reporting (return 1), and
the compact issue-native `achieve` contract from real consumer-path defects in
the plugin prefix and installed handoff issue loader. The dependent test groups
then passed, the broad producer reached `PASS`, and the child-specific isolated
consumer rendered a clean verdict. The parent dirty-range refusal remains
correct and is not converted into a green claim.

## Root Cause

The ownership cutover was applied as a large source change, but its dependent
contract tests and fixtures were not updated in the same ownership pass. The
standing producer is correctly broad enough to detect this, while the narrow
child test is too local to detect it. The structural gap is missing aggregate
contract reconciliation at the cutover boundary, not a runtime-budget bug.

## Invariant Proof

- Invariant: when the focused producer emits a test result, the changed-line
  consumer must render coverage only if that result is successful; a failed
  prerequisite remains `no-verdict`.
- Producer Proof: the repaired broad producer passed its standing suite; the
  parent-range consumer's refusal and the isolated clean child receipt are both
  recorded above.
- Final-Consumer Proof: the isolated child producer emitted `status: clean` and
  `consumer_returncode: 0`; the parent dirty-range producer stayed blocked.
- Interface-Shape Sibling Scan: closeout carriers, lifecycle docs, plugin
  references, and installed handoff loaders all translate one owner contract to
  another; each is a dependent boundary, not a runtime-budget implementation.
- Non-Claims: no mutation coverage, provider-host, installed live session,
  remote CI, issue closure, push, release, or Cautilus result is claimed.

## Detection Gap

- `test_runtime_budget_universe.py` did not fire because its 32 tests are local
  to the selected child; the aggregate standing producer was the missing check.
- The initial source/plugin and docs defects were repaired and their dependent
  gates now pass. The parent-range changed-line refusal still fires correctly
  for dirty/unmapped/uncovered scope; it is not a defect to weaken.

## Sibling Search

- Mental model: a large ownership cutover updates the producer but leaves
  consumers testing the retired contract.
- same layer: `tests/quality_gates/test_closeout_authorization_ingress.py`,
  `test_python_length_interpretation.py`, and the ownership allowlist | decision:
  same class, fix now | proof: direct failing tests and source comparison.
- abstraction up: `docs/goal-lifecycle.md`, achieve coordination prose, and
  plugin-path references | decision: same class, fix now | proof: static contract
  read and failing assertions.
- cross-file: `tests/test_handoff_chunker_installed_layout.py` and
  `skills/public/handoff/scripts/chunked_routing_issue_backend.py` | decision:
  same class, fix now | proof: installed-layout reproduction.

## Seam Risk

- Interrupt ID: cutover-dependent-surface-drift-2026-08-27
- Risk Class: repeated-symptom, external-seam
- Seam: cutover owner -> dependent test/docs/package/installed consumer -> standing verdict
- Disproving Observation: all dependent tests pass, the broad producer reaches
  `PASS`, and the isolated child consumer emits a clean coverage verdict.
- What Local Reasoning Cannot Prove: live installed-host adoption or provider behavior.
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Review Note: the dependent surfaces were reconciled and the child-specific
  proof is durable. The user-authorized implementation path omits forced
  fresh-eye execution, so no fresh-eye result is claimed; the parent dirty-range
  consumer remains an explicit non-claim.
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-08-25-consumer-boundary-invariants.md

## Prevention

Reconcile dependent tests, docs, allowlists, plugin mirrors, and installed
fixtures as one cutover slice, preserving only safety boundaries that still own
the behavior. Then rerun the exact standing command and the changed-line
producer; keep `no-verdict` when any prerequisite fails.
