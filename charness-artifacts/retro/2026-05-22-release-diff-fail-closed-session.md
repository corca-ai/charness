# Session Retro: Release Diff Fail-Closed

Date: 2026-05-22
Mode: session

## Context

This session continued the bug-pattern sibling scan and repaired the release
publish path that treated a failed unreleased-path diff as an empty release
delta.

## Evidence Summary

- Debug artifact:
  `charness-artifacts/debug/2026-05-22-release-diff-failure-suppression.md`.
- Fresh-eye critique found two real misses: dry-run behavior needed a direct
  regression, and dogfood review metadata drifted outside the release case.
- Closeout: `python3 scripts/run_slice_closeout.py --repo-root . --ack-cautilus-skill-review`
  completed.
- Quality: `./scripts/run-quality.sh --read-only` passed with `65` checks.

## Waste

- The first regression proved execute-mode fail-closed behavior but made a
  dry-run claim in artifacts before pinning dry-run stdout.
- Dogfood JSON patching briefly touched adjacent review metadata, so the
  reviewer had to catch unrelated public-skill evidence churn.

## Critical Decisions

- Fail closed in `unreleased_paths()` instead of treating unknown git delta
  state as no release content paths.
- Add both execute-mode and dry-run publish regressions, with dry-run asserting
  no JSON stdout.
- Keep broader real-host payload exception policy, post-create verification,
  and base-ref fallback redesign out of this slice.

## Expert Counterfactuals

- Gary Klein lens: before writing RCA claims, ask what observable mode differs
  from the main regression; here that was dry-run stdout.
- Daniel Kahneman lens: treat JSON metadata edits as high-risk for accidental
  neighbor churn and inspect the full file diff before validators.

## Next Improvements

- workflow: whenever an artifact says a shared path affects dry-run and execute,
  include one assertion for each visible mode before closeout.
- workflow: after editing long checked-in JSON registries, review the diff
  before running broad gates so neighbor metadata churn is caught locally.
- memory: keep release proof suppression split into fixed diff failure and
  deferred real-host payload/post-create/base-ref risks.

## Persisted

Persisted: yes `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`
