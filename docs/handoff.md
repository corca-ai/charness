# Charness Handoff

## Workflow Trigger

- Pickup with no explicit task invokes `charness:handoff`; a bare `/handoff`
  runs chunked routing over this baton plus live issues.

## Current State

- v0.66.3 is published at release commit/tag `917239ba`; local and
  `origin/main` are at public-evidence commit `677bc78c` before this lifecycle
  closeout.
- Verification lock now stops after sync-created tracked drift and names only
  the paths changed by sync. Concurrent identical feedback writers serialize
  into one append plus one replay no-op.
- Release quality, fresh-checkout probes, public HTTPS content, source-archive
  disposition, installed 0.66.3, and doctor readiness were independently read
  back. #433 and #436 remain OPEN exactly as requested.
- Residual #436-class waste remains: the tracked SLOC inventory producer is
  declared as a verify command, so artifact/test edits can still create tracked
  drift after sync and force another clean-HEAD lock.

## Next Session

1. Continue #436 without closing it: inspect
   [the surface manifest](../.agents/surfaces.json) and move
   every tracked writer—starting with `inventory_sloc.py --output`—before the
   first verify command, or make the runner stop immediately after any
   write-shaped verify command. Prove no broad runner starts after such drift.
2. Make mutation coverage hand off its exact resolved merge-base and a copyable
   `--reuse-coverage --require-fresh-coverage` consumer command. A tag label or
   the wrong base silently looks stale and can trigger an eight-minute duplicate
   sequential run plus multi-gigabyte contexts JSON.
3. Treat #433 as a separate unresolved behavior issue. Read its live body before
   any work and do not infer that this release authorized issue closure.

## Discuss

- Closing #433 or #436 remains a separate irreversible action and was not
  authorized by this release goal.
- Feedback locking covers cooperating feedback writers only; mixed event
  producers remain an evidence-triggered non-claim.

## References

- [goal](../charness-artifacts/goals/2026-07-11-north-star-autonomous-two-hour-release-round-2.md)
  · [release](../charness-artifacts/release/latest.md)
  · [quality proof](../charness-artifacts/quality/2026-07-11-quality-review.md)
  · [retro](../charness-artifacts/retro/2026-07-12-v0663-round2-autonomous-release.md)
  · [recent lessons](../charness-artifacts/retro/recent-lessons.md)

- Refresh kept: [issue #436](https://github.com/corca-ai/charness/issues/436)'s
  residual write-shaped-verifier follow-up and
  [issue #433](https://github.com/corca-ai/charness/issues/433)'s separate
  external boundary.

- Refresh non-claims: the [release carrier](../charness-artifacts/release/2026-07-11-v0.66.3-notes.md)
  does not prove #433/#436 resolution, mixed-writer locking, Cautilus evaluation,
  non-GitHub provider behavior, or user feedback observation.
