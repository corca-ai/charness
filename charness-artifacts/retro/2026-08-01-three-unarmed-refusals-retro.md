# Session Retro
Date: 2026-08-01

## Context

Goal under review:
[2026-08-01-get-the-operator-call-on-the-three-unarmed-refusals-d46-adap.md](../goals/2026-08-01-get-the-operator-call-on-the-three-unarmed-refusals-d46-adap.md).

The three-unarmed-refusals goal: handoff chunked routing over the live backlog
selected `chunk-c`, `achieve` shaped it, the operator answered three deferred
decisions, and three implementation slices plus a closeout ran against D46, D48,
and D47. Reviewed here because the goal's shape — an operator decision session
whose premises were destroyed twice by review — is the thing that should change
the next session, not the code it produced.

## Window

`8c3b3446..HEAD` on 2026-08-01. Four commits of goal work on top of yesterday's
sweep closeout, plus the goal artifact and one new probe.

## Evidence Summary

- The goal artifact's own Slice Log and Plan Critique Findings, written as the run
  went rather than reconstructed.
- Five bounded fresh-eye reviews (one plan critique, two rounds on slice 2, two on
  slice 3, one on slice 1), each with a `reviewer_boundary_fingerprint` window that
  verified `clean`.
- Executed before/after comparisons on a scratch worktree for D48, and a recorded
  probe (`charness-artifacts/probe/2026-08-01-inventory-marker-rule.json`) with
  both the buggy and corrected runs for D47.
- Host-log probe: measured thread-wide, not scoped to this goal —
  293 function calls, 34 patch applications, 6 subagent spawns, 0 context
  compactions, 443 token snapshots (point-in-time, not a cumulative total).

## Waste

**The dominant waste was building three things that had to be reverted**, all in
slice 2: lane-asymmetry inference, run-planner routing, and gating the resume
path. None was wrong-headed; each was refuted by a fact I could have read first.
Lane inference invented publishing semantics the repo does not author. Planner
routing forgot that the planner runs BEFORE sync, so absence there is the ordinary
fresh-checkout state. The resume gate broke 18 tests because every resume fixture
uses a repo with no generated tree. All three were discovered by running the
tests, which is the cheap channel — but each cost a full build-then-delete cycle.

**Second waste: a silent no-op reported as a repair.** My fix to the arming
comment in `validate_inventory_consumption.py` used an exact-string replace that
did not match a mid-sentence line wrap. It failed silently, I recorded the surface
as repaired, and round 2 found the superseded numbers still shipping in the gate
that exists to defend the threshold. This is the only waste here that produced a
false claim rather than a slow path.

**Not waste, despite looking like it:** the five review rounds. Every round found
at least one blocker, and three of them found defects in my *claims* rather than
my code — which is exactly the class no same-agent pass catches.

## Critical Decisions

1. **Escalating instead of silently redesigning when the plan critique broke two
   of the operator's three choices.** D47's and D48's own "better repair" text was
   wrong; the entries had been recording an unbuildable remedy. Returning that to
   the operator cost one question and produced two reshaped slices that were
   actually buildable. Quietly substituting my own design would have shipped work
   the operator never chose.
2. **Moving D48's teeth to the publish boundary rather than into `drift`.** This is
   the north star applied literally: a read-only status call must not redden a
   consumer's un-shipped lane, but a publish is where a wrong answer escapes. It
   also made the "no toll" claim checkable, which is how round 2 later proved a
   version of it false.
3. **Reverting three built things rather than half-shipping them.** Each is now a
   named known gap with its reason, which is a better artifact than a partial
   guard whose limits nobody wrote down.
4. **Measuring D47 instead of arming or dropping it.** The measurement immediately
   earned itself: it showed the entry's hand-counted refusal figure was one high,
   and — after the regex bug — that my own first machine number was worse than the
   hand count it replaced.

## Trends vs Last Retro

The 2026-08-01 retro that precedes this one recorded "round 2 caught defects
created by round 1's own repairs in EVERY slice where it ran." That held again,
in both slices where round 2 ran, and this time the round-2 findings were
*sharper* than round 1's in one case: round 2 found that my round-1 repair had
recreated the exact toll the entry refuses, through a channel (`drift`, which the
run planner routes on) that I had just finished closing elsewhere.

The prior retro also recorded "run the dup-ratchet at the first edit, not at the
closeout aggregate" as a lesson that had failed to prevent itself twice. This
session ran it at the first edit in every slice. It fired four times and each
firing produced a real extraction rather than a late hard-block: the chunker's
`forward_carried_keys` / `entries_from_pipeline_payload`, and the measurement
scripts' `inventory_measurement_lib`. That lesson is now holding.

## Expert Counterfactuals

**Engelbart, `system-improving-itself` (the briefed lens).** Engelbart's point is
that the tool, the human, and the training are one system, and you improve the
system by improving how it improves itself. Applied here: I treated the five
review rounds as quality control on my output, when the higher-leverage read is
that they are the *measurement instrument for my own claim-making*. Three of the
five rounds found a defect in something I asserted rather than something I built —
a comment that claimed a branch was live when the probe beside it said zero, a
"repair" that never applied, a units swap that manufactured agreement. Engelbart
would not add a sixth round; he would ask what cheap check makes those three
classes self-refuting. Two exist and I did not use them: after any string-replace
edit, assert the old text is gone; and after writing a number into prose, grep the
repo for the superseded number. Both are seconds of work and both would have
caught real defects this session.

**Second lens: Gary Klein's premortem, on decision quality.** The two slices that
went sideways both began from a sentence in a deferred-decision entry that named a
repair. A premortem on "this repair ships and is wrong" would have asked, before
any code: *what would have to be true of the channel this repair reads?* For D48
that question is answerable in one command (`written_paths` names a directory) and
for D47 in one file read (the declared fields are ordinary English words). Both
were eventually answered by a reviewer, after I had built against them. The
generalizable move: when an artifact hands you a named remedy, verify the remedy's
premise before scheduling it, not while implementing it.

## Next Improvements

- **workflow — verify a string-replace landed.** After any exact-string edit to a
  file I do not immediately re-read, assert the superseded text is absent. The
  silent-no-op class produced the only false claim this session.
- **workflow — premortem a borrowed remedy.** When a deferred decision or issue
  names "the better repair", spend one command verifying its premise before
  shaping a slice around it. Two of three slices needed this.
- **capability — a superseded-number sweep.** When a number is replaced in a
  durable record, grep the repo for the old value. Round 2 found the stale figure
  in the gate comment, and I had already missed it in the sibling docstring and
  the dogfood record.
- **memory — the units rule.** A measurement that lands near an expected number
  invites narrating agreement. Record the unit before the value: "5 reviews" and
  "5 citations across 4 artifacts" are not the same claim.

## Sibling Search

The transferable pattern is **"a durable record names a remedy that cannot be
built as described"**, and it recurred twice in one goal (D47, D48). Scanned the
other deferred decisions for the same shape.

- **Axis: sibling artifacts.** `docs/deferred-decisions.md` carries 48 entries.
  D45 names a remedy ("moving the exemption to the adapter") whose premise is the
  same self-declaration channel D48 just found insufficient; it is cross-referenced
  by both D46 and D48 as precedent. Not verified this session — recorded as a
  candidate, not a finding.
- **Axis: sibling surfaces.** The sweep artifact
  (`charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md`) records
  proposed repairs per row in the same "the better repair is X" voice. Rows S15,
  S31, S36, S37, S111 are open and carry such text.
- **Decision:** `tracked issue` — the pattern is real, recurs, and is bigger than
  this goal. Structural pattern: a durable record's proposed remedy is stored as
  prose and never re-verified against the channel it reads, so a later session
  schedules work around a premise that was false when written. Triggering
  instances: D47 (the distinctiveness declaration cannot both impose a rule and
  spare the cited reviews) and D48 (`written_paths` cannot name two of the four
  surfaces). Destination: this repo — the record and its consumers are repo-local.

## Portable Candidate

Not portable — the pattern is about this repo's deferred-decision record format
and its consumers, and abstracting it would produce a generic "verify your
assumptions" skill with no teeth.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-01-three-unarmed-refusals-retro.md

## Goal Closeout Metrics

- Goal metric window: not_requested — not requested (no --goal-path); signals below are thread-wide pressure, not a per-goal total

### Measured (thread-wide, claude session scope)
- session: /home/hwidong/.claude/projects/-home-hwidong-codes-charness/09c89f96-8aca-4f08-9427-7dcb4a27c936.jsonl
- token snapshots: 448 (point-in-time, not a cumulative total)
- function calls: 297
- custom tool calls: 0
- patch applications: 34
- context compactions: 0
- subagent spawn/wait/close: spawn=6

### Proxy (activity shape, not measured cost)
- repeated broad gates: none
- repeated VCS commands: none

### Window filter
- status: not_applied; included 1021 of 1021 records

### Token availability (Claude host)
- available: message.usage.input_tokens/output_tokens present
