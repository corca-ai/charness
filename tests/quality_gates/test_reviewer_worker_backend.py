"""Focused seam tests for the reviewer backend owner."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from skills.shared.scripts import reviewer_worker_backend as backend
from skills.shared.scripts import reviewer_worker_runtime as runtime
from skills.shared.scripts.reviewer_process import ReviewerProcessError


def _inputs(tmp_path: Path) -> dict[str, Path]:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    prompt = tmp_path / "prompt.md"
    prompt.write_text("Review this.\n", encoding="utf-8")
    schema = tmp_path / "schema.json"
    schema.write_text('{"type":"object"}\n', encoding="utf-8")
    return {
        "workspace": workspace,
        "prompt": prompt,
        "schema": schema,
        "stdout": tmp_path / "stdout.log",
        "stderr": tmp_path / "stderr.log",
        "pending": tmp_path / "pending.json",
        "raw": tmp_path / "raw.json",
    }


@pytest.mark.parametrize(
    ("backend_name", "raw_payload", "expected"),
    [
        ("codex_exec", {"kind": "review"}, {"kind": "review"}),
        (
            "claude_p",
            {"is_error": False, "structured_output": {"kind": "review"}},
            {"kind": "review"},
        ),
    ],
)
def test_supported_backends_normalize_through_one_owner(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    backend_name: str,
    raw_payload: dict[str, object],
    expected: dict[str, object],
) -> None:
    paths = _inputs(tmp_path)
    observed: dict[str, object] = {}

    def fake_run(command, *, cwd, stdin_path, stdout_path, stderr_path, timeout_seconds):
        observed.update(
            command=command,
            cwd=cwd,
            stdin_path=stdin_path,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            timeout_seconds=timeout_seconds,
        )
        if backend_name == "codex_exec":
            output_path = Path(command[command.index("-o") + 1])
        else:
            output_path = Path(stdout_path)
        output_path.write_text(json.dumps(raw_payload), encoding="utf-8")
        return 0

    monkeypatch.setattr(backend, "run_bounded_process", fake_run)
    exit_code = backend.execute_backend(
        backend_name,
        workspace=paths["workspace"],
        prompt=paths["prompt"],
        schema=paths["schema"],
        stdout=paths["stdout"],
        stderr=paths["stderr"],
        pending_output=paths["pending"],
        raw_output=paths["raw"],
        timeout_seconds=2.5,
    )

    assert exit_code == 0
    assert json.loads(paths["pending"].read_text(encoding="utf-8")) == expected
    assert observed["timeout_seconds"] == 2.5
    expected_stdout = paths["stdout"] if backend_name == "codex_exec" else paths["raw"]
    assert observed["stdout_path"] == expected_stdout


@pytest.mark.parametrize(
    ("status", "exit_code"),
    [("timed-out", 124), ("interrupted", 130)],
)
def test_process_failures_remain_typed_at_backend_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    status: str,
    exit_code: int,
) -> None:
    paths = _inputs(tmp_path)

    def fail(*_args, **_kwargs):
        raise ReviewerProcessError(status, f"backend {status}", exit_code=exit_code)

    monkeypatch.setattr(backend, "run_bounded_process", fail)
    with pytest.raises(backend.WorkerError) as raised:
        backend.execute_backend(
            "codex_exec",
            workspace=paths["workspace"],
            prompt=paths["prompt"],
            schema=paths["schema"],
            stdout=paths["stdout"],
            stderr=paths["stderr"],
            pending_output=paths["pending"],
            raw_output=paths["raw"],
            timeout_seconds=1.0,
        )

    assert raised.value.status == status
    assert raised.value.exit_code == exit_code


def test_nonzero_backend_exit_is_typed_and_keeps_output_unpublished(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    paths = _inputs(tmp_path)
    monkeypatch.setattr(backend, "run_bounded_process", lambda *_args, **_kwargs: 7)

    with pytest.raises(backend.WorkerError) as raised:
        backend.execute_backend(
            "codex_exec",
            workspace=paths["workspace"],
            prompt=paths["prompt"],
            schema=paths["schema"],
            stdout=paths["stdout"],
            stderr=paths["stderr"],
            pending_output=paths["pending"],
            raw_output=paths["raw"],
            timeout_seconds=1.0,
        )

    assert raised.value.status == "backend-failed"
    assert raised.value.exit_code == 7
    assert not paths["pending"].exists()


def test_claude_command_drops_top_level_schema_key(tmp_path: Path) -> None:
    """#878: the Claude CLI rejects draft 2020-12 $schema, so claude_p strips it."""
    paths = _inputs(tmp_path)
    paths["schema"].write_text(
        json.dumps(
            {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "properties": {"kind": {"type": "string"}},
            }
        ),
        encoding="utf-8",
    )

    command = backend._command(
        "claude_p", paths["workspace"], paths["schema"], paths["raw"]
    )

    payload = json.loads(command[command.index("--json-schema") + 1])
    assert "$schema" not in payload
    assert payload["type"] == "object"
    assert payload["properties"] == {"kind": {"type": "string"}}


def test_nonzero_exit_surfaces_the_backend_stderr_line(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """#878: a backend failure carries the backend's stderr line, not just the code."""
    paths = _inputs(tmp_path)

    def fail_with_stderr(*_args, **kwargs):
        Path(kwargs["stderr_path"]).write_text(
            "Error: --json-schema is not a valid JSON Schema: no schema with key\n",
            encoding="utf-8",
        )
        return 1

    monkeypatch.setattr(backend, "run_bounded_process", fail_with_stderr)
    with pytest.raises(backend.WorkerError) as raised:
        backend.execute_backend(
            "claude_p",
            workspace=paths["workspace"],
            prompt=paths["prompt"],
            schema=paths["schema"],
            stdout=paths["stdout"],
            stderr=paths["stderr"],
            pending_output=paths["pending"],
            raw_output=paths["raw"],
            timeout_seconds=1.0,
        )

    assert raised.value.status == "backend-failed"
    assert raised.value.exit_code == 1
    assert "backend exited with code 1" in str(raised.value)
    assert "--json-schema is not a valid JSON Schema" in str(raised.value)


def test_nonzero_exit_without_stderr_keeps_the_plain_message(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    paths = _inputs(tmp_path)
    monkeypatch.setattr(backend, "run_bounded_process", lambda *_args, **_kwargs: 7)

    with pytest.raises(backend.WorkerError) as raised:
        backend.execute_backend(
            "claude_p",
            workspace=paths["workspace"],
            prompt=paths["prompt"],
            schema=paths["schema"],
            stdout=paths["stdout"],
            stderr=paths["stderr"],
            pending_output=paths["pending"],
            raw_output=paths["raw"],
            timeout_seconds=1.0,
        )

    assert raised.value.status == "backend-failed"
    assert str(raised.value) == "backend exited with code 7"


def test_nonzero_exit_with_blank_stderr_keeps_the_plain_message(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    paths = _inputs(tmp_path)

    def fail_with_blank_stderr(*_args, **kwargs):
        Path(kwargs["stderr_path"]).write_text("\n  \n", encoding="utf-8")
        return 2

    monkeypatch.setattr(backend, "run_bounded_process", fail_with_blank_stderr)
    with pytest.raises(backend.WorkerError) as raised:
        backend.execute_backend(
            "codex_exec",
            workspace=paths["workspace"],
            prompt=paths["prompt"],
            schema=paths["schema"],
            stdout=paths["stdout"],
            stderr=paths["stderr"],
            pending_output=paths["pending"],
            raw_output=paths["raw"],
            timeout_seconds=1.0,
        )

    assert raised.value.status == "backend-failed"
    assert str(raised.value) == "backend exited with code 2"


def test_runtime_delegates_backend_construction_execution_and_normalization() -> None:
    runtime_source = Path(runtime.__file__).read_text(encoding="utf-8")
    backend_source = Path(backend.__file__).read_text(encoding="utf-8")

    for symbol in ("_command", "_normalize_claude", "execute_backend"):
        assert f"def {symbol}" not in runtime_source
        assert f"def {symbol}" in backend_source
    assert "execute_backend(" in runtime_source
