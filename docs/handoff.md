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
    short-circuit ok; latest.md/forward-only). PROVED live (capture #1): the
    `falsifiable-hypothesis-before-fix` assertion flipped FAIL->PASS — the run built
    a real reproduction + ran a disconfirmer. Floor still MISS (doc-skip persists).
  - **Plan B (853a5174):** references 633->565 lines, 11->10 files. Deleted
    `anti-patterns.md` (rule in SKILL.md Guardrails); compressed `sibling-search`
    156->110 and `detection-gap` 53->44 (validator/scaffold own the cut rules).
  - Floor unchanged: `requiredCommandFragments` stays [five-steps, debug-memory].
  [spec](../charness-artifacts/spec/2026-06-30-debug-doc-internalization-and-compression.md)

## Next Session

1. **Plan C gate (ask-before-run): one MORE clean debug capture (n=2).** Capture #1
   proved `falsifiable-hypothesis` PASS; a second confirming PASS gates retiring
   `five-steps.md` from the floor (let the substance assertion be the bar).
2. **Correctness sweep.** Capture the next hypothesis-floor skill one at a time,
   REUSING the proven outcome-assertion pattern per-eval. A miss = skill-shape signal
   (re-pin / re-classify / planner), never soften the matcher. `--justification-log`
   overrides `next_action: none`; mirror hitl/retro/quality/debug.
3. **AGENTS.md-level lesson-internalization fixture (operator-raised).** New cautilus
   target class: judge whether a prior recent-lessons.md lesson was internalized by a
   later session (consumer-side fidelity). Candidate issue; see latest session retro.
4. **More compression (optional):** remaining big debug docs (adapter-contract 88,
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
- proofs: [cautilus latest](../charness-artifacts/cautilus/latest.md) · [debug plan-a recapture](../charness-artifacts/cautilus/debug-claim-fidelity-2026-06-30-plan-a-recapture/finding.md)
