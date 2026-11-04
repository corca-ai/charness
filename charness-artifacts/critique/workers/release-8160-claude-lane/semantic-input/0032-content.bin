"""Behavior probes for the Claude lane modules' refusal and fallback lines.

Each test asserts what its line decides -- a refusal that names only the
operation, an identity check that stops an import, a window that ignores an
earlier invocation -- so a broken line fails the test rather than merely
leaving it executed. They observe local owner behavior with fakes in place of
`git`, `bwrap` and the Anthropic upstream; the sandbox round trips stay in
`tests/charness_cli/test_task_run_claude_sandbox.py`.
"""

from __future__ import annotations

import http.client
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.task_run import (
    task_run_claude_auth,
    task_run_claude_events,
    task_run_claude_sandbox,
    task_run_event_timing,
    task_run_steering,
)
from scripts.task_run.task_run_contract import TaskRunError

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "module",
    [
        task_run_claude_auth,
        task_run_claude_events,
        task_run_claude_sandbox,
        task_run_event_timing,
        task_run_steering,
    ],
)
def test_bootstrap_inserts_missing_repo_root(monkeypatch: pytest.MonkeyPatch, module) -> None:
    """Run directly, each module puts the repo root first so `scripts.` imports resolve."""
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != str(ROOT)])

    module._load_repo_runtime_bootstrap()

    assert sys.path[0] == str(ROOT)


# --- auth proxy -------------------------------------------------------------


def test_auth_proxy_refuses_a_lane_without_local_authentication() -> None:
    with pytest.raises(TaskRunError, match="requires local API or OAuth authentication"):
        with task_run_claude_auth.claude_auth_proxy({"PATH": "/usr/bin"}):
            pass


class _Upstream:
    instances: list[_Upstream] = []

    def __init__(self, host: str, timeout: float) -> None:
        self.host = host
        self.closed = False
        _Upstream.instances.append(self)

    def request(self, *_args, **_kwargs) -> None:
        raise OSError("upstream refused; header x-api-key: real-secret")

    def close(self) -> None:
        self.closed = True


def _proxy_get(child_env: dict[str, str], path: str) -> http.client.HTTPResponse:
    port = int(child_env["ANTHROPIC_BASE_URL"].rsplit(":", 1)[1])
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=30)
    connection.request("GET", path, headers={"x-api-key": child_env["ANTHROPIC_API_KEY"]})
    return connection.getresponse()


def test_auth_proxy_rejects_an_absolute_form_target_before_any_upstream_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _Upstream.instances.clear()
    monkeypatch.setattr(task_run_claude_auth.http.client, "HTTPSConnection", _Upstream)

    with task_run_claude_auth.claude_auth_proxy({"ANTHROPIC_API_KEY": "real-secret"}) as child_env:
        # The stdlib handler already folds a leading `//`; an absolute-form target
        # reaches this check intact and must not be relayed to the fixed upstream.
        response = _proxy_get(child_env, "http://evil.example/v1/messages")

    assert response.status == 400
    assert _Upstream.instances == []


def test_auth_proxy_drops_the_connection_without_echoing_an_upstream_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _Upstream.instances.clear()
    monkeypatch.setattr(task_run_claude_auth.http.client, "HTTPSConnection", _Upstream)

    with task_run_claude_auth.claude_auth_proxy({"ANTHROPIC_API_KEY": "real-secret"}) as child_env:
        with pytest.raises(http.client.RemoteDisconnected):
            _proxy_get(child_env, "/v1/models")

    assert [upstream.host for upstream in _Upstream.instances] == ["api.anthropic.com"]
    assert _Upstream.instances[0].closed is True


# --- events -----------------------------------------------------------------

_RESULT_OK = json.dumps({"type": "result", "subtype": "success", "is_error": False, "result": "done"})
_RESULT_ERROR = json.dumps({"type": "result", "subtype": "error_during_execution", "is_error": True})


def test_retain_events_leaves_logs_alone_when_no_stream_event_is_present(tmp_path: Path) -> None:
    stdout_log = tmp_path / "stdout.log"
    event_log = tmp_path / "claude.events.log"
    stdout_log.write_text("plain crash text\n", encoding="utf-8")

    assert task_run_claude_events.retain_events(stdout_log, event_log) is None

    assert not event_log.exists()
    assert stdout_log.read_text(encoding="utf-8") == "plain crash text\n"


def test_retain_events_terminates_an_unterminated_final_event_line(tmp_path: Path) -> None:
    stdout_log = tmp_path / "stdout.log"
    event_log = tmp_path / "claude.events.log"
    event_log.write_text("earlier\n", encoding="utf-8")
    raw = json.dumps({"type": "system", "session_id": "s-1"}) + "\n" + _RESULT_OK
    stdout_log.write_text(raw, encoding="utf-8")

    assert task_run_claude_events.retain_events(stdout_log, event_log) == "s-1"

    assert event_log.read_text(encoding="utf-8") == "earlier\n" + raw + "\n"
    assert stdout_log.read_text(encoding="utf-8") == "done"


def test_terminal_result_leaves_the_result_untouched_without_a_result_event() -> None:
    result = {"exit_code": 0}

    task_run_claude_events.apply_terminal_result(result, json.dumps({"type": "system"}))

    assert result == {"exit_code": 0}


def test_command_key_ignores_events_without_a_bash_boundary() -> None:
    bash_tasks: set[str] = {"known"}
    event = {"type": "user", "message": {"content": [
        {"type": "text", "text": "hi"},
        {"type": "tool_result", "tool_use_id": "unknown"},
    ]}}

    assert task_run_claude_events.command_key(event, bash_tasks) == (None, None)
    assert bash_tasks == {"known"}


def test_executor_result_reads_only_this_invocations_window(tmp_path: Path) -> None:
    event_log = tmp_path / "claude.events.log"
    event_log.write_text(_RESULT_ERROR + "\n", encoding="utf-8")
    offset = event_log.stat().st_size
    with event_log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"type": "assistant", "message": {"content": []}}) + "\n")

    interrupted = {"exit_code": 0}
    task_run_claude_events.apply_executor_result(interrupted, "claude", event_log, offset)
    assert interrupted == {"exit_code": 0}

    with event_log.open("a", encoding="utf-8") as handle:
        handle.write(_RESULT_ERROR + "\n")
    failed = {"exit_code": 0}
    task_run_claude_events.apply_executor_result(failed, "claude", event_log, offset)
    assert failed["exit_code"] == 1
    assert failed["claude_result"] == {"subtype": "error_during_execution", "is_error": True}


# --- command durations ----------------------------------------------------------


def _codex(kind: str) -> dict[str, object]:
    return {"type": kind, "item": {"type": "command_execution", "id": "c-1"}}


def test_an_unstamped_completion_is_skipped_and_keeps_its_start() -> None:
    durations = task_run_event_timing.CommandDurations()

    assert durations.completed_ms(_codex("item.started"), "2026-11-05T00:00:00Z") is None
    assert durations.completed_ms(_codex("item.completed"), "not-a-stamp") is None
    assert durations.completed_ms(_codex("item.completed"), "2026-11-05T00:00:02Z") == 2000


def test_a_muse_event_without_a_payload_mapping_is_not_a_command() -> None:
    durations = task_run_event_timing.CommandDurations()
    event = {"payload_type": "task.lifecycle.started", "payload": "damaged"}

    assert durations.completed_ms(event, "2026-11-05T00:00:00Z") is None
    assert durations._started == {}


# --- sandbox ------------------------------------------------------------------

sandbox = task_run_claude_sandbox


def _lane(tmp_path: Path) -> tuple[Path, Path]:
    worktree = tmp_path / "lane"
    runtime = tmp_path / "runtime"
    worktree.mkdir()
    runtime.mkdir()
    return worktree.resolve(), runtime.resolve()


def test_private_git_failure_names_only_the_operation(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(sandbox, "run_process", lambda *_a, **_k: SimpleNamespace(
        returncode=1, stdout="hook printed real-secret", stderr="real-secret"))

    with pytest.raises(TaskRunError) as caught:
        sandbox._git(tmp_path, "status", "--short")

    assert str(caught.value) == "Claude private Git operation failed: status"


def test_sandboxed_git_failure_names_only_the_operation(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    worktree, runtime = _lane(tmp_path)
    monkeypatch.setattr(sandbox, "sandbox_prefix", lambda *_a, **_k: ["bwrap"])
    monkeypatch.setattr(sandbox, "run_process", lambda *_a, **_k: SimpleNamespace(
        returncode=1, stdout="real-secret", stderr="real-secret"))

    with pytest.raises(TaskRunError) as caught:
        sandbox._sandbox_git(worktree, runtime, "rev-parse", "HEAD")

    assert str(caught.value) == "Claude sandboxed Git operation failed: rev-parse"


def _write_identity(runtime: Path, identity: dict[str, str]) -> Path:
    marker = runtime / "claude" / "git-identity.json"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps(identity), encoding="utf-8")
    return marker


def _refuse_git(*args, **_kwargs):
    raise AssertionError(f"git must not run: {args}")


def test_prepare_git_reuses_its_own_runtime_and_refuses_another_worktrees(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    worktree, runtime = _lane(tmp_path)
    monkeypatch.setattr(sandbox, "_git", _refuse_git)
    _write_identity(runtime, {"worktree": str(worktree), "branch": "pilot", "base": "a" * 40})

    sandbox._prepare_git(worktree, runtime)

    _write_identity(runtime, {"worktree": str(tmp_path / "other"), "branch": "pilot", "base": "a" * 40})
    with pytest.raises(TaskRunError, match="belongs to another worktree"):
        sandbox._prepare_git(worktree, runtime)


def test_bundle_copy_refuses_a_non_regular_candidate(tmp_path: Path) -> None:
    _worktree, runtime = _lane(tmp_path)

    with pytest.raises(TaskRunError, match="must be a regular file"):
        sandbox._copy_bundle_for_host(Path(os.devnull), runtime)

    assert not (runtime.parent / "claude-candidate.bundle").exists()


class _GitScript:
    """Host and sandboxed Git answers keyed by the operation, recording every call."""

    def __init__(self, host: dict[str, str], private: dict[str, str]) -> None:
        self.host, self.private, self.calls = host, private, []

    def git(self, _worktree: Path, *args: str, **_kwargs) -> str:
        self.calls.append(("host", args))
        return self.host.get(args[0], "")

    def sandbox_git(self, _worktree: Path, _runtime: Path, *args: str) -> str:
        self.calls.append(("private", args))
        return self.private.get(args[0], "")


def _finalize(monkeypatch, tmp_path, *, marker_base: str, tip: str, private_branch: str) -> _GitScript:
    worktree, runtime = _lane(tmp_path)
    current = "c" * 40
    _write_identity(runtime, {"worktree": str(worktree), "branch": "pilot", "base": marker_base})
    script = _GitScript({"symbolic-ref": "pilot", "rev-parse": current},
                        {"rev-parse": tip, "symbolic-ref": private_branch})
    monkeypatch.setattr(sandbox, "_git", script.git)
    monkeypatch.setattr(sandbox, "_sandbox_git", script.sandbox_git)
    sandbox.finalize_claude_git(worktree, runtime)
    return script


def test_finalize_without_a_private_runtime_does_nothing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    worktree, runtime = _lane(tmp_path)
    monkeypatch.setattr(sandbox, "_git", _refuse_git)

    assert sandbox.finalize_claude_git(worktree, runtime) is None


@pytest.mark.parametrize(
    ("marker_base", "tip", "private_branch", "message"),
    [
        ("b" * 40, "d" * 40, "pilot", "identity changed before import"),
        ("c" * 40, "not-a-commit", "pilot", "has no valid commit"),
        ("c" * 40, "d" * 40, "other", "changed the private task branch"),
    ],
)
def test_finalize_refuses_before_importing_anything(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, marker_base: str, tip: str, private_branch: str, message: str
) -> None:
    with pytest.raises(TaskRunError, match=message):
        _finalize(monkeypatch, tmp_path, marker_base=marker_base, tip=tip, private_branch=private_branch)


def test_finalize_refusal_does_not_update_the_host_branch(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[tuple[str, tuple[str, ...]]] = []
    original = _GitScript.git

    def recording(self, worktree, *args, **kwargs):
        calls.append(("host", args))
        return original(self, worktree, *args, **kwargs)

    monkeypatch.setattr(_GitScript, "git", recording)
    with pytest.raises(TaskRunError):
        _finalize(monkeypatch, tmp_path, marker_base="c" * 40, tip="d" * 40, private_branch="other")

    assert [args[0] for _side, args in calls] == ["symbolic-ref", "rev-parse"]


def test_an_ungranted_common_dir_keeps_private_git(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    worktree, _runtime = _lane(tmp_path)
    monkeypatch.setattr(sandbox, "_git", lambda *_a, **_k: str(tmp_path / "repo" / ".git"))

    assert sandbox._shared_git_dir(worktree, [tmp_path / "cache"]) is None


def test_sandbox_prefix_refuses_without_bubblewrap(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    worktree, runtime = _lane(tmp_path)
    monkeypatch.setattr(sandbox.shutil, "which", lambda _name: None)

    with pytest.raises(TaskRunError, match="requires bubblewrap"):
        sandbox.sandbox_prefix(worktree, runtime)


def test_sandbox_prefix_refuses_a_non_regular_credential_mask(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    worktree, runtime = _lane(tmp_path)
    monkeypatch.setattr(sandbox.shutil, "which", lambda _name: "/usr/bin/bwrap")
    (runtime / "claude").mkdir()
    os.mkfifo(runtime / "claude" / "empty-credential")

    with pytest.raises(TaskRunError, match="credential mask must be a regular file"):
        sandbox.sandbox_prefix(worktree, runtime)


def test_sandbox_prefix_keeps_a_temporary_grants_parent_readable_before_the_grant(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    worktree, runtime = _lane(tmp_path)
    grant = Path("/tmp/charness-coverage-grant/cache")
    monkeypatch.setattr(sandbox.shutil, "which", lambda _name: "/usr/bin/bwrap")
    monkeypatch.setattr(sandbox, "_git", lambda *_a, **_k: str(tmp_path / "repo" / ".git"))

    command = sandbox.sandbox_prefix(worktree, runtime, writable_dirs=[grant])

    def position(*triple: str) -> int:
        return next(i for i in range(len(command) - 2) if tuple(command[i:i + 3]) == triple)

    parent = "/tmp/charness-coverage-grant"
    assert position("--tmpfs", "/tmp", "--ro-bind") < position("--ro-bind", parent, parent)
    assert position("--ro-bind", parent, parent) < position("--bind", str(grant), str(grant))


def test_a_failed_private_import_fails_the_lane_with_a_fixed_message(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def refuse(_worktree, _runtime):
        raise TaskRunError("private detail real-secret")

    monkeypatch.setattr(sandbox, "finalize_claude_git", refuse)
    result: dict[str, object] = {"exit_code": 0}

    sandbox.finalize_executor_candidate(result, "claude", tmp_path, {"CHARNESS_RUNTIME_ROOT": str(tmp_path)})

    assert result == {
        "exit_code": 1,
        "exec_error": "Claude private Git import failed; inspect retained runtime",
    }
