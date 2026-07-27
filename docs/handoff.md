# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog; an explicit user task keeps its own authority. Pick the smallest coherent
  slice and close it end-to-end: mutate canonical source, sync generated/plugin
  mirrors before validators, then prove with the mandated bounded critique.

## Continuation Capability

Closed #460/#461/#463, then an evidence-surface bug hunt reproduced **30
defects** across the repo's proof surfaces; the empty-scope family (A4, A7, C5;
E2 partial) and the containment family (A1, A2; A9 partial) are fixed. Every
item, fixed or open, carries status, file:line, and a confirmed repro in the
[bug hunt record](../charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md)
— read it before planning any of them. The operator's standing decision is **no
push and no release until they are fixed**, so four commits sit local. No
GitHub issues are open (the three close on push). No decisions pending.

## Current State

- **The chunker reports staleness facts before ranking, and the auto-draft
  renders them.** Markers come from non-empty facts only, so an unmarked
  citation is never a freshness claim. Shipped in `2.11.2`.
- **CI is the only judge of the changed-line mutation gate here.** Its local run
  outruns a usable timeout and returns `untrusted` when HEAD moves mid-run.

## Next Session

1. **Fix the bug-hunt backlog; 23 items remain.** Next: **B1-B3** (the
   issue-close carrier, where a false PASS closes a real issue on GitHub), then
   **A5/A6**, which sit inside the commit-boundary floor A3 just restored and
   decide what it is worth. Expect the fix to be the easy part: three slices in a
   row needed review defects repaired *inside the fix*. Check who really calls a
   gate before tightening it.
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
4. **The drafter cannot see whether a staleness check ran.** The parser's
   top-level `staleness` block dies at `materialize_chunk_proposal_response`
   and the ranker packet — `ChunkCandidate` has no field for it. So the
   auto-draft marks positively-reported staleness (F9, now closed) but cannot
   distinguish "issue states checked, none closed" from "never asked". The
   path check always runs; the residual is issue citations only, because the
   issue check is gated behind `--with-issues`.
5. **D28 remainder** (`emit_payload_main --write`, scaffold fill guards); fill
   guards want an observed n-fold rework instance first.
6. **Suite speed.** 11756 spawns, git 68% (`rev-parse` 1322, `ls-files` 774,
   `add` 672). In-process `run_script` is the unmeasured lever; spawn count is
   the honest metric, 16-worker wall-clock is noise.
7. **Sibling-scan Tier 2 finding D** (operator-scheduled). Two tests snapshot the
   real shared `.charness/usage-episodes/` tree, so a live hook or a concurrent
   `run-quality.sh` fails them for unrelated reasons; needs design, detail in the
   [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md).

## Discuss

- Run release/skill helpers from `skills/public/.../scripts/`, NOT an installed
  or `plugins/` copy: an older lesson-index schema gets rejected mid-publish. The
  provenance guard refuses both cases now, but it lives in the copy you invoke,
  so a copy predating it carries no check —
  [RCA](../charness-artifacts/debug/2026-07-27-absent-guard-not-dead-guard.md).
- Skill loaders build a FRESH module object per import, with no `sys.modules`
  caching. Reading a module global back across a second load silently sees the
  unmutated copy; thread the value through explicitly instead.

## References

- [F9 critique](../charness-artifacts/critique/2026-07-27-handoff-auto-draft-stale-citation-markers-f9.md) · [chunked-routing contract](./handoff-chunked-routing.md) · [deferred decisions](./deferred-decisions.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [empty-scope critique](../charness-artifacts/critique/2026-07-27-empty-scope-family.md) · [issues 460/461/463 critique](../charness-artifacts/critique/2026-07-27-issues-460-461-463.md) · [artifact policy](./artifact-policy.md)
