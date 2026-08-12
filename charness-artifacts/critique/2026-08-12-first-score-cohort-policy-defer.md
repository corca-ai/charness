# First Score Cohort Policy-Defer Critique

Date: 2026-08-12
Goal: charness-artifacts/goals/2026-08-12-prepare-session-score-observation.md

## Decision Under Review

Do not introduce a score budget, threshold, formula, bucket change, or
selection-policy version from the first cohort: three agent-authored `+2`
records in one declared session.

## Failure Angles

- Jackson framing: a policy should solve an observed selection problem, not
  merely react to a nonzero score count.
- Weinberg diagnosis: schema/replay containment is distinct from the truth of
  an anchor, usefulness, policy causality, or an executed authoring-command
  receipt.

## Counterweight Pass

- Do not manufacture zero/negative scores, human receipts, or an arbitrary
  cohort-size threshold to make the policy decision look ready.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/retro/lesson-ledger.json | action: document | note: record the actual cohort as 1 session, 3/10 declared IDs, 3/16 eligible lessons, and only +2 values before closing.
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/goals/2026-08-12-prepare-session-score-observation.md | action: document | note: require comparative decision inputs—cross-session distribution, naturally observed sign diversity, and preview concentration/rank comparison—rather than a fixed sample threshold.
- F3 | bin: bundle-anyway | evidence: strong | ref: scripts/lesson_ledger_lib.py | action: document | note: narrow the current proof to schema/replay containment and materialized totals; do not claim anchor truth, usefulness, or authoring-command evidence.
- F4 | bin: over-worry | evidence: strong | ref: docs/development.md | action: defer | note: do not add human receipt, score calibration, or a budget now.
- F5 | bin: valid-but-defer | evidence: strong | ref: scripts/lesson_selection_preview_lib.py | action: defer | note: test any later threshold/formula only against a concrete proposed policy and comparative preview change.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye decision reviewers.
- Requested spawn fields: task_name, fork_turns=all; host default model/effort.
- Host exposure state: host-defaulted
- Application state: host-confirmed: two reviewer tasks were created and returned findings.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-12-033958-packet.md
- Packet path: charness-artifacts/critique/2026-08-12-033958-packet.json
- Packet SHA256: 3442101dd65291277bcade9e4c76776cd197d2661ae1b5436a1ceaddfeb3806a
- Identity SHA256: 995bbd7784f0adf649ee34085ee380a9b9aee7ca43fc5564b937d4a127347d8b
- Packet limitation: it bound transient quality receipts, not the later ledger
  append. The reviewers also read the explicit current ledger and goal state;
  this artifact does not present packet binding as proof of those later facts.

## Boundary Ownership

- Producer: the ledger validator replays record shape, citations, session
  containment, and materialized totals.
- Consumer: the selection preview consumes replayed totals/counts under its
  existing policy; the goal consumes them only for a defer decision.
- Owning surface: lesson-ledger-and-contract-register.
- Verdict: owned-correctly

## Deliberately Not Doing

- No synthetic score balance, score budget, policy retuning, human receipt
  claim, contract graduation, release, or external observation.

## Next Move

Close the evidence-only goal with a no-policy conclusion and reopen policy work
only when the named comparative observations exist.
