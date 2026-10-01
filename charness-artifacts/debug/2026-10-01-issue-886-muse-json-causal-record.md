# Debug Record — #886 muse lanes miss intermediate progress and retry causes

Date: 2026-10-01

## Symptom

Canonical `charness task run --executor muse` lanes receipted
`last_phases: []` and `first_scoped_diff.observed: false` even when the
lane edited files; a timed-out lane's only retry diagnostics were bare
`muse: retrying meta model stream ... (attempt N/M)` stderr lines with no
cause.

## Causal chain (measured)

1. `build_muse_args()` constructed fixed muse argv without `--json`.
   Probed on muse 1.4.1: without `--json`, lane stdout stays empty until
   the run ends (final text only); with `--json`, stdout streams JSONL.
2. Phase consumers (`lane_progress`, live guard) read stdout/stderr text.
   Empty stdout plus notice-only stderr yields zero markers, so the
   300 s no-progress budget never starts and the guard never observes a
   scoped diff — even while the worktree changes underneath.
3. `_result_delivery()` consumed complete stdout as the report, so
   switching the transport to JSONL without a terminal extractor would
   have delivered raw envelopes instead of the report.
4. Retry notices went to stderr as bare lines (no HTTP status, error
   body, or cause). With `--json`, the same retries surface as
   `task.lifecycle.status` events with `external_attempt` facets
   (`error_kind`, attempts) plus a terminal/task failure reason —
   the actionable cause the receipt was missing.

## Fix direction (chosen)

Repair invocation and consumers together: pass `--json`, accumulate
`run.output.delta` text for phase parsing, extract the `run_terminal`
report separate from the JSONL transport (raw kept in `muse.events.log`),
and retain per-lane `stream_diagnostics` with an explicit
`unavailable-upstream` marker when Muse provides no cause. No timeout
increase, no wrapper, no argument injection.

## Evidence

- `charness-artifacts/probe/2026-10-01-muse-json-shapes-886.md`
  (envelope census from success/failure/real-lane probes)
- Real provider lane `muse-886-proof5`: completed with live
  `PROGRESS [muse] phases=CONTRACT-READ,EDITING,TESTING`, observed
  first scoped diff, terminal delivery, clean diagnostics
- `tests/charness_cli/test_task_run_muse_stream_886.py` (fake-muse
  JSONL boundary proof incl. the timeout shape)
