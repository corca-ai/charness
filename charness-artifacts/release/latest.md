# Release Surface Check
Date: 2026-06-06

## Scope

Advanced `charness` toward release `0.24.0` (tag `v0.24.0`) through the repo-owned release helper.

## Current Version

- previous version: `0.23.0`
- target version: `0.24.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.
- post-publish artifact push recorded the verified public release state on the release branch.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v0.24.0`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Release Adapter Preflight

- Release adapter focused preflight status: `required`.
- Reason: release adapter changed in the release delta; focused adapter preflight is required before release mutation
- Previous release ref: `refs/tags/v0.23.0`
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
- Retro artifact: `charness-artifacts/retro/2026-06-06-v0-24-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 0.
- Evaluated changed paths: 44.
  - `.agents/release-adapter.yaml`
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-06-05-225242-packet.json`
  - `charness-artifacts/critique/2026-06-05-225242-packet.md`
  - `charness-artifacts/critique/2026-06-06-306-317-posthoc-critique.md`
  - `charness-artifacts/critique/2026-06-06-318-319-disposition-review.md`
  - `charness-artifacts/critique/2026-06-06-318-orchestrated-closeout-delegation.md`
  - `charness-artifacts/critique/2026-06-06-319-commit-boundary-headroom.md`
  - `charness-artifacts/critique/2026-06-06-v0.24.0-release-critique.md`
  - `charness-artifacts/goals/2026-06-06-306-316-open-followups.md`
  - `charness-artifacts/goals/2026-06-06-318-319-achieve-closeout-and-quality-headroom.md`
  - `charness-artifacts/probe/2026-06-06-318-319.json`
  - `charness-artifacts/quality/sloc-inventory/latest.json`
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/retro/2026-06-06-318-319-closeout.md`
  - `charness-artifacts/retro/lesson-selection-index.json`
  - `charness-artifacts/retro/recent-lessons.md`
  - `docs/conventions/authoring-preflight.md`
  - `docs/handoff.md`
  - `docs/prescribed-skill-closeout-contract.md`
  - ... 24 more

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

- Review proof: `charness-artifacts/critique/2026-06-06-v0.24.0-release-critique.md`.

## Post-Publish Proof

- Public release check: `gh release view v0.24.0`.

## Fresh Checkout Probes

- Fresh-checkout probe status: passed.
- `./charness --help >/dev/null`
- `./charness goal check --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --json --skip-release-probe >/dev/null`

## Issue Closeout

- Issue closeout verification: `verified`.
- GitHub repo: `corca-ai/charness`
- Issue #318: `CLOSED` (https://github.com/corca-ai/charness/issues/318)
  - carrier: `direct_release_commit_body`
  - manual fallback used: `True`
- Issue #319: `CLOSED` (https://github.com/corca-ai/charness/issues/319)
  - carrier: `direct_release_commit_body`
  - manual fallback used: `False`

## User Update Steps

- Run `charness update` to pull 0.24.0 (minor release: two additive features — #318 orchestrator-owned achieve sub-goal closeout-proof delegation, and #319 commit-boundary SKILL.md core-headroom gate).
- Restart Claude Code or Codex if the host cache still shows the previous version.
- No new manual migration is required beyond the normal `charness update` flow; existing non-timeboxed goals remain unaffected.
- ACHIEVE ORCHESTRATED CLOSEOUT (#318) - `achieve` adds an OPT-IN orchestrator/sub-goal proof-delegation mode: a sub-goal may close at local/proof-carrier complete while a NAMED orchestrator goal owns the deferred external proof. A goal with no `## Closeout Delegation` section is unchanged - the strict standalone default stays the hard default. An orchestrator's delegated-proof checklist must resolve every item (verified / skipped with a reason / a follow-up issue ref) before it can flip to complete.
- QUALITY COMMIT-BOUNDARY HEADROOM GATE (#319) - the SKILL.md `core_nonempty` >=4 headroom buffer is now enforced at the commit boundary for CHANGED public/support SKILL.md files (a ratchet that grandfathers skills already under buffer and blocks new erosion), not only in the broad gate. The existing broad-gate headroom test is unchanged.
- Carried-forward (0.23.0) - six open follow-ups #306/#311/#314/#315/#316/#317: mutation-coverage honesty, setup inspector + commit-discipline seeding, commit-boundary gate reconciliation, and achieve closeout/approval-boundary clarity.
- MUTATION-COVERAGE HONESTY (#306) - the recurring subprocess-only scaffold CLI class is now covered in-process, so the scheduled mutation gate's changed-line signal stops self-healing into ~2 auto-issues/day; the gate stays blocking on genuinely-uncovered changed lines.
- SETUP STALE-AGENTS FLAG (#311) - the setup inspector now flags an existing AGENTS.md that predates the #303 adapter-first reviewer rule as stale. Report-only: existing AGENTS.md bodies are never rewritten.
- COMMIT-BOUNDARY GATE RECONCILIATION (#314) - the fast structural checkers (`validate_skill_ergonomics`, `check_boundary_bypass_ratchet`) now run in the per-slice aggregate, and the per-slice aggregate and the literal git pre-commit hook run the same fast gate subset (generalizes #307).
- SETUP COMMIT-DISCIPLINE SEED (#317) - greenfield AGENTS.md now carries a compact commit-discipline block, and the inspector flags an AGENTS.md that has Charness goal routing but no commit discipline. Report-only: existing bodies are never rewritten.
- ACHIEVE CLOSEOUT PLACEHOLDERS (#315) - new achieve goal artifacts seed visible retro/host-log/disposition/Auto-Retro closeout placeholders; the complete gate still rejects untouched placeholders (`TODO`/`TBD`/`FIXME`/`<...>`).
- ACHIEVE APPROVAL BOUNDARY (#316) - achieve now states that external publication/apply approval is scoped to the phase or bundle that requested it; after an approved lane, done-early test-only continuation is local by default (prose + template, no new gate).
- Carried-forward (0.22.0, #303) - `setup` generates an adapter-first subagent reviewer rule into a greenfield AGENTS.md; an existing AGENTS.md is left untouched (greenfield-only; #311 above now flags the gap).
- Carried-forward (0.22.0, #304) - the compact subagent-delegation block agrees with the setup inspector across line wraps.
- Carried-forward (0.22.0, #302) - `gather`/web-fetch agent-browser sessions are guaranteed to close; the runtime guard counts reparented-PPID and zombie residue, not just the orphan daemon tree.
- Carried-forward (0.22.0, #305) - `publish_release.py` is resumable (`--resume`), bootstraps from the installed plugin cache, and blocks publish when adapter `update_instructions` still describe the previous version but not the target (this very note is what that guard checks).
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
