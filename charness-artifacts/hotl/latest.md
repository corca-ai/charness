# HOTL Current: Open issue closeout

Status: active-audit; proof incomplete
Last audited: 2026-06-16

## Current Loop

- Scope: open issue closeout for #375, #376, #377, #378, and #371.
- Source packet:
  [2026-06-16-open-issue-hotl-closeout-proof-packet.md](./2026-06-16-open-issue-hotl-closeout-proof-packet.md).
- Validated carrier draft for #375-#378:
  [2026-06-16-issues-375-378-closeout-carrier-draft.md](./2026-06-16-issues-375-378-closeout-carrier-draft.md).

## Current Evidence

- #375, #376, #377, and #378 have local implementation proof, fresh-eye
  critique artifacts, branch-wide local gate proof, and a feature-class PR-body
  draft validated by `issue_tool.py validate-closeout-draft` as
  `draft_verified` / `ready_to_publish`.
- The branch-wide changed-line mutation coverage consumer over
  `git merge-base origin/main HEAD` returns `"ok": true`, `"blocking": []`, and
  no `blocking_targets` for the changed mutation-pool files.
- #371 is excluded from the validated carrier. Current evidence supports only
  downstream post-hoc mitigation, not invocation-end browser process/profile
  teardown.

## Current Blockers

- GitHub source-of-truth readback still has #378, #377, #376, #375, and #371
  `OPEN`.
- No push, PR, merge, release, issue comment, or manual close has been performed
  from this HOTL packet.
- #371 must remain open unless controlled proof covers normal completion,
  cancellation, provider failure, and timeout teardown for both the browser
  process tree and matching `agent-browser-chrome-*` profile directory.

## Next Action

- Coordinate with any other active agent before remote mutation.
- If publishing is approved, use the #375-#378 carrier draft as the PR body or
  equivalent closeout carrier, then run `issue_tool.py verify-closeout` after
  merge/publish with `--expect-state CLOSED`.
- Keep #371 separate until lifecycle proof exists or an explicit operator
  decision changes its disposition.
