# Session Retro

Date: 2026-09-03

## Context

Goal Run #775, sessions three and four in one operator day: #780
wall-clock-rewrite-remainder, #781 lesson-promotion-and-budget with its joint
lesson review, and #782 integrated-closeout up to the parent close. The
operator set two rules mid-run that reshaped the work: graduation is three
questions (one owning `docs/` page with duplicates removed, a code mechanism
where possible, only then the event), and a docs-only graduation is allowed
only into a page read at the decision moment. What matters next is the hosted
readback of the one test that still raced the clock, and the second lesson
review (#783).

## Window

`1e9cb9991` (cursor at #780, 09:19 KST) to the #782 closeout commit (15:xx
KST): the FIFO witness, the 47-site rewrite, the graduate lifecycle, thirteen
lifecycle events and three seeds, seven graduation mechanisms, three push
refusals, and the clean-clone lanes.

## Evidence Summary

- `charness-artifacts/goal-runs/775/2026-09-03-session-record.md` (third and
  fourth sessions), `781-lesson-dispositions.md` (fifteen settled reasons),
  `782-clean-clone-lanes.md` (three lanes: 8750 passed; 82 passed, 5 not run;
  87 passed, 4 not run).
- `wall-clock-baseline.json` and `module-eviction-baseline.json` both empty;
  the gates report zero sites over 634 test files.
- Lesson ledger: 52 lessons, 39 active, 9 graduated, 4 archived, 13 lifecycle
  events; the three recurred classes active in the preview.
- Hosted: scheduled run 33701977188 on `1e9cb9991` failed its coverage
  baseline on one test, `test_cli_skill_surface_keeps_partial_output_when_even_the_drain_times_out`.
- No adapter `metrics_commands`; this retro is narrative with the counts above.

## Waste

- **Three push refusals for one commit, all the same class.** The release lane
  found a use-stamp written inside a hashed tree; the changed-line gate found
  about forty unproven lines and two unmapped modules. Each was fixable in
  minutes once named, and each was invisible to the focused runs the
  subagents had done. The previous session paid the same toll.
  (recurrence-class: green-test-is-not-covered-line)
- **A live-corpus invariant pinned in four tests without a name.** "Every
  lesson is active" held from the ledger's birth until the first lifecycle
  event, and four tests broke at once.
- **The wall-clock census had a blind shape.** A test whose deadline arrives
  through an environment knob into a subprocess carries no `time.*` call; the
  gate that closed 47 sites could not see the 48th, and it was the one the
  hosted baseline tripped on.
  (recurrence-class: verification-shape-mismatch)

## Critical Decisions

- The witness pattern: block on a FIFO the controlled child holds; no
  timeouts; the runner's budget is the only bound. Chosen over deadline polls
  because a poll passes vacuously when the child never reaches the point.
- Controlled children behind a kill proof sleep an hour, so a survivor cannot
  end EOF by dying of age. Found by mutating `_kill_tree` to a direct-child
  kill and watching the old tests still pass.
- Graduation as three questions, and the decision-moment criterion, both
  operator-settled and written into `lesson-graduation.md` rather than kept in
  the conversation.
- #782 closes today with #764 open: the fix for the last racing test is in the
  tree, and only a scheduled run may report recovery (#358).

## North Star Alignment

- P4/P5: no machine declared completion at an irreversible boundary; the
  parent closes through `goal-run-close` after exact readback, #764 waits for
  its observer.
- Documentation as code: the `Generated surfaces` rule has one owner, the
  mirror paragraph in `development.md` lost its duplicate, and a false
  sentence was deleted when its decision was found to have moved on.

## Trends vs Last Retro

- Push refusals: 3 (previous session 3). Same class both times; the structural
  move is in Next Improvements.
- Wall-clock sites in tests: 47 → 0 recorded; one unrecorded shape found by the
  hosted baseline and rewritten.
- Active lessons: 49 → 39 with the budget unchanged; graduated 0 → 9.

## Expert Counterfactuals

- A release engineer would have run the changed-line gate inside every
  subagent brief as the definition of done, instead of trusting focused runs.
  Cost of not doing so: two extra hook cycles of about five minutes each plus
  three subagent rounds.
- A kernel person would have asked, before the census, "which claims depend on
  time without calling the clock" and listed subprocess timeouts and probe
  deadlines beside `time.sleep`. Cost: one hosted baseline failure and one day.

## Next Improvements

- **workflow — `recurs:` the changed-line gate is part of a subagent's
  definition of done.** Every brief that touches `scripts/` or `skills/` names
  `release_changed_line_coverage.py --base-sha <base>` as a verification step
  and pastes its `blocking_detail`; a focused green is not a covered line.
  Structural pattern: verification bound to the writer's shape misses the
  reviewer's. Triggering instance(s): the second #781 push refusal, forty
  lines across seven files. (recurrence-class: green-test-is-not-covered-line)
- **capability — `recurs:` extend the wall-clock census to timeout-bound
  claims.** `check_wall_clock_form.py` or a sibling refuses a test whose
  verdict depends on a subprocess deadline knob (`*_TIMEOUT_SECONDS` set below
  a few seconds beside an assertion on captured output) rather than on a
  forced observation. Structural pattern: a proxy shape the gate does not
  model. Triggering instance(s): the drain test on hosted run 33701977188,
  rewritten in #782. (recurrence-class: verification-shape-mismatch)
- **memory — `recurs:` name a live-corpus invariant before the first event
  that can break it.** When a ledger, baseline, or record gains its first
  state transition, grep the tests that read the live artifact for the
  implicit "all rows are X" and give them a derived expectation.
  (recurrence-class: collection-time-pollution)

## Sibling Search

- same layer: other tests whose deadline arrives through an env knob |
  decision: valid follow-up outside the slice | proof: `grep -rn
  "TIMEOUT_SECONDS\"\] = \"0\." tests` names the two probe-boundary tests
  rewritten here and `test_cli_skill_surface_reports_probe_timeout`, whose
  claim is the timeout itself; follow-up: the census extension above.
- abstraction up: any hashed tree that a retention stamp could dirty |
  decision: fix now | proof: `grep -rn "last-used\|\.used" scripts tests` shows
  the seed cache already used a sibling `.used` file; support-skills now does.
- specialization down: other tests reading the live lesson ledger | decision:
  fixed in #781 | proof: the four repaired tests derive their expectation from
  the ledger's states.
- mental-model siblings: the installed plugin read ahead of the repo tree
  inside the charness repo | decision: valid follow-up outside the slice |
  proof: pickup refused from `~/.agents/src/charness` a fourth time this run;
  follow-up: the Claude host adapter routes skill scripts to the working tree
  in this repo, or release 8.0.3.

## Portable Candidate

- abstract pattern: a test that waits on a controlled child blocks on a FIFO
  the child holds, and a timeout test drives the module's clock from that
  observation.
- triggering evidence: 47 sites in one repo, six scheduled hosted runs lost to
  them.
- intended consumer/repo shape: any repo with subprocess-heavy tests under a
  loaded parallel runner.
- destination: `create-skill` is not the right home; the pattern is a test
  helper (`tests/fifo_witness.py`) and a rule sentence already in
  `docs/development.md`. Not portable as a skill.
- first-prompt acceptance claim: n/a.

## Packet Consumed

n/a (no adapter sections)

## Persisted

Persisted: yes: charness-artifacts/retro/2026-09-03-goal-775-closeout-retro.md
Seeding: 9 class(es) seeded
