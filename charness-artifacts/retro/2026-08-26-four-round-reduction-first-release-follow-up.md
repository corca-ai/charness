# Four-round reduction-first release follow-up

Date: 2026-08-26
Mode: session

## Context

This retro covers the four bounded review rounds behind the reduction-first
verification change and the first release-preflight attempt. The user's
question was the right one: does the workflow challenge the verification scope
and the verifier itself, and does it explain why another fix keeps appearing?
The trustworthy evidence is the five critique packets, the committed repairs,
the release log, and the local gate outputs. This record does not claim that
every reviewer delivered or that a passing local check proves publication.

## Window

The review sequence ran from `7eaa46939` through `e500c4611`, with four bounded
rounds and a post-round local verification of the last repair. The release
attempt at `62abfd5f7` then exposed three independent closeout obligations: a
fixture still using the old artifact contract, three intentional duplication
families not yet classified, and five receipted lesson sessions without a
disposition. Those are workflow/fixture bookkeeping findings, not reasons to
expand the verification product into a global retry system.

## Evidence Summary

- Packet consumed: `charness-artifacts/retro/2026-08-26-four-round-reduction-first-release-follow-up-packet.md`.
- Review records: `charness-artifacts/critique/2026-08-26-reduction-first-verification-packet.md`, `2026-08-26-reduction-first-verification-r2-packet.md`, `reduction-first-verification-r3-packet.md`, and `reduction-first-verification-r4-packet.md`.
- R3 repaired a live CLI execution-context omission and a confirmed-state/same-proxy guard mismatch.
- R4 repaired a release renderer sentence that overstated what an inconclusive same-proxy probe established.
- The release preflight first ran 89 passing checks and 4 failing checks; the failures were recorded rather than rebranded as a green release.
- The release retry is justified only after changed subject/evidence identities: the fixture contract, intentional duplicate overlay, and lesson dispositions are being repaired before rerunning the broad gate.

## Waste

- The first release run discovered the new artifact contract through an old test fixture instead of through the fixture's focused test. That is a test-maintenance gap, not a reason to weaken the new validator.
- The four rounds were expensive because each repair changed the surface being judged: a scope record, a retry helper, a live release consumer, and a renderer claim. Treating all four as one unchanged question would have been a false stop condition.
- The real meta-waste was allowing release closeout state to lag the review state: old unclaimed lesson receipts and unclassified intentional duplicate families were not part of the first review packet. They surfaced at the broad gate, which is the correct boundary but a late one.
- Less-is-more held in the repair choice: no global retry ledger, attempt counter, or semantic oracle was added. The one-shot retry helper remains a caller-owned decision record; broader automation is deferred until an actual recurring consumer boundary proves it necessary.

## Critical Decisions

- **Scope before execution.** The critique contract now records the claim, changed consumers, minimum sufficient proof, deliberately omitted checks, verifier contract, failure classification, and evidence identities before a reviewer can treat the slice as complete.
- **Verifier skepticism without verifier sprawl.** A changed or suspect verifier is named explicitly, and release publication reconciles backend `verified` against a distinct-channel guard. The scope validator checks shape and retry-key binding; it does not pretend to prove the verifier's preimage or semantics.
- **Repair identity controls retry.** A retry is allowed only when the subject, verifier, input, or stable failure identity changes. Evidence identity alone does not authorize repeating the same work; the same tuple stops as no progress.
- **Two rounds, then an honest non-claim.** Proof-surface verdict logic owes a second bounded read of the repairs. Round-2 repairs are accepted as locally verified but fresh-eye-unreviewed under the cap; a timed-out reviewer is recorded as delivery failure, not as approval.

## North Star Alignment

- **Held:** “brief a capable judge; keep teeth only where a wrong answer escapes.” The new fields narrow the claim before the gate runs, and the retry policy refuses repeated work on an unchanged identity. The release renderer was repaired to say `unproven` when the distinct channel was not actually established.
- **Held:** irreversible release publication still requires a separate claims review and a distinct public/hosted readback; the local release helper's green is not treated as publication proof.
- **Mis-applied:** the first implementation trusted a fake CLI test to provide a callback that production resume context did not bind, and one renderer sentence trusted a probe label more than the guard's actual state. Both are “proof of the carrier mistaken for proof of the claim.”
- **Failure signature walked into:** a proof-surface repair carried the class it was meant to close. That is why R3 and R4 found new blockers even though earlier rounds were valid for their earlier inputs.

## Expert Counterfactuals

- **Engelbart:** treat the harness, lesson/evidence model, and tool path as one system. He would have included the release consumer and the test fixture in the initial contract packet, so the live-context omission and old fixture could not hide behind a narrow unit test.
- **Ousterhout:** ask whether a module can know the claim its wording asserts. The renderer could not infer distinctness from an inconclusive guard; its sentence should have been structurally bound to the established state, not repaired by more prose.
- **Gary Klein:** build the cheapest escape first. For this slice the cheapest escapes were a fake-only callback, a confirmed state with a degenerate same-proxy view, and a non-confirming probe rendered as if it had established distinctness. Those counterexamples explain the repeated fixes more than “the reviewers were too picky” does.

## Sibling Search

- Same proof surface: release state, renderer, and CLI resume paths now share the same explicit distinctness contract; the earlier mismatch was found by comparing their live consumer boundaries.
- Same workflow: critique, debug, and retro scaffolds remain parallel exported boundaries. The duplicate scan's three new families were classified intentional because extracting them would hide ownership and add coupling for no meaningful reduction.
- Transferable lesson: before widening a gate, ask what it can observe and what it cannot. A shape validator can bind identities; it cannot certify a digest preimage or a public network observation. Those claims stay with their owning consumer and evidence channel.

## Lesson Evaluation

Lesson evaluation: {"reason":"presentation-unproven","score_event_count":0,"session_id":"2026-08-26-release-review-followup","status":"not-evaluated"}

## Next Improvements

- workflow: lock the minimum proof and the deliberately omitted checks before each bounded review; re-open scope only when an identity or consumer changes.
- capability: add a consumer-owned semantic negative control only if a real recurring release retry boundary appears; do not build a global ledger to solve a hypothetical loop.
- memory: preserve the distinction between review finding, gate finding, and publication readback, and record timed-out reviewer delivery as a non-claim rather than an approval.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-26-four-round-reduction-first-release-follow-up.md
