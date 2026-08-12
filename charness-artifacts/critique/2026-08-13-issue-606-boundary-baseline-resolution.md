# Issue 606 Boundary-Baseline Resolution Critique
Date: 2026-08-13

## Decision Under Review

Give the boundary-bypass no-increase ratchet a guarded canonical baseline writer
and reject stored state whose writer-owned verdict inputs have drifted.

## Failure Angles

- A hand-edited count, key set, or metadata field could change a future ratchet
  verdict while the loader still rendered green.
- A `regenerate` instruction without an executable writer invites unreviewed
  JSON editing or acceptance of an unintended whole-inventory delta.
- A malformed or non-file baseline path must produce the CLI's structured
  refusal contract, not a traceback.

## Counterweight Pass

- The SHA-256 value is an accidental-edit integrity tripwire, not a signature;
  signed policy or key management is not justified by this issue.
- Historical no-increase baselines may be larger than a reduced current
  inventory, so load-time equality with today's inventory would be a false
  failure. The writer-integrity check preserves that legitimate decrease.
- Every changed existing baseline requires confirmation; a separate safe-delta
  threshold would add policy without evidence.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: scripts/boundary_bypass_ratchet_lib.py | action: fix | note: Canonical writer integrity covers all persisted verdict inputs while preserving historical no-increase decreases.
- F2 | bin: bundle-anyway | evidence: strong | ref: scripts/check_boundary_bypass_ratchet.py | action: fix | note: Guarded writer reports metadata, summaries, and candidate-key delta before any changed baseline can be accepted.
- F3 | bin: bundle-anyway | evidence: strong | ref: tests/test_boundary_bypass_ratchet.py | action: fix | note: Regression tests cover every enforced count, other verdict inputs, non-object JSON, malformed JSON, and directory target refusals.
- F4 | bin: over-worry | evidence: strong | ref: scripts/boundary_bypass_ratchet_lib.py | action: defer | note: A deliberate digest recomputation is outside the stated accidental-edit threat model.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye reviewer.
- Requested spawn fields: task_name `issue606_r1` and `issue606_r2`; read-only scope; no model override.
- Host exposure state: metadata-hidden
- Application state: n/a — this host returns reviewer findings but exposes no typed reviewer-tier confirmation.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated; round 1 identified non-object JSON traceback and non-reviewable confirmation delta, both repaired. Round 2 identified omitted verdict metadata and directory-target traceback; both repairs are accepted-unreviewed under the two-round verdict-logic cap.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-12-155204-packet.md
- Packet path: charness-artifacts/critique/2026-08-12-155204-packet.json
- Packet SHA256: 7dbb5586295b0cb533102f56e4f4570d0a4a4436e6aefd46b2a59d8f11290f2b
- Identity SHA256: 82332cbdf4f99159dfb2e19381aac4bb550c1bef9c0e404da9e01be1dccbe2f9

## Boundary Ownership

- Producer: `build_baseline()` derives canonical ratchet state from inventory and exemptions.
- Consumer: `check_boundary_bypass_ratchet.py` loads state and emits the final no-increase verdict.
- Owning surface: boundary-bypass ratchet writer/loader seam.
- Verdict: owned-correctly
