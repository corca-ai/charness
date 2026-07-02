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
- **#411 gather public-URL substance floor CAPTURE-PROVEN** (4/4, live judge;
  `ae6d833d`, proof in [cautilus/latest.md](../charness-artifacts/cautilus/latest.md));
  doc-open RCF refuted 0/8 on a fresh run. RCF-flip now blocked on a design decision,
  not proof.
- **Untested-HYPOTHESIS floor sweep DESIGNED** (census-anchored, 7 never-captured
  skills, zero captures):
  [untested-hypothesis-floor-sweep.md](../charness-artifacts/reference-compaction/untested-hypothesis-floor-sweep.md)
  — REFUTED-class (announcement/ideation/narrative), MIXED (create-skill/release/spec),
  genuine-DEPTH verify-only (find-skills).
- Deferred honestly: setup greenfield (not in-repo capturable, #410).

## Next Session

1. **Unblock the RCF flips:** decide + implement **substance-floor-only spec support**
   in `claim_fidelity_lib` (allow empty RCF+RSF when a sibling `outcome-assertions.json`
   exists) — gates gather public-URL flip AND setup #413. Then flip gather (drop refuted
   RCF, inline the Access-Modes enum into SKILL.md, handle the `mode_option_pressure_terms`
   gate) + a capture-confirm.
2. **Batched ask-before-run captures** for the remaining untested HYPOTHESIS floors:
   [untested-hypothesis-floor-sweep.md](../charness-artifacts/reference-compaction/untested-hypothesis-floor-sweep.md).
   Gate via `plan_cautilus_proof.py` / `run_cautilus_eval.py`; capture-before-pin;
   missing-scenario trace before each REFUTED-class retire.
3. **File the deferred guard idea:** a validator cross-checking each planner's
   intent/condition-keyed required-reads against scenario specs.

## Discuss

- Brittle test: [test_handoff_plan.py](../tests/test_handoff_plan.py)
  `..._derives_refresh_and_pickup` reds broad pytest on any >=60-line handoff. Keep this
  file under 60 lines until the test is decoupled from live state.

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [reference-compaction contract](../charness-artifacts/reference-compaction/contract.md)
- proofs: [session retro](../charness-artifacts/retro/2026-07-02-session-retro.md) · [cautilus latest](../charness-artifacts/cautilus/latest.md)
