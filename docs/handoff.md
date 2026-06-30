# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Big picture:** skills satisfy two axes, evals verify each SEPARATELY —
  **correctness** (claim-fidelity: does a run honor its claim? proven by live
  capture) and **efficiency** (process + output waste; advisory, never pass/fail).

## Current State

- **Debug internalization + compression DONE (2026-06-30, handoff item 1).** Two
  slices landed:
  - **Plan A (ce3caa6c):** the falsifiable-hypothesis rule now lives in the
    scaffold STRUCTURE — `## Reproduction`/`## Hypothesis`/`## Verification` carry
    method seeds, and `validate_debug_artifact.py` requires the current `latest.md`
    `## Hypothesis` to carry a `disconfirmer:` honesty marker (n/a-escape + trivial
    short-circuit ok; latest.md/forward-only). Targets the proven
    `falsifiable-hypothesis-before-fix` re-capture FAIL. The OUTCOME assertion
    stays the substance bar; the marker is fresh-eye honesty, not anti-gaming.
  - **Plan B (853a5174):** references 633->565 lines, 11->10 files. Deleted
    `anti-patterns.md` (rule in SKILL.md Guardrails); compressed `sibling-search`
    156->110 and `detection-gap` 53->44 (validator/scaffold own the cut rules).
  - Floor unchanged: `requiredCommandFragments` stays [five-steps, debug-memory].
  [spec](../charness-artifacts/spec/2026-06-30-debug-doc-internalization-and-compression.md)

## Next Session

1. **Re-capture debug to confirm Plan A (ask-before-run).** Does a run now fill
   `disconfirmer:` with a real cheapest-refutation (PASS) vs static-only (FAIL)?
   Two clean captures gate **Plan C** (retire `five-steps.md` from the floor once
   substance-asserted) — NOT yet (n=1).
2. **Correctness sweep.** Capture the next hypothesis-floor skill one at a time,
   REUSING the proven outcome-assertion pattern per-eval (debug's set is the worked
   example, `pass_rate 0.8`). A miss = skill-shape signal (re-pin / re-classify /
   planner), never soften the matcher. `--justification-log` overrides
   `next_action: none`; mirror hitl/retro/quality/debug.
3. **More compression (optional):** remaining big debug docs (adapter-contract 88,
   invariant-first 78, named-target 75) are phrase-pinned depth; cut only with a
   capture-confirmed justification.

## Discuss

- **Brittle test surfaced:** [test_handoff_plan.py](../tests/test_handoff_plan.py)
  `..._derives_refresh_and_pickup` reads the LIVE `docs/handoff.md` and asserts
  `follow_workflow_trigger`, so ANY near_limit handoff (>=60 lines) reds broad
  pytest. 853fb9fc shipped it red; pruned here. Deeper fix: decouple the test from
  live mutable state.
- Threshold policy RESOLVED: per-skill `max_duration_ms` from a PASSING capture (~2x).

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [quality latest](../charness-artifacts/quality/latest.md)
- proofs: [cautilus latest](../charness-artifacts/cautilus/latest.md) · [debug recapture](../charness-artifacts/cautilus/debug-claim-fidelity-2026-06-30-recapture/finding.md)
