# Release Surface Check
Date: 2026-09-23

## Scope

Advanced `charness` toward release `8.9.8` (tag `v8.9.8`) through the repo-owned release helper.

## Current Version

- previous version: `8.9.7`
- target version: `8.9.8`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release --read-only` exited 0 in 281.3s at `post-claims-review, pre-push`, measured by this helper (`./scripts/run-quality.sh --release --read-only --receipt-json=/home/hwidong/.cache/tmp/charness/runtime/811b9f8f8a808bfa/scratch/release-prepush-quality/2622600-1790116061251248116/semantic-quality.json`).
- pre-push quality receipt: `charness-artifacts/release/8.9.8-prepush-quality.json` (sha256: `19df2d03d75eefe14e1b3be52eb09a4235ee494606c66467045778083291c94a`).
- `current_release.py` reported no version drift across 4 versioned surface(s), with 1 presence-only surface(s) not version-checked against target `8.9.8`, checked at `post-claims-review, pre-push`.
- initial release push carried the release branch update and tag from the release helper.
- post-publish artifact push recorded the verified public release state on the release branch.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v8.9.8`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v8.9.8`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v8.9.8`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `unauthored` (advisory; never blocks a publish).
- The published body carries no authored notes (81 body bytes) — this release shipped with a generated changelog line and nothing else. `gh release edit` is the remedy; the release itself is unaffected.
- Disposition reason: published body carries no authored notes (generated changelog line only); `gh release edit` is the remedy

## Release Adapter Preflight

- Release adapter focused preflight status: `not_required`.
- Reason: release adapter did not change in the release delta
- Focused preflight commands: none planned.
- Focused preflight execution: NOT recorded by this helper invocation; this record does not establish that the commands above ran.

## Review Proof

- Review proof: `charness-artifacts/critique/v898-critique.md`.

## Claims Review

- Claims review record: `charness-artifacts/release-review/2026-09-23-v8.9.8-prepared-claims-review.json`.
- Claims review verdict: `pass`.
- Observer distinctness: `separate-agent-context`.
- Recorded signal: subagent 01a0cb39-721e-79b3-b17b-698ceb60e699 delivered narrative 2026-09-22-v8.9.8-claims.md with version/verification/notes/closeout/proof linkage and non-claims
- Review narrative: `charness-artifacts/release-review/2026-09-22-v8.9.8-claims.md`.
- Verdict scope: 39 blocking path(s) gated this tag; 2 advisory path(s) (session narrative) were reviewed but did not.
- Advisory findings: none recorded by this review.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v8.9.8`.

## Install Refresh

- Post-publish install refresh status: `failed`.
- Command: `charness update`
- Return code: `1`
- Elapsed seconds: `1.413`
- Stderr tail: `STEP: refreshing source checkout
managed checkout `/home/hwidong/.agents/src/charness` diverged from `origin/main` (ahead 4, behind 15); `charness update` only fast-forwards managed checkouts. If the local commit is intentional dogfood, run `charness update --repo-root . --no-pull --skip-cli-install` from that checkout. Otherwise rebase or reset the managed checkout onto `origin/main` and retry.
STDOUT:

STDERR:
From https://github.com/corca-ai/charness
   5617a2f37..89f536981  main       -> origin/main
 * [new tag]             v8.9.7     -> v8.9.7
 * [new tag]             v8.9.8     -> v8.9.8
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
- `cli_skill_surface_gate`: 2.279s
- `quality_command`: 281.271s
- `fresh_checkout_probes_resume`: 6.519s
- `push_create_verify_release`: 292.541s
- `distinct_channel_verification`: 0.559s
- `published_notes_audit`: 0.451s
- `post_publish_install_refresh`: 1.413s
- `post_publish_installed_readback`: 1.133s
- `release_observer`: 0.001s
- `issue_closeout`: 0.000s

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-09-22-v8.9.8-release-observer.json`.
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

- Bump rationale: NOT recorded by this helper invocation. `version-policy.md` requires a stated rationale whenever the bump level is debatable; this record carries none, so the level above is an unexplained judgment call.