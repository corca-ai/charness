# Release Surface Check
Date: 2026-06-03

## Scope

Advanced `charness` toward release `0.17.0` (tag `v0.17.0`) through the repo-owned release helper.

## Current Version

- previous version: `0.16.0`
- target version: `0.17.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v0.17.0`; creation runs after the branch/tag push
- public release surface verification: not checked by this helper
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: expected after branch/tag push; not verified yet.

## Release Adapter Preflight

- Release adapter focused preflight status: `required`.
- Reason: release adapter changed in the release delta; focused adapter preflight is required before release mutation
- Previous release ref: `refs/tags/v0.16.0`
- Adapter paths in release delta:
  - `.agents/release-adapter.yaml`
- Changed adapter fields:
  - `update_instructions`
- Focused preflight commands:
  - `python3 skills/public/release/scripts/resolve_adapter.py --repo-root .`
  - `pytest tests/quality_gates/test_release_narrative_audit.py -q`

## Retro Trigger Evaluation

- Triggered: `True`.
- Evaluated at: `final_release_paths`.
- Input mode: `explicit_paths`.
- Reason: Changed surfaces hit configured install/update/support/export/discovery retro triggers.
- Closeout status: `written`.
- Retro artifact: `charness-artifacts/retro/2026-06-03-v0-17-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 2.
  - `skills/public/find-skills/scripts/list_capabilities.py`
  - `skills/public/find-skills/scripts/public_skill_recommendations.py`
- Evaluated changed paths: 80.
  - `.agents/issue-adapter.yaml`
  - `.agents/quality-adapter.yaml`
  - `.agents/release-adapter.yaml`
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-06-03-091616-packet.json`
  - `charness-artifacts/critique/2026-06-03-091616-packet.md`
  - `charness-artifacts/critique/2026-06-03-boundary-bypass-probe-critique.md`
  - `charness-artifacts/critique/2026-06-03-retro-issue-structural-decouple-split-disposition-review.md`
  - `charness-artifacts/critique/2026-06-03-test-dsl-first-slice-critique.md`
  - `charness-artifacts/critique/2026-06-03-testability-quality-ratchet-disposition-review.md`
  - `charness-artifacts/critique/2026-06-04-release-v0.17.0-critique.md`
  - `charness-artifacts/goals/2026-06-03-retro-issue-structural-decouple-split.md`
  - `charness-artifacts/goals/2026-06-03-testability-quality-skill-ratchet.md`
  - `charness-artifacts/probe/2026-06-03-retro-issue-structural-decouple-split.json`
  - `charness-artifacts/probe/2026-06-03-testability-quality-ratchet-host-log.json`
  - `charness-artifacts/quality/sloc-inventory/latest.json`
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/release/v0.17.0-notes.md`
  - `charness-artifacts/retro/2026-06-03-282-283-release-waste-retro.md`
  - `charness-artifacts/retro/2026-06-03-retro-issue-destination-split.md`
  - ... 60 more

## Real-Host Verification

- This slice still requires configured real-host verification before the release is fully closed.

## Real-Host Proof

- Release-time real-host proof is required for this slice.
- On a second machine or a clean temp-home, refresh `charness` through the published operator path before claiming the release surface is ready.
- Run `charness tool doctor tokei --json` before installing `tokei` and confirm the missing-binary state still surfaces the upstream install document URL instead of a guessed package-manager command.
- Install `tokei` through the manifest-supported path (`charness tool install tokei --json`, `cargo install tokei`, `brew install tokei`, or an upstream release binary), then verify `tokei --version`.
- Re-run `charness tool doctor tokei --json` and confirm the binary is detected on PATH.
- Run `charness tool sync-support tokei --json` and confirm it reports `skipped` with reason `integration has no support_skill_source`; `tokei` is an integration-only validation binary, not a materialized support skill.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-06-04-release-v0.17.0-critique.md`.

## Fresh Checkout Probes

- Fresh-checkout probe status: passed.
- `./charness --help >/dev/null`
- `./charness goal check --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --json --skip-release-probe >/dev/null`

## Issue Closeout

- Issue closeout verification: pending or not requested.

## User Update Steps

- Run `charness update` to pull 0.17.0 (minor release: testability quality ratchet and reusable quality routing).
- Restart Claude Code or Codex if the host cache still shows the previous version.
- No new manual migration is required beyond the normal `charness update` flow.
- NEW QUALITY RATCHET - `quality` now owns the boundary-bypass ratchet proof used by the testability initiative: candidate counts, clean-convertible/internal classification, keep-boundary decisions, and schema drift are validated by repo-owned scripts and surfaced in the quality artifact payload.
- NEW ROUTING - `find-skills` now routes testability, test DSL, lazy eval, and boundary-bypass-ratchet requests toward `quality`, making the same quality-first ratchet path easier to reuse in downstream Charness repos.
- HANDOFF QUEUE - the checked-in handoff now marks the ratchet goal complete and queues the next session for #284 first, then #286, with #285 only if #286 exposes live-issue fixture brittleness.
- RUNTIME BUDGET - the local x86_64/default `check-duplicates` budget is now 13.0s, matching the current release-path workload while remaining an enforced budget below the slower aarch64 profile.
- Carried-forward (0.16.0) - `achieve`/`retro` goal closeout records a goal-scoped `Host metric window:` line (via `record_metric_window.py`) and renders a standardized provider-safe measured-vs-proxy metrics block (`probe_host_logs.py --goal-path <artifact> --format markdown`) that records results, never provider CLI command strings; an absent window surfaces as a non-blocking attention signal at flip-to-complete instead of being reported thread-wide.
- Carried-forward (0.16.0) - Codex session/token reporter mutation survivors are killed by direct unit tests; no production behavior change.
- Carried-forward (0.16.0) - `validate_quality_artifact.py --report-all` lists every violation in one pass; the default stays fail-fast and unchanged.
- Carried-forward (0.15.0) - the Corca-internal `report_usage_product_review.py` usage product-review reporter with last-seen summaries and thresholded dry-run GitHub packets remains available (`--execute` stays explicit and redacts target refs in mutating comments by default).
- Carried-forward from 0.14.0 - stable `charness goal check`, broad closeout verification lock, and `tokei`-backed Python length gates remain part of the installed surface.
- VALIDATION DEPENDENCY - Python file and headroom length gates now require the `tokei` binary on PATH and fail closed when `tokei` or its JSON output is unavailable. Run `charness tool doctor tokei --json` or `charness tool install tokei --json` before local validation on machines that do not already have it.
- BEHAVIOR CHANGE (broad closeout lock) - `scripts/run_slice_closeout.py` refuses broad pytest unless `--verification-lock` is passed after the mutation set is locked. Use `--skip-broad-pytest` for pre-lock rehearsal of deterministic gates.
- NEW OPERATOR SURFACE - use `charness goal check --repo-root . --goal-path <path> --pursue-ready` as the stable goal-helper surface instead of invoking versioned plugin-cache helper paths directly.
- HOST HOOK CLEANUP - stale or duplicate Codex find-skills startup hook markers are cleaned up during hook reconciliation; if you hand-edited those hooks, inspect the generated config after update.
- AUTO-WIRE WIN (#244/#245) - `charness update` now AUTO-INSTALLS the find-skills SessionStart routing hook and dedups it by logical identity across checkouts. The manual user-level hook wiring required through 0.12.0 is no longer needed; if you hand-added one, you may remove the duplicate.
- BEHAVIOR CHANGE (achieve coordination floors) - a goal `Created` on/after 2026-05-31 now needs a `## Coordination Cues` step before the `complete` flip - a `Gather:` line (or `Gather: n/a — <reason>`) when `## Context Sources` names an external URL/Slack/Notion/Docs source, and a `Release:` line (or `Release: n/a — <reason>`) when the run touched a release surface. Existing and older goals are grandfathered (unaffected). The floors are presence-only and ship with an explicit opt-out, so they never block a goal that records the step.
- BEHAVIOR CHANGE (achieve disposition gate, #253) - a goal `Created` on/after 2026-05-30 also needs a non-blank `## Auto-Retro` and a bound `Disposition review:` line at `complete` (or a `host-blocked-subagent` skip), proving the closeout improvement-disposition review ran. Pre-rule goals are grandfathered.
- Carried-forward (since 0.12.0, still applies) - a bare `/handoff` pickup unions your LIVE open-issue backlog via the resolved issue provider; opt out with `issue_source: {enabled: false}` in `.agents/handoff-adapter.yaml`.
