# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Big picture:** skills satisfy two axes, evals verify each SEPARATELY —
  **correctness** (claim-fidelity: does a run honor its claim? proven by live
  capture) and **efficiency** (process + output waste; advisory, never pass/fail).

## Current State

- **Plan C DONE (2026-06-30): debug floor retired `five-steps.md`; n=2 PROVEN.**
  Capture #2 (`...plan-c-capture2/`) reproduced capture #1's
  `falsifiable-hypothesis-before-fix` PASS on an independent clean run (real repro +
  disconfirmer before any fix; floor still MISS, coverage 5/10). Gate met, so
  `requiredCommandFragments` is now `[debug-memory.md]` — the substance assertion is
  the bar; doc-opening retired as a proxy. `debug-memory.md` STAYS the floor (its
  consume-prior gap is unproven). Planner unchanged (still routes five-steps.md).
- **Debug internalize + compress DONE (handoff item 1):** Plan A (ce3caa6c)
  scaffold-seeded the repro/hypothesis/verification method + `disconfirmer:` marker;
  Plan B (853a5174) cut references 633->565 lines, 11->10 files.
  [spec](../charness-artifacts/spec/2026-06-30-debug-doc-internalization-and-compression.md)

## Next Session

1. **Correctness sweep.** Capture the next hypothesis-floor skill one at a time,
   REUSING the proven outcome-assertion pattern per-eval. A miss = skill-shape signal
   (re-pin / re-classify / planner), never soften the matcher. `--justification-log`
   overrides `next_action: none`; mirror hitl/retro/quality/debug.
2. **AGENTS.md-level lesson-internalization fixture (operator-raised).** New cautilus
   target class: judge whether a prior recent-lessons.md lesson was internalized by a
   later session (consumer-side fidelity). Candidate issue; see latest session retro.
3. **More compression (optional):** remaining big debug docs (adapter-contract 88,
   invariant-first 78, named-target 75) are phrase-pinned; cut only capture-confirmed.

## Discuss

- **Brittle test surfaced:** [test_handoff_plan.py](../tests/test_handoff_plan.py)
  `..._derives_refresh_and_pickup` reads the LIVE `docs/handoff.md` and asserts
  `follow_workflow_trigger`, so ANY near_limit handoff (>=60 lines) reds broad
  pytest. 853fb9fc shipped it red; pruned here. Deeper fix: decouple the test from
  live mutable state.
- Threshold policy RESOLVED: per-skill `max_duration_ms` from a PASSING capture (~2x).

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [quality latest](../charness-artifacts/quality/latest.md)
- proofs: [cautilus latest](../charness-artifacts/cautilus/latest.md) · [plan-a recapture n=1](../charness-artifacts/cautilus/debug-claim-fidelity-2026-06-30-plan-a-recapture/finding.md) · [plan-c capture2 n=2](../charness-artifacts/cautilus/debug-claim-fidelity-2026-06-30-plan-c-capture2/finding.md)
