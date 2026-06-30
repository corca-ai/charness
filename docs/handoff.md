# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Big picture:** skills satisfy two axes, evals verify each SEPARATELY —
  **correctness** (claim-fidelity: does a run honor its claim? proven by live
  capture) and **efficiency** (process + output waste; advisory, never pass/fail).

## Current State

- **impl capture DONE (2026-07-01): 5th sweep skill.** Floor **MISS** (coverage 0/8,
  `verification-ladder.md` not opened); substance **4/5** (executed-verification +
  smallest-slice PASS; `honest-categorized-closeout` FAIL — the run produced the
  closeout in PROSE, not the canonical Lint-Gate/completion-report enum that lives
  ONLY in `verification-ladder.md` and is NOT inlined in SKILL.md). **impl stays
  HYPOTHESIS; floor + assertions un-softened.** New `outcome-assertions.json` landed.
  [finding](../charness-artifacts/cautilus/impl-claim-fidelity-2026-07-01/finding.md)
- **#409 filed — BLOCKS sweep reuse.** capture→grade loses outcome-grader evidence
  for clean/committing skills (`preserve_outputs` diffs vs HEAD but a faithful impl
  run COMMITS; tree transcript missed the final closeout block, `stream.jsonl` was
  complete). Worked around manually this run.
- PROVEN: retro, hitl, quality, debug (n=2). impl = 5th captured, HYPOTHESIS. ~13
  skills still uncaptured. Debug Plan-C (2026-06-30): `five-steps.md` retired from
  floor at n=2; `debug-memory.md` stays the floor.

## Next Session

1. **Fix #409 FIRST — it unblocks the sweep.** `preserve_outputs` should diff vs the
   capture ref (not HEAD); build the transcript from `stream.jsonl` (not the truncated
   tree); add a cheap evidence-pipeline preflight before expensive captures. Until
   fixed, substance grading of any committing/clean skill needs the manual workaround.
2. **Continue the correctness sweep**, one skill at a time, REUSING the
   outcome-assertion pattern. Remaining HYPOTHESIS-floor skills: achieve, announcement,
   create-cli, create-skill, critique, find-skills, gather, handoff, hotl, ideation,
   narrative, release, spec. A miss = skill-shape signal (re-pin/re-classify/planner),
   never soften the matcher. `--justification-log` overrides `next_action: none`.
3. **Operator decision: impl closeout-vocabulary fork.** Internalize the enum into
   `impl/SKILL.md` (debug-Plan-A-style → floor weak proxy + substance pass) vs keep
   `verification-ladder.md` load-bearing (the MISS is a real gap). Candidate issue.
4. **AGENTS.md-level lesson-internalization fixture (operator-raised)** — still open;
   judge whether a prior recent-lessons lesson was internalized by a later session.

## Discuss

- Threshold policy RESOLVED: per-skill `max_duration_ms` from a PASSING capture (~2x).
  impl left UNSET (floor not passed); 123821ms natural-completion recorded for a PASS.
- Brittle test: [test_handoff_plan.py](../tests/test_handoff_plan.py)
  `..._derives_refresh_and_pickup` reads the LIVE handoff and reds broad pytest on any
  near-limit (>=60 line) handoff. Deeper fix: decouple the test from live mutable state.

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [quality latest](../charness-artifacts/quality/latest.md)
- proofs: [cautilus latest](../charness-artifacts/cautilus/latest.md) · [impl finding](../charness-artifacts/cautilus/impl-claim-fidelity-2026-07-01/finding.md) · [impl retro](../charness-artifacts/retro/2026-07-01-correctness-sweep-next-floor-closeout.md)
