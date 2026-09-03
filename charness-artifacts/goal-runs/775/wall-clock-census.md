# Wall-clock census of `tests/` (Goal Run #775, #779)

> Closed by #780 on 2026-09-03: every rewrite-scope site below is gone and `wall-clock-baseline.json` is empty. The kept kinds (`controlled-child`, `clock-as-data`) remain by design. Rewrite record: `2026-09-03-session-record.md`, third session.

Recorded 2026-09-03 before any rewrite, from a grep for `time.sleep(`, `time.monotonic(`, and `time.time(` over `tests/` excluding `tests/fixtures`. One row per site. Kinds:

- `elapsed-claim`: the assertion is on measured elapsed time. Rewrite or delete.
- `deadline-poll`: a `monotonic` deadline loop polling for an observation the child could signal. Rewrite to a blocking observation the test forces.
- `sleep-sync`: a bare sleep standing in for synchronisation. Rewrite.
- `controlled-child`: a sleep inside a seeded child script; the child is the controlled input and the sleep is its behaviour, not the test's claim. Kept.
- `clock-as-data`: `time.time()` producing a file age or ordering value with day-scale deltas. Kept.

| kind | sites |
| --- | --- |
| clock-as-data | 13 |
| controlled-child | 32 |
| deadline-poll | 30 |
| elapsed-claim | 12 |
| sleep-sync | 9 |

Total sites: 96. Rewrite scope (elapsed-claim, deadline-poll, sleep-sync): 51.

## Sites

| file | line | kind | code |
| --- | --- | --- | --- |
| `tests/test_subprocess_guard.py` | 32 | controlled-child | `["python3", "-c", "import time; time.sleep(2)"],` |
| `tests/test_subprocess_guard.py` | 44 | controlled-child | `["python3", "-c", "import time; time.sleep(0.2); print('slow')"],` |
| `tests/test_subprocess_guard.py` | 135 | sleep-sync | `time.sleep(2)` |
| `tests/test_subprocess_guard.py` | 156 | controlled-child | `["python3", "-c", "import time; time.sleep(5)"],` |
| `tests/test_subprocess_guard.py` | 218 | elapsed-claim | `started = time.monotonic()` |
| `tests/test_subprocess_guard.py` | 220 | controlled-child | `"python3 -c 'import time; time.sleep(25)' & sleep 25",` |
| `tests/test_subprocess_guard.py` | 228 | elapsed-claim | `elapsed = time.monotonic() - started` |
| `tests/test_subprocess_guard.py` | 248 | elapsed-claim | `started = time.monotonic()` |
| `tests/test_subprocess_guard.py` | 250 | controlled-child | `["python3", "-c", "import time; time.sleep(20)"],` |
| `tests/test_subprocess_guard.py` | 256 | elapsed-claim | `elapsed = time.monotonic() - started` |
| `tests/test_subprocess_guard.py` | 267 | controlled-child | `"subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'],\n"` |
| `tests/test_subprocess_guard.py` | 269 | controlled-child | `"time.sleep({child_sleep})\n"` |
| `tests/test_subprocess_guard.py` | 280 | elapsed-claim | `started = time.monotonic()` |
| `tests/test_subprocess_guard.py` | 288 | elapsed-claim | `elapsed = time.monotonic() - started` |
| `tests/test_subprocess_guard.py` | 336 | controlled-child | `["python3", "-c", "import time; time.sleep(30)"],` |
| `tests/test_subprocess_guard.py` | 342 | sleep-sync | `time.sleep(0.2)` |
| `tests/test_subprocess_guard.py` | 355 | controlled-child | `f"grandchild = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'])\n"` |
| `tests/test_subprocess_guard.py` | 357 | controlled-child | `"time.sleep(30)\n"` |
| `tests/test_subprocess_guard.py` | 368 | deadline-poll | `deadline = time.monotonic() + 5` |
| `tests/test_subprocess_guard.py` | 369 | deadline-poll | `while not marker.exists() and time.monotonic() < deadline:` |
| `tests/test_subprocess_guard.py` | 370 | deadline-poll | `time.sleep(0.01)` |
| `tests/test_subprocess_guard.py` | 408 | deadline-poll | `deadline = time.monotonic() + 2` |
| `tests/test_subprocess_guard.py` | 409 | deadline-poll | `while time.monotonic() < deadline:` |
| `tests/test_subprocess_guard.py` | 414 | deadline-poll | `time.sleep(0.05)` |
| `tests/test_subprocess_guard.py` | 428 | sleep-sync | `["python3", "-c", "import sys, time; print('partial' + '-body'); sys.stdout.flush(); time.` |
| `tests/test_subprocess_guard.py` | 502 | controlled-child | `["python3", "-c", "import time; time.sleep(0.35)"],` |
| `tests/quality_gates/test_manage_mutation_reports.py` | 13 | clock-as-data | `stamp = time.time() - age_days * 86400` |
| `tests/quality_gates/test_run_quality_engine.py` | 150 | elapsed-claim | `started = time.monotonic()` |
| `tests/quality_gates/test_run_quality_engine.py` | 154 | elapsed-claim | `assert time.monotonic() - started >= 1` |
| `tests/quality_gates/test_semantic_review_command.py` | 156 | controlled-child | `child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])` |
| `tests/quality_gates/test_semantic_review_command.py` | 158 | sleep-sync | `time.sleep(sleep_for)` |
| `tests/quality_gates/test_semantic_review_command.py` | 691 | deadline-poll | `deadline = time.monotonic() + 5` |
| `tests/quality_gates/test_semantic_review_command.py` | 692 | deadline-poll | `while not child_pid_file.exists() and time.monotonic() < deadline:` |
| `tests/quality_gates/test_semantic_review_command.py` | 693 | deadline-poll | `time.sleep(0.05)` |
| `tests/quality_gates/test_semantic_review_command.py` | 714 | deadline-poll | `time.sleep(0.05)` |
| `tests/quality_gates/test_mutation_recovery.py` | 70 | controlled-child | `"    time.sleep(30)\n"` |
| `tests/quality_gates/test_mutation_recovery.py` | 95 | deadline-poll | `deadline = time.monotonic() + 8` |
| `tests/quality_gates/test_mutation_recovery.py` | 96 | deadline-poll | `while time.monotonic() < deadline:` |
| `tests/quality_gates/test_mutation_recovery.py` | 102 | deadline-poll | `time.sleep(0.02)` |
| `tests/quality_gates/test_retention_refusal_coverage.py` | 23 | clock-as-data | `stamp = time.time() - 60 * 86400` |
| `tests/charness_cli/test_task_run.py` | 753 | sleep-sync | `time.sleep(1.2)` |
| `tests/charness_cli/test_codex_cache_refresh.py` | 312 | controlled-child | `" time.sleep(0.015)\n"` |
| `tests/charness_cli/test_codex_cache_refresh.py` | 314 | elapsed-claim | `started = time.monotonic()` |
| `tests/charness_cli/test_codex_cache_refresh.py` | 322 | elapsed-claim | `elapsed = time.monotonic() - started` |
| `tests/charness_cli/test_codex_cache_refresh.py` | 345 | deadline-poll | `deadline=time.monotonic() + 0.5,` |
| `tests/charness_cli/test_codex_cache_refresh.py` | 362 | deadline-poll | `deadline=time.monotonic() + 0.5,` |
| `tests/conftest.py` | 353 | deadline-poll | `deadline = time.monotonic() + 10` |
| `tests/conftest.py` | 360 | deadline-poll | `if result.returncode == 0 or time.monotonic() >= deadline:` |
| `tests/conftest.py` | 362 | deadline-poll | `time.sleep(1)` |
| `tests/seed_cache.py` | 182 | clock-as-data | `marker.write_text(str(time.time()), encoding="utf-8")` |
| `tests/test_agent_browser_runtime_guard.py` | 121 | controlled-child | `[sys.executable, "-c", "import time; time.sleep(120)"],` |
| `tests/test_markdown_preview_support.py` | 166 | controlled-child | `"time.sleep(2)",` |
| `tests/quality_gates/test_quality_runner_runtime_aggregate.py` | 191 | controlled-child | `"time.sleep(0.15)",` |
| `tests/quality_gates/test_reviewer_delivery_state_machine.py` | 325 | sleep-sync | `time.sleep(0.01)` |
| `tests/quality_gates/test_gate_summary_names_failures.py` | 101 | controlled-child | `_seed_gate(gate_repo, "import time\ntime.sleep(30)\n")` |
| `tests/quality_gates/test_gate_summary_names_failures.py` | 120 | deadline-poll | `deadline = time.monotonic() + 5` |
| `tests/quality_gates/test_gate_summary_names_failures.py` | 125 | deadline-poll | `while time.monotonic() < deadline:` |
| `tests/quality_gates/test_gate_summary_names_failures.py` | 131 | deadline-poll | `time.sleep(0.05)` |
| `tests/charness_cli/fixtures/fake_codex.py` | 92 | controlled-child | `time.sleep(0.015)` |
| `tests/charness_cli/test_worktree_audit.py` | 152 | clock-as-data | `old_time = time.time() - (30 * 86400)` |
| `tests/charness_cli/test_worktree_audit.py` | 170 | clock-as-data | `old_time = time.time() - (60 * 86400)` |
| `tests/test_script_timeout.py` | 36 | controlled-child | `"    time.sleep(0.2)",` |
| `tests/test_seed_cache.py` | 150 | sleep-sync | `time.sleep(0.2)` |
| `tests/test_web_fetch_cleanup.py` | 481 | deadline-poll | `deadline = time.monotonic() + _HANG_BACKSTOP_SECONDS` |
| `tests/test_web_fetch_cleanup.py` | 482 | deadline-poll | `while time.monotonic() < deadline:` |
| `tests/test_web_fetch_cleanup.py` | 495 | deadline-poll | `time.sleep(0.05)` |
| `tests/quality_gates/test_seed_cache_eviction.py` | 35 | clock-as-data | `now = time.time()` |
| `tests/quality_gates/test_seed_cache_eviction.py` | 55 | clock-as-data | `now = time.time()` |
| `tests/quality_gates/test_seed_cache_eviction.py` | 72 | clock-as-data | `_entry(tmp_path, current, used=time.time())` |
| `tests/quality_gates/test_seed_cache_eviction.py` | 87 | clock-as-data | `now = time.time()` |
| `tests/quality_gates/test_seed_cache_eviction.py` | 107 | clock-as-data | `_entry(tmp_path, name, used=time.time() + offset)` |
| `tests/quality_gates/test_seed_cache_eviction.py` | 129 | sleep-sync | `time.sleep(0.01)` |
| `tests/quality_gates/test_seed_cache_eviction.py` | 147 | clock-as-data | `now = time.time()` |
| `tests/quality_gates/test_seed_cache_eviction.py` | 168 | clock-as-data | `_entry(tmp_path, current, used=time.time())` |
| `tests/quality_gates/test_startup_probe_measure.py` | 32 | controlled-child | `f"time.sleep({probe_sleep_seconds})",` |
| `tests/quality_gates/test_standing_pytest_runner.py` | 932 | clock-as-data | `root=rootdir, prefix="pytest-", keep=3, consider_lock_dead_if_created_before=time.time() +` |
| `tests/quality_gates/test_standing_pytest_run_execution.py` | 375 | deadline-poll | `deadline = time.monotonic() + 15` |
| `tests/quality_gates/test_standing_pytest_run_execution.py` | 376 | deadline-poll | `while not started.exists() and time.monotonic() < deadline:` |
| `tests/quality_gates/test_standing_pytest_run_execution.py` | 377 | deadline-poll | `time.sleep(0.05)` |
| `tests/quality_gates/test_standing_pytest_run_execution.py` | 391 | sleep-sync | `time.sleep(4)` |
| `tests/quality_gates/test_cli_skill_surface.py` | 235 | controlled-child | `repo / "scripts" / "hang.py", "#!/usr/bin/env python3\nimport time\ntime.sleep(2)\n"` |
| `tests/quality_gates/test_cli_skill_surface.py` | 572 | controlled-child | `"deadline = time.monotonic() + 5.0\n"` |
| `tests/quality_gates/test_cli_skill_surface.py` | 573 | controlled-child | `"while not stop_path.exists() and time.monotonic() < deadline:\n"` |
| `tests/quality_gates/test_cli_skill_surface.py` | 574 | controlled-child | `"    time.sleep(0.01)\n"` |
| `tests/quality_gates/test_cli_skill_surface.py` | 600 | deadline-poll | `deadline = time.monotonic() + 6.0` |
| `tests/quality_gates/test_cli_skill_surface.py` | 601 | deadline-poll | `while time.monotonic() < deadline:` |
| `tests/quality_gates/test_cli_skill_surface.py` | 605 | deadline-poll | `time.sleep(0.01)` |
| `tests/quality_gates/test_cli_skill_surface.py` | 664 | controlled-child | `"time.sleep(600)\n",` |
| `tests/quality_gates/test_cli_skill_surface.py` | 722 | controlled-child | `"time.sleep(600)\n",` |
| `tests/quality_gates/test_cli_skill_surface.py` | 727 | elapsed-claim | `started = time.monotonic()` |
| `tests/quality_gates/test_cli_skill_surface.py` | 736 | elapsed-claim | `elapsed = time.monotonic() - started` |
| `tests/quality_gates/test_cli_skill_surface.py` | 778 | controlled-child | `"child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(600)'],\n"` |
| `tests/quality_gates/test_cli_skill_surface.py` | 837 | controlled-child | `"time.sleep(600)\n",` |
| `tests/quality_gates/test_cli_skill_surface.py` | 877 | controlled-child | `repo / "scripts" / "hang.py", "#!/usr/bin/env python3\nimport time\ntime.sleep(30)\n"` |
| `tests/quality_gates/test_quality_runner_progress.py` | 14 | controlled-child | `"import time\ntime.sleep(1)\nprint('slow validator finished')\n",` |
| `tests/quality_gates/fixtures/engine_gate.py` | 12 | controlled-child | `time.sleep(1.2)` |

## The #764 baseline failures, read from run 33631065064's log

- `test_cli_skill_surface.py::test_cli_skill_surface_bounds_the_drain_when_the_grandchild_escapes_the_group` and `::test_cli_skill_surface_keeps_partial_output_when_even_the_drain_times_out`: `assert len(escaped_pids) == attempts` read 1 == 2. The check's second attempt was killed before its escapee recorded a pid. Wall-clock: the 0.5 s probe timeout races the child's start.
- `test_markdown_preview_support.py::test_markdown_preview_retries_glow_with_file_stdout` and `::test_markdown_preview_uses_yaml_config_and_changed_only_scope`: `_isolated_path()` is the interpreter's directory. Locally `/usr/bin` also holds `git` and `script`; on the hosted runner the toolcache directory holds neither, so the `script` retry and `git diff` both vanish. Not wall-clock: an environment-shape leak.
- `test_issue_source_capture.py::test_cli_resolves_a_relative_snapshot_against_the_repo_root_it_was_given`: `run_gh` is patched on one module object and the CLI calls another; locally the real authenticated `gh` answers, in CI it exits 4 without a token. Not wall-clock: the patch never controlled the dependency.

The union across all six runs is 113 distinct tests; most were one-run environment failures on trees before #770. The baseline reproduction in the CI shape on the current tree decides which are live.
