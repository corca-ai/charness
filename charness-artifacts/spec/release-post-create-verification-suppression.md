# Release Post-Create Verification Suppression

## Problem

Release publication crossed an external seam when `gh release create` returned
a URL, but the helper could still treat failed `gh release view` verification
as `not_checked` and continue into later success steps.

## Current Slice

After release creation, verify public release visibility with bounded retries.
When verification still fails, write and push a failed-verification recovery
artifact, then exit nonzero before issue closeout.

## Fixed Decisions

- `not_checked` is reserved for pre-create artifact state.
- Failed post-create visibility is recorded as
  `public_release_verification: failed`.
- The recovery artifact is committed and pushed after the external mutation so
  operators have durable state even though the command exits nonzero.
- Issue closeout does not run unless public release verification succeeds.

## Probe Questions

- Live GitHub eventual consistency is not proven locally; the fixture proves the
  helper behavior when create and view disagree.

## Deferred Decisions

- A broader release recovery taxonomy can wait until another post-mutation
  recovery branch needs more than `verified`, `failed`, and `not_checked`.

## Non-Goals

- Do not delete or roll back a release that the external backend already
  created.
- Do not make pre-create artifacts claim public release verification.

## Constraints

- Release artifacts must distinguish expected pending state from checked failure.
- Public release verification must happen before issue closeout.
- Plugin and generated surfaces must be synced before closeout validation.

## Success Criteria

- A create-without-view backend causes a nonzero publish exit after at least
  three `release view` attempts.
- The final artifact records failed public release verification and no
  successful post-publish proof.
- The post-publish artifact commit SHA is available in the diagnostic.
- Issue closeout is skipped when post-create verification fails.
- Normal release publication still records verified public release state.

## Acceptance Checks

- `python3 -m pytest -q tests/quality_gates/test_release_publish.py -k 'post_create_verification or bumps_pushes_tags_and_creates_release or verifies_and_falls_back_to_manual_issue_close'`
- `ruff check skills/public/release/scripts/publish_release_cli.py skills/public/release/scripts/publish_release_helpers.py skills/public/release/scripts/publish_release_post_create.py skills/public/release/scripts/publish_release_artifact.py tests/quality_gates/test_release_publish.py`
- `python3 scripts/check_python_lengths.py --repo-root .`
- `python3 /home/hwidong/.codex/plugins/cache/local/charness/0.7.8/scripts/validate_debug_artifact.py --repo-root .`

## Critique

- Interrupt Source: release-post-create-verification-suppression
- Seam Summary: GitHub release create -> release view verification -> recovery artifact and issue closeout
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: the current fix does not need a public taxonomy change;
  it adds the missing post-create failure branch and focused fixture proof.
- What Disproving Observation Is Resolved: fake create-without-view now pushes
  a failed-verification artifact and exits before issue closeout.

Fresh-eye review required a distinct failed state, recovery artifact commit, and
nonzero exit after the external mutation. The follow-up tightened the regression
to count only post-create `release view` attempts, excluding the pre-create
target-availability check.

## Canonical Artifact

This spec carries the forced debug interrupt from
`charness-artifacts/debug/2026-05-22-release-post-create-verification-suppression.md`.

## First Implementation Slice

Implementation is in progress in the release publish scripts and regression
tests. The next slice is final sync, closeout validation, and commit.
