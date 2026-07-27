# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog; an explicit user task keeps its own authority. Pick the smallest coherent
  slice and close it end-to-end: mutate canonical source, sync generated/plugin
  mirrors before validators, then prove with the mandated bounded critique.

## Continuation Capability

One open issue (#459). The 2026-07-27 goal run closed #457/#458 and four backlog
items; [its goal artifact](../charness-artifacts/goals/2026-07-27-handoff-backlog-minus-aarch64.md) holds the slice log and non-claims. No decisions pending.

## Current State

- **Verify a backlog line against source before planning it.** Three of five entries
  last run were stale and a fourth already shipped; the plan was rewritten twice.
  #459 makes it checkable; until then, open the cited path first.
- **The lesson loop has a BIND path now.** `recurrence-class:` tags group a concept
  across wordings and dates; live proof, `premise-not-checked-against-source` sits
  at n=2, weight 1.24, above every 1.0 one-off. It accrues only from tagged retros.
- **CI is the only judge of the changed-line mutation gate here.** Its local run
  outruns a usable timeout and returns `untrusted` when HEAD moves mid-run.

## Next Session

1. **Unify the artifact-validator CLI — operator-decided, A+B+C.** A: flip
   debug/critique to one-pass default. B: `--fail-fast` becomes the only control,
   `--report-all` a deprecated no-op (per `validate_quality_artifact.py`). C:
   single-source through `artifact_validator.run_changed_artifact_validator` so the
   split cannot re-form — critique's `--changed-ref` and per-path
   `require_tier_evidence` are real work the helper does not model. Update D28.
2. **#459 — chunker-side backlog staleness.** The entry model already parses
   `referenced_paths` and `referenced_issues`; report which no longer resolve, as
   facts and never an auto-drop. Direct fix for the waste that cost the most
   last run.
3. **Re-base this file's cap on CONTENT lines — operator-decided.** Count only
   content: exclude blank lines, the validator-required `##` headings, and the
   `## References` block; recalibrate to an effective ~55-60. Measured basis: 13 of
   the last 14 committed handoffs landed at 69-70 against a cap of 70 (a pinned
   distribution), and structure alone eats ~24% of the budget, so long reference
   links are penalised while a diary of short lines is not. `MAX_ARTIFACT_LINES` in
   `validate_handoff_artifact.py`; an operating-contract change, so move the skill's
   stated 30-60 target with it.
4. **Suite speed beyond the git-identity fix.** Census: 11756 spawns, git still 68%
   (`rev-parse` 1322, `ls-files` 774, `add` 672). The in-process `run_script` lever
   is unmeasured. Spawn count is the honest metric; 16-worker wall-clock is noise.
5. **Sibling-scan Tier 2 finding D** (operator-scheduled). Two tests snapshot the
   real shared `.charness/usage-episodes/` tree and assert byte-identity after a CLI
   subprocess, so a live SessionStart hook or concurrent `run-quality.sh` fails them
   for unrelated reasons. Needs design; detail in the
   [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md).

## Discuss

- A named subagent spawn strands its result on this host; the rule now lives in
  always-loaded `AGENTS.md` for every spawn. If findings never arrive, run
  `reviewer_result.py get` before reporting them lost — it recovered a full review.
- Editing structured code with line patterns corrupted files twice, and an
  unanchored `str.index` on a heading deleted six artifact sections a third time.
  Use AST or line-anchored matching and re-parse before writing.

## References

- [goal artifact](../charness-artifacts/goals/2026-07-27-handoff-backlog-minus-aarch64.md) · [session retro](../charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md) · [named-spawn recurrence](../charness-artifacts/debug/2026-07-27-named-spawn-recurrence.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
