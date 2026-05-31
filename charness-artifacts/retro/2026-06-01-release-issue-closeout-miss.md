# Session Retro - v0.13.2 Issue Closeout Miss

## Context

The reviewed unit is the `v0.13.2` push and the follow-up user correction that
the commits resolving GitHub issues should have carried close keywords.

The release was only the carrier that happened to expose the miss. The real
contract is commit/PR-level: when a direct-to-default commit resolves issues,
the commit body must carry `Close #N.` keywords plus the closeout ledger before
it is pushed. In a PR flow, the PR body is the carrier instead.

## Evidence Summary

- `91f2245 Release charness 0.13.2` had no commit body, so it could not close
  issues even though it was the direct-to-default carrier for the resolved
  tranche.
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

The immediate mistake was not putting the close keywords on the commit that
resolved the issue tranche. Because the release helper generated that commit,
the concrete missing command flags were `--close-issue 268 --close-issue 269
--close-issue 264 --close-issue 270`.

The deeper workflow failure was treating issue closeout as release-specific
instead of commit-carrier-specific. The goal artifact contained enough
information to distinguish closeable issues from non-claims, but I did not
convert that into a commit-message requirement before the carrier was created.

The fresh-eye review also warned "do not claim live issue closure" and "do not
close #265/#261"; I overfit to the warning as a reason to avoid issue closeout
entirely instead of deriving the correct subset.

## Critical Decisions

- Correct: `#265` and `#261` stayed open.
- Incorrect: `#268`, `#269`, `#264`, and `#270` were not carried in the commit
  body that first pushed their fixes to the default branch.
- Correct repair: use a direct-to-default closeout commit with validated body
  and verify final GitHub state as `CLOSED`.

## Expert Counterfactuals

Gary Klein premortem: before commit/push, ask "what will be embarrassingly
false in the final answer?" The answer would have been "resolved issues are
still open," which forces the closeout carrier to be checked before publish.

Daniel Kahneman checklist discipline: do not let a fluent narrative ("release
done" or "commit done") substitute for a base-rate checklist. The commit or PR
body should be derived from a visible table: close, leave open, reason.

## Next Improvements

- workflow: Before any task-completing commit/PR that resolves issues, build a
  short issue closeout matrix: `close`, `leave open`, `reason`, and map every
  `close` row to the carrier body.
- capability: Add a `commit-msg` hook, not a `pre-commit` hook, that recognizes
  staged issue-closeout artifacts and blocks the commit when the message lacks
  required close keywords and ledger fields. `pre-commit` can only flag staged
  context; it cannot validate the final commit message.
- capability: Add release-helper preflight as a specialized instance of the
  same invariant: when the helper is about to create a direct-to-default commit
  for a resolved tranche, empty `close_issue_numbers` should require an explicit
  "no issues close" decision.
- capability: Teach critique packets to include an explicit "issue closeout
  subset" field, not just generic warnings about live issue mutation.
- memory: Keep this retro as the recurrence marker for "avoid-all-closeout"
  overcorrection after a reviewer warns not to close some issues.

## Sibling Search

Transferable pattern: a commit/PR carrier is created without proving whether it
is also responsible for issue closeout.

Sibling surfaces to inspect next:

- `.githooks/commit-msg`: block issue-resolution commits whose message omits
  close keywords or the closeout ledger.
- `.githooks/pre-commit`: optionally detect staged `charness-artifacts/issue/*`
  closeout artifacts and print the expected commit-message carrier requirement.
- release helper: treat `--close-issue` as the direct-commit carrier mechanism,
  not as a separate release-only concern.
- achieve closeout: ensure final coordination cues distinguish "work resolved
  an issue" from "work mentioned an issue but intentionally leaves it open."

## Persisted

Persisted: yes
`charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`.
