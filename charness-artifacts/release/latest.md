# Release Surface Check
Date: 2026-07-17

## Scope

Advanced `charness` toward release `2.0.0` (tag `v2.0.0`) through the repo-owned release helper.

## Current Version

- previous version: `1.3.0`
- target version: `2.0.0`
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
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v2.0.0`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v2.0.0`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Lifecycle Usage Capture

- Lifecycle capture status: `appended`.
- Local telemetry pair appended: `True`.
- Delivery episode ID: `episode-d26dac6678c9ef90089970d2f28669ef10109bcc1c4a0053bfe4b3b965b4598e`.
- Linked feedback ID: `feedback-faf7a09164097fc96b3b73451624d91a894e3d56a257eb7176e35dea3b2dd6a5`.
- Capture error count: `0`.
- Non-claim: objective lifecycle capture is not human approval or general satisfaction evidence.

## Release Adapter Preflight

- Release adapter focused preflight status: `not_required`.
- Reason: release adapter did not change in the release delta
- Focused preflight commands: none executed.

## Retro Trigger Evaluation

- Triggered: `True`.
- Evaluated at: `final_release_paths`.
- Input mode: `explicit_paths`.
- Reason: Changed surfaces hit configured install/update/support/export/discovery retro triggers.
- Closeout status: `written`.
- Retro artifact: `charness-artifacts/retro/2026-07-17-v2-0-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 0.
- Evaluated changed paths: 47.
  - `.agents/surfaces.json`
  - `.charness/specdown/report.json`
  - `.charness/specdown/report/on-demand-validation.html`
  - `.charness/specdown/report/tool-doctor.html`
  - `.claude-plugin/marketplace.json`
  - `charness`
  - `charness-artifacts/critique/2026-07-17-affordance-convergence-slice.md`
  - `charness-artifacts/critique/2026-07-17-v2-0-0-release-critique.md`
  - `charness-artifacts/goals/2026-07-17-prove-dogfood-via-444-polish.md`
  - `charness-artifacts/quality/dup-review.json`
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/spec/cli-output-affordance-contract.md`
  - `docs/generated/cli-reference.md`
  - `docs/handoff.md`
  - `packaging/charness.json`
  - `plugins/charness/.claude-plugin/plugin.json`
  - `plugins/charness/.codex-plugin/plugin.json`
  - `plugins/charness/scripts/install_machine_local.py`
  - `plugins/charness/scripts/render_cli_reference.py`
  - `plugins/charness/scripts/suggest_mutation_coverage_command.py`
  - ... 27 more

## Real-Host Verification

- Release-time real-host verification was triggered for this slice.
- Real-host checklist items remain open until their executed proof is recorded.

## Real-Host Proof

- Release-time real-host proof is required for this slice.
- On THIS maintainer/dev machine, run `charness update` after publish so the installed plugin at `~/.agents/src/charness` stays `== repo`, then re-verify with `charness doctor` (or `python3 scripts/doctor.py --repo-root . --json`) and a cited-check == repo-gate spot check; record the `charness update` output as executed proof. This closes the installed-vs-repo version-skew class.
- Run `charness tool doctor nose --no-write-locks` before installing `nose` and confirm missing `nose` reports `doctor_disposition: advisory-install-needed`, not a blocking install failure.
- Run `charness tool install nose --dry-run` and confirm it points at the upstream `nose-cli-installer.sh` release path and latest `v0.4.0` or newer metadata.
- Install `nose` through the manifest-supported path (`charness tool install nose`, the upstream release installer, or `brew install corca-ai/tap/nose`), then verify `nose --version`.
- Re-run `charness tool doctor nose --no-write-locks` and confirm the binary is detected on PATH.
- Run `charness tool sync-support nose` and confirm it reports no materialized support skill requirement; `nose` is an integration-only validation binary consumed by the public `quality` skill.
- Run `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json` once with `nose` available and confirm findings, if any, are advisory refactoring candidates rather than standing quality failures.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-07-17-v2-0-0-release-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v2.0.0`.

## Install Refresh

- Post-publish install refresh status: `failed` on first run, **completed on
  manual re-run** (see resolution below).
- Command: `charness update`
- Return code: `1`
- Elapsed seconds: `5.492`
- Resolution (2026-07-17, same session): the failure is the one-time
  v1.3.0→v2.0.0 migration crash — the old installed binary refreshed the
  managed checkout and the installed binary to 2.0.0, then its old in-memory
  `install_surface` read the new installer's `host_next_steps` output and
  raised `KeyError: 'next_steps'`. The immediate re-run of `charness update`
  on the refreshed binary completed cleanly; `charness version` reports
  `2.0.0` and the runtime doctor `next_action` is structured. The GitHub
  release notes carry an "Upgrading from v1.3.0" section naming the
  re-run requirement.
- Stderr tail: `STEP: refreshing source checkout
STEP: refreshing install surface
Traceback (most recent call last):
  File "/home/hwidong/.local/bin/charness", line 5589, in <module>
    raise SystemExit(main())
  File "/home/hwidong/.local/bin/charness", line 5584, in main
    return args.func(args)
  File "/home/hwidong/.local/bin/charness", line 3896, in cmd_update
    payload = install_surface(
  File "/home/hwidong/.local/bin/charness", line 2155, in install_surface
    payload["host_next_steps"]["claude"] = claude_plugin_message
KeyError: 'next_steps'`

## Release Runtime

- `requested_review_gate`: 0.001s
- `cli_skill_surface_gate`: 1.852s
- `quality_command`: 81.131s
- `fresh_checkout_probes_initial`: 3.093s
- `fresh_checkout_probes_after_amend`: 3.006s
- `push_create_verify_release`: 60.032s
- `distinct_channel_verification`: 0.531s
- `issue_closeout`: 0.000s
- `post_publish_install_refresh`: 5.492s

## Baton Reconcile

- Baton reconcile observation: `stale` for `docs/handoff.md`.
- Just-published version: `2.0.0`.
- Versions claimed by the baton's routing sections: `1.3.0`.
- RECONCILE REQUIRED: Reconcile `docs/handoff.md` (its `## Current State` / `## Next Session` routing sections) to the just-published `2.0.0`, or record an explicit n/a disposition in the release record, before ending the session.
- This is an observation, not completion: the populated record forces the reconcile question; the release critique/retro reviewers judge the disposition.

## Fresh Checkout Probes

- Fresh-checkout probe status: passed.
- `./charness --help >/dev/null`
- `./charness goal check --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --json --skip-release-probe >/dev/null`

## Issue Closeout

- Issue closeout verification: `not_requested`.

## User Update Steps

- Run `charness update` to install the latest published Charness release.
- Read the GitHub release notes for release-specific behavior changes, migrations, or rollback notes.
