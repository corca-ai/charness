# Release Pytest Economics Closeout

Reviewer: subagent `019e92ba-4633-7c40-8e47-b4ec3a5bbef4`.

## Scope

Bounded closeout review for replacing repeated full fake release-repo failure
tests with cheaper helper-level checks while preserving publish execute-path
mutation guards.

Changed tests:

- `tests/quality_gates/test_release_publish_real_host_delta.py`
- `tests/quality_gates/test_release_publish_tag_history.py`

## Findings

- Initial blocker: both publish-current tag-discovery failure tests had been
  reduced to helper-level checks, dropping CLI `--publish-current --execute`
  mutation-guard proof.
- Fixed before commit: the local tag-discovery failure test now keeps the full
  CLI execute path and mutation guards; the remote tag-discovery failure remains
  helper-level.
- Initial low finding: tag-history tests imported a loaded private helper from
  a sibling test module.
- Fixed before commit: tag-history tests load `publish_release_helpers`
  locally. They still reuse shared fake publish setup helpers from the sibling
  test module, which is acceptable for this slice.

## Verification

- `pytest -q tests/quality_gates/test_release_publish_tag_history.py tests/quality_gates/test_release_publish_real_host_delta.py` passed with `16 passed`.
- Full non-release pytest was rerun after the final fix before commit.

## Disposition

Proceed. The slice removes repeated full publish subprocess setup from
redundant failure-path tests while retaining one execute-path mutation guard for
publish-current tag discovery and the existing execute-path guards for
real-host delta failures.
