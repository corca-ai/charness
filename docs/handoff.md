# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Big picture:** skills satisfy two axes and evals verify each SEPARATELY —
  **correctness** (claim-fidelity: does a run honor its claim? pass/fail, proven by
  live capture) and **efficiency** (process + output waste; advisory/degrade, never
  pass/fail). Order agreed 2026-06-29 — see Next Session.

## Current State

- **Correctness:** planner-uniformity items 1 (matcher) + 2 (canonical envelope
  `charness.run_plan_envelope.v1`, all 7 planners) LANDED. Live captures PROVEN
  **2/20**: retro (planner-fixed) + hitl (no planner needed). 18 floors stay
  HYPOTHESES until each gets one capture. [planner-uniformity spec](../charness-artifacts/spec/2026-06-29-skill-planner-uniformity.md).
- **Efficiency:** **A/B harness** + **outcome grader** LANDED. A/B runs n>1 per-ref arms
  behind an offline `--selftest` gate ([run_skill_efficiency_ab.py](../scripts/run_skill_efficiency_ab.py)).
  Outcome grader ([grade_skill_outcome.py](../scripts/grade_skill_outcome.py)) is **3-live PROVEN** —
  output+transcript preservation + a live `claude -p` judge scored a fresh hitl capture 5/6, all 3
  judge-kind PASS with cited evidence ([finding](../charness-artifacts/efficiency/hitl-outcome-live/finding.md), [methodology spec](../charness-artifacts/spec/2026-06-23-skill-claim-fidelity-doc-philosophy.md)).
- **Gate hygiene:** `validate_cautilus_diagnostics --all` is GREEN (the two retro
  bundles' `PROOF.md` renamed to the canonical `finding.md`).

## Next Session

1. **Efficiency — outcome grader: (4) wire into A/B report + (a) clean re-run (both remain).**
   Outcome layer is built + 3-live proven (Current State); remaining, in order: (4) auto-grade
   per arm inside [run_skill_efficiency_ab.py](../scripts/run_skill_efficiency_ab.py) and fold the
   verdict into the report; a `--keep-untracked-outputs` for gitignored-runtime skills (hitl's queue
   is gitignored, so `output_*` can't grade it — the transcript carried the judge); a durable
   validator surface for [outcome-assertions.json](../evals/cautilus/hitl-claim-fidelity/outcome-assertions.json)
   (conformance test only today); more per-eval assertion sets (only hitl exists). (a) clean
   variant-A-vs-B efficiency re-run (retro pre/post
   `plan_retro_run.py`; routing cancels), ask-before-run. Detail: methodology spec.
2. **Correctness sweep (item 3, continue, ask-before-run):** capture the next of
   the 18 hypothesis-floor skills, one at a time. A miss = skill-shape signal
   (re-pin / re-classify / give-a-planner), never soften the matcher; do NOT
   planner-ize mechanically. `--justification-log` is the override past
   `next_action: none`; mirror the hitl/retro path. Re-derive quality's provisional
   `max_duration_ms` (600000) from its first PASSING capture.
3. **Light doctrine (from ponytail, cheap):** a `floor-addition-restraint:` ledger
   harvester (grep markers -> queryable list, flag ones with no upgrade trigger);
   an output-minimalism rule ("code first; if the explanation outruns the code,
   delete it"); optionally the YAGNI ladder into `impl`.

## Discuss

- Threshold policy — RESOLVED: per-skill `max_duration_ms` from that skill's PASSING
  capture (~2x headroom). Open: promote trace-digest to a REQUIRED floor only after deciding how to treat the transcript-less retro bundles.

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [quality latest](../charness-artifacts/quality/latest.md)
- proofs: [hitl](../charness-artifacts/cautilus/hitl-claim-fidelity-2026-06-29/) ·
  [hitl trace](../charness-artifacts/cautilus/hitl-claim-fidelity-2026-06-29-tracecapture/) ·
  [retro](../charness-artifacts/cautilus/retro-claim-fidelity-2026-06-29-recapture/) ·
  [cautilus latest](../charness-artifacts/cautilus/latest.md)
