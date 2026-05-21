# Release Diff Failure Suppression Debug
Date: 2026-05-22

## Problem

The release publish helper converted `git diff --name-only <base>..HEAD`
failures into an empty unreleased-path list, so a broken release delta could
silently suppress real-host proof selection.

## Correct Behavior

Given release publication needs an unreleased-path delta, when `git diff
--name-only <base>..HEAD` fails, then publish must fail before version bumps,
quality proof, artifact writes, tags, pushes, or GitHub release creation.

## Observed Facts

- `unreleased_paths()` returned `[]` on a nonzero diff subprocess.
- `publish_release.py` computes unreleased paths before dry-run and execute
  branches, so the fail-closed behavior intentionally affects dry-runs too.
- A fake-git regression can force `git diff --name-only` to exit `42` with
  stderr `forced diff failure`.
- Focused publish proof now exits before release mutation and reports the
  failed command, base ref, exit code, stdout, and stderr.

## Reproduction

Run `publish_release.py --execute` in a seeded release repo with
`FAKE_GIT_DIFF_NAME_ONLY_FAIL=1`. Before the fix, the failed diff became an
empty path set. After the fix, stderr starts with `release diff failed while
computing unreleased paths` and includes `exit_code: 42`.

## Candidate Causes

- The release helper treated unknown diff state as equivalent to no changed
  release paths.
- Real-host proof selection was allowed to continue after its input delta was
  unreliable.
- Existing publish-path tests covered positive real-host deltas but not
  failure of the git diff command that feeds them.

## Hypothesis

If `unreleased_paths()` raises on nonzero `git diff --name-only`, and the
publish-path regression asserts no mutation after that failure, then release
proof suppression from an unreadable delta is blocked.

## Verification

- Focused pytest passed for the new execute-mode and dry-run fail-closed
  regressions plus existing real-host delta tests.
- `ruff check` passed for the changed release helper and publish tests.
- `python3 scripts/check_python_lengths.py --repo-root .` passed.
- `./scripts/run-quality.sh --read-only` and `run_slice_closeout.py` passed.

## Root Cause

`unreleased_paths()` returned an empty list for a failed diff command, collapsing
an unknown release delta into the same representation as a clean delta.

## Detection Gap

- release diff command | no regression for nonzero `git diff --name-only` in
  publish flow | add fake-git failure injection and no-mutation assertions.
- release proof inputs | helper error was advisory by omission | make the
  helper fail closed with command and stream details.
- dry-run planning | dry-run could inherit the same misleading path set | share
  the same fail-closed path before dry-run output.

## Sibling Search

- Mental model: missing release delta evidence can be treated as no release
  delta evidence.
- fixed now: nonzero `git diff --name-only` in `unreleased_paths()`.
- deferred: broad exceptions in real-host payload collection still need their
  own design because they may be advisory by host type.
- deferred: post-create release verification remains the larger release-side
  caveat recorded in release and quality artifacts.
- deferred: `_release_base_ref()` fallback behavior on tag lookup/fetch failure
  needs a separate compatibility review before changing behavior.

## Seam Risk

- Interrupt ID: release-diff-failure-suppression
- Risk Class: contract-freeze-risk
- Seam: release git delta -> real-host proof selection -> publish mutation
- Disproving Observation: fake-git diff failure now exits before any release
  mutation and prints the failed command details.
- What Local Reasoning Cannot Prove: whether every remaining real-host proof
  suppression path should be fatal instead of advisory.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: docs/handoff.md

## Prevention

Keep release proof producer failures distinct from empty proof results. Publish
tests that inject external-tool failures must assert both the diagnostic and the
absence of version bumps, artifact writes, commits, tags, pushes, and release
creation.

## Related Prior Incidents

- `2026-05-21-bug-pattern-sibling-scan.md`: sibling scan surfaced release
  current-pointer and release diff suppression risks.
- `2026-05-17-empty-policy-silent-pass.md`: previous empty-result silent pass
  showed why unknown state must not be represented as success.
