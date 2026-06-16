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

- **Open-issue HOTL bundle shipped as v0.51.0.** Release `v0.51.0` was published
  at <https://github.com/corca-ai/charness/releases/tag/v0.51.0>. `origin/main`
  includes the release commit and post-publish issue closeout artifact commit.
- **#375-#378 are closed.** The release helper closed #375, #376, #377, and
  #378 through the direct release commit body carrier and verified GitHub
  `CLOSED` readback. The proof is recorded in
  [HOTL packet](../charness-artifacts/hotl/2026-06-16-open-issue-hotl-closeout-proof-packet.md).
- **The PR-body carrier draft is historical provenance.** The checked-in draft at
  [issues 375-378 carrier draft](../charness-artifacts/hotl/2026-06-16-issues-375-378-closeout-carrier-draft.md)
  validated before publish, but final closeout used the release helper's direct
  release commit body carrier.
- **#371 remains open by design.** The issue comments say the local repair is
  post-hoc mitigation only. Do not close #371 unless controlled proof shows
  invocation-end teardown of both the browser process tree and the matching
  `agent-browser-chrome-*` profile directory for normal completion,
  cancellation, provider failure, and timeout.
- Open issues (`gh`, 2026-06-16): #371.

## Next Session

- First decision: either obtain controlled #371 lifecycle proof or keep #371 as
  the explicit `issue` disposition recorded in the HOTL packet.
- Restart active Codex/Claude sessions if they need the freshly installed
  Charness v0.51.0 plugin cache.
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
- [HOTL proof packet](../charness-artifacts/hotl/2026-06-16-open-issue-hotl-closeout-proof-packet.md)
- [issues 375-378 carrier draft](../charness-artifacts/hotl/2026-06-16-issues-375-378-closeout-carrier-draft.md)
