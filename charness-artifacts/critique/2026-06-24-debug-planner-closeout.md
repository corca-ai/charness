# Debug Planner Closeout
Date: 2026-06-24

## Decision Under Review

Move `debug` bootstrap to a planner-first shape: `plan_debug_run.py` names the
current artifact state, prior debug memory, seam-risk interrupt posture,
required/on-demand reads, gate packets, and next action before broad search or
repair. Keep the public skill body focused on diagnosis-first RCA and durable
memory.

## Failure Angles

- Fresh-eye review found the planner had hand-copied seam-risk taxonomy instead
  of consuming the canonical risk-interrupt parser, so `repeated-symptom` could
  be misrouted as ordinary implementation.
- Fresh-eye review found prior incidents were sorted by filename, not recency;
  mixed historical names could hide newer incidents behind older `debug-*`
  records.
- Same-agent review checked the exported-plugin and boundary-bypass hazards:
  the new planner must remain runnable in source and plugin layouts, while tests
  should not add a new subprocess boundary around an import-safe script.

## Counterweight Pass

- The taxonomy issue was a real ship blocker because it could suppress the
  planner's most important interrupt signal before the validator ran.
- The prior-memory ordering issue was not correctness-critical for every run,
  but it directly weakened the skill's durable-memory promise and was cheap to
  fix in the same slice.
- A broader redesign of debug memory classification, reference merging, or full
  Cautilus scenario recapture is valid but outside this planner-first slice; the
  deterministic tests and existing dogfood registry cover the changed contract.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/debug/scripts/plan_debug_run.py | action: fix | note: Use `scripts.risk_interrupt_lib` canonical taxonomy/parser so forced seam risks cannot be planner-misrouted.
- F2 | bin: bundle-anyway | evidence: moderate | ref: skills/public/debug/scripts/plan_debug_run.py | action: fix | note: Sort prior debug records by mtime/name recency before capping the planner's related-memory list.
- F3 | bin: over-worry | evidence: weak | ref: evals/cautilus/scenarios.json | action: defer | note: Do not recapture the maintained `debug-adapter-bootstrap` scenario for this slice; routing/adapter identity stayed the same and deterministic planner/scaffold/artifact tests own the changed behavior.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: bounded fresh-eye code review.
- Requested spawn fields: default subagent with explicit read-only scope over the current uncommitted debug planner slice.
- Host exposure state: requested_fields_sent
- Application state: host-confirmed: subagent `019ef738-b793-7612-b669-3f2c8db9fbbf` returned two findings; both were fixed and regression-tested.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated. The parent spawned one bounded
fresh-eye reviewer for the uncommitted slice. The reviewer reported two
actionable findings: canonical seam-risk taxonomy drift and prior-incident
ordering. Both were fixed before closeout, with focused regression coverage in
`tests/test_debug_plan.py`.
