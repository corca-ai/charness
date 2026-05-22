# charness Handoff

## Workflow Trigger

- Start every task-oriented pickup with `charness:find-skills`, then read this file,
  [quality latest](../charness-artifacts/quality/latest.md), and recent-lessons.md.
- Refresh live state before acting: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, and `gh issue list --state open --limit 50`.
- Before mutating code, generated exports, or validation behavior, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).
- Route external URLs or source links that should become repo working context through `gather`.

## Current State

- Current shipped release is `v0.7.10`; local `main` is 10 commits ahead of
  origin pending push.
- Usage-episodes adapter remains `enabled: false` and `host_hooks` commented
  out. Slice B of the
  [H-LAM/T completion spec](../charness-artifacts/spec/usage-episodes-h-lam-t-completion.md)
  landed: SessionStart hook, host-hook install lib, reconcile runner, init/
  update reconcile, and `charness session-capture status/install/uninstall`.
  Codex precedence was resolved via the refreshed
  [codex hooks gather](../charness-artifacts/gather/2026-05-22-codex-hooks-surface.md):
  default install is `~/.codex/config.toml`, with fallback to `hooks.json`
  when that file already carries entries. Critique follow-ups (SC2 wording,
  structured reconcile errors, installed_at only on real install, CLI
  round-trip test) landed inline; remainder is recorded as D20/D21/D22 in
  [deferred-decisions](./deferred-decisions.md).

## Next Session

1. Flip [usage-episodes adapter](../.agents/usage-episodes-adapter.yaml)
   `enabled: true` (and optionally set `host_hooks.{claude,codex}: enabled`
   for dogfood) as a separate intentional commit. Before flipping, run
   `python3 charness session-capture status` to confirm a clean baseline and
   capture the resulting reconcile payload so the first session-grouped
   episode lands deliberately.
2. After enable, monitor `.charness/usage-episodes/usage_episode.jsonl` for
   at least one closeout episode with `session_id` and `t_evidence`
   populated; this satisfies SC5/SC6 against real charness commits.
3. Reopen-trigger watchlist: D21 (orphan hook after checkout move) and D22
   (depth cap on hook script repo-root walk) are the most likely first hits
   once a maintainer adopts the hook on a real machine.

## Discuss

- Static `check-current-pointer-writes` scanner only catches string-literal
  writes; future adapter-resolved writers must adopt the helper until D19's
  reopen trigger fires.
- Step-env leakage into nested test-command coverage probes: subprocess tests
  building `env={**os.environ, ...}` must scrub `MUTATION_*` keys first.
- Watch list: Yarn Berry hooks; pnpm+lefthook stale snippets; `filelock` +
  `pytest-xdist`; seed-cache LRU eviction; release proof suppression.
- Usage-episodes Slice A non-blockers (reopen when reporting consumes
  episode data): schema cannot enforce `classification_skipped`
  required-when-classifier-invoked; `issue-closed` uses `<commit-message>`
  as a matched_paths sentinel; emitter's `emit_failed` reports only the
  exception class name.

## References

- [usage-episodes H-LAM/T completion spec](../charness-artifacts/spec/usage-episodes-h-lam-t-completion.md):
  fixed decisions and two-slice implementation plan.
- [codex hooks surface](../charness-artifacts/gather/2026-05-22-codex-hooks-surface.md):
  Codex SessionStart/Stop/UserPromptSubmit/PreToolUse/PostToolUse hook surface.
- [bug-pattern sibling scan](../charness-artifacts/debug/2026-05-21-bug-pattern-sibling-scan.md):
  current-pointer and gitignore sibling scan RCA and prevention.
- [quality posture](../charness-artifacts/quality/latest.md) and
  [release surface](../charness-artifacts/release/latest.md): current state pointers.
