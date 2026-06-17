# Critique Review
Date: 2026-06-17

## Decision Under Review

Issue #382 changes HOTL proving-surface staleness from deterministic proof debt
to a candidate signal requiring agent adjudication, syncs the plugin mirror, and
adds focused regression coverage for the public and exported contract.

## Failure Angles

- Michael Jackson / problem framing: the first draft fixed staleness vocabulary
  but left the workflow completion-audit bullet status-only. Applied: the HOTL
  workflow now blocks unresolved stale-candidate adjudication.
- Gerald Weinberg / diagnostic: the original cause was a collapsed distinction
  between detection and proof debt; the first test only rejected old wording.
  Applied: the test now also pins unresolved-adjudication blocking and the
  plan-vs-proof clause.
- Atul Gawande / operational checklist: the first test did not inspect the
  exported plugin mirror. Applied: the focused test reads both public and plugin
  HOTL skill/reference files.

## Counterweight Pass

- Act Before Ship: none after the applied fixes. The current diff treats stale
  proving-surface refs as `stale_candidate` / `needs_adjudication`, enumerates
  adjudication outcomes, and blocks unresolved adjudication.
- Bundle Anyway: align the ledger-reference completion-audit paragraph with the
  workflow checklist so a future reader cannot quote it as status-only. Applied.
- Over-Worry: do not add a runtime HOTL ledger engine, ceal-local guard changes,
  or unrelated quality/release/HITL stale-signal rewrites in this issue slice.
- Valid but Defer: a future structured ledger schema or audit command could
  encode the adjudication enum mechanically; that is outside this contract fix.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/hotl/SKILL.md:96 | action: fix | note: completion audits needed to block unresolved stale-candidate adjudication; applied in the workflow checklist
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_hotl_adapter.py:166 | action: fix | note: focused regression needed to read plugin mirror and assert unresolved-adjudication blocking plus plan-vs-proof wording; applied
- F3 | bin: bundle-anyway | evidence: strong | ref: skills/public/hotl/references/ledger-and-dispositions.md:76 | action: fix | note: ledger completion-audit paragraph needed the same unresolved-adjudication wording; applied
- F4 | bin: over-worry | evidence: moderate | ref: issue #382 scope | action: document | note: runtime ledger engine and ceal-local behavior changes are outside this contract-fix slice
- F5 | bin: valid-but-defer | evidence: weak | ref: issue #382 scope | action: defer | note: structured ledger-schema enforcement could be future hardening but is not required to close this issue

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority
- Host exposure state: requested_fields_sent
- Application state: host returned completed reviewer results for angle agents
  `019ed3d8-d9bf-7d42-b508-452c10a8ff5d`,
  `019ed3d9-0963-7233-869d-791d3f5bb1c9`,
  `019ed3d9-4c3b-7791-a31a-8c7d37bda45a`, and counterweight agent
  `019ed3db-edbb-7db1-9725-a3f94b00ab01`.

## Fresh-Eye Satisfaction

parent-delegated. Three angle reviewers and one separate counterweight reviewer
ran through the host subagent surface and returned completed results.
