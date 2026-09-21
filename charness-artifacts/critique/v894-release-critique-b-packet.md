# Release critique B — charness 8.9.4 patch slice: quality-engine stale failure-log sweep

- Reviewer: release-critique-reviewer-b
- Verdict: **PASS** (include in 8.9.4)
- Scope (only): commit `4e24ed9ee`'s changes to `scripts/run_quality_engine.py`
  and `scripts/run_quality_engine_output.py` (run-start sweep of stale failure
  logs) plus regression tests in
  `tests/quality_gates/test_quality_runner.py` and
  `tests/quality_gates/test_gate_summary_names_failures.py`.
- Out of scope (not claimed here): the same commit's closeout-draft readiness
  change (`resources/issue/scripts/issue_validate_closeout_draft.py` and its
  tests). Another reviewer owns that slice.

Fresh-eye satisfaction: parent-delegated — the spawned subagent reviewer ran the scoped diff, the regression tests, and an extra edge case beyond the suite, and delivered this packet with verdict PASS; no same-agent substitution.

## Reviewer Tier Evidence

- **Requested tier**: `n/a` (no tier requested; host-defaulted)
- **Requested spawn fields**: `n/a` (subagent defaults; no explicit model/effort ask)
- **Host exposure state**: `host-defaulted`
- **Application state**: `spawned subagent reviewer delivered; verdict PASS received, approval not inferred`
- **Delivery state**: `findings-received`
- **Execution mode**: `typed-subagent`

## Boundary Ownership

- **Producer:** the quality engine owns failure-log lifecycle
  (`scripts/run_quality_engine_output.py`, called from
  `scripts/run_quality_engine.py`).
- **Consumer:** operators reading quality failure summaries.
- **Verdict:** `single-surface` — a run-start sweep plus regression tests;
  no other surface semantics move with this change.

## What the change does

- New `sweep_stale_failure_logs(failure_dir, *, older_than_ns)` in
  `scripts/run_quality_engine_output.py:32` deletes `*.log` files with
  `st_mtime_ns < older_than_ns`, skipping non-files, non-`.log` files, and
  anything raising `OSError`; returns the removal count.
- `run()` in `scripts/run_quality_engine.py:289` calls it once at run start
  with `older_than_ns=time.time_ns()`, guarded by
  `getattr(context, "failure_log_dir", None)` so minimal test doubles without
  that attribute are unaffected.
- Problem fixed: the runtime root is shared across runs, so a fresh failure
  summary's `[log:]` pointer could name a previous run's log under the same
  gate label. After the sweep, a pointer can only name a file this run wrote
  (sequential-run case).
- Regression tests: `test_failure_log_sweep_removes_only_previous_run_logs`
  and `test_failure_log_sweep_survives_unremovable_files` (sweep semantics),
  plus an update to
  `test_a_log_copy_that_fails_warns_instead_of_promising_a_stale_file` so the
  copy-failure path is pinned with a read-only *directory* (a merely read-only
  stale file is now swept away at start, which is the intended new behavior).

## Evidence tiers

### Verified (ran in this session)

1. Scoped diff inspected:
   `git diff v8.9.3..HEAD -- scripts/run_quality_engine.py
   scripts/run_quality_engine_output.py
   tests/quality_gates/test_quality_runner.py
   tests/quality_gates/test_gate_summary_names_failures.py` — matches the
   description above; no other production files in scope.
2. Scoped regression suite green, full bodies of both files, unmodified:
   `python3 -m pytest tests/quality_gates/test_quality_runner.py
   tests/quality_gates/test_gate_summary_names_failures.py -q` →
   **48 passed in 35.87s**.
3. Edge probes executed live against the real `sweep_stale_failure_logs`:
   - Empty failure-log dir → returns 0, no error.
   - Missing failure-log dir → returns 0 (`OSError` on `iterdir` handled).
   - Older-schema stale log (`WEIRD__gate..v1.log`, old mtime) → removed;
     `notes.txt` and a subdirectory named `nested.log` both survive.
   - True-overlap race reproduced: run A writes `gate-a.log` after its start
     `T0`; a second run sweeping with threshold `T1 > T0` deletes A's log
     (`removed: 1`). This is the residual the docstring explicitly documents
     ("True overlap still races, and that residual is documented, not solved,
     here"). Sequential runs — the supported CI shape — are fixed; concurrent
     runs sharing one runtime root were already unsafe (both runs also
     interleave `write_text` copies), so this is accepted, not a blocker.

### Corroborated (read, not executed)

- `consume_result` (`run_quality_engine_output.py:78`) writes the failure copy
  with `target.write_text(...)` and warns (`WARN: could not save full output
  ...`) on `OSError`; the read-only-directory test update keeps that warning
  path pinned while the sweep handles the stale-file path. Consistent with the
  sweep's best-effort `except OSError: continue` contract.
- `getattr(context, "failure_log_dir", None)` fallback keeps minimal test
  doubles working; no new required attribute on the context object.

### Degraded

- None. No claim below rests on unrunnable or skipped evidence.
- Minor residue noted (verified behavior, not a failure): if the log dir ever
  contained a *symlink* `alias.log -> real.log`, iteration order can unlink
  `real.log` first and leave a dangling `alias.log` behind (`is_file()` is
  `False` for a dangling symlink, so it is skipped; probe returned `removed:
  1`, target gone, link remaining). Planting symlinks in the runtime root is
  outside the threat model, and `write_text` through a dangling link
  re-materializes the target on the next failing run, so this does not
  misattribute a `[log:]` pointer. No action required for 8.9.4; at most a
  future hardening note (e.g. also unlink symlinks regardless of target
  liveness).

## Verdict rationale

- The fix is minimal, correctly bounded (strictly-older `mtime_ns`
  comparison, `.log`-only, error-swallowing sweep that can never fail a run),
  and covered by focused regression tests that pass unmodified.
- The one genuine hazard (overlapping concurrent runs on a shared runtime
  root) is real but documented, pre-existing in worse form, and out of scope
  for a patch release.
- No production code was edited, committed, or pushed by this reviewer.

## Files checked

- `scripts/run_quality_engine.py` (lines ~1–20 imports, ~286–292 sweep call)
- `scripts/run_quality_engine_output.py` (lines 32–56 sweep, 59–88
  `consume_result`)
- `tests/quality_gates/test_quality_runner.py` (two new sweep tests)
- `tests/quality_gates/test_gate_summary_names_failures.py` (read-only-dir
  test update)

## Commands run

1. `git diff v8.9.3..HEAD -- scripts/run_quality_engine.py scripts/run_quality_engine_output.py tests/quality_gates/test_quality_runner.py tests/quality_gates/test_gate_summary_names_failures.py`
2. `python3 -m pytest tests/quality_gates/test_quality_runner.py tests/quality_gates/test_gate_summary_names_failures.py -q` → 48 passed
3. Live `sweep_stale_failure_logs` probes: empty dir / missing dir /
   old-schema log + subdir + non-log / symlink ordering
4. Live two-run overlap-race reproduction (A's log deleted by B's later
   threshold sweep)
5. `git show 4e24ed9ee --stat` (scope-boundary check only)
