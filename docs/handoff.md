# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Big picture:** skills satisfy two axes, evals verify each SEPARATELY —
  **correctness** (claim-fidelity, proven by live capture) and **efficiency** (advisory).

## Current State

- **Reference-compaction Slices 1–6 DONE; Slice 7 issue-filed (#410).** S1 keystone;
  S2–S4 deletes + advisory `classTag`; **S5 (`3c5c8657`) = impl proving slice: token-home
  lift + RCF→RSF floor, PROVEN by a live ask-before-run capture (FLOOR PASS + substance
  5/5; the plan's assumed `unverified-future` was NOT emitted — only `ran-pass` pinned)**;
  S6 (`f9003594`) spec verification-type enum lift (no floor move, INLINE tags off-plan
  per coverage-honesty). All fresh-eye SHIP. Residual:
  `check_skill_surface_preflight.py` near its code-line cap — extract helpers before next
  add. [contract](../charness-artifacts/reference-compaction/contract.md) ·
  [plan.json](../charness-artifacts/reference-compaction/plan.json).
- **#409 DONE (`9d4c2882`).** capture→grade preserves evidence for committing/clean
  runs (diff vs capture base, transcript from `stream.jsonl`). Sweep reuse unblocked.
- impl capture (5th sweep skill): floor **MISS** (0/8), substance **4/5**
  (`honest-categorized-closeout` FAIL — the enum lives ONLY in `verification-ladder.md`,
  not inlined). The impl closeout-vocab fork is now RESOLVED into the keystone (Option A).
  [finding](../charness-artifacts/cautilus/impl-claim-fidelity-2026-07-01/finding.md)
- PROVEN floors: retro, hitl, quality, debug (n=2), impl (n=1, new emitted-token floor).
  ~13 uncaptured.

## Next Session

1. **Reference-compaction Slice 7 sweep — see #410.** Per-skill RCF→RSF floor rewrites
   (critique/hitl/gather/hotl/handoff/setup/create-cli/achieve), each its own gate-clean
   slice needing a FRESH ask-before-run cautilus capture to re-baseline the RSF token
   (proven necessary in S5 — do NOT assume). greenfield-flow.md + default-surfaces.md STAY
   RCF-pinned; issue/markdown-preview need no change. Also surfaced: **#409 Gap 2 recurs at
   the mjs-direct layer** — `build-skill-execution-observation.mjs --session-tree <projDir>`
   tree-truncates the final post-commit closeout block; grade claim-fidelity captures
   against `stream.jsonl`, not the raw tree. Lesson still hot: run broad pytest BEFORE the
   critique (grep misses path-built test consumers, e.g.
   [test_skill_lesson_durability.py](../tests/quality_gates/test_skill_lesson_durability.py)).
2. **Continue correctness sweep** one skill at a time, reusing outcome-assertions.
   Remaining HYPOTHESIS-floor: achieve, announcement, create-cli, create-skill, critique,
   find-skills, gather, handoff, hotl, ideation, narrative, release, spec. A miss =
   skill-shape signal (re-pin/re-classify/planner), never soften the matcher.
3. **AGENTS.md lesson-internalization fixture (operator-raised)** — still open.

## Discuss

- Brittle test: [test_handoff_plan.py](../tests/test_handoff_plan.py)
  `..._derives_refresh_and_pickup` reds broad pytest on any >=60-line handoff. Keep this
  file under 60 lines until the test is decoupled from live state.

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [reference-compaction contract](../charness-artifacts/reference-compaction/contract.md)
- proofs: [cautilus latest](../charness-artifacts/cautilus/latest.md) · [impl finding](../charness-artifacts/cautilus/impl-claim-fidelity-2026-07-01/finding.md)
