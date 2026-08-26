# Debug Review
Date: 2026-08-27

## Problem

Issue #693's premise was true: `record_round_findings.py` accepted arbitrary
UTF-8 stdin or `--findings-file` bytes and wrote them as reviewer findings.
The record carried a boundary snapshot digest but no reviewer execution,
producer, packet, or reviewed-input identity, so a same-context substitution
could look like delivered review evidence.

## Correct Behavior

Round recording accepts only a provenance-valid delivered worker report. The
report/receipt/result/ledger chain must join on attempt, producer, execution
mode, packet, reviewed input, parent receipt, boundary, output, and findings
identity. The exact typed result is the findings carrier. A delivered typed
`block` or `defer` is recordable; it is not approval.

## Observed Facts

- The old writer exposed `--findings-file` and stdin and only hashed those raw
  bytes.
- `reviewer_worker_report.py` already retains `producer_run_id` and binding;
  `reviewer_worker_carrier_support.py` already joins receipt/result/ledger.
- The delivery helper required `pass`, which is correct for approval but too
  strict for recording a typed finding.
- RCA ledger entry `reviewer-findings-carrier-mismatch` says future recording
  must consume typed `result.json`, with `report.yaml` as delivery evidence.

## Reproduction

The old behavior is reproduced by the pre-change focused test that supplied a
plain findings file and received a successful round record. The new executable
fixture invokes the same final consumer with `--findings-file`; it exits with
an argument error and creates no record. A copied, chain-valid historical
`block` result is accepted and its exact result digest is retained.

## Candidate Causes

- The round writer owned a second raw findings input contract beside the worker
  delivery contract.
- The approval-only carrier validator was not reusable for collection because
  `require_pass` was hard-coded.
- Tests asserted boundary and content hashes but never required producer or
  reviewed-input identity.

## Hypothesis

The missing identity is caused by bypassing the shared delivery-chain owner;
requiring its typed report and relaxing only the semantic pass predicate for
collection will make raw same-context input fail while preserving block/defer
evidence. disconfirmer: run the focused raw-rejection, typed-block acceptance,
boundary-mismatch, overwrite, and existing approval tests.

## Verification

Confirmed. The focused round suite is green, the raw input test refuses the
legacy flag, the typed block fixture records exact `result.json` bytes, and the
existing worker-report suite remains green with approval still pass-only.

## Root Cause

The writer treated “bytes returned to the parent” as equivalent to “findings
delivered by a distinct reviewer execution.” That collapsed delivery evidence,
semantic result, and approval into one unowned text parameter. The fix makes the
worker report the only input boundary, reuses the existing receipt/result/ledger
join, and stores result bytes rather than report prose as findings.

## Invariant Proof

- Invariant: a round record may claim delivered review evidence only when a
  typed result and its producer/delivery identities join to the exact boundary.
- Producer Proof: `reviewer_worker_report.py` emits producer run, output/receipt
  binding, attempt, packet, input, parent, and boundary provenance.
- Final-Consumer Proof: `validate_delivered_worker_report` checks the complete
  receipt/result/ledger chain with `require_pass=False`; the recorder then
  re-hashes the result before writing.
- Interface-Shape Sibling Scan: `reviewer_worker_carrier.py` keeps
  `approval_eligible` pass-only while the round writer consumes
  `collection_ready` evidence.
- Non-Claims: local files do not host-attest that a producer process was human
  or physically distinct; only the declared Charness delivery boundary is
  proven.

## Detection Gap

`tests/test_critique_round_findings.py` previously covered snapshot identity,
raw content digest, overwrite, and malformed snapshots, but no test supplied a
worker report or rejected a same-context findings file. The smallest detector
is a required `--worker-report` argument plus one accepted typed-block fixture
and one legacy-flag refusal.

## Sibling Search

- Mental model: durable review evidence flows producer -> receipt -> typed
  result -> delivery ledger -> final consumer.
- same-layer axis: `skills/shared/scripts/reviewer_worker_carrier_support.py` |
  decision: reuse its join and make `pass` optional only for collection | proof:
  existing approval suite plus typed block fixture.
- abstraction-up axis: `skills/shared/scripts/reviewer_worker_report.py` |
  decision: retain its producer identity in the round record | proof: positive
  record assertions.
- cross-file: `skills/shared/scripts/reviewer_worker_report.py`; it is the
  producer-side report owner outside the subject writer.

## Seam Risk

- Interrupt ID: debug-plan-693
- Risk Class: contract-freeze-risk
- Seam: the repository can bind files and producer identifiers but cannot
  independently attest the host's process identity.
- Disproving Observation: a valid report/receipt/ledger join with a typed result
  still permits a raw same-context path; the new negative fixture must fail.
- What Local Reasoning Cannot Prove: human authorship, host isolation, or live
  provider freshness beyond producer-attested fields.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: no
- Next Step: impl
- Handoff Artifact: none

## Prevention

Keep one owner for delivery-chain validation and one explicit distinction:
`collection_ready` means typed findings arrived; `approval_eligible` means the
semantic verdict is pass. Any future round recorder must consume the typed
result through that owner and must retain the producer/input identities rather
than accepting free-form parent text.

## Evidence Disposition

- Report Identity: issue:693#sha256:7d7ed77c949eacec9bf09e00e48b572215d04920c59ace613180f8e15348ecdc
- Reported Findings: 1
- Dispositioned Findings: DBG-693-F1
- Missing Findings: none
- Evidence Digest: sha256:e5398968088760ead7a2c99a02d015b36aa90698e92c555e1bd19d3fed04b6de
- Report Source: charness-artifacts/goal-runs/724/bodies/backlog-693.md
- Report Source SHA256: 7d7ed77c949eacec9bf09e00e48b572215d04920c59ace613180f8e15348ecdc

## Adversarial Verification

- Finding: DBG-693-F1 | source: skills/public/critique/scripts/record_round_findings.py | expected: raw same-context findings are rejected while a bound typed worker result is accepted | stimulus: invoke the recorder with --findings-file instead of --worker-report | disposition: reproduced | observed: the CLI exits with argument error and writes no round record; the paired typed-worker test passes | proof: executable fixture | handoff: charness-artifacts/impl/2026-08-27-issue-693-reviewer-provenance.md | next move: keep --worker-report as the only findings input | receipt: charness-artifacts/debug/receipts/issue-693-raw-findings-rejected.json | receipt sha256: f9512275d982e81e409ee71f9ced632ec5941dbc26d038b45938b8dbf42ab503
