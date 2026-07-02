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

- **Prune+brief pattern SHIPPED on `quality`** (pilot + reusable pattern:
  [quality-prune-brief-pilot.md](../charness-artifacts/reference-compaction/quality-prune-brief-pilot.md)).
  Lever is NOT delete/role-flip (strands capability) but **upgrade planner stdout
  into a substantive `brief`, then the primer becomes trigger-gated depth**
  (mirrors retro's `lens_brief`). Demoted 3 of 9 mandatory primer reads (9→6),
  each adversarially verified; residue inline in `plan_quality_run.py`.
- **H0 capture corrected the assumption** (`capture-skill-run.sh` is host-owned/
  ungated; only cautilus *scoring* is gated): dominant cost was artifact
  **closeout churn**, not reference reads → FIXED (validator report-all default +
  scaffold-first, `27354b7d`). Also single-sourced gate-classification's enum to
  the brief (−13, `87922a7e`); the other demoted docs are test-locked depth — refs
  earn their bytes, so real compaction is read-timing, not byte count.
- Verified throughout: `tests/quality_gates` 2475 passed; fresh-eye SOUND.

## Next Session

**Go to the next skill — `spec`.** Census: #2 by refs (16) and the ONLY skill with
a large **DUP bucket (8 pure-DUP deletes already flagged)** + an acceptance-checks
enum lift — real `삭제` candidates, unlike quality's 0-DUP.

1. **Capture-then-diagnose FIRST** (the H0 lesson): real `/charness:spec` via
   `capture-skill-run.sh` (ungated) + `build-skill-execution-observation.mjs`;
   find the DOMINANT cost before assuming it is reference reads, and fix that.
2. **Then prune/brief/single-source**: the 8 DUP deletes, acceptance-checks enum
   → brief, teeth→brief for briefable mandatory reads (adversarially verify each).
3. Judge by "그게 정말 최선인가?", not ref count.

**Quality remainder (lower priority):** inventory-dispatch stays required until a
machine `scripts:` routing layer lets the planner brief its ~19 scripts; softer
candidates need adversarial verify; quality-lenses.md is the one required + RCF.

## Discuss

- The ungated capture path (`capture-skill-run.sh` + build-observation) IS
  runnable for evidence; only `cautilus evaluate` scoring is ask-before-run and
  `cautilus improve` (optimize) is disabled by repo policy.
- Brittle test: [test_handoff_plan.py](../tests/test_handoff_plan.py)
  `..._derives_refresh_and_pickup` reds broad pytest on any >=60-line handoff.

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [reference-compaction contract](../charness-artifacts/reference-compaction/contract.md)
