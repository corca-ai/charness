# Recent Retro Lessons

## Current Focus

- Closed the handoff's self-fixable open issues (#198, #202-#206) and RCA'd #207 (by-design) through the design→impl→pattern-scan→RCA→final-critique loop with five bounded fresh-eye subagent passes. (source: `charness-artifacts/retro/2026-05-23-handoff-open-issue-sweep.md`)
- This session worked through the autonomous-processable items in `docs/handoff.md`: fixed issue #194 (test-isolation leak of `host-hooks-state.json` into the live repo from the two session-capture CLI tests), confirmed issue #191's mutation test regression was already fixed in the unpushed commit `eead33f`, landed issue #192 (argparse `help=` rule in `create-skill` portable authoring), and emitted SC5/SC6 evidence with `session_id` plus `t_evidence` against a real commit. (source: `charness-artifacts/retro/2026-05-23-handoff-bug-cleanup-session.md`)

## Repeat Traps

- Adding a trap directly to `charness-artifacts/retro/recent-lessons.md` by hand was reverted by `refresh_recent_lessons.py` on the next pre-push run; the digest is generated from the selection index, not authored. (source: `charness-artifacts/retro/2026-05-23-handoff-bug-cleanup-session.md`)
- The #192 commit message used `Add #192` instead of a closing keyword (`Fix`/`Closes`/`Resolves`), so GitHub did not auto-close the issue on push. The sibling #194 commit used `Fix #194` and auto-closed cleanly. Manual `gh issue close 192` recovered, but the cost of one stray PR or closeout review missing the keyword can be a stale OPEN issue for days. (source: `charness-artifacts/retro/2026-05-23-handoff-bug-cleanup-session.md`)
- The commit subject `Fixes #198 #202 #203 #204 #205 #206` auto-closed only **#198**. GitHub applies a closing keyword to the FIRST issue number only; a list of bare numbers after one keyword are mentions, not closing references. The result was 6 unpushed-then-pushed fixes that all stayed OPEN until a manual `gh issue close` sweep. The prior session's `a689024` (`Fixes #199 #200 #201`) had the same defect — #199 closed, #200/#201 did not — so this already recurred once and was not caught. (source: `charness-artifacts/retro/2026-05-23-handoff-open-issue-sweep.md`)
- The first draft of the #194 fix added a `CHARNESS_USAGE_EPISODES_STATE_PATH` env override to `host_hook_install_lib.py`. The override blocked the leak but exposed a second test bug: the tests also depended on the live `.agents/usage-episodes-adapter.yaml` for adapter intent. The cleaner rewrite (tmp fake repo with symlinked `packaging/scripts/`) handles both surfaces, so the env override was reverted before commit. Discarded code, but it took two iterations to see the second dependency. (source: `charness-artifacts/retro/2026-05-23-handoff-bug-cleanup-session.md`)

## Next-Time Checklist

- keep release proof suppression split into fixed diff failure and deferred real-host payload/post-create/base-ref risks is stale after this session; current split is fixed diff, fixed real-host payload/config, fixed base-ref lookup/fetch, and deferred post-create recovery semantics. (source: `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`; sources: 2)
- after any push that should auto-close issues, verify each issue's state (`gh issue view <n> --json state`) before declaring closeout done; the check is cheap and catches both this trap and the parent `Add #NNN` trap. (source: `charness-artifacts/retro/2026-05-23-handoff-open-issue-sweep.md`)
- do not edit `charness-artifacts/retro/recent-lessons.md` directly; write a session retro file and run `python3 skills/public/retro/scripts/refresh_recent_lessons.py --repo-root .` so the digest stays consistent with the selection index. (source: `charness-artifacts/retro/2026-05-23-handoff-bug-cleanup-session.md`)
- this refines the existing closing-keyword lesson rather than replacing it; the parent ("use a closing keyword at all") still holds. (source: `charness-artifacts/retro/2026-05-23-handoff-open-issue-sweep.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-22-release-base-ref-fallback-session.md`
- `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`
- `charness-artifacts/retro/2026-05-23-handoff-bug-cleanup-session.md`
- `charness-artifacts/retro/2026-05-23-handoff-open-issue-sweep.md`
