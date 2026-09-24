"""Focused probes for task-run result, progress, event, and prelaunch fallbacks.

These tests observe local owner behavior. They do not claim live executor or
release behavior; the changed-line gate remains the consumer of their coverage.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from scripts.task_run import (
    task_run_events,
    task_run_execution,
    task_run_lane_runner,
    task_run_prelaunch,
    task_run_progress,
    task_run_state,
)


def _event(**updates: Any) -> dict[str, Any]:
    event: dict[str, Any] = {
        "schema_version": 1,
        "event_id": "event-1",
        "occurred_at": "2026-09-24T00:00:00Z",
        "source": "friction-log",
        "event_kind": "block",
        "facts": {},
    }
    event.update(updates)
    return event


@pytest.mark.parametrize(
    ("updates", "message"),
    [
        ({"schema_version": True}, "schema_version must be 1"),
        ({"event_id": "  "}, "event_id must be a non-empty string"),
        ({"occurred_at": ""}, "occurred_at must be a UTC timestamp"),
        ({"occurred_at": "not-a-date"}, "occurred_at must be a UTC timestamp"),
        ({"source": "unknown"}, "source must be one of"),
    ],
)
def test_event_validation_rejects_invalid_envelope_fields(
    updates: dict[str, Any], message: str
) -> None:
    with pytest.raises(task_run_events.EventSchemaError, match=message):
        task_run_events.validate_event(_event(**updates))


def test_event_validation_reports_non_json_facts() -> None:
    # The integer is accepted by the JSON-shape walk but rejected by the JSON
    # encoder's digit limit, exercising its TypeError/ValueError translation.
    with pytest.raises(
        task_run_events.EventSchemaError,
        match="facts must contain only JSON values",
    ):
        task_run_events.validate_event(_event(facts={"large": 10**5000}))


@pytest.mark.parametrize(
    ("event", "message"),
    [
        (None, "event must be an object"),
        ({}, "event fields mismatch"),
        (_event(occurred_at="2026-09-24T09:00:00+09:00"), "include a UTC offset"),
        (_event(event_kind="unknown"), "event_kind is not valid for source"),
        (_event(facts=[]), "facts must be an object"),
        (_event(facts={"bad": object()}), "facts must be an object"),
    ],
)
def test_event_validation_rejects_invalid_shapes(event: object, message: str) -> None:
    with pytest.raises(task_run_events.EventSchemaError, match=message):
        task_run_events.validate_event(event)


def test_event_validation_guards_a_non_object_normalized_facts_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Simulate a decoder contract violation to probe the post-normalization guard.
    monkeypatch.setattr(task_run_events.json, "loads", lambda *_args, **_kwargs: [])
    with pytest.raises(task_run_events.EventSchemaError, match="facts must be an object"):
        task_run_events.validate_event(_event())


def test_progress_parser_reads_nested_json_event_text() -> None:
    transcript = (
        '{"item":{"text":"EDITING\\nTESTING"},'
        '"content":[{"message":"BLOCKED: premise false"}]}\n'
    )

    parsed = task_run_progress.lane_progress(transcript, "")

    assert parsed == {"phases": ["EDITING", "TESTING"], "blocker": "premise false"}


@pytest.mark.parametrize("receipt", [None, "not-a-receipt", []])
def test_result_kind_receipt_rejects_non_mappings(receipt: object) -> None:
    assert task_run_state.result_kind_for_receipt(receipt) is task_run_state.ResultKind.FAILED


@pytest.mark.parametrize("kind", ["unknown-kind", []])
def test_result_kind_receipt_rejects_invalid_explicit_kinds(kind: object) -> None:
    assert task_run_state.result_kind_for_receipt({"result_kind": kind}) is (
        task_run_state.ResultKind.FAILED
    )


def test_result_kind_status_rejects_non_strings() -> None:
    assert task_run_state.result_kind_for_status(None) is task_run_state.ResultKind.FAILED


def test_prelaunch_bootstrap_inserts_owning_repo_root(monkeypatch: pytest.MonkeyPatch) -> None:
    source = Path(task_run_prelaunch.__file__).resolve()
    repo_root = str(source.parents[2])
    monkeypatch.setattr(
        sys,
        "path",
        [entry for entry in sys.path if entry not in {"", repo_root}],
    )
    spec = importlib.util.spec_from_file_location("task_run_prelaunch_bootstrap_probe", source)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert sys.path[0] == repo_root


@pytest.mark.parametrize(
    ("value", "message"),
    [
        ({"critical_lane": 1}, "inputs must be booleans"),
        ({"acceptance_skeleton": " "}, "repo-relative test path"),
        ({"acceptance_skeleton": "/absolute/test.py"}, "repo-relative test path"),
        ({"acceptance_skeleton": "../outside.py"}, "repo-relative test path"),
        ({"critical_lane": True}, "requires --acceptance-skeleton"),
        ({"premise_checks": "invalid"}, "must be a list"),
        ({"premise_checks": ["invalid"]}, "needs ID, PREMISE, and DECISION"),
        (
            {"premise_checks": [["same", "first", "decide"], ["same", "second", "decide"]]},
            "IDs must be unique",
        ),
    ],
)
def test_prelaunch_contract_rejects_invalid_declarations(
    value: dict[str, Any], message: str
) -> None:
    with pytest.raises(task_run_state.TaskRunError, match=message):
        task_run_prelaunch._resolve_prelaunch_contract(value)


def test_prelaunch_contract_accepts_mapping_premise_check() -> None:
    resolved = task_run_prelaunch._resolve_prelaunch_contract(
        {"premise_checks": [{"id": "consumer", "premise": "used", "decision_needed": "keep"}]}
    )

    assert resolved["premise_checks"] == [
        {"id": "consumer", "premise": "used", "decision_needed": "keep"}
    ]


def test_typed_premise_results_ignore_bad_ids_and_block_duplicate_ids() -> None:
    declarations = [{"id": "api", "premise": "available", "decision_needed": "choose"}]

    [result] = task_run_prelaunch._typed_premise_results(
        declarations,
        {
            "premise_checks": [
                {"id": 42, "kind": "success", "evidence": "ignored"},
                {"id": "api", "kind": "success", "evidence": "first"},
                {"id": "api", "kind": "success", "evidence": "second"},
            ]
        },
    )

    assert result["kind"] == task_run_state.ResultKind.PREMISE_BLOCKED.value


def test_acceptance_skeleton_rejects_a_missing_symlink_target(tmp_path: Path) -> None:
    link = tmp_path / "missing-test.py"
    link.symlink_to(tmp_path / "absent-test.py")

    result = task_run_prelaunch.run_acceptance_skeleton(tmp_path, link.name)

    assert result == {"status": "invalid", "exit_code": None, "duration_ms": 0}


def test_acceptance_skeleton_rejects_an_untracked_test(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    candidate = tmp_path / "candidate.py"
    candidate.write_text("assert True\n", encoding="utf-8")
    monkeypatch.setattr(
        task_run_prelaunch,
        "run_process",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=1),
    )

    result = task_run_prelaunch.run_acceptance_skeleton(tmp_path, candidate.name)

    assert result["status"] == "invalid"
    assert result["exit_code"] is None


@pytest.mark.parametrize(
    ("error", "timed_out", "expected"),
    [
        (OSError("pytest unavailable"), False, "pytest unavailable"),
        (None, True, "acceptance skeleton timed out"),
    ],
)
def test_acceptance_skeleton_reports_execution_failures(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    error: OSError | None,
    timed_out: bool,
    expected: str,
) -> None:
    candidate = tmp_path / "candidate.py"
    candidate.write_text("assert True\n", encoding="utf-8")
    monkeypatch.setattr(
        task_run_prelaunch,
        "run_process",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=0),
    )

    def run_phase(*_args: Any, **_kwargs: Any) -> Any:
        if error is not None:
            raise error
        return SimpleNamespace(
            timed_out=timed_out, returncode=-9, stdout="", stderr=""
        )

    monkeypatch.setattr(task_run_prelaunch, "run_monitored_phase", run_phase)
    result = task_run_prelaunch.run_acceptance_skeleton(tmp_path, candidate.name)

    assert result["status"] == "invalid"
    assert expected in result["output"]


def test_scope_and_coverage_mapping_deficits_name_missing_evidence(tmp_path: Path) -> None:
    scope = task_run_prelaunch._scope_file_deficits(
        {"scope_preflight": {"required_scope_paths": ["missing.py"]}},
        tmp_path,
        [],
        ["missing.py"],
    )
    mapping = task_run_prelaunch._coverage_mapping_deficits(
        {
            "status": "configured",
            "bundle_status": "missing-bundle",
            "scope_paths": ["missing.py"],
        },
        tmp_path,
        ["missing.py"],
    )

    assert "in-scope file deficit" in scope[0]
    assert any("coverage mapping deficit" in item for item in mapping)


def _fake_codex_setup(tmp_path: Path) -> tuple[Path, Path, list[str]]:
    runtime = tmp_path / "runtime-root" / "lane" / "runtime"
    runtime.mkdir(parents=True)
    counter = tmp_path / "invocations.txt"
    fake = tmp_path / "fake-codex"
    fake.write_text(
        f"#!{sys.executable}\n"
        "import json, pathlib, sys\n"
        f"counter = pathlib.Path({str(counter)!r})\n"
        "count = int(counter.read_text()) + 1 if counter.exists() else 1\n"
        "counter.write_text(str(count))\n"
        "output = pathlib.Path(sys.argv[sys.argv.index('--output-last-message') + 1])\n"
        "if count == 1:\n"
        "    print(json.dumps({'type': 'thread.started', 'thread_id': 'session-1'}), end='')\n"
        "    output.write_text('first turn\\n')\n"
        "elif count == 2:\n"
        "    raise SystemExit(7)\n"
        "else:\n"
        "    print(json.dumps({'type': 'thread.started', 'thread_id': 'session-1'}), end='')\n"
        "    output.write_text('final turn\\n')\n",
        encoding="utf-8",
    )
    fake.chmod(0o755)
    command = [str(fake), "--output-last-message", str(runtime / "last-message.txt")]
    return runtime, counter, command


def _execute_fake_codex(
    runtime: Path,
    command: list[str],
    *,
    lane_watch: Any = None,
) -> dict[str, Any]:
    return task_run_execution._execute_codex(
        command,
        prompt="exercise the fake executor loop",
        target_path=runtime,
        configured_env=dict(os.environ),
        stdout_log=runtime / "codex.stdout.log",
        stderr_log=runtime / "codex.stderr.log",
        timeout_seconds=10,
        lane_watch=lane_watch,
        executor="codex",
    )


def test_fake_executor_covers_queue_delivery_resume_failure_and_relaunch(
    tmp_path: Path,
) -> None:
    runtime, counter, command = _fake_codex_setup(tmp_path)
    queue = runtime / "steer.queue.jsonl"
    task_run_lane_runner.enqueue_steer(queue, "lane", "repeat the request")

    result = _execute_fake_codex(runtime, command)

    [message] = result["steer_messages"]
    assert result["exit_code"] == 0
    assert counter.read_text(encoding="utf-8") == "3"
    assert message["disposition"] == "accepted"
    assert message["resume_path"] == "relaunch-in-place"
    event_log = runtime / "codex.events.log"
    assert len(event_log.read_text(encoding="utf-8").splitlines()) == 2
    assert event_log.read_text(encoding="utf-8").endswith("\n")


def test_fake_executor_records_delivery_through_lane_watch(tmp_path: Path) -> None:
    runtime, counter, command = _fake_codex_setup(tmp_path)

    class Watch:
        stop_reason = None

        def __init__(self) -> None:
            self.pending = [
                {
                    "message_id": "watch-message",
                    "task_id": "lane",
                    "message": "continue",
                    "queued_at": "2026-09-24T00:00:00Z",
                }
            ]
            self.deliveries: list[str] = []

        def start(self, **_kwargs: Any) -> None:
            return None

        def stop(self) -> None:
            return None

        def pending_steers(self) -> list[dict[str, str]]:
            pending, self.pending = self.pending, []
            return pending

        def record_steer_delivery(self, _messages: Any, *, resume_path: str) -> None:
            self.deliveries.append(resume_path)

    watch = Watch()

    result = _execute_fake_codex(runtime, command, lane_watch=watch)

    assert result["exit_code"] == 0
    assert counter.read_text(encoding="utf-8") == "3"
    assert watch.deliveries == ["session-resume", "relaunch-in-place"]


def test_fake_executor_open_error_is_returned_as_exec_error(tmp_path: Path) -> None:
    runtime, counter, command = _fake_codex_setup(tmp_path)
    (runtime / "codex.events.log").mkdir()

    result = _execute_fake_codex(runtime, command)

    assert result["exec_error"]
    assert "codex.events.log" in result["exec_error"]
    assert counter.read_text(encoding="utf-8") == "1"


class _ValueErrorOnIndex(list[str]):
    def index(self, _value: str, *_args: Any) -> int:
        raise ValueError("simulated sequence lookup failure")


@pytest.mark.parametrize(
    ("lookup", "executor", "flag"),
    [
        ("session", "muse", "--session-id"),
        ("last-message", "codex", "--output-last-message"),
    ],
)
@pytest.mark.parametrize("value_error", [False, True])
def test_executor_argument_parse_fallbacks_return_none(
    lookup: str, executor: str, flag: str, value_error: bool
) -> None:
    command: list[str] = _ValueErrorOnIndex([flag, "value"]) if value_error else [flag]

    if lookup == "session":
        parsed = task_run_execution._command_session_id(command, executor)
    else:
        parsed = task_run_execution._last_message_path(command, executor)

    assert parsed is None
