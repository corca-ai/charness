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
- **Efficiency:** trace lane LANDED this session — `build-skill-execution-observation.mjs`
  emits a durable per-call trace digest into each bundle + an advisory waste lens; the
  diagnostics validator recognizes it. First real trace (hitl re-capture) surfaced
  a find-flail + state churn (n=1, directional only). [methodology spec](../charness-artifacts/spec/2026-06-23-skill-claim-fidelity-doc-philosophy.md).
- **Gate hygiene:** `validate_cautilus_diagnostics --all` is GREEN (the two retro
  bundles' `PROOF.md` renamed to the canonical `finding.md`).

## Next Session

1. **Efficiency A/B harness (n>1) — START HERE, biggest leverage.** Today every
   efficiency/improvement claim is an n=1 anecdote. Build an `evals/` A/B: baseline
   vs skill arms, **isolation** (ponytail hit a baseline-contamination bug),
   **n≥4 with mean/range and honest caveats**, **self-tested instruments**
   (known-bad scores worse than known-good before any spend), an **audited LLM
   judge** (over-build / completeness), and **output-side** metrics (LOC) — not
   just our process-side trace. Reuse `capture-skill-run.sh` and the new trace
   digest. Model: `../ponytail/benchmarks/` (promptfoo plus `agentic/run.py`).
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

- Threshold policy — RESOLVED: `max_duration_ms` per-skill from that skill's own
  PASSING capture (~2x headroom, retro model). Promote trace-digest to a REQUIRED
  bundle floor only after deciding how to treat the transcript-less retro bundles.

## References

- proofs: [hitl](../charness-artifacts/cautilus/hitl-claim-fidelity-2026-06-29/) ·
  [hitl trace](../charness-artifacts/cautilus/hitl-claim-fidelity-2026-06-29-tracecapture/) ·
  [retro](../charness-artifacts/cautilus/retro-claim-fidelity-2026-06-29-recapture/) ·
  [cautilus latest](../charness-artifacts/cautilus/latest.md)
