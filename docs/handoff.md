# charness Handoff

## Workflow Trigger

- Start every task-oriented pickup with `charness:find-skills`, then read this file, [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md), and [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md).
- Refresh live state before acting: `git status --short --branch`, `git log --oneline origin/main..HEAD`, and `gh issue list --state open --limit 50 --json number,title,labels,createdAt,url`.
- Before mutating code, scripts, docs, skills, generated exports, or validation behavior, read [docs/conventions/implementation-discipline.md](./conventions/implementation-discipline.md). Before closeout, read [docs/conventions/operating-contract.md](./conventions/operating-contract.md).
- Route external URLs or source links that should become repo working context through `gather` before using them as durable input.

## Current State

- `main` pushed to `origin/main` at `9e0ac1c` closing #180/#181/#182 via commit body; #183 fix landed and will auto-close on the next successful or PASS-partial mutation workflow run (`gh run view 26134097162` to track the dispatched run).
- Public release is `v0.7.6` with no open real-host gap; [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md) marks Real-Host Verification as "no configured trigger matched."
- Latest worktree-adapter seed now auto-detects pnpm/yarn/bun/npm and lefthook/husky/simple-git-hooks/repo-owned hook systems; `setup` inspector also surfaces the seam when `git worktree list` reports >1 worktree even without a Node hook manager.
- Mutation workflow now captures partial dumps via internal `--exec-timeout-seconds` (default 9000) and reports `PASS-partial` / `FAIL-incomplete` against a 75% executed floor; previous 3-hour cancel was the structural cause of #183.

## Next Session

1. **Verify** the dispatched mutation workflow (`gh run view 26134097162` or the latest scheduled run) actually finishes within 150min and writes `reports/mutation/cosmic-ray-dump.jsonl`; if the partial-run ratio is consistently under 75%, lower `mutation_testing.max_files` in [.agents/quality-adapter.yaml](../.agents/quality-adapter.yaml) from 10 to a measured value or enable cosmic-ray local-distributor concurrency.
2. **Passive** doc refresh — [docs/worktree-prepare.md](./worktree-prepare.md) and [skills/public/setup/references/bootstrap-seams.md](../skills/public/setup/references/bootstrap-seams.md) still describe the worktree adapter seed as a lefthook-centric template; update to mention auto-detection plus the active-worktrees trigger. Non-blocking; can ride the next release.
3. **Passive — seed-cache LRU eviction**. `~/.cache/charness/test-seeds/<hash>/` grows unboundedly across HEAD changes. When the cache becomes operationally noticeable, add an LRU helper that keeps N most-recent hashes by mtime; until then the cache is easy to clean manually.

## Discuss

- The plugin import-smoke gate (`check-plugin-import-smoke`) caught a real export defect introduced by the seed refactor: a bare `from seed_worktree_adapter_lib import ...` works when the script is executed but not when the gate loads modules via `spec_from_file_location` against the exported plugin tree. Resolved by explicitly inserting the script's directory onto `sys.path` at the top of `seed_worktree_adapter.py`. Worth confirming `check_export_safe_imports.py` covers this static shape too — currently only the runtime smoke catches it.

## References

- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)
- [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md)
- [charness-artifacts/debug/latest.md](../charness-artifacts/debug/latest.md)
