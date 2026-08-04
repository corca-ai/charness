# Critique: Reduce Current Closeout Bottleneck Goal

Date: 2026-08-04

## Decision Under Review

Whether the new goal `charness-artifacts/goals/2026-08-04-reduce-current-closeout-bottleneck.md`
is shaped tightly enough to activate as a current-environment #503 follow-up.
The goal must find and reduce one real closeout bottleneck, or honestly prove
that the historical signal has no current safe target, without weakening proof.

## Execution

Delegated fresh-eye critique ran with three distinct lenses and three successive
repair/activation-read passes. All reviewers were instructed to use the shared
worktree read-only; no files, index, or git state were changed by reviewers.

## Fresh-Eye Satisfaction

parent-delegated — findings were received from Zeno, Godel, Banach, Schrodinger,
Carver, and Sagan. Boundary fingerprints were clean for all six windows.

## Packet Consumed

- Packet consumed: `charness-artifacts/critique/2026-08-04-111554-packet.md`

The original angle pass reviewed the earlier packet
`charness-artifacts/critique/2026-08-04-110830-packet.md`; intermediate repair
reads used the regenerated `111122` and `111233` packets. The final activation
read used the packet bound below and returned PASS after the sample-count repair.

## Reviewed Input Identity

- Packet path: `charness-artifacts/critique/2026-08-04-111554-packet.json`
- Packet SHA256: `27db2b94b18ecc3c195c570e742529544884a7ae50fb3c22e525382f8d0dccb8`
- Identity SHA256: `3c57a62b71e83824df9c6bb72beb202d9daaeebf0914c342cddf58a8646d0476`

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_turns=none
- Host exposure state: requested_fields_sent
- Application state: spawn call accepted; host did not expose a separate application confirmation signal
- Delivery state: findings-received

## Target

Spec critique — pre-implementation goal contract and activation boundary.

## Change

The goal changes the next move from “report recurring telemetry” to “measure
the actual local closeout journey, select one present critical-path bottleneck,
run a fixed before/after experiment, and preserve the correctness boundary.”

## Capability at Stake

The operator should spend less time waiting on repeated local proof while still
seeing failures, recovery paths, coverage, and unproven states. The historical
#503 cohort is a lead, not the current capability contract.

## Findings

### Act Before Ship

- The first baseline must cover the actual local closeout journey, not only a
  convenient pair of commands. Selection now compares `run-quality.sh
  --read-only` and standing pytest with phase elapsed time, invocation
  frequency, serial position, and proof sensitivity.
- Timing comparability must be explicit. The goal now requires at least three
  baseline and three candidate observations, fixed command/corpus/HEAD facts,
  runtime/profile/cache/load facts when available, a fixed statistic and
  threshold chosen before the intervention, and an `inconclusive` result when
  the evidence remains ambiguous.
- No-safe-change behavior must be operational. A failed correctness check,
  failed relief threshold, or inconclusive result restores the pre-change
  behavior. Only evidence-only instrumentation may remain, with an explicit
  reason, owner, and reopen observation.

### Bundle Anyway

- The acceptance matrix now maps current-target selection, material relief,
  proof preservation, and no-safe-change to decisive evidence.
- The correctness channel is explicit: controlled failure/fixture checks plus
  the final local correctness lock, separate from timing runs.
- The prior #503 goal is explicitly complete as a measurement/decision surface;
  this goal is a new current-environment experiment.

## Counterweight Pass

- Over-Worry: cross-host normalization, a universal runtime budget, a new
  telemetry schema, remote CI, and release proof are not needed for this local
  reversible experiment.
- Valid but Defer: `over_slice`, release-helper ordering, and wider scheduling or
  CI restructuring remain separate because they use different units or
  boundaries.
- The counterweight rejected both ritualistically large performance studies and
  a preselected optimization based only on the historical 16-entry cohort.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: goal Slice A and User Acceptance matrix | action: fix | note: baseline must measure the actual local closeout journey and choose by critical-path contribution, not historical duration alone
- F2 | bin: act-before-ship | evidence: strong | ref: goal Agent Verification Plan and Boundaries | action: fix | note: comparable samples, fixed statistic/threshold, and explicit inconclusive handling are required before timing claims
- F3 | bin: act-before-ship | evidence: strong | ref: goal Boundaries and Acceptance Check Matrix | action: fix | note: failed or inconclusive improvements must restore pre-change behavior; only evidence instrumentation may remain with an owner and reopen trigger
- F4 | bin: bundle-anyway | evidence: moderate | ref: goal User Acceptance | action: fix | note: acceptance criteria need explicit decisive checks rather than prose-only success claims
- F5 | bin: over-worry | evidence: weak | ref: goal Non-Goals | action: defer | note: cross-host normalization, universal budgets, telemetry redesign, and remote proof are outside this local experiment
- F6 | bin: valid-but-defer | evidence: moderate | ref: docs/deferred-decisions.md#d51 | action: defer | note: over-slice, release ordering, and broad scheduling work use separate units or boundaries
- F7 | bin: act-before-ship | evidence: strong | ref: goal Interview Decisions | action: fix | note: unified the post-change evidence floor at three comparable observations after the final repair read found a two-versus-three inconsistency

## Deliberately Not Doing

- No performance gate is added merely to make performance a new blocking floor.
- No historical runtime number is reclassified as current relief.
- No telemetry schema expansion is included unless Slice A proves missing
  provenance blocks a concrete local decision.

## Fixed/Probe/Defer Coherence Result

- Fixed: local-only scope, one bottleneck, proof-preservation invariant,
  rollback on failed/inconclusive relief, and no remote side effects.
- Probe: actual closeout journey, current critical-path matrix, comparable
  timing protocol, selected seam owner, and candidate falsifier. Each is
  answerable in Slice A or B and written into the goal/closeout record.
- Defer: cross-host normalization, telemetry redesign, over-slice optimization,
  release-helper ordering, and broad CI scheduling. Each has a separate owner or
  boundary and remains outside this goal.
- Result: pass after the folded repairs; no unresolved unknown is left for the
  implementation slice to invent silently.

## Acceptance Check Coverage Result

- Current target: covered by the goal's acceptance matrix and Slice A selection
  matrix.
- Material relief: covered by fixed baseline/candidate sample counts, fixed
  statistic and threshold, and an explicit inconclusive disposition.
- Proof preservation: covered by controlled failure/fixture checks plus the
  separate final local correctness channel.
- No-safe-change: covered by rollback, explicit evidence-only retention rules,
  owner, and reopen observation.

## Boundary Ownership

- Producer: the selected local runner's phase/timing receipt and its gate
  outputs.
- Consumer: Slice B's target-selection decision and the operator's final
  closeout record.
- Owning surface: the selected runner or gate implementation owner identified by
  Slice A; the generic telemetry miner remains a derivation aid, not the
  optimization owner.
- Verdict: owned-correctly

## Next Move

The goal is safe to activate after these repairs. Slice A must begin with a
current end-to-end local closeout baseline and must be allowed to conclude
`historical signal retired` or `no safe current target` without forcing a code
change. Any concrete implementation then receives a separate slice-level
critique before it is locked. The final activation-read reviewer Sagan returned
PASS after the three-sample repair; its boundary fingerprint verified clean.
