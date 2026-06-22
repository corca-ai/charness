# Critique Review
Date: 2026-06-23

Packet Consumed: charness-artifacts/critique/2026-06-22-225157-packet.md
Decision Path:
charness-artifacts/goals/2026-06-23-skill-claim-fidelity-doc-philosophy.md

## Decision Under Review

Implement Slice 4 of the skill claim-fidelity goal: edit the public `quality`
skill flow with exactly one bounded judgment-primer insertion before broad
gates, then finding-triggered on-demand reference routing. Keep the remediation
narrow: no new scripts, no tag-aware builder scoring, no broader quality-flow
redesign.

## Failure Angles

- Behavior-contract reviewer confirmed the implementation adds one primer,
  names the 9 engage-always references, forbids link chasing during the primer,
  and adds no scripts or scoring. They found one Act Before Ship issue: the
  on-demand line said only "their trigger", leaving trigger matching too
  implicit.
- Portability reviewer confirmed the public and packaged skill surfaces were
  synced, stayed under the 200-line skill cap, and avoided leaking
  `charness-artifacts`, `referenceEngagement`, eval-spec paths, or Cautilus
  internals into the portable skill surface.

## Counterweight Pass

Act before ship: folded. The public skill now says on-demand references open
only when the concrete finding matches the reference's named trigger/topic and
explicitly says not to scan the on-demand corpus for coverage. The eval spec
comment was also updated after workflow renumbering so it no longer claims the
`quality-lenses.md` route is step 4.

Bundle anyway: keep the line-budget warning visible. `quality` `SKILL.md` is
197/200 lines after this change, so any later addition needs a deliberate trim.

Over-worry: pointing the portable public skill directly at
`evals/cautilus/quality-claim-fidelity/spec.json` or `referenceEngagement` would
leak evaluator implementation into the shipped operator prompt. The folded
wording preserves the committed trigger constraint without exposing that
internal table.

Valid but defer: runtime validation is still required before #397 can be
claimed fixed. Slice 4 only changes the skill contract; Slice 5 must capture a
representative `/charness:quality` run that actually opens
`quality-lenses.md`.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/SKILL.md | action: fix | note: on-demand trigger wording was tightened without leaking eval internals
- F2 | bin: bundle-anyway | evidence: strong | ref: evals/cautilus/quality-claim-fidelity/spec.json | action: fix | note: stale "step 4" comment updated after workflow renumbering
- F3 | bin: valid-but-defer | evidence: strong | ref: skills/public/quality/SKILL.md | action: defer | note: prompt edit still needs representative runtime capture before #397 closeout

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: reasoning_effort=medium
- Host exposure state: requested_fields_sent
- Application state: spawn accepted; two angle reviewers and one counterweight
  reviewer completed; provider application of tier metadata not externally
  confirmed.

## Fresh-Eye Satisfaction

parent-delegated. The host exposed `multi_agent_v1.spawn_agent`; two bounded
angle reviewers and one separate counterweight reviewer completed read-only
review tasks. One Act Before Ship finding was folded before closeout.
