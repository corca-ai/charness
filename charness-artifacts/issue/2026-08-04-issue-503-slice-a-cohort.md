# Issue #503 — Slice A cohort and ownership record

Date: 2026-08-04
Status: Slice A complete; Slice B decision required
Issue: https://github.com/corca-ai/charness/issues/503

## Decision under review

Select one comparable local closeout-cost cohort and name the producer,
consumer, and decision owner before choosing an optimization. This record is
not an issue closeout and does not authorize changing, skipping, rescheduling,
or weakening a proof gate.

## Selected cost cohort

The selected unit is one exact gate-runtime key, not a mixture of seconds and
over-slice run length:

- **Source:** `.charness/usage-episodes/closeout_telemetry.jsonl`, the local
  gitignored closeout stream read by
  `skills/public/retro/scripts/mine_closeout_telemetry.py`.
- **Population:** all retained records in the current stream with
  `event_type=closeout_telemetry` and `schema_version=1`.
- **Measurement snapshot:** Slice A captured 1,325 retained records through
  `2026-08-03T23:56:26Z`. A later live detail replay after the implementation
  emitted one additional record, so the current stream is 1,326 records
  through `2026-08-04T01:16:44Z` (949 `completed`, 248 `failed`, 129
  `blocked`); the selected 16-entry cohort is unchanged.
- **Population window:** `2026-06-13T11:33:19Z` through `2026-08-03T23:56:26Z`.
- **Population denominator:** 1,325 retained, valid records; 1,325 physical
  lines; zero malformed lines; all 1,325 lines are `closeout_telemetry`.
  Statuses across the population are 948 `completed`, 248 `failed`, and 129
  `blocked`.
- **Cohort query:** an entry in `gate_runtime.over_budget` with exact
  `phase=verify`, exact command
  `pytest -q -m 'not release_only' tests/quality_gates tests/control_plane tests/test_*.py`,
  and `over_budget=true`.
- **Cohort window:** `2026-06-13T11:57:31Z` through
  `2026-06-15T21:54:08Z`.
- **Cohort denominator:** 16 matching over-budget entries / 1,325 retained
  population records (12 top-level `completed`, 4 `failed`). This is not a
  claim of 16 successful suite executions: the stream does not carry command
  exit status or suite pass/fail identity.
- **Budget:** 120.0 seconds per executed gate entry.
- **Elapsed-seconds summary:** 16 numeric observations; total 6,257.15s;
  mean 391.07s; median 447.03s; minimum 242.43s; maximum 475.46s; aggregate
  excess over the 120s budget 4,337.15s.
- **Exclusions:** every retained record without the exact matching entry is
  excluded; malformed and non-`closeout_telemetry` lines are excluded (none
  occurred in this retained file). Other commands and the separate
  `over_slice` finding are not folded into this seconds cohort.
- **Retention:** the emitter rotates the stream with a bounded size and one
  backup (`scripts/slice_closeout_telemetry.py`), but no backup file is present
  in the current checkout. Older/lost records and the full historical window
  outside the retained file are therefore unknown, not zero.
- **Unavailable provenance:** the schema records timestamp, status, advisory,
  over-slice, and slice-churn fields, but no runner/profile, command exit code,
  or run identity. No historical runner/profile attribution is made here.

The separate over-slice signal remains its own cohort: 37 occurrences with a
peak trailing artifact-only run of 4. Its unit is occurrences/run length, not
seconds, so it is not ranked against this gate-runtime cohort.

## Ownership map

| Boundary | Current owner and evidence | What it can honestly decide |
| --- | --- | --- |
| Verdict producer | `scripts/slice_closeout_advisories.py` evaluates executed command elapsed time and attaches `gate_runtime_advisory`; `scripts/run_slice_closeout.py` calls it after execution | Whether an executed closeout gate entry exceeded the configured advisory budget |
| Transport/persistence | `scripts/slice_closeout_telemetry.py` reuses that payload and appends a schema-1 record; it is called on stopped and completed closeout paths | Preserve the local recurrence evidence, subject to bounded rotation and unknown lost history |
| Aggregator | `skills/public/retro/scripts/mine_closeout_telemetry.py` groups by exact `(phase, command)` and marks recurrence at `recur_min >= 2` | Surface a recurring local cost and route it to tracked work rather than the decaying lesson digest |
| Final consumer | The Charness maintainer/operator reading the miner output and the tracked #503 decision record | Decide whether to retain the proof cost, run a bounded proof-preserving optimization experiment, or record why no safe change exists |
| Decision owner for #503 | Charness quality/achieve maintainer — the operator of this goal — until a later record assigns a narrower gate implementation owner | Own the decision record and reopen/retain action; telemetry alone does not assign a code owner |

The current advisory text says to route a finding to the “gate-implementation
owner,” but the telemetry has no field that identifies that person or module.
That phrase is a routing hint, not evidence of an assigned owner.

## Preservation boundary for Slice B

Any proposed action must preserve all of the following:

1. A failed closeout remains visible as failed; a passing gate remains distinct
   from an over-budget advisory.
2. The operator receipt and recovery path remain available even if telemetry
   emission or a warning fails.
3. The selected cohort continues to distinguish exact phase/command entries,
   status, budget, elapsed seconds, and retained-record scope.
4. No local result is narrated as remote CI, release, cross-repo, or live proof.

The safe candidate class is an advisory decision/report surface that records
the cohort contract, an owner, a preservation invariant, candidate actions, and
a measurable reopen trigger. Recurrence alone is not permission to weaken or
move the gate.

## Evidence and non-claims

- The local miner was run with:
  `python3 skills/public/retro/scripts/mine_closeout_telemetry.py --repo-root .`.
- The raw stream was inspected directly for the exact query and elapsed summary.
- Quality option probes were run with
  `inventory_ci_recoverable_gates.py --repo-root . --detail`,
  `render_runtime_summary.py --repo-root . --detail`, and the standing-test and
  structural-waste inventories. They remain advisory; token matches do not
  prove equivalent CI coverage.
- A delegated fresh-eye cohort review returned `parent-delegated` findings;
  its shared-worktree fingerprint verified clean before this record was written.
- This record does not prove that the gate is wrong, that any optimization is
  safe, that the cost is cross-repo, that a particular runner/profile produced
  the historical entries, or that future relief will occur.
- No #496 predicate recommendation is made here.

## Slice B handoff

Compare at least these reversible options against the preservation boundary:

1. Keep the gate and add only a richer decision/report receipt around the
   exact cohort; reopen after a new comparable window.
2. Run a bounded proof-preserving optimization experiment against a named
   lower-layer seam, with a before/after cohort and a separate correctness
   channel; do not change the standing gate yet.
3. Record no safe change yet if the available evidence cannot identify a
   proof-preserving seam, with the option comparison and a measurable reopen
   trigger.

The next slice must select one option and name its owner and falsifier before
implementation.
