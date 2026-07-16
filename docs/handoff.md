# Charness Handoff

## Workflow Trigger

- With no explicit task, invoke `charness:handoff` and run chunked routing over
  this baton and live issues. Restart first only when testing installed-plugin
  behavior; an explicit user task keeps its own authority.

## Current State

- v1.1.0 is public at tag `55529413`; the release URL returned HTTP 200 over
  the distinct https-fetch channel, post-publish `charness update` refreshed
  the installed surface (rc=0), and the post-publish artifact commit
  `bb72d553` is pushed on `main` (local == origin).
- v1.1.0 ships the operator-approved 2026-07-16 improvement bundle: the
  post-publish baton-reconcile observation (this file is the adapter-declared
  baton; the observation fired `stale` on its first real publish and this
  refresh answers it), the provenance-gated glow/tokei/vulture update
  contract, compact doctor `observed_version`, safer mutating `next_action`,
  and the P2-aligned skill length-gate message.
- Active host sessions may retain stale injected skill paths from before the
  post-publish cache rotation; restart Codex or Claude Code before judging
  installed-plugin behavior.
- Charness still requests `gpt-5.6-terra` with `medium` effort and
  `fork_turns: "none"` for its subagents. This is a request contract, not
  proof that a provider applied those settings.

## Next Session

1. With no explicit task, run the handoff chunker over this baton and the open
   issues. #440 (round-5 retro pair) and #441 (dup-ratchet member visibility)
   were resolved and closed on 2026-07-16; #439 (skill-cap split backlog,
   `impl` first) is open, paused on the operator's split-vs-delete decision —
   resume from the dated 2026-07-16 issue-439 resolution brief in the issue
   artifacts directory (kept uncommitted until the resolution commit; the
   commit-msg hook demands a full closeout ledger for any staged issue
   artifact). Close scope is already decided: close after the `impl` slice
   with a follow-up issue for `spec`/`critique`/`announcement`.
2. Restart Codex or Claude Code before testing installed-plugin behavior; no
   restart is needed for repo-local triage.
3. Remaining operator decisions from the 2026-07-16
   [goal artifact](../charness-artifacts/goals/2026-07-16-scout-driven-improvement.md)
   `## Operator Decision Queue`: the D18 disposition and the live Codex probe
   question (the push/release decision was resolved by the operator's
   "push release" and shipped as v1.1.0).

## Discuss

- Whether a live Codex experiment can add provider-applied reviewer-profile
  evidence without confusing it with the requested configuration contract
  (queued with an owner and revisit trigger in the 2026-07-16 goal's Operator
  Decision Queue).

## References

- [release state](../charness-artifacts/release/latest.md)
  · [v1.1.0 release critique](../charness-artifacts/critique/2026-07-16-v1-1-0-baton-provenance-release-critique.md)
  · [v1.1.0 auto retro](../charness-artifacts/retro/2026-07-16-v1-1-0-release-auto-retro.md)
  · [goal run retro](../charness-artifacts/retro/2026-07-16-scout-driven-improvement-retro.md)
  · [recent lessons](../charness-artifacts/retro/recent-lessons.md)

- Refresh kept: [release state](../charness-artifacts/release/latest.md),
  conditional restart, and the requested-versus-applied boundary because each
  changes the first action.
- Refresh non-claims: [release state](../charness-artifacts/release/latest.md)
  makes no provider-applied model/effort claim and no live network
  `tool update` execution claim; the installed refresh is an rc=0 refresh
  record, not an independent installed-version readback.
