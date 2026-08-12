# Achieve Goal: Prepare evidence for session-score policy

Status: active
Created: 2026-08-12
Activation: `/goal @charness-artifacts/goals/2026-08-12-prepare-session-score-observation.md` — user explicitly authorized starting score observation from this session on 2026-08-12.

## Active Operating Frame

- Current slice: declare this session's deterministic preview and collect only
  real, cited, session-bound score observations.
- Current slice intent: establish the first nonzero score cohort without
  inventing a budget, a delivery receipt, or a policy conclusion.
- Next action: record `2026-08-12-score-observation-1`, then present its IDs
  for the operator's actual score judgment.
- Verification cadence: validate any proposed evidence schema against the
  ledger checker and test an append/refusal path before policy is changed.
- Gate cadence: ledger validation after every append; focused authoring tests
  before any policy decision; broad quality only if code or a verdict surface changes.
- History boundary: recorded observations and future policy evidence move to
  `## Slice Log`; this frame names only the live collection intent.

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

## Discuss Before Activation

- Discuss before activation: resolved — the user explicitly asked to start
  scores in this session. The authorized action is local declaration and cited
  observation only; score values remain operator judgment, and no receipt,
  budget, graduation, release, or external proof is implied.

## Slice Log

- Shaping: successor was activated after the completed shown-set goal left a
  zero-score ledger and the user authorized beginning observation in this
  session. No policy threshold or score budget is selected.
- Slice 1: declared session `2026-08-12-score-observation-1` with seed of the
  same value. Its frozen snapshot has 16 eligible lessons and 10 ordered IDs;
  ledger validation remains green at 16 lessons/16 transitions and zero scores.
  The next action is operator judgment for one or more cited listed lessons.

## Interview Decisions

- Observation now versus defer until a later session. Chosen: record the
  deterministic session now because the user authorized it; rejected defer
  because it would preserve a zero-score premise without need.
- Author an arbitrary score versus request actual operator judgment. Chosen:
  request judgment after the session list is declared; rejected fabrication
  because a cited score is durable local evidence.

## Plan Critique Findings

- The completed predecessor goal established that a local session record proves
  containment only, never human receipt or usefulness. This goal retains that
  non-claim and does not alter any verdict logic while collecting observations.

## Closeout Binding Plan

- Reviewed inputs: this goal, the schema-v3 ledger, declared session events,
  and cited score events.
- Frozen target: commit each durable observation before any score-policy
  proposal; a later policy slice receives a fresh packet and review.
- Fresh-eye channel: required only for a policy threshold, budget, or verdict
  surface change; collection-only appends use the existing ledger checker.
- Verification lock: cite checker output and score-event count before a policy
  conclusion.
- Terminal record: close only after a real cohort either supports a bounded
  policy decision or demonstrates that the decision remains premature.

## Off-Goal Findings

- No score budget or graduation action is justified by the current zero-score
  state; this is an evidence-collection goal, not an implementation shortcut.

## Final Verification

- Pending — activated collection has not yet recorded its first declared
  session or cited score.

## User Verification Instructions

- After a session is declared, inspect its lesson IDs in the ledger and provide
  only actual cited score judgments through the documented score command.

## Auto-Retro

- Pending — no completed slice yet.

## Context Sources

1. `docs/design-north-star.md` — prevents a score policy from outrunning what
   local evidence can observe.
2. `charness-artifacts/goals/2026-08-12-shown-set-session-records.md` — completed
   containment boundary and its residual non-claims.
3. `charness-artifacts/retro/2026-08-12-shown-set-session-records-retro.md` —
   score-budget deferral and evidence-gap rationale.
