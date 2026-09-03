## Situation

Goal Run #775 closed on 2026-09-03 with three follow-ups recorded in its closeout retro and session record, and #783 open for the second joint lesson review. The four strongest graduation candidates (`changed-line-proof-before-broad-quality`, `green-test-is-not-covered-line`, `detector-blind-class-unstated`, `bar-recorded-as-prose`) share a shape with those follow-ups: each needs a mechanism to graduate onto under the three-question rule.

## Experience

A subagent reports a focused green and the push is refused four times on lines nobody proved. A test with no `time.*` call fails the hosted baseline because its verdict rode on a timeout knob the census could not see. A session in this repo picks up its own goal and the installed 8.0.2 plugin refuses it, four times, until the agent runs the checkout's script by hand. The runtime root for this repo holds 50 GB, 41 GB of it 23,401 runtime roots of fixture repos nested inside its cache, with no policy that reaches them.

## Evidence

| Surface | Read 2026-09-03 |
| --- | --- |
| lesson ledger | 61 lessons, 47 active of 50, 34 scored active; top candidates 14/20, 11/11, 10/15, 7/12 `changed-an-action` |
| changed-line gate | pre-push hook only; `task_run_completion.py` has `base_sha` and writes no changed-line verdict; four refusals for #781 |
| wall-clock census | both baselines empty; 12 test files read `*_TIMEOUT_SECONDS`; hosted run 33701977188 tripped on that shape |
| runtime root | this key 50 GB; `xdg-cache/charness/runtime/` 23,401 nested keys, 41 GB; `charness/runtime/` 1,871 keys, 340 GB; retention only for `pytest-tmp`, `test-seeds`, `support-skills` |
| installed plugin | 8.0.2 at `~/.agents/src/charness`; 173 commits since v8.0.2; pickup refused four times in #775 |

Planning record: `charness-artifacts/goals/2026-09-03-lesson-review-and-775-followups.md`.

## Impact

Each item is a path by which a wrong done, a wrong green, or an older tree reaches a decision, and the disk one is a path by which a session stops for lack of space. The cost already paid: three subagent rounds and two hook cycles for one commit, one hosted baseline failure and a day, four hand fallbacks, and 340 GB.

## Desired outcome

- Each of the 34 scored active lessons has a settled disposition with a written reason; graduations carry owner page, duplicates removed, mechanism or stated gap, and event in one commit.
- A lane receipt carries the changed-line verdict; a brief's definition of done names it.
- The form check refuses a timeout-bound verdict and states what it still cannot see.
- Runtime roots are siblings, never nested, with a retention row per subtree and per key; the first cross-key sweep reported before it deletes.
- Skill scripts resolve to the checkout inside this repo; 8.0.3 shipped or its deferral recorded.

## Ownership contract

- Goal Draft owns intent, boundaries, and slice design; Goal Binding owns the frozen identity; this parent owns the cursor; Work Item issues own implementation state and proof. #783 is a reused child.
- Graduation is settled lesson by lesson between the operator and the agent; no rule, classifier, or commit inspection decides one; mechanisms precede the lessons they graduate.
- A focused green is not a covered line; a test's verdict never depends on wall-clock time; deletion under the runtime root is reported before it is done and never reaches outside `charness/runtime/`.
- Publishing 8.0.3 is separately authorized; #764 closes only through its observer; the parent closes only through the guarded close after exact readback.

## Work sequence

1. lane-changed-line-done
2. timeout-bound-census
3. lesson-review-783
4. runtime-root-retention
5. checkout-first-routing-and-8-0-3
6. integrated-closeout

## Completion criteria

- Every child provider-closed with behavioural evidence.
- Standing, full read-only, and release lanes green in a clean clone with the skip list read.
- Parent closed only through the guarded Goal Run close after exact readback.

## Non-claims

- No budget increase, seeder change, vocabulary change, sampler redesign, hosted `release_only` job, rename-sweep tool, file move, or AGENTS.md/CLAUDE.md edit.
- Push, tag, release publish, cross-key deletion, and installed-host mutation remain separately authorised.

AI provenance: drafted by an AI agent (Claude Code) from the operator's 2026-09-03 request; activation and approval are deferred to the next session.
