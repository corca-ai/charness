# charness Handoff

## Workflow Trigger

- Start every task-oriented pickup with `charness:find-skills`, then read this file, [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md), and [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md).
- Refresh live state before acting: `git status --short --branch`, `git log --oneline origin/main..HEAD`, and `gh issue list --state open --limit 50 --json number,title,labels,createdAt,url`.
- Before mutating code, scripts, docs, skills, generated exports, or validation behavior, read [docs/conventions/implementation-discipline.md](./conventions/implementation-discipline.md). Before closeout, read [docs/conventions/operating-contract.md](./conventions/operating-contract.md).
- Route external URLs or source links that should become repo working context through `gather` before using them as durable input.

## Current State

- `main` is ahead of `origin/main` by recent quality-track commits; this turn landed the two previous active+passive next gates (orphan teardown + content-addressed seed cache) plus the underlying `--help`→`--version` runtime-guard fix.
- Public release is `v0.7.6` with no open real-host gap; [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md) marks Real-Host Verification as "no configured trigger matched."
- Latest quality posture: [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md) — [scripts/run-quality.sh](../scripts/run-quality.sh) now reliably finishes 64/0 twice in succession without manual orphan cleanup; seed fan-out collapsed from 54 materializations to one per `(HEAD, dirty-digest)` via [tests/seed_cache.py](../tests/seed_cache.py); xdist workers share one seed through `filelock`.

## Next Session

1. **Passive** (background queue): downstream-repo dogfood on the stronger generated skill-ergonomics default before changing the rule set again. No code action this turn; collect issues from consuming repos first.
2. **Passive — seed-cache LRU eviction**. `~/.cache/charness/test-seeds/<hash>/` grows unboundedly across HEAD changes (one directory per `(HEAD, dirty-digest)`). When the cache becomes operationally noticeable, add an LRU helper that keeps N most-recent hashes by mtime; until then the cache is easy to clean manually. See `Weak` in [latest.md](../charness-artifacts/quality/latest.md).

## Discuss

- Confirmed empirically: the agent-browser orphan race was caused by `agent_browser_runtime_guard.py --doctor-check` running `agent-browser --help`, which warms a background daemon as a side effect. `--version` is a sufficient binary-functionality check that does not spawn a daemon, so we switched and removed the orphan source at its root. The `pytest_sessionfinish` cleanup hook in [tests/conftest.py](../tests/conftest.py) stays as a controller-side backstop.

## References

- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)
- [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md)
- [charness-artifacts/debug/latest.md](../charness-artifacts/debug/latest.md)
