# Broader Proof Claims Goal Pre-Mortem
Date: 2026-08-05

## Decision Under Review

Whether to replace the narrow #502 next-goal draft with a broader goal covering
#491, #496, #502, #504, and #506 as one proof-boundary trust outcome.

## Klein Lineage Cite

`docs/design-north-star.md` P4/P5 and the previous
`charness-artifacts/critique/2026-08-05-proof-verdict-contracts-goal-critique.md`
are the decision lineage: proof claims need a distinct observer/channel, but
the remedy must not become a universal gate or schema.

## Change

Keep the broader user-requested issue family visible, but make the goal an
umbrella maintenance outcome with independent reader/producer/owner tracks.
Only #502 carries a new shared implementation slice. #496 and #504 are local
repair/closeout tracks unless fresh evidence reopens implementation; #491 and
#506 retain their own decision and helper boundaries.

## Capability at Stake

A Charness maintainer at a proof boundary should be able to tell what an
evidence surface claims, which scope or identity it binds, who owns the meaning,
and what action follows. The same vocabulary can organize review, but it cannot
stand in for a shared runtime consumer: terminal quality output, a stale doc,
goal-bound retro persistence, and a reviewer snapshot are read by different
actors at different moments.

## Failure Angles

- **Jackson / problem framing:** the five issues share a maintenance concern,
  not one first-reader workflow. A goal that says every surface must expose one
  six-field contract would solve the convenience of the plan rather than a
  user's actual decision.
- **Weinberg / diagnostic integrity:** #502 has a direct one-producer/
  17-consumer ownership failure. #496 is a policy-aware semantic warning and is
  already locally repaired. #491 is reference/behavior drift, #504 is goal
  identity binding, and #506 is verifier-input selection. They need separate
  owners and separate falsifiers.
- **Gawande + Raskin / operational first reader:** each track must name one
  immediate observable and next action: a final quality line and exit code for
  #502, an intent-safe warning for #496, a claim disposition for #491, a
  goal-bound retro readback for #504, and an explicit window refusal for #506.
  “Legible” without this observable is not acceptance.
- **Counterweight / scope discipline:** a universal receipt, reference manifest,
  semantic meta-gate, or new shared schema would add maintenance burden without
  evidence that these surfaces share a consumer. #503/#505, #480/#482/#483/#484,
  and #468 remain distinct families.

## Counterweight Pass

- **Act Before Ship — strong:** replace the draft's requirement that every
  included surface expose all common fields with a per-issue matrix. Record the
  reader, producer, owner, exact observable, evidence identity, next action,
  and non-claim per row.
- **Act Before Ship — strong:** mark #496 and #504 as existing-local-repair /
  closeout tracks, not fresh implementation slices. Reopening their settled
  behavior would repeat prior work and blur local behavior proof with remote
  issue closure.
- **Bundle Anyway — strong:** retain #502's two terminal producer surfaces in
  one implementation track and retain the common matrix as a review/closeout
  aid. This preserves the user's broader outcome without inventing a runtime
  protocol.
- **Over-Worry — moderate:** a universal verdict protocol, universal reference
  manifest, and new semantic gate are not justified. The current evidence shows
  recurring misses, not a common checker that should own all meanings.
- **Valid but Defer — strong:** #491's manifest versus literal-set check versus
  reviewer-owned question; #506's default invocation policy; #504's remote
  closeout carrier; and #496's remote issue closeout remain distinct decisions.

## Acceptance Tightening

- The goal's acceptance now requires a per-issue matrix and independent proof;
  no selected surface is required to implement every matrix field.
- #502 remains the only new shared-owner implementation: focused semantic
  fields, thin renderers, last-line behavior, mixed recovery evidence, and
  subprocess exit status.
- #496 must preserve its existing field-aware positive/negative controls and
  must not reopen the generic empty-default predicate without new evidence.
- #491, #504, and #506 each require their own reader-facing observable and
  behavior channel before any issue-close claim.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: goal `## Goal`, `## Boundaries` | action: fix | note: replace the universal six-dimension requirement with a per-issue reader/owner/observable matrix
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/issue/2026-08-04-issue-496-local-closeout.md; docs/handoff.md | action: fix | note: classify #496 and #504 as local-repair/closeout tracks, not fresh implementation
- F3 | bin: bundle-anyway | evidence: strong | ref: live #502; charness-artifacts/critique/2026-08-05-proof-verdict-contracts-goal-critique.md | action: fix | note: keep #502's quality and slice-closeout terminal surfaces together under one receipt-owner slice
- F4 | bin: bundle-anyway | evidence: strong | ref: goal `## Slice Plan` | action: fix | note: keep the common matrix as review/closeout structure while preserving independent track owners
- F5 | bin: over-worry | evidence: moderate | ref: docs/design-north-star.md; live #491 | action: document | note: do not create a universal verdict protocol, reference manifest, or semantic meta-gate
- F6 | bin: valid-but-defer | evidence: strong | ref: live #491 | action: defer | follow-up: deferred #491 corpus/claim-owner decision | note: choose reviewer-owned versus narrow mechanical coupling only after inventory
- F7 | bin: valid-but-defer | evidence: strong | ref: live #506; skills/shared/scripts/reviewer_boundary_fingerprint.py | action: defer | follow-up: deferred #506 explicit-window/default invocation hardening | note: keep snapshot selection as a helper-owned track
- F8 | bin: act-before-ship | evidence: strong | ref: goal `## Boundaries` track scope map | action: fix | note: bind every row to producer, consumer/first reader, observable/falsifier, and closure dependency
- F9 | bin: act-before-ship | evidence: strong | ref: docs/handoff.md; goal `## Boundaries` | action: fix | note: make the umbrella coordination boundary independent from any one release or issue-close transaction
- F10 | bin: bundle-anyway | evidence: strong | ref: goal `## Slice Plan` | action: fix | note: preserve #502 as the only new shared implementation and keep #496/#504 as local-proof/closeout tracks
- F11 | bin: over-worry | evidence: moderate | ref: goal `## Non-Goals` | action: document | note: do not add matrix fields, runtime receipts, manifests, or gates merely for symmetry
- F12 | bin: valid-but-defer | evidence: strong | ref: live #491; live #506 | action: defer | follow-up: deferred issue-specific owner decisions | note: keep #491 corpus coupling and #506 default-window policy for their own tracks

## Deliberately Not Doing

- No one receipt schema or status vocabulary across the five surfaces.
- No reimplementation of #496 or #504 merely to make the umbrella goal look
  symmetrical.
- No new semantic meta-gate for #491; a reviewer-owned decision remains valid
  unless a real mechanically observable claim relationship is found.
- No inclusion of the #503/#505 runtime-cost family, the #480/#482/#483/#484
  packaging/reachability family, or #468 deferred-remedy verification.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.6-terra; reasoning_effort=medium;
  service_tier=priority; unnamed one-shot spawn; fork_context=false.
- Host exposure state: requested_fields_sent
- Application state: host-confirmed: four spawned agents returned completed
  findings; provider application of model fields is not independently exposed.
- Delivery state: findings-received.

## Fresh-Eye Satisfaction

parent-delegated — four distinct bounded reviewers ran: Jackson/problem framing,
Weinberg/diagnostic integrity, Gawande/Raskin operational first-reader, and a
separate counterweight. All findings arrived in the parent context and all
reviewers reported read-only behavior. A second repaired-surface round ran the
same four distinct lenses; it found the missing producer/consumer/falsifier
columns and the ambiguous shared transaction/handoff route. Those findings were
folded into the goal and handoff, and all four second-round boundary verifies
were `verdict: clean`.

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/broader-proof-claims-goal-packet.json`
- Packet path: `charness-artifacts/critique/broader-proof-claims-goal-packet.json`
- Packet SHA256: `68ec665bd8a5d19c72e4b83eb0dd5e0fdd36aea5eee70117eebc96e964bd77d1`
- Reviewer-facing packet: `charness-artifacts/critique/broader-proof-claims-goal-packet.md` (SHA256 `20c0762cc103b79ae3fdc13ad7959c43b571b2bee9de6373c60d4bfe304c2941`)
- Identity SHA256: `10889116602c0fefffc191686f55edb0c98063d91240b9fd78505e962c0a1722`
- The packet was regenerated after the matrix, transaction boundary, and
  handoff repairs so the durable input identity is current. The second-round
  findings above are the fresh-eye evidence for those repairs; the final packet
  rebind after the handoff pointer refresh adds no new review claim.

## Closeout Claims Review

One separate closeout-claims reviewer found no blocker: the artifact honestly
states that it is a draft, makes #502 the only new shared implementation, keeps
#496/#504 as local-repair/closeout tracks, and makes no remote-success or issue-
close claim. One wording correction was folded: publication and issue-close
actions may follow a final local bundle, but remain separately verified track
boundaries. The claims review boundary verify returned
`verdict: parent-attributed` with only the parent goal edit declared; no
undeclared reviewer drift was reported.

## Boundary Ownership

- Producer: each selected surface's own producer — quality/closeout receipt,
  policy-aware warning, reference claim, retro persistence boundary, or
  reviewer-boundary snapshot verifier.
- Consumer: the first reader named in the per-issue matrix — terminal operator,
  policy/config author, behavior-changing maintainer, goal operator, or review
  parent.
- Owning surface: the producer/consumer pair for each issue; the umbrella goal
  owns only the comparison matrix and sequencing, not their semantic state.
- Verdict: owned-correctly.

## Next Move

The goal and handoff now carry the tightened independent-track boundary, the
per-track scope map, and the current packet identity. Validate both artifacts
and leave the goal inert until the operator confirms that the broader umbrella
is worth the coordination cost. If the operator wants one first-reader
implementation goal instead, activate the existing #502-focused draft and
leave these four issues as independent follow-ups.
