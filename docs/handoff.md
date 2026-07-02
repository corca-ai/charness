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
- Verified: `tests/quality_gates` 2475 passed; fresh-eye critique SOUND;
  `plan_cautilus_proof.py` → next_action none (deterministic + scenario review own
  closeout; live capture contract-refused). Committed with artifacts.

## Next Session

1. **inventory-dispatch.md instance** — biggest remaining always-loaded item (297
   lines; kept required this session because ~19 inventory scripts live ONLY there
   and the planner emits no script names). Add a machine-readable `scripts:` routing
   layer to catalog.yaml so the planner can brief surface→script(+flags) routing,
   THEN demote. A naive demote strands the scripts.
2. **Extend the pattern to other overhead-heavy skills** — same method: audit
   mandatory reads, adversarially verify each demote, brief the residue via the
   planner, prove by scenario review. Judge by "그게 정말 최선인가?", not read-count.
3. **Softer `quality` candidates** (proposal-flow, operability-signals,
   skill-quality, skill-ergonomics): adversarially verify BEFORE demoting.
   quality-lenses.md stays the one required-primer + RCF floor.

## Discuss

- Operator intent wanted live cautilus verification ("실제로 돌려보자");
  `plan_cautilus_proof.py` returns next_action none for this reversible slice.
  Ask before any live capture (eval-only, ask-before-run).
- Brittle test: [test_handoff_plan.py](../tests/test_handoff_plan.py)
  `..._derives_refresh_and_pickup` reds broad pytest on any >=60-line handoff.

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [reference-compaction contract](../charness-artifacts/reference-compaction/contract.md)
