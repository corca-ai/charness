# Release Post-Create Verification Suppression Debug
Date: 2026-05-22

## Problem

`publish_release.py` could create a GitHub release, fail to verify it with the
release backend, record `public_release_verification: not_checked`, and still
continue into issue closeout and success-oriented artifact recovery.

## Correct Behavior

Given the release create command has already returned a release URL, when
post-create release visibility cannot be verified after bounded retries, then
publish must record the failed verification in the post-publish artifact, push
that recovery artifact, and exit nonzero before issue closeout. The
pre-create artifact may still say the public release surface is not checked by
that helper invocation.

## Observed Facts

- `create_release()` returned the backend stdout URL before any post-create
  verification decision.
- The final artifact path could be rewritten after mutation, so a failed
  post-create check has a recovery surface even though the release mutation
  already happened.
- The previous finalization path used the same `not_checked` value for
  pre-create state and post-create verification failure.
- A fake `gh release create` can return a URL without making `gh release view`
  succeed, reproducing the suppressed verification branch deterministically.

## Reproduction

Run `publish_release.py --part patch --execute` in the seeded release fixture
with `FAKE_GH_RELEASE_CREATE_WITHOUT_VIEW=1`. Before the fix, the flow could
continue after release creation with a non-verified public release state. After
the fix, stderr starts with `release post-create verification failed after
external mutation`, includes the failed `gh release view v0.0.1` command, and
reports a committed post-publish artifact SHA.

## Candidate Causes

- The publish flow represented failed post-create verification as the same
  `not_checked` state used before create.
- The release artifact text had no failed-verification wording distinct from
  "expected after push" recovery.
- Issue closeout was allowed to proceed even though the public release record
  had not been verified after external mutation.

## Hypothesis

If post-create verification retries `release view`, records
`public_release_verification: failed` when the check remains unavailable, pushes
the recovery artifact, and raises before issue closeout, then the release helper
cannot present an externally mutated but unverified release as a successful
publish.

## Verification

- Focused pytest passed for post-create verification failure, no issue closeout
  after post-create failure, normal release success, and manual issue-closeout
  fallback.
- `ruff check` passed for the changed release scripts and publish tests.
- `python3 scripts/check_python_lengths.py --repo-root .` passed.
- Fresh-eye review identified the same suppression and required a distinct
  failed state plus recovery artifact commit before the nonzero exit; the
  follow-up tightened tests to count only post-create `release view` attempts.

## Root Cause

The post-create verification branch reused a pre-create "not checked" artifact
state and did not treat failed public release visibility as a blocking
post-mutation recovery condition.

## Detection Gap

- post-create release verification | no fake-backend test where create returns
  a URL but view remains unavailable | add a release fixture mode that withholds
  view state after create and assert retries plus nonzero exit.
- recovery artifact semantics | no assertion distinguished pre-create
  `not_checked` from failed post-create verification | assert the final artifact
  says `public release surface verification: failed` and omits successful
  post-publish proof.
- issue closeout ordering | no failure test proved issue closeout waits for
  verified public release state | assert `gh issue close` is not called and the
  issue remains open after post-create verification failure.

## Sibling Search

- Mental model: after the external create call returns, unverified public
  release state can be treated like a pending artifact update.
- fixed now: post-create verification failure records a failed public release
  state, commits and pushes the recovery artifact, and exits nonzero.
- checked non-blocker: the initial pre-create artifact still uses `not_checked`
  because the public release cannot exist until the create command runs.
- deferred: broader completion audit should re-scan release recovery wording and
  remaining bug-pattern surfaces after this named suppression queue is cleared.

## Seam Risk

- Interrupt ID: release-post-create-verification-suppression
- Risk Class: external-seam
- Seam: GitHub release create -> release view verification -> recovery artifact and issue closeout
- Disproving Observation: fake create-without-view now retries `gh release view`
  at least three times, pushes the failed-verification artifact, and exits 1
  before issue closeout.
- What Local Reasoning Cannot Prove: whether the real GitHub API was eventually
  consistent after the bounded retry window in a live incident.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/release-post-create-verification-suppression.md

## Prevention

For post-mutation recovery paths, keep "not yet checked" distinct from
"checked and failed." Tests must force the external create/view split and assert
both the durable recovery record and the boundary where later success steps stop.

## Related Prior Incidents

- `2026-05-22-release-base-ref-fallback-suppression.md`: release proof fallback
  converted unknown previous-tag state into a smaller proof boundary.
- `2026-05-22-release-real-host-config-suppression.md`: real-host proof failure
  was represented as no proof required.
- `2026-05-22-release-diff-failure-suppression.md`: failed release delta
  discovery was represented as an empty changed-path set.
