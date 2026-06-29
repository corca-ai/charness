# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Pinned next task: the skill-planner-uniformity program (locked intent) —
  [spec](../charness-artifacts/spec/2026-06-29-skill-planner-uniformity.md).**
  Items (1) matcher fix and (2) envelope unification are **LANDED**; item
  **(3) capture-prioritized rollout** is **in progress** — `hitl` is now
  live-capture PROVEN (no planner needed). START HERE: next skill in the sweep.

## Current State

- **`hitl` claim-fidelity PROVEN (item 3, first capture).** A real `/charness:hitl`
  run at HEAD opened `references/chunk-contract.md` and authored bounded chunks
  against it; `cautilus evaluate observation` → `passed`, stable. Unlike retro,
  hitl did NOT show the passive-pointer failure shape (its step-5 summary defers
  to the doc as authority and the run followed it), so hitl correctly needs NO
  planner. Proof: [`charness-artifacts/cautilus/hitl-claim-fidelity-2026-06-29/`](../charness-artifacts/cautilus/hitl-claim-fidelity-2026-06-29/);
  `thresholds.max_duration_ms` set to 240000 from the 101982ms passing baseline.
- **Items 1+2 LANDED** (prior session). Item 2: one canonical envelope
  `charness.run_plan_envelope.v1` (lib [`run_plan_envelope.py`](../skills/shared/scripts/run_plan_envelope.py),
  contract [run-plan-envelope.md](../skills/shared/references/run-plan-envelope.md)); all 7 planners emit it
  with uniform `{required_reads, next_action(dict w/ kind), gate_packets}`; the
  conditional planner standard is baked into `create-skill`. Item 1: matcher
  counts Bash file reads (`parseReadCommandBasenames`).

## Next Session

1. **Capture-prioritized rollout (item 3, continue):** `hitl` is DONE (proven, no
   planner). Pick the next skill to capture (ask-before-run, one at a time): both
   planner-absent skills are now captured, so the remaining ~17 uncaptured public
   skills carry HYPOTHESIS floors — each needs one live capture to flip it. If a
   capture confirms a passive-pointer shape, give that skill a planner using the
   canonical envelope (linear skills use `build_linear_envelope`, never fabricated
   branches). Add a branch fixture only where a single prompt can't honestly
   evaluate the skill. The `--justification-log` override (operator request) is the
   door past the planner's `next_action: none`; mirror the hitl/retro capture path.
2. Secondary: support-skill tier; quality pilot #397 runtime proof. Each new
   floor stays a live-capture HYPOTHESIS until one capture proves it. Re-derive
   quality's `max_duration_ms` (now a provisional 600000) from its first PASSING
   capture per the threshold decision below.

## Discuss

- Threshold policy — RESOLVED 2026-06-29: `max_duration_ms` is set per-skill from
  that skill's own PASSING capture (~2x headroom, the retro model), not a shared
  cap. Recorded in the [methodology spec](../charness-artifacts/spec/2026-06-23-skill-claim-fidelity-doc-philosophy.md).

## References

- [planner-uniformity locked intent](../charness-artifacts/spec/2026-06-29-skill-planner-uniformity.md) ·
  [methodology spec](../charness-artifacts/spec/2026-06-23-skill-claim-fidelity-doc-philosophy.md)
- proofs: [hitl](../charness-artifacts/cautilus/hitl-claim-fidelity-2026-06-29/) ·
  [retro](../charness-artifacts/cautilus/retro-claim-fidelity-2026-06-29-recapture/) ·
  [cautilus latest](../charness-artifacts/cautilus/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
