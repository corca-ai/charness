# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Big picture:** skills satisfy two axes, evals verify each SEPARATELY —
  **correctness** (claim-fidelity, proven by live capture) and **efficiency** (advisory).

## Current State

- **Reference-compaction Slice 1 (KEYSTONE) DONE (committed `5971a29e`).** Shared
  mechanism only, no per-skill token movement: RCF-or-RSF floor guard + advisory
  `classTag` (DUP/INLINE/DEPTH, untagged→DEPTH) + `## Closeout Vocabulary` headroom
  exemption w/ token-shape anti-abuse + create-skill token-home rule. 28 node + 16 py
  tests, 25 live specs green, fresh-eye critique verdict SHIP. Residual:
  `check_skill_surface_preflight.py` at 478/480 code lines — extract helpers before
  the next add. [contract](../charness-artifacts/reference-compaction/contract.md)
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

1. **Continue reference-compaction (Slice 1 keystone DONE).** Next: **Slice 2 = DEAD
   deletes** (web-fetch/gather-slack/gather-notion provenance memos: rm file + drop
   SKILL.md `## References` bullet + mirror + find-skills inventory, together), then
   **Slice 3** (spec 8 pure-DUP deletes), **Slice 4** (advisory classTag only). **Slice 5
   (impl)** and **Slice 6 (spec enum)** move real tokens and Slice 5 **needs a FRESH
   ask-before-run cautilus capture** to pick the honest RSF token. Slice 7 (RCF→RSF sweep)
   is issue-filed. Per-slice contracts + risk verdicts in
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
