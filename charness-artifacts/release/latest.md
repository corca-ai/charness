# Release Surface Check
Date: 2026-05-29

## Scope

Advanced `charness` toward release `0.11.0` (tag `v0.11.0`) through the repo-owned release helper.

## Current Version

- previous version: `0.10.0`
- target version: `0.11.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v0.11.0`; creation runs after the branch/tag push
- public release surface verification: not checked by this helper
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: expected after branch/tag push; not verified yet.

## Real-Host Verification

- This slice still requires configured real-host verification before the release is fully closed.

## Real-Host Proof

- Release-time real-host proof is required for this slice.
- On a second machine or a clean temp-home, refresh `charness` through the published operator path before claiming the release surface is ready.
- Run `charness tool doctor cautilus --json` before installing `cautilus` and confirm the missing-binary state still surfaces an install document URL instead of a guessed package-manager command.
- Follow the official Cautilus install script at `https://github.com/corca-ai/cautilus/blob/main/install.sh`, then verify `cautilus --version` and `cautilus version --verbose`.
- Re-run `charness tool doctor cautilus --json` and confirm the binary is detected on PATH.
- Run `charness tool sync-support cautilus --json`, then confirm the generated support surface exists and the doctor payload reports support as materialized.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-05-29-v0.11.0-release-critique.md`.

## Fresh Checkout Probes

- No repo-declared fresh checkout probes were configured for this release.

## Issue Closeout

- Issue closeout verification: pending or not requested.

## User Update Steps

- Run `charness update` (delivers the new `scripts/session_start_find_skills.py` routing-trigger script into the plugin).
- Restart Claude Code or Codex if the host cache still shows the previous version.
- NOTE - session-start find-skills routing is NOT auto-wired. `charness init`/`charness update` install only the usage-episodes SessionStart hook. To enable the find-skills routing trigger, manually add a user-level SessionStart hook pointing at the installed plugin's `scripts/session_start_find_skills.py` - Claude Code via `~/.claude/settings.json` (`--host claude`), Codex via `~/.codex/config.toml` (`--host codex`).
- Honest ceiling - the hook injects a directive to call `charness:find-skills`; it strengthens routing via context-recency but does not hard-force the skill invocation.
