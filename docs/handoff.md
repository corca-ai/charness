# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Big picture:** skills satisfy two axes, evals verify each SEPARATELY —
  **correctness** (claim-fidelity, proven by live capture) and **efficiency** (advisory).

## Current State

- **v0.58.0 SHIPPED** — tag pushed, `main`==`origin/main`; #412/#413 closed on push.
- **Method locked (operator-directed):** every skill path/condition gets its OWN
  falsifiable fixture; capture VERIFIES, docs+routing DESIGN; token OBSERVED never assumed.
- **#411 gather public-URL substance floor SHIPPED** (`outcome-assertions.json`,
  `3b650cb6`, fresh-eye SOUND); its enum-inline + RCF-flip is the capture-gated remainder.
- **Untested-HYPOTHESIS floor sweep DESIGNED** (census-anchored, 7 never-captured
  skills, zero captures):
  [untested-hypothesis-floor-sweep.md](../charness-artifacts/reference-compaction/untested-hypothesis-floor-sweep.md)
  — REFUTED-class (announcement/ideation/narrative), MIXED (create-skill/release/spec),
  genuine-DEPTH verify-only (find-skills).
- Deferred honestly: setup greenfield (not in-repo capturable, #410).

## Next Session

1. **Run the BATCHED ask-before-run Cautilus capture session** over the queue in
   [untested-hypothesis-floor-sweep.md](../charness-artifacts/reference-compaction/untested-hypothesis-floor-sweep.md)
   (gather MOVE + REFUTED-class + MIXED + find-skills). Gate via
   `plan_cautilus_proof.py`; run `run_cautilus_eval.py`, never bare `cautilus evaluate`.
   Before each REFUTED-class retire, do the missing-scenario trace (caveat 1).
2. **File the deferred guard idea:** a validator cross-checking each planner's
   intent/condition-keyed required-reads against scenario specs (auto-detect a
   conditionally-required doc no scenario forces).

## Discuss

- Brittle test: [test_handoff_plan.py](../tests/test_handoff_plan.py)
  `..._derives_refresh_and_pickup` reds broad pytest on any >=60-line handoff. Keep this
  file under 60 lines until the test is decoupled from live state.

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [reference-compaction contract](../charness-artifacts/reference-compaction/contract.md)
- proofs: [session retro](../charness-artifacts/retro/2026-07-02-session-retro.md) · [cautilus latest](../charness-artifacts/cautilus/latest.md)
