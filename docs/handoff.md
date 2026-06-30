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

1. **Dup audit DONE + 3 extractions landed** (this session)
   [VERIFIED table](../charness-artifacts/quality/2026-06-30-dup-portability-falsification-audit.md).
   25 families (workflow judge→refute + fresh-eye). **#390 governs ONLY the
   `_load_skill_runtime_bootstrap` finder shim (`cd865345`, irreducible)** — NOT the resolver
   `main()` tail. EXTRACTED, all proven behavior-neutral + fresh-eye SAFE: `fe221bab`/`54bc9db2`
   (16 resolvers → `SKILL_RUNTIME.run_adapter_cli`), `878bffbe` (dogfood format_human),
   `c2c42ffe` (tool-rec payload). DEFERRED with hands-on VERIFIED notes (awkward-param /
   divergent / risky-equivalence / doc-composition, not clean neutral wins): `16fec8ed`
   `a664a431` `3edc6552` `704b93d2` `13741926` `b8dbc45f`. **Lesson:** a standing-decision
   override is only as broad as what the gate ACTUALLY governs; a "fixable" verdict still
   needs hands-on byte-identical proof before it lands.
2. **Correctness sweep (continue, ask-before-run):** capture the next hypothesis-floor
   skill, one at a time. A miss = skill-shape signal (re-pin / re-classify / planner),
   never soften the matcher; do NOT planner-ize mechanically. `--justification-log`
   overrides `next_action: none`; mirror the hitl/retro/quality path. The outcome-grade
   surface is live, so a captured skill can also get an outcome assertion set
   (only hitl has one) — add per-eval as you capture, not speculatively.
3. **debug follow-ups (operator-agreed):** author a debug OUTCOME-ASSERTION set
   (protect the structural-improvement intent by SUBSTANCE — real Detection Gap /
   Sibling Search / Prevention content — not doc-opening, a weak proxy); review
   whether debug reference docs are over-built given the scaffold already supplies
   the structure; fix `continue-existing-artifact` mode mis-firing for fresh bugs;
   re-capture debug to attempt a PASS.

## Discuss

- Threshold policy RESOLVED: per-skill `max_duration_ms` from a PASSING capture (~2x).
  Open: promote trace-digest to a REQUIRED floor after deciding how to treat the
  transcript-less retro bundles.

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [quality latest](../charness-artifacts/quality/latest.md)
- proofs: [cautilus latest](../charness-artifacts/cautilus/latest.md) · [hitl](../charness-artifacts/cautilus/hitl-claim-fidelity-2026-06-29/) · [retro](../charness-artifacts/cautilus/retro-claim-fidelity-2026-06-29-recapture/)
