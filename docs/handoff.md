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

- `main` is in sync with `origin/main` at commit `e057bfd`.
- Issue #193 (256 `add_argument` calls missing `help=`) resolved: 254 calls
  fixed across 87 hand-authored files in `skills/public/**/scripts/`; AST
  scanner reports `global remaining: 0`. The generated `plugins/charness/`
  install surface was re-synced via
  [scripts/sync_root_plugin_manifests.py](../scripts/sync_root_plugin_manifests.py)
  in the same commit.
- Issue #191 (mutation test regression) closed with reference to the already-
  pushed fix commit `eead33f` ("Scrub MUTATION_BASE_SHA leak into sampler probe test").
- Issues #194 and #192 were closed in the previous session.

## Next Session

1. The remaining open issues are ideation-shaped:
   [#185 AI/ML 엔지니어링 성공 패턴](https://github.com/corca-ai/charness/issues/185) and
   [#184 제품 성공 기준과 핵심 메트릭](https://github.com/corca-ai/charness/issues/184).
   These need product discovery, not autonomous repo work — route through
   `ideation` or `spec` before any implementation slice.
2. Reopen-trigger watchlist: D21–D26.
3. Optional follow-up to #193: a small `quality` validator that scans for
   `add_argument(...)` without `help=` so the gap does not silently reopen.
   Deferred as low priority — recent sweep proved the surface is small enough
   to spot-check during create-skill review per #192 rule.

## Discuss

- Subprocess tests passing `--repo-root str(REPO_ROOT)` to a CLI that writes
  gitignored state must use a tmp fake repo with symlinked `packaging/` and
  `scripts/`. See `fake_charness_repo` in
  [tests/test_usage_episodes_host_hooks.py](../tests/test_usage_episodes_host_hooks.py).
- After mutating `skills/public/` for any multi-file sweep, run
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .` before the
  read-only quality gate; otherwise drift surfaces as a failing
  `test_plugin_preamble_..._readiness`.
- When adding `help=` to an `add_argument` that already carries `choices=`,
  the help text must reflect the actual choice strings. Caught one such bug
  at `skills/public/issue/scripts/issue_tool.py:266` during the #193 sweep.
- Watch list: Yarn Berry hooks; pnpm+lefthook stale snippets; `filelock` +
  `pytest-xdist`; seed-cache LRU eviction; `MUTATION_*` env-scrub in subprocess
  tests; release proof suppression.

## References

- [usage-episodes H-LAM/T completion spec](../charness-artifacts/spec/usage-episodes-h-lam-t-completion.md):
  fixed decisions and two-slice implementation plan.
- [codex hooks surface](../charness-artifacts/gather/2026-05-22-codex-hooks-surface.md):
  Codex SessionStart/Stop/UserPromptSubmit/PreToolUse/PostToolUse hook surface.
- [bug-pattern sibling scan](../charness-artifacts/debug/2026-05-21-bug-pattern-sibling-scan.md):
  current-pointer and gitignore sibling scan RCA and prevention.
- [quality posture](../charness-artifacts/quality/latest.md) and
  [release surface](../charness-artifacts/release/latest.md): current state pointers.
- [#193 help= sweep retro](../charness-artifacts/retro/2026-05-23-help-text-sweep-session.md):
  parallel-subagent sweep, sync-after-mutate trap, misleading enum-in-help bug.
