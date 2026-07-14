# Charness Handoff

## Workflow Trigger

- Pickup with no explicit task invokes `charness:handoff` and runs chunked
  routing over this baton plus live issues. Restart first only when that pickup
  will test installed-plugin behavior, not for repo-local triage. An explicit
  user task keeps its own authority.

## Current State

- Continue from the verified v1.0.5 public/install state; admit new work only
  from a current issue, reproduction, measurement, or operator request.
- v1.0.5 is public at tag `86e85052`; clean local/remote main `7bd4ad1a` is the
  expected post-publish evidence commit, and GitHub has no open issues.
- Installed CLI, source checkout, Codex source/cache, and Claude plugin state
  read 1.0.5. Active sessions may retain stale injected cache paths; restart
  Claude Code and Codex before judging the refreshed plugin.
- Release quality, fresh-checkout probes, public HTTP/API readback, installed
  readback, and a separate fresh-eye observer passed. The release artifact owns
  the detailed evidence and presence-versus-behavior boundary.
- Provider mutation run 29289933683 passed on issue-resolution commit
  `c6a1e828` (Python 89.0%, JavaScript 93.0%); it is not release-HEAD proof.
- Cautilus 0.19.3 is current. Charness now selects JSON explicitly for parsed
  commands; no Cautilus evaluation was run or claimed.
- Nine Python length advisories remain intentionally: seven cohesive units and
  two production validators deferred to behavior-led refactoring.
- A local post-v1.0.5 north-star slice fixes lifecycle feedback truthfulness and
  the shared `SKILL_DIR` shell bootstrap contract. It is not published, so
  installed v1.0.5 caches still require export-before-use and do not contain
  this source fix.

## Next Session

1. With no explicit task, run the handoff chunker. The baton can still surface
   deferred discussion when GitHub issues are empty; if it yields no work, wait
   for an operator request or a fresh measured failure.
2. Restart active Claude Code and Codex sessions before plugin or installed-
   surface behavior checks; restart is not a prerequisite for repo-local triage.
3. If behavior work touches `check_skill_surface_preflight.py` or
   `validate_critique_artifacts.py`, consider a characterized cohesive split;
   do not refactor them for line count alone.
4. If publication is authorized, carry the post-v1.0.5 lifecycle/bootstrap
   slice through the normal release proof and installed-cache update boundary;
   until then, do not claim the released plugin contains these fixes.

## Discuss

- Whether same-command evidence can reduce the release-only managed-install
  runtime while retaining one real install/update smoke.
- Whether a third parsed Cautilus subprocess should trigger a shared explicit-
  format helper; two consumers do not yet justify that abstraction.

## References

- [release](../charness-artifacts/release/latest.md)
  · [quality](../charness-artifacts/quality/2026-07-14-quality-review.md)
  · [release critique](../charness-artifacts/critique/2026-07-14-v1-0-5-release-critique.md)
  · [auto retro](../charness-artifacts/retro/2026-07-13-v1-0-5-release-auto-retro.md)
  · [recent lessons](../charness-artifacts/retro/recent-lessons.md)

- Refresh kept: [release state](../charness-artifacts/release/latest.md),
  conditional restart, scoped mutation evidence, and behavior-led advisory
  decisions because each changes the first action.
- Refresh non-claims: [quality](../charness-artifacts/quality/2026-07-14-quality-review.md)
  makes no Cautilus evaluation, release-HEAD provider mutation, installed
  functional rerun, or line-count-only refactor claim.
