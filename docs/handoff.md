# charness Handoff

## Workflow Trigger

- Start every task-oriented pickup with `charness:find-skills`, then read this
  file, [quality latest](../charness-artifacts/quality/latest.md), and
  [recent lessons](../charness-artifacts/retro/recent-lessons.md).
- Refresh live state: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, and `gh issue list --state open --limit 50`.
- Before mutating code, generated exports, or validation behavior, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).
- Route external URLs through `gather`.

## Current State

- **v0.7.15 is published and verified**: `main` and tag `v0.7.15` are on
  GitHub; release state and #218 closeout are recorded in
  [release latest](../charness-artifacts/release/latest.md).
- **Working tree is clean on `main...origin/main`**. `current_release.py`
  reports no version drift across packaging and generated install surfaces.
- **#216 is the active self-fixable issue**:
  [Mutation test regression on main](https://github.com/corca-ai/charness/issues/216)
  remains open with repeated scheduled mutation-test comments.
- **#184/#185 remain deferred product/AI-ML direction work**. Treat them as
  intentional ideation/metrics backlog, not urgent maintenance bugs.

## Next Session

1. Review #216 from GitHub source of truth, then classify before mutating. It
   currently looks bug-class because scheduled mutation testing is red on
   `main` despite normal release gates passing.
2. For #216, inspect the latest issue comment first. The newest signal on
   `6a0ebee...` reports reachable score above threshold but still fails on a
   remaining sampled scope gap; older comments show lower scores and broader
   survivor clusters.
3. If resolving #216, follow `issue` workflow: causal review first, then a
   smallest complete fix, mutation-focused verification, resolution critique,
   commit, push, release/closeout verification.
4. RCA ledger baseline observation remains deferred: let live non-seed events
   accrue from `debug`/`issue`/`retro` closeouts, then revisit with
   `python3 scripts/aggregate_rca_ledger.py`.

## Discuss

- Changed-line and changed-path gates verified before commit are blind to the
  fix's own uncommitted files. Commit-then-verify is required for final mutation
  sample evidence.
- Scheduled mutation issues can fail even when the reachable score is above
  threshold if sampled scope gaps remain. Do not treat score alone as closeout.
- Current PR CI posture is intentional maintainer-local enforcement per
  [operating contract](./conventions/operating-contract.md); do not reopen unless outside PRs
  become recurring.
- Watch: Yarn Berry hooks; pnpm+lefthook stale snippets; `filelock`+`pytest-xdist`;
  seed-cache LRU eviction; release proof suppression; D21-D26 reopen watchlist.

## References

- [quality posture](../charness-artifacts/quality/latest.md), [debug artifact](../charness-artifacts/debug/latest.md), [release surface](../charness-artifacts/release/latest.md)
