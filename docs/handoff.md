# Charness Handoff

## Workflow Trigger

- With no explicit task, invoke `charness:handoff` and run chunked routing over
  this baton and live issues. Restart first only when testing installed-plugin
  behavior; an explicit user task keeps its own authority.

## Current State

- v1.0.8 is public at tag `f1b0009e`; post-publish evidence commit `a04b9d21`
  is on `main` and the release's GitHub/API and distinct HTTPS checks passed.
- Release quality and fresh-checkout probes passed. The installed CLI, Codex
  source/cache, and Claude plugin read 1.0.8; active host sessions may retain
  old injected skill paths and must restart before installed-behavior judgment.
- Charness now requests `gpt-5.6-terra` with `medium` effort and
  `fork_turns: "none"` for its coding, review, and dynamic-workflow subagents.
  This is a request contract, not proof that a provider applied those settings.
  The next operator can rely on the release artifact for detailed evidence.

## Next Session

1. With no explicit task, run the handoff chunker; if it yields no work, wait
   for an operator request or a fresh measured failure.
2. Restart Codex or Claude Code before testing installed-plugin behavior; no
   restart is needed for repo-local triage.
3. Treat provider-side model/effort application or host tool restrictions as a
   separate live-host experiment, not as a claim made by this release.

## Discuss

- Whether a live Codex experiment can add provider-applied reviewer-profile
  evidence without confusing it with the requested configuration contract.

## References

- [release state](../charness-artifacts/release/latest.md)
  · [v1.0.8 notes](../charness-artifacts/release/2026-07-14-v1.0.8-notes.md)
  · [release critique](../charness-artifacts/critique/2026-07-14-v1-0-8-codex-v2-defaults-release-critique.md)
  · [auto retro](../charness-artifacts/retro/2026-07-14-v1-0-8-release-auto-retro.md)
  · [recent lessons](../charness-artifacts/retro/recent-lessons.md)

- Refresh kept: [release state](../charness-artifacts/release/latest.md),
  conditional restart, and the requested-versus-applied boundary because each
  changes the first action.
- Refresh non-claims: [release state](../charness-artifacts/release/latest.md)
  makes no provider-applied model/effort, installed functional rerun, or live
  host-restriction claim.
