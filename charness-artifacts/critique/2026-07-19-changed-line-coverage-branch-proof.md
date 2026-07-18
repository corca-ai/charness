# Changed-Line Coverage Branch Proof Critique
Date: 2026-07-19

Packet Consumed: charness-artifacts/critique/changed-line-coverage-branch-proof-final-packet.md

## Decision Under Review

Close the final mutation-coverage gap with tests for the exact missing branches,
without changing production behavior or excluding files from the gate.

## Failure Angles

- Exercised the SQLite `since` predicate and invalid aggregate timestamp against
  a real database fixture.
- Exercised reviewed-input range/empty capture, filesystem failure, unavailable
  reconstruction, malformed packets, boundary paths, and missing fields.
- Exercised empty efficiency aggregation and release observer unavailable,
  schema failure, failed readback, and untracked-record commit paths.
- Limited mocking to filesystem-error and external-command seams; asserted the
  complete release add/commit/push sequence.

## Counterweight Pass

- No coverage exclusions, pragmas, threshold changes, or production branches
  were removed.
- The release command runner is an external seam; exact call-order assertions
  prevent a no-op mock from satisfying the test.
- The SQLite threshold changes a known thread count, so an omitted predicate
  cannot pass accidentally.
- Floor-Addition Restraint: no new gate; tests satisfy the existing changed-line
  consumer that caught the gap.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/test_reviewed_input_identity_failures.py | action: fix | note: security and stale-evidence failures now have direct branch proof
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_release_observer.py | action: fix | note: irreversible-boundary observer degradation and commit paths are exercised
- F3 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_retro_codex_session_audit.py | action: document | note: SQL-side filtering retains behavioral proof alongside its performance win

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_turns=none
- Host exposure state: requested_fields_sent
- Application state: host accepted caller-provided fields; model internals remain metadata-hidden

## Fresh-Eye Satisfaction

parent-delegated — the exact staged packet passed canonical verification, 55
declared tests passed in the reviewer context, the verdict was SHIP, and the
parent boundary fingerprint reported no worktree or index drift.

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/changed-line-coverage-branch-proof-final-packet.json
- Packet SHA256: 029b4855f3f89272659f4ff42af21671cfe2cfc363a34f6e6502198a15468e61
- Identity SHA256: 3c4b5c29c419c3caf51bb00217b848875301298fee9e7f621e452b2f1ddcd92d

## Boundary Ownership

- Producer: branch-specific tests for changed campaign code
- Consumer: changed-line mutation-coverage gate
- Owning surface: repository quality proof
- Verdict: owned-correctly — the tests execute the missing behavior and the
  gate remains unchanged.

## Verdict

SHIP. The previously uncovered branches now have behavioral tests, pending the
fresh cumulative coverage run that remains the authoritative final proof.
