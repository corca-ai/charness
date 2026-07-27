# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog; an explicit user task keeps its own authority. Pick the smallest coherent
  slice and close it end-to-end: mutate canonical source, sync generated/plugin
  mirrors before validators, then prove with the mandated bounded critique.

## Continuation Capability

One open issue (#459). The 2026-07-27 goal run closed #457 and #458 and the four
in-scope backlog items; [its goal artifact](../charness-artifacts/goals/2026-07-27-handoff-backlog-minus-aarch64.md)
holds the slice log, non-claims, and the decision record. No decisions are pending.

## Current State

- **Verify a backlog line against source before planning it.** Three of five
  entries last run were stale and a fourth was work that already shipped; the plan
  was rewritten twice. #459 exists to make that checkable at chunk time. Until it
  lands, open the cited path first.
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
   `require_tier_evidence` are the real work and the helper does not model them.
   Basis: the rule-count split in `a930cc5f`/D28 no longer matches the code
   (critique 3 checks, handoff 7), and CI already passes `--report-all`. Update D28.
2. **#459 — chunker-side backlog staleness.** The entry model already parses
   `referenced_paths` and `referenced_issues`; report which no longer resolve, as
   facts and never an auto-drop. This is the direct fix for the waste that cost the
   most last run.
3. **`local-linux-aarch64-4cpu` has still never run on aarch64 hardware.** Owed the
   real box, where `check_runtime_budget.py --runtime-profile
   local-linux-aarch64-4cpu --suggest-budgets` replaces a block with no aggregate
   bar behind its eight per-gate bars. The 4-core x86_64 window still holds one red.
4. **Suite speed beyond the git-identity fix.** Census: 11756 spawns, git still 68%
   — `rev-parse` 1322, `ls-files` 774, `add` 672, `commit` 581, `init` 535. The
   in-process `run_script` lever is unmeasured and open. Spawn count is the honest
   metric; wall-clock at 16 workers is noise.
5. **Sibling-scan Tier 2 finding D** (operator-scheduled). Two tests snapshot the
   real shared `.charness/usage-episodes/` tree and assert it is byte-identical
   after a CLI subprocess, so a live SessionStart hook or concurrent
   `run-quality.sh` fails them for reasons unrelated to the SUT. Needs design: fence
   the delta to paths the test could have created, or use a copied tree. Detail and
   the fixed Tier 1 in the [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md).

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
