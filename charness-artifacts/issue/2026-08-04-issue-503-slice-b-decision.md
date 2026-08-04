# Issue #503 — Slice B decision and reversible report surface

Date: 2026-08-04
Status: Slice B decision complete; Slice C implementation proof in progress
Issue: https://github.com/corca-ai/charness/issues/503

## Selected action

Select option 1 from the Slice A comparison: keep the standing proof gate and
add an opt-in, read-only detail receipt to the existing local telemetry miner.
The receipt audits the currently readable schema-1 population, reports the
exact phase/command cohort with parent-record statuses and finite elapsed /
budget summaries, and states what the stream cannot prove. It changes no gate,
emitter schema, CI placement, scheduling, or verdict condition.

The decision owner is the Charness quality/achieve maintainer operating this
goal. The consumer action is to run:

    python3 skills/public/retro/scripts/mine_closeout_telemetry.py --repo-root . --detail

Then record one of: retain the current proof cost, open a bounded
proof-preserving experiment with a named seam and separate correctness
channel, or record that no safe change is identified. The report itself does
not choose among those actions and cannot assign a historical runner/profile
owner.

## Option comparison

| Option | Decision | Evidence and reason |
| --- | --- | --- |
| Richer local report receipt | **Selected** | The existing miner is the read-only derivation boundary; an opt-in receipt makes denominator, retention, status, finite elapsed values, unknown provenance, and over-slice unit separation rerunnable without changing proof behavior. |
| Bounded optimization experiment | Deferred | Local probes identify possible CI/test-economics candidates, but no named lower-layer seam with equivalence proof and a separate correctness channel is established by the current cohort. |
| No-safe-change record only | Deferred as the immediate surface | The absence of a safe experiment is itself recorded, but a durable receipt is needed to make the next retain/experiment/no-change decision repeatable rather than prose-only. |

## Preservation and falsification

The action is falsified if the detail path changes default miner output,
re-admits unsupported or malformed records, emits non-finite elapsed values,
counts entries as parent closeouts, mispairs elapsed seconds with budgets, or
renders a missing/unreadable stream as clean zero. Focused fixtures exercise
those negative controls; the generated plugin mirror is required to remain
byte-identical to the public source.

The action does not claim local relief yet. The current receipt is a decision
surface, not an optimization: its expected cost relief is **0 seconds
measured** until a later comparable retained window demonstrates otherwise.

## Reopen trigger and boundary

Reopen the option comparison when a later current-readable retained window
contains at least two occurrences (`recur_min >= 2`) of the same exact
`(phase, command)` key, then rerun the owner decision against that window.
Do not use historical totals, cross-machine relief, over-slice run length as
gate seconds, or recurrence alone to authorize weakening, skipping,
rescheduling, or moving proof. Rotation and lost history remain unknown.

No predicate recommendation is made for #496. Its hollow-refill predicate
must be reproduced and decided independently in the later #496 slices.

## Proof recorded for this slice

- Focused telemetry-miner tests pass, including default-output parity, mixed
  input audit, missing stream, schema filtering under `--recur-min`,
  parent-record status counting, non-finite rejection, budget pairing, and
  source/plugin mirror equality.
- The Slice B replay captured a 1,325-record retained population; a later live
  replay reports the current 1,326-record population through
  `2026-08-04T01:16:44Z` (949 completed, 248 failed, 129 blocked). Both report
  the same 16-entry selected cohort, 12 completed and 4 failed parent records,
  and 4,337.15 seconds of finite paired excess over the 120-second budget.
- The bounded fresh-eye review round found no new unreviewed blocker after the
  first repair; its four semantic repairs were applied. Because the repository
  caps this verdict-logic review at two rounds, those round-two repairs are
  recorded as accepted-unreviewed and remain covered by the focused negative
  controls and final broad proof.
