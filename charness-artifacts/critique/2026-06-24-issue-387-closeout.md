# issue 387 closeout
Date: 2026-06-24

## Decision Under Review

Close #387 after confirming the `achieve` goal-closeout shape helper now gives a
goal-specific one-pass report for missing or malformed closeout evidence while
leaving `check_goal_artifact.py` as the authoritative complete-flip validator.

## Failure Angles

- Closeout strictness could have been weakened by turning the validator into an
  advisory. Fresh-eye check: strictness remains with `check_goal_artifact.py`;
  `describe_goal_closeout_shape.py --goal-path` is an authoring affordance.
- One-pass reporting could drift from the real floors. Fresh-eye check:
  `goal_conditional_shape()` reads the live closeout and timebox reports rather
  than re-deriving their trigger logic.
- A future floor could be added without a describe row. Fresh-eye check: this is
  the residual recurrence risk; the existing floor-addition advisory/test
  discipline should force a matching describe row and fixture when the floor is
  added.

## Counterweight Pass

- Act before ship: none found by the bounded reviewer.
- Bundle anyway: close #387 now because the shipped A2 change directly satisfies
  the issue's useful outcome and is already on `origin/main`.
- Valid but defer: do not add another blocking gate for this class. The current
  recurrence control is a non-blocking floor-addition advisory plus tests.
- Over-worry: do not require Cautilus here; this is a local deterministic helper
  and documentation contract, covered by focused tests and a reviewer smoke.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: skills/public/achieve/scripts/describe_goal_closeout_shape.py:221 | action: document | note: `--goal-path` renders triggered missing floors plus satisfied floors and appends the live form reference
- F2 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_describe_goal_closeout_shape.py:127 | action: document | note: focused tests prove non-blocking render, missing/satisfied split, grandfathered omission, and static catalog backward compatibility
- F3 | bin: valid-but-defer | evidence: moderate | ref: skills/public/achieve/scripts/describe_goal_closeout_shape.py:147 | action: defer | note: `_floor_rows()` is an explicit catalog, so future floors still need matching describe rows and fixtures when added

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: none; parent used `multi_agent_v1.spawn_agent` with
  default inherited model/effort per host tool guidance.
- Host exposure state: host-defaulted
- Application state: host-confirmed: `multi_agent_v1.spawn_agent` returned
  agent `019ef6c0-b234-7b11-9b75-ce05534e0c4e`, and it completed via
  `wait_agent`.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated. One bounded fresh-eye reviewer
inspected the source, docs, commits `e6d1a59a` and `49748a25`, ran focused
`test_describe_goal_closeout_shape.py` proof with bytecode disabled, and smoke
ran `describe_goal_closeout_shape.py --goal-path` against a temp goal. Verdict:
close #387; no blocker before closing.
