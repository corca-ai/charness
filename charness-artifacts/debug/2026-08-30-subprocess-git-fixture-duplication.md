# Debug Review
Date: 2026-08-30

## Problem

The standing suite launched 18,010 synchronous child processes for 8,586 tests,
including 13,300 Git processes. Test count grew while launches per test remained
essentially flat, so prior speed work did not remove the dominant process cost.

## Correct Behavior

Given a standing test run, when several assertions need the same immutable repo
state, then one owner should construct or read that state once and cheaper tests
should reuse it; only tests whose claim is the process or Git boundary should
cross that boundary independently.

## Observed Facts

- `/tmp/charness-spawn-probe/current.jsonl` records 18,010 `Popen` launches: 13,300
  Git and 2,997 Python-family processes.
- `/tmp/charness-spawn-probe/attributed.jsonl` ties repeated calls to both product
  helpers and test fixture bootstrap. `tests/quality_gates/seeding_support.py`
  alone accounts for 453 Git launches.
- The earlier 5,651-test baseline used 11,756 launches. Density stayed near 2.1
  launches per test instead of falling.
- `scripts/worktree_doctor_checks.py` independently reread coherent checkout
  metadata; release claim surfaces independently relisted the same tracked tree.
- The census exposed process lifetime waste as well as launch count: PID 1258960
  was an orphaned mutation wrapper for more than a day, waiting for a deleted
  `child-start` marker after its pytest parent died before child attachment.
- One intermediate reviewed-input census put `sitecustomize.py` at the repository
  root. Python then auto-loaded its `sys.settrace` hook in unrelated tests, making
  a timeout test fail and invalidating wall-time comparisons from that interval.
  The probe was removed; the final census uses an opt-in `/tmp` module instead.

## Reproduction

- Run the standing suite with `/tmp/charness-spawn-probe/sitecustomize.py` on
  `PYTHONPATH`; aggregate `attributed.jsonl` by executable and caller.

## Candidate Causes

- Boundary tests and logic matrix tests both pay a new Python process.
- Tiny Git repositories are rebuilt per test instead of copied from immutable
  session seeds.
- Helpers expose scalar Git probes, so one operation rereads coherent state
  through multiple layers.
- The mutation pre-exec wrapper waited only for a start-file appearance. It had
  no observation that the parent responsible for publishing that file had died.
- Measurement instrumentation had no ownership boundary of its own. A global
  import hook placed inside the subject tree silently became part of every Python
  test process instead of remaining an external observer.

## Hypothesis

- If coherent reads become operation-scoped snapshots and repeated repository
  setup becomes immutable seed plus copy, the same standing selection will show
  materially fewer Git/Python launches without losing boundary-specific tests.
  Disconfirmer: unchanged attributed caller totals after focused replacements.

## Verification

- Result: confirmed across the identical standing selection. The final external
  census records 10,597 launches for 8,623 passing tests: 7,524 Git and 1,834
  Python-family processes. Against 18,010 / 13,300 / 2,997 at 8,586 tests, that
  is 41.2% fewer total launches, 43.4% fewer Git launches, and 38.8% fewer
  Python-family launches while the suite gained 37 tests. Launch density fell
  from 2.10 to 1.23 per test.
- The reductions came from operation snapshots, immutable repo seeds, explicit
  separation of process-boundary tests from logic matrices, in-process script
  runners with representative delivery tests, and removal of repeated fixture
  bootstrap. The mutation wrapper also exits when its expected parent dies.
- The census was instrumented, so its elapsed time is not speed evidence. It
  proves removed process work in this suite, not consumer-repository latency.
- The v8.0.0 publish exposed a sibling after the census: the release helper's
  130.8-second established quality run was followed by the pre-push hook's
  100.8-second broad run over the same push. A semantic one-push receipt now
  binds pass/exit/unproven/full-queue state to the exact clean HEAD/tree and
  ignored materialized-export digest. The irreversible close-keyword scan is
  never reused; stale or changed state runs the ordinary gate.

## Root Cause

Test completeness was modeled as each test independently reconstructing and
re-observing reality. There was no operation-level state snapshot or explicit
division between boundary proof and lower-layer behavior proof, so duplication
looked like thoroughness and runtime budgets hid the accumulated cost.

The same boundary-ownership gap existed in process lifecycle: the mutation
parent owned attachment and cleanup, while its pre-exec child owned an unbounded
wait without a parent-liveness condition. Abrupt parent death therefore removed
the only actor capable of completing or cancelling the wait.

## Invariant Proof

- Invariant: each operation reads one coherent immutable view; only delivery
  tests independently cross a process boundary.
- Producer Proof: focused call-count tests for checkout and tracked-tree snapshots.
- Final-Consumer Proof: `/tmp/charness-final-spawn-probe/final-standing-v9-20260831.jsonl`;
  the identical standing selection completed with 8,623 passing tests.
- Interface-Shape Sibling Scan: task-run carrier state, reviewed-input identity,
  release delta resolution, and Git-backed test setup share the same shape.
- Non-Claims: mutation runtime and consumer-repository speed are not measured.

## Detection Gap

- runtime budget | aggregate wall time stayed below a loose ceiling and did not
  expose process density | retain measurement as an inventory signal, not a new
  standing gate, and compare identical selections during structural work.
- orphan guard | the end-of-session scan recognized only browser-runtime
  descendants, so a mutation wrapper could survive unnoticed | make the wrapper
  self-terminate when its expected parent or recovery directory disappears and
  retain one real process-boundary regression.
- census isolation | a repo-root `sitecustomize.py` was automatically imported by
  unrelated Python processes, and only a timing failure exposed the contamination
  | keep diagnostic import hooks outside the repository, require an explicit log
  environment variable, and reject wall-time evidence from an instrumented run.
- release/push composition | two individually correct quality owners ran in
  sequence without a proof handoff | accept only the quality runner's semantic
  receipt sealed to the final push subject; never infer trust from exit 0 alone.

## Sibling Search

- Mental model: independent reconstruction is stronger proof even when tests
  observe the same immutable state.
- same layer: Git-backed fixtures | decision: same bug, fix now | proof: attributed runtime census.
- abstraction up: CLI logic matrices using subprocess | decision: same bug, fix now | proof: attributed runtime census.
- specialization down: actual push/tag/remote readback tests | decision: intentional boundary | proof: static contract review.
- cross-file: `scripts/task_run_git.py`, `scripts/reviewed_input_identity.py`, and
  `tests/quality_gates/support.py` are concrete snapshot/boundary siblings.

## Seam Risk

- Interrupt ID: subprocess-density-2026-08-30
- Risk Class: none
- Seam: local synchronous process boundary
- Disproving Observation: identical-selection census and focused semantic tests
- What Local Reasoning Cannot Prove: consumer-repository elapsed-time improvement
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Make boundary ownership explicit in test helpers: shared immutable seeds for
setup, operation-scoped snapshots for coherent reads, and a thin named set of
real subprocess/Git delivery tests. Judge each deletion by preserved capability,
then use the attributed census as evidence that the structural move paid off.
Every child that can wait before `exec` must also own a parent-loss exit
condition; parent-side `finally` cleanup alone is not a crash-survival contract.
Diagnostic hooks must likewise live outside the subject tree and be opt-in; a
measurement that changes every interpreter's execution model is not neutral
evidence.
