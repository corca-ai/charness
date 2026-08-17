# Critique Review
Date: 2026-08-17

## Decision Under Review

Closing #617 ("Persist opened lesson sessions for compaction-safe reference") as
RESOLVED on the claim that a PRIOR session already implemented it, so closing merely
records an existing fact. Nobody in this session wrote the implementation, which is the
condition under which a closure is most likely to be transcribed rather than measured.

## Failure Angles

- The whole premise — "a prior session already did it" — resting on reading code that
  looks right rather than on executed proof or release containment.
- A stated expectation quietly dropped because the other two-thirds of the same sentence
  are satisfied: #617 asks the command, the work workflow, AND retro to reference the
  bundle by session id.
- The bundle being written but not MANDATORY, so a receipt could be accepted with the
  file missing and the compaction-recovery promise silently void.
- A crash between the bundle write and the receipt write leaving a state that validates
  anyway.
- The one-contract rule (no migration, no compatibility branch) producing an unrequested
  regression for receipts written before the bundle existed.
- The issue's own canonical living contract disagreeing with the closure.

## Counterweight Pass

One bounded reviewer, read-only, instructed to default to NOT-CLOSABLE under
uncertainty. It returned **NOT-CLOSABLE**, and it was right on both counts.

REAL, and blocking. The living contract for #617
(`charness-artifacts/spec/2026-08-14-issue-617-durable-lesson-session-bundle.md`) still
read `Status: delivered-unreleased` with the verbatim line "it still reproduces for its
reporter until S7 publishes". S7 did publish; nobody refreshed the status. Closing the
issue while its own designated contract asserts on its face that the bug still
reproduces is precisely the contradiction an issue-closeout floor exists to catch. The
parent had not established which side was stale — that was the reviewer's second, and
procedurally more important, finding: the premise was transcribed, not measured.

Both are now discharged by executed evidence rather than argument, and the commands are
named in the spec so a later reader re-runs them instead of trusting the line.

REAL, and acted on. Requirement (c) was genuinely two-thirds met. `main()` in
`open_lesson_session.py` called `open_session`, which has always RETURNED `bundle_path`,
and discarded it — so an agent that ran the documented command learned the lesson bytes
but never where they were frozen, which is the exact reread path the issue exists to
provide after compaction. Fixed here, on stderr rather than stdout: stdout bytes are
digest-bound to the bundle, so announcing the bundle on stdout would make every receipt
the command writes fail its own digest check. The test asserts BOTH streams, because
choosing the wrong one is the failure mode.

REAL, and NOT fixed — carried as a named residual rather than silently closed over. No
SHIPPED surface tells a consumer to cite the session id and bundle path in the work
artifact, while the shipped retro reference instructs retro to recover them "from the
affected work's durable artifact". The retro third of (c) works; the work-workflow third
is an instruction gap in the skill packages. This is the reason the closure is being put
to the operator rather than taken unilaterally.

OVER-WORRY, and left alone. The reviewer's atomicity caveats — `_write_once` does not
fsync the parent directory after `os.replace`, and its `path.exists()` guard is TOCTOU-
racy — are real properties but not #617 defects: the crash asymmetry is fail-closed in
the direction that matters (a bundle without a receipt cannot be scored; a receipt whose
bundle is missing or altered is refused on re-read), and duplicate session ids are
refused upstream. Recorded, not acted on.

NOT a regression, but stated out loud. A consumer repo that opened lesson sessions on a
pre-bundle charness now gets `invalid-receipt` for every old receipt, permanently. That
is the deliberate consequence of the issue's own "one current receipt contract, no
migration command or compatibility branch", not an unrequested side effect. It is now
written into the spec's non-claims so a consumer meets it as a documented decision.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/spec/2026-08-14-issue-617-durable-lesson-session-bundle.md | action: fix | note: status read `delivered-unreleased` and "still reproduces for its reporter" after S7 published; corrected to `released` with the four re-runnable containment commands named inline
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/open_lesson_session.py | action: fix | note: main() dropped the `bundle_path` open_session returns, so the command never referenced the bundle as #617 requires; announced on stderr because stdout is digest-bound
- F3 | bin: act-before-ship | evidence: strong | ref: tests/test_lesson_session_emission.py | action: fix | note: the CLI test's fake returned `{}` and asserted no output; now asserts the path on stderr AND an empty stdout, and fails when the stream is swapped
- F4 | bin: valid-but-defer | evidence: strong | ref: skills/public/achieve/SKILL.md | action: file-issue | follow-up: deferred docs/handoff.md#next-session | note: no shipped surface instructs citing session id and bundle path in the work artifact, while the shipped retro reference depends on that citation existing
- F5 | bin: valid-but-defer | evidence: moderate | ref: scripts/lesson_evaluation_continuity_lib.py | action: defer | note: `_write_once` fsyncs the temp file but not the parent directory, so the rename is not crash-durable on power loss; out of #617's scope
- F6 | bin: over-worry | evidence: weak | ref: scripts/lesson_evaluation_continuity_lib.py | action: defer | note: the `path.exists()` guard is TOCTOU-racy against `os.replace`; duplicate session ids are already refused upstream by `declare_session`

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: subagent_type=bounded-reviewer, no host addressing name
- Host exposure state: applied
- Application state: host-confirmed: one bounded-reviewer spawn returned findings inline
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- No prepare_packet was consumed; the reviewer was given the issue's verbatim
expected-behavior clauses and an explicit file scope inline, plus an instruction to
default to NOT-CLOSABLE under uncertainty. -->

## Boundary Ownership

- Producer: the lesson-session emission path and its shipped plugin copy
- Consumer: a consuming repo whose agent reopens a frozen bundle after compaction
- Owning surface: repo-python and skill-packages
- Verdict: escalated-to-issue-spec

The emitter half is owned correctly: `open_lesson_session.py` produces the bundle and
the path, and the shipped retro reference consumes them. The instruction half is not.
The shipped retro reference tells retro to recover the session id and bundle path
"from the affected work's durable artifact", but the surface that would make a work
artifact CARRY that citation is the `achieve`/work skill package, whose owner is out of
this change's scope. Encoding the instruction here would put a consumer-facing contract
in the wrong package, so F4 is escalated rather than written in.
