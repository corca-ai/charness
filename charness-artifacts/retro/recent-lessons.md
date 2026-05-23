# Recent Retro Lessons

## Current Focus

- This session worked through the autonomous-processable items in `docs/handoff.md`: fixed issue #194 (test-isolation leak of `host-hooks-state.json` into the live repo from the two session-capture CLI tests), confirmed issue #191's mutation test regression was already fixed in the unpushed commit `eead33f`, landed issue #192 (argparse `help=` rule in `create-skill` portable authoring), and emitted SC5/SC6 evidence with `session_id` plus `t_evidence` against a real commit. (source: `charness-artifacts/retro/2026-05-23-handoff-bug-cleanup-session.md`)
- This session continued the bug-pattern sibling scan and repaired the release publish path that treated a failed unreleased-path diff as an empty release delta. (source: `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`)

## Repeat Traps

- Adding a trap directly to `charness-artifacts/retro/recent-lessons.md` by hand was reverted by `refresh_recent_lessons.py` on the next pre-push run; the digest is generated from the selection index, not authored. (source: `charness-artifacts/retro/2026-05-23-handoff-bug-cleanup-session.md`)
- The #192 commit message used `Add #192` instead of a closing keyword (`Fix`/`Closes`/`Resolves`), so GitHub did not auto-close the issue on push. The sibling #194 commit used `Fix #194` and auto-closed cleanly. Manual `gh issue close 192` recovered, but the cost of one stray PR or closeout review missing the keyword can be a stale OPEN issue for days. (source: `charness-artifacts/retro/2026-05-23-handoff-bug-cleanup-session.md`)
- The first draft of the #194 fix added a `CHARNESS_USAGE_EPISODES_STATE_PATH` env override to `host_hook_install_lib.py`. The override blocked the leak but exposed a second test bug: the tests also depended on the live `.agents/usage-episodes-adapter.yaml` for adapter intent. The cleaner rewrite (tmp fake repo with symlinked `packaging/scripts/`) handles both surfaces, so the env override was reverted before commit. Discarded code, but it took two iterations to see the second dependency. (source: `charness-artifacts/retro/2026-05-23-handoff-bug-cleanup-session.md`)
- Compatibility for no-trigger dry-run repos without `.agents/surfaces.json` was implied by execute tests but not directly pinned. (source: `charness-artifacts/retro/2026-05-22-release-real-host-config-session.md`)

## Next-Time Checklist

- keep release proof suppression split into fixed diff failure and deferred real-host payload/post-create/base-ref risks is stale after this session; current split is fixed diff, fixed real-host payload/config, fixed base-ref lookup/fetch, and deferred post-create recovery semantics. (source: `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`; sources: 2)
- do not edit `charness-artifacts/retro/recent-lessons.md` directly; write a session retro file and run `python3 skills/public/retro/scripts/refresh_recent_lessons.py --repo-root .` so the digest stays consistent with the selection index. (source: `charness-artifacts/retro/2026-05-23-handoff-bug-cleanup-session.md`)
- when a commit resolves a GitHub issue, the commit message subject line must use a GitHub closing keyword (`Fix`, `Fixes`, `Closes`, `Resolves`) so auto-close fires on push. `Add #NNN`, `Implement #NNN`, and `Document #NNN` do not auto-close; the `issue` skill already states this preference but the trap recurs on non-bug commits. (source: `charness-artifacts/retro/2026-05-23-handoff-bug-cleanup-session.md`)
- when a test passes `--repo-root str(REPO_ROOT)` to a subprocess that writes gitignored state, switch to a tmp fake repo with symlinked `packaging/` and `scripts/`. The `fake_charness_repo` fixture in `tests/test_usage_episodes_host_hooks.py` is the canonical pattern. (source: `charness-artifacts/retro/2026-05-23-handoff-bug-cleanup-session.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-22-release-base-ref-fallback-session.md`
- `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`
- `charness-artifacts/retro/2026-05-22-release-real-host-config-session.md`
- `charness-artifacts/retro/2026-05-23-handoff-bug-cleanup-session.md`
