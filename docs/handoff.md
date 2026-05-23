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

- `main` synced with `origin/main` at `5c5f15c` (retro+handoff); #193 sweep
  landed in `e057bfd` — 254 `add_argument` calls in 87 source files received
  `help=`, AST `remaining: 0`, plugin install surface re-synced.
- Critic-flagged sweep follow-ups (corpus is ship-quality, not perfect):
  18× `"Repository root path"`, 6× `"Emit JSON output"`, 7 missing-`help=`
  subparsers in `skills/public/issue/scripts/issue_tool.py:233-278`,
  `"Repo"` vs `"Repository"` vocab split across the subagent boundary.
- **#195 OPEN** (mutation cron, 80.5% vs 80% threshold against `e057bfd`).
  Bounded review: UNRELATED to the sweep — survivors are `if __name__ == "__main__":`
  in `init_adapter.py` shims (zero diff in sweep). Sweep starved the
  changed-file sampler; Fill drew from pre-existing weak coverage.
- **#191 closed with wrong commit ref**: cited `eead33f` actually fixes #190
  (Python probe leak); #191's body was StrykerJS. De-facto fix landed
  elsewhere (StrykerJS run 26323487405 PASS at 91.9%). Correcting comment owed.
- #194, #192, #193 closed cleanly.

## Next Session

1. **Triage #195**: skip-mark `__name__ == "__main__":` / `sys.path.insert(...)`
   in adapter shims, or raise the per-file mutant skip for trivial entry
   guards. The help= sweep is NOT the cause.
2. **Correcting comment on #191**: point at workflow run 26323487405
   (StrykerJS PASS 91.9%) so the audit trail does not anchor on `eead33f`.
3. **Optional #193 cleanup**: 18× generic `"Repository root path"`, 6×
   `"Emit JSON output"`, `issue_tool.py:233-278` subparser `help=`, and one
   of `"Repo"` / `"Repository"` corpus-wide.
4. **Ideation-shaped**:
   [#185 AI/ML 패턴](https://github.com/corca-ai/charness/issues/185),
   [#184 성공 기준/메트릭](https://github.com/corca-ai/charness/issues/184)
   route through `ideation` / `spec` first.

## Discuss

- After multi-file mutation under `skills/public/`, run
  [scripts/sync_root_plugin_manifests.py](../scripts/sync_root_plugin_manifests.py)
  before the quality gate; drift otherwise surfaces as a failing
  `test_plugin_preamble_..._readiness`.
- `add_argument` with `choices=` must have `help=` that reflects the actual
  choice strings; argparse auto-prints choices, so a paraphrase contradicts.
- Subprocess tests passing `--repo-root str(REPO_ROOT)` to a writing CLI
  must use the `fake_charness_repo` fixture in
  [tests/test_usage_episodes_host_hooks.py](../tests/test_usage_episodes_host_hooks.py);
  scrub `MUTATION_*` env keys before forwarding `os.environ`.
- Watch: Yarn Berry hooks; pnpm+lefthook stale snippets; `filelock` +
  `pytest-xdist`; seed-cache LRU eviction; release proof suppression;
  D21–D26 reopen-trigger watchlist.

## References

- [#193 help= sweep retro](../charness-artifacts/retro/2026-05-23-help-text-sweep-session.md)
- [quality posture](../charness-artifacts/quality/latest.md),
  [release surface](../charness-artifacts/release/latest.md)
- [usage-episodes spec](../charness-artifacts/spec/usage-episodes-h-lam-t-completion.md),
  [codex hooks surface](../charness-artifacts/gather/2026-05-22-codex-hooks-surface.md),
  [bug-pattern sibling scan](../charness-artifacts/debug/2026-05-21-bug-pattern-sibling-scan.md)
