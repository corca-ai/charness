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

- **Lever class is CHURN, not references** — 4 H0s agree, and the reusable patterns
  are now **LOCKED**:
  [anti-churn-patterns.md](../charness-artifacts/reference-compaction/anti-churn-patterns.md)
  (retro = exemplar; transfer targets + churn heuristic + H0 method).
  - **quality** — churn FIXED+PROVEN (report-all default + scaffold-first). *Still has
    an un-surfaced `max_lines` ceiling — see Next Session #1.*
  - **debug** — churn FIXED+PROVEN (`ff80f914`, A/B `f54f8e4f`): invisible `MAX=180`
    trim-loop → scaffold surfaces `size_budget`; A/B edits 37→7, `wc -l` 19→0.
    [debug-h0-closeout-churn.md](../charness-artifacts/reference-compaction/debug-h0-closeout-churn.md)
  - **spec** — NO lever (pure-prose, refs load-bearing):
    [spec-h0-capture-diagnosis.md](../charness-artifacts/reference-compaction/spec-h0-capture-diagnosis.md)
  - **retro** — no dominant lever + micro-lever FIXED (`6f71db59`); anti-churn
    exemplar (~8× leaner):
    [retro-h0-anti-churn-exemplar.md](../charness-artifacts/reference-compaction/retro-h0-anti-churn-exemplar.md)

## Next Session

Transfer the locked patterns (static-checked, ranked):

1. **quality — surface `size_budget` (HIGH, cheap).** Static-check: quality has a
   `max_lines` ceiling but `scaffold_quality_artifact.py` does NOT pass `size_budget`
   → the debug trim-loop likely persists. Shared field + count-reporting validator
   already exist; wire it like debug, then prove with a controlled A/B.
2. **ideation — check for a format-rule micro-lever** (has a validator, no ceiling;
   retro's `Persisted` case proved non-ceiling format rules also churn).
3. **issue / achieve / hotl — heuristic predicts churn ABSENT** (scaffold-only, no
   validator ceiling). Confirm cheaply; do not over-invest.
4. **Strongest long-run transfer:** move artifact skills to retro's persist-helper-
   that-stamps shape (pattern 1) — a bigger per-skill change, weigh later.
5. **Orthogonal debug gap:** debug still skips the `debug-memory.md` RCF — its own lever.

## Discuss

- Ungated evidence path = `capture-skill-run.sh` + `build-observation.mjs`; only
  `cautilus evaluate` scoring is ask-before-run, `cautilus improve` disabled.
- Brittle test: [test_handoff_plan.py](../tests/test_handoff_plan.py)
  `..._derives_refresh_and_pickup` reds broad pytest on any >=60-line handoff.

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [reference-compaction contract](../charness-artifacts/reference-compaction/contract.md) · [anti-churn-patterns.md](../charness-artifacts/reference-compaction/anti-churn-patterns.md)
