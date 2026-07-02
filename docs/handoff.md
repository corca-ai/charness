# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Governing intent** (read first):
  [intent.md](../charness-artifacts/reference-compaction/intent.md) — the point is a
  SMARTER agent, not proof/surface; prune gates/refs that don't earn their place;
  the ONLY test is "그게 정말 최선인가?" (no proxy metric). claim-fidelity/cautilus is
  the *instrument*, read for "does this ref meaningfully help," not "floor passed."

## Current State

- **The lever class is CHURN/RITUAL, not references.** Three per-skill H0 captures
  now agree:
  - **quality** — churn lever FOUND+FIXED+PROVEN (closeout re-run 6× → report-all
    default + scaffold-first).
  - **spec** — NO lever; refs load-bearing, costs are the skill working well:
    [spec-h0-capture-diagnosis.md](../charness-artifacts/reference-compaction/spec-h0-capture-diagnosis.md).
  - **debug** — churn lever FOUND+FIXED+**PROVEN** (`ff80f914`):
    [debug-h0-closeout-churn.md](../charness-artifacts/reference-compaction/debug-h0-closeout-churn.md).
    Trim-to-fit loop vs an invisible `MAX_ARTIFACT_LINES=180` → scaffold surfaces
    `size_budget` + validator reports overage. Controlled A/B re-capture (same
    session/bug, only the fix differs): edits 37→7, `wc -l` 19→0, wall 18→11min,
    artifact 180 (at ceiling)→152 (headroom) and still complete. The run heeded
    the budget — fresh-eye's 'debug ignores guidance' worry refuted.

## Next Session

1. **Continue the churn-class hunt** on the next artifact-write/closeout-heavy
   skill (`ideation`, `retro`, `issue`, `achieve` are the candidates) — capture-
   then-diagnose, name the suspected avoidable cost, fix on sight, then prove with
   a controlled A/B re-capture (the debug pattern: same session/bug, only the fix
   differs — stronger than n=2 uncontrolled). Do NOT sweep by ref count (spec
   proved ref count ≠ lever).
2. **Reusable win:** the shared `size_budget` scaffold field + count-reporting
   `validate_max_lines` now help ANY length-capped artifact skill — check whether
   quality/retro/etc. artifacts show the same trim-loop and wire their scaffolds.
3. **Orthogonal debug gap (separate):** debug runs still skip the `debug-memory.md`
   RCF (documented, not-yet-internalized cross-incident memory) — its own lever.

## Discuss

- The debug fix is honest-but-unproven; #1 is the gate before calling it fixed.
- Ungated evidence path = `capture-skill-run.sh` + `build-observation.mjs`; only
  `cautilus evaluate` scoring is ask-before-run, `cautilus improve` disabled.
- Brittle test: [test_handoff_plan.py](../tests/test_handoff_plan.py)
  `..._derives_refresh_and_pickup` reds broad pytest on any >=60-line handoff.

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [reference-compaction contract](../charness-artifacts/reference-compaction/contract.md)
