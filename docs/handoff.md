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

- **Lever class is CHURN, not references.** Four per-skill H0 captures agree, and
  the mechanism is now precise (see the rule below):
  - **quality** — churn FIXED+PROVEN (report-all default + scaffold-first).
  - **debug** — churn FIXED+**PROVEN** (`ff80f914`, A/B `f54f8e4f`):
    [debug-h0-closeout-churn.md](../charness-artifacts/reference-compaction/debug-h0-closeout-churn.md).
    Invisible `MAX_ARTIFACT_LINES=180` trim-loop → scaffold surfaces `size_budget`
    and the validator reports the overage. Controlled A/B: edits 37→7, `wc -l` 19→0.
  - **spec** — NO lever (refs load-bearing; pure-prose, no artifact gate):
    [spec-h0-capture-diagnosis.md](../charness-artifacts/reference-compaction/spec-h0-capture-diagnosis.md).
  - **retro** — no *dominant* lever, the **anti-churn exemplar** (~8× cheaper than
    debug) + one micro-lever **FIXED**:
    [retro-h0-anti-churn-exemplar.md](../charness-artifacts/reference-compaction/retro-h0-anti-churn-exemplar.md).
    persist-helper + no ceiling + lens_brief = what the churn fixes converge to;
    `persist_retro_artifact` now stamps the `## Persisted` path (no hand-edit).

## Next Session

1. **Target by the HEURISTIC, don't sweep.** Churn PRESENT ⇐ a skill (a) hand-edits
   its artifact via `Edit` (no persist helper) AND (b) the run iterates to satisfy an
   invisible **validator-format rule** (a `MAX_*_LINES` ceiling is one; retro's
   `Persisted` form was a micro-case with no ceiling). Cheap STATIC check of a
   candidate's scaffold+validator predicts the capture. Candidates: `issue`,
   `achieve`, `ideation`, `hotl` — static-check first, H0 only the hits.
2. **Fix pattern:** surface the budget (debug) or adopt a persist helper (retro,
   the stronger shape). Prove with a controlled A/B re-capture (same session/bug,
   only the fix differs — stronger than n=2 uncontrolled).
3. **Reusable win already shared:** `size_budget` scaffold field + count-reporting
   `validate_max_lines` help ANY length-capped artifact skill (wire their scaffolds).
4. **Orthogonal debug gap:** debug runs still skip the `debug-memory.md` RCF — its
   own (non-churn) lever, documented.

## Discuss

- Ungated evidence path = `capture-skill-run.sh` + `build-observation.mjs`; only
  `cautilus evaluate` scoring is ask-before-run, `cautilus improve` disabled.
- Brittle test: [test_handoff_plan.py](../tests/test_handoff_plan.py)
  `..._derives_refresh_and_pickup` reds broad pytest on any >=60-line handoff.

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [reference-compaction contract](../charness-artifacts/reference-compaction/contract.md)
