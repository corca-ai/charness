# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Pinned next task: continue live captures on the provisional floors — start by
  capturing `hitl`.** Per live-capture-before-assert: capture FIRST, then apply
  lens 9 (give-it-a-planner, mirroring the retro pilot) ONLY if the capture reveals
  a passive-pointer shape. hitl is a flagged candidate (script-resolution RCF
  `43d066a9`; named by retro's Sibling Search) but it ships briefing scripts
  (`check_review_state.py`), so do NOT assume the retro defect — confirm by capture.
  Loop: `plan_cautilus_proof.py` -> `run_cautilus_eval.py` (ask-before-run, one at
  a time).

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

1. **Capture `hitl`** (see Workflow Trigger): ONE authorized live capture FIRST;
   only if it reveals a passive-pointer shape, mirror the retro pilot
   (`plan_hitl_run.py` -> planner-first SKILL.md -> sync -> validators ->
   fresh-eye critique -> commit -> re-capture to prove).
2. Continue live captures on the remaining provisional floors under the new
   methodology, one ask-before-run at a time; apply lens 9 only where a capture
   reveals the shape.
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
