# Lesson Evaluation Observability Implementation Critique
Date: 2026-08-13

## Decision Under Review

Whether the new lesson-session opener, retro disposition floor, continuity
reporter, planner/adapter wiring, quality gate, and checked-in plugin exports can
land without reproducing a false-clean verdict or forcing Charness policy into
unrelated public-skill consumers.

## Failure Angles

- Round 1 evidence semantics tested partial stdout writes, flush and receipt
  failures, receipt mutation, unsafe identifiers, session reuse, foreign score
  citations, invalid-disposition denominator preservation, and overdue receipts.
- Round 1 operator review tested whether the continuity report was merely a
  planner reminder or a real Charness quality gate, and whether canonical and
  exported surfaces stayed aligned.
- Round 1 counterweight tested whether `no-effect` was inferred from score zero,
  whether valid receipt plus uncertain presentation had an honest state, and
  whether the new hard floor had durable recurrence evidence.
- Round 2 read the repaired full verdict surface and asked whether the fix
  reproduced the class it fixed. One reviewer accepted the verdict logic; the
  ownership reviewer found the public scaffold/reference still hard-coded the
  Charness grammar.

## Findings And Repairs

- Short writes could receipt intended bytes after emitting only a prefix. The
  opener now loops until every byte is written, rejects invalid progress, and
  receipts only after flush; focused tests cover short write, broken pipe, flush
  failure, receipt replacement failure, and exact byte binding.
- Unsafe session IDs were rejected only after ledger mutation. Validation now
  precedes declaration and the regression asserts no filesystem mutation.
- A valid command receipt plus uncertain human presentation had no truthful
  state. `presentation-unproven` now requires a valid receipt, stays incomplete,
  and is distinct from `emission-unproven`.
- The receipt hash was overclaimed as tamper evidence. The contract now calls it
  accidental/incomplete-edit detection only, with no authenticity claim.
- Planner routing alone did not prevent ledger/receipt mismatches from escaping.
  The continuity reporter is now a named Charness quality gate with seeded
  runner support.
- The hard-floor rationale now cites the durable 2026-08-13 session audit that
  recorded non-operation across the #615 slice; grandfathering remains next-day
  and form-only.
- Round 2 found Charness grammar in the public scaffold and reference. The capped
  repair adds a generic adapter `artifact_sections` seam, keeps the public
  reference evaluator-generic, and moves exact Charness form/command ownership
  into `.agents/retro-adapter.yaml` plus `docs/development.md`. This repair is
  accepted-unreviewed under the mandatory two-round cap; no third round is
  claimed.

## Counterweight Pass

- Act Before Ship: partial-write false receipts, late unsafe-ID refusal,
  presentation-state absence, missing quality registration, and public/private
  ownership inversion were concrete blockers and are repaired.
- Bundle Anyway: explanatory prose is allowed beside exactly one machine line;
  receipt identity remains subordinate to the ledger snapshot.
- Over-Worry: cryptographic authenticity, host delivery/read confirmation,
  automatic SessionStart writes, and an all-chat denominator are not added.
- Valid but Defer: work that never produces a durable retro needs a future
  machine-local observer before it can enter this denominator honestly.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/open_lesson_session.py | action: fix | note: complete short writes and reject unsafe IDs before declaration
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/lesson_evaluation_continuity_lib.py | action: fix | note: add presentation-unproven and keep no-effect affirmative rather than score-inferred
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh | action: fix | note: register continuity reconciliation as a Charness quality gate
- F4 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/retro/2026-08-13-session-retro.md:242 | action: fix | note: bind the new form-only floor to the durable non-operation observation
- F5 | bin: act-before-ship | evidence: strong | ref: round-2 ownership review | action: fix | note: move Charness grammar from public assets to adapter-owned sections and repo development docs; accepted-unreviewed under cap
- F6 | bin: bundle-anyway | evidence: moderate | ref: scripts/lesson_evaluation_continuity_lib.py:parse_disposition | action: fix | note: permit explanation while retaining exactly one machine line
- F7 | bin: over-worry | evidence: strong | ref: charness-artifacts/spec/2026-08-13-lesson-evaluation-observability-contract.md#non-goals | action: document | note: no crypto host-delivery or all-chat observer in this slice
- F8 | bin: valid-but-defer | evidence: strong | ref: docs/handoff.md#discuss | action: defer | follow-up: deferred docs/handoff.md#discuss | note: host work without durable retros remains outside the measured cohort

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_turns=none
- Host exposure state: requested_fields_sent
- Application state: host accepted the requested fields and delivered findings; provider-side applied-model metadata was not exposed
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — three distinct round-1 reviewers and two distinct round-2
reviewers returned findings. Parent-side fingerprints for windows
`lesson-eval-code-r1` and `lesson-eval-code-r2` both returned `verdict: clean`
with no worktree, index, or HEAD drift. The round-2 ownership repair is explicitly
accepted-unreviewed under the two-round stopping rule.

## Reviewed Input Identity

- Packet consumed: review-time round-1 and round-2 markdown packets; the final JSON below is the current post-round-2 repair binding
- Packet path: charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-code-round2-packet.json
- Packet SHA256: 35024de2e3aa139777c00372af9ebc14da6f079398866a00034ed922a64f418c
- Identity SHA256: a426820c53ee1309a2071ee319daae82a216eaf3bab7f5d9d566c4e1bd1dbfdf
- Review-time round-1 binding: packet `11620427c5e48b0abca757fb588c017e0a0bd06ae7aaa00b0e614d8118fe206d`, identity `bc8c0d68c91fdd6c6509ef7aa86a366d03fd9caaace603d3712a4cf19c9d3b1f`.
- Review-time round-2 binding: packet `59f62c3385dcbe0618a7161d9f3fa119b767e5600a6c1981d274eef17c6798f1`, identity `ededf82f34517e2a5e029e228263cccac72a7231b3674910624b071337537ff0`.

The current packet binds the accepted-unreviewed round-2 repair bytes. It is not
a claim that reviewers read edits made after their capped round.

## Boundary Ownership

- Producer: the schema-v3 ledger produces immutable session identity; the start command produces bounded stdout-write evidence; the retro author produces the human evaluation disposition.
- Consumer: the continuity reporter derives the cohort verdict, and Charness quality/retro operators consume it.
- Owning surface: the public retro package owns generic adapter routing; the Charness adapter and development guide own the exact evaluator form; checked-in plugin files are generated projections.
- Verdict: moved-to-owner
