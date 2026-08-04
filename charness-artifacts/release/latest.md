# Release Surface Check
Date: 2026-08-04

## Scope

Advanced `charness` toward release `3.2.0` (tag `v3.2.0`) through the repo-owned release helper.

## Current Version

- previous version: `3.1.1`
- target version: `3.2.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- local release-content commit: `2a652b18de280fa50d0f1e46f9caebe41c70755a`.
- branch push was executed with normal pre-push gates and independently read back
  through GitHub API/Actions.

## Release State

- local release mutation: complete
- branch push: verified at exact SHA `2a652b18de280fa50d0f1e46f9caebe41c70755a`
- tag push: verified at exact SHA `2a652b18de280fa50d0f1e46f9caebe41c70755a`
- GitHub release record: published URL `https://github.com/corca-ai/charness/releases/tag/v3.2.0`
- public release surface verification: confirmed by unauthenticated HTTPS page readback; REST API readback was rate-limited with HTTP 403 and is not claimed.
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release helper at
  `https://github.com/corca-ai/charness/releases/tag/v3.2.0`.
- Distinct-channel public readback: unauthenticated `curl` page returned HTTP
  200; the page contained `Charness 3.2.0` and `v3.2.0`.
- REST API readback: unauthenticated `curl` returned HTTP 403, rate-limit
  message; this is recorded as unavailable, not as release evidence.

## Remote Branch and CI Readback

- Branch observer: GitHub API `refs/heads/main` returned exact SHA
  `2a652b18de280fa50d0f1e46f9caebe41c70755a`.
- Commit observer: GitHub API `/commits/2a652b18de280fa50d0f1e46f9caebe41c70755a`
  returned the same SHA.
- CI workflow: `Quality Core`, run `30874005717`, head SHA
  `2a652b18de280fa50d0f1e46f9caebe41c70755a`, completed `success`.
- CI jobs: `Core deterministic gates` success and `Changed-line mutation
  coverage (push/PR mirror)` success; the latter completed at
  `2026-08-04T03:22:52Z`.
- This readback is separate from the `git push` exit code and is the release
  commit's remote CI proof.

## Lifecycle Usage Capture

- Lifecycle capture status: not recorded by this helper invocation.

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
- Retro artifact: `charness-artifacts/retro/2026-08-04-v3-2-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 1.
  - `skills/support/markdown-preview/scripts/markdown_preview_render.py`
- Evaluated changed paths: 126.
  - `.agents/critique-adapter.yaml`
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-08-03-211703-packet.json`
  - `charness-artifacts/critique/2026-08-03-211703-packet.md`
  - `charness-artifacts/critique/2026-08-03-221939-packet.json`
  - `charness-artifacts/critique/2026-08-03-221939-packet.md`
  - `charness-artifacts/critique/2026-08-03-222903-packet.json`
  - `charness-artifacts/critique/2026-08-03-222903-packet.md`
  - `charness-artifacts/critique/2026-08-03-223438-packet.json`
  - `charness-artifacts/critique/2026-08-03-223438-packet.md`
  - `charness-artifacts/critique/2026-08-03-225320-packet.json`
  - `charness-artifacts/critique/2026-08-03-225320-packet.md`
  - `charness-artifacts/critique/2026-08-04-critique-review.md`
  - `charness-artifacts/critique/2026-08-04-decide-where-a-recurring-lesson-lives-disposition-review.md`
  - `charness-artifacts/critique/2026-08-04-issue-497-500-501-resolution-critique.md`
  - `charness-artifacts/critique/2026-08-04-issue-497-500-501-resolution-packet.json`
  - `charness-artifacts/critique/2026-08-04-issue-497-500-501-resolution-packet.md`
  - `charness-artifacts/critique/2026-08-04-make-recurring-closeout-cost-actionable-critique.md`
  - `charness-artifacts/critique/2026-08-04-release-3-2-0-additive-operator-surface-packet.json`
  - `charness-artifacts/critique/2026-08-04-release-3-2-0-additive-operator-surface-packet.md`
  - ... 106 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-04-release-3-2-0-additive-operator-surface.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Install Refresh

- Post-publish install refresh: `refreshed`; `charness update` returned 0 and
  reported checkout, Codex source/cache, and installed surfaces at `3.2.0`.
- Post-publish version readback: `charness version` returned `version: 3.2.0`.
- Post-publish doctor readback: `charness doctor` returned 0 with checkout,
  Codex source/cache, and target repo at `3.2.0`, with no cache drift.

## Release Runtime

- `requested_review_gate`: 0.002s
- `cli_skill_surface_gate`: 1.819s
- `quality_command`: 168.190s
- `fresh_checkout_probes_initial`: 3.457s
- `remote_branch_ci_readback`: recorded in this artifact and the public-readback artifact.
- `public_release_readback`: recorded by unauthenticated HTTPS page; API channel unavailable (403).
- `post_publish_install_refresh`: returned 0; installed surfaces refreshed.
- `post_publish_version_readback`: returned 0.
- `post_publish_doctor_readback`: returned 0.

## Baton Reconcile

- Baton reconcile observation: `n/a` — `docs/handoff.md` carries no release
  version claim in its `## Current State` / `## Next Session` routing sections;
  no version-specific reconcile was needed.

## Fresh Checkout Probes

- Fresh-checkout probe status: passed.
- `./charness --help >/dev/null`
- `./charness goal check --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --json --skip-release-probe >/dev/null`

## Issue Closeout

- Issue closeout verification: `not_requested`; remote issues #496 and #503
  remain open and no issue-close phase was run.

## User Update Steps

- Run `charness update` to install the latest published Charness release.
- Read the GitHub release notes for release-specific behavior changes, migrations, or rollback notes.
