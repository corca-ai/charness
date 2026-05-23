# charness Handoff

## Workflow Trigger

- Start every task-oriented pickup with `charness:find-skills`, then read this file,
  [quality latest](../charness-artifacts/quality/latest.md), and recent-lessons.md.
- Refresh live state: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, and `gh issue list --state open --limit 50`.
- Before mutating code, generated exports, or validation behavior, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).
- Route external URLs through `gather`.

## Current State

- `main` synced at `5c5f15c` (retro+handoff); #193 sweep landed in `e057bfd`
  — 254 `add_argument` calls in 87 source files received `help=`, AST scan
  `remaining: 0`, plugin install surface re-synced.
- #194, #192, #193 closed cleanly. Correcting + nuance comments posted on
  #191 (already closed; comments named the actual StrykerJS workflow run
  and the Python slice that survives in #195).
- Open follow-ups filed: **#196** (#193 corpus cleanup), **#197**
  (post-mutation sync gate to close the mutate→sync→verify barrier).
- **#195 OPEN** (Python mutation slice, 80.5% vs 80% threshold against
  `e057bfd`). Bounded review concluded UNRELATED to the sweep — survivors
  are `if __name__ == "__main__":` in `init_adapter.py` shims (zero diff in
  the sweep). The sweep starved the changed-file sampler so Fill drew from
  pre-existing weak coverage.

## Next Session

1. **Triage #195**: skip-mark `__name__ == "__main__":` / `sys.path.insert(...)`
   in adapter shims or raise the per-file mutant skip for trivial entry
   guards. The help= sweep is NOT the cause.
2. **Implement #197 sync gate** wired into `run-quality.sh --read-only` so
   the mutate→sync→verify barrier fails closed at the gate, not via
   `test_plugin_preamble_..._readiness`. The issue body lists false-positive
   hazards (SKILL.md vs scripts; staged vs committed scope).
3. **Run #196 sweep cleanup** — bounded session: 18 generic Repository-root
   strings, 6 generic Emit-JSON strings, 7 subparser help= in
   `issue_tool.py:233-278`, and one of Repo/Repository corpus-wide.
4. **Ideation-shaped, deferred**:
   [#185 AI/ML 패턴](https://github.com/corca-ai/charness/issues/185),
   [#184 성공 기준/메트릭](https://github.com/corca-ai/charness/issues/184)
   route through `ideation` / `spec` first.

## Discuss

- After multi-file mutation under `skills/public/`, run
  [scripts/sync_root_plugin_manifests.py](../scripts/sync_root_plugin_manifests.py)
  before the quality gate; otherwise drift only surfaces via failing
  `test_plugin_preamble_..._readiness`. #197 will mechanize this.
- `add_argument` with `choices=` must have `help=` reflecting the actual
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
  [bug-pattern sibling scan](../charness-artifacts/debug/2026-05-21-bug-pattern-sibling-scan.md)
