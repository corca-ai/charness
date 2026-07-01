# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Big picture:** skills satisfy two axes, evals verify each SEPARATELY —
  **correctness** (claim-fidelity, proven by live capture) and **efficiency** (advisory).

## Current State

- **Reference-compaction Slices 1–3 DONE (`5971a29e`, `0e3f5f4f`, `1306b1c8`).** S1
  KEYSTONE (mechanism only): RCF-or-RSF floor guard + advisory `classTag` +
  `## Closeout Vocabulary` headroom exemption + create-skill token-home rule. S2
  deleted 3 dead provenance memos. S3 deleted 8 pure-DUP spec refs (16→8, 4-surface
  removals, RCF intact). All fresh-eye SHIP. Residual:
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

1. **Continue reference-compaction (Slices 1–3 DONE).** Next: **Slice 4 = advisory
   classTag only** (retro/achieve/create-skill/find-skills/announcement/narrative/debug;
   cosmetic, no token movement), then **Slice 5 (impl)** + **Slice 6 (spec enum)** which
   move real tokens — Slice 5 **needs a FRESH ask-before-run cautilus capture** for the
   honest RSF token. Slice 7 (RCF→RSF sweep) is issue-filed. Delete-slice lessons: watch
   the ≥1-`references/`-file floor (validate_skills:327,356 — a skill can't hit zero refs);
   **run the broad pytest BEFORE the fresh-eye critique** — grep misses path-built test
   consumers (S3 caught only in critique). Detail:
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
