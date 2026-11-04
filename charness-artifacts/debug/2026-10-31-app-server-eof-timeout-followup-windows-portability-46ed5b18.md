# Debug: app-server EOF versus timeout
Date: 2026-10-31

## Problem

The app-server EOF test reported `timed out while waiting for Codex app-server response` under load instead of `exited before returning a response`.

## Correct Behavior

Given an exited child with no response, when the response wait reaches its deadline, then the refresh result reports the exit; a child still running at the deadline reports a timeout.

## Observed Facts

The fake exits only after Python starts and receives initialize, while the integration test used a real 0.5-second deadline.
The reader checked that deadline before observing an already exited child.

## Reproduction

The EOF integration case waits for its fake child to exit, then calls the response reader with an expired deadline; before the fix it returned timeout.

## Candidate Causes

- Child startup can outlast the real deadline under load, so the original test did not establish that an exit had occurred.
- An already exited child could be classified as timed out because the reader checked the clock first.

## Hypothesis

- If deadline expiration checks child exit before choosing its error, a synchronized exited child reports EOF while a live child still reports timeout | disconfirmer: run the synchronized exited-child case against the original reader.

## Verification

- Confirmed: the synchronized EOF case failed with timeout before the fix; the focused tests and the loaded 50-run proof verify the repaired behavior.

## Root Cause

The test coupled its exit assertion to child scheduling, and the reader chose a timeout without checking whether the child had already exited.

## Invariant Proof

- Invariant: an observed child exit takes precedence over timeout in the final refresh error envelope.
- Producer Proof: `read_jsonrpc_line_before` distinguishes an exited process from a live one at both timeout branches.
- Final-Consumer Proof: the synchronized EOF integration case asserts the refresh error envelope.
- Interface-Shape Sibling Scan: the select-timeout branch is exercised for exited and running children.
- Non-Claims: a process still alive at the deadline cannot be classified by a future exit.

## Detection Gap

- The existing EOF integration case depended on startup completing before a short deadline; synchronize the exit and test the expired-deadline branch deterministically.
- Scoped critique: checking a future exit would defeat the deadline; the poll classifies only an exit observed at the decision, and the live-child test preserves timeout behavior.

## Sibling Search

- Mental model: deadline expiration and process exit are mutually exclusive observations.
- Same file: both deadline and select-timeout paths now check the process; deterministic tests cover both.
- Cross-file: `host_codex_rpc.py` forwards reader errors into the existing refresh envelope; the integration test covers that consumer.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: none
- Disproving Observation: none
- What Local Reasoning Cannot Prove: behavior of a child that has not yet exited at the deadline.
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: no
- Next Step: impl
- Handoff Artifact: none

## Prevention

Keep exit and timeout observations independently controlled in tests rather than treating a short real deadline as proof of child termination.
