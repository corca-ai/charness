# handoff claim-fidelity capture — 2026-07-01 (reference-compaction Slice 7)

## Verdict

**#410's handoff RCF-drops are MOSTLY REFUTED; the honest slice is the
document-seams.md DUP deletion + three PROVEN floors + one planner finding.** All
three handoff scenarios were captured live (their RCF is planner-derived from
`plan_handoff_run.py`). Result: workflow-trigger.md, state-selection.md, and
spill-targets.md are all load-bearing (opened) — so #410's "drop the pickup/refresh
docs → RSF" does NOT apply. Only continuation-sequence.md is questionable, and that
is a PLANNER over-requirement, not a spec move.

## What ran (the three scenario captures)

| scenario | RCF | outcome | coverage | verdict |
|---|---|---|---|---|
| default (chunked_routing) | `[chunked-routing.md]` | passed | 1/7 | opened chunked-routing.md → **PROVEN** |
| refresh | `[state-selection.md, spill-targets.md]` | passed | 2/7 | opened **BOTH** → **PROVEN**, #410 drop REFUTED |
| pickup | `[workflow-trigger.md, continuation-sequence.md]` | failed | 1/7 | opened workflow-trigger.md (PROVEN); continuation-sequence.md NOT opened |

(default: `HEAD`=73e8ec14, 325663ms; refresh: 273120ms; pickup: 209413ms.)

The pickup run was notably on-point: it read `workflow-trigger.md`, resumed THIS
sweep, noticed the handoff doc was stale (written at 73e8ec14, before the
gather/hotl commits), and prepped the next slice — a faithful pickup that simply
didn't need continuation-sequence.md.

## The pickup finding (planner over-requirement, filed follow-up)

`continuation-sequence.md` is for "when several plausible pickups exist" (SKILL.md).
The captured pickup was unambiguous (one clear pinned task), so the run correctly
skipped it. But `plan_handoff_run.py` emits `continuation-sequence.md` as a pickup
`_required_read` **unconditionally** (verified:
`plan_handoff_run.py --intent pickup` → required_reads include
continuation-sequence.md). So the pickup spec RCF faithfully mirrors the planner,
and the eval CORRECTLY flags the gap. The fix is at the PLANNER (make
continuation-sequence.md conditional on pickup ambiguity, aligning with the skill's
own guidance), not the spec — the RCF is KEPT planner-faithful, never softened.
The pickup scenario's floor legitimately fails until the planner is fixed
(filed follow-up).

## Changes landed

- **document-seams.md DELETED** (handoff's copy only): DUP — its "default to
  docs/handoff.md, override via adapter" rule is inlined in SKILL.md Bootstrap, and
  it was opened by NONE of the three scenario runs. Removed from all 3 specs'
  declaredReferences, the SKILL.md `## References` bullet, the plugin mirror, and
  the find-skills inventory. (debug/ and gather/ keep their own separate copies —
  out of #410 scope.)
- **thresholds.max_duration_ms** set from the passing baselines: default 660000
  (325663ms), refresh 550000 (273120ms). pickup gets none (its floor legitimately
  fails until the planner fix).
- **_comment** on all 3 specs records the captures + the #410-refutation.
- **No RCF→RSF token move** (correctly — all kept RCF docs are load-bearing planner
  reads, not wastefully re-read enums).
