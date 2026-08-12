## Observed

The supported release path cannot satisfy the release contract's required
pre-publication claims review. `publish_release.py --execute` calls
`_create_release_commit()`, which bumps and synchronizes the release surface,
writes the final release record, runs release quality and fresh-checkout probes,
and commits that record. It then calls `_publish_and_finalize()` in the same
execution, which tags, pushes, creates the GitHub release, and verifies it.

The release contract requires a distinct claims-review round after the version
and final release record exist, but before publication makes that record public.
There is no supported CLI stage that pauses between those two operations.
`--resume --publish-current` is recovery for an already partial release attempt,
not a documented preparation stage; directly calling private helper functions
would create unsupported recovery state.

Evidence:

- `skills/public/release/scripts/publish_release_execute.py`
- `skills/public/release/references/critique-boundary.md` (`Claims Review` and
  `Timing`)

## Impact

An operator must either skip the independent claims review or bypass the
release helper's supported workflow. Both choices violate the release contract,
so this blocks publication of the prepared v5.1.0 candidate.

## Candidate direction (non-binding)

Provide a supported prepare/local-release-record stage, followed by a supported
resume-to-publish operation. The split should retain rollback behavior, release
quality, manifest synchronization, and the no-issue-close default while giving
the claims reviewer an immutable local record to inspect before tag, push, or
GitHub release creation.

## Non-claims

- This issue does not authorize weakening the critique or claims-review floor.
- It does not authorize closing any tracker issue.
- No v5.1.0 version bump, tag, push, hosted-CI proof, GitHub release, or
  installed-tool readback has occurred.
