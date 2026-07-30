# Session Retro
Date: 2026-07-30

## Context

One goal run: the armed changed-line pre-push lane's known holes, taken from the
handoff chunker's ranked chunk 1 and shaped through `achieve`. Five slices, all
closed, 17 commits. What matters next is that two of the three gaps the handoff
listed under "named and did not close" are now closed, and the handoff still says
otherwise.

## Window

`4516729a` (the verdict-timing sweep's owning artifact) through the slice-5
commit `b80f0088` plus closeout. Six bounded review rounds across four slices,
each spawned as a typed `bounded-reviewer` with the boundary fingerprint
snapshotted before and verified at return.

## Evidence Summary

- Goal artifact `charness-artifacts/goals/2026-07-29-close-the-armed-changed-line-pre-push-lane-s-known-holes-pin.md`,
  five Slice Log entries with per-slice falsifiers.
- `bash scripts/run-quality.sh`: 82 passed / 1 failed on the first final run, both
  failures traced and fixed, re-run clean.
- `python3 scripts/prepush_focused_changed_line_coverage.py` run AFTER each
  commit: BLOCKED on four separate slices, clean after covering the reported
  lines each time.
- Host log probe (claude session scope, thread-wide): 535 function calls, 58
  patch applications, 10 subagent spawns, 0 context compactions. Token snapshots
  are point-in-time, not a cumulative total, so no token cost is claimed.
- `mine_closeout_telemetry.py`: 4 recurring waste items, `over_slice` at 37
  occurrences with peak run 4.

## Waste

- **The stash/pop that cost ~12 minutes and a false alarm.** To decide whether 15
  `charness_cli` failures were mine, I stashed, ran the suite (201 pass), popped,
  and ran again (13 failed + 21 errors). The cause was plugin-mirror drift: I had
  edited source after the last sync, and the stash cycle made it visible. Three
  full suite runs at ~3 minutes each to rediscover sync-before-verify, which is
  the first line of this repo's Phase Rules.
- **Four separate changed-line BLOCKs, all the same shape.** Every slice added
  verdict branches exercised only through subprocess runs, so each slice
  committed, got blocked, and added in-process tests. Four cycles of a lesson
  that was fully learned after the first. **Corrected 2026-07-30 while closing
  #465, by measurement:** "the coverage mapper cannot see across a process
  boundary" — as this entry originally read — is false here. The producer writes
  a `sitecustomize` calling `coverage.process_startup()`, and a subprocess-only
  test of a script at its real path attributes 143 lines. What loses the
  measurement is narrower: an `env=` that REPLACES the environment, or a test
  that runs an out-of-tree COPY of the script (outside the rcfile's
  `source = <repo_root>`, 0 lines attributed). Some of the four BLOCKs were
  therefore TRUE blocks on genuinely unexercised branches.
- **Two adapter-schema guesses.** I wrote a test against
  `adapter["runtime_budgets"]["profiles"]` and then against a `budgets` key that
  did not exist, before reading the actual shape (`runtime_budget_profiles`).
  Two rejections for something one `python3 -c` would have settled first.
- **Not waste, and worth separating:** the six review rounds and the reproduce-
  first probes. Every round changed the design, and four of the six caught a
  defect in the repair rather than in the original.

## Critical Decisions

- **Probing `../ceal`, `../crill`, `../cautilus` instead of arguing about
  consumer repos.** This collapsed slice 1 from "arm every consumer repo" to "stop
  this repo silently disarming itself". No consumer runs charness's runner —
  ceal and cautilus own theirs, crill uses lefthook. The chunk was ranked #1 on a
  premise that three `ls` commands falsified.
- **Reverting the release role-word widening rather than repairing it.** The
  widening made a dated release RECORD match, and the refusal's remedy tells the
  operator to rename or delete the file and commit that. A verdict surface at an
  irreversible boundary pointing that advice at durable evidence is worse than
  the miss it guarded — and the miss was never observed in 51 files.
- **Recording D42 and D43 instead of deciding them.** Both are exit-code and
  advisory-scope contract questions with real arguments on each side; deciding
  either inside a defect-repair slice would smuggle a contract change in under a
  repair banner.
- **Following a wrong premise until it broke.** Slice 5's stated premise was
  inverted (the advisory divides by max, not median). Checking *why* the advisory
  did not fire is what surfaced that the bar was tight rather than loose, which
  is what surfaced `run-quality-read-only` — the bar that actually stops a push,
  already reporting `latest-spike`, which the slice had not been looking at.

## Trends vs Last Retro

The prior digest's four repeat traps: two recurred and two did not.

- **Recurred: "commit before reading a changed-line verdict."** Not as a false
  green this time — I ran it after commit every time — but as four consecutive
  BLOCKs for the same unmeasured-subprocess-branch reason. The digest entry
  covers the ordering; it does not cover the shape.
- **Recurred: hand-authoring instead of starting from the shape.** Last session
  it was four enum rejections on a critique artifact. This session it was two
  adapter-schema guesses. Same class, different surface.
- **Did not recur: the installed-vs-source helper trap.** No release helper was
  run from an installed copy.
- **Did not recur: reviewer-boundary verification timing.** Every one of the six
  rounds snapshotted before the spawn and verified at return BEFORE repairing —
  the exact correction the last retro asked for, applied six times.

## Expert Counterfactuals

**Engelbart (system-improving-itself), on the four identical changed-line
BLOCKs.** The briefed lens says design T alongside LAM: the tool that reports the
gap should also close the loop that produces it. Four times I committed, was
told "these verdict branches are uncovered", and wrote in-process tests. The
information needed to prevent iteration 2 existed at iteration 1 — the gate
already names `blocking_targets` as `path:line` with source text, and every one
of those lines was a branch whose only exercise was a subprocess. The
counterfactual is not "remember to write in-process tests"; it is that
`suggest_mutation_coverage_command.py` could report, for a blocked line, whether
the file's existing tests reach it only via `subprocess`/`run_script` — turning a
four-cycle habit into a one-line diagnosis. That is a capability, and it is the
one I would build first.

**Gary Klein (pre-mortem / recognition-primed decision), on slice ordering.** A
pre-mortem on slice 1 would have asked "if this ships and changes nothing, why?"
The answer — "because no consumer repo runs this runner" — was three directory
listings away and would have reordered the whole goal before any code was
written. I got there, but via a bounded reviewer at round 1 of slice 1, after the
plan was shaped and the chunk was ranked. The cheap move is a *reachability
probe* during shaping for any slice whose value claim names a consumer or an
environment the session cannot see.

## Sibling Search

- axis: **same-shape unmeasured verdict branches** | location: every gate script
  whose refusal paths are tested through `run_script`/`subprocess` | decision:
  valid follow-up outside the slice | proof: the boundary-bypass baseline records
  61 `test → script` subprocess pairs, and this session hit the coverage
  consequence four times in four different files (`validate_maintainer_setup`,
  `check_changed_line_mutation_coverage`, `check_mutation_run_proof`,
  `audit_public_release_narrative`) | follow-up: deferred handoff-anchor
  `subprocess-only-verdict-branches`
- axis: **contract prose asserting a compensating control that does not exist** |
  location: rationale comments and docstrings on proof surfaces | decision:
  fixed in slice | proof: round 2 of slice 4 caught my own comment claiming "the
  adapter contract now does" document a convention it did not; the same class
  appeared in slice 2's module header, which stated a rule for readers
  (`_git_lines` returning `[]` "must be read as could not establish") that the
  code did not implement | follow-up: n/a — both instances repaired and the
  lesson is in the digest below
- axis: **bars and baselines whose basis predates a landed cost** | location:
  `.agents/quality-adapter.yaml` runtime profiles | decision: valid follow-up
  outside the slice | proof: three named in slice 5 — the 4cpu `run-quality-full`
  and `run-quality-read-only` bars, and the 4cpu changed-line samples that would
  make `--suggest-budgets` propose ~3500 for the dominant gate | follow-up:
  deferred handoff-anchor `pre-lane-runtime-bases`

## Next Improvements

- workflow: **run a reachability probe during shaping for any slice whose value
  claim names a consumer, host, or environment the session cannot see.** Slice 1
  was ranked #1 on a claim three `ls` commands falsified. This is the Klein
  counterfactual, and it is cheaper than a review round.
- capability: **teach the changed-line gate to say when a blocked line's only
  coverage is a subprocess test.** The gate already emits `blocking_targets` with
  source text; the mapper already knows which tests reference the file. Reporting
  "reached only via `run_script`" would collapse this session's four-cycle habit
  into a one-line diagnosis. Filed as a Next Improvement, not applied: it changes
  a blocking gate's payload and owes its own two-round review.
- memory: **a rationale is a claim.** Writing "the adapter contract now documents
  this" without checking reproduced, inside the justification for a fix, the
  exact class the slice was closing. Verify the compensating control you cite in
  the same breath as citing it.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-30-session-retro.md
