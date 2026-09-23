# Release Surface Check
Date: 2026-09-23

## Scope

Advanced `charness` toward release `8.10.0` (tag `v8.10.0`) through the repo-owned release helper.

## Current Version

- previous version: `8.9.8`
- target version: `8.10.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release --read-only` exited 0 in 405.9s at `post-claims-review, pre-push`, measured by this helper (`./scripts/run-quality.sh --release --read-only --receipt-json=/home/hwidong/.cache/tmp/charness/runtime/811b9f8f8a808bfa/scratch/release-prepush-quality/136444-1790128339723892542/semantic-quality.json`).
- pre-push quality receipt: `charness-artifacts/release/8.10.0-prepush-quality.json` (sha256: `bd93b769e9254c0ab02c09b4fbbcb624a80d482c172e33e18161046ba637d903`).
- `current_release.py` reported no version drift across 4 versioned surface(s), with 1 presence-only surface(s) not version-checked against target `8.10.0`, checked at `post-claims-review, pre-push`.
- initial release push carried the release branch update and tag from the release helper.
- post-publish artifact push recorded the verified public release state on the release branch.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v8.10.0`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v8.10.0`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v8.10.0`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `unauthored` (advisory; never blocks a publish).
- The published body carries no authored notes (82 body bytes) — this release shipped with a generated changelog line and nothing else. `gh release edit` is the remedy; the release itself is unaffected.
- Disposition reason: published body carries no authored notes (generated changelog line only); `gh release edit` is the remedy

## Release Adapter Preflight

- Release adapter focused preflight status: `not_required`.
- Reason: release adapter did not change in the release delta
- Focused preflight commands: none planned.
- Focused preflight execution: NOT recorded by this helper invocation; this record does not establish that the commands above ran.

## Review Proof

- Review proof: `charness-artifacts/critique/v8100-critique.md`.

## Claims Review

- Claims review record: `charness-artifacts/release-review/2026-09-23-v8.10.0-prepared-claims-review.json`.
- Claims review verdict: `pass`.
- Observer distinctness: `separate-agent-context`.
- Recorded signal: subagent task 01a0cbe9-3d62-74a3-919f-4529fe98da13 completed with delivered findings envelope; parent session retains the child session log as the distinct-context signal
- Review narrative: `charness-artifacts/release-review/v8100-claims-narrative.md`.
- Verdict scope: 31 blocking path(s) gated this tag; 1 advisory path(s) (session narrative) were reviewed but did not.
- Advisory findings: 3 finding(s) recorded in advisory scope and carried into this release record without gating this tag:
  - Quality exit-0 reported alongside explicit unestablished declaration; pytest-release proof pending at resume.
  - Fresh-checkout passed is helper-measured only, no persisted log artifact; resume re-runs probes.
  - No v8.10.0 notes file yet (generate-notes at publish); verify notes exist before calling the release public.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v8.10.0`.

## Install Refresh

- Post-publish install refresh status: `failed`.
- Command: `charness update`
- Return code: `1`
- Elapsed seconds: `1.105`
- Stderr tail: `STEP: refreshing source checkout
managed checkout `/home/hwidong/.agents/src/charness` diverged from `origin/main` (ahead 4, behind 10); `charness update` only fast-forwards managed checkouts. If the local commit is intentional dogfood, run `charness update --repo-root . --no-pull --skip-cli-install` from that checkout. Otherwise rebase or reset the managed checkout onto `origin/main` and retry.
STDOUT:

STDERR:
From https://github.com/corca-ai/charness
   91ce106e4..4e1aee721  main       -> origin/main
 * [new tag]             v8.10.0    -> v8.10.0
hint: Diverging branches can't be fast-forwarded, you need to either:
hint:
hint: 	git merge --no-ff
hint:
hint: or:
hint:
hint: 	git rebase
hint:
hint: Disable this message with "git config set advice.diverging false"
fatal: Not possible to fast-forward, aborting.`

## Release Runtime

- `requested_review_gate`: 0.007s
- `cli_skill_surface_gate`: 2.377s
- `quality_command`: 405.907s
- `fresh_checkout_probes_resume`: 6.367s
- `push_create_verify_release`: 387.229s
- `distinct_channel_verification`: 0.619s
- `published_notes_audit`: 0.392s
- `post_publish_install_refresh`: 1.105s
- `post_publish_installed_readback`: 1.186s
- `release_observer`: 0.001s
- `issue_closeout_carrier`: 17.407s
- `issue_closeout`: 2.339s

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-09-23-v8.10.0-release-observer.json`.
- Installed readback disposition: `version-mismatch`.
- Verdict ownership: this record embeds `distinct_channel_verification`; it does not declare a second release-success verdict.

## Fresh Checkout Probes

- Fresh-checkout probe status: passed.
- `./charness --help >/dev/null`
- `./charness goal run --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --skip-release-probe >/dev/null`

## Issue Closeout

- Issue closeout verification: `state-verified`.
- GitHub repo: `corca-ai/charness`
- Issue #831: `CLOSED` (https://github.com/corca-ai/charness/issues/831)
  - carrier: `direct_post_publish_commit_body`
  - manual fallback used: `False`
- Issue #832: `CLOSED` (https://github.com/corca-ai/charness/issues/832)
  - carrier: `direct_post_publish_commit_body`
  - manual fallback used: `False`

## User Update Steps

- Run `charness update` to fast-forward the managed checkout on its configured branch; that branch carries the latest published Charness release and any commits landed after it, and `charness version` names the installed version.
- Read the GitHub release notes for release-specific behavior changes, migrations, or rollback notes.


## Bump Rationale

> minor, not patch: alongside the #831 behavior repair and the #832 leak fix, the release adds operator-facing surface (preflight scope_warnings, receipt scope_extension_request/lane_env fields, rescope_result helper, CHARNESS_TASK_RUN_KEEP_SECRET_ENV) that existing users adopt without migration.