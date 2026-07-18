# Codex App-Server Request Deadline Debug
Date: 2026-07-19

## Problem

The Codex app-server cache refresh waits with a fresh timeout for every
JSON-RPC line. A stream of unrelated messages can therefore keep one request
alive beyond its declared timeout.

## Correct Behavior

Given one initialize or plugin-install request, all messages consumed while
waiting for its response ID share one absolute deadline. Unrelated messages do
not extend that request budget, and timeout, malformed JSON, EOF, and matching
error responses retain the existing YAML-facing failure envelope.

## Observed Facts

- `read_jsonrpc_line_with_deadline` creates `time.monotonic() + timeout_seconds`
  inside every invocation.
- Both response-ID loops call that function again after ignoring an unrelated
  message.
- There is no message-count cap or request-level deadline at either caller.
- The failure is local protocol-control logic; primary source and fixtures are
  available in this repository, so an external web search would add no evidence.

## Reproduction

Load the root CLI module and wait for one response ID from a child process that
emits different response IDs at intervals shorter than the timeout. Before the
repair, the wait remains live beyond the original request budget; the focused
fixture records elapsed time and requires the original budget to bound it.

## Candidate Causes

- Per-line timeout recreation extends a logical request deadline.
- Text-stream buffering around `select` and `readline` could hide an already
  buffered second line and produce a false timeout.
- Child-process EOF or cleanup behavior could make an ordinary exit look like
  an unbounded response wait.

## Hypothesis

The per-line deadline recreation is the root cause. One absolute monotonic
deadline is now created for initialize and another for plugin/install, then
passed through response-ID matching. The unrelated-message stream times out
inside the original budget while matching, malformed, EOF, and error cases keep
their established shapes. disconfirmer: the same stream exceeding the request
budget after callers stop recreating deadlines did not occur.

## Verification

- confirmed — before implementation, all four response-wait fixtures failed
  because the narrow helper did not exist; after implementation, 17 focused
  cache-refresh tests pass in 14.69 seconds.
- the continuous unrelated-message fixture shares one 60 ms deadline and
  asserts the wait ends within 150 ms; malformed JSON and EOF raise the prior
  `CharnessError` text, and the matching error survives an unrelated message.
- cache-refresh integration fixtures prove continuous unrelated messages,
  malformed JSON, EOF, and initialize errors all become the existing failed
  `app-server-error` envelope; plugin-install errors retain their distinct
  existing envelope.

## Root Cause

`refresh_codex_cache_via_app_server` treated each received line as a new timed
operation even though the declared timeout belongs to a sent request. Its two
open-coded response-ID loops hid that renewal, and immediate-success fixtures
never exercised the liveness boundary.

## Invariant Proof

- Invariant: one JSON-RPC request owns one non-renewable response deadline.
- Producer Proof: continuous unrelated-message, malformed, EOF, and matching-ID
  fixtures exercise `wait_for_jsonrpc_response` against one passed deadline.
- Final-Consumer Proof: cache-refresh integration fixtures retain the existing
  failed result envelopes for transport/initialize and plugin-install errors.
- Interface-Shape Sibling Scan: initialize and plugin/install now use the same
  response-ID seam while retaining separate request budgets and error handling.
- Non-Claims: this repair does not create a general JSON-RPC client or impose a
  message-count limit.

## Detection Gap

- app-server fixture | covered only immediate success | added unrelated stream,
  malformed payload, EOF, initialize/matching error, and public-envelope cases.

## Sibling Search

- same layer: initialize and plugin/install open-coded ID loops | same defect |
  both now call the narrow response waiter with independent deadlines.
- abstraction up: generic subprocess timeouts | intentional boundary | request
  budgets remain local to Codex app-server protocol ownership.
- specialization down: malformed JSON and EOF | adjacent failure paths | kept
  their existing exception text and covered them directly.
- mental-model sibling: matching JSON-RPC error as transport failure | distinct
  application result | preserved the existing `plugin-install-error` envelope.
- cross-file: `tests/charness_cli/fixtures/fake_codex.py` owns the app-server
  process peer exercised by the root CLI adapter; no production change needed.

## Seam Risk

- Interrupt ID: codex-app-server-request-deadline
- Risk Class: none
- Seam: request send -> unrelated message filtering -> matching response.
- Disproving Observation: elapsed wait exceeds the original absolute deadline.
- What Local Reasoning Cannot Prove: timing behavior of every real Codex build.
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/debug/2026-07-19-codex-app-server-deadline.md

## Prevention

Made response-ID waiting own a caller-supplied absolute deadline, removed both
renewing loops, and added the missing liveness/failure matrix. Kept the change
narrow: no generic client, message cap, new public enum, or JSON/YAML surface
change.
