"""Muse `--json` stream observability for `charness task run` (#886).

A controlled fake muse emits the real binary's measured JSONL envelopes
(`run.output.delta`, `task.lifecycle.status`, `run_terminal`, probed on Muse
`1.4.1-R4503.1`): argv shape, nested progress events split across chunks,
terminal delivery separate from the JSONL transport, stream-retry cause
retention, and unchanged no-progress semantics are verified together through
the canonical task boundary. Raising the timeout is not the fix.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from scripts.task_run import task_run_execution as execution
from scripts.task_run import task_run_muse_events as muse_events
from scripts.task_run import task_run_progress as prog
from scripts.task_run import task_run_state as state

from .test_task_run_fixtures import _repo, _run


def _envelope(payload_type: str, payload: dict) -> dict:
    return {"payload_type": payload_type, "payload": payload}


def _delta(text: str) -> dict:
    return _envelope("run.output.delta", {"kind": "run_output_delta", "text": text})


def _status(message: str, phase: str, facet: dict | None = None) -> dict:
    facets = [facet] if facet is not None else []
    return _envelope(
        "task.lifecycle.status",
        {
            "kind": "task_lifecycle",
            "event": {
                "kind": "status",
                "message": message,
                "details": {"phase": phase, "facets": facets},
            },
        },
    )


def _terminal(text: str, terminal: str = "completed", reason: str | None = None) -> dict:
    return _envelope(
        f"run.terminal.{terminal}",
        {"kind": "run_terminal", "terminal": terminal, "text": text, "reason": reason},
    )


def _failed_task(reason: str) -> dict:
    return _envelope(
        "task.lifecycle.failed",
        {"kind": "task_lifecycle", "event": {"kind": "failed", "reason": reason}},
    )


def _fake_muse(
    tmp_path: Path,
    *,
    name: str = "muse",
    events: list[dict],
    edit: str | None = None,
    exit_code: int = 0,
    stderr_lines: list[str] | None = None,
    sleeps: list[float] | None = None,
) -> tuple[Path, Path]:
    """Write a fake muse emitting fixed JSONL envelopes; return (exe, argv_file)."""
    argv_file = tmp_path / f"{name}-args.txt"
    executable = tmp_path / name
    script = (
        f"#!{sys.executable}\n"
        "import json, pathlib, sys, time\n"
        f"pathlib.Path({str(argv_file)!r}).write_text("
        "'\\n'.join(sys.argv[1:]) + '\\n', encoding='utf-8')\n"
        + (
            f"pathlib.Path('module.py').write_text({edit!r}, encoding='utf-8')\n"
            if edit is not None
            else ""
        )
        + "".join(
            f"print({event!r}, flush=True)\n" + (f"time.sleep({delay})\n" if delay else "")
            for event, delay in zip(
                [json.dumps(event) for event in events],
                list(sleeps or []) + [0.0] * len(events),
            )
        )
        + "".join(
            f"print({line!r}, file=sys.stderr, flush=True)\n" for line in (stderr_lines or [])
        )
        + f"sys.exit({exit_code})\n"
    )
    executable.write_text(script, encoding="utf-8")
    executable.chmod(0o755)
    return executable, argv_file


def test_muse_json_progress_reaches_receipt_with_terminal_report(
    tmp_path: Path, monkeypatch
) -> None:
    """argv, split-chunk phases, terminal delivery, and scoped-diff observation."""
    monkeypatch.setenv(prog.PROGRESS_POLL_ENV, "0.05")
    repo = _repo(tmp_path)
    report = "CONTRACT-READ\nEDITING\nTESTING\nShared-primitive candidates: none\n"
    events = [
        _envelope("run.lifecycle.started", {"kind": "run_started"}),
        _status("opening meta model stream attempt 1/10", "opening_stream"),
        # The marker line is split across two streamed chunks.
        _delta("CONTRACT-"),
        _delta("READ\nvalidated the contract\n"),
        _delta("EDITING\n"),
        _delta("TESTING\nran focused tests\n"),
        _terminal(report),
    ]
    executable, argv_file = _fake_muse(
        tmp_path,
        events=events,
        edit="VALUE = 2\n",
        sleeps=[0.0, 0.3, 0.0, 0.3, 0.3, 0.3, 0.0],
    )
    payload = _run(repo, tmp_path, executable, executor="muse", effort="xhigh", timeout_seconds=120)

    assert payload["status"] == "completed", payload
    args = argv_file.read_text(encoding="utf-8").splitlines()
    assert args[:3] == ["exec", "--json", "--reasoning-effort"]
    assert args[args.index("--reasoning-effort") + 1] == "xhigh"
    assert "--disable-approval" in args
    assert "--trust-workspace" in args
    assert args[args.index("--workspace") + 1] == payload["worktree_path"]
    assert payload["lane_progress"]["phases"] == ["CONTRACT-READ", "EDITING", "TESTING"]
    assert payload["progress_guard"]["last_phases"] == ["CONTRACT-READ", "EDITING", "TESTING"]
    snapshot = payload["progress_guard"]["first_scoped_diff"]
    assert snapshot["observed"] is True
    assert snapshot["changed_paths"] == ["module.py"]

    delivery = payload["result_delivery"]
    assert delivery["status"] == "delivered", delivery
    full_report = Path(delivery["full_report"]["path"]).read_text(encoding="utf-8")
    assert full_report == report
    assert "run.output.delta" not in full_report
    events_log = Path(payload["logs"]["stdout"]).with_name("muse.events.log")
    raw = events_log.read_text(encoding="utf-8")
    assert "run_terminal" in raw

    diagnostics = payload["execution"]["stream_diagnostics"]
    assert diagnostics["terminal"] == "completed"
    assert diagnostics["retries"] == 0
    assert diagnostics["cause_status"] == "not-applicable"


def test_muse_no_progress_stop_survives_json_transport(tmp_path: Path, monkeypatch) -> None:
    """CONTRACT-READ without EDITING still stops the lane after the budget."""
    monkeypatch.setenv(prog.NO_PROGRESS_BUDGET_ENV, "1")
    monkeypatch.setenv(prog.PROGRESS_POLL_ENV, "0.05")
    repo = _repo(tmp_path)
    executable, argv_file = _fake_muse(
        tmp_path,
        name="muse-stall",
        events=[_delta("CONTRACT-READ\nstill exploring\n")],
        sleeps=[300.0],
    )
    payload = _run(
        repo,
        tmp_path,
        executable,
        executor="muse",
        effort="high",
        scopes=["gateway/lease.py"],
        require_change=True,
        timeout_seconds=60,
    )

    assert payload["status"] == "failed", payload
    assert "exec" in argv_file.read_text(encoding="utf-8").splitlines()
    assert "--json" in argv_file.read_text(encoding="utf-8").splitlines()
    assert "no EDITING" in (payload["execution"].get("progress_stopped") or "")
    assert payload["lane_progress"]["phases"] == ["CONTRACT-READ"]
    assert "no EDITING" in (payload["lane_progress"]["blocker"] or "")
    assert payload["progress_guard"]["stop_reason"] is not None
    assert payload["candidate"]["status"] == "absent"


def test_muse_stream_retry_cause_reaches_failure_receipt(tmp_path: Path) -> None:
    """Structured retry facets and the terminal reason survive onto the receipt."""
    repo = _repo(tmp_path)
    reason = "transport error: error sending request for url (http://127.0.0.1:9/responses)"
    events = [
        _status("opening meta model stream attempt 1/10", "opening_stream"),
        _status(
            "retrying meta model stream in 250ms (attempt 2/4)",
            "retry_scheduled",
            {
                "kind": "external_attempt",
                "attempt": 2,
                "max_attempts": 4,
                "operation": "model.response",
                "system": "meta",
                "error_kind": "transport",
                "retry_delay_ms": 250,
                "next_attempt": 3,
            },
        ),
        _failed_task(reason),
        _terminal("", terminal="failed", reason=reason),
    ]
    executable, _argv_file = _fake_muse(tmp_path, events=events, exit_code=1)
    payload = _run(
        repo,
        tmp_path,
        executable,
        executor="muse",
        effort="high",
        require_change=False,
        timeout_seconds=60,
    )

    diagnostics = payload["execution"]["stream_diagnostics"]
    assert diagnostics["source"] == "events"
    assert diagnostics["retries"] == 1
    assert diagnostics["last_phase"] == "retry_scheduled"
    assert diagnostics["last_error_kind"] == "transport"
    assert diagnostics["last_attempt"] == 2
    assert diagnostics["last_max_attempts"] == 4
    assert diagnostics["terminal"] == "failed"
    assert diagnostics["terminal_reason"] == reason
    assert diagnostics["cause_status"] == "provided"
    assert payload["failure"]["kind"] == "executor-error"
    assert payload["failure"]["message"] == reason
    assert payload["result_delivery"]["status"] == "non-delivery"


def test_muse_retry_without_cause_names_upstream_gap(tmp_path: Path) -> None:
    """Bare retries with no cause read as an explicit upstream gap, not silence."""
    repo = _repo(tmp_path)
    events = [
        _status("opening meta model stream attempt 1/10", "opening_stream"),
        _status("retrying meta model stream in 1000ms (attempt 2/10)", "retry_scheduled"),
        _terminal("", terminal="failed", reason=None),
    ]
    executable, _argv_file = _fake_muse(
        tmp_path,
        events=events,
        exit_code=1,
        stderr_lines=["muse: retrying meta model stream in 1000ms (attempt 2/10)"],
    )
    payload = _run(
        repo,
        tmp_path,
        executable,
        executor="muse",
        effort="high",
        require_change=False,
        timeout_seconds=60,
    )

    diagnostics = payload["execution"]["stream_diagnostics"]
    assert diagnostics["retries"] == 1
    assert diagnostics["terminal_reason"] is None
    assert diagnostics["cause_status"] == "unavailable-upstream"


def test_lane_progress_accumulates_split_muse_deltas() -> None:
    """A marker split across streamed chunks still parses as a phase."""
    stdout = "\n".join(
        json.dumps(event)
        for event in (
            _delta("CONTRACT-"),
            _delta("READ\n"),
            _status("opening meta model stream attempt 1/10", "opening_stream"),
        )
    )
    progress = prog.lane_progress(stdout, "")
    assert progress["phases"] == ["CONTRACT-READ"]
    assert progress["blocker"] is None


def test_stream_diagnostics_falls_back_to_stderr_retries() -> None:
    """Transcripts without structured events still count stderr retry notices."""
    diagnostics = muse_events.stream_diagnostics(
        "plain lane output\n",
        "muse: workspace trust: trusted source=run-flag\n"
        "muse: retrying meta model stream in 1000ms (attempt 2/10)\n",
    )
    assert diagnostics["source"] == "stderr"
    assert diagnostics["retries"] == 1
    assert diagnostics["cause_status"] == "unavailable-upstream"
    assert muse_events.stream_diagnostics("plain\n", "")["source"] == "none"


def test_stream_retry_count_is_best_of_both_signals() -> None:
    """Status events without retry facets do not hide stderr retry notices."""
    events = "\n".join(
        json.dumps(event)
        for event in (_status("opening meta model stream attempt 1/10", "opening_stream"),)
    )
    diagnostics = muse_events.stream_diagnostics(
        events,
        "muse: retrying meta model stream in 1000ms (attempt 2/10)\n"
        "muse: retrying meta model stream in 2000ms (attempt 3/10)\n",
    )
    assert diagnostics["retries"] == 2
    assert diagnostics["cause_status"] == "unavailable-upstream"


def test_stream_diagnostics_reads_past_old_tail_cuts(tmp_path: Path) -> None:
    """Early retries survive a long lane's events log, not just its tail."""
    log_dir = tmp_path / "lane-logs"
    log_dir.mkdir()
    stdout_log = log_dir / "muse.stdout.log"
    stderr_log = log_dir / "muse.stderr.log"
    event_log = log_dir / "muse.events.log"
    event_log.write_text(
        '{"padding": "' + "x" * 1024 + '"}\n',
        encoding="utf-8",
    )
    with event_log.open("a", encoding="utf-8") as handle:
        for _ in range(1200):
            handle.write('{"padding": "' + "y" * 1024 + '"}\n')
        handle.write(
            json.dumps(
                _status(
                    "retrying meta model stream in 250ms (attempt 2/4)",
                    "retry_scheduled",
                    {"kind": "external_attempt", "error_kind": "transport"},
                )
            )
            + "\n"
        )
        handle.write(json.dumps(_terminal("late report\n")) + "\n")
    assert event_log.stat().st_size > 1024 * 1024
    stdout_log.write_text("late report\n", encoding="utf-8")
    stderr_log.write_text("", encoding="utf-8")
    result: dict = {}
    execution._muse_stream_diagnostics(result, stdout_log, stderr_log, "muse")
    diagnostics = result["stream_diagnostics"]
    assert diagnostics["retries"] == 1
    assert diagnostics["last_error_kind"] == "transport"
    assert diagnostics["terminal"] == "completed"


def test_muse_timeout_keeps_phases_partial_report_and_retries(tmp_path: Path, monkeypatch) -> None:
    """The issue's exact shape: timeout with partial deltas, edit, retries."""
    monkeypatch.setenv(prog.PROGRESS_POLL_ENV, "0.05")
    repo = _repo(tmp_path)
    events = [
        _status("opening meta model stream attempt 1/10", "opening_stream"),
        _delta("CONTRACT-READ\nvalidated the contract\n"),
        _status(
            "retrying meta model stream in 250ms (attempt 2/4)",
            "retry_scheduled",
            {"kind": "external_attempt", "error_kind": "transport"},
        ),
        _delta("EDITING\n"),
    ]
    executable, _argv_file = _fake_muse(
        tmp_path,
        name="muse-timeout",
        events=events,
        edit="VALUE = 2\n",
        sleeps=[0.0, 0.3, 0.0, 300.0],
    )
    payload = _run(
        repo,
        tmp_path,
        executable,
        executor="muse",
        effort="high",
        timeout_seconds=5,
    )

    assert payload["status"] == "timed-out", payload
    assert payload["execution"]["timed_out"] is True
    assert payload["lane_progress"]["phases"] == ["CONTRACT-READ", "EDITING"]
    assert payload["progress_guard"]["last_phases"] == ["CONTRACT-READ", "EDITING"]
    snapshot = payload["progress_guard"]["first_scoped_diff"]
    assert snapshot["observed"] is True
    assert snapshot["changed_paths"] == ["module.py"]
    delivery = payload["result_delivery"]
    assert delivery["status"] == "delivered", delivery
    assert Path(delivery["full_report"]["path"]).read_text(encoding="utf-8") == (
        "CONTRACT-READ\nvalidated the contract\nEDITING\n"
    )
    diagnostics = payload["execution"]["stream_diagnostics"]
    assert diagnostics["retries"] == 1
    assert diagnostics["last_error_kind"] == "transport"
    assert diagnostics["terminal"] is None
    assert diagnostics["cause_status"] == "provided"


def test_failed_task_reason_covers_missing_terminal() -> None:
    """A failed-task reason names the cause when no terminal event exists."""
    events = "\n".join(
        json.dumps(event)
        for event in (
            _status("opening meta model stream attempt 1/10", "opening_stream"),
            _failed_task("transport error: connection reset"),
        )
    )
    diagnostics = muse_events.stream_diagnostics(events, "")
    assert diagnostics["terminal"] is None
    assert diagnostics["terminal_reason"] == "transport error: connection reset"
    assert diagnostics["cause_status"] == "provided"


def test_stream_diagnostics_ignores_success_outcome_kind() -> None:
    """A succeeded stream's outcome token is not a stream error."""
    succeeded = _status(
        "completed meta model stream attempt 1/10",
        "stream_succeeded",
        {
            "kind": "external_attempt",
            "attempt": 1,
            "max_attempts": 10,
            "operation": "model.response",
            "system": "meta",
            "error_kind": "stream_succeeded",
        },
    )
    events = "\n".join(json.dumps(event) for event in (succeeded, _terminal("report\n")))
    diagnostics = muse_events.stream_diagnostics(events, "")
    assert diagnostics["last_error_kind"] is None
    assert diagnostics["cause_status"] == "not-applicable"

    retried = "\n".join(
        json.dumps(event)
        for event in (
            _status(
                "retrying meta model stream in 250ms (attempt 2/4)",
                "retry_scheduled",
                {"kind": "external_attempt", "error_kind": "transport"},
            ),
            succeeded,
            _terminal("report\n"),
        )
    )
    diagnostics = muse_events.stream_diagnostics(retried, "")
    assert diagnostics["retries"] == 1
    assert diagnostics["last_error_kind"] == "transport"
    assert diagnostics["cause_status"] == "provided"


def test_stream_diagnostics_reads_stderr_failure_cause() -> None:
    """The stderr terminal-failure line is the cause when events lack one."""
    diagnostics = muse_events.stream_diagnostics(
        "",
        "run ended with Failed: transport error: connection refused\n",
    )
    assert diagnostics["terminal_reason"] == "transport error: connection refused"
    assert diagnostics["cause_status"] == "provided"


def test_muse_stdout_report_prefers_terminal_over_deltas() -> None:
    """Completed terminal text wins; partial deltas cover a missing terminal."""
    completed = "\n".join(
        json.dumps(event) for event in (_delta("partial\n"), _terminal("final report\n"))
    )
    assert muse_events.muse_stdout_report(completed) == "final report\n"
    partial = "\n".join(json.dumps(event) for event in (_delta("CONTRACT-"), _delta("READ\n")))
    assert muse_events.muse_stdout_report(partial) == "CONTRACT-READ\n"
    assert muse_events.muse_stdout_report("plain lane output\n") is None


def test_hostile_transcript_degrades_to_unobserved_fields() -> None:
    """Unknown envelopes never crash the muse consumers."""
    hostile = "\n".join(
        [
            "{not json",
            'prefix "task.lifecycle.status" suffix',
            '{"task.lifecycle.status": broken json',
            '["task.lifecycle.status"]',
            json.dumps(["a", "list", "envelope"]),
            json.dumps({"payload_type": 42, "payload": {}}),
            json.dumps({"payload_type": "run.output.delta", "payload": []}),
            '{"payload_type": "something-else", "payload": {}, "run.output.delta": 0}',
            '{"payload_type": "something-else", "payload": {}, "task.lifecycle.status": 0}',
            '{"payload_type": "something-else", "payload": {}, "task.lifecycle.failed": 0}',
            json.dumps(_delta("").get("payload", {})),
            json.dumps(_envelope("run.output.delta", {"kind": "run_output_delta", "text": 42})),
            json.dumps(_envelope("task.lifecycle.status", {"kind": "task_lifecycle"})),
            json.dumps(
                _envelope(
                    "task.lifecycle.status",
                    {"kind": "task_lifecycle", "event": {"kind": "status"}},
                )
            ),
            json.dumps(
                _envelope(
                    "task.lifecycle.status",
                    {
                        "kind": "task_lifecycle",
                        "event": {
                            "kind": "status",
                            "message": "  ",
                            "details": {"phase": 42, "facets": [{"kind": "external_attempt"}]},
                        },
                    },
                )
            ),
            json.dumps(
                _envelope(
                    "task.lifecycle.status",
                    {
                        "kind": "task_lifecycle",
                        "event": {
                            "kind": "status",
                            "message": "retrying meta model stream in 10ms (attempt 2/4)",
                            "details": {
                                "phase": "retry_scheduled",
                                "facets": [
                                    {
                                        "kind": "external_attempt",
                                        "attempt": True,
                                        "max_attempts": "4",
                                        "error_kind": 42,
                                    },
                                    {"kind": "producer"},
                                ],
                            },
                        },
                    },
                )
            ),
            json.dumps(_envelope("run.terminal.failed", {"kind": "run_terminal"})),
            json.dumps(_envelope("run.terminal.completed", {"text": "WRONG terminal"})),
            json.dumps(
                _envelope(
                    "task.lifecycle.failed",
                    {"kind": "task_lifecycle", "event": {"kind": "failed"}},
                )
            ),
            json.dumps(
                _envelope(
                    "task.lifecycle.failed",
                    {"kind": "task_lifecycle", "event": {"kind": "failed", "reason": "  "}},
                )
            ),
        ]
    )
    assert muse_events.accumulated_agent_text(hostile) == ""
    assert muse_events.muse_stdout_report(hostile) == ""
    diagnostics = muse_events.stream_diagnostics(
        hostile, "run ended with Failed:   \n\nmuse: quiet\n"
    )
    assert diagnostics["source"] == "events"
    assert diagnostics["retries"] == 1
    assert diagnostics["last_error_kind"] is None
    assert diagnostics["last_attempt"] is None
    assert diagnostics["last_max_attempts"] is None
    assert diagnostics["terminal_reason"] is None
    assert diagnostics["cause_status"] == "unavailable-upstream"
    assert prog.lane_progress(hostile, "") == {"phases": [], "blocker": None}


def test_retain_muse_events_keeps_report_and_terminates_log(tmp_path: Path) -> None:
    """Raw JSONL lands newline-terminated in the events log; stdout keeps text."""
    stdout_log = tmp_path / "muse.stdout.log"
    event_log = tmp_path / "muse.events.log"
    stdout_log.write_text(
        json.dumps(_delta("EDITING\n")) + "\n" + json.dumps(_terminal("done\n")),
        encoding="utf-8",
    )
    execution._retain_muse_events(stdout_log, event_log)
    assert stdout_log.read_text(encoding="utf-8") == "done\n"
    assert event_log.read_text(encoding="utf-8").endswith("\n")

    plain_log = tmp_path / "plain.stdout.log"
    plain_log.write_text("task complete\n", encoding="utf-8")
    execution._retain_muse_events(plain_log, tmp_path / "plain.events.log")
    assert plain_log.read_text(encoding="utf-8") == "task complete\n"
    assert not (tmp_path / "plain.events.log").exists()


def test_muse_stream_diagnostics_attaches_for_muse_only(tmp_path: Path) -> None:
    """Diagnostics attach on muse lanes and stay off every other executor."""
    stdout_log = tmp_path / "muse.stdout.log"
    stderr_log = tmp_path / "muse.stderr.log"
    stdout_log.write_text("partial agent text\n", encoding="utf-8")
    stderr_log.write_text(
        "muse: retrying meta model stream in 1000ms (attempt 2/10)\n",
        encoding="utf-8",
    )
    result: dict = {}
    execution._muse_stream_diagnostics(result, stdout_log, stderr_log, "muse")
    assert result["stream_diagnostics"]["source"] == "stderr"
    assert result["stream_diagnostics"]["retries"] == 1
    codex_result: dict = {}
    execution._muse_stream_diagnostics(codex_result, stdout_log, stderr_log, "codex")
    assert "stream_diagnostics" not in codex_result


def test_classify_failure_prefers_muse_terminal_reason() -> None:
    """A named muse failure keeps its cause; a nameless one keeps the code."""
    named = state.classify_failure(
        {
            "exit_code": 1,
            "stream_diagnostics": {"terminal_reason": "transport error: refused"},
        }
    )
    assert named["message"] == "transport error: refused"
    nameless = state.classify_failure(
        {"exit_code": 1, "stream_diagnostics": {"terminal_reason": "  "}}
    )
    assert nameless["message"] == "executor exited with code 1"
    legacy = state.classify_failure({"exit_code": 1})
    assert legacy["message"] == "executor exited with code 1"
