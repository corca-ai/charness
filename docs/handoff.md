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
- **Efficiency:** trace lane + **A/B harness skeleton** LANDED.
  `build-skill-execution-observation.mjs` emits a durable per-call trace digest +
  advisory waste lens (validator recognizes it). [run_skill_efficiency_ab.py](../scripts/run_skill_efficiency_ab.py)
  runs n>1 isolated per-ref arms, aggregates mean/range, and has an offline
  `--selftest` that refuses unless the extractor ranks a synthetic wasteful run worse
  (PASSED; no API). Live matrix NOT yet run (real spend). [methodology spec](../charness-artifacts/spec/2026-06-23-skill-claim-fidelity-doc-philosophy.md).
- **Gate hygiene:** `validate_cautilus_diagnostics --all` is GREEN (the two retro
  bundles' `PROOF.md` renamed to the canonical `finding.md`).

## Next Session

1. **Efficiency A/B — RUN it + add the judge.** Skeleton + offline self-test
   landed this session. Remaining: (a) **run a live matrix** on a real before/after
   pair — a real token spend (n×arms `claude -p`), ask-before-run; needs a skill
   with an efficiency fix to compare (e.g. the hitl find-flail/state-churn fix,
   itself a separate slice), then run the harness with `--run <config>`.
   (b) **Add the audited LLM judge** (over-build / completeness,
   ponytail-style, self-tested) — deferred this session as the expensive/subjective
   part. Config schema + concrete example: the `run_skill_efficiency_ab.py` docstring.
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
