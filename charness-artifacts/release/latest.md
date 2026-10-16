# Release Surface Check
Date: 2026-10-17

## Scope

Advanced `charness` toward release `8.14.7` (tag `v8.14.7`) through the repo-owned release helper.

## Current Version

- previous version: `8.14.6`
- target version: `8.14.7`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release --read-only` exited 0 in 324.5s at `post-claims-review, pre-push`, measured by this helper (`./scripts/run-quality.sh --release --read-only --receipt-json=/home/hwidong/.cache/tmp/charness/runtime/212fea5446419103/scratch/release-prepush-quality/3466784-1792191342784897502/semantic-quality.json`).
- pre-push quality receipt: `charness-artifacts/release/8.14.7-prepush-quality.json` (sha256: `d0e980c5812f7e2c66998b2f0f023e0471b84f0fe63d47cdbf9cca7dfdbd2845`).
- `current_release.py` reported no version drift across 4 versioned surface(s), with 1 presence-only surface(s) not version-checked against target `8.14.7`, checked at `post-claims-review, pre-push`.
- Validated tree: commit `4e8dc49b70bf7db6bed83b29793a763123c4cd25` (tree `9bcdb280a4c0ab47b49a038c2835c7980880eaff`); a pushed tag or branch that does not contain this tree was not what this check validated.
- initial release push carried the release branch update and tag from the release helper.
- post-publish artifact push recorded the verified public release state on the release branch.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v8.14.7`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v8.14.7`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v8.14.7`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `clean` (advisory; never blocks a publish).
- No mutable source-tree pointers found (3085 body bytes).

## Release Adapter Preflight

- Release adapter focused preflight status: `not_required`.
- Reason: release adapter did not change in the release delta
- Focused preflight commands: none planned.
- Focused preflight execution: NOT recorded by this helper invocation; this record does not establish that the commands above ran.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-10-17-v8.14.7-release-critique.md`.

## Claims Review

- Claims review record: `charness-artifacts/release-review/2026-10-17-v8.14.7-prepared-claims-review.json`.
- Claims review verdict: `pass`.
- Observer distinctness: `separate-agent-context`.
- Recorded signal: native agent /root/charness_integrate_release/v8147_claims_review delivered a pass verdict with two advisories to the parent context
- Review narrative: `charness-artifacts/release-review/2026-10-17-v8.14.7-claims-review.md`.
- Verdict scope: 134 blocking path(s) gated this tag; 2 advisory path(s) (session narrative) were reviewed but did not.
- Advisory findings: 2 finding(s) recorded in advisory scope and carried into this release record without gating this tag:
  - persistence wording is broader than the best-effort changed-diff SQL statement detector
  - patch rationale command-compatibility wording means existing syntax remains usable despite additive and opt-in behavior changes

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v8.14.7`.

## Install Refresh

- Post-publish install refresh status: `failed`.
- Command: `charness update`
- Return code: `75`
- Elapsed seconds: `0.004`
- Stderr tail: `maintainer install refresh withheld: parent-owned coordination; shared installed/source/cache state intentionally unchanged`

## Release Runtime

- `requested_review_gate`: 0.007s
- `cli_skill_surface_gate`: 2.113s
- `quality_command`: 324.479s
- `fresh_checkout_probes_resume`: 6.866s
- `push_create_verify_release`: 259.835s
- `distinct_channel_verification`: 0.541s
- `published_notes_audit`: 0.459s
- `post_publish_install_refresh`: 0.005s
- `post_publish_installed_readback`: 2.115s
- `release_observer`: 0.001s
- `issue_closeout`: 0.000s

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-10-16-v8.14.7-release-observer.json`.
- Installed readback disposition: `version-mismatch`.
- Verdict ownership: this record embeds `distinct_channel_verification`; it does not declare a second release-success verdict.

## Fresh Checkout Probes

- Fresh-checkout probe status: passed.
- `./charness --help >/dev/null`
- `./charness goal run --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --skip-release-probe >/dev/null`

## Issue Closeout

- Issue closeout verification: `not_requested`.

## User Update Steps

- Run `charness update` to fast-forward the managed checkout on its configured branch; that branch carries the latest published Charness release and any commits landed after it, and `charness version` names the installed version.
- Read the GitHub release notes for release-specific behavior changes, migrations, or rollback notes.


## Bump Rationale

- Bump: `8.14.6` -> `8.14.7` (`publish-current`).
> patch: this release repairs existing task-run, review-delivery, inventory, packaging, and completion behavior without changing command compatibility or requiring migration.