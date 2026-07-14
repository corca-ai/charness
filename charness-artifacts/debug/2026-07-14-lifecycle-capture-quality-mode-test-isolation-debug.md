# Lifecycle Capture Quality Mode Test Isolation Debug
Date: 2026-07-14

## Problem

The final read-only standing pytest run failed six new lifecycle-capture tests:
write-path cases returned `readonly_quality_run`, and their expected JSONL file
did not exist. The operator capability at risk was a trustworthy locked
repository closeout for the lifecycle feedback slice.

## Correct Behavior

Given a standing quality process that exports its read-only sentinel, when
tests exercise ordinary lifecycle capture writes, then their fixture explicitly
clears ambient quality mode; when the dedicated read-only case runs, it opts in
and proves that no record is written.

## Observed Facts

- The locked suite reported 6 failed and 4,597 passed; all six failures were in
  `tests/test_lifecycle_usage_capture.py` and observed `readonly_quality_run` or
  the resulting absent JSONL file.
- `scripts/run_standing_pytest.py:163` exports `CHARNESS_QUALITY_MODE` to the
  entire pytest process, while `scripts/lifecycle_usage_capture.py:255` treats
  any non-empty value as a write prohibition.
- The original focused run passed outside that environment. This custom,
  repository-private sentinel made a web search irrelevant; the runner, helper,
  and exact local reproduction are the primary evidence.
- Existing sibling tests in `tests/test_usage_feedback.py` and
  `tests/quality_gates/test_slice_closeout_telemetry.py` already clear ambient
  quality mode before exercising write paths.

## Reproduction

- Before the fix, `python3 scripts/run_standing_pytest.py --repo-root . --mode
  read-only` failed the six write-path cases.
- Smallest equivalent environment: run the lifecycle test file with
  `CHARNESS_QUALITY_MODE=1`; ordinary write assertions receive
  `readonly_quality_run` unless their fixture clears the inherited sentinel.

## Candidate Causes

- Production capture incorrectly suppresses all writes, independent of the
  environment.
- The standing runner propagates a read-only sentinel that production code is
  supposed to honor, but the new write-path tests fail to isolate it.
- The checked-in plugin copy captured different import-time environment or
  diverged from source behavior.
- Parallel pytest workers raced on one shared output stream.

## Hypothesis

- falsifiable claim: inherited `CHARNESS_QUALITY_MODE`, not capture logic,
  plugin drift, or concurrency, causes the failures; clearing ambient quality
  mode in an autouse fixture while setting it explicitly in the read-only test
  will make both the smallest reproduction and standing suite pass |
  disconfirmer: rerun the same test file with both quality sentinels present,
  then rerun the exact standing consumer.

## Verification

- result: confirmed — normal focused pytest, `CHARNESS_QUALITY_READ_ONLY=1`,
  and `CHARNESS_QUALITY_MODE=1` each passed all 15 lifecycle tests after the
  fixture change.
- final-consumer result: `python3 scripts/run_standing_pytest.py --repo-root .
  --mode read-only` passed 4,603 tests in 34.63 seconds.
- the dedicated quality-mode test still sets `CHARNESS_QUALITY_MODE` explicitly,
  returns `readonly_quality_run`, and proves the JSONL path remains absent.

## Root Cause

The standing runner intentionally exports quality mode; the lifecycle helper
intentionally refuses writes under it; the new tests covered both ordinary and
read-only behavior but implicitly assumed a clean process environment. The
structural cause was a missing test-fixture boundary: write-path tests did not
declare that ambient suite mode was outside their input contract.

## Invariant Proof

- Invariant: when the standing runner emits a quality-mode signal, production
  write helpers must honor it, while write-path unit tests must control that
  signal explicitly before asserting output.
- Producer Proof: the runner exports the mode and the dedicated unit case proves
  the helper refuses the write.
- Final-Consumer Proof: the exact read-only standing suite passed 4,603 tests.
- Interface-Shape Sibling Scan: usage-feedback and closeout-telemetry tests use
  the same ambient-sentinel boundary and already clear or set it explicitly.
- Non-Claims: no installed-host or provider behavior changed or was rerun.

## Detection Gap

- normal focused pytest | did not supply the standing runner's ambient quality
  mode | run the new file once with `CHARNESS_QUALITY_MODE=1`, now covered by
  the autouse fixture and exact final-consumer rerun.

## Sibling Search

- Mental model: a unit test process environment was treated as empty even
  though the aggregate runner owns a suite-wide safety sentinel.
- same layer: `tests/test_usage_feedback.py` and
  `tests/quality_gates/test_slice_closeout_telemetry.py` | decision: same class,
  diagnostic-only for this slice | proof: static scan shows explicit clearing
  and their standing tests pass.
- abstraction up: write-producing helpers under `CHARNESS_QUALITY_MODE` |
  decision: same class, diagnostic-only for this slice | proof: repository scan
  plus 4,603-test final-consumer pass found no additional failure.
- specialization down: source and exported-plugin lifecycle write cases |
  decision: same bug, fix now | proof: both execute under the shared autouse
  fixture and passed with the sentinel pre-set.
- mental-model sibling: `CHARNESS_QUALITY_READ_ONLY` legacy input | decision:
  same class, diagnostic-only for this slice | proof: focused pre-set run passed.
- cross-file: `tests/test_usage_feedback.py` and
  `tests/quality_gates/test_slice_closeout_telemetry.py` are matching sentinel
  boundary siblings, not merely keyword matches.

## Seam Risk

- Interrupt ID: lifecycle-capture-quality-mode-test-isolation
- Risk Class: none
- Seam: standing pytest environment to lifecycle unit-test fixture
- Disproving Observation: the same tests pass with either sentinel pre-set once
  the fixture controls ambient mode, while the explicit read-only case remains.
- What Local Reasoning Cannot Prove: none required for this repository-local
  deterministic test boundary.
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/spec/2026-07-14-lifecycle-feedback-and-quality-truthfulness.md

## Prevention

Keep the autouse environment boundary in the lifecycle test module and retain
the exact read-only standing suite in locked closeout. Do not weaken the
production write prohibition or the aggregate runner to make unit tests pass.
