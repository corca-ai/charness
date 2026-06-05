# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**. Bare
  `/handoff` runs chunked routing over handoff entries plus live open issues;
  `## Next Session` is sequencing judgment, not the full queue.
- Refresh: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **v0.22.0 is shipped and verified.** Tag `v0.22.0` at `a50cf8b3`, GitHub
  release live and marked latest, all version surfaces at 0.22.0, and #302–#305
  closed (via push close-keywords). Release:
  <https://github.com/corca-ai/charness/releases/tag/v0.22.0>.
  Release content: gather agent-browser close + clean-runtime proof (#302),
  setup adapter-first reviewer rule (#303), setup delegation line-wrap agreement
  (#304), release publish resilience (#305). Minor bump (one additive `feat`).
- Critique: bounded fresh-eye release critique (3 angle + 1 counterweight) at
  [v0.22.0 release critique](../charness-artifacts/critique/2026-06-05-v0.22.0-release-critique.md).
- The `--release` gate surfaced **pre-existing committed debt** in the #302–#305
  work (issue anchors in portable skill scripts; 3 debug artifacts in a
  non-canonical structure; stale debug seam-risk index). Fixed in `f17e3e8e`;
  `./scripts/run-quality.sh --release` then passed 72/0.
- Publish tooling friction (worked around, filed as #312): the happy-path
  `publish_release.py --execute` raced a usage-episode test via its
  `run_slice_closeout` wrapper, and `--resume` left an uncommitted `latest.md`
  that the pre-push hook blocked. Completed via the repo push path directly
  (`git push origin main v0.22.0` → pre-push gate 71/0 → `gh release create`).

## Next Session

1. New follow-ups filed this release: **#309** (cleanup-orphans dead-end for
   reparented/zombie residue), **#310** (gather acquire error clobber, pre-existing),
   **#311** (reviewer rule greenfield-only backfill), **#312** (release publish-flow
   resilience round 2 — resume `latest.md` ordering + closeout usage-episode race).
   Route through `find-skills` then `issue` to resolve.
2. Prior open work still outside this release: #184, #293, #294, #295, #296.
3. Do not reopen #302–#305 or the portable-skill goal unless current verification
   contradicts the shipped evidence.

## Discuss

- #312 should likely be fixed before the next release: both gaps (resume
  `latest.md` ordering and the closeout-wrapped quality usage-episode race) will
  recur and forced a manual push this time. The cleanest framing is that
  `run_slice_closeout`'s quality run should be read-only-safe (no live
  usage-episode writes during the suite), and `--resume` should commit its
  refreshed `latest.md` before pushing.
- The `--release` gate caught real debt the #302–#305 goal closeout missed
  because that closeout did not run the full `--release` gate. Worth deciding
  whether goal closeout should run the release gate when the work targets a
  release surface, rather than discovering it at publish time.

## References

- [v0.22.0 release critique](../charness-artifacts/critique/2026-06-05-v0.22.0-release-critique.md),
  [release latest](../charness-artifacts/release/latest.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md),
  [quality latest](../charness-artifacts/quality/latest.md)
- [#302–#305 robustness goal](../charness-artifacts/goals/2026-06-05-302-305-gather-setup-release-robustness.md)
