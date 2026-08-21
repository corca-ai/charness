# Critique Round Findings

- Round: 2
- Recorded date: 2026-08-21
- Boundary window id: `r2-semantic-candidate-provider-schema-round-2b`
- Boundary snapshot: `.charness/reviewer-boundary/2026-08-21-r2-semantic-candidate-provider-schema-round-2b.json`
- Boundary snapshot SHA-256: `a30bac5fe94e2d4cbb4e4375bc0bcca59b952743fcfc542edee01952d10d0e8c`
- Findings SHA-256: `817e496c94289e88a8b70f60a7949c145ab23c112e7f5fcf31118bc25ea1c00f`

## Findings Returned

# Round-2 bounded fresh-eye findings

Boundary verification: `boundary-drift` (not clean). The verifier reported all
worker runtime files under `.charness/reviewer-round-2/r2b-*` as
`untracked-added`; therefore this round's tree-integrity rail is quarantined.
The runtime-output ignore gap is recorded at
`charness-artifacts/debug/2026-08-21-reviewer-boundary-runtime-output-unignored.md`.

All three workers nevertheless delivered typed, fresh, hash-matching results
through the combined report and reached `findings-received`. Their reviewer
verdicts were all `block`; `approval_eligible` is delivery permission, not a
review verdict.

## semantic-mode-and-authorization — block

- `SEM-MODE-001` blocker: the report builder hardcodes/emits
  `file-backed-worker` instead of enforcing and faithfully carrying the actual
  requested mode; typed-labelled inputs can reach the file-backed report path.
- `SEM-MODE-002` major: caller flags can override adapter-selected mode/backend.
- `SEM-PROOF-003` blocker: `worker-delivered` remains an artifact-level claim
  unless bound to a real matching combined report carrier.

Repair: bind expected/attempt/receipt mode and backend, make adapter selection
authoritative, and add cross-mode/conflicting-override/nonexistent-report
negative tests. Round-2 repairs are accepted-unreviewed under the two-round cap.

## consumer-provenance-and-verdict — block

- `CPV-R2-REPORT-CARRIER` blocker: worker-delivered can be asserted without a
  real matching report carrier.
- `CPV-R2-RESULT-IDENTITY` blocker: result packet/input identities are not bound
  to invocation.
- `CPV-R2-FOREIGN-RECEIPT` blocker: a foreign receipt can bypass parent/run
  binding when worker fields match.
- `CPV-R2-LEDGER-REPLAY` blocker: forged state-valid history/findings identity
  can satisfy approval.
- `CPV-R2-LEDGER-RACE` major: unlocked read-modify-write can overwrite a
  timeout with `findings-received`.

Repair: require a report carrier and result identity joins, carry and verify
parent receipt identity, validate event history and serialize ledger updates.

## portability-and-operational-boundaries — block

- `PORT-001` blocker: the packet was byte-correct but stale against the current
  candidate; its target was `da35...`, current HEAD was `680be...`.
- `PORT-002` blocker: plugin-mirror runner path resolution breaks in installed
  layout.
- `PORT-003` blocker: schema validation does not bind result packet/input
  identities to the actual packet/run.
- `PORT-004` high: stale pre-existing receipts can remain approval-eligible
  after a worker refusal.
- `PORT-005` high: input files are absent from collision checks.
- `PORT-006` high: timeout does not bound every runner/cleanup wait.
- `PORT-007` high: documented operator sequence cannot produce delivery.
- `PORT-008` medium: ledger read-modify-write is unlocked.
- `PORT-009` medium: explicit zero timeout falls back to the adapter default.

Repair: regenerate a current-bound packet, fix plugin-root resolution, bind
semantic identities, reject stale/colliding inputs and receipts, bound cleanup,
repair the operator sequence, serialize ledger writes, and preserve zero as an
explicit timeout.

Disposition: no fresh-eye approval, release approval, or clean boundary claim.
