# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog; an explicit user task keeps its own authority. Pick the smallest coherent
  slice and close it end-to-end: mutate canonical source, sync generated/plugin
  mirrors before validators, then prove with the mandated bounded critique.

## Continuation Capability

Two records drive this work. The
[2026-07 hunt](../charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md)
reproduced 30 defects over 22 surfaces; **9 OPEN + 4 PARTIAL remain**. The
[triage sweep](../charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md)
first-looked the other 146 surfaces: **105 leads still open**, 34 high severity.
It now carries a `CLOSED (parent-reproduced <date>)` status — the ONLY status that
means a row is done. Read its status vocabulary before citing any row.

## Current State

- **The burn-down is the work, and 6 rows closed this session** (S6, S19, S20, S93
  from the sweep; C3 and both C-slice siblings from the hunt). Each was reproduced
  in the parent before anything changed, and each has a test that fails on revert.
- **`dup-ratchet` is green.** It failed identically on the session's base commit
  in a pristine worktree; the 6 families were the artifact validators' copied
  section readers, which now live in one home each
  ([markdown sections](../scripts/markdown_sections.py),
  [structured-entry floor](../scripts/structured_entry_floor.py)). 83 of 83 gates pass.
- **The fix keeps reproducing the defect: 9 of 9 slices.** Both reviews this session
  found the fix carrying the class it fixed — a widened trigger reading prose as a
  path, a consolidated reader fence-blind while its own caller was not, and S19
  fixed at the gather entrypoint while the generic pointer writer kept the hole.
  Budget for review AND for the repair round after it.
- **C6 stays PARTIAL by decision, not omission.** The committed-range/worktree
  union was written, reviewed and reverted: the boundary tooth is a HARD refusal,
  so any unrelated dirty library file would refuse every selected critique.
- **#464's blocking signal is a moving 12h window**, so its rows self-clear; every
  line its live comment named is covered now, measured in-process. CI stays the only
  judge of that gate — the local run outruns a usable timeout.

## Next Session

1. **Work the sweep's remaining 34 high-severity rows, reproducing each first.**
   Class (a) is still the dominant shape; S27/S33/S34 (quality dup/nose readers
   returning clean over zero families) are the next coherent batch. **S29 is
   reproduced but NOT fixed** — an empty scan inventory reads as `clean`; it needs
   care because this session re-baselined that gate.
2. **The original hunt's A5/A6, A8/A9/A10, B4/B5** (**E last** — per-changed-file
   mutation discrimination is a contract change).
3. **A3 is PARTIAL: scheduled is not judged.** Only `check_staged_mirror_drift`
   reads the index; the rest walk the worktree, and `git revert` runs no pre-commit
   hook (probed). Needs a live staged/revert probe, not fixtures.
   [A3 critique](../charness-artifacts/critique/2026-07-27-a3-staged-scope.md) F8/F9.
4. **D4 is PARTIAL and cannot be closed by this channel.** A pushed tag with no
   release returns 200 with the tag present. Needs a release-specific channel
   independent of unauthenticated API quota — a design decision before code.
5. **Containment-slice deferrals** F9/F10, **D28 remainder** and **sibling-scan
   Tier 2 finding D** are unchanged and still un-dispositioned.

## Discuss

- **Fenced text is shown, not asserted.** Four gates have now read it as the
  author's claim. The shared section reader blanks fences; the sibling readers that
  locate their own heading still do not.
- **A widened content trigger buys a false refusal**, twice proven this session.
  Read the declared VALUE and require its shape, not the line.
- **A dead allowlist row is worse than none**: it reads as a live decision. Its
  test agreed with it because the test had reconstructed a file the corpus lacks.
- Run release/skill helpers from `skills/public/.../scripts/`, NOT an installed
  or `plugins/` copy ([RCA](../charness-artifacts/debug/2026-07-27-absent-guard-not-dead-guard.md)).

## References

- [chunked-routing contract](./handoff-chunked-routing.md) · [deferred decisions](./deferred-decisions.md) · [design north star](./design-north-star.md)
- [why the class stayed invisible](../charness-artifacts/audit/2026-07-28-why-the-hunt-class-stayed-invisible.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [C-cluster critique](../charness-artifacts/critique/2026-07-28-critique-evidence-floor-as-one-subsystem.md) · [publish-gate critique](../charness-artifacts/critique/2026-07-27-publish-gate-d1-d2-d3-d5.md) · [distinct-channel critique](../charness-artifacts/critique/2026-07-28-distinct-channel-d4-d6-d8.md)
