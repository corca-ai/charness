"""Executor availability and ordered fallback at the task-run boundary."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

import scripts.cli.cmd_task as task_payload
from scripts.task_run import task_run_attempts, task_run_plan, task_run_runtime, task_run_state
from tests.charness_cli.support import CLI, load_cli_module
from tests.charness_cli.test_task_run_fixtures import _repo, _run


def _executable(path: Path, contents: str) -> Path:
    path.write_text(f"#!/bin/sh\n{contents}\n", encoding="utf-8")
    path.chmod(0o755)
    return path


def test_usage_limit_receipt_has_executor_kind_and_retry_after(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _repo(tmp_path)
    runtime = tmp_path / "task-runtime"
    monkeypatch.setattr(task_run_plan, "_runtime_preview", lambda _repo: runtime)
    codex = _executable(
        tmp_path / "codex",
        "cat >/dev/null\n"
        "printf '%s\\n' \"You've hit your usage limit. Try again at 2099-05-06T07:08:09Z.\" >&2\n"
        "exit 1",
    )

    payload = _run(repo, tmp_path, codex)

    assert payload["status"] == "executor-unavailable"
    assert payload["result_kind"] == "executor-unavailable"
    assert payload["failure"]["kind"] == "executor-unavailable"
    assert payload["failure"]["retry_after"] == "2099-05-06T07:08:09Z"
    assert payload["attempts"][0]["failure_kind"] == "executor-unavailable"
    assert task_run_state.exit_code_for_result_kind(payload["result_kind"]) == 4
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.defpath}")
    monkeypatch.setattr(task_run_runtime, "task_runtime_root", lambda _repo: runtime)
    module = load_cli_module("charness_task_executors_after_limit", CLI)
    monkeypatch.setattr(task_payload, "_load_task_run_lib", lambda _args: None)
    args = module.build_parser().parse_args(["task", "executors", "--repo-root", str(repo)])

    assert args.func(args) == 0
    report = yaml.safe_load(capsys.readouterr().out)
    codex_status = next(item for item in report["executors"] if item["kind"] == "codex")
    assert codex_status["availability"] == "available"
    assert codex_status["quota_state"] == "unknown"
    assert codex_status["last_observed_usage_limit"]["retry_after"] == ("2099-05-06T07:08:09Z")


def test_task_executors_resolves_paths_without_invoking_or_starting_lane(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _repo(tmp_path)
    bindir = tmp_path / "bin"
    bindir.mkdir()
    invocation_log = tmp_path / "invoked.txt"
    for name in ("codex", "muse"):
        _executable(
            bindir / name,
            f"printf '%s\\n' {name} >> {str(invocation_log)!r}\nexit 99",
        )
    monkeypatch.setenv("PATH", f"{bindir}{os.pathsep}{os.defpath}")
    monkeypatch.setattr(
        task_run_runtime, "task_runtime_root", lambda _repo: tmp_path / "empty-runtime"
    )
    module = load_cli_module("charness_task_executors_probe", CLI)
    monkeypatch.setattr(task_payload, "_load_task_run_lib", lambda _args: None)
    args = module.build_parser().parse_args(["task", "executors", "--repo-root", str(repo)])

    assert args.func(args) == 0
    report = yaml.safe_load(capsys.readouterr().out)

    assert report["probe"] == "executable-resolution-only"
    assert report["lane_started"] is False
    assert [item["kind"] for item in report["executors"]] == ["codex", "muse"]
    assert all(item["availability"] == "available" for item in report["executors"])
    assert all(item["quota_state"] == "unknown" for item in report["executors"])
    assert not invocation_log.exists()
    assert sorted(path.name for path in repo.iterdir()) == [".git", "module.py"]


def test_usage_limit_falls_through_in_requested_executor_order(tmp_path: Path, monkeypatch) -> None:
    repo = _repo(tmp_path)
    monkeypatch.setattr(task_run_plan, "_runtime_preview", lambda _repo: tmp_path / "task-runtime")
    bindir = tmp_path / "bin"
    bindir.mkdir()
    order_log = tmp_path / "executor-order.txt"
    codex = _executable(
        bindir / "codex",
        f"printf '%s\\n' codex >> {str(order_log)!r}\n"
        "cat >/dev/null\n"
        "printf '%s\\n' 'Usage limit reached. Try again after 2099-05-06T07:08:09Z' >&2\n"
        "exit 1",
    )
    _executable(
        bindir / "muse",
        f"printf '%s\\n' muse >> {str(order_log)!r}\n"
        "printf 'VALUE = 2\\n' > module.py\n"
        "printf 'task complete\\n'",
    )
    monkeypatch.setenv("PATH", f"{bindir}{os.pathsep}{os.defpath}")

    payload = _run(repo, tmp_path, codex, executor="codex,muse")

    assert order_log.read_text(encoding="utf-8").splitlines() == ["codex", "muse"]
    assert payload["status"] == "completed"
    assert payload["executor"]["kind"] == "muse"
    assert payload["executor_order"] == ["codex", "muse"]
    assert [item["executor"] for item in payload["attempts"]] == ["codex", "muse"]
    assert payload["attempts"][0]["failure_kind"] == "executor-unavailable"
    assert payload["attempts"][0]["retry_after"] == "2099-05-06T07:08:09Z"
    assert payload["result_kind"] == "success"


def test_usage_limit_falls_from_muse_to_codex(tmp_path: Path, monkeypatch) -> None:
    repo = _repo(tmp_path)
    monkeypatch.setattr(task_run_plan, "_runtime_preview", lambda _repo: tmp_path / "task-runtime")
    bindir = tmp_path / "bin"
    bindir.mkdir()
    order_log = tmp_path / "executor-order.txt"
    _executable(
        bindir / "muse",
        f"printf '%s\\n' muse >> {str(order_log)!r}\n"
        "cat >/dev/null\n"
        "printf '%s\\n' 'Usage limit reached. Try again after 2099-05-06T07:08:09Z' >&2\n"
        "exit 1",
    )
    codex = _executable(
        bindir / "codex",
        f"printf '%s\\n' codex >> {str(order_log)!r}\n"
        "cat >/dev/null\nprintf 'VALUE = 2\\n' > module.py\nprintf 'task complete\\n'",
    )
    monkeypatch.setenv("PATH", f"{bindir}{os.pathsep}{os.defpath}")

    payload = _run(repo, tmp_path, codex, executor="muse,codex")

    assert order_log.read_text(encoding="utf-8").splitlines() == ["muse", "codex"]
    assert payload["status"] == "completed"
    assert payload["executor"]["kind"] == "codex"
    assert [item["executor"] for item in payload["attempts"]] == ["muse", "codex"]


def test_executor_order_rejects_empty_and_duplicate_entries() -> None:
    with pytest.raises(task_run_plan.TaskRunError, match="use commas"):
        task_run_plan._parse_executor_order("codex,,muse")
    with pytest.raises(task_run_plan.TaskRunError, match="must be unique"):
        task_run_plan._parse_executor_order("codex,muse,codex")


def test_ordered_fallback_requires_preparation_context(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="preparation context"):
        task_run_attempts._execute_watched_lane(
            {},
            [],
            lane_prompt="",
            resolved_target=tmp_path,
            configured_env={},
            stdout_log=tmp_path / "lane.stdout.log",
            stderr_log=tmp_path / "lane.stderr.log",
            timeout_seconds=1,
            require_change=False,
            base_sha="base",
            scope_specs=[],
            executor_order=("codex", "muse"),
        )
