# charness Handoff

## Workflow Trigger

- Start every task-oriented pickup with `charness:find-skills`, then read this file, [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md), and [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md).
- Refresh live state before acting: `git status --short --branch`, `git log --oneline origin/main..HEAD`, and `gh issue list --state open --limit 50 --json number,title,labels,createdAt,url`.
- Before mutating code, scripts, docs, skills, generated exports, or validation behavior, read [docs/conventions/implementation-discipline.md](./conventions/implementation-discipline.md). Before closeout, read [docs/conventions/operating-contract.md](./conventions/operating-contract.md).
- Route external URLs or source links that should become repo working context through `gather` before using them as durable input.

## Current State

- `main` is even with `origin/main` at `78d0023` (`Record release verification for v0.7.5`).
- Current public release is `v0.7.5`, published 2026-05-19. `gh release list --repo corca-ai/charness --limit 5` marks it Latest, and [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md) records the release proof.
- `v0.7.5` automated/public release verification is done. Installed-machine real-host proof remains open and unowned in this session; the required operator proof is listed in [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md).
- Observed live GitHub issue list is empty. [#171](https://github.com/corca-ai/charness/issues/171) is closed as completed, so it is no longer handoff pickup work.
- Latest quality state is [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md): [scripts/run-quality.sh](../scripts/run-quality.sh) passed on 2026-05-19 with 61 passed / 0 failed; Cautilus planner returned `next_action: none`.
- Current debug context is mutation-score validity, captured in [charness-artifacts/debug/latest.md](../charness-artifacts/debug/latest.md). Do not treat older mutation, Cautilus rename, or issue closeout details as active handoff work unless a fresh live signal points back to them.

## Next Session

1. For any release-status or release-closeout pickup, start with the open `v0.7.5` real-host verification sequence in [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md) on a second machine or clean temp home, then record the proof before claiming `v0.7.5` fully closed.
2. For issue-resolution work, the observed live GitHub issue queue is empty; ask the user for the next target instead of reviving closed #171/#172/#170/#174 threads from history.
3. Treat raw response persistence and maintained Cautilus scenario-registry mutation as prior deferred topics, out of scope unless the user explicitly asks to reopen them.

## Discuss

- Whether to spend the next session on `v0.7.5` real-host verification or leave it as release-follow-up while starting a new user-selected target.

## References

- [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md)
- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)
- [charness-artifacts/debug/latest.md](../charness-artifacts/debug/latest.md)
