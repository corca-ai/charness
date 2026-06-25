# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship the test-speed slice that moves ordinary payload assertions below the
subprocess boundary in `test_risk_interrupt`, `test_plugin_preamble`, and local
`test_quality_scaffold` paths while preserving thin CLI/exported-boundary smokes.

## Failure Angles

- Jackson/problem framing: converting tests could optimize runner mechanics while
  accidentally removing the real CLI contract being protected.
- Gawande/operations: behavior might become hidden behind helpers if assertions
  move away from the test site.
- Kent Beck/test feedback: the slice should reduce boundary fanout measurably
  without requiring a new gate or broad redesign.

## Counterweight Pass

- No act-before-ship issue remains: risk-interrupt and plugin-preamble keep
  in-process `main()` checks, and quality scaffold still keeps exported consumer
  subprocess smoke.
- Behavior assertions remain visible at test sites: payload fields, status
  transitions, template contract, validator command, and CLI exit/output are
  still named directly.
- Adding another candidate now is over-worry; this slice already reduces the
  ratchet counts and avoids speculative expansion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/test_risk_interrupt.py | action: fix | note: ordinary plan behavior moved to library calls while CLI exit mapping remains covered through main
- F2 | bin: bundle-anyway | evidence: strong | ref: tests/test_plugin_preamble.py | action: fix | note: payload behavior moved to build_payload while JSON CLI output remains covered through main
- F3 | bin: bundle-anyway | evidence: strong | ref: tests/test_quality_scaffold.py | action: fix | note: local scaffold and validator proof moved in-process while exported consumer smoke remains subprocess-backed
- F4 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/quality/2026-06-26-boundary-bypass-test-speed-quality-review.md | action: defer | note: remaining single-target clean candidates should be converted one at a time after boundary-smoke review
- F5 | bin: over-worry | evidence: moderate | ref: tests/test_quality_scaffold.py | action: document | note: adding a separate source-tree scaffold main smoke is unnecessary because exported consumer smoke proves the higher-value boundary

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority
- Host exposure state: requested_fields_sent
- Application state: fields accepted by spawn call; provider application not independently confirmed

## Fresh-Eye Satisfaction

parent-delegated: bounded reviewer `019f00dd-8f0b-7fc2-8492-bb80d2c2d96d`
completed through `multi_agent_v1.spawn_agent`, found no act-before-ship issue,
and recommended shipping without adding another candidate.
