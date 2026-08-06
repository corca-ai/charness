# Slice 6 Publish-State Ledger Implementation Review

Date: 2026-08-06

## Decision Under Review

The implementation adds an offline validator and ledger that reconcile the
captured manifest, two source-owned claim blocks, and one published SHA. This
is a proof surface: a false green could be consumed by a later operator, so
implementation review required two bounded fresh-eye rounds after the first
round repaired verdict logic.

## Execution

- Fresh-eye pass: `scripts/publish_state_ledger.py` — round 1 found the
  whole-document source-binding and refusal-matrix gaps; round 2 read the
  repaired surface and found structured unreadable-manifest handling plus the
  source-invalid field spelling mismatch. Both parent boundaries were clean;
  round-2 repairs are accepted-unreviewed under the two-round cap.
- Round 1: one unnamed, one-shot, read-only bounded reviewer inspected the
  source/plugin validator, tests, ledger, contract, goal, and handoff. The
  boundary fingerprint was clean. Findings: whole-document source hashing
  crossed the mutable-document ownership boundary, and refusal coverage was
  incomplete.
- Repairs: source locators now hash canonical sorted compact JSON for the
  marked claim only; tests cover surrounding-prose drift, the refusal matrix,
  and refusal-mode parity.
- Round 2: a distinct unnamed, one-shot, read-only bounded reviewer read the
  repaired surface. The boundary fingerprint was clean. Findings: unreadable
  manifest handling needed a structured refusal, and source-claim-invalid
  fields needed to match the contract's broad `sources.<owner>` spelling.
- Final repairs: manifest read errors now return `manifest_missing` at
  `manifest.path`; source-invalid cases return `sources.<owner>`; a regression
  covers the unreadable-manifest path. Under the repo's two-round cap, these
  round-2 repairs are accepted-unreviewed; no third reviewer round is claimed.

## Failure Angles

- F1 | round 1 | source binding | fixed: whole-document source hashes
  invalidated unchanged claims when continuation prose changed; canonical
  claim hashing and a prose-drift fixture now preserve the owner boundary.
- F2 | round 1 | behavior coverage | fixed: tests now assert exact refusal
  codes and fields for the matrix, malformed/duplicate/shape cases, and a
  human/JSON refusal rendering.
- F3 | round 2 | manifest read errors | fixed: unreadable manifest reads are
  converted into the specified structured refusal instead of escaping as an
  OSError.
- F4 | round 2 | refusal field contract | fixed: malformed, missing, and
  duplicate source claim failures now use the exact broad field specified by
  the contract.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/publish_state_ledger.py | action: fix | note: bind the source locator to the canonical marked claim rather than the mutable Markdown document
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_publish_state_ledger.py | action: fix | note: cover exact refusal code and field combinations and refusal-mode parity
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/publish_state_ledger.py | action: fix | note: turn manifest read failures into manifest_missing at manifest.path
- F4 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/spec/2026-08-06-publish-state-ledger-contract.md | action: fix | note: align source-invalid field spelling with the explicit refusal matrix

## Verification Summary

- Focused behavior: `python3 -m pytest -q
  tests/quality_gates/test_publish_state_ledger.py` — 27 passed.
- Integrated neighboring behavior: premise preflight, slice manifest,
  final-bundle preflight, and ledger focused selection — 95 passed.
- Source/plugin parity: `cmp -s scripts/publish_state_ledger.py
  plugins/charness/scripts/publish_state_ledger.py` — passed.
- Human and JSON checked-in ledger modes both return the same captured target
  and `reconciled_captured_snapshot` verdict.

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded reviewer.
- Requested spawn fields: model `gpt-5.6-terra`, medium reasoning, priority,
  unnamed one-shot reviewers, fork context disabled.
- Host exposure state: requested_fields_sent
- Application state: host-confirmed that both rounds returned full findings;
  provider-side model application is not independently exposed.
- Delivery state: findings-received for both rounds.
- Round 1 parent window: `slice6-impl-round1`, boundary verify clean.
- Round 2 parent window: `slice6-impl-round2`, boundary verify clean.

## Fresh-Eye Satisfaction

`parent-delegated` — two distinct bounded reviewer contexts read the proof
surface, with clean parent boundary fingerprints. The required second round
read the repaired surface; its final repairs are explicitly accepted-unreviewed
under the cap rather than silently treated as reviewed.

## Reviewed Input Identity

- Packet path: `charness-artifacts/critique/2026-08-06-slice-6-publish-state-ledger-implementation-review-final-packet.json`
- Packet SHA256: `9eb44e4fb0dad48eaca8ec38187799fab49aaec86413c546a45fc3bdb7449d28`
- Identity SHA256: `296c3896e6a8647e3994572256d3c14ba41920d3a696a9bc53470bbe68b5d886`
- Round 1 prepared packet JSON SHA256:
  `ba9859fb0cadfa0b65f0a9cfae6a6075373c0964cb4556ed441584a6b0c98d84`
- Round 1 prepared identity SHA256:
  `31c32e26af8db640ec23c8fe7dd59e558ad3670b1b5f6be769bfefbe23622caf`
- Round 1 reviewer-reported packet Markdown SHA256:
  `79879455e8423b0e428b4f87cbf6684adb1014714dfe014154abe0fafb042f46`
- Round 2 packet JSON SHA256:
  `689b1164101f432d46de98c596401a559e662ce9f4a4697a79f932c05d38d544`
- Round 2 identity SHA256:
  `64810e2d65b27bdd29ca85a315116fec12865b5a7549779191072caa049a188a`
- Round 2 reviewer-reported packet Markdown SHA256:
  `f2c6a38a18cd2b9fe4931cbe3df129743a040f8b156cb0fe870c79ff38855a28`
- The final binding packet was regenerated after the round-2 repairs and local
  regression/closeout synchronization; it is current input identity evidence,
  not a claim that either reviewer re-read those final bytes.

## Boundary Ownership

- Producer: the captured manifest owns CI/issue facts; goal and handoff own
  their marked claims; the source validator/plugin mirror produce the same
  reconciliation behavior.
- Consumer: the repo-local ledger validator and later operator consume the
  source locators and return a captured verdict or structured refusal.
- Owning surface: source-bound offline publish-state reconciliation.
- Verdict: `owned-correctly`.
- External providers remain state owners; no current freshness or write is
  claimed.
