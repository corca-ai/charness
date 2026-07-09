# Outcome-driven feedback loop pre-implementation critique
Date: 2026-07-10

## Decision Under Review

Lock the S1 contract for a privacy-safe feedback path that observes follow-through
after a delivered usage episode without relabeling `slice_closeout` delivery as
satisfaction.

## Failure Angles

- Problem framing and structure: the initial S1 wording proved only that another
  emitter could exist; it did not define which observer-owned fact qualifies as
  feedback or bind each success criterion to an executable check.
- Diagnostic ownership: `slice_closeout_usage_episode.py` owns delivery and
  first-value evidence. Later human or lifecycle feedback must stay append-only
  and observer-owned instead of mutating or backfilling that producer's record.
- Contract split-brain: `docs/product-success-metrics.md` names a closed feedback
  vocabulary, while `episode.schema.json` accepts every non-empty string and the
  reporter leaves `edited` unclassified.
- Operational integrity: a feedback event without target linkage, idempotency,
  evidence provenance, and reporter reconciliation can inflate episode counts or
  count an unlinked observation as satisfaction.

## Counterweight Pass

- Act before implementation: define feedback qualification, a closed enum,
  append-only target linkage, evidence provenance, idempotency, and denominator
  separation. These are the minimum conditions for an honest report.
- Bundle anyway: map the contract to focused schema, writer, validator, and
  reporter fixtures; make plain output distinguish delivery episodes from
  feedback events.
- Over-worry: a parallel event store, general registry, historical backfill, and
  live consumer proof are unnecessary. Widen the existing JSONL record contract
  into a small discriminated union and preserve the live-proof non-claim.
- Valid but defer: automatic issue/release/handoff observers and remote consumer
  feedback coverage belong after the local record/reconciliation seam is proven.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/slice_closeout_usage_episode.py:67 | action: fix | note: keep delivery production separate from append-only observer-owned feedback
- F2 | bin: act-before-ship | evidence: strong | ref: integrations/usage-episodes/episode.schema.json:123 | action: fix | note: make the feedback vocabulary closed and align reporter classifications
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/report_usage_episodes.py:218 | action: fix | note: link and reconcile feedback without inflating the delivery denominator
- F4 | bin: bundle-anyway | evidence: moderate | ref: charness-artifacts/goals/2026-07-10-outcome-driven-autonomous-improvement.md | action: fix | note: bind S1 criteria to named focused test targets
- F5 | bin: valid-but-defer | evidence: strong | ref: docs/product-success-metrics.md:376 | action: defer | note: consumer-repo feedback proof and broader automatic observers remain outside S1
- F6 | bin: over-worry | evidence: moderate | ref: scripts/report_usage_episodes.py:23 | action: document | note: a separate stream or general event-sourcing subsystem is unnecessary for the first linked feedback event

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority.
- Host exposure state: requested_fields_sent
- Application state: spawn requests accepted and reviewer agent ids returned; provider-side application metadata was not exposed.

## Fresh-Eye Satisfaction

parent-delegated — two distinct spec angles and one separate counterweight
review completed against
`charness-artifacts/critique/2026-07-09-211611-packet.md`.

## Boundary Ownership

- Producer: `slice_closeout` produces delivery/first-value episodes; a later
  feedback observer produces linked feedback evidence.
- Consumer: usage validation and reporting reconcile both records for operators
  reviewing product evidence.
- Owning surface: the usage-episodes integration owns schemas and record
  semantics; the feedback writer owns append behavior; the reporter owns joined
  denominators and non-claims.
- Verdict: owned-correctly
