# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Big picture:** skills satisfy two axes, evals verify each SEPARATELY —
  **correctness** (claim-fidelity, proven by live capture) and **efficiency** (advisory).

## Current State

- **#409 DONE (pushed `9d4c2882`).** capture→grade now preserves evidence for
  committing/clean runs (diff vs the capture base, transcript from `stream.jsonl`).
  Sweep reuse unblocked.
- **Reference-compaction census + plan DONE (this session).** All 24 skills / 196 refs
  classified — **DEPTH 109 · INLINE 58 · DUP 26 · DEAD 3**. Keystone policy + 7-slice
  plan ready, operator-approved, deferred to next session.
  [contract](../charness-artifacts/reference-compaction/contract.md)
  (+ [census.json](../charness-artifacts/reference-compaction/census.json),
  [plan.json](../charness-artifacts/reference-compaction/plan.json) = per-skill exec
  detail + risk verdicts).
- impl capture (5th sweep skill): floor **MISS** (0/8), substance **4/5**
  (`honest-categorized-closeout` FAIL — the enum lives ONLY in `verification-ladder.md`,
  not inlined). The impl closeout-vocab fork is now RESOLVED into the keystone (Option A).
  [finding](../charness-artifacts/cautilus/impl-claim-fidelity-2026-07-01/finding.md)
- PROVEN floors: retro, hitl, quality, debug (n=2). impl HYPOTHESIS. ~13 uncaptured.

## Next Session

1. **Execute reference-compaction, slice by slice** (per the contract). Start
   **Slice 1 = keystone mechanism** (gate exemption + RCF-or-RSF guard + classTag infra +
   `create-skill` rule; no per-skill content; MUST be first — empty-RCF fails closed until
   the guard relaxes). Then 2→6; Slice 7 (RCF→RSF sweep) is issue-filed and needs fresh
   ask-before-run captures. Diagnosis CORRECTED: coverage was already advisory; the real
   teeth is RCF pinned to a doc filename → assert emitted TOKENS via RSF instead.
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
