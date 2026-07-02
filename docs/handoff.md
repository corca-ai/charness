# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Governing intent** (read first):
  [intent.md](../charness-artifacts/reference-compaction/intent.md) — the point is a
  SMARTER agent, not proof/surface; prune gates/refs that don't earn their place;
  the ONLY test is "그게 정말 최선인가?" (no proxy metric). claim-fidelity/cautilus is
  the *instrument*, read for "does this ref meaningfully help / is it already covered
  by body/script/template," not "floor passed."

## Current State

- **v0.58.0 SHIPPED** — tag pushed, `main`==`origin/main`; #412/#413 closed on push.
- **Method locked (operator-directed):** every skill path/condition gets its OWN
  falsifiable fixture; capture VERIFIES, docs+routing DESIGN; token OBSERVED never assumed.
- **#411 gather public-URL substance floor CAPTURE-PROVEN** (4/4, live judge;
  `ae6d833d`, proof in [cautilus/latest.md](../charness-artifacts/cautilus/latest.md));
  doc-open RCF refuted 0/8 on a fresh run.
- **Substance-floor-only spec support SHIPPED** (`325909f7`, fresh-eye SOUND):
  `claim_fidelity_lib` now allows empty RCF+RSF when a sibling `outcome-assertions.json`
  exists — unblocks the gather public-URL AND setup #413 RCF flips.
- **Untested-HYPOTHESIS floor sweep DESIGNED** (census-anchored, 7 never-captured
  skills, zero captures):
  [untested-hypothesis-floor-sweep.md](../charness-artifacts/reference-compaction/untested-hypothesis-floor-sweep.md)
  — REFUTED-class (announcement/ideation/narrative), MIXED (create-skill/release/spec),
  genuine-DEPTH verify-only (find-skills).
- Deferred honestly: setup greenfield (not in-repo capturable, #410).

## Next Session

1. **Flip gather public-URL + setup #413** (now unblocked by `325909f7`): drop the
   refuted RCF → empty (substance floor carries it), inline the Access-Modes enum into
   gather SKILL.md while **resolving the `mode_option_pressure_terms` ergonomics gate**
   the enum trips (reduce mode vocab or declare the opt-in rule), sync mirror, then a
   confirming ask-before-run capture each (substance floor already proven, so this is a
   behavior re-confirm).
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
