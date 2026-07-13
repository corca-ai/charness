# Charness Handoff

## Workflow Trigger

- Pickup with no explicit task invokes `charness:handoff`; a bare `/handoff`
  runs chunked routing over this baton plus live issues. An explicit user task
  keeps its own authority.

## Current State

- Resume from the public v1.0.3 state without redoing round-four proof. Admit
  new issue or optimization work only from a current reproduction or measured
  cost, and keep issue closure as a separately authorized boundary.
- v1.0.3 is public at tag `9be247ae`; remote verification commit `2a7400e7`,
  substantive unauthenticated HTTPS readback, installed 1.0.3, and doctor/cache
  no-drift passed. The release record owns the detailed proof.
- Round four fixed invalid issue-target preflight ordering, removed two focused
  duplicate test costs, and repaired quality-scaffold evidence durability.
  Exact lock and fresh-eye closeout passed; no full-suite speedup is claimed.
- GitHub issues #433 and #436 remain OPEN/context-only. Neither tracker state
  nor earlier related work establishes a current behavioral failure.
- Active Claude/Codex sessions should be restarted after the plugin cache
  rotation to v1.0.3.

## Next Session

1. Restart active host sessions before judging installed behavior.
2. With no explicit task, run the handoff chunker against the live backlog and
   choose work from current evidence rather than this session's history.
3. Before work on #433 or #436, read the live body/comments and reproduce the
   residual behavior against v1.0.3; do not duplicate already shipped repairs.
4. Treat closing either issue as a separate irreversible action requiring
   explicit authority and issue-workflow behavioral closeout.

## Discuss

- Whether a future measured speed slice should investigate remaining serial
  managed-install tests; round four deliberately made no full-suite claim.
- Whether #433/#436 should remain open, receive a narrowed residual statement,
  or enter separately authorized tracker closeout after live reproduction.

## References

- [round-four goal](../charness-artifacts/goals/2026-07-13-north-star-autonomous-two-hour-release-round-4.md)
  · [release](../charness-artifacts/release/latest.md)
  · [retro](../charness-artifacts/retro/2026-07-13-north-star-autonomous-two-hour-release-round-4-retro.md)
  · [recent lessons](../charness-artifacts/retro/recent-lessons.md)

- Refresh kept: the [round-four goal](../charness-artifacts/goals/2026-07-13-north-star-autonomous-two-hour-release-round-4.md)
  binds public/install v1.0.3, host-session restart, and the live #433/#436
  reproduction/lifecycle boundaries because they change the next move.
- Refresh non-claims: the [release record](../charness-artifacts/release/latest.md)
  does not claim Cautilus, remote CI, full-suite speedup, an independent
  second-observer fresh clone, or issue closure.
