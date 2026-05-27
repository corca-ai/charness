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

- **v0.9.0 is published and verified**: `main` and tag `v0.9.0` are on GitHub;
  release state (including the `--no-verify` publish rationale) is in
  [release latest](../charness-artifacts/release/latest.md). Working tree clean
  on `main...origin/main`; `current_release.py` reports no version drift.
- **0.9.0 shipped the `achieve` skill publicly for the first time**, plus the
  #223 quality/achieve duplicate-test-pressure contract, find-skills/achieve
  test-regression fixes, and a `local-linux-aarch64-4cpu` runtime budget profile.
- **#225 is RESOLVED** (commit `7e757c39` on `main`, issue closed): the
  pre-push gate is deterministic again and honest pushes from this host no
  longer need `--no-verify` (verified: the push of `7e757c39` ran the real
  pre-push hook and passed 69/0). True root cause was NOT generic xdist
  flakiness — `run-quality.sh` placed the pytest basetemp *inside* the repo
  (temp-root fallback used bare `$HOME` instead of `$HOME/.cache`, and this
  host's repo is `$HOME/charness`), which broke external-worktree/outside-git/
  copytree fixtures; plus cautilus/coverage tests hard-failed on absent optional
  capabilities instead of skipping. Fix added a guard that hard-fails if the
  temp root ever resolves inside the repo. See
  [debug artifact](../charness-artifacts/debug/2026-05-27-issue-225-prepush-nondeterminism.md).
- **#224 and #219 are scheduled mutation-test regression issues** (the recurring
  bot-filed class, successor to the old #216/#208). Treat as the mutation
  backlog, not new bugs.
- **#184/#185 remain deferred product/AI-ML direction work** (ideation/metrics
  backlog, not urgent maintenance).

## Next Session

1. **Mutation backlog (#224/#219)** is now the top self-fixable work. Classify
   before mutating; scheduled mutation can be red even when reachable score
   clears threshold if sampled scope gaps remain — score alone is not closeout.
2. **#184/#185** remain deferred product/AI-ML direction work (ideation/metrics
   backlog, not urgent maintenance).
3. Optional follow-up from #225: `verify-closeout` for `direct-commit` only
   inspects the commit body, so the bug ledger lives in the #225 close
   *comment* (all fields present, state CLOSED) rather than the commit body —
   no action needed, just know the tool reports `missing_fields` for this carrier.

## Discuss

- Pre-push gate determinism is restored (#225 resolved); honest pushes from this
  host no longer need `--no-verify`. Watch for a regressed temp-root: the new
  `run-quality.sh` guard now hard-fails loudly if the basetemp lands in the repo.
- Current PR CI posture is intentional maintainer-local enforcement per
  [operating contract](./conventions/operating-contract.md); do not reopen unless
  outside PRs become recurring.
- Watch: Yarn Berry hooks; pnpm+lefthook stale snippets; `filelock`+`pytest-xdist`;
  seed-cache LRU eviction; release proof suppression.

## References

- [quality posture](../charness-artifacts/quality/latest.md), [debug artifact](../charness-artifacts/debug/latest.md), [release surface](../charness-artifacts/release/latest.md)
