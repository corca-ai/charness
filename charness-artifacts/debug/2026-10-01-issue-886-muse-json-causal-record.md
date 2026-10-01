# Debug Record: issue 886 muse lanes miss progress and retry causes
Date: 2026-10-01

## Problem

Canonical `charness task run --executor muse` lanes receipted no phases
and no observed first scoped diff even when the lane edited files, and a
timed-out lane's only retry diagnostics were bare stderr lines with no
actionable cause.

## Correct Behavior

Supported muse intermediate events reach phase/progress receipts, real
scoped edits are observed per the documented guard contract, the final
artifact is the actual terminal report separate from its JSONL transport,
and retry/failure diagnostics preserve the provided cause or explicitly
name the upstream gap.

## Observed Facts

- `build_muse_args()` constructed fixed muse argv without `--json`.
- Probed on muse 1.4.1: without `--json`, lane stdout stays empty until
  the run ends; with `--json`, stdout streams JSONL envelopes.
- Phase consumers read stdout/stderr text, so empty stdout plus
  notice-only stderr yields zero markers and the no-progress budget
  never starts, even while the worktree changes underneath.
- `_result_delivery()` consumed complete stdout as the report.
- Bare stderr retry lines carried no HTTP status, error body, or cause;
  with `--json` the same retries surface as status events with
  `external_attempt` facets plus a terminal/task failure reason.

## Reproduction

- Run any require-change muse lane to timeout without `--json` and read
  `progress_guard.last_phases` (`[]`) and
  `first_scoped_diff.observed` (`false`) against a worktree the lane
  edited; compare with the repaired lane, which receipts all markers.
- `python3 /tmp/neg_control_886.py` replays a marker split across two
  delta chunks with accumulation disabled (`[]`) and enabled
  (`['CONTRACT-READ']`).

## Candidate Causes

- Candidate: the timeout is undersized for muse lanes. Disconfirmed by
  the issue's own successful lanes at the same budget.
- Candidate: the guard or phase parser drops muse markers. Disconfirmed:
  the consumers are correct; they were fed an empty transcript.
- Confirmed: the invocation never requested the structured transport,
  so intermediate output had no channel to the consumers.

## Hypothesis

- If the lane passes `--json` and the consumers accumulate delta text,
  extract the `run_terminal` report, and roll up status/terminal
  diagnostics, then timed-out lanes receipt partial phases, partial
  delivery, and retry causes. Disconfirmer: a fake-muse timeout lane
  whose receipt lacks any of the three.

## Verification

- Result: resolved. Fake-muse JSONL lanes prove argv, split-chunk
  phases, terminal delivery, timeout partials, no-progress stop, and
  diagnostics; hostile transcripts degrade to unobserved fields; a real
  provider lane completed with live phase relay and a clean receipt;
  the full read-only lane passed 85/85.

## Root Cause

The muse invocation and its consumers were specified for a plain-text
transport the binary only emits at run end. Intermediate agent output
existed solely inside the executor process, so every downstream
consumer — live guard, terminal receipt, diagnostics — correctly
reported the nothing it was given.

## Invariant Proof

- Invariant: when a muse lane runs, its receipted phases, delivery, and
  stream diagnostics must derive from the executor's structured output,
  not from an empty transcript.
- Producer Proof: `muse exec --json` emits `run.output.delta`,
  `task.lifecycle.status`, and `run_terminal` envelopes on stdout.
- Final-Consumer Proof: the timeout-shaped fake lane and the real lane
  receipts carry phases, reports, and diagnostics read back from
  `result.json`.
- Interface-Shape Sibling Scan: the codex executor already consumes its
  `--json` transport plus a last-message file; both `lane_progress`
  call sites flow through the single fixed transcript reader.
- Non-Claims: provider retry causality beyond what the binary emits is
  not established; a binary that stays silent yields an explicit gap
  marker, not a cause.

## Detection Gap

- executor-lane tests | fakes printed plain text, so no test fed the
  consumers a structured muse transcript | add fake-muse JSONL lanes
  covering argv, split phases, terminal delivery, timeout partials, and
  diagnostics.
- real-binary evidence | envelope shapes were assumed, never measured |
  pin the consumed shapes to a measured probe record and degrade
  unknown envelopes to unobserved fields.

## Sibling Search

- Mental model: an empty lane transcript means the executor produced
  nothing worth receipting, even when the worktree changed underneath.
- same layer: codex lane transport | decision: not a sibling, already
  correct | proof: `--json` plus last-message extraction with
  passing lane tests.
- abstraction up: all executor output consumers | decision: fixed once
  at the shared transcript reader | proof: both `lane_progress` call
  sites flow through `_transcript_lines`.
- specialization down: self-review codex invocation | decision: not a
  sibling | proof: codex-only with `--json` plus last-message, moved
  verbatim.
- cross-file: `task_run_attempts` log rotation and ordered-executor
  fallback replace rather than attribute diagnostics; pre-existing
  shapes, deferred to their own slices.

## Seam Risk

- Interrupt ID: issue-886-muse-json-observability
- Risk Class: none
- Seam: executor structured transport to lane receipt consumers
- Disproving Observation: timeout-shaped and hostile-transcript lanes
  receipt phases, partial delivery, and diagnostics or explicit gap
  markers with no crashes.
- What Local Reasoning Cannot Prove: future binary envelope drift
  beyond the measured 1.4.1 shapes.
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/critique/v8146-critique.md

## Prevention

Consume the executor's structured transport at the shared reader,
extract terminal delivery separate from that transport, retain
retry/failure diagnostics with an explicit gap marker, pin new lanes
with fake-executor boundary tests, and degrade unknown envelopes
instead of crashing on them.
