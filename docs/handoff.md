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

- **Prune+brief pattern ESTABLISHED + first instance SHIPPED on `quality`.**
  Result + reusable pattern:
  [quality-prune-brief-pilot.md](../charness-artifacts/reference-compaction/quality-prune-brief-pilot.md).
  The lever is NOT delete/role-flip (a naive flip strands capability) but:
  **upgrade planner stdout into a substantive `brief`, then the primer becomes
  trigger-gated depth** (mechanism mirrors retro's `lens_brief`).
- Demoted 3 of 9 mandatory `quality` primer reads (required_reads 9→6, −479 lines):
  gate-classification, automation-promotion, maintainer-local-enforcement — each
  adversarially verified; residue carried inline in `plan_quality_run.py` `brief`.
- Verified: `tests/quality_gates` 2475 passed; adversarial verify + fresh-eye
  critique SOUND. Committed with artifacts.
- **H0 capture (`capture-skill-run.sh` is host-owned/ungated; only cautilus
  *scoring* is gated) confirmed the pilot AND corrected the assumption:** the
  dominant cost is artifact **closeout churn**, not reference reads → FIXED
  (validator report-all default + scaffold-first; commit `27354b7d`).

## Next Session

1. **inventory-dispatch.md instance** — biggest remaining always-loaded item (297
   lines; kept required this session because ~19 inventory scripts live ONLY there
   and the planner emits no script names). Add a machine-readable `scripts:` routing
   layer to catalog.yaml so the planner can brief surface→script(+flags) routing,
   THEN demote. A naive demote strands the scripts.
2. **Capture-then-diagnose, don't assume the lever** (the H0 method lesson): a
   real ungated capture found a bigger lever (closeout churn) than reference
   pruning. Extend to other overhead-heavy skills the same way — capture,
   diagnose the dominant cost, fix that. Judge by "그게 정말 최선인가?", not read-count.
3. **Softer `quality` candidates** (proposal-flow, operability-signals,
   skill-quality, skill-ergonomics): adversarially verify BEFORE demoting.
   quality-lenses.md stays the one required-primer + RCF floor.

## Discuss

- The ungated capture path (`capture-skill-run.sh` + build-observation) IS
  runnable for evidence; only `cautilus evaluate` scoring is ask-before-run and
  `cautilus improve` (optimize) is disabled by repo policy.
- Brittle test: [test_handoff_plan.py](../tests/test_handoff_plan.py)
  `..._derives_refresh_and_pickup` reds broad pytest on any >=60-line handoff.

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [reference-compaction contract](../charness-artifacts/reference-compaction/contract.md)
