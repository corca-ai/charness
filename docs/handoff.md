# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**. Bare
  `/handoff` runs chunked routing over handoff entries plus live open issues;
  `## Next Session` is sequencing judgment, not the full queue.
- Refresh live state before acting: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **Open-issue HOTL proof bundle is local, not published.**
  `main` is ahead of `origin/main` by 7 commits through `23be9793`
  (`hotl: validate open issue carrier draft`). The local bundle implements and
  proves #375, #376, #377, and #378, plus HOTL proof records. No push, PR, issue
  comment, manual close, or release has been performed from this packet.
- **Local branch gate is clean for the bundle.** The branch-wide changed-line
  mutation coverage consumer over `git merge-base origin/main HEAD` returns
  `"ok": true`, `"blocking": []`, and no `blocking_targets` for the 15 changed
  mutation-pool files. The proof is recorded in
  [HOTL packet](../charness-artifacts/hotl/2026-06-16-open-issue-hotl-closeout-proof-packet.md).
- **Carrier readiness exists for #375-#378 only.** The checked-in PR-body draft
  at
  [issues 375-378 carrier draft](../charness-artifacts/hotl/2026-06-16-issues-375-378-closeout-carrier-draft.md)
  validates with `issue_tool.py validate-closeout-draft` as `draft_verified` /
  `ready_to_publish`. It deliberately excludes #371.
- **#371 remains open by design.** The issue comments say the local repair is
  post-hoc mitigation only. Do not close #371 unless controlled proof shows
  invocation-end teardown of both the browser process tree and the matching
  `agent-browser-chrome-*` profile directory for normal completion,
  cancellation, provider failure, and timeout.
- Open issues (`gh`, 2026-06-16): #378, #377, #376, #375, #371.

## Next Session

- **First decision:** coordinate with any other active agent before remote
  mutation. If publishing is approved, use the validated #375-#378 carrier draft
  as a PR body or equivalent carrier, then run `issue_tool.py verify-closeout`
  after merge/publish with `--expect-state CLOSED`.
- Keep #371 separate from that carrier. Either obtain the controlled lifecycle
  proof named above or leave it with the `issue` disposition recorded in the
  HOTL packet.
- **Still deferred** (reopen triggers): **E2b** (chunker ingests recurring waste —
  needs real 0.45.0+ usage telemetry) and the **Coordination-Cues floor merge**
  (a floor *removal*, separately critiqued).
- Older deferrals: D28/D29 in [deferred decisions](./deferred-decisions.md); the
  [contract-effectiveness fixture](../evals/cautilus/contract-effectiveness.fixture.json)
  needs a log-backed request.

## Discuss

- Whether the local #375-#378 proof bundle should be published as one PR/merge
  carrier now, and who owns the #371 upstream lifecycle proof path.

## References

- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [quality latest](../charness-artifacts/quality/latest.md)
- [HOTL proof packet](../charness-artifacts/hotl/2026-06-16-open-issue-hotl-closeout-proof-packet.md)
- [issues 375-378 carrier draft](../charness-artifacts/hotl/2026-06-16-issues-375-378-closeout-carrier-draft.md)
