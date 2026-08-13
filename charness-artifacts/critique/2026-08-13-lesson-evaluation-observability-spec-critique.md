# Lesson Evaluation Observability Spec Critique
Date: 2026-08-13

## Decision Under Review

Whether the lesson-evaluation observability contract is precise enough to govern implementation of a session-opening receipt, a required retro disposition, and a continuity report without claiming human exposure or rewarding score creation.

## Failure Angles

- Framing and denominator: the durable-retro denominator is honest, but the draft omitted a one-session-to-one-retro invariant. Reusing one valid session across multiple retros would make multiple work units appear disposed.
- Evidence semantics: the ledger has no event date, so an orphan rule over all declared sessions cannot distinguish historical, active, and overdue work. Orphan eligibility must come from the new opening record and the shared observed-date rule.
- Score coupling: zero score events cannot itself establish `no-effect`; that status must be an affirmative retro disposition. Score count is a consistency check, not the source of the evaluation claim.
- Receipt boundary: a command-side record can establish only that its stdout write and flush returned successfully for specified bytes. It cannot establish host delivery, display, reading, use, or benefit.
- Operational completeness: the draft needed an exact disposition grammar, a status/receipt/score truth table, stable violation identifiers, and fixtures for date disagreement, duplicate session reuse, receipt tampering, broken pipes, and human/JSON output.

## Counterweight Pass

- Act before ship: fix the 1:1 lifecycle, cohort/orphan predicate, affirmative `no-effect` semantics, truth table, byte-level receipt fields, and executable acceptance matrix before `impl` consumes the contract.
- Bundle anyway: name the ledger as session identity authority and describe the receipt as `stdout-write-and-flush-returned`, not presentation proof.
- Over-worry: do not add host transcript capture, automatic SessionStart writes, a ledger schema migration, or an all-chat denominator in this slice.
- Valid but defer: work units that never produce a retro remain outside this report; the output must call itself retro-artifact continuity rather than all-session coverage.

## Spec Contract Checks

- Fixed/Probe/Defer coherence: **fail pending repair**. The activation observer, 1:1 relation, orphan eligibility, and status truth table are implementation prerequisites and must move to Fixed Decisions. Sidecar durability remains a probe only if the fallback and decision point are explicit.
- Acceptance Check Coverage: **fail pending repair**. Success criteria need exact fixtures and outcomes for activation eve/day, filename/body disagreement, duplicate session references, status-by-receipt-by-score combinations, byte/render tampering, broken pipe, and compact human/JSON fields.
- Pre-Impl Action: update the spec with those fixed predicates and checks, then consume the repaired contract in `impl`. No implementation starts from the reviewed draft.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/spec/2026-08-13-lesson-evaluation-observability-contract.md#fixed-decisions | action: fix | note: enforce one session ID per one canonical retro and reject duplicate cross-retro reuse
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/validate_retro_artifact.py:_retro_observed_date | action: fix | note: fix the shared observed-date activation rule and scope orphan eligibility to new opening records
- F3 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/spec/2026-08-13-lesson-evaluation-observability-contract.md#entities-and-evidence-semantics | action: fix | note: make no-effect an affirmative disposition and use score count only as a consistency constraint
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/record_lesson_session.py:append_session | action: fix | note: define exact receipt fields and broken-pipe or write-failure behavior without claiming human exposure
- F5 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/spec/2026-08-13-lesson-evaluation-observability-contract.md#acceptance-checks | action: fix | note: add the complete status date identity tamper and human-or-JSON acceptance matrix
- F6 | bin: bundle-anyway | evidence: moderate | ref: scripts/lesson_ledger_lib.py:snapshot_sha256 | action: fix | note: keep ledger session identity authoritative and make receipts subordinate bindings
- F7 | bin: over-worry | evidence: strong | ref: charness-artifacts/spec/2026-08-13-lesson-evaluation-observability-contract.md#deferred-decisions | action: document | note: do not add host delivery observation automatic hooks or all-chat coverage
- F8 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/spec/2026-08-13-lesson-evaluation-observability-contract.md#denominator | action: defer | follow-up: deferred docs/handoff.md#discuss | note: work units with no durable retro need a later machine-local observer

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_turns=none
- Host exposure state: requested_fields_sent
- Application state: host accepted the requested fields but returned no applied-model metadata
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — three distinct fresh contexts returned framing, evidence-semantics, and counterweight findings; the parent-side reviewer boundary verified clean with no worktree, index, or HEAD drift.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-preimpl-packet.md
- Packet path: charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-preimpl-packet.json
- Packet SHA256: f5b52cb1519091764e6209c4ac98bca858093a9977921d8a67726d4a20619f70
- Identity SHA256: 4a2caa3082b143b74f1f5cfe34ca255e80dd728deca188049b370841a6465b8f

The current packet rebinds the living contract after implementation learning;
it is not a claim that the pre-implementation reviewers read later contract
updates already covered by the implementation critique and capped review.

## Boundary Ownership

- Producer: the repo-local lesson-session opener and the retro author produce bounded evidence records.
- Consumer: the repo-local continuity reporter reconciles those records for operators and future retros.
- Owning surface: the existing ledger owns session identity, the opening receipt owns command-write evidence, and the retro owns the human disposition; the reporter derives but does not rewrite them.
- Verdict: owned-correctly
