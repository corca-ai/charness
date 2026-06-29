# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Pinned next task: the skill-planner-uniformity program (locked intent) —
  [spec](../charness-artifacts/spec/2026-06-29-skill-planner-uniformity.md).**
  Sequence: **(1) LANDED** — the matcher now counts Bash file reads
  (`parseReadCommandBasenames` in `build-skill-execution-observation.mjs`);
  **(2) START HERE** unify the 6 existing planners + retro into ONE canonical
  envelope + shared lib + minimal vocab (`required_reads`/`next_action`/
  `gate_packets`) BEFORE any rollout; **(3)** capture-prioritized rollout (capture
  `hitl` first; add a branch fixture only where the default prompt can't evaluate
  the skill). Guardrail: envelope before more planners; do not planner-ize 14
  skills mechanically.

## Current State

- **retro pilot COMPLETE and proven** (commits `a7e49790`..`3310fcdf`): the first
  live capture FAILED retro's floor (planner-absent; `expert-lens.md` skipped, the
  Engelbart lens missed) -> extracted `plan_retro_run.py` (planner-first) ->
  re-capture flipped it failed->proven (Engelbart lens now applied) -> methodology
  updated.
- **The sweep is now in its LIVE-CAPTURE phase** under the updated methodology
  (lens 9 + live-capture-before-assert): a statically-calibrated floor is a
  HYPOTHESIS until one capture proves it; the 19 remaining floors are provisional.
  A miss is a skill-shape signal (re-pin / re-classify / give-it-a-planner), never
  a matcher to soften.
- **Planner landscape (corrected):** only 6 of 20 public skills ship a `plan_*.py`
  planner (debug/gather/handoff/issue/quality/release); 14 derive RCF via
  script-resolution, several with planner-EQUIVALENT briefing scripts. lens 9 is
  per-skill where a capture reveals the shape — not "planner-ize all 14".

## Next Session

1. ~~Matcher fix (item 1)~~ **LANDED**: `parseReadCommandBasenames` counts Bash
   `cat|sed|head|tail|less|nl|rg|grep|awk` reads toward coverage, dropping
   grep/rg/awk/sed pattern operands (named-in-pattern != opened). Re-tally verified:
   failed capture 0/9 → 1/9 (`expert-lens.md` still missing, outcome still failed),
   passed re-capture 4/9 unchanged. Floor unaffected.
2. **Planner envelope unification** (item 2, the real structural work — START
   HERE): one canonical envelope, shared lib, and minimal vocab across all 7
   planners (the 6 existing plus retro); linear skills get a minimal required_reads
   emitter; then bake into `create-skill`. First read all 7 plan_*.py to map the
   divergent schemas.
3. **Capture-prioritized rollout** (item 3): capture `hitl` first (ask-before-run,
   one at a time); fix with the unified planner only if a passive-pointer shape is
   confirmed; add a branch fixture only where a single prompt can't evaluate the
   skill. Secondary: support-skill tier; quality pilot #397 runtime proof.

## Discuss

- Threshold policy: retro set `max_duration_ms` from its own pass baseline
  (420000); the quality pilot used the 600000 cap. Per-skill-from-real-run vs a
  shared cap.

## References

- [planner-uniformity locked intent (next program)](../charness-artifacts/spec/2026-06-29-skill-planner-uniformity.md)
- [methodology spec (lens 9 + Live-Capture Lesson)](../charness-artifacts/spec/2026-06-23-skill-claim-fidelity-doc-philosophy.md)
- [retro pilot proof](../charness-artifacts/cautilus/retro-claim-fidelity-2026-06-29-recapture/) + [cautilus latest](../charness-artifacts/cautilus/latest.md)
- [retro planner to mirror for hitl](../skills/public/retro/scripts/plan_retro_run.py)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
