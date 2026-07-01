# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Big picture:** skills satisfy two axes, evals verify each SEPARATELY —
  **correctness** (claim-fidelity, proven by live capture) and **efficiency** (advisory).

## Current State

- **Reference-compaction Slices 1–4 DONE (`5971a29e`, `0e3f5f4f`, `1306b1c8`, `bbb088b5`).**
  S1 KEYSTONE mechanism; S2 deleted 3 dead provenance memos; S3 deleted 8 pure-DUP spec
  refs (16→8); S4 added advisory `classTag` to 7 skills' specs (no token movement, RCF
  untouched; 2 tags census-aligned off-plan per critique — debug/five-steps→INLINE,
  narrative/source-map→DEPTH). All fresh-eye SHIP. Residual:
  `check_skill_surface_preflight.py` 478/480 code lines — extract helpers before next
  add. [contract](../charness-artifacts/reference-compaction/contract.md)
  (+ [census.json](../charness-artifacts/reference-compaction/census.json),
  [plan.json](../charness-artifacts/reference-compaction/plan.json)).
- **#409 DONE (`9d4c2882`).** capture→grade preserves evidence for committing/clean
  runs (diff vs capture base, transcript from `stream.jsonl`). Sweep reuse unblocked.
- impl capture (5th sweep skill): floor **MISS** (0/8), substance **4/5**
  (`honest-categorized-closeout` FAIL — the enum lives ONLY in `verification-ladder.md`,
  not inlined). The impl closeout-vocab fork is now RESOLVED into the keystone (Option A).
  [finding](../charness-artifacts/cautilus/impl-claim-fidelity-2026-07-01/finding.md)
- PROVEN floors: retro, hitl, quality, debug (n=2). impl HYPOTHESIS. ~13 uncaptured.

## Next Session

1. **Continue reference-compaction (Slices 1–4 DONE) — USER will do S5+S6 next session.**
   **Slice 5 (impl)**: `## Closeout Vocabulary` lift (Lint-Gate enum + 5 completion-report
   categories from verification-ladder.md → pointer-to-core) + RCF→RSF; validator-enforced,
   HIGHEST risk (200-line knife-edge ~199, needs S1's guard). **NEEDS a FRESH ask-before-run
   cautilus capture** to pick the honest RSF token (consult `plan_cautilus_proof.py` first;
   use `run_cautilus_eval.py`). **Slice 6 (spec)**: acceptance-checks enum lift (no RCF
   rewrite → no capture, lower risk). Slice 7 (RCF→RSF sweep) is issue-filed. Lessons: run
   broad pytest BEFORE the critique (grep misses path-built test consumers); watch the
   ≥1-`references/` floor when deleting. Per-slice detail:
   [plan.json](../charness-artifacts/reference-compaction/plan.json) (`execution.slices`).
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
