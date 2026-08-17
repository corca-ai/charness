# Resolution Critique — issue 633 verify-and-close
Date: 2026-08-18

## Decision Under Review

Close [#633](https://github.com/corca-ai/charness/issues/633) as fixed, on the strength
of the S6 repair already on main, re-proven this session by executing the issue's own
reproductions rather than reading the code as repaired.

## Failure Angles

Raised by the bounded fresh-eye reviewer, not the author:

- **Coverage of every claim, not the headline one.** The issue names three harms
  (grammar acceptance, counted-before-checked, write-time acceptance of a real `none`
  session). Each maps to an executed refusal: grammar refusal in
  `lesson_evaluation_continuity_lib.py`, a `reserved-session-id` violation raised
  BEFORE `status_counts` increments in `lesson_evaluation_reconcile_lib.py`, and
  `_replay_sessions` refusing the reserved id at write time — the last also enforced
  pre-persist by `record_lesson_session.py`.
- **Sentinel drift.** `RESERVED_SESSION_ID` is defined once (`lesson_ledger_lib.py`)
  and imported by every consumer, including both plugin-mirror copies, which the
  reviewer verified rather than assumed.
- **False-close risk: a refused row silently leaving the denominator.** The reviewer
  traced `collect_dispositions` converting parse refusals into `invalid-disposition`
  violations, but found no test pinning it.

## Counterweight Pass

- The reviewer's two minors do not reopen the bypass. (1) The SessionStart hook's
  copied `_SESSION_ID` regex in `session_start_lesson_context.py` would suggest
  `--session-id none` if a host handed it that literal; the ledger's pre-persist replay
  refuses it loudly, so the harm is a UX dead-end, not a bypass. (2) The production
  lane's invocation of `check_lesson_evaluation_continuity.py` was read, not executed
  standalone; the CLI's `main()` has its own argv-level exit-code tests, and this
  session watched the live gate exit 1 on this repo's own open receipt — the same
  entrypoint.
- Verify-and-close is honest here because the reproductions were EXECUTED: both issue
  payloads refused at the grammar, the reserved-id row refused before counting, and the
  write-time replay refusal observed — none of it inferred from diff reading.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/test_lesson_evaluation_contract_boundaries.py | action: fix | note: no test pinned that a refused disposition becomes an `invalid-disposition` violation instead of leaving the denominator; pin added as `test_void_disposition_becomes_a_red_violation_not_a_dropped_row`, passing.
- F2 | bin: valid-but-defer | evidence: moderate | ref: scripts/session_start_lesson_context.py | action: document | note: the hook's copied `_SESSION_ID` regex lacks the reserved-id exclusion, so a host payload of literally `none` yields a suggested declare command the ledger then refuses loudly — UX dead-end, not a bypass; recorded for the session retro's sibling axis.
- F3 | bin: over-worry | evidence: weak | ref: scripts/check_lesson_evaluation_continuity.py | action: defer | note: standalone bad-disposition run through `main()` not executed (fixture needs a full valid ledger cohort); argv-level exit-code tests plus the live gate exiting 1 this session cover the same entrypoint.

## Reviewer Tier Evidence

- Requested tier: high-leverage (repo default for issue closeout review).
- Requested spawn fields: subagent_type=bounded-reviewer, unnamed one-shot spawn, no
  model/effort override (session-inherited).
- Host exposure state: applied
- Application state: host-confirmed: typed `bounded-reviewer` spawn accepted and the
  reviewer ran with the read-only toolset (Read/Grep/Glob only, per its own envelope
  report).
- Delivery state: findings-received

## Reviewed Input Identity

<!-- No packet was consumed: this critique reviews a verify-and-close decision over
repo state at f01a9bfcc, not a prepared packet. -->

## Boundary Ownership

- Producer: `lesson_ledger_lib.py` mints session ids and owns the reserved-id refusal.
- Consumer: `lesson_evaluation_reconcile_lib.py` renders the continuity verdict and
  re-derives the refusal rather than trusting the parser.
- Owning surface: lesson-evaluation continuity gate (scripts layer).
- Verdict: owned-correctly

## Fresh-Eye Satisfaction

`parent-delegated`. One bounded reviewer, spawned unnamed as `bounded-reviewer`, read
the three fixed surfaces, both test files, and both plugin mirrors; verdict CLOSE-SAFE.
Boundary fingerprint verify around the round: `ok: true`, `drift: []`
(window w-20260817T225039Z-916805). The added pin test was written by the parent AFTER
the reviewer returned and is inside the closeout commit; it is author-attributed work
acting on a reviewer finding, not reviewer-approved code.

## Non-Claims

- No claim that the lesson-evaluation loop's other checks are sound; only the #633
  bypass class is examined here.
- No claim about consuming repos still running a pre-fix installed copy; the fix
  reaches them by upgrade, not by this close.
