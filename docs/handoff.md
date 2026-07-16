# Charness Handoff

## Workflow Trigger

- With no explicit task, invoke `charness:handoff` and run chunked routing over
  this baton and live issues. Restart first only when testing installed-plugin
  behavior; an explicit user task keeps its own authority.

## Current State

- v1.0.11 is public; the GitHub release URL returned HTTP 200 over the
  distinct https-fetch channel and post-publish `charness update` refreshed
  the installed surface to match the repo (rc=0). The release record proves
  the refresh, not an independent installed-version readback.
- Active host sessions may retain stale injected skill paths from before the
  post-publish cache rotation; restart Codex or Claude Code before judging
  installed-plugin behavior.
- Charness still requests `gpt-5.6-terra` with `medium` effort and
  `fork_turns: "none"` for its subagents. This is a request contract, not
  proof that a provider applied those settings.
- The release closeout tail now records a `Baton Reconcile` observation, so a
  publish forces the question when this handoff still claims a prior release
  instead of leaving it silently stale (the v1.0.9–v1.0.11 recurrence).

## Next Session

1. With no explicit task, run the handoff chunker; if it yields no work, wait
   for an operator request or a fresh measured failure.
2. Restart Codex or Claude Code before testing installed-plugin behavior; no
   restart is needed for repo-local triage.
3. Operator decisions queued by the 2026-07-16 autonomous improvement run live
   in the
   [goal artifact](../charness-artifacts/goals/2026-07-16-scout-driven-improvement.md)
   `## Operator Decision Queue`: push approval for the local commits, the D18
   disposition, and the live Codex probe question.

## Discuss

- Whether a live Codex experiment can add provider-applied reviewer-profile
  evidence without confusing it with the requested configuration contract
  (queued with an owner and revisit trigger in the 2026-07-16 goal's Operator
  Decision Queue).

## References

- [release state](../charness-artifacts/release/latest.md)
  · [v1.0.11 release critique](../charness-artifacts/critique/2026-07-15-update-all-aggregate-provenance-release-critique.md)
  · [v1.0.11 auto retro](../charness-artifacts/retro/2026-07-15-v1-0-11-release-auto-retro.md)
  · [recent lessons](../charness-artifacts/retro/recent-lessons.md)

- Refresh kept: [release state](../charness-artifacts/release/latest.md),
  conditional restart, and the requested-versus-applied boundary because each
  changes the first action.
- Refresh non-claims: [release state](../charness-artifacts/release/latest.md)
  makes no provider-applied model/effort, installed functional rerun, or live
  host-restriction claim.
