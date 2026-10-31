# Debug: nested quality runner runtime isolation
Date: 2026-10-31

## Problem

A pre-push release pytest run failed `test_run_quality_summarizes_success_without_replaying_logs` because nested standing pytest failed.

## Correct Behavior

Given a synthetic quality runner, when it runs its nested pytest, then its runtime and retention operate independently of host and other test runtimes.

## Observed Facts

The saved hook failure's nested pytest log shows `tarfile.ReadError: empty header` during `runtime_root_retention.py` lane salvage under `/tmp/charness/runtime`.
The fixture passed only `PATH`; without `CHARNESS_RUNTIME_ROOT`, `XDG_CACHE_HOME`, or `TMPDIR`, `scripts/runtime_bootstrap.py` selects the system temporary directory.
The pre-push runtime script unsets Git repository-local variables and selects the hook runtime root.
The earlier train-loader failure had a separate mutable bootstrap-root cause; this record does not assert a common leaked Git variable.

## Reproduction

The new fixture regression supplies an unrelated `TMPDIR` and executes nested pytest; before the fix it fails because a `charness/runtime` tree appears in that directory.
The hook-environment release rerun failed a different `tool doctor` test on a 28-second subprocess timeout; the original named failure's saved nested traceback is the direct evidence for its failure.

## Candidate Causes

- Missing fixture runtime selection sends nested runs into a shared fallback tree where retention sees unrelated lane records.
- Concurrent retention writing a salvage archive may explain the empty header, but the saved log does not establish the writer interleaving.

## Hypothesis

- A per-fixture explicit runtime root prevents the nested runner from entering the unrelated fallback runtime | disconfirmer: run the new fixture regression before the fix and inspect the fallback tree.

## Verification

- Confirmed: the regression failed before the fixture change and passed afterward; the hook-environment release pytest is checked separately.

## Root Cause

The synthetic quality-runner environment discarded all runtime-location variables without supplying a fixture-owned `CHARNESS_RUNTIME_ROOT`.
The runtime bootstrap therefore chose `/tmp`, allowing retention to touch unrelated runtime records.

## Invariant Proof

- Invariant: each synthetic quality fixture's nested runtime is outside its checkout and independent of unrelated host runtime trees.
- Producer Proof: the shared quality-runner environment supplies an explicit per-fixture runtime.
- Final-Consumer Proof: the regression executes the real nested quality runner and verifies that the unrelated temporary root remains free of a runtime tree.
- Interface-Shape Sibling Scan: the shared helper is used by both freshly seeded and cloned fixtures.
- Non-Claims: the exact concurrency that produced the original empty tar header is not established.

## Detection Gap

- The old quality summary assertion did not constrain nested runtime ownership; the new test runs with an unrelated temporary root and checks it remains untouched.
- Scoped critique: preserve tests' explicit runtime overrides; only the synthetic fixture default changes.

## Sibling Search

- Mental model: an environment with only `PATH` is isolated from the host.
- Same seam: both synthetic creation and cloning now use the same fixture environment.
- Cross-file: `runtime_bootstrap.py` intentionally falls back to system temp when no location is supplied; that production policy is unchanged.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: none
- Disproving Observation: none
- What Local Reasoning Cannot Prove: the original tar writer interleaving and unrelated test timeout causes.
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: no
- Next Step: impl
- Handoff Artifact: none

## Prevention

Synthetic runners that invoke retention must own their runtime root, even when the rest of their environment is deliberately minimal.
