# Issue 616 Applied Lifecycle Resolution Critique
Date: 2026-08-13

## Decision Under Review

Whether lesson archive/resurrection and contract graduation/retirement can become
explicit replayed lifecycles without allowing scores, generated projections, or
retention observations to authorize or silently reconstruct a transition.

## Execution

Target: code critique. Round 1 used Jackson/Weinberg ownership and
Gawande/Raskin operator angles plus a separate counterweight. The ownership angle
approved the replay-versus-live-doc separation; the operator angle found one raw
`KeyError` escape. That escape was repaired and the mandatory round 2 read the
full repaired proof surface. Every used reviewer-boundary fingerprint verified
clean. An initial raw-file-hash staleness claim was withdrawn after the canonical
`sha256-v2` verifier returned `current`; it did not drive a repair.

## Failure Angles

- Ownership: are append-only events authoritative while materialized state and
  live H2 inventory remain independently checked projections?
- Problem framing: does the slice complete the missing lifecycle, rather than
  invent score thresholds or let quality evidence authorize mutation?
- Operator recovery: do migrations, invalid identities, dry runs, reviewed
  applications, and refusal messages preserve bytes and explain the next move?
- Counterweight: are Markdown rendering, generic dry-run expansion, distributed
  locking, and automated decision-text interpretation required here?

## Findings

- Lesson ledger v4 replays explicit archive/resurrect events into state while
  preserving score/session history and a fixed active budget of 50.
- Preview policy v2 selects its first nine slots only from active lessons and its
  archive slot only from archived lessons; absence leaves the slot empty.
- Contract register v2 freezes seed units and budget, replays reviewed membership
  transitions, then separately requires the projection to equal live H2 docs.
- Round 1 reproduced an unknown lesson ID reaching `_materialize` before domain
  validation and printing a raw `KeyError`. The writer now refuses the unseeded ID
  explicitly; its CLI regression asserts exit 1, exact stderr, and byte equality.
- Round 2 found no sibling projection-before-validation or raw-refusal escape
  across score/session, citation/proposal, or contract-transition writers. It
  required no further repair.

## Counterweight Pass

- Act Before Ship: repair the unknown-lesson raw refusal and prove unchanged
  bytes through the real CLI; completed before round 2.
- Bundle Anyway: keep decision-reference semantics explicitly judgment-owned and
  non-authorizing in the operator/quality records; completed.
- Over-Worry: do not make event replay render Markdown, add a generic lifecycle
  dry run, or repair the withdrawn raw-hash staleness claim.
- Valid but Defer: multi-host serialization needs a concrete distributed storage
  contract before it can be designed or claimed.

## Deliberately Not Doing

This slice does not invent score or staleness thresholds, auto-graduate lessons,
map gate catches to contract units, parse approval prose, rewrite contract docs,
or claim distributed transactions. It does not enable PLR2004; that diagnostic
inventory belongs to a separate production-code baseline/ratchet decision.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/record_lesson_lifecycle.py | action: fix | note: unknown lesson identities now receive a domain refusal before projection materialization
- F2 | bin: bundle-anyway | evidence: strong | ref: docs/development.md | action: fix | note: evidence and retention reporting remain explicitly non-authorizing
- F3 | bin: over-worry | evidence: strong | ref: scripts/contract_register_lib.py | action: defer | note: replay correctly compares with rather than renders the Markdown contract
- F4 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/quality/2026-08-13-issue-616-applied-lifecycle.md | action: defer | note: multi-host serialization has no supported storage or coordination owner

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `fork_turns=none`, `model=gpt-5.6-terra`, `reasoning_effort=medium`, `service_tier=priority`.
- Host exposure state: requested_fields_sent
- Application state: the host accepted the fields and delivered findings; provider-side application metadata was not exposed.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated. Two round-1 angles, a separate counterweight, and one repaired-
surface round-2 reviewer delivered findings. Parent-side fingerprints for the
three used windows verified `clean`; round 2 required no repair.

## Fresh-Eye Passes

Fresh-eye pass: scripts/apply_contract_transition.py — round 2 found no raw-refusal or projection-before-validation bypass.
Fresh-eye pass: scripts/migrate_contract_register.py — round 2 found no degenerate success or write-before-validation path.
Fresh-eye pass: scripts/migrate_lesson_lifecycle.py — round 2 found no degenerate success or write-before-validation path.
Fresh-eye pass: scripts/record_contract_citation.py — round 2 found candidate validation before write and no sibling raw refusal.
Fresh-eye pass: scripts/record_contract_graduation_proposal.py — round 2 found candidate validation before write and no sibling raw refusal.
Fresh-eye pass: scripts/record_lesson_lifecycle.py — round 2 approved the explicit unknown-ID refusal and unchanged-byte proof.
Fresh-eye pass: scripts/render_contract_retention_review.py — non-authorizing verdict and unavailable catch/staleness states remain explicit.
Fresh-eye pass: scripts/contract_unit_inventory_lib.py — accepted-unreviewed mechanical ownership split after the two-round cap; H2 discovery logic is unchanged from the reviewed register surface.

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/2026-08-13-issue-616-round2-packet.md`
- Packet path: `charness-artifacts/critique/2026-08-13-issue-616-final-binding-packet.json`
- Packet SHA256: `209567ce5adc7cf4e66c06c999d97edb7e00f59c0a6315bc6bcb78aace114daa`
- Identity SHA256: `d2e5df80f8e955453e5b42ee3f8d0f84d62f018af9962fc2b3132a7262197649`
- Review-time packet path: `charness-artifacts/critique/2026-08-13-issue-616-round2-packet.json`
- Review-time Packet SHA256: `10463d7cdde8c3f10002d9f617a8620f7535a2bdfb216dd234a97c1ac518ad25`
- Review-time Identity SHA256: `b74aea2207210faac829c019bbdb9397a4f749293782a479daa50f23731e8ac7`

The final packet binds the accepted-unreviewed mechanical module/test ownership
split and truth-surface refresh after the two-round cap. It does not claim that a
third reviewer read those edits.

## Boundary Ownership

- Producer: operator commands append reviewed lifecycle, proposal, citation, and
  membership events after validating a complete candidate.
- Consumer: preview and retention reports read validated projections; operators
  and quality reviewers decide whether evidence warrants the next event.
- Owning surface: ledger/register libraries own replay and deterministic refusal;
  Markdown contract docs own the human-authored binding text.
- Verdict: owned-correctly

## Next Move

Run the broad related gates and artifact validators, bind the issue closeout to a
local direct commit, and leave push/GitHub closure unclaimed.
