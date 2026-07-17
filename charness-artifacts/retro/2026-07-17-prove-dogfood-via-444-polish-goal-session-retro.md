# prove-dogfood-via-444-polish goal session retro
Date: 2026-07-17

## Mode

session

## Context

Autonomous pickup ("리포 자율 개선") ran the handoff chunker over the live
backlog, merged handoff entries 1+3 into one goal
(`charness-artifacts/goals/2026-07-17-prove-dogfood-via-444-polish.md`), and
executed it end-to-end: the #444 deferred F5/F6 polish landed as commit
`963e147c`, and the prove dogfood row was promoted to `reviewed` on live
consumer-run evidence as commit `b1b74e0c`. This retro is the achieve
After-phase efficiency review for that goal.

## Evidence Summary

- Slice 1: 3 files, 33 focused tests green, live CLI demo of both failure
  paths, locked closeout with focused mutation-coverage producer.
- Slice 2: 5 files, `validate_public_skill_dogfood` green (20 cases, 20
  required), locked closeout rerun green after the drift-pin addition.
- Two bounded-reviewer fresh-eye passes (plan: ac87480d048c93622, slice 1:
  aed11f4ced72e56b9) plus one promotion review (a4cd9fa1bd39a3287); all three
  wrapped in boundary-fingerprint snapshot/verify with `drift: []`.
- Host log probe: `charness-artifacts/goals/2026-07-17-prove-dogfood-via-444-polish-host-log-probe.json`.

## Waste

One broad locked closeout run was spent early: the slice-2 locked closeout was
launched in parallel with the slice-2 fresh-eye review, and the review's
drift-guard finding forced a test addition that invalidated the just-produced
broad proof (one full rerun, ~3 minutes). The discipline order
(critique-then-lock, docs/conventions/implementation-discipline.md) already
names this; the parallelization was a deliberate gamble that lost.

## Critical Decisions

- Pairing the prove dogfood run with the #444 polish (chunker merge) rather
  than a synthetic slice — made the promotion evidence observe genuine work.
- Plan critique's demand to add `PROMPT_HINTS["prove"]` before promotion —
  without it the row's "routes the prompt" evidence would have recorded a
  description-fallback prompt as a routing observation.
- Applying the md-list drift guard same-slice instead of filing an issue —
  kept external writes out of an autonomous session and retired a
  demonstrated drift class for 11 lines.

## Expert Counterfactuals

- A Weinberg-style consumer-boundary lens applied at the original dogfood
  scaffolding would have caught the description-fallback prompt months
  earlier: the scaffold silently reuses producer metadata (frontmatter
  description) as consumer input whenever `PROMPT_HINTS` lacks an entry, so
  every future public skill lands with an unrealistic prompt until someone
  notices. The next `create-skill` addition will hit the same fallback.

## Sibling Search

- axis: scaffold fallback reuse | location: scripts/public_skill_dogfood_lib.py
  `build_matrix` prompt fallback | decision: valid follow-up outside the slice |
  proof: static scan only (PROMPT_HINTS lacks entries only for `prove` before
  this goal; all other public skills have hints) | follow-up: deferred to the
  handoff Discuss note on new-skill dogfood scaffolding.

## Next Improvements

- workflow: keep critique strictly before the locked closeout even when the
  parallel gamble looks cheap; the loss mode (invalidated broad proof) costs
  more than the wait.
- capability: consider a scaffold-time warning when a dogfood row's prompt
  equals the skill description (fallback in use), so the next new skill does
  not inherit an unrealistic consumer prompt silently.
- memory: bounded-reviewer synchronous spawns returned results inline this
  session (no polling needed), unlike the 2026-07-16 session; treat the
  polling lesson as host-version-dependent rather than permanent.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-17-prove-dogfood-via-444-polish-goal-session-retro.md
