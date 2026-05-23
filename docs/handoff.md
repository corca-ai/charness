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

- Shipped release `v0.7.10`; local `main` is 14 commits ahead of origin.
- Usage-episodes adapter is `enabled: true` with both host hooks installed.
  SC5/SC6 is satisfied: this session's closeout emitted records with
  `session_id` and `t_evidence` against commit `bc5899b` in
  [.charness/usage-episodes/usage_episode.jsonl](../.charness/usage-episodes/usage_episode.jsonl)
  (gitignored).
- Issue #194 (test-isolation leak) resolved in commit `02c34b5`; the two
  CLI tests now use a `fake_charness_repo` fixture with a regression guard
  over [tests/test_usage_episodes_host_hooks.py](../tests/test_usage_episodes_host_hooks.py).
- Issue #192 (argparse help rule) landed in commit `bc5899b` in
  [portable-authoring.md](../skills/public/create-skill/references/portable-authoring.md).

## Next Session

1. Push 14 commits to `origin/main` so the dogfood adapter state, #194 fix,
   and #192 rule become visible. Push also gives the mutation cron a new
   HEAD so the #191 same-SHA failure trail stops (already fixed locally in
   `eead33f`).
2. After push, close #194 and #192 on GitHub referencing landing commits.
3. Optional: tackle #193 sweep (259 add_argument calls missing `help=`
   across ~131 files). Lowest-risk-first per-skill split documented in the
   issue body; quality(96) and release(30) are the heaviest.
4. Reopen-trigger watchlist: D21–D26.

## Discuss

- Subprocess tests passing `--repo-root str(REPO_ROOT)` to a CLI that writes
  gitignored state must use a tmp fake repo with symlinked `packaging/` and
  `scripts/`. See `fake_charness_repo` in
  [tests/test_usage_episodes_host_hooks.py](../tests/test_usage_episodes_host_hooks.py).
- Step-env leakage: subprocess tests building `env={**os.environ, ...}` must
  scrub `MUTATION_*` keys first.
- Watch list: Yarn Berry hooks; pnpm+lefthook stale snippets; `filelock` +
  `pytest-xdist`; seed-cache LRU eviction; release proof suppression.

## References

- [usage-episodes H-LAM/T completion spec](../charness-artifacts/spec/usage-episodes-h-lam-t-completion.md):
  fixed decisions and two-slice implementation plan.
- [codex hooks surface](../charness-artifacts/gather/2026-05-22-codex-hooks-surface.md):
  Codex SessionStart/Stop/UserPromptSubmit/PreToolUse/PostToolUse hook surface.
- [bug-pattern sibling scan](../charness-artifacts/debug/2026-05-21-bug-pattern-sibling-scan.md):
  current-pointer and gitignore sibling scan RCA and prevention.
- [quality posture](../charness-artifacts/quality/latest.md) and
  [release surface](../charness-artifacts/release/latest.md): current state pointers.
