# Critique Review
Date: 2026-06-23

Packet Consumed: charness-artifacts/critique/2026-06-22-224426-packet.md
Decision Path:
charness-artifacts/goals/2026-06-23-skill-claim-fidelity-doc-philosophy.md

## Decision Under Review

Choose #397 remediation from the quality reference classification before editing
the quality skill flow.

Decision: choose BOTH, ordered narrowly. First add one bounded quality judgment
primer before the heavy gate suite; second route on-demand references only from
concrete gate or inventory findings.

## Failure Angles

- Framing reviewer confirmed BOTH addresses the actual execution-shape defect:
  only front-loading can satisfy the `quality-lenses.md` discriminator, but only
  gate-triggered routing can still miss the core judgment primer.
- Operational reviewer confirmed BOTH is sound only if implementation stays
  narrow: one `SKILL.md` primer insertion, no new scripts, no tag-aware builder
  scoring, and no broad quality-flow redesign.

## Counterweight Pass

Act before ship: none after the decision preserves the constraints below.

Bundle anyway: record explicit non-goals for implementation: no tag-aware
builder scoring, no new scripts, no broader quality-flow redesign.

Over-worry: requiring all 9 engage-always references in the first validation
capture unless the implementation explicitly claims full engage-always coverage.
The #397 minimum remains runtime consultation of `quality-lenses.md` plus
observed coverage movement.

Valid but defer: tag-aware scoring/validation and richer on-demand trigger
machinery after the basic execution-shape repair is proven.

## Decision Constraints

- Implement exactly one quality `SKILL.md` primer insertion before broad gates.
- The primer reads only the 9 `engage-always` references and does not chase
  links during the primer.
- On-demand references open only from concrete findings whose trigger matches
  `referenceEngagement.trigger`.
- Do not add new scripts, new scoring, or tag-aware builder behavior in the
  remediation slice.
- Validation for #397 requires runtime consultation of `quality-lenses.md` and
  observed coverage movement; duration remains a separate runtime-budget signal.

## Structured Findings

- F1 | bin: over-worry | evidence: strong | ref: evals/cautilus/quality-claim-fidelity/spec.json | action: document | note: all 9 engage-always refs need not be required in first validation unless implementation claims full engage-always coverage
- F2 | bin: valid-but-defer | evidence: strong | ref: scripts/agent-runtime/build-skill-execution-observation.mjs | action: defer | note: tag-aware builder scoring waits until after basic execution-shape repair
- F3 | bin: bundle-anyway | evidence: strong | ref: skills/public/quality/SKILL.md | action: fix | note: remediation decision must constrain implementation to one primer insertion plus finding-triggered on-demand routing

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
review tasks.
