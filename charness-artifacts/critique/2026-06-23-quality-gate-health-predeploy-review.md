# Quality Gate Health Predeploy Review
Date: 2026-06-23

## Decision Under Review

Push/release the two quality-track commits currently ahead of `origin/main`,
including the quality skill compression, planner catalog, catalog/index
validator, exact-prose test cleanup, and gate health/cost review.

Packet Consumed:
`charness-artifacts/critique/2026-06-23-113738-packet.md`

## Failure Angles

- Gate bloat: the new catalog/index validator could add another blocking floor
  that freezes authoring form instead of preventing escaped wrong answers.
- Cost under-evidence: the gate health review could claim the old 10+ minute
  concern is resolved without current timing evidence.
- Premature scheduler deferral: `parallel_group` could be decorative metadata
  while the skill still spends operator budget serially.

## Counterweight Pass

The fresh reviewer found no Act Before Ship issue for item 3. The new validator
is cheap, changed-scoped, and tied to a recorded recurrence: human-visible
quality references can be absent from, or misclassified in, the executable
planner catalog.

Blocking release on executable parallel scheduling would be overreach. The
current artifact records `run-quality-read-only` around one minute median on
the active local profile, with `check-coverage` and `pytest` as the dominant
costs. `parallel_group` can remain judgment metadata until a separate scheduler
design proves applicability, environment expansion, dependency ordering, and
failure aggregation.

## Structured Findings

- F1 | bin: valid-but-defer | evidence: moderate | ref: scripts/validate_quality_reference_catalog.py:34 | action: defer | note: duplicate catalog/index entries are collapsed by dict shape, but duplicate-entry enforcement is outside the drift class being shipped
- F2 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/quality/2026-06-23-gate-health-cost-review.md:66 | action: defer | note: executable `parallel_group` scheduling remains a real future design, not a predeploy blocker
- F3 | bin: over-worry | evidence: strong | ref: docs/conventions/validator-timing-layers.md:83 | action: document | note: the new catalog validator is not needless floor weight because it is cheap and changed-scoped to quality reference/planner edits

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority
- Host exposure state: requested_fields_sent
- Application state: host accepted spawn request and completed reviewer `019ef445-bb03-7c81-9ff4-782b27cb6169`

## Fresh-Eye Satisfaction

parent-delegated. Reviewer `019ef445-bb03-7c81-9ff4-782b27cb6169` completed
with `Execution: executed`, `Fresh-Eye Satisfaction: parent-delegated`, and no
Act Before Ship findings.
