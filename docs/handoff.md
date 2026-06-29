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
- **dup-ratchet GREEN + capture git-hook friction fixed (this session):**
  capture-skill-run.sh now neutralizes hooks to an empty dir; the red dup-ratchet
  (17+2 families) resolved via 1 extraction + honest intentional classifications.
  **Portability finding:** `fae23` (debug↔retro adapter echo) was classified
  "intentional/portability" but the experiment FALSIFIED that — it was reducible into
  the already-shared `run_plan_envelope.py` (byte-identical output, portability
  intact, now extracted). So SOME "intentional" notes are over-applied.
  [hooks+dup critique](../charness-artifacts/critique/2026-06-30-capture-hooks-and-dup-ratchet-critique.md)
- **Efficiency — outcome grader COMPLETE + LIVE-PROVEN** (prior session): auto-grade
  wired into the A/B harness (`run_ab` grades each bundle; `--judge-cmd` /
  `--keep-untracked-outputs`; `validate_outcome_assertions.py`). hitl + retro A/B live.

## Next Session

1. **Aggressive dup-review portability audit (NEW, user-requested):** the `fae23`
   experiment proved some "intentional/portability" classifications hide reducible
   dups. Mechanism: `run_plan_envelope.py` is ALREADY a universal planner dependency,
   so "would add coupling" is FALSE for anything that can live there. Falsification-
   test EVERY intentional family (start with `1029`, `32e8` — debug/retro/4-planner
   blocks): try the reduction; keep if behavior-neutral + portability-intact, else
   keep the note now VERIFIED (not assumed). Review ALL families, be aggressive.
2. **Correctness sweep (continue, ask-before-run):** capture the next hypothesis-floor
   skill, one at a time. A miss = skill-shape signal (re-pin / re-classify / planner),
   never soften the matcher; do NOT planner-ize mechanically. `--justification-log`
   overrides `next_action: none`; mirror the hitl/retro/quality path. The outcome-grade
   surface is live, so a captured skill can also get an outcome assertion set
   (only hitl has one) — add per-eval as you capture, not speculatively.
3. **Light doctrine (cheap):** `floor-addition-restraint:` ledger harvester;
   output-minimalism rule ("code first; delete the explanation if it outruns code").

## Discuss

- Threshold policy RESOLVED: per-skill `max_duration_ms` from a PASSING capture (~2x).
  Open: promote trace-digest to a REQUIRED floor after deciding how to treat the
  transcript-less retro bundles.

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [quality latest](../charness-artifacts/quality/latest.md)
- proofs: [cautilus latest](../charness-artifacts/cautilus/latest.md) · [hitl](../charness-artifacts/cautilus/hitl-claim-fidelity-2026-06-29/) · [retro](../charness-artifacts/cautilus/retro-claim-fidelity-2026-06-29-recapture/)
