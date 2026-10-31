# Debug: final lane progress observation
Date: 2026-10-31

## Problem

The completed Muse receipt can omit the final `TESTING` phase from `progress_guard.last_phases` even when the terminal lane transcript includes it.

## Correct Behavior

After the executor exits and its output capture drains, the final guard receipt records the phases and scoped changes observable in its logs without enforcing running-lane stop rules.

## Observed Facts

The clean Git environment coverage run failed `test_muse_json_progress_reaches_receipt_with_terminal_report`: expected three phases, observed `CONTRACT-READ` and `EDITING`.
`scripts/task_run/task_run_execution.py` stopped the watch before closing the capture pipe; the last logged event could arrive after the last periodic poll.
The terminal transcript and `lane_progress` already contained `TESTING`.

## Reproduction

- `/tmp/charness-branch-clean-git.log` contains the failing coverage producer receipt and test assertion.
- The focused Muse fixture now emits all events without sleeps and asserts the final guard receipt and scoped diff.

## Candidate Causes

- The final event is missed between the last poll and pipe drain; the existing stop path has no final read.
- The structured parser discards the phase: disconfirmed by the same receipt's `lane_progress` containing the full phase list.

## Hypothesis

- A final observation after pipe drain records the missed phase without relying on scheduler timing; disconfirmer: the no-sleep Muse test fails its guard receipt assertion.

## Verification

- Confirmed: the no-sleep focused Muse test passed after the final observation was added.

## Root Cause

The receipt represented the last periodic sample rather than the drained terminal transcript, and the test attempted to guarantee polling with short sleeps.

## Invariant Proof

- Invariant: terminal guard observation follows capture drain, and never applies a live-only stop to an exited lane.
- Producer Proof: `task_run_execution._execute_codex` closes the stamping pipe before `observe_completion`.
- Final-Consumer Proof: the no-sleep Muse lane checks `progress_guard.last_phases` and its observed scoped diff.
- Interface-Shape Sibling Scan: both supported executors use this execution boundary and watcher.
- Non-Claims: incomplete capture remains separately reported by the existing capture receipt.

## Detection Gap

- `test_task_run_muse_stream_886.py` | timed sleeps allowed scheduler-dependent polling | remove sleeps and assert the terminal receipt.

## Sibling Search

- Mental model: the latest periodic sample always contains all events at process exit.
- same layer: watcher live stop | decision: leave live rules on periodic ticks | proof: completion ignores stop decisions.
- cross-file: capture pipe | decision: drain before terminal observation | proof: execution ordering and lane test.
- abstraction up: both executor transports | decision: use shared execution boundary | proof: `_execute_codex` owns both.
- specialization down: retry attempts | decision: each attempt uses its own watcher | proof: `task_run_attempts` constructs one per attempt.

## Seam Risk

- Interrupt ID: final-lane-progress
- Risk Class: none
- Seam: executor output capture to progress guard receipt
- Disproving Observation: terminal receipt misses an emitted phase after capture completes.
- What Local Reasoning Cannot Prove: external executor transport completeness.
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: no
- Next Step: impl
- Handoff Artifact: none

## Prevention

Exercise final receipt observation with immediate executor output rather than sleeps, and preserve capture completeness diagnostics.
