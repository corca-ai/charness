# Achieve Goal: Prepare evidence for session-score policy

Status: complete
Created: 2026-08-12
Activation: `/goal @charness-artifacts/goals/2026-08-12-prepare-session-score-observation.md` — user explicitly authorized starting score observation from this session on 2026-08-12.

## Active Operating Frame

- Current slice: complete — first score cohort recorded and evaluated without policy retuning.
- Current slice intent: preserve three cited, session-bound agent judgments and
  record why they do not identify a score-policy problem.
- Next action: none in this goal; successor comparison remains inactive until naturally varied observations exist.
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
| 1 | Inspect a nonzero local score cohort and state the policy premise. | No budget is defensible while all scores are zero. | Replayed ledger facts and reviewed decision record. | complete |
| 2 | Implement only an approved evidence-intake or policy change. | A chosen premise must precede durable policy. | No-policy decision record; no policy change is warranted. | complete — deferred by evidence |

## Backlog Recount

- Counted: not run — this draft claims no GitHub issue.
- Claims: none.
- Not claimed: all repository issues and contract-graduation work.

## Operator Decision Queue

- none — the user clarified that the agent authors operational lesson scores;
  the first cited cohort is now recorded, while a score-policy decision remains
  deferred for insufficient evidence rather than awaiting user input.

## Coordination Cues

- Phases: spec, critique, impl, prove, retro.
- Routing: successor planning is derived from the completed shown-set goal's
  observed zero-score premise; activation will use the matching installed skill.
- Gather: n/a — the needed first evidence is local ledger state.
- Release: n/a — no release surface is planned.
- Issue closeout: n/a — no issue is claimed.
- Successor goal: `charness-artifacts/goals/2026-08-12-compare-score-policy-evidence.md` — compare naturally varied, cross-session observations before proposing score policy.

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
  ledger validation remains green at 16 lessons/16 transitions.
- Slice 2: recorded three agent-authored, cited, session-contained +2 scores:
  `durable-lesson-ledger-first` for ledger-first sequencing,
  `proof-surface-review-binding` for claims-review repair, and
  `goal-closeout-evidence-binding` for bound closeout evidence. Each has an
  anchor naming this session's observed action. The replayed ledger now has 3
  score events across 3 lessons, all from one declared session.
- Evaluation: insufficient for a score budget or policy decision. The cohort is
  one agent-authored session with 3/10 declared IDs scored, 3/16 eligible
  lessons scored, and only `+2` values. It validates that these three records
  satisfy schema/replay containment; it does not prove the command authoring
  path, anchor fact, usefulness, calibration, presentation effect, or
  contract-graduation eligibility. No new threshold, budget, formula, bucket,
  or `selection_policy_version` was introduced; existing score-sensitive preview
  behavior may still rank these records differently.
- Reopen predicate: before a policy proposal, inspect (1) distribution across
  independently declared sessions, (2) observed zero or negative scores as they
  occur rather than manufactured balance, and (3) comparative preview selection
  concentration/rank changes for no-change and any proposed policy. These are
  required decision inputs, not arbitrary sample-size thresholds.

## Interview Decisions

- Observation now versus defer until a later session. Chosen: record the
  deterministic session now because the user authorized it; rejected defer
  because it would preserve a zero-score premise without need.
- Author an arbitrary score versus agent-authored operational judgment. Chosen:
  score only observed actions with a cited source and concrete anchor; rejected
  unsupported scoring because a cited score is durable local evidence.

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

- No score budget or graduation action is justified by the first correlated
  positive cohort; this is an evidence-collection goal, not an implementation
  shortcut.
- The cohort supersedes the zero-score premise but does not identify whether a
  score-policy problem exists; this is an evidence result, not a ledger defect.

## Final Verification

- Ledger proof: `python3 scripts/check_lesson_ledger.py --repo-root .` passed
  after the three score appends and replays 16 lessons/16 transitions. The
  ledger contains two declared sessions, three score events, three scored
  lessons, and only `+2` event values.
- Focused behavior proof: `pytest -q tests/test_lesson_ledger.py tests/test_lesson_ledger_refusals.py tests/test_lesson_selection_preview.py` passed 23 tests after recording the cohort.
- Decision review: `charness-artifacts/critique/2026-08-12-first-score-cohort-policy-defer.md` confirms no score-policy problem is identified by one correlated positive cohort.
- No broad quality run: no code, validator, preview policy, plugin export, or
  quality surface changed in this goal; the executed focused verifier matches
  the ledger state boundary.
- Residual non-claims: replay proves record shape, citations, session containment,
  and materialized totals only. It does not prove anchor truth, command-path
  execution, human receipt, usefulness, calibration, a policy effect, contract
  graduation, release, or external behavior.

Retro: charness-artifacts/retro/2026-08-12-first-score-cohort-retro.md
Host log probe: skipped: host-log-not-exposed: no goal-scoped host session file or activation-time window is available; thread-wide signals would not measure this short cohort accurately.
Disposition review: charness-artifacts/critique/2026-08-12-prepare-session-score-observation-disposition-review.md

## User Verification Instructions

- Inspect the session ID, score-event anchors, and replayed totals in the ledger;
  the agent may append an operational score only for an observed action tied to
  a cited listed lesson.

## Auto-Retro

- Triggered and persisted: `charness-artifacts/retro/2026-08-12-first-score-cohort-retro.md` refreshed the generated lesson index.
- Retro dispositions: applied: agent-authored score records now use cited source, declared containing session, and concrete action anchor.
- Disposition: applied: the first cohort is explicitly evaluated against comparative evidence inputs, not an arbitrary minimum score count.
- Structural follow-up: repo-local guard: `charness-artifacts/goals/2026-08-12-compare-score-policy-evidence.md` retains the scorer-role prompt correction and comparative evidence requirement.

## Context Sources

1. `docs/design-north-star.md` — prevents a score policy from outrunning what
   local evidence can observe.
2. `charness-artifacts/goals/2026-08-12-shown-set-session-records.md` — completed
   containment boundary and its residual non-claims.
3. `charness-artifacts/retro/2026-08-12-shown-set-session-records-retro.md` —
   score-budget deferral and evidence-gap rationale.
