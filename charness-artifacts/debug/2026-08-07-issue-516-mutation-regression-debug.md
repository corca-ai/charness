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
- No historical-checkout reproduction or current remote mutation conclusion is
  claimed. Quality Core run `31115253605` for `5df4fb61…` had core gates pass,
  while its changed-line mutation job was still running at this record.

## Reproduction

The reported failure does not reproduce at current `HEAD`; the exact failing
tests and their containing suite pass. Reproducing the original requires an
isolated checkout of `79ea3447…` with the runner's dependency state, which was
not performed in this slice.

## Candidate Causes

- A historical publish-state source claim, manifest, and handoff snapshot were
  temporarily out of sync at `79ea3447…`.
- The scheduled runner observed a release-baton transition before all durable
  state surfaces had synchronized, so the ledger tests correctly refused the
  captured snapshot.
- A runner dependency or checkout-state difference caused the scheduled
  baseline to see a different artifact set from the current local checkout.

## Hypothesis

- Candidate: the failure was a historical source-claim/manifest mismatch that
  later reconciliation repaired | disconfirmer: run the exact four tests from
  an isolated `79ea3447…` checkout and compare the ledger's bound source fields.

## Verification

- Current-state disconfirmer passed: the four reported tests and the full ledger
  suite pass now. The historical hypothesis remains still-candidate because the
  original SHA was not checked out in an isolated environment.

## Root Cause

Not yet confirmed. The strongest bounded finding is a stale historical
regression: the issue's exact failing tests pass at current `HEAD`, but the
producer/runner-to-issue history has not been replayed at the reported SHA.

## Invariant Proof

- Invariant: when the mutation baseline producer emits a failure for a SHA, the
  issue consumer must preserve that SHA and failing nodeids as a historical
  observation, while a later pass must be verified separately.
- Producer Proof: issue #516 and workflow run `31103691239` preserve the old
  SHA and four failing nodeids.
- Final-Consumer Proof: the current issue remains OPEN; no closeout or automatic
  stale-issue transition was claimed.
- Interface-Shape Sibling Scan: the mutation mirror in
  `.github/workflows/quality-core.yml`, the scheduled workflow in
  `.github/workflows/mutation-tests.yml`, and the publish-state ledger tests
  share the baseline-verdict-to-operator-record shape; only local test proof
  is available for this slice.
- Non-Claims: no historical checkout, remote mutation completion, provider,
  cross-host, or Cautilus proof.

## Detection Gap

- Scheduled mutation baseline: it detected the old failure, but no current-SHA
  recheck or stale-issue disposition was attached | smallest change: require an
  exact failing-nodeid recheck plus SHA identity before proposing closeout.
- Local ledger suite: it now fires for current state, but cannot reconstruct a
  prior runner environment | smallest change: retain the runner SHA and enough
  artifact identity to replay the baseline.

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

- Interrupt ID: mutation-516-historical-baseline-identity
- Risk Class: external-seam
- Seam: scheduled GitHub Actions checkout -> local baseline -> issue record
- Disproving Observation: an isolated run at the recorded SHA reproduces or
  disproves the four failures with matching ledger inputs.
- What Local Reasoning Cannot Prove: historical runner state and current remote
  mutation completion.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: open
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: docs/handoff.md — keep #516 open until the historical SHA
  replay or a delegated causal review supplies the missing evidence.

## Prevention

Keep mutation issues immutable as historical observations, bind any closeout to
the exact reported SHA, and require a distinct current-SHA behavior recheck.
Do not close #516 from the present local green alone; the host has no exposed
Agent/Workflow spawn tool for the required causal fresh-eye reviewer.
