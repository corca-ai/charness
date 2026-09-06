# Release plan: issue review readiness

The operator authorized push and release after the local repair was completed. Target: Charness 8.6.0, from 8.5.0; minor because `review-resolution` is an additive maintained operator command. Existing Git-repository invocations and final approval contracts remain supported. Non-Git compatibility was explicitly removed at the operator's request and is disclosed in the notes. Alternate provider routes remain untouched.

## Frozen scope and evidence

Source candidate: `73ab2754f`; remote main observed at `fb00b100e9f2e5ba7b6c3999ba3b38b166241261`, with no remote `v8.6.0` tag. All current release surfaces report 8.5.0 without drift. No Goal or issue transition is part of this release.

- Changed-line proof at production commit `1563e116b`: all eight changed execution files covered; no unmapped file; consumer exit zero.
- Final standing suite at `73ab2754f`: 9,266 passed in 94.25 seconds.
- Final full read-only lane: 83 passed, zero failed, five not run (browser baseline/hygiene, dead-code advisory and online supply-chain are opt-in; coverage is disabled in read-only). Separate changed-line proof is not a whole-corpus coverage claim.
- Declared fresh-checkout probes executed before release mutation: CLI help, Goal CLI help, and doctor without the release probe all passed. This is the pre-bump tree, not proof about the future tag; the publish helper must execute its post-bump probes.
- The [comparison](./comparison.json) preserves real fake-backend launch-to-consumer observations. Both public consumers reject the first baseline purpose and accept the corrected baseline and the candidate. It makes no live savings claim.
- The [code critique](../../critique/2026-09-06-review-closeout-code.md) carries delivered independent code reviews and the subsequent non-Git deletion disposition. Release critique should not rerun that implementation audit.

## Surface lock

- Additive issue CLI command and bundled-closeout usage instructions.
- Selected-document durability readiness and Git-only selection behavior; existing final closeout guards remain intact.
- Canonical packaging version and its generated Claude/Codex plugin and marketplace surfaces, changed only through the publish/sync owners.
- Public release notes and the helper-produced release/claims/observer records.

## Release boundary

Use the existing publish helper for prepare, claims-bound resume, tag/branch push, public release and distinct-channel readback. Reviewers assess operator compatibility and claim honesty with separate lenses before version mutation. A separate observer reviews the prepared publication record after it exists. Reuse unchanged local proof; do not infer publication from a local gate or a tag push.

The configured helper also refreshes the maintainer installation after publication. Explicit confirmation for that installation phase is pending; do not execute the publish workflow until this is resolved. No adapter change, hidden skip, issue close, Goal reopen, or announcement backend post is authorized by this plan.

## Non-claims and deferred work

No live end-to-end efficiency gain, whole-repository non-Git purge, or repair of the failed implementation lane's retention behavior is claimed. The [recovery record](./recovery.json) remains an explicit cost/operability limitation. A clean local tree is not yet a public release or an updated installation.
