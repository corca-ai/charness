# Session Retro - v0.13.2 Issue Closeout Miss

## Context

The reviewed unit is the `v0.13.2` release push and the follow-up user
correction that the release should have carried GitHub close keywords.

The release itself succeeded, but the first publish command omitted
`--close-issue` flags. That left the release commit without `Close #N.`
keywords, so issues that were resolved by the tranche stayed open until a
follow-up direct-to-default repair commit.

## Evidence Summary

- `91f2245 Release charness 0.13.2` had no commit body.
- `charness-artifacts/release/latest.md` initially recorded issue closeout as
  `not_requested`.
- `7ffde0e Close released hardening issues for v0.13.2` repaired the carrier
  with `Close #268/#269/#264/#270`.
- `issue_tool.py verify-closeout --expect-state CLOSED` verified those four
  issues closed.
- `#265` and `#261` intentionally remained open because the goal artifact
  recorded remaining mutation-survivor policy/equivalence work as non-claims.

## Waste

- The release had to be repaired after publication, creating two extra commits
  and a trust hit.
- The final answer claimed "issue close was not requested" even though the
  workflow expectation was that resolved issue closeout should be carried by
  the release commit.
- The release artifact briefly held stale `not_requested` state after live
  closeout had been repaired.

## Root Cause

The immediate mistake was not passing `--close-issue 268 --close-issue 269
--close-issue 264 --close-issue 270` to `publish_release.py`.

The deeper workflow failure was that I treated "push release" as a packaging
boundary and did not force an explicit issue-closeout subset before executing
the helper. The goal artifact contained enough information to distinguish
closeable issues from non-claims, but I did not convert that into helper flags.

The fresh-eye review also warned "do not claim live issue closure" and "do not
close #265/#261"; I overfit to the warning as a reason to avoid issue closeout
entirely instead of deriving the correct subset.

## Critical Decisions

- Correct: `#265` and `#261` stayed open.
- Incorrect: `#268`, `#269`, `#264`, and `#270` were not passed through the
  release helper's closeout path.
- Correct repair: use a direct-to-default closeout commit with validated body
  and verify final GitHub state as `CLOSED`.

## Expert Counterfactuals

Gary Klein premortem: before publish, ask "what will be embarrassingly false in
the final answer?" The answer would have been "resolved issues are still open,"
which forces a `close_issue_numbers` checklist item before `--execute`.

Daniel Kahneman checklist discipline: do not let a fluent narrative ("release
done") substitute for a base-rate checklist. The release command should be
derived from a visible table: close, leave open, reason.

## Next Improvements

- workflow: Before any release that follows a goal or issue-resolution tranche,
  build a short issue closeout matrix: `close`, `leave open`, `reason`, and map
  every `close` row to `--close-issue`.
- capability: Add a release preflight that fails or warns when recent goal or
  release artifacts mention resolved issue numbers but the publish payload has
  `close_issue_numbers: []`.
- capability: Teach the release critique packet to include an explicit
  "issue closeout subset" field, not just generic warnings about live issue
  mutation.
- memory: Keep this retro as the recurrence marker for "avoid-all-closeout"
  overcorrection after a reviewer warns not to close some issues.

## Sibling Search

Transferable pattern: a helper supports a required side-effect by flag, but the
agent treats the absence of flags as a valid default.

Sibling surfaces to inspect next:

- release helper: infer or require a closeout decision when issue numbers are
  named in the release/goal context
- issue helper: make direct-to-default repair easier to invoke when release
  closeout was missed
- achieve closeout: ensure final `Release:` coordination cue distinguishes
  "release needed" from "release plus issue auto-close needed"

## Persisted

Persisted by draft at
`charness-artifacts/retro/2026-06-01-release-issue-closeout-miss-draft.md`;
the retro persistence helper should write the canonical artifact.
