# Usage feedback code critique
Date: 2026-07-10

## Decision Under Review

Land the S1 mixed-stream feedback writer, semantic validator, reporter
reconciliation, schemas, documentation, tests, and installed-plugin mirrors.

## Failure Angles

- Evidence semantics: both reviewers reproduced a split validity path where the
  validator rejected duplicate feedback but the reporter accepted it and
  produced a satisfaction rate of 2.0 over one delivery episode.
- Compatibility and export: the existing 1,330 delivery records remained valid,
  but installed-plugin reporting initially lacked a linked-feedback fixture.
- Operator interface: quality mode initially blocked dry-run preview even though
  preview performs no write.
- Append integrity: concurrent identical executions can still race, and
  rotation cannot yet reconcile linked targets across rotated files.

## Counterweight Pass

- Act before ship: the reporter now calls the shared semantic validator before
  product-evidence aggregation, and quality mode blocks only `--execute`.
- Bundle anyway: installed-plugin reporting now proves one delivery plus one
  linked feedback event reaches 100% coverage without inflating delivery count.
- Over-worry: `counts.feedback_signal` now describes observed feedback while
  missing coverage stays in its explicit gap fields; no known consumer requires
  the old `<missing>` bucket. Schema cannot prove the meaning of an opaque token,
  so privacy remains a shape-and-policy boundary rather than a fake oracle.
- Valid but defer: concurrent-execute locking and stream-aware multi-file
  rotation are real robustness seams, but neither is required for the explicit
  single-writer S1 path; both remain visible in the goal disposition.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/report_usage_episodes.py:111 | action: fix | note: applied shared semantic feedback validation before reporter claims
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/record_usage_feedback.py:90 | action: fix | note: quality mode now permits read-only preview and blocks only execute
- F3 | bin: bundle-anyway | evidence: moderate | ref: tests/test_usage_feedback.py | action: fix | note: bundled installed-plugin linked-feedback reporter proof
- F4 | bin: over-worry | evidence: contested | ref: scripts/report_usage_episodes.py | action: document | note: do not restore the legacy missing bucket without a real consumer regression
- F5 | bin: valid-but-defer | evidence: moderate | ref: scripts/record_usage_feedback.py | action: defer | note: concurrent identical execute locking belongs to the append-robustness follow-up recorded in the goal
- F6 | bin: valid-but-defer | evidence: strong | ref: docs/product-success-metrics.md | action: defer | note: stream-aware rotation and multi-file reconciliation remain explicitly deferred

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority.
- Host exposure state: requested_fields_sent
- Application state: spawn requests accepted and reviewer agent ids returned; provider-side application metadata was not exposed.

## Fresh-Eye Satisfaction

parent-delegated — two distinct code angles and one separate counterweight
review completed against
`charness-artifacts/critique/2026-07-09-212954-packet.md`.

## Boundary Ownership

- Producer: the feedback writer and shared feedback module produce and define
  append-only feedback semantics.
- Consumer: validator and reporter consume the same semantic validity result;
  product evidence renders only semantically valid joined records.
- Owning surface: usage-episodes integration plus its source/plugin script pair.
- Verdict: owned-correctly
