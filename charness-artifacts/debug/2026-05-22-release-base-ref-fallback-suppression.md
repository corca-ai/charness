# Release Base Ref Fallback Suppression Debug
Date: 2026-05-22

## Problem

Release publish could treat an unavailable previous-release tag base as the
branch base, so already-pushed release-surface changes could disappear from the
real-host proof delta.

## Correct Behavior

Given a previous release version is known and the local tag is missing, when
the remote tag lookup or fetch fails, then dry-run and execute publish must fail
before JSON output, version bumps, artifacts, quality proof, commits, tags,
pushes, or release creation. A successful remote tag fetch must still use the
tag ref as the release delta base.

## Observed Facts

- `_release_base_ref()` checked the local tag, then `git ls-remote --tags`, then
  `git fetch --quiet`, but any lookup or fetch failure fell through to
  `origin/<branch>`.
- In the already-pushed branch case, falling back to `origin/main..HEAD` can
  produce an empty delta even when `refs/tags/v0.0.0..HEAD` contains the
  release-surface change.
- `publish_release.py` already calls `ensure_release_target_available()` before
  `unreleased_paths()`, so the release flow has already required the remote to
  answer a target-tag lookup.
- Fresh-eye review required both execute and dry-run assertions and log proof
  that no fallback diff runs after lookup or fetch failure.

## Reproduction

Create a fixture repo where `v0.0.0` exists on `origin`, delete the local tag,
change `README.md`, commit and push `main`, then force either
`git ls-remote --tags origin refs/tags/v0.0.0` or
`git fetch --quiet origin refs/tags/v0.0.0:refs/tags/v0.0.0` to fail while
running `publish_release.py --part patch` or `--part patch --execute`.

## Candidate Causes

- The base-ref helper treated remote lookup/fetch failures as equivalent to
  "tag absent".
- The release proof path trusted a branch fallback even after a previous release
  version was known.
- Tests covered successful missing-local-tag fetch but not failed lookup/fetch.

## Hypothesis

If `_release_base_ref()` raises with the failed command details whenever the
previous tag lookup or fetch fails, then publish cannot collapse unknown release
base state into an empty branch delta.

## Verification

- Focused pytest passed for the release real-host delta suite, including
  execute and dry-run fail-closed regressions for previous-tag lookup failure
  and previous-tag fetch failure.
- `python3 scripts/check_python_lengths.py --repo-root .` passed after adding
  the regressions.
- Fresh-eye review executed before closeout and required the same-function
  `ls-remote` failure case, which was added to this slice.

## Root Cause

The release base-ref helper encoded an unknown previous-release tag base as a
safe branch fallback. That fallback is only safe when the tag is explicitly
absent, not when the remote lookup or fetch command fails.

## Detection Gap

- release base-ref lookup | failed `ls-remote` fell back to branch diff | add
  execute and dry-run fail-closed regressions.
- release base-ref fetch | known remote tag fetch failure fell back to branch
  diff | add execute and dry-run fail-closed regressions.
- fallback proof | no assertion proved branch diff was not reached after base
  lookup/fetch failure | assert git log ordering in failure tests.

## Sibling Search

- Mental model: release proof can fall back to a broader branch base when tag
  proof is unavailable.
- fixed now: release diff, broken real-host config, real-host proof-builder
  failure, and previous-tag lookup/fetch failures all fail before dry-run output
  or execute mutation.
- deferred: post-create public release verification still records `not_checked`
  after external mutation and needs separate recovery design.
- deferred: mutation changed-file discovery can still turn `git diff` failure
  into no changed files; this is the next non-release fail-closed slice.
- deferred: read-only quality changed-path discovery still contains shell
  `|| true` fallbacks and needs separate gate design.

## Seam Risk

- Interrupt ID: release-base-ref-fallback-suppression
- Risk Class: contract-freeze-risk
- Seam: previous release tag discovery -> unreleased-path delta -> real-host proof trigger
- Disproving Observation: failed previous-tag lookup/fetch now exits before
  dry-run JSON or execute-mode mutation.
- What Local Reasoning Cannot Prove: post-create recovery semantics after a
  release record has already been created.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: docs/handoff.md

## Prevention

Do not treat failed discovery commands as empty release inputs. When a fallback
would shrink the proof boundary, tests must assert both dry-run visibility and
execute-mode mutation boundaries.

## Related Prior Incidents

- `2026-05-22-release-diff-failure-suppression.md`: diff failure collapsed
  unknown release delta into no real-host proof.
- `2026-05-22-release-real-host-config-suppression.md`: proof-builder failure
  collapsed unknown real-host proof state into no proof required.
