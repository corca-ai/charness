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
- **debug follow-ups LANDED (2026-06-30):** the outcome-assertion PATTERN is
  authored + PROVEN to discriminate substance (re-capture `pass_rate 0.8`: Detection
  Gap / Sibling Search / Prevention PASS, `falsifiable-hypothesis` FAIL = a real
  static-only-RCA gap). The planner resolved-state guard fixes the
  `continue-existing-artifact` mis-fire (proven live: the run scaffolded a FRESH
  artifact + set `Resolution: resolved`). **NEW finding:** the floor doc-skip is
  INDEPENDENT of the mis-fire — the run STILL skipped `five-steps`/`debug-memory` in
  fresh mode, so debug stays HYPOTHESIS (floor NOT softened). Grader judge-window
  truncation fixed (500→8000). [recapture](../charness-artifacts/cautilus/debug-claim-fidelity-2026-06-30-recapture/finding.md) · [goal](../charness-artifacts/goals/2026-06-30-issue-2-debug-follow-ups-start-here-sharpens-2.md)
- **dup-ratchet GREEN + capture git-hook friction fixed:** capture-skill-run.sh
  neutralizes hooks to an empty dir; the `fae23` portability finding seeded the full
  audit (Next Session 1).
  [hooks+dup critique](../charness-artifacts/critique/2026-06-30-capture-hooks-and-dup-ratchet-critique.md)
- **Efficiency — outcome grader COMPLETE + LIVE-PROVEN** (prior session): auto-grade
  wired into the A/B harness (`run_ab` grades each bundle; `--judge-cmd` /
  `--keep-untracked-outputs`; `validate_outcome_assertions.py`). hitl + retro A/B live.

## Next Session

1. **Correctness sweep (ask-before-run) — START HERE.** Capture the next hypothesis-floor
   skill, one at a time, REUSING the now-proven outcome-assertion pattern per-eval (debug's
   set is the worked example — it discriminated substance at `pass_rate 0.8`). A miss =
   skill-shape signal (re-pin / re-classify / planner), never soften the matcher; do NOT
   planner-ize mechanically. `--justification-log` overrides `next_action: none`; mirror the
   hitl/retro/quality/debug path. **debug follow-up (deferred, candidate issue):** the floor
   doc-skip is a debug skill-shape question — does a run need the reference docs when the
   scaffold already supplies the structure? NOT a floor softening.
2. **Dup leg — RECORDED / closed.** Audit (25 families) + 3 extractions landed (resolver
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
