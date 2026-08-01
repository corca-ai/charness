# Closeout claims review — push the lane, then close the record, the regression and the rows
Date: 2026-08-01

## Decision Under Review

Whether the goal `2026-08-01-push-the-lane-then-close-the-record-the-regression-and-the-rows`
may flip to `complete`: does each claim in the goal artifact, its retro, and the
sweep's new dispositions match what the owning records actually say?

## Failure Angles

- A lane's `## User Acceptance` criterion certified as met when the run's own
  records say it was not — the highest-cost class, because a future session plans
  against the criterion, not the narrative.
- Figures asserted in a closeout with no checkable source — the exact defect this
  goal's Lane B existed to repair, in the closeout that repaired it.
- A durable number replaced somewhere and left stale elsewhere.
- A headline measurement whose denominator could not have contained a violation.
- Sweep row status cells claiming more or less than their narrative supports.

## Counterweight Pass

Four findings were real blockers and were folded. Several others were correctly
identified as disclosure gaps rather than false claims — Lane A's distinct-channel
readback WAS honoured, the prohibition on citing the local changed-line lane WAS
honoured (the reviewer grepped for it and found none), D45's every checkable claim
IS corroborated by the files it names, and the reviewer-spawn count IS consistent
with the persisted fingerprint windows. The review's own framing was right that
those are not defects.

The one place I push back on the reviewer: F1's suggestion that the alternative to
an acceptance amendment is reopening #467. Reopening would free and re-consume the
cron dedupe marker without improving the evidence, which is now direct line
coverage rather than a gate's range. The amendment is the honest instrument, and
it was written into `## User Acceptance` where the criterion lives — not into a
narrative section a planner would skip.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: goal `## User Acceptance` Lane C | action: fix | note: #467 was closed on the outcome the criterion declared inadmissible, and the record never said so; an explicit AMENDMENT now states the criterion was not met as written, names the deviation, and explains why leave-closed-plus-correct was taken over reopen
- F2 | bin: act-before-ship | evidence: strong | ref: goal `## Final Verification`, `## Slice Plan`, `## Auto-Retro`, `## Off-Goal Findings` | action: fix | note: all were TODO or empty while the retro asserted all four lanes closed; every section is now filled, and the figures carry sources in the form Lane B shipped
- F3 | bin: act-before-ship | evidence: strong | ref: retro `## Evidence Summary` | action: fix | note: "23 in scope, 0 refused — armed" omitted that 20 of 23 are undatable and only 2 were compared; the same shape round 2 refuted for the sibling floor, shipped armed in the same slice. Restated with its denominator, and the Sibling Search corrected from "could be armed tomorrow" to "was armed today"
- F4 | bin: act-before-ship | evidence: strong | ref: `goal_artifact_figure_form.py` docstring vs D49 | action: fix | note: the relaxed-form refusal count read 44 in the module and 41 in three records; re-measured against the shipped module — 41 is correct, 44 predated the heading-grouping repair. Corrected in source and mirror, and the stale value grepped out
- F5 | bin: act-before-ship | evidence: moderate | ref: goal `## Operator Decision Queue` Q1 | action: fix | note: Q1 FIRED and its answer lived only in the retro; the red run, its per-job verdict, both run URLs, and the operator's fix-forward decision are now recorded in the queue entry itself
- F6 | bin: valid-but-defer | evidence: moderate | ref: sweep rows S15, S111 | action: document | note: both status cells are honest but their original wrong-output cells now contain superseded characterizations; in-cell correction markers added in the S12 style rather than rewriting the frozen reproduction text
- F7 | bin: over-worry | evidence: moderate | ref: retro figures classified "asserted only" | action: document | note: a closeout cannot check in a coverage report for every figure without becoming an artifact dump; the repair is the `<value> — <source>` form, which names the command a reader can re-run, and that is now applied throughout `## Final Verification`
- F8 | bin: act-before-ship | evidence: strong | ref: goal `## Final Verification` non-claims | action: document | note: no `verify --before` result was recorded for any reviewer window and 2 of 4 reviews have no persisted window at all — a shortfall against this goal's own High-Confidence Checks, now stated as a non-claim rather than left implied-satisfied
- F9 | bin: act-before-ship | evidence: strong | ref: retro + goal backlog counts | action: fix | note: 29, 30, and 31 appeared for one quantity; counted rather than transcribed — 31 + 2 = 33 total, each with its command
- F10 | bin: valid-but-defer | evidence: moderate | ref: goal `## Boundaries` clause (3) | action: fix | note: the enumeration named only Lane D and the retro as issue-filing sources, but #469 was filed from a Lane A/C finding; the clause is widened rather than stretched, since an unenumerated write is the defect that block exists to prevent

## Reviewer Tier Evidence

- Requested tier: `bounded-reviewer` (the repo's typed read-only reviewer agent).
- Requested spawn fields: `subagent_type: bounded-reviewer`, no host addressing/team `name`, `run_in_background: false`. No model/effort override: on a Claude Code host the per-host contract uses session-model inheritance.
- Host exposure state: host-defaulted
- Application state: host-confirmed: the spawn returned findings inline; the reviewer reported its own envelope as bound to Read/Grep/Glob.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed; the reviewer was given an inline brief naming the artifacts to read and seven claim-checking questions. The binding floor is therefore off by design, and this critique does not claim packet-bound identity. -->

## Boundary Ownership

- Producer: this run's goal artifact, retro, resolution critique, and the sweep's disposition section.
- Consumer: a future session planning against those records, which reads the acceptance criteria and the figures rather than the narrative.
- Owning surface: the goal artifact owns its acceptance criteria and closeout evidence; the retro owns the waste and improvement claims; the sweep owns each row's disposition.
- Verdict: owned-correctly

Each finding was folded into the record that OWNS the claim, not into a summary:
the Lane C amendment sits in `## User Acceptance` beside the criterion it
qualifies, the denominator restatement sits in the retro's Evidence Summary, the
41/44 correction went into the module docstring and D49, and the Q1 answer went
into the Operator Decision Queue entry. A finding folded only into a closeout
narrative would be invisible to the reader the criterion is written for.
