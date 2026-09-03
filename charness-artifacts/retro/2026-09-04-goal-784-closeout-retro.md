# Session Retro

Date: 2026-09-04

## Context

Goal Run #784, fourth session: #789 integrated-closeout up to the guarded
parent close. Five children were already closed by `Closes #N` carriers in the
earlier sessions of the same operator day; this session proved the
composition (three lanes in a clean clone), gave every child its issue-owned
closeout comment, read the hosted mutation run for #764, and prepared the
close proof. What matters next is the hosted mutation budget: the sampler's
baseline is green again, and the run now dies of its own size.

## Window

`b5fb69dba` (cursor at #789, 06:30 KST) to the #789 carrier commit: clean-clone
lanes, five `verify-closeout` readbacks and five comments, the #764 reading,
the terminal obligation and expected final graph, this retro, and the close.

## Evidence Summary

- `charness-artifacts/goal-runs/784/789-clean-clone-lanes.md` (standing 8863
  passed; full read-only 83 passed, 5 not run; release lane recorded there).
- `verify-closeout` = `verified` for #783, #785, #786, #787, #788 against
  their carriers; comments posted through `close-with-comment` on the already
  closed issues, byte-for-byte the carrier commit messages
  (`closeouts/issue-<n>.md`).
- Hosted: scheduled run 33756376766 on `bce861e15`: `Select mutation sample`
  success, `Run mutation` cancelled at `elapsed=8880.1s` by
  `timeout-minutes: 180`, no per-mutant result. Reading recorded on #764 and in
  `764-recovery-observer-reading.md`.
- Lesson ledger: 62 lessons, 25 active, 25 graduated, 12 archived, 37
  lifecycle events (after #783). Pickup preview seed `goal-784-session4`.
- Prepare packet `2026-09-03-214008-packet.md`: rework issues since 2026-08-04
  name `achieve` twice, `issue` once, `retro` once; none filed this session.

## Waste

- **The hosted mutation run recovered its baseline and then lost the job to
  its own budget.** The #782 fix held (sampler green for the first time since
  2026-08-31), but 118 executable mutants times a per-mutant run of the whole
  non-release suite is about three hours, the job allows 180 minutes minus 33
  minutes of setup and sampling, and the exec's internal 9000 s timeout is
  longer than what the job has left. The job cancel arrives first, so the
  summary reads UNEXPLAINED instead of the exec's own timeout marker. Two
  budgets, the inner one wider than the outer one, and nothing checks the
  order. (recurrence-class: inner-timeout-outlives-outer-budget)
- **Issue-owned closeout comments arrive in a batch at closeout, not at each
  close.** Same shape as #775: the `Closes #N` carrier closes the issue, and
  the comment the close proof needs is posted hours later by the integrated
  closeout. Cheap this time (five commands), but the proof's evidence identity
  is created by the last session rather than by the close that earned it.

## Critical Decisions

- #764 stays open with the budget named as the next work; no hand close
  (#789 non-claim), no dispatch run, no ceiling change inside this slice.
- The five child comments are the carrier commit messages verbatim, so the
  comment, the commit, and `verify-closeout` all read the same bytes.
- The parent obligation names release 8.0.3 as published inside #788 under
  pre-approval and not re-claimed by the close.

## North Star Alignment

- P4/P5: the parent closes only through `goal-run-close` after exact
  readback; #764 waits for its observer even though the fix it waited for is
  proven; the machine records the budget finding and stops.
- Documentation as code: no `docs/` page changed this session; the reading
  lives on the issue and in the dated artifact, not in a standing page.

## Trends vs Last Retro

- Push refusals: 0 so far this session (previous retro: 3). The changed-line
  done-gate from #785 and the release lane in the hook were in place for every
  push of this run after #785.
- Hosted mutation: baseline failure (previous retro) to baseline green and an
  exec timeout (this retro); the failure moved one step later in the job.
- Active lessons: 39 to 25 with the budget unchanged; graduated 9 to 25.

## Expert Counterfactuals

- A CI engineer (Charity Majors' "you have to size the run to the runner")
  would have set `max_executable_mutants` from a measured per-mutant runtime
  and the job budget on the day the sampler ceiling was chosen, and would have
  put the exec timeout below the job timeout so the tool's marker, not the
  runner's cancel, is what the summary reads. Cost of not doing so: one lost
  three-hour hosted run and one more #764 cycle.
- A decision-quality lens (Gary Klein's premortem) would have asked at the
  #782 closeout, "if the next scheduled run is not green, what besides the
  test set could it be?" and listed the job budget beside the baseline. The
  reading would then have been a check, not a discovery.

## Next Improvements

- **capability — `novel:` bind the mutation exec budget to the job budget.**
  `run_cosmic_ray_mutation.py` refuses or shrinks a sample whose
  `executable_mutants × measured_baseline_seconds` exceeds the job's remaining
  budget, and the exec timeout is derived below `timeout-minutes` so the
  marker is the tool's. Structural pattern: an inner deadline wider than the
  outer one, with no ordering check. Triggering instance(s): hosted run
  33756376766, cancelled at 8880 s of a 9000 s exec inside a 180-minute job.
  Destination: issue on #764's thread as the next work.
  (recurrence-class: inner-timeout-outlives-outer-budget)
- **workflow — post the issue-owned closeout comment when the carrier lands,
  not at the integrated closeout.** The child closeout step in the session
  recipe runs `close-with-comment` with the carrier body right after
  `verify-closeout`, so the close proof's evidence identity exists the moment
  the child is proven. Structural pattern: proof evidence created by the
  reader, not the writer. Triggering instance(s): five comments posted in this
  session for closes made in the previous three.

## Sibling Search

- same layer: other hosted jobs with an inner tool timeout beside a
  `timeout-minutes` | decision: valid follow-up outside the slice | proof:
  `grep -rn "timeout-minutes" .github/workflows` and `grep -rn "TIMEOUT_SECONDS
  = " scripts/mutation` name the mutation job only; the release and standing
  workflows carry no inner timeout; follow-up: the capability item above.
- abstraction up: any sampler ceiling chosen without a per-unit runtime |
  decision: valid follow-up outside the slice | proof: `max_executable_mutants`
  120 and `max_executable_mutants_per_file` 80 in the adapter slots carry no
  runtime basis; same follow-up.
- specialization down: n/a — the budget check is one site.
- mental-model siblings: a step reported as UNEXPLAINED that is in fact a
  known cause (job cancel) | decision: recorded on #764 | proof: the summary
  step already distinguishes three states; the fourth (outer cancel) is what
  the capability item adds.

## Portable Candidate

- abstract pattern: when a tool runs under two deadlines, derive the inner one
  from the outer one and refuse a workload the outer one cannot hold.
- triggering evidence: one hosted run lost after the baseline it waited for
  was finally green.
- intended consumer/repo shape: any repo running a sampled long job under a
  hosted runner with a job timeout.
- destination: not portable as a skill; it is a rule sentence for the
  mutation runner and a workflow check.
- first-prompt acceptance claim: n/a.

## Packet Consumed

`2026-09-03-214008-packet.md`: changed files were all goal-run evidence under
`charness-artifacts/goal-runs/784/`; rework attribution read (no new rework
issues this session).

## Persisted

Persisted: yes: charness-artifacts/retro/2026-09-04-goal-784-closeout-retro.md
Seeding: 1 class(es) seeded
