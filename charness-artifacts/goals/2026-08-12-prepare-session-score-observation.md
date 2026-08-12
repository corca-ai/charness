# Achieve Goal: Prepare evidence for session-score policy

Status: draft
Created: 2026-08-12
Activation: draft successor to `2026-08-12-shown-set-session-records.md`; activate only when an operator provides real local session/score observations.

## Active Operating Frame

- Current slice: draft — no score-policy implementation has begun.
- Current slice intent: define the smallest evidence intake and decision record
  needed to judge a score budget without inventing presentation or usefulness
  claims.
- Next action: activate after at least one real cited, session-bound score
  event is available for inspection.
- Verification cadence: validate any proposed evidence schema against the
  ledger checker and test an append/refusal path before policy is changed.

## Goal

Turn real local session-bound cited scores into a reviewable decision about
whether any score budget or ranking policy is warranted, without treating the
session record as proof of human receipt or contract-graduation evidence.

## Non-Goals

- Fabricating scores, sessions, presentation receipts, calibration results, or
  contract membership changes to make a policy decision possible.
- Adding a fixed score budget before a real cohort supplies a premise.
- Push, release, hosted behavior, or external observation claims.

## Boundaries

- The existing schema-v3 ledger remains the source of cited, session-contained
  score facts; a successor may not weaken its append-only or provenance checks.
- A score count is local authoring data, not evidence a user saw or used a
  selected lesson.
- Any budget, selection adjustment, or graduation proposal requires a distinct
  reviewed decision from observed data and stays out of this draft.

## User Acceptance

- An operator can see exactly what observation is missing before score policy
  is considered, rather than receiving an arbitrary budget.

## Agent Verification Plan

### Low-Cost Checks

- Ledger checker, focused session/score tests, and a state-count inspection.

### High-Confidence Checks

- Fresh-eye review if a policy threshold, scoring budget, or validator verdict
  is proposed.

### External Or Live Proof

- Required only for actual human-facing receipt claims; those claims are not
  authorized by this draft.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Inspect a nonzero local score cohort and state the policy premise. | No budget is defensible while all scores are zero. | Replayed ledger facts and reviewed decision record. | pending |
| 2 | Implement only an approved evidence-intake or policy change. | A chosen premise must precede durable policy. | Tests, review, and broad quality receipt. | pending |

## Backlog Recount

- Counted: not run — this draft claims no GitHub issue.
- Claims: none.
- Not claimed: all repository issues and contract-graduation work.

## Operator Decision Queue

- Decision: whether and when to supply real session-bound cited scores for the
  first policy cohort.
- Owner: operator.
- Why deferred: current ledger state has zero score events, so a score budget
  would be invented rather than inferred.
- Unblock action: record actual cited score events through the existing session
  and score commands, then activate this goal.
- Revisit trigger: ledger checker reports a nonzero score-event count.

## Coordination Cues

- Phases: spec, critique, impl, prove, retro.
- Routing: successor planning is derived from the completed shown-set goal's
  observed zero-score premise; activation will use the matching installed skill.
- Gather: n/a — the needed first evidence is local ledger state.
- Release: n/a — no release surface is planned.
- Issue closeout: n/a — no issue is claimed.

## Context Sources

1. `docs/design-north-star.md` — prevents a score policy from outrunning what
   local evidence can observe.
2. `charness-artifacts/goals/2026-08-12-shown-set-session-records.md` — completed
   containment boundary and its residual non-claims.
3. `charness-artifacts/retro/2026-08-12-shown-set-session-records-retro.md` —
   score-budget deferral and evidence-gap rationale.
