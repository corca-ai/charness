# Release Surface Check
Date: 2026-05-29

## Scope

Advanced `charness` toward release `0.12.0` (tag `v0.12.0`) through the repo-owned release helper.

## Current Version

- previous version: `0.11.0`
- target version: `0.12.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v0.12.0`; creation runs after the branch/tag push
- public release surface verification: not checked by this helper
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: expected after branch/tag push; not verified yet.

## Real-Host Verification

- No configured release-time real-host verification trigger matched this slice.

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-05-29-249-248-v0.12.0-release-critique.md`.

## Fresh Checkout Probes

- No repo-declared fresh checkout probes were configured for this release.

## Issue Closeout

- Issue closeout verification: pending or not requested.

## User Update Steps

- Run `charness update` to pull 0.12.0 (handoff chunker v2 - live-backlog input + bare-invocation trigger + #248 stage-script ergonomics).
- Restart Claude Code or Codex if the host cache still shows the previous version.
- BEHAVIOR CHANGE - 0.12.0 turns the handoff chunker's issue source ON by default. At a bare `/handoff` pickup the chunker unions your LIVE open-issue backlog by shelling out to the resolved issue provider (e.g. `gh issue list`); any provider failure degrades safely to doc-only chunking. To opt out, set `issue_source: {enabled: false}` in your handoff adapter (`.agents/handoff-adapter.yaml`). Exercised live only against `gh`; non-gh backends use the adapter `issue_backend.commands.list_open` override and are not yet proven on a live non-gh host.
- Carried from 0.11.0 (still applies) - session-start find-skills routing is NOT auto-wired; manually add a user-level SessionStart hook pointing at the installed plugin's `scripts/session_start_find_skills.py` (Claude `~/.claude/settings.json`, Codex `~/.codex/config.toml`). #244 tracks auto-wiring.
