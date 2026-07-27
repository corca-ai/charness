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
— read it before planning any of them. **23 OPEN + 5 PARTIAL remain** (the
earlier "20" folded PARTIAL rows in as landed — count them apart). `2.11.3` is
published and all work is pushed. No decisions pending.

## Current State

- **CI is the only judge of the changed-line mutation gate here.** Its local run
  outruns a usable timeout and returns `untrusted` when HEAD moves mid-run.
- **`2.11.3` shipped three gate tightenings that can turn a consuming repo red.**
  Remedies and the patch-not-major argument are in the notes.

## Next Session

1. **Fix the bug-hunt backlog.** Order: **D4/D6/D8** (distinct-channel and
   readback claims — north-star P4 itself, and D2's `--generate-notes` residual
   lands there), then **C1-C4/C6**, **A5/A6**, **B4/B5**, **A8/A9/A10**, **E**
   last (per-changed-file mutation discrimination is a contract change). Expect
   the fix to be the easy part: **five** slices running needed review defects
   repaired *inside the fix*, and the publish-gate slice's own D1 fix reproduced
   D1. Check who really calls a gate before tightening it.
2. **A3 is PARTIAL: scheduled is not judged.** Only `check_staged_mirror_drift`
   reads the index; the rest walk the worktree, and `git revert` runs no
   pre-commit hook (probed). [A3 critique](../charness-artifacts/critique/2026-07-27-a3-staged-scope.md) F8/F9.
3. **Two deferrals from the containment slice**
   ([critique](../charness-artifacts/critique/2026-07-27-provenance-containment.md)
   F9/F10): `capability_catalog_resolver` ranks `repo-plugin-export` above
   `repo-public-skill`, so the documented skill-path recovery hands back the copy
   the provenance guard refuses mid-`mutate -> sync`; and the export-layout fact
   lives in three places in `helper_provenance_lib.py`.
4. **The drafter cannot see whether a staleness check ran** — the `staleness`
   block dies before `ChunkCandidate`, so the auto-draft cannot tell "checked,
   none closed" from "never asked". Detail in the F9 critique below.
5. **D28 remainder** (`emit_payload_main --write`, scaffold fill guards; the fill
   guards want an observed n-fold rework instance first).
6. **Suite speed.** 11756 spawns, git 68% (`rev-parse` 1322, `ls-files` 774).
   In-process `run_script` is the unmeasured lever; spawn count is the honest
   metric, 16-worker wall-clock is noise.
7. **Sibling-scan Tier 2 finding D** (operator-scheduled): two tests snapshot the
   real shared `.charness/usage-episodes/` tree, so a live hook or concurrent
   `run-quality.sh` fails them for unrelated reasons — needs design, detail in the
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
  tooth that works is making the skip LOUD. Set floors at or below observed
  honest usage or you buy padding.
- **Fenced text is shown, not asserted.** Two gates read it as the author's own
  claim; one was a false PASS at publish. Strip code before judging content.

## References

- [F9 critique](../charness-artifacts/critique/2026-07-27-handoff-auto-draft-stale-citation-markers-f9.md) · [chunked-routing contract](./handoff-chunked-routing.md) · [deferred decisions](./deferred-decisions.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [empty-scope critique](../charness-artifacts/critique/2026-07-27-empty-scope-family.md) · [issues 460/461/463 critique](../charness-artifacts/critique/2026-07-27-issues-460-461-463.md) · [artifact policy](./artifact-policy.md)
