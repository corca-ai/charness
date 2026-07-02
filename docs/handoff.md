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
  - **debug** — churn lever FOUND, mechanism LANDED, reduction **UNPROVEN**
    (`ff80f914`): [debug-h0-closeout-churn.md](../charness-artifacts/reference-compaction/debug-h0-closeout-churn.md).
    Trim-to-fit loop vs an invisible `MAX_ARTIFACT_LINES=180`; scaffold now surfaces
    `size_budget` + validator reports overage. Fresh-eye SOUND-WITH-DEFECTS —
    behavioral reduction not captured, and debug runs demonstrably ignore surfaced
    guidance, so 'surface→heed' is unproven here.

## Next Session

1. **PROOF GATE for the debug fix (do FIRST):** fresh `/charness:debug` capture on
   `ff80f914` vs the pre-fix baseline, same planted bug (a non-gitignore-aware
   scanner on a scratch branch); compare Edit/`wc -l` churn. Drops → claim fixed.
   Persists → the budget rides a channel debug ignores; escalate (planner-enforced /
   pre-sized sections). Either outcome is a real finding.
2. **Continue the churn-class hunt** on artifact-write/closeout-heavy skills
   (ideation, retro, issue, achieve) — name the suspected avoidable cost, then H0.
   Do NOT sweep by ref count (spec proved ref count ≠ lever).

## Discuss

- The debug fix is honest-but-unproven; #1 is the gate before calling it fixed.
- Ungated evidence path = `capture-skill-run.sh` + `build-observation.mjs`; only
  `cautilus evaluate` scoring is ask-before-run, `cautilus improve` disabled.
- Brittle test: [test_handoff_plan.py](../tests/test_handoff_plan.py)
  `..._derives_refresh_and_pickup` reds broad pytest on any >=60-line handoff.

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [reference-compaction contract](../charness-artifacts/reference-compaction/contract.md)
