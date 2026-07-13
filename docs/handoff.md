# Charness Handoff

## Workflow Trigger

- Pickup with no explicit task invokes `charness:handoff`; a bare `/handoff`
  runs chunked routing over this baton plus live issues. An explicit user task
  keeps its own authority.

## Current State

- v1.0.4 is public at tag `ef4016b8`; remote main `84354696` is the expected
  post-publish evidence commit. Unauthenticated GitHub REST returned the
  substantive release body, and the release record owns detailed timings.
- Installed CLI, source checkout, provenance, Codex source/cache, and Claude
  plugin state read 1.0.4. Codex source/cache drift is false. Restart active
  Claude/Codex sessions after the cache rotation before judging behavior.
- Round five fixed two reproduced operator boundaries: catalog refresh now
  rejects a missing/file explicit repo root without writes or traceback, and a
  custom Charness home now reaches every Claude observation/mutation subprocess.
- Frozen standing proof, release quality, security/supply-chain, generated
  parity, fresh-checkout probes, public readback, and installed readback passed.
  No test-speed improvement is claimed; measured managed-install cost was kept.
- GitHub issues #433 and #436 remain OPEN/context-only. No issue lifecycle action
  or claim of residual failure entered v1.0.4.

## Next Session

1. Restart active host sessions before judging the rotated 1.0.4 plugin caches.
2. With no explicit task, run the handoff chunker against the live backlog and
   admit work from a current reproduction or measurement.
3. If release adapters are touched, evaluate whether root `charness`
   host-plugin mutations need a narrow real-host proof trigger. Require a safe,
   scoped design; do not manufacture destructive host mutation for coverage.
4. Before work on #433 or #436, read live body/comments and reproduce against
   v1.0.4. Treat closeout as a separately authorized irreversible boundary.

## Discuss

- Whether same-command evidence can reduce the 78.78s release-only
  managed-install proof while retaining at least one real install/update smoke.
- Whether the root-CLI host-proof mapping deserves a guard or issue after a
  second occurrence; v1.0.4 explicitly does not claim a real Claude custom-home
  run.

## References

- [round-five goal](../charness-artifacts/goals/2026-07-13-north-star-autonomous-two-hour-release-round-5.md)
  · [release](../charness-artifacts/release/latest.md)
  · [retro](../charness-artifacts/retro/2026-07-13-north-star-autonomous-round-5-retro.md)
  · [quality](../charness-artifacts/quality/2026-07-13-round5-v1-0-4-release-readiness.md)
  · [recent lessons](../charness-artifacts/retro/recent-lessons.md)

- Refresh kept: v1.0.4 public/install state, session restart, evidence-admitted
  host-proof probe, and #433/#436 authority boundaries change the next move.
- Refresh non-claims: no Cautilus, remote CI, issue closure, test-speed gain,
  authenticated API proof, or real Claude custom-home execution.
