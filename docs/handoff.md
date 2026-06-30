# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Big picture:** skills satisfy two axes, evals verify each SEPARATELY —
  **correctness** (claim-fidelity: does a run honor its claim? pass/fail, proven by
  live capture) and **efficiency** (process + output waste; advisory/degrade, never
  pass/fail).

## Current State

- **Correctness:** planner-uniformity items 1 (matcher) + 2 (canonical envelope,
  all 7 planners) LANDED. Live captures PROVEN **3/20**: retro + hitl + **quality**
  (n=2; cautilus skill_task_fidelity PASS, degraded only on runtime_budget). ~16
  floors stay HYPOTHESES. quality surfaced + fixed a matcher false-negative on
  for-loop batch reads (`expandForLoopReadCommands`; sharpening, not softening);
  `max_duration_ms` stays provisional 600000 (captures hit the cap on a red
  dup-ratchet + git-hook rabbit-hole).
  [spec](../charness-artifacts/spec/2026-06-29-skill-planner-uniformity.md) · [quality finding](../charness-artifacts/cautilus/quality-claim-fidelity-2026-06-29/finding.md)
- **debug capture (2026-06-30) = MISS (informative):** competent structural RCA
  (exemplary Detection Gap + Sibling Search) but skipped its own `five-steps` +
  `debug-memory` floor refs. `five-whys-causal-chain.md` RE-PINNED out (planner
  routes it on_demand; a good run reached the structural outcome without it). debug
  stays HYPOTHESIS. [finding](../charness-artifacts/cautilus/debug-claim-fidelity-2026-06-30/finding.md)
- **dup-ratchet GREEN + capture git-hook friction fixed:** capture-skill-run.sh
  neutralizes hooks to an empty dir; the `fae23` portability finding seeded the full
  audit (Next Session 1).
  [hooks+dup critique](../charness-artifacts/critique/2026-06-30-capture-hooks-and-dup-ratchet-critique.md)
- **Efficiency — outcome grader COMPLETE + LIVE-PROVEN** (prior session): auto-grade
  wired into the A/B harness (`run_ab` grades each bundle; `--judge-cmd` /
  `--keep-untracked-outputs`; `validate_outcome_assertions.py`). hitl + retro A/B live.

## Next Session

1. **debug follow-ups — START HERE (sharpens #2).** Author a debug OUTCOME-ASSERTION set
   (protect the structural intent by SUBSTANCE — real Detection Gap / Sibling Search /
   Prevention content, not doc-opening, a weak proxy); fix `continue-existing-artifact`
   mis-fire for fresh bugs; re-capture debug to attempt a PASS. **Why first:** landing the
   outcome-assertion pattern on one worked skill lets the #2 sweep REUSE it per-eval
   instead of reinventing it skill-by-skill.
2. **Correctness sweep (ask-before-run):** capture the next hypothesis-floor skill, one at a
   time. A miss = skill-shape signal (re-pin / re-classify / planner), never soften the
   matcher; do NOT planner-ize mechanically. `--justification-log` overrides
   `next_action: none`; mirror the hitl/retro/quality path. Add an outcome-assertion set
   per-eval as you capture (the #3 pattern; only hitl has one), not speculatively.
3. **Dup leg — RECORDED / closed.** Audit (25 families) + 3 extractions landed (resolver
   tail 16 skills → `run_adapter_cli`, dogfood `format_human`, tool-rec payload), all
   behavior-neutral proven; 6 deferred as OPTIONAL behavior-equivalence refactors (not
   blocking) — [VERIFIED table](../charness-artifacts/quality/2026-06-30-dup-portability-falsification-audit.md).
   Lesson: a "fixable" verdict still needs hands-on byte-identical proof before it lands.

## Discuss

- Threshold policy RESOLVED: per-skill `max_duration_ms` from a PASSING capture (~2x).
  Open: promote trace-digest to a REQUIRED floor after deciding how to treat the
  transcript-less retro bundles.

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [quality latest](../charness-artifacts/quality/latest.md)
- proofs: [cautilus latest](../charness-artifacts/cautilus/latest.md) · [hitl](../charness-artifacts/cautilus/hitl-claim-fidelity-2026-06-29/) · [retro](../charness-artifacts/cautilus/retro-claim-fidelity-2026-06-29-recapture/)
