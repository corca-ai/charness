# Probe Record: standing-lane-flake-bar

The first record written under `scripts/probe_record_lib.py`, for the precondition
repair of the probe-provenance goal. It is a worked example on real work rather than
on a fixture, which is the thing this repo has repeatedly shipped without.

Claim: the readiness wait in `test_acquire_closes_session_on_sigterm_mid_render` no
  longer renders a verdict on how loaded the machine is
Claim kind: change
Observable: the wait loop's outcome (pass, or `AssertionError`) against a child that
  reaches its `open` line later than the old 10s bar while staying alive throughout
Source ref: docs/handoff.md
Source revision: 1b49a1ae0
Source conditions: the failure occurs only under the full parallel lane; the test
  passes in isolation, under partial parallelism, and on the pre-session base tree
Base ref: 1b49a1ae0
Head ref: 8527936fd
Base arm: base-observed
Call sites unproven: none — the wait loop has exactly one call site, the test that
  owns it (`tests/test_web_fetch_cleanup.py::test_acquire_closes_session_on_sigterm_mid_render`)

## Source text

```
  `test_acquire_closes_session_on_sigterm_mid_render` waits 10s for a fake agent-browser
  subprocess to log; it fails only under the full parallel lane and passes in isolation,
  under partial parallelism, and on the pre-session base tree. It blocks pre-push.
```

## Stimulus

Both arms run against the SAME child in the same process, back to back, so nothing but
the loop body differs. The child is a stand-in for `acquire_public_url.py`: alive and
progressing the whole time, but slower than the old bar to reach the line the test
waits for. The 12s delay is chosen to sit between the old 10s bar and the new 120s hang
backstop, which is the condition the source names — a lane busy enough to push the
pre-`open` work past the deadline.

```
python3 -c "import time,pathlib;time.sleep(12);pathlib.Path(LOG).write_text('--url x open y\n');time.sleep(25)"
```

## Base observable

```
base  waited  10.0s -> AssertionError: fake agent-browser never logged an open call
```

## Head observable

```
head  waited  12.1s -> passed
```

## Non-claims

- This record does NOT claim the flake is gone. It claims the bar stopped being a clock
  that measures the machine below 120s. The remaining backstop is still a clock, and its
  blind class is stated at the constant and at the loop in the test itself.
- The standing lane was green at this tree (10156 passed, 72.6s). That is context, not
  evidence: a green run under one load is exactly the observation that cannot tell a
  fixed flake from an unexercised one, which is why the base/HEAD pair above is the
  proof and the green run is not cited as one.
- The base and head observables were captured by running both loop bodies, not derived
  from reading the diff. The record cannot prove that to a reader; a distinct observer
  re-running the stimulus can.
