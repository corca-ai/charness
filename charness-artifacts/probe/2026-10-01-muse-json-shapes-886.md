# Muse `--json` Shape Probe — #886 (derived, 2026-10-01)

Binary: `muse` 1.4.1 (`1.4.1-R4503.1`). Three advisory probes measured the
envelope shapes `scripts/task_run/task_run_muse_events.py` consumes. This
record carries shapes and counts only — no prompts, session ids, or
provider credentials.

## Success probe (echo provider)

- `run.output.delta` ×1: `payload.text` carries streamed agent text.
- `run.terminal.completed` ×1: `payload.kind == "run_terminal"`,
  `payload.terminal == "completed"`, `payload.text` is the full report,
  `payload.reason` null.
- Exit 0. stderr: workspace notices only.

## Failure probe (meta provider, unreachable base URL)

- `task.lifecycle.status` ×8: `event.message` plus
  `event.details.phase` in `opening_stream` / `retry_scheduled` /
  `stream_failed`; `external_attempt` facets carry `attempt`,
  `max_attempts`, `operation`, `system`, `error_kind` (`transport`,
  `transport_connect_unreachable`), `retry_delay_ms`, `next_attempt`.
- `task.lifecycle.failed` ×1: `event.reason` names the transport cause.
- `run.terminal.failed` ×1: `payload.reason` repeats the cause,
  `payload.text` empty.
- Exit 1. stderr adds `run ended with Failed: <reason>`.

## Real lane probe (`charness task run --executor muse`, require-change)

- `run.output.delta` ×6 streamed the agent text (markers inside);
  `run.terminal.completed` ×1 carried the identical full report.
- `task.lifecycle.status` ×10, all `opening_stream` / `stream_succeeded`.
  Success facets set `error_kind: "stream_succeeded"` — outcome token, not
  failure proof; the consumer excludes it (replay-verified).
- Receipt: `lane_progress` and guard `last_phases` all three markers,
  `first_scoped_diff.observed` true with the real diff, `full-report.log`
  the terminal text (150 bytes), raw JSONL (144 lines) in
  `muse.events.log`, `stream_diagnostics.cause_status == "not-applicable"`.

## Non-claims

- Shapes are pinned to the probed binary; a newer binary may add
  envelopes. Unknown envelopes degrade to unobserved fields (hostile
  transcript test), never to a crash.
- No claim about provider retry causality beyond what the binary emits:
  when Muse names no cause, the receipt records `unavailable-upstream`
  instead of manufacturing one.
