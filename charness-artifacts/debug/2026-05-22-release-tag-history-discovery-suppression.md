# Release Tag History Discovery Suppression Debug
Date: 2026-05-22

## Problem

`publish_release.py --publish-current` could treat failed release tag history
discovery as if no previous release tag existed, then continue with
`current_version` as the previous version.

## Correct Behavior

Given publish-current must resolve the previous released version from local and
remote semver tags, when either `git tag --list` or the remote tag-history
`git ls-remote` command fails, then dry-run and execute publish must exit
nonzero before JSON output, quality proof, artifacts, commits, tags, pushes, or
release creation. An explicit absence of older semver tags may still fall back
to the current version.

## Observed Facts

- `_release_tag_versions()` ran local and remote tag discovery with
  `check=False`.
- Nonzero local discovery was ignored; nonzero remote discovery was also
  ignored.
- `release_previous_version()` then collapsed a missing candidate set into
  `current_version`, making command failure indistinguishable from "no previous
  release exists".
- The earlier base-ref fix only covered lookup/fetch failures after a previous
  version was already known.

## Reproduction

Create a fixture repository with `v0.0.0` pushed, bump the packaging manifest
to `0.0.1`, then run `publish_release.py --publish-current --execute` while a
fake `git` exits nonzero for either:

- `git tag --list v[0-9]*.[0-9]*.[0-9]*`
- `git ls-remote --tags origin refs/tags/v[0-9]*`

Before the fix, one side of discovery could be dropped and publish would keep
going. After the fix, stderr starts with `release tag discovery failed while
resolving previous release version`.

## Candidate Causes

- The helper encoded failed discovery and empty discovery with the same return
  type: a possibly empty `set[str]`.
- The publish-current fallback was safe for an explicit initial-release case
  but unsafe for unknown tag history health.
- Existing tests covered previous-tag base-ref lookup/fetch failures but not
  the earlier history enumeration step.

## Hypothesis

If `_release_tag_versions()` raises with failed command details for local or
remote tag-history discovery failures, then publish-current cannot misbase the
previous release version on incomplete tag history.

## Verification

- Focused pytest passed for local tag-list failure, remote tag-history failure,
  the successful publish-current previous-tag proof path, and the explicit
  no-previous-release-tags fallback after successful discovery.
- The new failure tests assert no JSON stdout, no quality marker, no release
  artifact, no release commit, no target tag, no push, and no release creation.
- Fresh-eye review found the no-previous-release-tags allowance was not pinned;
  the added dry-run regression now asserts both broad discovery commands ran
  and the fallback stayed at `current_version`.

## Root Cause

The release history helper treated discovery command health as optional and
left callers to interpret an empty result. For publish-current, an empty result
is only meaningful after both local and remote history commands have succeeded.

## Detection Gap

- release tag history discovery | failed `git tag --list` became an empty local
  contribution | add execute-mode fail-closed regression.
- remote release tag history discovery | failed broad `git ls-remote` became an
  empty remote contribution | add execute-mode fail-closed regression.
- publish-current mutation boundary | no assertion covered pre-mutation abort
  before release history was known | assert no quality, artifact, commit, tag,
  push, or release creation.

## Sibling Search

- Mental model: an empty discovery result is a safe fallback unless a specific
  target ref is already known.
- fixed now: release diff failure, base-ref lookup/fetch failure, post-create
  release verification failure, and publish-current tag-history discovery
  failure all fail closed where unknown state would shrink release proof.
- deferred: central `repo_file_listing.py` fallback still needs standing-gate
  strict-mode review.

## Seam Risk

- Interrupt ID: release-tag-history-discovery-suppression
- Risk Class: contract-freeze-risk
- Seam: release tag history discovery -> previous version selection -> release
  proof delta
- Disproving Observation: failed local or remote tag-history discovery exits
  before publish-current mutation.
- What Local Reasoning Cannot Prove: none for the fixture-covered command
  health boundary.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: docs/handoff.md

## Prevention

When a fallback would make unknown release history look like an initial-release
or no-prior-release case, keep command health separate from the discovered
value and prove the failure path before mutation.

## Related Prior Incidents

- `2026-05-22-release-base-ref-fallback-suppression.md`: previous release tag
  lookup/fetch failures after a previous version was known.
- `2026-05-22-release-diff-failure-suppression.md`: release diff command
  failure collapsed into an empty proof delta.
