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
- GitHub issues #433, #436, and #437 are CLOSED. The production fixes for #433
  and #436 were already on main in `041aa380`/`32a15c19` and `ea810544`; their
  closeout comments preserve that history instead of attributing the fixes to
  the later proof slice.
- Main now includes `1e99eb5b`, which closes #437 by covering every reported
  root-CLI changed line in the scheduled mutation test selection and killing
  the five required-argument guard mutants plus a reported dispatch mutant.
  The standing suite passed with 4,585 tests. This is targeted local evidence,
  not a fresh scheduled/provider mutation run or a real Claude host roundtrip.

## Next Session

1. Restart active host sessions before judging the rotated 1.0.4 plugin caches.
2. With no explicit task, run the handoff chunker against the live backlog and
   admit work from a current reproduction or measurement.
3. Read the next scheduled mutation result when it exists; do not present the
   targeted #437 session as provider-backed proof.
4. If release adapters are touched, evaluate whether root `charness`
   host-plugin mutations need a narrow real-host proof trigger. Require a safe,
   scoped design; do not manufacture destructive host mutation for coverage.

## Discuss

- Whether same-command evidence can reduce the 78.78s release-only
  managed-install proof while retaining at least one real install/update smoke.
- Whether the root-CLI host-proof mapping deserves a guard or issue after a
  second occurrence; v1.0.4 explicitly does not claim a real Claude custom-home
  run.
- Ambient quality advisories remain non-blocking: lexical skill-ergonomics hits,
  12 Python files in the length advisory band, and Cautilus 0.18.0 locally while
  0.19.3 is available. None was changed by the issue-resolution slice.

## References

- [round-five goal](../charness-artifacts/goals/2026-07-13-north-star-autonomous-two-hour-release-round-5.md)
  · [release](../charness-artifacts/release/latest.md)
  · [retro](../charness-artifacts/retro/2026-07-13-north-star-autonomous-round-5-retro.md)
  · [quality](../charness-artifacts/quality/2026-07-14-quality-review.md)
  · [resolution critique](../charness-artifacts/critique/2026-07-14-issues-433-436-437-resolution-critique.md)
  · [recent lessons](../charness-artifacts/retro/recent-lessons.md)

- Refresh kept: [the round-five goal](../charness-artifacts/goals/2026-07-13-north-star-autonomous-two-hour-release-round-5.md)
  binds v1.0.4 public/install state, session restart, the evidence-admitted
  host-proof probe, and #433/#436 authority boundaries because they change the
  next move.
- Refresh non-claims: [the resolution critique](../charness-artifacts/critique/2026-07-14-issues-433-436-437-resolution-critique.md)
  does not claim a fresh scheduled/provider mutation run, a real Claude
  custom-home execution, Cautilus evaluation, or a test-speed gain.
