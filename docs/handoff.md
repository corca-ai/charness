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

- Current shipped release is `v0.7.10`; local `main` is 11 commits ahead of
  origin pending push.
- Usage-episodes adapter is now `enabled: true` with
  `host_hooks: {claude: enabled, codex: enabled}` and the SessionStart hook
  is installed in `~/.claude/settings.json` plus `~/.codex/config.toml`. Slice
  closeout emission has already landed at least one
  `slice-closeout-*` record in `.charness/usage-episodes/usage_episode.jsonl`;
  a SessionStart-driven record carrying `session_id` is expected on the next
  Claude/Codex session. The flip critique
  ([2026-05-22-usage-episodes-adapter-flip.md](../charness-artifacts/critique/2026-05-22-usage-episodes-adapter-flip.md))
  triaged all surfaced concerns to over-worry, existing D21/D22, four new
  deferred decisions (D23–D26), and one GH issue for the test isolation leak.

## Next Session

1. Monitor `.charness/usage-episodes/usage_episode.jsonl` for the first
   SessionStart-driven record with `session_id` and `t_evidence` populated;
   that record (combined with any closeout episode it pairs with) satisfies
   SC5/SC6 against a real charness commit.
2. After SC5/SC6 evidence lands, push the staged commits to `origin/main`
   (currently 11 ahead) so the dogfood adapter state and the new deferred
   decisions are visible to the next checkout.
3. Reopen-trigger watchlist after enable: D21 (orphan hook after checkout
   move), D22 (depth cap on hook script repo-root walk), D23 (Codex TOML
   block dedup + boundary), D24 (closeout emitter best-effort), D25 (per-host
   install exit code), D26 (hook command interpreter). Issue #194 tracks the
   test isolation leak in
   [tests/test_usage_episodes_host_hooks.py](../tests/test_usage_episodes_host_hooks.py)
   and is the most likely first hit once the next test run rewrites
   `host-hooks-state.json`.

## Discuss

- Step-env leakage into nested test-command coverage probes: subprocess tests
  building `env={**os.environ, ...}` must scrub `MUTATION_*` keys first.
- Watch list: Yarn Berry hooks; pnpm+lefthook stale snippets; `filelock` +
  `pytest-xdist`; seed-cache LRU eviction; release proof suppression.
- Usage-episodes Slice A non-blockers (reopen when reporting consumes
  episode data): `classification_skipped` required-when-classifier-invoked
  not enforceable in schema; `issue-closed` uses `<commit-message>` sentinel;
  `emit_failed` reports only the exception class name. Privacy block on the
  adapter is advisory until a non-gitignored upload pipeline appears.

## References

- [usage-episodes H-LAM/T completion spec](../charness-artifacts/spec/usage-episodes-h-lam-t-completion.md):
  fixed decisions and two-slice implementation plan.
- [codex hooks surface](../charness-artifacts/gather/2026-05-22-codex-hooks-surface.md):
  Codex SessionStart/Stop/UserPromptSubmit/PreToolUse/PostToolUse hook surface.
- [bug-pattern sibling scan](../charness-artifacts/debug/2026-05-21-bug-pattern-sibling-scan.md):
  current-pointer and gitignore sibling scan RCA and prevention.
- [quality posture](../charness-artifacts/quality/latest.md) and
  [release surface](../charness-artifacts/release/latest.md): current state pointers.
