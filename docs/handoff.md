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

- **Design north star landed + #386 shipped as v0.52.4.** Release `v0.52.4` is
  published and verified at
  <https://github.com/corca-ai/charness/releases/tag/v0.52.4>;
  [`docs/design-north-star.md`](./design-north-star.md) is now the governing
  design standard (referenced from `AGENTS.md`). #386 (non-terminal issue-bundle
  closeout) is verified CLOSED — fixed by a Rung-2 distinct-observer/
  distinct-channel disposition-review mandate (achieve `lifecycle.md`, hotl
  `ledger-and-dispositions.md`), **no new gate**. Maintainer install auto-refreshed
  `0.52.3 -> 0.52.4`.
- **The overhaul is the main next work.** Plan of record:
  [`docs/north-star-overhaul-roadmap.md`](./north-star-overhaul-roadmap.md) —
  realign the harness to the north star (consolidate the terminal-green
  recurrence-cluster gates into non-terminal per-unit-disposition; separate
  concepts to stop prose/gate sprawl). Execution was deliberately deferred to a
  post-compaction session.
- **#371 remains open by design.** Local repair is post-hoc mitigation only; do
  not close without controlled invocation-end teardown proof (process tree +
  `agent-browser-chrome-*` profile dir) for completion, cancellation, provider
  failure, and timeout.
- Open issues (`gh`, 2026-06-18): #387 (overhaul Phase-1 pilot), #388
  (mutation-test regression — separate CI-hygiene track), #371.

## Next Session

- **Primary: pursue the north-star overhaul roadmap.** Start at Phase 0 (validate
  the diagnosis / back-test the recurrence cluster), then Phase 1 = resolve #387
  (one-pass goal-closeout shape errors) as the cheap evidenced pilot. Honor the
  roadmap's per-surface migration discipline (replacement-before-deletion).
- Operator decisions before Phase 2 (in the roadmap): shape the overhaul as one
  `achieve` goal vs. independent issues; Phase-3 deletion aggressiveness.
- #388 (mutation-test regression) and #371 stay on their own tracks; do not
  couple them to the overhaul.
- Restart active Codex/Claude sessions if they need the freshly installed
  v0.52.4 plugin cache (release helper reported cache-path rotation).
- Older deferrals: D28/D29 in [deferred decisions](./deferred-decisions.md).

## Discuss

- Who owns the #371 upstream lifecycle proof path.

## References

- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [quality latest](../charness-artifacts/quality/latest.md)
- [release latest](../charness-artifacts/release/latest.md)
- [HOTL proof packet](../charness-artifacts/hotl/2026-06-16-open-issue-hotl-closeout-proof-packet.md)
- [issues 375-378 carrier draft](../charness-artifacts/hotl/2026-06-16-issues-375-378-closeout-carrier-draft.md)
