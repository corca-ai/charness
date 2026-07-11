# Charness Handoff

## Workflow Trigger

- Pickup with no explicit task invokes `charness:handoff`; a bare `/handoff`
  runs chunked routing over this baton plus live issues.

## Current State

- v0.66.2 is published at tag `746510ec`; `origin/main` and local `main` are at
  public-evidence commit `68f24313` before this lifecycle-only closeout.
- Five reversible north-star slices shipped: canonical quality H1 scaffolding,
  one immutable coverage campaign anchor, one safe dead-code deletion, closeout
  parser extraction, and structural dataclass-field classification.
- The release helper passed the release gate and fresh-checkout probes, created
  the public release, confirmed it through HTTPS, and refreshed the installed
  Charness version from 0.66.1 to 0.66.2.
- An independent unauthenticated HTTPS observer confirmed the visible tag,
  title, Latest status, substantive notes, and two source assets.
- #433 remains OPEN by design. Issue #436 now owns the repeated generated-sync
  discovery after expensive verification-lock runs.

## Next Session

1. Start with issue #436: reproduce the sync-after-lock waste and choose the
   smallest teeth-bearing design, either a sync-only preflight or fail-fast
   immediately after sync dirties tracked state. Preserve the final clean-HEAD
   verification lock.
2. Treat #433 as a separate unresolved behavior issue. Do not infer that the
   v0.66.2 release or its carrier closed it; read the live issue and comments
   before any resolution work.
3. Keep future release preparation ordered as mutate, sync, commit, verify,
   publish. Run cheap carrier-specific doc/reference checks before paying for
   the broad release gate.

## Discuss

- Closing #433 remains a separate irreversible action and was not authorized by
  this release goal.
- Feedback append locking remains deferred until concurrent-writer evidence.

## References

- [goal](../charness-artifacts/goals/2026-07-11-north-star-autonomous-two-hour-release.md)
  · [release](../charness-artifacts/release/latest.md)
  · [quality proof](../charness-artifacts/quality/2026-07-11-0662-full-carrier-release-readiness.md)
  · [retro](../charness-artifacts/retro/2026-07-11-north-star-autonomous-two-hour-release-retro.md)
  · [recent lessons](../charness-artifacts/retro/recent-lessons.md)

- Refresh kept: [issue #433](https://github.com/corca-ai/charness/issues/433)'s
  external boundary and [issue #436](https://github.com/corca-ai/charness/issues/436)'s
  generated-sync follow-up.

- Refresh non-claims: the [release carrier](../charness-artifacts/release/2026-07-11-v0.66.2-notes.md)
  does not prove a fresh install, #433 behavior resolution, Cautilus evaluation,
  non-GitHub provider behavior, or user feedback observation.
