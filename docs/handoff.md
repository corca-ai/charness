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
- **Efficiency — outcome grader: COMPLETE + LIVE-PROVEN (this session).** Auto-grade is now
  WIRED into the A/B harness ([skill_outcome_wiring.py](../scripts/skill_outcome_wiring.py)):
  `run_ab` grades each preserved bundle and folds a per-arm Outcome-grade section into
  `report.md`; `--judge-cmd`/`--keep-untracked-outputs` added; durable validator
  ([validate_outcome_assertions.py](../scripts/validate_outcome_assertions.py), in the
  claim-fidelity-specs surface). Live: hitl auto-graded in-harness with the judge (3/3
  judge PASS, deterministic floor-miss caught, materialized-queue via keep-untracked) +
  retro variant-A-vs-B (planner extraction ~15–22% leaner, correctness held). Commits
  `f7e5ec73`,`08c15fbf`,`62ac96be`; [hitl finding](../charness-artifacts/efficiency/hitl-outcome-wired/finding.md),
  [retro finding](../charness-artifacts/efficiency/retro-variant-ab/finding.md).
- **Gate hygiene:** `validate_cautilus_diagnostics --all` is GREEN (the two retro
  bundles' `PROOF.md` renamed to the canonical `finding.md`).

## Next Session

1. **Correctness sweep (continue, ask-before-run):** capture the next of
   the 18 hypothesis-floor skills, one at a time. A miss = skill-shape signal
   (re-pin / re-classify / give-a-planner), never soften the matcher; do NOT
   planner-ize mechanically. `--justification-log` is the override past
   `next_action: none`; mirror the hitl/retro path. Re-derive quality's provisional
   `max_duration_ms` (600000) from its first PASSING capture. NOTE: the outcome-grade
   surface is now live, so a captured skill can also get an outcome assertion set
   (only hitl has one) — add per-eval sets here as you capture, not speculatively.
2. **Light doctrine (from ponytail, cheap):** a `floor-addition-restraint:` ledger
   harvester (grep markers -> queryable list, flag ones with no upgrade trigger);
   an output-minimalism rule ("code first; if the explanation outruns the code,
   delete it"); optionally the YAGNI ladder into `impl`.
3. **Small efficiency follow-ups (deferred, cheap):** a file-COUNT cap on the
   gitignored sweep (critique C3 — binary-skip already mitigates the worst case,
   .pyc; no charness skill writes a large text tree under capture yet); a
   check-secrets reminder when `--keep-untracked-outputs` preserves files. Lesson:
   the live run vindicated C3 the counterweight had dropped as "no consumer" — the
   consumer (any captured run emits `.pyc`) was universal.

## Discuss

- Threshold policy — RESOLVED: per-skill `max_duration_ms` from that skill's PASSING
  capture (~2x headroom). Open: promote trace-digest to a REQUIRED floor only after deciding how to treat the transcript-less retro bundles.

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [quality latest](../charness-artifacts/quality/latest.md)
- proofs: [hitl](../charness-artifacts/cautilus/hitl-claim-fidelity-2026-06-29/) ·
  [hitl trace](../charness-artifacts/cautilus/hitl-claim-fidelity-2026-06-29-tracecapture/) ·
  [retro](../charness-artifacts/cautilus/retro-claim-fidelity-2026-06-29-recapture/) ·
  [cautilus latest](../charness-artifacts/cautilus/latest.md)
