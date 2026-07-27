# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog; an explicit user task keeps its own authority. Pick the smallest coherent
  slice and close it end-to-end: mutate canonical source, sync generated/plugin
  mirrors before validators, then prove with the mandated bounded critique.

## Continuation Capability

One open issue (#459). The 2026-07-27 goal run closed #457 and #458 and the four
in-scope backlog items; [its goal artifact](../charness-artifacts/goals/2026-07-27-handoff-backlog-minus-aarch64.md)
holds the slice log, non-claims, and two operator decisions.

## Current State

- **Verify a backlog line against source before planning it.** Three of five
  entries last run were stale and a fourth was work that already shipped; the plan
  was rewritten twice. #459 exists to make that checkable at chunk time. Until it
  lands, open the cited path first.
- **The lesson loop has a BIND path now.** `recurrence-class:` tags group a concept
  across wordings and sections, and the weighting was re-derived so recurrence can
  outrank recency. Live proof: `premise-not-checked-against-source` already sits at
  n=2, weight 1.24, above every 1.0 one-off. It only accrues from tagged retros.
- **CI is the only judge of the changed-line mutation gate here.** Its local
  reproduction outruns a usable timeout on this machine and returns `untrusted`
  when HEAD moves mid-run. A local green is not evidence; the first push proved it.
- Two operator decisions are queued in the goal artifact: whether debug/critique
  flip to one-pass-by-default (reversing an explicit narrowing, so not an agent's
  call), and whether sibling-scan Tier 2 finding D becomes its own slice.

## Next Session

1. **#459 — chunker-side backlog staleness.** The entry model already parses
   `referenced_paths` and `referenced_issues`; report which no longer resolve, as
   facts and never an auto-drop. This is the direct fix for the waste that cost the
   most last run.
2. **`local-linux-aarch64-4cpu` has still never run on aarch64 hardware.** Excluded
   by operator decision last run and unchanged: owed the real box, where
   `check_runtime_budget.py --runtime-profile local-linux-aarch64-4cpu
   --suggest-budgets` replaces a block that still has no aggregate bar behind its
   eight per-gate bars. The 4-core x86_64 read-only window still holds one red.
3. **Suite speed beyond the git-identity fix.** Measured census: 11756 spawns, git
   still 68% — `rev-parse` 1322, `ls-files` 774, `add` 672, `commit` 581, `init`
   535. The in-process `run_script` lever named by the previous handoff is
   unmeasured and remains open. Spawn count is the honest metric; wall-clock at 16
   workers is noise.
4. Unowned/deferred (signed off): the [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
   Tier 2/3 only — its Tier 1 is fixed and the artifact now says so.

## Discuss

- A named subagent spawn strands its result on this host, and the rule now lives in
  always-loaded `AGENTS.md` for every spawn. If findings never arrive, run
  `reviewer_result.py get` before reporting them lost — that diagnostic recovered a
  full review last run after it had been written off.
- Editing structured code with line patterns corrupted files twice, and an
  unanchored `str.index` on a heading deleted six artifact sections a third time.
  Use AST or line-anchored matching and re-parse before writing.

## References

- [goal artifact](../charness-artifacts/goals/2026-07-27-handoff-backlog-minus-aarch64.md) · [session retro](../charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md) · [named-spawn recurrence](../charness-artifacts/debug/2026-07-27-named-spawn-recurrence.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
