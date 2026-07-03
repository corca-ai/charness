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
  - **quality** — churn FIXED+PROVEN (report-all + scaffold-first + `size_budget`
    single-sourced/routed via `--json`, `855f611c`). Lever class closed for quality.
  - **debug** — churn FIXED+PROVEN (`ff80f914`, A/B `f54f8e4f`): invisible `MAX=180`
    trim-loop → scaffold surfaces `size_budget`; A/B edits 37→7, `wc -l` 19→0.
    [debug-h0-closeout-churn.md](../charness-artifacts/reference-compaction/debug-h0-closeout-churn.md)
  - **spec** — NO lever (pure-prose, refs load-bearing):
    [spec-h0-capture-diagnosis.md](../charness-artifacts/reference-compaction/spec-h0-capture-diagnosis.md)
  - **retro** — no dominant lever + micro-lever FIXED (`6f71db59`); anti-churn
    exemplar (~8× leaner):
    [retro-h0-anti-churn-exemplar.md](../charness-artifacts/reference-compaction/retro-h0-anti-churn-exemplar.md)
  - **ideation** — no format-rule micro-lever; churn ABSENT (static, no capture;
    fresh-eye SOUND): [ideation-h0-format-rule-check.md](../charness-artifacts/reference-compaction/ideation-h0-format-rule-check.md)

## Next Session

**Two live tracks, both matter (operator: 둘 다 중요, 적을수록 좋음):**

- **Redundancy compaction** — Phase 0 re-verified the 17 surviving DUP/DEAD
  candidates against the LIVE tree: **0 delete-safe** (calibration passed; census
  is stale and mislabels RCF floors as DUP). Deletion track CLOSED; lift yield ~nil.
  Real lever is UPSTREAM — `claim_fidelity` `declaredReferences` actively resists ref
  deletion, so **gated on the concurrent test-necessity verdict.** Plan + per-ref
  evidence: [compaction-plan.md](../charness-artifacts/reference-compaction/compaction-plan.md).
- **Churn sweep** — ideation DONE this session (ABSENT, static, fresh-eye SOUND;
  heuristic sharpened — a non-ceiling format rule churns only when the format is
  *invisible* OR a *tool-computable value is hidden*). Remaining, in order:
  1. issue / achieve / hotl — predicted ABSENT; confirm cheaply by static check.
  2. persist-helper transfer (pattern 1) — bigger per-skill change, weigh later.
  3. debug still skips the `debug-memory.md` RCF — its own lever.

## Discuss

- Ungated evidence path = `capture-skill-run.sh` + `build-observation.mjs`; only
  `cautilus evaluate` scoring is ask-before-run, `cautilus improve` disabled.
- Brittle test: [test_handoff_plan.py](../tests/test_handoff_plan.py)
  `..._derives_refresh_and_pickup` reds broad pytest on any >=60-line handoff.

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [reference-compaction contract](../charness-artifacts/reference-compaction/contract.md) · [anti-churn-patterns.md](../charness-artifacts/reference-compaction/anti-churn-patterns.md)
