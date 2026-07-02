# handoff AMBIGUOUS-pickup claim-fidelity — 2026-07-02 (reference-compaction Slice 7, #412 / #410)

## Verdict

**The AMBIGUOUS arm of the conditionalized pickup planner is PROVEN falsifiable.**
A faithful ambiguous `/charness:handoff` pickup OPENS both `workflow-trigger.md`
AND `continuation-sequence.md` — so `continuation-sequence.md` is genuinely
load-bearing under the ambiguous condition (on-demand DEPTH), not INLINE.

## Why this capture exists (per-condition falsifiable design)

Slice 3 conditionalized `plan_handoff_run.py` so pickup emits
`continuation-sequence.md` ONLY when the pickup is ambiguous. That created two
distinct pickup CONDITIONS, each needing its own falsifiable fixture:

- CLEAR pickup (`pickup.spec.json`): one clearly-pinned task → planner requires only
  `workflow-trigger.md`. Re-baselined from the existing Slice-7 capture (it opened
  `workflow-trigger.md`, skipped `continuation-sequence.md`) → PASSES `RCF=[workflow-trigger.md]`.
- AMBIGUOUS pickup (`pickup-ambiguous.spec.json`, THIS capture): generic resume + a
  task directive to bypass the chunker, no pinned task, ≥2 plausible pickups →
  planner requires BOTH docs.

## What ran

Operator-authorized ask-before-run capture at commit `c1a66f4d` (conditional planner),
prompt = the pickup-ambiguous fixture. The run resolved intent=**pickup** (not
chunked_routing), Read=37 / Bash=25, ~12min.

## The proof (floor PASS, falsifiable)

- `observed.ambiguous-PASSED.v1.json`: **outcome=passed**, coverage 2/6 — the run
  OPENED both `workflow-trigger.md` and `continuation-sequence.md`, satisfying
  `requiredCommandFragments=[workflow-trigger.md, continuation-sequence.md]`.
- FALSIFIABLE: an ambiguous pickup that skipped `continuation-sequence.md` would
  MISS the floor (a genuine fail) — the opposite direction from the clear arm.

## Both conditions now covered

| condition | fixture | floor | evidence |
| --- | --- | --- | --- |
| clear pickup | pickup.spec.json | RCF=[workflow-trigger.md] | Slice-7 capture (re-graded PASS) |
| ambiguous pickup | pickup-ambiguous.spec.json | RCF=[workflow-trigger.md, continuation-sequence.md] | THIS capture (PASS) |

Together they prove the planner's conditional emission in both directions and make
`continuation-sequence.md` an honestly-classified on-demand DEPTH reference.

## Non-Claims

- n=1 per arm: the ambiguous floor is PROVEN falsifiable at a single sample, not a
  stability proof.
- The clear-pickup arm's PASS is a re-grade of the existing Slice-7 capture, not a
  fresh run.
- Not a matcher softening: the planner's conditional emission is the mechanism; the
  fix was a per-condition fixture split, never a relaxed matcher.

## Bundle

- `observed.ambiguous-PASSED.v1.json` — the passing grade (both docs opened).
- `transcript-closeout.txt` — the ambiguous pickup closeout.
- `justification.md` — operator authorization + purpose.
