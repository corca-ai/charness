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

- **Operator Decision Queue shipped as v0.52.0.** Release `v0.52.0` was
  published at <https://github.com/corca-ai/charness/releases/tag/v0.52.0>.
  `origin/main` includes the release commit and post-publish verification
  commit. The release helper verified the public release surface, ran the
  declared fresh-checkout probes, and auto-refreshed the maintainer install from
  `0.51.1` to `0.52.0`.
- **#381 is closed.** Commit `1424c261` added the Operator Decision Queue
  closeout surface for fresh achieve/HOTL/handoff work; release `v0.52.0`
  carries the operator update instructions.
- **#371 remains open by design.** The issue comments say the local repair is
  post-hoc mitigation only. Do not close #371 unless controlled proof shows
  invocation-end teardown of both the browser process tree and the matching
  `agent-browser-chrome-*` profile directory for normal completion,
  cancellation, provider failure, and timeout.
- Open issues (`gh`, 2026-06-17): #371.

## Next Session

- First decision: either obtain controlled #371 lifecycle proof or keep #371 as
  an explicit upstream/tool-lifecycle split.
- Restart active Codex/Claude sessions if they need the freshly installed
  Charness v0.52.0 plugin cache; the release helper reported cache-path
  rotation from `local/charness 0.51.1 -> 0.52.0`.
- **Still deferred** (reopen triggers): **E2b** (chunker ingests recurring waste —
  needs real 0.45.0+ usage telemetry) and the **Coordination-Cues floor merge**
  (a floor *removal*, separately critiqued).
- Older deferrals: D28/D29 in [deferred decisions](./deferred-decisions.md); the
  [contract-effectiveness fixture](../evals/cautilus/contract-effectiveness.fixture.json)
  needs a log-backed request.

## Discuss

- Who owns the #371 upstream lifecycle proof path.

## References

- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [quality latest](../charness-artifacts/quality/latest.md)
- [release latest](../charness-artifacts/release/latest.md)
- [HOTL proof packet](../charness-artifacts/hotl/2026-06-16-open-issue-hotl-closeout-proof-packet.md)
- [issues 375-378 carrier draft](../charness-artifacts/hotl/2026-06-16-issues-375-378-closeout-carrier-draft.md)
