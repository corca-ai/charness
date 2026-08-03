# Critique Review
Date: 2026-08-06

Resolution critique for issues #487, #488, #489, #490.
Goal: [2026-08-06-make-a-verdict-state-the-scope-it-measured.md](../goals/2026-08-06-make-a-verdict-state-the-scope-it-measured.md)

## Decision Under Review

Whether the shipped work for #487, #488, #489 and #490 resolves what each issue
REPORTED, and whether anything is about to be claimed that the evidence does not
support. Not a re-review of the code — three of the four already had two bounded
rounds each.

## Failure Angles

- The fix addresses a nearby thing rather than the reported condition.
- A part of the issue is left unfixed and a close silently drops it.
- The close body claims a proof level the evidence does not reach (production,
  a consumer repo, a channel that was never read).
- A `## Final Verification` non-claim contradicts closing one of them.

## Counterweight Pass

Real blockers: the unread CI channel for two of the four, and #487's unswept
sibling helper — both concrete, both fixable before the flip. Over-worry, raised
and not folded: the `mutation_testing` nested-sub-key coarseness was considered as
a reason to hold #489 open and rejected — #489 reported `coverage_floor_policy`,
whose refilled keys are top-level and fully detected; the nested case
under-reports and never over-reports. It was filed (#493) rather than blocking.

## Verdicts as returned


| Issue | Verdict | Why |
| --- | --- | --- |
| #490 | CLOSABLE | The reported condition is what the test bites on; `scope_not_checked` + multi-clause reason mean the verdict no longer reads as a whole-artifact claim. |
| #488 | CLOSABLE, conditional on a CI re-read | `unanalyzed_changed_pool_files` now reaches the byte; the ordering hazard is fixed and commented; a non-opted-in label falls to FAIL not PASS, so no surviving green. |
| #489 | CLOSABLE | The issue's own pasted reproduction is a test, plus two further spellings and a non-regression control. The operator-chosen direction was the one taken. |
| #487 | **NOT-CLOSABLE as scoped** | `upsert_goal.py` has the same argv channel, was named in the goal's own `## Boundaries`, and the stop condition required the remaining sweep be RECORDED. It was not. |

## Claims it struck, and what was done

1. **"9 required sections" (#490).** The issue body itself miscounted — 9 was the
   TOTAL (7 of 11 required + 2 of 3 portability), already corrected in a comment.
   Repeating it would re-assert the corrected thing. **Struck from the close body.**
2. **Any production-proof claim for exit 4 (#488).** It has never fired on a real
   push; every push this session had a fully-analyzed changed set. **The close says
   "proven by tests and a subprocess run".**
3. **"names every refilled sub-key" (#489).** It names every refilled TOP-LEVEL
   sub-key. **Reworded, and the residual filed as #493.**
4. **"the prose-through-argv channel is closed for the `achieve` helpers"
   (plural, #487).** The evidence supports one helper. **#487 is closed on
   `append_slice_log.py` ONLY, and the remaining channel is filed as #494.**

## Blocking findings, and their resolution

- **The `## Final Verification` non-claim said remote CI was confirmed for only 2
  of 6 commits, and pointed at `## Coordination Cues` for the final read — which
  did not contain one.** Resolved: `94d2b74b`, the HEAD carrying all four fixes,
  reads `completed/success` on BOTH check-runs through the check-runs API, and
  that read is now recorded in `## Coordination Cues`. The intermediate SHAs'
  mutation mirrors are `cancelled` because the next push superseded them — the CI
  system cancelling its own in-flight run, not a failure.
- **`## Coordination Cues` had no `Issue closeout:` line at all.** Added.
- **The `mutation_testing` nested-sub-key coarseness had no tracked home**, living
  only in a code comment while the goal's other residuals got issues. **Filed as
  #493.**
- **A live contradiction introduced by slice D's own repair:**
  `references/goal-artifact.md` carried the new rule ("pass prose through
  `--fields-file`, not these flags") directly above an example calling
  `upsert_goal.py --goal-body "..."`, a helper with no `--fields-file`. The
  reference forbade a form and then demonstrated it. **Fixed in both copies**, and
  the underlying helper gap is #494.

## What this critique cost, honestly

It refused two of four closes and produced two new issues (#493, #494) plus one
doc repair. Both refusals were on the same axis: **the fix stopped at the surface
the issue named, and the sibling named in the goal's own scope was not swept.**
That is the third instance of that axis in this goal (#489 → #493 is the same
shape one level down).

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/goals/2026-08-06-make-a-verdict-state-the-scope-it-measured.md | action: fix | note: `## Final Verification` said CI was confirmed for 2 of 6 commits and pointed at `## Coordination Cues` for the final read, which held no such read and no `Issue closeout:` line at all
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/achieve/scripts/upsert_goal.py | action: fix | note: #487's close as scoped would drop the sibling helper named in the goal's own Boundaries; either repair it or narrow the close and file it
- F3 | bin: bundle-anyway | evidence: moderate | ref: scripts/quality_bootstrap_lib.py | action: file-issue | note: the `mutation_testing` nested-sub-key coarseness had no tracked home while the goal's other residuals got issues | follow-up: https://github.com/corca-ai/charness/issues/493
- F4 | bin: act-before-ship | evidence: strong | ref: skills/public/achieve/references/goal-artifact.md | action: fix | note: the reference carried the new rule directly above an example demonstrating the form it forbids, for a helper with no alternative
- F5 | bin: over-worry | evidence: moderate | ref: scripts/run-quality.sh | action: defer | note: a residual false-green was considered for the new exit 4; checked and rejected — a non-opted-in label falls to FAIL, not PASS

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (typed read-only subagent; Read/Grep/Glob only).
- Requested spawn fields: subagent_type=bounded-reviewer, one-shot, no addressing name.
- Host exposure state: applied
- Application state: host-confirmed: the reviewer reported its envelope bound with only Read/Grep/Glob exposed and no Bash/Edit/Write/Agent.
- Delivery state: findings-received

## Boundary Ownership

- Verdict: escalated-to-issue-spec

Two of this critique's findings were producer/consumer boundary problems, and
both were escalated rather than absorbed into the close. F2: the prose-through-argv
channel is a CONSUMER-facing contract of the `achieve` helpers, and `#487`'s fix
covered one producer (`append_slice_log.py`) while the other (`upsert_goal.py`)
kept the old contract — escalated to issue #494 rather than papered over by a
close claiming the plural. F3: `_mark_subkey_refills` is the producer of a refill
account that consumers read, and its granularity stops one level above the next
instance — escalated to issue #493.

The remaining findings (F1, F4) are single-surface: the goal artifact's own
closeout evidence, and a reference file contradicting itself. Both were fixed in
place by the surface that owns them.

## Fresh-Eye Satisfaction

parent-delegated — spawned by the parent as a typed `bounded-reviewer` and run
BEFORE the close call, not after it. Boundary snapshot taken before the spawn and
verified clean on return, before any parent write.
