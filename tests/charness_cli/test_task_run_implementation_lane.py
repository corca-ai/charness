"""Implementation-lane shaping for require-change task runs.

The carrier treats declared scope as an edit boundary, requires premise and
owner validation before editing, and records phase/blocker signals.
"""

from __future__ import annotations

from pathlib import Path

from scripts.task_run import task_run_git, task_run_scope
from scripts.task_run import task_run_lane_runner as lane_runner
from scripts.task_run import task_run_progress as prog
from tests.charness_cli.test_task_run_fixtures import _repo, _run


def test_implementation_prompt_separates_edit_scope_from_judgment() -> None:
    shaped = lane_runner.build_lane_prompt(
        "Fix the lease delta.",
        require_change=True,
        scopes=["gateway/lease.py"],
    )
    assert "implementation lane" in shaped
    assert "gateway/lease.py" in shaped
    assert "declared scope limits edits, not judgment" in shaped
    assert "Before editing" in shaped
    assert "option, check, or verifier" in shaped
    assert "real consumer" in shaped
    assert "meaningful contract or product-state difference" in shaped
    assert "fixture or simulation may own a bounded lower-level claim" in shaped
    assert "must never substitute for or be reported as product or release behavior" in shaped
    assert "requested product or release claim" in shaped
    assert "actual behavior owner" in shaped
    assert "EDITING" in shaped
    assert "BLOCKED: premise/scope mismatch - <concrete reason>" in shaped
    assert shaped.rstrip().endswith("Fix the lease delta.")


def test_implementation_prompt_does_not_prejudge_a_change_or_hurry_a_diff() -> None:
    requests = (
        "Add a --json mode even though the command always returns JSON.",
        "Use a synthetic Host fixture as release proof.",
    )
    for request in requests:
        shaped = lane_runner.build_lane_prompt(
            request,
            require_change=True,
            scopes=["tests/fixture.py"],
        )
        assert "not a critique lane" not in shaped
        assert "minimum contract reads" not in shaped
        assert "prioritize producing the first scoped diff" not in shaped
        assert shaped.index("Before editing") < shaped.index("EDITING")
        assert shaped.rstrip().endswith(request)


def test_non_require_change_prompt_passes_through_untouched() -> None:
    assert (
        lane_runner.build_lane_prompt(
            "Review this.", require_change=False, scopes=["a.py"]
        )
        == "Review this."
    )


def test_lane_progress_parses_phases_and_blocker() -> None:
    progress = prog.lane_progress(
        "thinking\nCONTRACT-READ\nmore\nEDITING\nBLOCKED: no lease event\n"
    )
    assert progress["phases"] == ["CONTRACT-READ", "EDITING"]
    assert progress["blocker"] == "no lease event"


def test_lane_progress_without_markers_is_empty() -> None:
    assert prog.lane_progress("analysis only\n") == {
        "phases": [],
        "blocker": None,
    }


def test_lane_progress_parses_markers_from_stderr() -> None:
    """Regression (#815 reopen): Codex emits progress on stderr while stdout
    (the delivery stream) stays empty, so stderr-only markers must count."""
    progress = prog.lane_progress("", "noise\nCONTRACT-READ\nmore\n")
    assert progress["phases"] == ["CONTRACT-READ"]
    assert progress["blocker"] is None


def test_stderr_only_markers_reach_receipt(tmp_path: Path) -> None:
    """End-to-end shape of the wi6 lane: empty delivery, CONTRACT-READ on
    stderr, zero scoped changes. The receipt must still name the phase and
    the stall instead of reporting empty progress."""
    repo = _repo(tmp_path)
    executable = _stub(tmp_path, 'echo "CONTRACT-READ" >&2\nexit 0')
    payload = _run(
        repo,
        tmp_path,
        executable,
        scopes=["gateway/lease.py"],
        require_change=True,
    )
    assert payload["status"] == "failed", payload
    assert payload["lane_progress"]["phases"] == ["CONTRACT-READ"]
    assert payload["lane_progress"]["blocker"] is None
    assert "without EDITING" in payload["next_step"]


def test_stderr_scan_is_bounded_to_tail(tmp_path: Path) -> None:
    stderr_log = tmp_path / "codex.stderr.log"
    stderr_log.write_bytes(b"CONTRACT-READ\n" + b"x" * (300 * 1024) + b"\nEDITING\n")
    text = prog._lane_stderr_text(
        tmp_path / "codex.stdout.log", stderr_log
    )
    assert "EDITING" in text
    assert "CONTRACT-READ" not in text


def test_missing_stderr_scans_as_no_markers(tmp_path: Path) -> None:
    assert (
        prog._lane_stderr_text(
            tmp_path / "stdout.log", tmp_path / "absent.log"
        )
        == ""
    )


def test_no_progress_stop_parses_as_blocker() -> None:
    progress = prog.lane_progress(
        "", "CONTRACT-READ\nNO-PROGRESS-STOP: no EDITING and no scoped diff\n"
    )
    assert progress["phases"] == ["CONTRACT-READ"]
    assert progress["blocker"] == "no EDITING and no scoped diff"


def test_no_progress_stop_due_needs_spent_budget() -> None:
    due = prog.no_progress_stop_due(
        phases=["CONTRACT-READ"],
        contract_read_at=1000.0,
        now=1000.0 + 299.0,
        budget_seconds=300.0,
        diff_present=False,
    )
    assert due is None
    overdue = prog.no_progress_stop_due(
        phases=["CONTRACT-READ"],
        contract_read_at=1000.0,
        now=1000.0 + 300.0,
        budget_seconds=300.0,
        diff_present=False,
    )
    assert overdue is not None and "CONTRACT-READ" in overdue


def test_no_progress_stop_spares_editing_diff_and_disabled() -> None:
    kwargs = {"contract_read_at": 0.0, "now": 9999.0, "budget_seconds": 300.0}
    assert (
        prog.no_progress_stop_due(
            phases=["CONTRACT-READ", "EDITING"], diff_present=False, **kwargs
        )
        is None
    )
    assert (
        prog.no_progress_stop_due(
            phases=["CONTRACT-READ"], diff_present=True, **kwargs
        )
        is None
    )
    assert (
        prog.no_progress_stop_due(phases=[], diff_present=False, **kwargs)
        is None
    )
    assert (
        prog.no_progress_stop_due(
            phases=["CONTRACT-READ"],
            contract_read_at=0.0,
            now=9999.0,
            budget_seconds=0.0,
            diff_present=False,
        )
        is None
    )


def _watch(tmp_path: Path, *, budget: float = 100.0) -> prog.LaneProgressWatch:
    repo = _repo(tmp_path)
    base_sha = task_run_git._git_output(repo, "rev-parse", "HEAD").strip()
    specs = task_run_scope.resolve_scope_specs(repo, ["module.py"], base_sha)
    return prog.LaneProgressWatch(
        stdout_log=tmp_path / "codex.stdout.log",
        stderr_log=tmp_path / "codex.stderr.log",
        worktree=repo,
        base_sha=base_sha,
        scope_specs=specs,
        budget_seconds=budget,
        poll_seconds=15.0,
    )


def _drive(watch: prog.LaneProgressWatch) -> list:
    # White-box drive: tick() is the deterministic core; only the thin _run
    # loop touches wall-clock time, so tests never start the thread.
    emitted: list = []
    watch._started_at = 0.0
    watch._emit = lambda phases, elapsed: emitted.append((list(phases), elapsed))
    return emitted


def test_watch_tick_relays_phases_then_stops_on_spent_budget(
    tmp_path: Path,
) -> None:
    watch = _watch(tmp_path)
    emitted = _drive(watch)
    watch._stderr_log.write_text("noise\nCONTRACT-READ\n", encoding="utf-8")
    assert watch.tick(1000.0) is None
    assert ([["CONTRACT-READ"]], [1000.0]) == (
        [phases for phases, _ in emitted],
        [elapsed for _, elapsed in emitted],
    )
    assert watch.tick(1000.0 + 99.0) is None
    reason = watch.tick(1000.0 + 100.0)
    assert reason is not None and "no scoped diff" in reason


def test_watch_tick_spares_editing_lane(tmp_path: Path) -> None:
    watch = _watch(tmp_path)
    _drive(watch)
    watch._stderr_log.write_text("CONTRACT-READ\nEDITING\n", encoding="utf-8")
    assert watch.tick(0.0) is None
    assert watch.tick(10_000.0) is None


def test_watch_keeps_phases_that_aged_out_of_tail(tmp_path: Path) -> None:
    watch = _watch(tmp_path)
    _drive(watch)
    watch._stderr_log.write_text("CONTRACT-READ\n", encoding="utf-8")
    assert watch.tick(0.0) is None
    watch._stderr_log.write_bytes(b"x" * (70 * 1024))
    reason = watch.tick(1000.0)
    assert reason is not None and "no scoped diff" in reason


def test_watch_tick_spares_lane_with_real_scoped_diff(tmp_path: Path) -> None:
    watch = _watch(tmp_path)
    _drive(watch)
    watch._stderr_log.write_text("CONTRACT-READ\n", encoding="utf-8")
    assert watch.tick(0.0) is None
    (watch._worktree / "module.py").write_text("VALUE = 2\n", encoding="utf-8")
    assert watch.tick(10_000.0) is None


def test_watch_tick_gives_blocker_time_to_exit(tmp_path: Path) -> None:
    watch = _watch(tmp_path)
    _drive(watch)
    watch._stderr_log.write_text(
        "CONTRACT-READ\nBLOCKED: scope mismatch - real owner elsewhere\n",
        encoding="utf-8",
    )
    assert watch.tick(0.0) is None
    assert watch.tick(59.0) is None


def test_watch_fire_records_marker_and_kills(tmp_path: Path) -> None:
    watch = _watch(tmp_path)
    killed: list = []
    watch._kill = lambda: killed.append("killed")
    watch.fire("require-change lane produced no EDITING")
    assert killed == ["killed"]
    marker = watch._stderr_log.read_text(encoding="utf-8")
    assert marker.startswith("NO-PROGRESS-STOP: require-change lane")
    progress = prog.lane_progress("", marker)
    assert progress["blocker"] == "require-change lane produced no EDITING"


def test_scoped_diff_present_reads_dirty_tree(tmp_path: Path) -> None:
    watch = _watch(tmp_path)
    assert (
        prog.scoped_diff_present(
            watch._worktree, watch._base_sha, watch._scope_specs
        )
        is False
    )
    (watch._worktree / "module.py").write_text("VALUE = 2\n", encoding="utf-8")
    assert (
        prog.scoped_diff_present(
            watch._worktree, watch._base_sha, watch._scope_specs
        )
        is True
    )


def test_scoped_diff_present_is_unknown_when_unobservable(tmp_path: Path) -> None:
    assert prog.scoped_diff_present(tmp_path / "absent", "deadbeef", []) is None


def test_no_progress_stop_due_spares_unobservable_diff() -> None:
    assert (
        prog.no_progress_stop_due(
            phases=["CONTRACT-READ"],
            contract_read_at=0.0,
            now=9999.0,
            budget_seconds=300.0,
            diff_present=None,
        )
        is None
    )


def test_watch_tick_spares_overdue_lane_it_cannot_observe(tmp_path: Path) -> None:
    watch = _watch(tmp_path)
    _drive(watch)
    watch._stderr_log.write_text("CONTRACT-READ\n", encoding="utf-8")
    assert watch.tick(0.0) is None
    (watch._worktree / ".git").rename(watch._worktree / ".git-broken")
    try:
        assert prog.scoped_diff_present(
            watch._worktree, watch._base_sha, watch._scope_specs
        ) is None
        assert watch.tick(10_000.0) is None
    finally:
        (watch._worktree / ".git-broken").rename(watch._worktree / ".git")


def test_stop_mechanisms_are_independent_in_receipt(tmp_path: Path) -> None:
    watch = _watch(tmp_path)
    receipt = watch.receipt()
    assert receipt["stop_enabled"] is True
    assert receipt["linger_stop_enabled"] is True
    assert receipt["blocked_grace_seconds"] == prog.DEFAULT_BLOCKED_GRACE_SECONDS

    watch._stderr_log.write_text("CONTRACT-READ\n", encoding="utf-8")
    _drive(watch)
    watch._budget_seconds = 0
    assert watch.tick(10_000.0) is None
    assert watch.receipt()["stop_enabled"] is False
    assert watch.receipt()["linger_stop_enabled"] is True

    watch._stderr_log.write_text(
        "CONTRACT-READ\nBLOCKED: scope mismatch - real owner elsewhere\n",
        encoding="utf-8",
    )
    assert watch.tick(10_000.0) is None
    reason = watch.tick(10_000.0 + 60.0)
    assert reason is not None and "kept running" in reason


def test_non_positive_grace_turns_linger_stop_off(tmp_path: Path) -> None:
    watch = _watch(tmp_path)
    watch._blocked_grace_seconds = 0
    _drive(watch)
    watch._stderr_log.write_text("BLOCKED: scope mismatch\n", encoding="utf-8")
    assert watch.tick(0.0) is None
    assert watch.tick(10_000.0) is None
    assert watch.receipt()["linger_stop_enabled"] is False


def test_lingering_blocked_lane_is_stopped_after_grace(tmp_path: Path) -> None:
    watch = _watch(tmp_path)
    _drive(watch)
    watch._stderr_log.write_text(
        "CONTRACT-READ\nBLOCKED: scope mismatch - real owner elsewhere\n",
        encoding="utf-8",
    )
    assert watch.tick(0.0) is None
    assert watch.tick(59.0) is None
    reason = watch.tick(60.0)
    assert reason is not None and "kept running" in reason


def test_guard_blocker_covers_lost_transcript_marker() -> None:
    from scripts.task_run import task_run_lane_runner as lane_runner

    payload: dict = {}
    blockers: list = []
    lane_runner.apply_lane_receipt(
        payload,
        blockers,
        delivery={"text": ""},
        require_change=True,
        scope={"changed_paths": [], "disallowed_paths": []},
        stderr_text="",
        guard_phases=["CONTRACT-READ"],
        guard_blocker="require-change lane produced no EDITING",
    )
    assert payload["lane_progress"]["blocker"] == (
        "require-change lane produced no EDITING"
    )
    assert blockers == [
        "lane reported blocker: require-change lane produced no EDITING"
    ]


def test_transcript_blocker_wins_over_guard_blocker() -> None:
    from scripts.task_run import task_run_lane_runner as lane_runner

    payload: dict = {}
    blockers: list = []
    lane_runner.apply_lane_receipt(
        payload,
        blockers,
        delivery={"text": "BLOCKED: lease event never fires\n"},
        require_change=True,
        scope={"changed_paths": [], "disallowed_paths": []},
        guard_blocker="require-change lane produced no EDITING",
    )
    assert payload["lane_progress"]["blocker"] == "lease event never fires"


def test_evicted_blocker_still_arms_linger_stop(tmp_path: Path) -> None:
    watch = _watch(tmp_path)
    _drive(watch)
    watch._stderr_log.write_text(
        "BLOCKED: scope mismatch - real owner elsewhere\n", encoding="utf-8"
    )
    assert watch.tick(0.0) is None
    watch._stderr_log.write_bytes(b"x" * (70 * 1024))
    assert watch.tick(59.0) is None
    reason = watch.tick(60.0)
    assert reason is not None and "kept running" in reason
    assert "scope mismatch" in reason


def test_lingering_blocked_lane_is_killed_live_and_receipted(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv(prog.BLOCKED_GRACE_ENV, "1")
    monkeypatch.setenv(prog.PROGRESS_POLL_ENV, "0.05")
    repo = _repo(tmp_path)
    executable = _stub(
        tmp_path, 'echo "BLOCKED: scope mismatch - real owner elsewhere" >&2\nsleep 300'
    )
    payload = _run(
        repo,
        tmp_path,
        executable,
        scopes=["gateway/lease.py"],
        require_change=True,
        timeout_seconds=60,
    )
    assert payload["status"] == "failed", payload
    assert "kept running" in (payload["execution"].get("progress_stopped") or "")
    assert payload["lane_progress"]["blocker"] == (
        "scope mismatch - real owner elsewhere"
    )
    assert payload["progress_guard"]["stop_reason"] is not None


def test_persisted_candidate_retires_uncommitted_claim(tmp_path: Path) -> None:
    """#823: a lane that declares BLOCKED as uncommitted but leaves a useful
    dirty candidate must receipt an explicit persisted-for-review disposition,
    not a stale uncommitted claim beside a persisted commit."""
    repo = _repo(tmp_path)
    executable = _stub(
        tmp_path,
        'echo "CONTRACT-READ"\n'
        'echo "EDITING"\n'
        "printf 'VALUE = 2\\n' > module.py\n"
        'echo "BLOCKED: commit gate failed - candidate staged but uncommitted"\n'
        'echo "done"\n',
    )
    payload = _run(
        repo,
        tmp_path,
        executable,
        scopes=["module.py"],
        require_change=True,
    )
    assert payload["status"] == "validated-partial-result", payload
    persist = payload["candidate"]["persist"]
    assert persist["status"] == "committed"
    assert persist["after_block"] is True
    assert payload["lane_progress"]["blocker"] == (
        "commit gate failed - candidate staged but uncommitted"
    )
    assert "persisted for review" in payload["next_step"]
    assert "correctness unverified" in payload["next_step"]
    assert "ineligible" in payload["next_step"]


def test_clean_persist_records_no_after_block(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _stub(
        tmp_path,
        'echo "CONTRACT-READ"\n'
        'echo "EDITING"\n'
        "printf 'VALUE = 2\\n' > module.py\n"
        'echo "done"\n',
    )
    payload = _run(
        repo,
        tmp_path,
        executable,
        scopes=["module.py"],
        require_change=True,
    )
    persist = payload["candidate"].get("persist") or {}
    assert "after_block" not in persist
    assert "persisted for review" not in payload["next_step"]


def test_stalled_lane_is_killed_live_and_receipted(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(prog.NO_PROGRESS_BUDGET_ENV, "1")
    monkeypatch.setenv(prog.PROGRESS_POLL_ENV, "0.05")
    repo = _repo(tmp_path)
    executable = _stub(tmp_path, 'echo "CONTRACT-READ" >&2\nsleep 300')
    payload = _run(
        repo,
        tmp_path,
        executable,
        scopes=["gateway/lease.py"],
        require_change=True,
        timeout_seconds=60,
    )
    assert payload["status"] == "failed", payload
    assert "no EDITING" in (payload["execution"].get("progress_stopped") or "")
    assert payload["lane_progress"]["phases"] == ["CONTRACT-READ"]
    assert "no EDITING" in (payload["lane_progress"]["blocker"] or "")
    assert payload["candidate"]["status"] == "absent"
    assert payload["progress_guard"]["stop_reason"] is not None


def test_receipt_merges_guard_phases_missing_from_transcript() -> None:
    from scripts.task_run import task_run_lane_runner as lane_runner

    payload: dict = {}
    blockers: list = []
    lane_runner.apply_lane_receipt(
        payload,
        blockers,
        delivery={"text": "analysis only\n"},
        require_change=True,
        scope={"changed_paths": [], "disallowed_paths": []},
        stderr_text="",
        guard_phases=["CONTRACT-READ", "EDITING"],
    )
    assert payload["lane_progress"]["phases"] == ["CONTRACT-READ", "EDITING"]
    assert payload["lane_progress"]["merged_guard_phases"] == [
        "CONTRACT-READ",
        "EDITING",
    ]
    assert payload["lane_progress"]["blocker"] is None
    assert blockers == []


def test_stderr_sibling_fallback_is_used_without_explicit_log(
    tmp_path: Path,
) -> None:
    stdout_log = tmp_path / "codex.stdout.log"
    stdout_log.write_text("", encoding="utf-8")
    (tmp_path / "codex.stderr.log").write_text("CONTRACT-READ\n", encoding="utf-8")
    assert prog._lane_stderr_text(stdout_log, None) == "CONTRACT-READ\n"


def test_stderr_unreadable_scans_as_no_markers(
    tmp_path: Path, monkeypatch
) -> None:
    from pathlib import Path as _Path

    stderr_log = tmp_path / "codex.stderr.log"
    stderr_log.write_text("CONTRACT-READ\n", encoding="utf-8")

    def _raise(self, *args, **kwargs):
        raise OSError("unreadable transcript")

    monkeypatch.setattr(_Path, "read_bytes", _raise)
    assert prog._lane_stderr_text(tmp_path / "o.log", stderr_log) == ""
    assert prog._tail_text(stderr_log) == ""


def test_nonfinite_durations_fall_back_to_defaults(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv(prog.NO_PROGRESS_BUDGET_ENV, "nan")
    monkeypatch.setenv(prog.BLOCKED_GRACE_ENV, "inf")
    monkeypatch.setenv(prog.PROGRESS_POLL_ENV, "-inf")
    watch = prog.build_progress_watch(
        require_change=True,
        stdout_log=tmp_path / "o.log",
        stderr_log=tmp_path / "e.log",
        worktree=tmp_path,
        base_sha="deadbeef",
        scope_specs=[],
    )
    assert watch is not None
    receipt = watch.receipt()
    assert receipt["budget_seconds"] == prog.DEFAULT_NO_PROGRESS_BUDGET_SECONDS
    assert receipt["stop_enabled"] is True
    assert receipt["linger_stop_enabled"] is True


def test_invalid_budget_env_falls_back_to_default(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv(prog.NO_PROGRESS_BUDGET_ENV, "not-a-number")
    watch = prog.build_progress_watch(
        require_change=True,
        stdout_log=tmp_path / "o.log",
        stderr_log=tmp_path / "e.log",
        worktree=tmp_path,
        base_sha="deadbeef",
        scope_specs=[],
    )
    assert watch is not None
    assert watch.receipt()["budget_seconds"] == prog.DEFAULT_NO_PROGRESS_BUDGET_SECONDS


def test_watch_tick_without_markers_is_quiet(tmp_path: Path) -> None:
    watch = _watch(tmp_path)
    emitted = _drive(watch)
    assert watch.tick(1000.0) is None
    assert emitted == []
    assert watch.receipt()["last_phases"] == []


def test_watch_fire_survives_unwritable_transcript(tmp_path: Path) -> None:
    watch = _watch(tmp_path)
    killed: list = []
    watch._kill = lambda: killed.append("killed")
    watch._stderr_log = tmp_path
    watch.fire("require-change lane produced no EDITING")
    assert killed == ["killed"]


def test_bootstrap_inserts_repo_root_when_missing(monkeypatch) -> None:
    import importlib
    import sys

    import scripts.task_run.task_run_progress as prog_mod

    root = str(Path(prog_mod.__file__).resolve().parents[2])
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != root])
    assert root not in sys.path
    importlib.reload(prog_mod)
    assert root in sys.path


def test_watch_run_relays_phases_live(tmp_path: Path) -> None:
    import threading

    watch = _watch(tmp_path)
    watch._stderr_log.write_text("CONTRACT-READ\n", encoding="utf-8")
    relayed: list = []
    empty = threading.Event()

    def _emit(phases, elapsed):
        relayed.append((list(phases), elapsed))
        empty.set()

    watch._poll_seconds = 0.05
    watch.start(emit=_emit, kill=lambda: None)
    try:
        assert empty.wait(timeout=30)
    finally:
        watch.stop()
    assert [phases for phases, _ in relayed] == [["CONTRACT-READ"]]
    assert watch.stop_reason is None
    assert watch._thread is not None and not watch._thread.is_alive()


def test_watch_run_survives_failing_poll(tmp_path: Path) -> None:
    import threading

    watch = _watch(tmp_path)
    polls: list = []
    continued = threading.Event()

    def _boom(now):
        polls.append(now)
        if len(polls) >= 2:
            continued.set()
        raise RuntimeError("unreadable log")

    watch.tick = _boom  # type: ignore[method-assign]
    watch._poll_seconds = 0.05
    watch.start(emit=lambda phases, elapsed: None, kill=lambda: None)
    try:
        assert continued.wait(timeout=30)
    finally:
        watch.stop()
    assert watch.stop_reason is None


def test_watch_run_records_stop_before_failing_fire(tmp_path: Path) -> None:
    import threading

    watch = _watch(tmp_path)
    fired: list = []
    failed = threading.Event()

    def _stop(now):
        return "require-change lane produced no EDITING"

    def _fail(reason):
        fired.append(reason)
        failed.set()
        raise RuntimeError("cannot append marker")

    watch.tick = _stop  # type: ignore[method-assign]
    watch.fire = _fail  # type: ignore[method-assign]
    watch._poll_seconds = 0.05
    watch.start(emit=lambda phases, elapsed: None, kill=lambda: None)
    try:
        assert failed.wait(timeout=30)
    finally:
        watch.stop()
    assert fired == ["require-change lane produced no EDITING"]
    assert watch.stop_reason == "require-change lane produced no EDITING"


def test_build_progress_watch_off_without_require_change(tmp_path: Path) -> None:
    assert (
        prog.build_progress_watch(
            require_change=False,
            stdout_log=tmp_path / "o.log",
            stderr_log=tmp_path / "e.log",
            worktree=tmp_path,
            base_sha="deadbeef",
            scope_specs=[],
        )
        is None
    )


def test_scope_mismatch_outside_declared_scope_is_typed_refusal(tmp_path: Path) -> None:
    """The discovered real test owner outside declared scope must produce an
    early typed BLOCKED refusal, not adjacent-file exploration."""
    repo = _repo(tmp_path)
    executable = _stub(
        tmp_path,
        'echo "CONTRACT-READ"\n'
        "echo \"BLOCKED: scope mismatch - real owner "
        "scripts/run-unit-tests-fast-split.test.ts is outside declared scope\"\n"
        "exit 0",
    )
    payload = _run(
        repo,
        tmp_path,
        executable,
        scopes=["gateway/lease.py"],
        require_change=True,
    )
    assert payload["status"] == "failed", payload
    assert "scope mismatch" in (payload["lane_progress"]["blocker"] or "")
    assert "lane reported blocker" in payload["next_step"]


def _stub(tmp_path: Path, body: str) -> Path:
    executable = tmp_path / "codex"
    executable.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
    executable.chmod(0o755)
    return executable


def test_blocked_lane_records_typed_blocker(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _stub(
        tmp_path,
        'echo "CONTRACT-READ"\necho "BLOCKED: lease event never fires"\nexit 0',
    )
    payload = _run(
        repo,
        tmp_path,
        executable,
        scopes=["gateway/lease.py"],
        require_change=True,
    )
    assert payload["status"] == "failed", payload
    assert payload["lane_progress"]["blocker"] == "lease event never fires"
    assert "lane reported blocker" in payload["next_step"]


def test_stalled_lane_names_missing_editing(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _stub(tmp_path, 'echo "CONTRACT-READ"\nexit 0')
    payload = _run(
        repo,
        tmp_path,
        executable,
        scopes=["gateway/lease.py"],
        require_change=True,
    )
    assert payload["status"] == "failed", payload
    assert payload["lane_progress"]["phases"] == ["CONTRACT-READ"]
    assert payload["lane_progress"]["blocker"] is None
    assert "without EDITING" in payload["next_step"]


def test_editing_lane_records_phases_and_completes(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _stub(
        tmp_path,
        "echo CONTRACT-READ\necho EDITING\n"
        "echo delta > worktree-file.txt\n"
        "echo TESTING\nexit 0",
    )
    payload = _run(
        repo,
        tmp_path,
        executable,
        scopes=["worktree-file.txt"],
        require_change=True,
    )
    assert payload["status"] == "completed", payload
    assert payload["lane_progress"]["phases"] == [
        "CONTRACT-READ",
        "EDITING",
        "TESTING",
    ]
    assert payload["lane_progress"]["blocker"] is None


def test_execute_codex_records_progress_stop_from_the_lane_watch(
    tmp_path: Path, monkeypatch
) -> None:
    from types import SimpleNamespace

    from scripts.task_run import task_run_execution

    stdout_log = tmp_path / "stdout.log"
    stderr_log = tmp_path / "stderr.log"

    def finished_phase(*_args, **_kwargs):
        return SimpleNamespace(timed_out=False, returncode=0)

    monkeypatch.setattr(task_run_execution, "run_monitored_phase", finished_phase)

    watch = SimpleNamespace(
        stop_reason="require-change lane produced no EDITING",
        start=lambda **_kwargs: None,
        stop=lambda: None,
    )
    result = task_run_execution._execute_codex(
        ["codex"],
        prompt="stop",
        target_path=tmp_path,
        configured_env={},
        stdout_log=stdout_log,
        stderr_log=stderr_log,
        timeout_seconds=30,
        lane_watch=watch,
    )

    assert result["exit_code"] == 0
    assert result["progress_stopped"] == "require-change lane produced no EDITING"
