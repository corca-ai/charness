# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog; an explicit user task keeps its own authority. Pick the smallest coherent
  slice and close it end-to-end: mutate canonical source, sync generated/plugin
  mirrors before validators, then prove with the mandated bounded critique.

## Continuation Capability

An evidence-surface bug hunt reproduced **30 defects** across the repo's proof
surfaces. Seven families have landed (empty-scope, containment, A3 partial,
issue-close carrier, publish-gate, distinct-channel, empty-scope remainder);
every item carries status, file:line and a confirmed repro in the
[bug hunt record](../charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md)
— read it before planning any of them. **16 OPEN + 5 PARTIAL remain.** Work is
pushed through `d0172d3b`; `2.11.3` is published. **One decision is open and it
changes how the rest are done — see Discuss, first item.**

## Current State

- **The fix keeps reproducing the defect: 6 of 6 slices so far.** Every slice's
  bounded review found defects *inside* that slice's fix, several of them the
  exact class being fixed (the D1 fence-blind fix, the E5 gate that its own fix
  hard-broke, the D7 scope that never reached the artifact). Fresh-eye review is
  the only mechanism in this run that caught the class reliably. Budget for it.
- **CI is the only judge of the changed-line mutation gate here.** Its local run
  outruns a usable timeout and returns `untrusted` when HEAD moves mid-run.

## Next Session

1. **Decide the structural question below FIRST**, then continue the backlog.
   Remaining order if the answer is "keep going per-instance": **C1-C4/C6** (the
   critique floors every other closeout leans on), **A5/A6**, **B4/B5**,
   **A8/A9/A10**, **E** last (per-changed-file mutation discrimination is a
   contract change, not a patch).
2. **A3 is PARTIAL: scheduled is not judged.** Only `check_staged_mirror_drift`
   reads the index; the rest walk the worktree, and `git revert` runs no
   pre-commit hook (probed). [A3 critique](../charness-artifacts/critique/2026-07-27-a3-staged-scope.md) F8/F9.
3. **D4 is PARTIAL and cannot be closed by this channel.** Measured: a pushed tag
   with NO release returns 200 with the tag present, and the tag is pushed before
   the release is created. Closing it needs a release-specific channel that does
   not depend on unauthenticated API quota.
4. **Two deferrals from the containment slice**
   ([critique](../charness-artifacts/critique/2026-07-27-provenance-containment.md)
   F9/F10): `capability_catalog_resolver` ranks `repo-plugin-export` above
   `repo-public-skill`, so the documented skill-path recovery hands back the copy
   the provenance guard refuses; and the export-layout fact lives in three places.
5. **D28 remainder** and **sibling-scan Tier 2 finding D** (operator-scheduled)
   are unchanged; see the [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md).

## Discuss

- **DECISION, and it changes how the rest are done: keep fixing per-instance, or
  make the structural move first?** The defects were introduced already broken,
  not decayed; D4 came in on the very commit implementing north-star P4, so
  *applying P4 produced a P4 violation*. They stayed invisible because a
  fail-open gate emits no signal by construction and because a gate's tests are
  written by its author in the same sitting. What the north star **forbids** as
  the remedy — one more gate that checks gates — and the candidate directions
  that remain are in the
  [invisibility record](../charness-artifacts/audit/2026-07-28-why-the-hunt-class-stayed-invisible.md).
  Read it before choosing; the choice is the operator's.
- **A length floor is not a proof floor.** No length refuses a fluent excuse; the
  tooth that works is making the skip LOUD. Set floors at or below observed
  honest usage or you buy padding.
- **Fenced text is shown, not asserted.** Two gates read it as the author's own
  claim; one was a false PASS at publish. Strip code before judging content.
- Run release/skill helpers from `skills/public/.../scripts/`, NOT an installed
  or `plugins/` copy — the guard lives in the copy you invoke
  ([RCA](../charness-artifacts/debug/2026-07-27-absent-guard-not-dead-guard.md)).

## References

- [chunked-routing contract](./handoff-chunked-routing.md) · [deferred decisions](./deferred-decisions.md) · [design north star](./design-north-star.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [publish-gate critique](../charness-artifacts/critique/2026-07-27-publish-gate-d1-d2-d3-d5.md) · [distinct-channel critique](../charness-artifacts/critique/2026-07-28-distinct-channel-d4-d6-d8.md) · [empty-scope remainder critique](../charness-artifacts/critique/2026-07-28-empty-scope-remainder-d7-d9-d10-e5.md)
