# Final Release Boundary Retro — R3 Delivery Review
Date: 2026-08-21
Goal: charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md

## Context

This retro closes the receipted R3 delivery/provenance review session. It
records the structural repair of process-success versus delivered behavior,
and the boundary discipline used when the bounded reviewer reports themselves
returned blocks rather than approval.

## Window

The window spans the second bounded review, delivery-status repair, source/plugin
parity proof, and the preparation of exact release-boundary evidence.

## Evidence Summary

- Four file-backed workers returned typed `block` findings; no fresh-eye PASS was
  claimed and the two-round cap remains consumed.
- The root CLI now fails closed for host-delivery failure, preserves skipped and
  unavailable states, and requires same-version content readback before cache
  success claims.
- Source/plugin parity, focused tests, changed-line proof, and the release gate
  passed before the release candidate was versioned.

## Waste

- recurrence-class: goal-closeout-evidence-binding — release publication and
  post-publish readback completed before the goal/handoff documents were
  reconciled to the new truth. The structural repair is to bind closeout
  artifacts after external readback and before changing terminal status.
- recurrence-class: proof-surface-message-drift — unsupported command forms were
  encountered during release preparation. They were kept as rejected evidence,
  while only owned help/inventory-derived commands were counted as checks.

## Critical Decisions

- Treat every worker `block` as repair input and preserve the lack of approval;
  do not substitute same-agent review or a third bounded round.
- Make the root status and exit code carry delivery provenance, not merely child
  process success or media output.
- Complete the release externally, then reconcile the durable goal/handoff and
  issue disposition surfaces before closeout.

## North Star Alignment

The north star held at the irreversible boundary because the release's public
and install observers were distinct from the producer. It was mis-applied when
the existing documents remained pointed at a pre-version candidate after the
boundary had moved; the final closeout must treat stale prose as a failed truth
surface, not as harmless documentation debt.

## Expert Counterfactuals

- Engelbart would put the delivery ledger, consumer renderer, and release
  planner on one contract so a child status could never be promoted to a root
  success without the readback identity.
- A skeptical incident reviewer would ask “what would still be false if this
  process returned zero?” That question leads directly to the typed delivery
  state, cache-content readback, and explicit host-side #687 non-claim.

## Sibling Search

- same layer: reviewer result, delivery ledger, and root CLI status | decision: same waste, fix now | proof: typed result/receipt joins and failure-aware exit tests
- abstraction up: release planner and closeout goal | decision: same waste, fix now | proof: post-publish artifact and goal binding requirements
- specialization down: cache manifest, same-version hash readback, and update-all recovery | decision: same waste, fix now | proof: focused regression suite and doctor output
- mental-model siblings: process exit, transcript, HTTP page, tag, GitHub Release, and installed version | decision: intentional boundary | proof: each observer's non-claim is recorded

## Next Improvements

- workflow: make post-publish reconciliation a required parent-only slice with
  goal, handoff, issue packet, and release record updated in one verified batch.
- capability: add a typed closeout join that rejects stale candidate pointers
  before a goal can become terminal.
- memory: classify wrong path/ref/flag/key calls as structural contract smells in
  every proof and delivery review.

## Lesson Evaluation

Lesson evaluation: {"score_event_count":2,"session_id":"2026-08-21-r3-delivery-provenance-repair-review","status":"effect-recorded"}

## Packet Consumed

Packet Consumed: charness-artifacts/retro/2026-08-21-123706-packet.md

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-21-r3-delivery-review-final.md
