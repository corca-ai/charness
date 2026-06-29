# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Pinned next task: the skill-planner-uniformity program (locked intent) —
  [spec](../charness-artifacts/spec/2026-06-29-skill-planner-uniformity.md).**
  Items (1) matcher fix and (2) envelope unification are **LANDED**; the live
  work is now **(3) capture-prioritized rollout** (START HERE).

## Current State

- **Item 2 (planner envelope unification) LANDED this session.** One canonical
  envelope `charness.run_plan_envelope.v1` with shared builders + `build_envelope`
  validator in [`skills/shared/scripts/run_plan_envelope.py`](../skills/shared/scripts/run_plan_envelope.py)
  (contract: [run-plan-envelope.md](../skills/shared/references/run-plan-envelope.md)).
  All 7 planners (debug/gather/handoff/issue/quality/release/retro) emit it; the
  minimal vocab `{required_reads, next_action, gate_packets}` is uniform and
  `next_action` is now ALWAYS a dict with `kind` (was a bare string in
  quality/issue). Per-skill `schema_version` and extensions are unchanged. The
  well-formedness standard ("a skill ships a planner") is baked into `create-skill`.
- Item 1 (matcher counts Bash file reads via `parseReadCommandBasenames`) remains
  landed; the floor is unaffected.

## Next Session

1. **Capture-prioritized rollout (item 3, START HERE):** capture `hitl` first
   (ask-before-run, one at a time); if a passive-pointer shape is confirmed, give
   it a planner using the canonical envelope (linear skills use
   `build_linear_envelope`, never fabricated branches). Add a branch fixture only
   where a single prompt can't honestly evaluate the skill.
2. Secondary: support-skill tier; quality pilot #397 runtime proof. Each new
   floor stays a live-capture HYPOTHESIS until one capture proves it.

## Discuss

- Threshold policy: retro set `max_duration_ms` from its own pass baseline
  (420000); the quality pilot used the 600000 cap. Per-skill-from-real-run vs a
  shared cap.

## References

- [planner-uniformity locked intent](../charness-artifacts/spec/2026-06-29-skill-planner-uniformity.md)
- [methodology spec (lens 9 + Live-Capture Lesson)](../charness-artifacts/spec/2026-06-23-skill-claim-fidelity-doc-philosophy.md)
- [retro pilot proof](../charness-artifacts/cautilus/retro-claim-fidelity-2026-06-29-recapture/) + [cautilus latest](../charness-artifacts/cautilus/latest.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
