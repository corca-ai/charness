# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Big picture:** skills satisfy two axes, evals verify each SEPARATELY —
  **correctness** (claim-fidelity, proven by live capture) and **efficiency** (advisory).

## Current State

- **Reference-compaction Slice 7 sweep DONE — all 8 skills captured + decided (#410 summary
  comment).** 3 clean MOVES (create-cli `323f14a6` RSF=`version`; achieve `cf0edb5f`
  RSF=`charness-artifacts/goals` +new substance judge; hitl `1397731a` flaky doc-open retired →
  existing judge). 3 keep-PROVEN (hotl `65d12860`; handoff `92d7f2aa` +document-seams.md DUP delete;
  critique `4fc6389c`). 2 REFUTED → redesign (gather **#411**, setup **#413**; script-driven,
  0-coverage). Each: fresh ask-before-run capture graded vs `stream.jsonl` + fresh-eye SHIP +
  gate-clean commit. **Meta-finding: Move C fits only inlined-token OR has-substance-judge skills;
  SKILL/script-driven + load-bearing-authority skills are keeps/refutes, not token moves.** Also
  filed **#412** (handoff planner over-requires continuation-sequence.md).
  [contract](../charness-artifacts/reference-compaction/contract.md).
- PROVEN floors now: create-cli/achieve/hitl/hotl/handoff(×3)/critique(×2) + prior
  retro/quality/debug/impl. Remaining HYPOTHESIS-floor: announcement, create-skill, find-skills,
  ideation, narrative, release, spec.

## Next Session

1. **Slice-7 residual follow-ups.** **#411** (gather) + **#413** (setup): floor REDESIGN to an
   artifact/substance instrument (add `outcome-assertions.json` + `output_glob`) — same class, a
   script-driven skill has no honest doc-routing floor. **#412**: conditionalize the handoff planner's
   continuation-sequence.md pickup read. Non-blocking matcher nuance: the RCF command-log matcher
   counts a reference filename NAMED IN A SUBAGENT PROMPT as engagement (seen in critique-decision).
2. **Continue correctness sweep** for the remaining untested HYPOTHESIS floors (announcement,
   create-skill, find-skills, ideation, narrative, release, spec), one at a time — expect
   keeps/refutes, not just moves. Mechanics: `capture-skill-run.sh` needs an ABSOLUTE `--out-dir`;
   grade mjs `--stream stream.jsonl`; scrub the worktree/config before ANY commit — its
   `config/settings.json` pollutes repo-wide `check_doc_links` (never commit while a capture is live);
   broad pytest BEFORE the critique (grep misses path-built consumers, e.g.
   [test_handoff_skill.py](../tests/quality_gates/test_handoff_skill.py)).
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
