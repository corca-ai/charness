# Session Retro
Date: 2026-07-02

## Mode

session

## Context

Reviewing the achieve goal
`charness-artifacts/goals/2026-07-02-issue-410-411-412-413-reference-compaction-slice-7-per-condition-claim-fidelity-fl.md`
— the setup (#413) + handoff (#412) per-condition claim-fidelity floor redesign,
part of the reference-compaction Slice-7 sweep (#410). The session ran the full
pickup → find-skills → handoff chunker → goal → 6 slice-commits path and closed
out internally (external issue-close + push operator-gated).

## Evidence Summary

- 6 commits `69552811..551a1f49`: shape+activate, setup instrument, setup vocab,
  setup floor flip (RCF→RSF), handoff planner conditional, handoff pickup
  per-condition fixtures.
- 2 live operator-authorized ask-before-run captures (`claude -p`, abs out-dir
  outside repo): setup normalization + handoff ambiguous pickup. Both graded
  old-floor-FAIL / new-floor-PASS side by side.
- 4 fresh-eye subagent critiques (plan + Slice 1/2b/3/4): all SOUND, no #410
  softening, no blockers.
- Broad pytest 3981 passed (run per slice); `grade_skill_outcome` selftest
  good=1.0/bad=0.0; registry validation 47 passed.

## Waste

- **Edited the generated mirror, not the source.** First setup `## Closeout
  Vocabulary` edit went to `plugins/charness/skills/setup/SKILL.md` (the export)
  instead of `skills/public/setup/SKILL.md` (the source). Caught before commit,
  redone on source + synced. Guarded going forward by the staged-mirror-drift
  gate, so bounded.
- **Under-scoped the per-condition falsifiability discipline until corrected.**
  I initially recommended deferring the ambiguous-pickup fixture (option A) —
  which would have shipped the conditionalized planner while proving only the
  clear arm. The operator caught it ("각 조건별 반증 가능한 픽스처"). The correction
  cost one clarification round but prevented a half-verified floor.

## Critical Decisions

- **Capture-before-pin held throughout.** setup's RSF token and the handoff
  ambiguous floor were OBSERVED from live captures, never assumed (the impl
  Slice-5 lesson). This is why the fresh-eye critiques could confirm honesty.
- **Per-condition falsifiable fixtures (operator-directed).** Slice 4 split the
  pickup floor into clear + ambiguous arms, each failing in the opposite
  direction — the decision that made #412 an honest re-baseline rather than a
  planner-only patch.
- **Internal-closeout-only.** Issue-close (#412/#413) + push left operator-gated;
  the goal completes with those lanes dispositioned, not falsely claimed.

## Expert Counterfactuals

- **Engelbart (system-improving-itself): treat (H + LAM + T) as one unit; design
  T alongside LAM.** I changed the *method/language* (LAM: the planner now emits
  continuation-sequence.md only when ambiguous) but initially proposed deferring
  the *tool* (T: the fixture that verifies the new ambiguous condition). Engelbart
  says the tool and the method co-evolve as one unit — a method change that splits
  behavior into a new condition is not "done" until the tool that exercises that
  condition ships with it. Applying the lens: the ambiguous-pickup fixture had to
  ship in the SAME slice as the conditional planner. The operator's correction
  restored the unit; the lens would have caught it up front.

## Sibling Search

- axis: other condition-keyed planners/matchers in this session's surface | location: `skills/public/handoff/scripts/plan_handoff_run.py` intent-keyed reads (chunked_routing/pickup/refresh) | decision: valid follow-up outside the slice | proof: only the pickup intent was newly split (clear/ambiguous); refresh + chunked_routing remain single-condition scenarios, and the other reference-compaction skills' floor conditions are already tracked under the #410 sweep | follow-up: deferred to #410 (no NEW untracked sibling introduced this session)

## Next Improvements

- workflow: when a change SPLITS behavior into a new condition/branch, design a
  falsifiable fixture for EACH branch in the same slice — never defer a branch's
  proof. (Applied in Slice 4.)
- capability: a validator that cross-checks each planner's intent/condition-keyed
  required-reads against the scenario specs, flagging any conditionally-required
  doc that NO scenario forces — this would auto-detect the ambiguous-fixture gap
  the operator caught by hand.
- memory: this retro + the goal artifact record the per-condition-falsifiability
  discipline and capture-before-pin; carried to the next-session handoff.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-02-session-retro.md
