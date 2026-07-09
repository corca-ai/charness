# Critique Review
Date: 2026-07-09

## Decision Under Review

A/B efficiency harness follow-up: move live-run config validation into a helper,
reject malformed configs before selftest or capture spend, wire plugin mirrors,
and add pre-spend order tests for the default and explicit `--out-dir` paths.

Packet Consumed: `n/a (prepare packet was generated during review and removed because packet drafts under critique/ fail the live corpus validator)`

## Failure Angles

- Problem framing: the first patch solved most malformed config cases but the
  key success condition is pre-spend refusal, not only nicer exceptions.
- Operational checklist: explicit `--out-dir` initially bypassed `name`
  validation, letting a malformed advertised schema field reach selftest.
- Boundary ownership: root script owns source behavior; plugin script is a
  generated mirror and must be synced, not hand-edited as the source of truth.

## Counterweight Pass

- Act Before Ship: explicit `--out-dir` had to validate `name` before selftest;
  fixed by `validate_run_config(..., require_results_name=True)` plus order
  tests.
- Bundle Anyway: direct helper coverage for `require_results_name=True` was
  cheap and now pins the helper contract.
- Over-Worry: the default results-dir path was already pre-selftest guarded;
  the added default-path order test is defensive.
- Valid but Defer: broader helper API simplification can wait; current CLI
  behavior is covered without expanding into unrelated schema design.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/run_skill_efficiency_ab.py:455 | action: fix | note: explicit --out-dir bypassed config name validation before selftest; fixed by requiring results name in run config validation
- F2 | bin: bundle-anyway | evidence: moderate | ref: tests/test_skill_efficiency_ab.py:571 | action: fix | note: helper option require_results_name now has direct unit coverage
- F3 | bin: over-worry | evidence: moderate | ref: tests/test_skill_efficiency_ab.py:523 | action: document | note: default results-dir bypass concern was already guarded, but the order test remains useful regression proof
- F4 | bin: valid-but-defer | evidence: weak | ref: scripts/run_skill_efficiency_ab_validation.py:45 | action: defer | note: broader helper API simplification is real but not needed to close the pre-spend CLI bug

## Reviewer Tier Evidence

- Requested tier: high-leverage where available; runtime exposed explicit model fields only.
- Requested spawn fields: model=gpt-5.4-mini, reasoning_effort=medium.
- Host exposure state: requested_fields_sent
- Application state: host accepted reviewer spawns and returned three independent reports.

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: root A/B harness config validator and live-run CLI path.
- Consumer: live A/B runner, plugin-exported CLI mirror, and operators avoiding accidental live capture spend.
- Owning surface: repo-owned root script plus generated plugin export.
- Verdict: owned-correctly
