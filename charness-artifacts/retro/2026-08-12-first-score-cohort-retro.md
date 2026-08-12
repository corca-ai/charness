# Goal Closeout Retro: First Score Cohort

Goal: charness-artifacts/goals/2026-08-12-prepare-session-score-observation.md
Date: 2026-08-12

## Context

This goal recorded the first three cited, session-contained agent score records
and decided not to turn one correlated positive cohort into score policy.

## Window

- Declared session: `2026-08-12-score-observation-1`.
- Cohort: three `+2` records for three of the session's ten listed lessons.

## Evidence Summary

- Ledger replay validates 16 lessons/16 transitions, two declared sessions, and
  three score events.
- Focused ledger and preview tests passed after the append.
- Fresh-eye decision review required comparative observations rather than a
  fixed cohort-size rule before policy is considered.

## Waste

- The run initially asked the user to score agent operational lessons. That
  confused the scorer role and delayed the first observation; the user corrected
  it, after which only observed agent decisions were recorded.

## Critical Decisions

- Record agent-authored scores only with a source citation, containing session,
  and concrete anchor.
- Defer score budget or selection retuning: one session, 3/10 listed lessons,
  3/16 eligible lessons, and only +2 signs do not identify a policy problem.

## North Star Alignment

The ledger gate checks replayable containment rather than pretending to measure
helpfulness. The decision keeps policy teeth out of an observationally weak
cohort and preserves the explicit non-claims.

## Expert Counterfactuals

- Klein's premortem lens asks what would make a score policy fail: treating a
  correlated positive closeout flow as independent calibration evidence.
- Ousterhout's lens keeps the evidence seam narrow: state facts stay in the
  ledger, while future policy comparison remains a separate concern.

## Sibling Search

- agent-operational scoring prompts: `docs/development.md` score authoring
  guidance | decision: valid follow-up outside this goal | proof: this run
  misattributed the scorer role before correction | follow-up: deferred
  charness-artifacts/goals/2026-08-12-compare-score-policy-evidence.md.

## Next Improvements

- workflow: state at first score prompt that the agent, not the user, records
  observed operational impact (recurrence-class: agent-authored-score-role).
- capability: compare naturally varied scores across sessions before proposing
  a budget or score formula.
- memory: retain the no-policy rationale and required comparative inputs in the
  successor goal and critique artifact.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-12-first-score-cohort-retro.md
