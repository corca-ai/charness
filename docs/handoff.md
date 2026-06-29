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
- **Efficiency:** trace lane + **A/B harness** LANDED + first live run done.
  `build-skill-execution-observation.mjs` emits a per-call trace digest + waste lens;
  [run_skill_efficiency_ab.py](../scripts/run_skill_efficiency_ab.py) runs n>1 per-ref
  arms behind an offline `--selftest` gate. First live matrix (hitl n=3) caught a
  CLAUDE.md routing contamination — both arms ran hitl ([bundle](../charness-artifacts/efficiency/hitl-baseline-vs-skill/finding.md), [methodology spec](../charness-artifacts/spec/2026-06-23-skill-claim-fidelity-doc-philosophy.md)).
- **Gate hygiene:** `validate_cautilus_diagnostics --all` is GREEN (the two retro
  bundles' `PROOF.md` renamed to the canonical `finding.md`).

## Next Session

1. **Efficiency A/B — (b) outcome grader through 3-live PROVEN; (4) report wiring + (a) clean re-run remain.**
   [grade_skill_outcome.py](../scripts/grade_skill_outcome.py) grades a capture's OUTCOME vs a per-eval
   assertion set (deterministic + judge-kind) → PASS/FAIL + evidence + weighted pass_rate, behind an offline
   `--selftest` gate. Output+transcript preservation LANDED; the live `claude -p` judge ran end-to-end on a
   fresh hitl capture — 5/6, all 3 judge-kind PASS with cited evidence
   ([finding](../charness-artifacts/efficiency/hitl-outcome-live/finding.md)). Remaining (b): (4) wire the
   grade into the A/B bundle/report (+ `--keep-untracked-outputs` for gitignored-runtime skills); (a) clean
   variant-A-vs-B (retro pre/post planner; routing cancels). Gap: methodology spec.
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
