# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Big picture:** skills satisfy two axes, evals verify each SEPARATELY —
  **correctness** (claim-fidelity, proven by live capture) and **efficiency** (advisory).

## Current State

- **Reference-compaction Slices 1–6 DONE; Slice 7 (#410) UNDERWAY.** S1 keystone (RCF-or-RSF
  guard, `## Closeout Vocabulary`, `classTag`); S5 (`3c5c8657`) proved the impl RCF→RSF pattern.
  **S7 create-cli DONE (`323f14a6`): FLOOR PASS, RSF=[`version`] OBSERVED (not in prompt),
  command-conventions.md→DEPTH, RCF 3-entry, +quality-gates.md nit; fresh-eye SHIP.** Residual:
  `check_skill_surface_preflight.py` near its code-line cap — extract helpers before next add.
  [contract](../charness-artifacts/reference-compaction/contract.md) · [plan.json](../charness-artifacts/reference-compaction/plan.json).
- **#409 DONE (`9d4c2882`).** capture→grade preserves evidence for committing/clean
  runs (diff vs capture base, transcript from `stream.jsonl`). Sweep reuse unblocked.
- impl capture (5th sweep skill): floor **MISS** (0/8), substance **4/5**
  (`honest-categorized-closeout` FAIL — the enum lives ONLY in `verification-ladder.md`,
  not inlined). The impl closeout-vocab fork is now RESOLVED into the keystone (Option A).
  [finding](../charness-artifacts/cautilus/impl-claim-fidelity-2026-07-01/finding.md)
- PROVEN floors: retro, hitl, quality, debug (n=2), impl (n=1, new emitted-token floor).
  ~13 uncaptured.

## Next Session

1. **Reference-compaction Slice 7 sweep — see #410.** Per-skill RCF→RSF, each its own
   gate-clean slice needing a FRESH ask-before-run capture to re-baseline the RSF token (S5
   lesson: do NOT assume). **DONE: create-cli.** REMAINING: hotl, handoff, setup (normalization
   only; greenfield-flow.md + default-surfaces.md STAY RCF-pinned), critique (ceiling + dual-spec),
   achieve (conditional), **hitl (CONTESTED — chunk-contract.md holds a rubric beyond the
   disposition enum; the capture must confirm the RCF drop is not over-relaxation)**, gather
   (capture fetches an external URL → needs sandbox network). Proven mechanics: `capture-skill-run.sh`
   needs an ABSOLUTE `--out-dir`; grade the mjs `--stream stream.jsonl`; scrub worktree/credentials
   from the bundle before commit; run broad pytest BEFORE the critique (grep misses path-built
   consumers, e.g. [test_skill_lesson_durability.py](../tests/quality_gates/test_skill_lesson_durability.py)).
2. **Continue correctness sweep** one skill at a time, reusing outcome-assertions.
   Remaining HYPOTHESIS-floor: achieve, announcement, create-cli, create-skill, critique,
   find-skills, gather, handoff, hotl, ideation, narrative, release, spec. A miss =
   skill-shape signal (re-pin/re-classify/planner), never soften the matcher.
3. **AGENTS.md lesson-internalization live capture (operator-raised)** — does AGENTS.md make
   an agent READ+ACT on recent-lessons? = the deferred "live-session capture unit" of the
   existing `lesson-internalization-claim-fidelity` eval (offline instrument DONE; #3 unblocks
   the capture side). Spec-level: arbitrary-session harness + vacuous-pass guard + rotation.

## Discuss

- Brittle test: [test_handoff_plan.py](../tests/test_handoff_plan.py)
  `..._derives_refresh_and_pickup` reds broad pytest on any >=60-line handoff. Keep this
  file under 60 lines until the test is decoupled from live state.

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [reference-compaction contract](../charness-artifacts/reference-compaction/contract.md)
- proofs: [cautilus latest](../charness-artifacts/cautilus/latest.md) · [impl finding](../charness-artifacts/cautilus/impl-claim-fidelity-2026-07-01/finding.md)
