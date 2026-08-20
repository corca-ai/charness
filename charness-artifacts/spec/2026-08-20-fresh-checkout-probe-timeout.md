# Fresh Checkout Probe Timeout Spec

## Problem

`check_fresh_checkout_probes.py` inherits the shared 10-second CLI alarm even
though its own clone and child probe operations are bounded at 120 and 300
seconds. The outer alarm can terminate a valid fresh-checkout proof before any
probe result is attributed.

## Capability Contract

The release fresh-checkout producer must emit an established pass/fail payload
when its bounded clone and declared probes complete. A timeout remains blocking,
but must belong to the operation that owns the timeout rather than a shorter
unrelated global default.

## Current Slice

Repair the producer-side timeout contract, keep the checked-in plugin mirror in
lockstep, and add focused regression coverage for the default timer selection
and the existing result-state vocabulary.

## Fixed Decisions

- Do not widen `scripts/script_timeout.py`'s shared 10-second default; that would
  hide unrelated short-script hangs and change every caller.
- Do not replace the generic timeout with a blind fixed aggregate budget. The
  checker already bounds clone setup and each child probe at their owning seams.
- Preserve explicit `CHARNESS_SCRIPT_TIMEOUT_SECONDS` overrides for operators and
  callers that intentionally provide an outer process budget.
- Preserve fail-closed status semantics: a timeout or failed child is not a pass.

## Probe Questions

- Is the smallest producer repair an explicit `default_seconds=0` opt-out, with
  child operations remaining bounded, or does the adapter contract require a
  computed aggregate budget? Resolve this through focused tests and the fresh
  checkout integration command.
- Does the release publish caller consume the repaired established payload without
  adding a second, shorter timeout boundary?

## Deferred Decisions

- Per-probe elapsed-time telemetry beyond the existing command and previews.
- A future adapter-declared total timeout, if consumers need one after this slice.

## Non-Goals

- No release version bump, tag, push, publication, install refresh, or hosted
  readback is part of this repair slice.
- No change to the global timeout helper or unrelated release status commands.

## Deliberately Not Doing

- Do not “fix” the symptom by setting a larger arbitrary number such as 420
  seconds in the producer; that merely changes the point at which the same
  producer/child budget mismatch reappears.
- Do not treat the successful override run as the final proof; it is the
  falsifier that identifies the outer timer and must be followed by a default
  invocation after repair.

## Constraints

- Source and `plugins/charness` mirror must be byte-identical for shipped script
  surfaces.
- The fresh-checkout command runs sequentially in a temporary clone and must
  remain bounded by clone/probe subprocess timeouts.
- The result states `passed`, `blocked`, `not_configured`, and
  `not_established` are public release-proof vocabulary and must not drift.

## Success Criteria

- `unit`: focused tests prove the producer does not inherit the 10-second default
  while preserving explicit environment override behavior.
- `integration`: the exact default `--run-probes --detail` command completes with
  `status: passed`, five probe results, and zero return codes on the current repo.
- `unit`: no-probe, unrun-probe, and failing-probe states retain their existing
  exit bytes and payload shapes.
- `integration`: source/plugin parity and release planner consumption checks pass.

## Acceptance Checks

- `unit` — `python3 -m pytest -q tests/quality_gates/test_release_fresh_checkout_probes.py tests/quality_gates/test_script_inprocess_behaviors.py`.
- `unit` — `python3 -m pytest -q tests/test_script_timeout.py`.
- `integration` — `python3 skills/public/release/scripts/check_fresh_checkout_probes.py --repo-root . --run-probes --detail`.
- `integration` — `python3 scripts/check_plugin_mirror_drift.py --repo-root .`.
- `integration` — `python3 skills/public/release/scripts/plan_release_run.py --repo-root . --detail`.

## Boundary Ownership

- `check_fresh_checkout_probes.py` owns the producer-side outer timeout choice and
  child result attribution.
- `scripts/script_timeout.py` owns the reusable default and explicit environment
  override semantics; it is not changed by this slice.
- `publish_release_cli.py` and `plan_release_run.py` consume the producer result;
  they must not convert an unestablished result into a pass.

## Critique

- Interrupt Source: fresh-checkout-release-proof-timeout-2026-08-20
- Seam Summary: local release planner → temporary checkout → child CLI/doctor probes.
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: the falsifier run and source binding establish the producer
  seam; implementation can now test the smallest explicit producer contract.
- What Disproving Observation Is Resolved: `CHARNESS_SCRIPT_TIMEOUT_SECONDS=420`
  completes the same fresh checkout and all five declared probes with return code
  0, disconfirming a child-specific failure as the primary cause.
- Fresh-eye status: unproven. The host created reviewer threads but did not bind
  the bounded-reviewer tools, so no fresh-eye approval is claimed.
- Counterweight: a computed aggregate timeout remains a viable alternative if
  focused tests reveal an unbounded producer path; do not choose `default_seconds=0`
  without proving all owned subprocesses remain bounded.

## Canonical Artifact

`charness-artifacts/debug/2026-08-20-fresh-checkout-probe-timeout.md` records the
diagnosis; this spec is the implementation contract for its repair.

## First Implementation Slice

Inspect the existing `arm_cli_timeout` test seam, add a focused assertion for the
producer default, implement the explicit producer-side policy in the source copy,
sync the plugin mirror, and run the acceptance checks before any broader release
claim.
