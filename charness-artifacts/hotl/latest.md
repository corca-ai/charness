# HOTL Current: Open issue closeout

Status: closed with #371 issue disposition
Last audited: 2026-06-16

## Current Loop

- Scope: open issue closeout for #375, #376, #377, #378, and #371.
- Source packet:
  [2026-06-16-open-issue-hotl-closeout-proof-packet.md](./2026-06-16-open-issue-hotl-closeout-proof-packet.md).
- Historical validated carrier draft for #375-#378:
  [2026-06-16-issues-375-378-closeout-carrier-draft.md](./2026-06-16-issues-375-378-closeout-carrier-draft.md).
- Published release carrier: `v0.51.0`
  (https://github.com/corca-ai/charness/releases/tag/v0.51.0).

## Current Evidence

- #375, #376, #377, and #378 have local implementation proof, fresh-eye
  critique artifacts, branch-wide local gate proof, and published release
  closeout proof.
- Release helper issue closeout is `verified`; independent GitHub readback
  reports #375, #376, #377, and #378 `CLOSED`.
- The branch-wide changed-line mutation coverage consumer over
  `git merge-base origin/main HEAD` returns `"ok": true`, `"blocking": []`, and
  no `blocking_targets` for the changed mutation-pool files.
- #371 is excluded from the validated carrier. Current evidence supports only
  downstream post-hoc mitigation, not invocation-end browser process/profile
  teardown.

## Current Blockers

- #371 remains `OPEN`.
- #371 must remain open unless controlled proof covers normal completion,
  cancellation, provider failure, and timeout teardown for both the browser
  process tree and matching `agent-browser-chrome-*` profile directory.

## Next Action

- Keep #371 separate until lifecycle proof exists or an explicit operator
  decision changes its disposition.
- Restart active Codex/Claude sessions if they need the freshly installed
  Charness v0.51.0 plugin cache.
