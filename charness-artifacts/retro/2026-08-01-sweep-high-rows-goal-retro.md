# Goal Retro — the sweep's remaining high rows, four slices

Date: 2026-08-01

## Context

The whole `achieve` run: chunked routing picked the sweep's high rows, the goal was
shaped and plan-critiqued, four slices ran, and the closeout disposition review cleared
it. This retro closes the goal. The mid-run slice-1 retro
([2026-08-01-slice-1-absent-input-batch-retro.md](./2026-08-01-slice-1-absent-input-batch-retro.md))
proposed three improvements with three slices left to apply them to; the first thing this
retro owes is an honest score on whether they landed.

Goal: [close-the-sweeps-remaining-high-rows-by-class](../goals/2026-08-01-close-the-sweeps-remaining-high-rows-by-class.md)

## Window

`7de074c1..cac8ac98` — nine commits, from shaping to the disposition fold. One goal, four
slices, eight review rounds.

## Evidence Summary

- The goal artifact's `## Final Verification`, which carries the bundle proof and the
  non-claims.
- Six critique artifacts under `charness-artifacts/critique/` dated 2026-08-01: one plan
  critique (recorded inside the goal), four slice-level, one midpoint, and the round-2
  addendum. The closeout disposition review's findings are folded into the goal and this
  retro rather than into a seventh.
- Two recorded probes, both re-runnable:
  `2026-08-01-adapter-yaml-uninterpreted.json`, `2026-08-01-inventory-consumption-floor.json`.
- Bundle proof: 6515 tests passing in one serial run; `./scripts/run-quality.sh` 82/1;
  `prepush_focused_changed_line_coverage.py --base-sha 7efa0240 --refuse-unestablished`
  CLEAN after three runs.
- Host log (`probe_host_logs.py`, claude scope, thread-wide not per-goal): 458 function
  calls, 29 patch applications, **17 subagent spawns**, 0 context compactions. Proxy:
  `git worktree` ×8 — the detached-HEAD comparisons that proved each repair's baseline.
  Token snapshots exist but are point-in-time, so no token claim is made.

## Waste

**The dup-ratchet blocked ten times, all at the closeout aggregate.** Four last session,
ten this one. The slice-1 retro proposed running it at the first edit to a gated file;
that improvement was written down and not implemented, so the same treadmill ran three
more times. One of the ten produced a real extraction (`repo_path_display`, which two
surfaces had grown independently); the rest were classifications of rotated boilerplate.

**Three passes on one 100-line measurement script, then a second script repeating the
first's mistakes.** `measure_adapter_yaml_uninterpreted` was written to justify a decision
already made, then found to measure the wrong population, then found to be a
zero-denominator green. `measure_inventory_consumption_floor` then shipped without a test,
without measuring the label floors its own comment cited, and without a `--floor` flag
making its counterfactual re-runnable — all three of which the *same session* had already
learned one script earlier.

**The claims drifted from the code in three separate places, each caught by a different
round.** Slice 2's round 2 repaired a false floor claim in the code and left the identical
claim standing in the goal artifact, where the midpoint round found it. The disposition
round then found five more affirmatively-false claims about slice 4 — "round 2 was never
run" after it had run, a Slice Plan status contradicting its own row, an empty Commits
field. Repairs propagate to code by habit; they do not propagate to prose without a round
whose only job is prose.

**Not waste, though it reads like it:** eight review rounds and 15 reviewer spawns. Round
2 found defects created by round 1's own repairs in every slice where it ran, including
one that would have shipped a parser silently merging YAML documents. The midpoint and
disposition rounds each found a class the slice rounds structurally could not see.

## Critical Decisions

- **Withdrawing the S24 arming rather than re-scoping the stop condition**, and doing the
  same again for D47 and D48. Three refusals measured, costed, and deliberately not armed
  is the run's shape.
- **Reproducing S23 instead of trusting the plan's REFUTE prediction.** The plan and a
  round-1 reviewer independently concluded it could not reproduce, from the same correct
  evidence. It reproduces through a post-hoc fold. The rule bought a real defect.
- **Closing six of nine rows as NARROWED.** Every one had a defensible CLOSED story.
- **Running slice 4's round 2 when the operator asked** rather than leaving it as the
  recorded gap I had planned to hand off. It found four blockers.

## Trends vs Last Retro

Scoring the slice-1 retro's three improvements:

- **workflow — dup gate at first edit: NOT DONE.** Cost: six more late blocks. This is now
  three retros naming it.
- **capability — the measurement script's empty-corpus refusal: DONE**, and it held. But
  the lesson did not generalize to the *second* measurement script, which had to be
  taught the same three things by review.
- **memory — "a self-authored constraint is not a check": PARTIALLY HELD.** No stop
  condition was violated again. But the artifact-side variant of the same shape ran three
  times: a claim written by me, contradicted by my own measurement, and caught only by a
  reviewer.

Against the older trend line, the batching lever the 2026-08-01 retro named was applied
throughout — round-1 reviewers ran while the parent worked the next batch, and there was
no idle wait in any slice.

## Expert Counterfactuals

**Engelbart — treat (H + LAM + T) as one unit; design T alongside LAM.** The slice-1
retro already named this: goal-artifact prose is tooling with no L. Three slices later the
diagnosis is sharper and worse. Every *code* claim in this run is now backed by a
re-runnable script and a pinned test, because the changed-line gate and the test suite
force it. Every *artifact* claim is backed by a human reading it once. That asymmetry is
the whole shape of this run's waste: the midpoint and disposition rounds are two humans
doing a diff a tool could do — comparing the goal's per-row assertions against the sweep's
rows and the commit list. The Engelbart move is not "review harder", it is that
`check_goal_artifact.py` already parses this artifact and could refuse a Slice Plan row
whose status contradicts its own outcome cell, an empty `Commits:` on a DONE slice, or a
`## Off-Goal Findings` that is empty while the Slice Log names findings. Three of the
disposition round's eight blockers are exactly that shape and cost a reviewer to find.

**Direct lens on generalization — the second instance is where a lesson is actually
tested.** The first measurement script learned three things by review; the second one,
written by the same agent in the same session with the first still in context, repeated
all three. The lesson had been recorded as a fact about a file rather than as a rule about
a kind of file. The changed action is small: when a fix lands on a surface, ask "what is
the CLASS of this surface, and what else in this session belongs to it" *before* writing
the next member. That question would have cost one sentence and saved a full review round.

## Sibling Search

- same layer: `scripts/measure_evidence_residual.py` — the S3 floor's measuring script,
  the third member of the measurement-script class | decision: valid follow-up outside the
  slice | proof: re-checked this session; it reports `corpus_established: false` over an
  empty corpus and still exits 0, and no caller consumes the field. It has a test, unlike
  the second script did, but the exit-code channel carries none of its finding |
  follow-up: deferred `docs/handoff.md` `## Next Session` — carried as a named lead
- abstraction up: `check_goal_artifact.py` and the achieve floor family, which parse the
  goal artifact and could mechanically refuse the three self-contradiction shapes the
  disposition round found by hand | decision: valid follow-up outside the slice | proof:
  the disposition round's blockers 1, 2 and the Slice-Plan-status contradiction are all
  parseable from the artifact this validator already reads | follow-up: deferred
  `docs/handoff.md` `## Discuss` — needs an operator call on whether goal-artifact
  self-consistency becomes a gate
- specialization down: `scripts/measure_inventory_consumption_floor.py` | decision: same
  waste, fix now | proof: fixed in slice 2 — empty-corpus refusal, `--floor`, label-floor
  measurement, and a test that re-runs the recorded probe
- mental-model siblings: any repair that lands in code while its claim lives in prose —
  the sweep rows, the deferred decisions, the goal artifact, the handoff | decision:
  diagnostic-only | proof: this run produced three measured instances (slice 2's floor
  claim, slice 4's round-2 status, the handoff's five stale claims), and the only channel
  that caught them was a review round whose packet was prose

## Portable Candidate

- Abstract pattern: a goal-lifecycle artifact is a verdict surface, and its
  self-contradictions are mechanically detectable — a DONE slice with an empty commit
  field, a plan row whose status disagrees with its outcome cell, an empty findings
  section beside a log that names findings.
- Triggering evidence: three of eight closeout-disposition blockers this run; the midpoint
  round's blocker 2 (both `Commits:` empty); the prior goal's closeout finding that an
  acceptance criterion had gone unmet for all five slices.
- Intended consumer/repo shape: any repo running `achieve`-style goal artifacts.
- Destination: `create-skill` — extend `check_goal_artifact.py`'s existing parse rather
  than a new surface. Not filed yet: this is the second instance across two goals, and
  this repo has withdrawn one-instance floors twice, so it wants the operator's call
  (carried to `## Discuss`) rather than a unilateral gate.
- First-prompt acceptance claim: "given a goal artifact with a DONE slice and an empty
  `Commits:` field, the check refuses and names the row."

## Next Improvements

- workflow: **run the dup-ratchet at the first edit to a gated file.** Third retro naming
  it, ten blocks this run against four last. It is no longer a suggestion; either wire it
  into `run_slice_closeout.py --predict-commit` or stop recording it.
- capability: `applied: charness-artifacts/critique/2026-08-01-goal-midpoint-claims-review.md`
  — the midpoint round had no checked-in record until the disposition round found that
  gap, in a goal whose acceptance criteria exist because the prior goal had none. Every
  review round in this goal now has an artifact.
- memory: **a lesson learned on one file is not learned until the second file of its class
  passes without review.** The second measurement script repeated all three of the first
  one's defects, in the same session, with the first still in context.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-01-sweep-high-rows-goal-retro.md
