# charness Handoff

## Workflow Trigger

- Start every task-oriented pickup with `charness:find-skills`, then read this file, [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md), and [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md).
- Refresh live state before acting: `git status --short --branch`, `git log --oneline origin/main..HEAD`, and `gh issue list --state open --limit 50 --json number,title,labels,createdAt,url`.
- Before mutating code, scripts, docs, skills, generated exports, or validation behavior, read [docs/conventions/implementation-discipline.md](./conventions/implementation-discipline.md). Before closeout, read [docs/conventions/operating-contract.md](./conventions/operating-contract.md).
- Route external URLs or source links that should become repo working context through `gather` before using them as durable input.

## Current State

- `main` is at `3e5e77c` (`Land remaining next gates: depth-bounded du + release contract doc + audit`); ahead of `origin/main` by recent quality-track commits.
- Public release is `v0.7.6` with no open real-host gap; [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md) marks Real-Host Verification as "no configured trigger matched."
- Latest quality posture: [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md) — standing pytest dropped from ~80s to ~22s after routing `release_only` correctly; `check-seed-fixture-budget` runtime collapsed to ~0.1s after depth-bounded `du`; agent-browser orphan flakiness is the next gate to install.

## Next Session

1. **Active gate** (smallest meaningful move): add a session-scoped autouse teardown in [tests/conftest.py](../tests/conftest.py) that calls [scripts/agent_browser_runtime_guard.py](../scripts/agent_browser_runtime_guard.py) with `--cleanup-orphans --execute` at pytest session end. Verify by running [scripts/run-quality.sh](../scripts/run-quality.sh) twice in succession — both must finish 64+/0 without manual orphan cleanup between runs. This unblocks the intermittent `check-cli-skill-surface`/`check-coverage` failures recorded in `Weak` of [latest.md](../charness-artifacts/quality/latest.md).
2. **Passive** (only if user asks for cost reduction): introduce content-addressed seed cache at `~/.cache/charness/test-seeds/<repo-hash>/` for `seeded_charness_repo`, `seeded_charness_git_repo`, and `seeded_managed_home`. Same-HEAD reruns should pay zero copy cost. Key: `git rev-parse HEAD` + dirty file digest; locking via `filelock` for xdist worker concurrency.
3. **Passive** (background queue): downstream-repo dogfood on the stronger generated skill-ergonomics default before changing the rule set again. No code action this turn; collect issues from consuming repos first.

## Discuss

- The agent-browser orphan race appears to be caused partly by `agent_browser_runtime_guard.py --doctor-check` itself spawning daemons during healthcheck. Confirm whether the autouse teardown is sufficient or whether the guard should be split into a "passive observe" path that does not start a daemon.

## References

- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)
- [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md)
- [charness-artifacts/debug/latest.md](../charness-artifacts/debug/latest.md)
