# Release Surface Check
Date: 2026-06-05

## Scope

Advanced `charness` toward release `0.22.0` (tag `v0.22.0`) through the repo-owned release helper.

## Current Version

- previous version: `0.21.0`
- target version: `0.22.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v0.22.0`; creation runs after the branch/tag push
- public release surface verification: not checked by this helper
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: expected after branch/tag push; not verified yet.

## Release Adapter Preflight

- Release adapter focused preflight status: `required`.
- Reason: release adapter changed in the release delta; focused adapter preflight is required before release mutation
- Previous release ref: `refs/tags/v0.21.0`
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
- Retro artifact: `charness-artifacts/retro/2026-06-05-v0-22-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 7.
  - `skills/public/release/scripts/publish_release_cli.py`
  - `skills/public/release/scripts/publish_release_plan.py`
  - `skills/public/release/scripts/publish_release_preflight.py`
  - `skills/public/release/scripts/publish_release_resume.py`
  - `skills/public/release/scripts/publish_release_retro.py`
  - `skills/support/web-fetch/scripts/acquire_public_url.py`
  - `skills/support/web-fetch/scripts/agent_browser_session.py`
- Evaluated changed paths: 60.
  - `.agents/release-adapter.yaml`
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-06-05-111217-packet.json`
  - `charness-artifacts/critique/2026-06-05-111217-packet.md`
  - `charness-artifacts/critique/2026-06-05-302-305-gather-setup-release-robustness-disposition-review.md`
  - `charness-artifacts/critique/2026-06-05-disposition-review-inventory-conversions-nose-05-and-release.md`
  - `charness-artifacts/critique/2026-06-05-issue-302-gather-browser-close-and-clean-runtime.md`
  - `charness-artifacts/critique/2026-06-05-issue-303-adapter-first-reviewer-rule.md`
  - `charness-artifacts/critique/2026-06-05-issue-304-template-inspector-agreement.md`
  - `charness-artifacts/critique/2026-06-05-issue-305-release-publish-resilience.md`
  - `charness-artifacts/critique/2026-06-05-v0.22.0-release-critique.md`
  - `charness-artifacts/debug/2026-06-05-issue-302-gather-browser-close-and-clean-runtime.md`
  - `charness-artifacts/debug/2026-06-05-issue-304-template-inspector-wrap.md`
  - `charness-artifacts/debug/2026-06-05-issue-305-release-publish-resilience.md`
  - `charness-artifacts/debug/seam-risk-index.json`
  - `charness-artifacts/goals/2026-06-05-302-305-gather-setup-release-robustness.md`
  - `charness-artifacts/goals/2026-06-05-inventory-conversions-nose-05-and-release-early-close-report.md`
  - `charness-artifacts/goals/2026-06-05-inventory-conversions-nose-05-and-release.md`
  - `charness-artifacts/issue/2026-06-05-followup-premortem-before-authoring-constrained-surfaces.md`
  - `charness-artifacts/issue/2026-06-05-followup-repo-copy-invariant-timing.md`
  - ... 40 more

## Real-Host Verification

- This slice still requires configured real-host verification before the release is fully closed.

## Real-Host Proof

- Release-time real-host proof is required for this slice.
- On a second machine or a clean temp-home, refresh `charness` through the published operator path before claiming the release surface is ready.
- Run `charness tool doctor nose --json --no-write-locks` before installing `nose` and confirm missing `nose` reports `doctor_disposition: advisory-install-needed`, not a blocking install failure.
- Run `charness tool install nose --dry-run --json` and confirm it points at the upstream `nose-cli-installer.sh` release path and latest `v0.4.0` or newer metadata.
- Install `nose` through the manifest-supported path (`charness tool install nose --json`, the upstream release installer, or `brew install corca-ai/tap/nose`), then verify `nose --version`.
- Re-run `charness tool doctor nose --json --no-write-locks` and confirm the binary is detected on PATH.
- Run `charness tool sync-support nose --json` and confirm it reports no materialized support skill requirement; `nose` is an integration-only validation binary consumed by the public `quality` skill.
- Run `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json` once with `nose` available and confirm findings, if any, are advisory refactoring candidates rather than standing quality failures.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-06-05-v0.22.0-release-critique.md`.

## Fresh Checkout Probes

- Fresh-checkout probe status: passed.
- `./charness --help >/dev/null`
- `./charness goal check --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --json --skip-release-probe >/dev/null`

## Issue Closeout

- Issue closeout verification: pending or not requested.

## User Update Steps

- Run `charness update` to pull 0.22.0 (minor release: gather/setup/release robustness fixes for #302-#305 plus one additive `setup` operator surface).
- Restart Claude Code or Codex if the host cache still shows the previous version.
- No new manual migration is required beyond the normal `charness update` flow; existing non-timeboxed goals remain unaffected.
- NEW SETUP REVIEWER RULE (#303) - `setup` now generates an adapter-first subagent reviewer rule into a greenfield AGENTS.md: bounded reviewers follow the owning skill/adapter's reviewer tier and concrete spawn fields instead of inheriting the parent turn's host defaults. NOTE - an AGENTS.md that already exists is left untouched (the block is greenfield-only); existing repos that want the rule should add it by hand for now.
- SETUP DELEGATION FIX (#304) - the compact subagent-delegation block now agrees with the setup inspector across line wraps, so the host-doc generator no longer emits a delegation block its own inspector rejects.
- GATHER RUNTIME HYGIENE (#302) - `gather`/web-fetch agent-browser sessions are guaranteed to close, and a fail-visible clean-runtime proof reports residue; the runtime guard now also counts reparented-PPID and zombie (`<defunct>`) residue, not just the orphan daemon tree. Pure reparented/zombie residue is the container init's job to reap; `--cleanup-orphans` only clears the orphan daemon tree.
- RELEASE PUBLISH RESILIENCE (#305) - `publish_release.py` is now resumable (`--resume` re-validates and re-pushes a partial publish), bootstraps safely from the installed plugin cache, and unconditionally blocks publish when adapter `update_instructions` still describe the previous version but not the target (this very note is what that guard checks).
- Carried-forward (0.21.0) - the `quality` clone-family advisory runs under nose 0.5 (parses the 0.5 JSON object schema, reports the live nose version); `integrations/tools/nose.json` prefers nose 0.5.0+. nose stays advisory; the gate passes without it.
- Carried-forward (0.18.0) - `quality` runs an `inventory-nose-clones` advisory phase. If `nose` is absent it prints an explicit advisory skip and exits zero; if present on PATH, or via maintainer-local `NOSE_BIN`, it summarizes clone families from `nose scan`.
- Carried-forward (0.18.0) - `integrations/tools/nose.json` declares upstream install/update/doctor metadata for arbitrary machines. `charness update all` and `charness tool install/update nose` can use the upstream `nose` 0.4.0+ release installer path.
- Carried-forward (0.18.0) - the hard near-copy gate is document-oriented (`check-doc-near-duplicates`); code clone cleanup starts advisory through `nose`, with `jscpd` still deferred until a baseline/ignore policy is justified.
- Carried-forward (0.21.0) - `quality` owns the boundary-bypass ratchet proof used by the testability initiative: candidate counts, clean-convertible/internal classification, keep-boundary decisions, and schema drift are validated by repo-owned scripts and surfaced in the quality artifact payload.
- Carried-forward (0.21.0) - `find-skills` routes testability, test DSL, lazy eval, and boundary-bypass-ratchet requests toward `quality`, making the same quality-first ratchet path easier to reuse in downstream Charness repos.
- Carried-forward (0.21.0) - the local x86_64/default `check-doc-near-duplicates` budget is 13.0s, matching the release-path workload while remaining an enforced budget below the slower aarch64 profile.
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
