# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog; an explicit user task keeps its own authority. Pick the smallest coherent
  slice and close it end-to-end: mutate canonical source, sync generated/plugin
  mirrors before validators, then prove with the mandated bounded critique.

## Continuation Capability

Closed #460/#461/#463, then an evidence-surface bug hunt reproduced **30
defects** across the repo's proof surfaces; the empty-scope family (A4, A7, C5;
E2 partial), the containment family (A1, A2; A9 partial), A3 partial, and the
issue-close carrier family (B3; B2 narrowed, B1 partial) are fixed. Every item,
fixed or open, carries status, file:line, and a confirmed repro in the
[bug hunt record](../charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md)
— read it before planning any of them. **20 remain.** The no-push hold is lifted:
all work is pushed and **`2.11.3` is published** (tag `v2.11.3`, installed
readback compared, not just observed). No decisions pending.

## Current State

- **CI is the only judge of the changed-line mutation gate here.** Its local run
  outruns a usable timeout and returns `untrusted` when HEAD moves mid-run.
- **`2.11.3` shipped three gate tightenings that can turn a consuming repo red.**
  Remedies and the patch-not-major argument are in the notes.

## Next Session

1. **Fix the bug-hunt backlog; 20 items remain.** Next: **A5/A6**, which sit
   inside the commit-boundary floor A3 restored and decide what it is worth, then
   **D1/D5** (the publish gate and the only standing release-version
   cross-check). Expect the fix to be the easy part: **four** slices in a row
   needed review defects repaired *inside the fix* — B1-B3's reviewers caught a
   branch removed as "redundant" that dropped two bug-only floors. Check who
   really calls a gate, and what a shared predicate's other callers expect.
2. **A3 is PARTIAL: scheduled is not judged.** A deletion schedules its surface
   gates now, but only `check_staged_mirror_drift` reads the index — the rest walk
   the worktree, and `git revert` runs no pre-commit hook at all (probed).
   [A3 critique](../charness-artifacts/critique/2026-07-27-a3-staged-scope.md) F8/F9.
3. **Two deferrals from the containment slice**
   ([critique](../charness-artifacts/critique/2026-07-27-provenance-containment.md)
   F9/F10). `capability_catalog_resolver` ranks `repo-plugin-export` above
   `repo-public-skill`, so the documented skill-path recovery hands back the copy
   the provenance guard now refuses mid-`mutate -> sync`. And the export-layout
   fact lives in three places in `helper_provenance_lib.py`.
4. **The drafter cannot see whether a staleness check ran** — the parser's
   `staleness` block dies before `ChunkCandidate`, so the auto-draft cannot tell
   "checked, none closed" from "never asked". Issue citations only; detail in the
   F9 critique below.
5. **D28 remainder** (`emit_payload_main --write`, scaffold fill guards; the fill
   guards want an observed n-fold rework instance first).
6. **Suite speed.** 11756 spawns, git 68% (`rev-parse` 1322, `ls-files` 774).
   In-process `run_script` is the unmeasured lever; spawn count is the honest
   metric, 16-worker wall-clock is noise.
7. **Sibling-scan Tier 2 finding D** (operator-scheduled). Two tests snapshot the
   real shared `.charness/usage-episodes/` tree, so a live hook or concurrent
   `run-quality.sh` fails them for unrelated reasons; needs design, detail in the
   [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md).

## Discuss

- Run release/skill helpers from `skills/public/.../scripts/`, NOT an installed
  or `plugins/` copy: an older lesson-index schema gets rejected mid-publish. The
  guard lives in the copy you invoke, so a copy predating it carries no check —
  [RCA](../charness-artifacts/debug/2026-07-27-absent-guard-not-dead-guard.md).
- Skill loaders build a FRESH module object per import, with no `sys.modules`
  caching. Reading a module global back across a second load silently sees the
  unmutated copy; thread the value through explicitly instead.
- **A length floor is not a proof floor.** No length refuses a fluent excuse; the
  tooth that works is making the skip LOUD. Set length floors at or below
  observed honest usage (real host signals run 24-39 chars) or you buy padding.

## References

- [F9 critique](../charness-artifacts/critique/2026-07-27-handoff-auto-draft-stale-citation-markers-f9.md) · [chunked-routing contract](./handoff-chunked-routing.md) · [deferred decisions](./deferred-decisions.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [empty-scope critique](../charness-artifacts/critique/2026-07-27-empty-scope-family.md) · [issues 460/461/463 critique](../charness-artifacts/critique/2026-07-27-issues-460-461-463.md) · [artifact policy](./artifact-policy.md)
