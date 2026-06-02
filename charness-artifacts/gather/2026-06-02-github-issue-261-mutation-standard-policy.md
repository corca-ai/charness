# Gather: GitHub Issue #261 Mutation-Standard Policy

Source: https://github.com/corca-ai/charness/issues/261
Access Mode: direct-cli via authenticated `gh issue view 261`
Freshness: 2026-06-02 session read; issue state `OPEN`, updated `2026-06-01T09:21:15Z`
Canonical Identity: corca-ai/charness#261

## Requested Scope

Durable source snapshot for shaping an `achieve` goal around #261 only, after prior #273/#274 bundled goals intentionally left #261 open.

## Current GitHub State

- Number: #261
- Title: Coordination-cues achieve trio has latent mutation survivors (never mutation-tested due to chronic changed-line blocking)
- State: OPEN
- Labels: none
- Created: 2026-05-30T20:43:19Z
- Updated: 2026-06-01T09:21:15Z

## Issue Body Summary

The issue was filed after #260 finally mutation-tested the coordination-cues achieve trio that had previously been dropped by changed-line blockers. The body records latent mutation survivors in:

- `goal_artifact_closeout_evidence.py`
- `goal_artifact_coordination_floors.py`
- `check_goal_artifact.py`

Initial scoped data named `closeout_evidence` at 88.8%, `coordination_floors` at 85.0%, and `check_goal_artifact` below the fill-eligibility floor. The issue distinguished this from #260's measured failure and identified a gate-design sub-question: whether known-equivalent operator classes should be excluded rather than chased.

## Live Comments Summary

- 2026-06-01 comment after open-issue closeout carrier: #261 stays open because #265 handled the mechanical survivor triage path, while #261 owns the mutation-standard policy boundary for equivalent or low-value survivors.
- 2026-06-01 comment after #273 mutation gate recovery carrier: prior scoped proof remains 514/514 executed, 467 killed, 47 survived, 90.9% reachable score. Remaining survivors are an equivalent/low-value mutation-standard policy question, not a #273 coverage fix.

## Repo Context To Follow

- `charness-artifacts/critique/2026-06-01-265-261-coordination-survivor-triage-critique.md`
- `charness-artifacts/goals/2026-06-01-273-261-mutation-regression-and-survivors.md`
- `charness-artifacts/goals/2026-06-02-274-261-mutation-regression-and-standard-decision.md`
- `charness-artifacts/issue/2026-06-01-273-261-mutation-gate-recovery.md`
- `charness-artifacts/issue/2026-06-02-274-261-mutation-workflow-recovery.md`

## Open Gaps

This gather record does not include a fresh mutation run. It records the live issue state and prior proof anchors needed to decide the #261 policy slice.
