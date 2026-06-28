# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Pinned next task: give `hitl` a planner (the other planner-absent skill), then
  re-capture.** Mirror the proven retro pilot: extract `plan_hitl_run.py` matching
  the planner family, make SKILL.md planner-first, anchor hitl's claim-fidelity RCF
  to the planner's required_reads, then run ONE live capture to prove the floor
  (ask-before-run: `plan_cautilus_proof.py` -> `run_cautilus_eval.py`). hitl was
  named by the retro re-capture's own Sibling Search.

## Current State

- **retro pilot COMPLETE and proven** (commits `a7e49790`..`3310fcdf`): the first
  live capture FAILED retro's floor (planner-absent; `expert-lens.md` skipped, the
  Engelbart lens missed) -> extracted `plan_retro_run.py` (planner-first) ->
  re-capture flipped it failed->proven (Engelbart lens now applied) -> methodology
  updated.
- **The sweep is now in its LIVE-CAPTURE phase** under the updated methodology
  (lens 9 + live-capture-before-assert): a statically-calibrated floor is a
  HYPOTHESIS until one capture proves it; the 18 remaining floors are provisional.
  A miss is a skill-shape signal (re-pin / re-classify / give-it-a-planner), never
  a matcher to soften.

## Next Session

1. **hitl planner rollout** (see Workflow Trigger): `plan_hitl_run.py` ->
   planner-first SKILL.md -> sync mirror -> validators -> fresh-eye critique ->
   commit -> ONE authorized live capture to prove the floor.
2. After hitl: continue live captures on the remaining single-floor skills under
   the new methodology, one ask-before-run at a time.
3. Secondary: support-skill claim-fidelity tier not started; quality pilot #397
   runtime-consultation proof still open.

## Discuss

- Threshold policy: retro set `max_duration_ms` from its own pass baseline
  (420000); the quality pilot used the 600000 cap. Per-skill-from-real-run vs a
  shared cap.

## References

- [methodology spec (lens 9 + Live-Capture Lesson)](../charness-artifacts/spec/2026-06-23-skill-claim-fidelity-doc-philosophy.md)
- [retro pilot proof](../charness-artifacts/cautilus/retro-claim-fidelity-2026-06-29-recapture/) + [cautilus latest](../charness-artifacts/cautilus/latest.md)
- [retro planner to mirror for hitl](../skills/public/retro/scripts/plan_retro_run.py)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
