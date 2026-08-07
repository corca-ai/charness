# Issue #516 Mutation Regression Debug
Date: 2026-08-07

## Problem

The scheduled mutation workflow filed #516 after baseline pytest failed at
commit `79ea3447e186bb4f3f073d4d115c0eebb2deea1b`; the issue lists four failing
`test_publish_state_ledger.py` cases and reports that no mutants ran.

## Correct Behavior

Given a mutation run for a commit, the baseline must pass before mutation
sampling begins, and an automated regression issue must identify the exact
commit and failing tests. When the same baseline is re-run on a later commit,
the result must remain a separate observation rather than silently closing the
historical issue.

## Observed Facts

- Issue #516 records workflow run `31103691239`, SHA `79ea3447…`, and four
  baseline failures; it also records a missing StrykerJS report as collateral.
- The exact four nodeids from the issue pass at current `HEAD`:
  `pytest -q tests/quality_gates/test_publish_state_ledger.py::test_valid_ledger_reconciles_captured_snapshot tests/quality_gates/test_publish_state_ledger.py::test_human_and_json_cli_modes_share_verdict 'tests/quality_gates/test_publish_state_ledger.py::test_refusal_matrix_rejects_one_factor_drift[open-issue-kwargs8-issues_not_empty-manifest.remote_readback.open_issues.open_count]' tests/quality_gates/test_publish_state_ledger.py::test_surrounding_source_prose_does_not_change_claim_binding` — 4 passed.
- The complete ledger suite also passes: `pytest -q tests/quality_gates/test_publish_state_ledger.py` — 27 passed.
- The original run's failure log identifies `source_claim_mismatch` at
  `sources.handoff.claim`: `79ea3447…` had handoff `published_sha=7eed13ec…`
  while the goal/manifest and ledger expected `e7c3e1b3…`; commit `8d6ad5e7`
  later aligned the handoff claim.
- Quality Core run `31115253605` for `5df4fb61…` completed with core gates
  passing but changed-line mutation failing because this critique record's
  absolute packet path resolved outside the runner repository. The failing
  test was `test_live_corpus_critique_artifacts_pass_whole_tree_validation`.
- The packet field is now repo-relative; local whole-tree critique validation
  passes for 775 artifacts and the failing regression test passes. Post-repair
  Quality Core run `31117396157` for `9e2c390d…` passed both Core deterministic
  gates and changed-line mutation coverage.

## Reproduction

The reported failure does not reproduce at current `HEAD`; the exact failing
tests and their containing suite pass. Reproducing the original requires an
isolated checkout of `79ea3447…` with the runner's dependency state, which was
not performed in this slice.

## Candidate Causes

- A historical publish-state source claim, manifest, and handoff snapshot were
  temporarily out of sync at `79ea3447…` (confirmed by the original runner
  log and historical artifact comparison).
- The current remote mutation runner resolved a machine-local absolute packet
  path outside its checkout; the critique artifact, not the validator, owned
  the malformed value.
- A runner dependency or checkout-state difference may explain other historical
  details, but remains unproven and is not needed for this bounded fix.

## Hypothesis

- Confirmed: the historical baseline failed on the handoff source-claim
  mismatch, and the current remote failure was caused by the absolute packet
  locator | disconfirmer for additional environment claims: run the exact four
  tests from an isolated `79ea3447…` checkout.

## Verification

- The four reported tests and full ledger suite pass now; the original remote
  log plus historical comparison confirm the source-claim root cause without a
  local historical checkout. The current path repair passes local whole-tree
  validation and its focused regression test; post-repair remote proof passed in
  run `31117396157`.

## Root Cause

Confirmed bounded root cause: the historical run's handoff source claim was
bound to `7eed13ec…` while the goal/manifest ledger expected `e7c3e1b3…`, so
`publish_state_ledger.py` rejected `sources.handoff.claim` and the remaining
reported tests cascaded from that invalid baseline. A separate current runner
failure exposed a machine-local absolute packet path; making the field
repo-relative repairs that portability defect without changing validator
semantics.

## Invariant Proof

- Invariant: when the mutation baseline producer emits a failure for a SHA, the
  issue consumer must preserve that SHA and failing nodeids as a historical
  observation, while a later pass must be verified separately.
- Producer Proof: issue #516 and workflow run `31103691239` preserve the old
  SHA and four failing nodeids; the log names `source_claim_mismatch`.
- Final-Consumer Proof: current local tests and the whole-tree validator pass
  after the repo-relative path edit; the failed remote run names the exact
  consumer test. A new remote run is required before issue closeout.
- Interface-Shape Sibling Scan: the mutation mirror in
  `.github/workflows/quality-core.yml`, the scheduled workflow in
  `.github/workflows/mutation-tests.yml`, and the publish-state ledger tests
  share the baseline-verdict-to-operator-record shape; only local test proof
  is available for this slice.
- Non-Claims: no historical checkout, remote mutation completion, provider,
  cross-host, or Cautilus proof.

## Detection Gap

- Scheduled mutation baseline: it detected the old failure and preserved its
  SHA, but did not itself attach a current-SHA disposition | smallest change:
  require an exact failing-nodeid recheck plus SHA identity before closeout.
- Local critique validation: a machine-local absolute path passed locally but
  failed under the runner root | smallest change: store repo-relative packet
  paths and keep the containment check fail-closed.

## Sibling Search

- Mental model: a historical automated alert is a current bug until its commit
  identity and recheck are separated.
- same layer: `scripts/publish_state_ledger.py` and
  `tests/quality_gates/test_publish_state_ledger.py` | decision: same class,
  diagnostic-only for this slice | proof: local payload and 27 passing tests.
- abstraction up: `scripts/check_changed_line_mutation_coverage.py` and
  `scripts/run-quality.sh` also translate local verdicts into operator claims |
  decision: same class, diagnostic-only for this slice | proof: static scan only.
- cross-file: `scripts/publish_state_ledger.py` | decision: same class,
  diagnostic-only for this slice | proof: static scan only.

## Seam Risk

- Interrupt ID: mutation-516-historical-baseline-identity-and-portability
- Risk Class: external-seam
- Seam: scheduled GitHub Actions checkout -> durable claim/packet path -> local
  validator -> issue record
- Disproving Observation: Quality Core run `31117396157` at repaired commit
  `9e2c390d…` passed the whole-tree critique corpus and changed-line mutation
  baseline.
- What Local Reasoning Cannot Prove: dependency equivalence for the old runner
  or any provider/cross-host behavior.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/mutation-baseline-observation-identity.md

<!-- `Next Step` was authored as `issue-closeout-complete`, which is not in the
validator's enum (`impl` | `spec`), so `build_debug_seam_risk_index.py --check` refused
this artifact from `bb3ff353` onward and the pre-push gate stayed red across ten unpushed
commits. Corrected to `spec`, which is not a free choice: `Risk Class: external-seam` is a
FORCED risk class, and `risk_interrupt_lib.py` requires a forced interrupt to record
`Next Step: spec` (and `Critique Required: yes`, which this artifact already had).
Completion is carried by `Resolution: resolved`, the field the planner reads to demote a
closed investigation, so nothing about this record's meaning changed.

`Handoff Artifact` pointed at the resolution critique, which the same forced-interrupt rule
refuses: it must name a `charness-artifacts/spec/*.md`. The spec was owed and never
written, so it was written rather than the requirement being edited away; the critique is
still cited from the spec's Source line. -->


## Prevention

Keep mutation issues immutable as historical observations, bind any closeout to
the exact reported SHA, store packet locators repo-relatively, and require a
distinct current-SHA behavior recheck. #516's post-repair remote mutation
readback is now recorded in run `31117396157`.
