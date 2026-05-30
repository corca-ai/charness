# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` → **invoke `charness:handoff`**. A bare
  `/handoff` now fires chunked routing too (#249), and the chunker unions the
  **live open-issue backlog** with the entries below — so this list is a
  curation/sequencing memo, not the full queue. Then read
  [quality latest](../charness-artifacts/quality/latest.md) +
  [recent lessons](../charness-artifacts/retro/recent-lessons.md).
- Refresh: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) +
  [operating contract](./conventions/operating-contract.md).

## Current State

- **`main` is ahead of `origin/main` by 5 commits — UNPUSHED.** This session's
  work is local only; push/PR is a maintainer decision.
- **#253 improvement-disposition gate SHIPPED** (goal
  [`2026-05-30-253`](../charness-artifacts/goals/2026-05-30-253-improvement-disposition-gate.md),
  Status: complete; dogfooded its own closeout). Two-rung "gate + 지능": rung-1
  deterministic floor (block-the-blank + bound `Disposition review:` line,
  grandfathered by `Created >= 2026-05-30`) in new leaf module
  `goal_artifact_disposition.py`; rung-2 fresh-eye reviewer records a
  per-improvement verdict. **GitHub #253 still OPEN** — close after push.
- **#256 + #257 SHIPPED + CLOSED** (closeout-ergonomics gates): a length-headroom
  advisory (`check_python_lengths --headroom`) auto-surfaced by
  `run_slice_closeout.py` (#256); a hard pre-commit `check_staged_mirror_drift.py`
  blocking staged source without its synced `plugins/` mirror (#257). pkill
  command-hygiene recorded in
  [implementation-discipline.md](./conventions/implementation-discipline.md).
- **v0.12.0 real-host proof still pending** (clean-machine) — carried forward.

## Next Session

> A bare `/handoff` unions the tracker — so chunk the live backlog rather than
> trusting this list. This memo carries only cross-issue judgment.

1. **#255 — `is_non_trivial_goal` full-text marker poisoning (good `/achieve`
   candidate).** Pre-existing bug found while shipping #253; well-scoped in the
   issue (fix: scope the `_TRIVIAL_GOAL_MARKER` scan to the `## Slice Plan`
   section, mirroring how #253 scoped its opt-out to the Auto-Retro span). Same
   `goal_artifact_*` surface as #253 — context carries over.
2. **Push the 5 local commits**, then close GitHub #253 (fix is shipped locally
   but unpushed).
3. **usage-episodes / hooks cluster:** #244 (auto-wire find-skills SessionStart
   hook), #245 (cross-checkout hook dup), #243 (consumer/report gap). #244+#245
   both touch the host-hook installer.
4. **v0.12.0 real-host proof** (Cautilus clean-machine smoke) + remaining
   backlog: #242/#219 (mutation), #233, #241, #237/#236, #184/#185.

## Discuss

- **Issue-source non-gh path is unproven live** (stub-tested only). If a non-gh
  host adopts charness, exercise the `issue_backend.commands.list_open` override
  before trusting the backlog union there. Full session waste / decisions:
  [closeout retro](../charness-artifacts/retro/2026-05-29-249-248-handoff-chunker-v2-closeout.md).

## References

- [quality posture](../charness-artifacts/quality/latest.md),
  [chunker contract](./handoff-chunked-routing.md),
  [release latest](../charness-artifacts/release/latest.md)
