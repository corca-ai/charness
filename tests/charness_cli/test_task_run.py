from __future__ import annotations

import os
import shlex
import signal
import time
from pathlib import Path

import pytest

from scripts import (
    task_run,
    task_run_execution,
    task_run_plan,
    task_run_runtime,
)

from .support import run_cli_path
from .test_task_run_fixtures import _codex, _git, _repo, _run


def test_invalid_task_run_inputs_are_typed_and_actionable(tmp_path: Path) -> None:
    repo = _repo(tmp_path)

    def resolve(**overrides):
        options = {
            "target_path": tmp_path / "lane",
            "branch": "lane/validation",
            "base": "HEAD",
            "lane": None,
            "scopes": ["module.py"],
            "prompt": "instructions",
            "codex": "python3",
            "effort": "medium",
            "task_id": None,
            "prepare": None,
            "require_change": None,
            "skip_prepare": False,
            "allow_no_change": False,
            "timeout_seconds": 1,
        }
        options.update(overrides)
        return task_run_plan.resolve_task_inputs(repo, **options)

    with pytest.raises(task_run.TaskRunError, match="--prepare and --skip-prepare"):
        resolve(prepare=True, skip_prepare=True)
    with pytest.raises(task_run.TaskRunError, match="--require-change and --allow-no-change"):
        resolve(require_change=True, allow_no_change=True)
    with pytest.raises(task_run.TaskRunError, match="--task-id is derived from --lane"):
        resolve(target_path=None, branch=None, base=None, lane="safe-lane", task_id="explicit")
    with pytest.raises(task_run.TaskRunError, match="explicit task runs require"):
        resolve(target_path=None, branch=None, base=None)
    with pytest.raises(task_run.TaskRunError, match="--prompt or --prompt-file"):
        resolve(prompt=" ")
    with pytest.raises(task_run.TaskRunError, match="orchestrator-selected --effort"):
        resolve(effort=None)
    with pytest.raises(task_run.TaskRunError, match="--timeout-seconds must be a positive integer"):
        resolve(timeout_seconds=0)


def test_runtime_input_refusals_explain_the_required_shape(tmp_path: Path) -> None:
    non_executable = tmp_path / "not-executable"
    non_executable.write_text("#!/bin/sh\n", encoding="utf-8")

    with pytest.raises(task_run.TaskRunError, match="--codex must name an executable"):
        task_run_runtime._resolve_codex(" ")
    with pytest.raises(task_run.TaskRunError, match="Codex executable is not runnable"):
        task_run_runtime._resolve_codex(str(non_executable))
    with pytest.raises(task_run.TaskRunError, match="Codex executable is not on PATH"):
        task_run_runtime._resolve_codex("definitely-missing-codex")
    with pytest.raises(task_run.TaskRunError, match="--lane must be a non-empty id"):
        task_run_runtime.validate_lane_id("-invalid")
    with pytest.raises(task_run.TaskRunError, match="--task-id must start with a letter"):
        task_run_runtime._task_id("lane/name", "bad/id")
    with pytest.raises(task_run.TaskRunError, match="invalid task id"):
        task_run_runtime.task_result_path(tmp_path, "bad/id")


def test_read_task_result_returns_none_when_the_record_is_absent(tmp_path: Path) -> None:
    assert task_run_runtime.read_task_result(tmp_path, "missing") is None


def test_read_task_result_refuses_non_object_json(tmp_path: Path) -> None:
    result_path = tmp_path / "task-run" / "broken" / "result.json"
    result_path.parent.mkdir(parents=True)
    result_path.write_text("[]\n", encoding="utf-8")

    with pytest.raises(task_run.TaskRunError, match="task result must be a JSON object"):
        task_run_runtime.read_task_result(tmp_path, "broken")


def test_read_task_results_reads_json_objects_from_the_result_store(tmp_path: Path) -> None:
    result_path = tmp_path / "task-run" / "one" / "result.json"
    result_path.parent.mkdir(parents=True)
    result_path.write_text('{"task_id": "one", "status": "completed"}\n', encoding="utf-8")

    assert task_run_runtime.read_task_results(tmp_path) == [
        {"task_id": "one", "status": "completed"}
    ]


def test_read_task_results_refuses_non_object_json(tmp_path: Path) -> None:
    result_path = tmp_path / "task-run" / "broken" / "result.json"
    result_path.parent.mkdir(parents=True)
    result_path.write_text("[]\n", encoding="utf-8")

    with pytest.raises(task_run.TaskRunError, match="task result must be a JSON object"):
        task_run_runtime.read_task_results(tmp_path)


def test_execute_codex_records_keyboard_interrupt_and_stops_the_group(
    tmp_path: Path, monkeypatch
) -> None:
    killed: list[tuple[int, signal.Signals]] = []
    stdout_log = tmp_path / "stdout.log"
    stderr_log = tmp_path / "stderr.log"

    def interrupting_phase(*_args, **_kwargs):
        stdout_log.with_suffix(".pgid").write_text("31415\n", encoding="utf-8")
        raise KeyboardInterrupt

    monkeypatch.setattr(task_run_execution, "run_monitored_phase", interrupting_phase)
    monkeypatch.setattr(
        task_run_execution.os,
        "killpg",
        lambda pid, sig: killed.append((pid, sig)),
    )

    result = task_run_execution._execute_codex(
        ["codex"],
        prompt="stop",
        target_path=tmp_path,
        configured_env={},
        stdout_log=stdout_log,
        stderr_log=stderr_log,
        timeout_seconds=1,
    )

    assert result == {"exit_code": None, "timed_out": False, "interrupted": True}
    assert killed == [(31415, signal.SIGKILL)]


def test_execute_codex_reports_process_start_oserror(tmp_path: Path, monkeypatch) -> None:
    def fail_start(*_args, **_kwargs):
        raise OSError("cannot execute codex")

    monkeypatch.setattr(task_run_execution, "run_monitored_phase", fail_start)
    result = task_run_execution._execute_codex(
        ["codex"],
        prompt="start",
        target_path=tmp_path,
        configured_env={},
        stdout_log=tmp_path / "stdout.log",
        stderr_log=tmp_path / "stderr.log",
        timeout_seconds=1,
    )

    assert result["exec_error"] == "cannot execute codex"


def test_codex_arguments_fix_luna_sandbox_and_effort(tmp_path: Path) -> None:
    git_common_dir = tmp_path / ".git"
    git_common_dir.mkdir()
    assert task_run.build_codex_args(
        effort="xhigh",
        writable_dirs=[git_common_dir],
    ) == [
        "--sandbox",
        "workspace-write",
        "--add-dir",
        str(git_common_dir),
        "-m",
        "gpt-5.6-luna",
        "-c",
        "model_reasoning_effort=xhigh",
    ]


def test_codex_effort_is_limited_to_orchestrator_presets() -> None:
    with pytest.raises(task_run.TaskRunError, match="medium, xhigh, max"):
        task_run.build_codex_args(effort="high")


def test_task_run_lane_shorthand_owns_safe_defaults_and_external_target(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "exit 0")
    monkeypatch.setenv("TMPDIR", str(tmp_path / "runtime-base"))

    payload = task_run.run_task(
        repo,
        lane="short-lane",
        scopes=["module.py"],
        prompt="update the module",
        codex=str(executable),
        effort="xhigh",
        dry_run=True,
    )

    assert payload["status"] == "pass"
    assert payload["lane"] == "short-lane"
    assert payload["task_id"] == "short-lane"
    assert payload["branch"] == "task/short-lane"
    assert payload["base"] == "HEAD"
    assert payload["base_sha"] == _git(repo, "rev-parse", "HEAD").stdout.strip()
    assert (
        Path(payload["worktree_path"])
        == Path(payload["runtime_root"]) / "task-run" / "short-lane" / "worktree"
    )
    assert payload["prepare"] is True
    assert payload["require_change"] is True
    assert payload["codex"] == {
        "executable": str(executable),
        "model": "gpt-5.6-luna",
        "effort": "xhigh",
    }


def test_task_prompt_is_stdin_not_an_option_bearing_argv_value(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    captured_args = tmp_path / "codex-args.txt"
    captured_stdin = tmp_path / "codex-stdin.txt"
    prompt = "--dangerously-bypass-approvals-and-sandbox --model hostile\nkeep the fixed lane"
    executable = _codex(
        tmp_path,
        f"printf '%s\\n' \"$@\" > {shlex.quote(os.fspath(captured_args))}\n"
        f"cat > {shlex.quote(os.fspath(captured_stdin))}",
    )

    payload = task_run.run_task(
        repo,
        target_path=tmp_path / "lane",
        branch="lane/stdin-prompt",
        base="HEAD",
        scopes=["module.py"],
        prompt=prompt,
        codex=str(executable),
        effort="max",
        require_change=False,
    )

    args = captured_args.read_text(encoding="utf-8").splitlines()
    assert payload["status"] == "completed", payload
    assert args[-1] == "-"
    assert prompt not in args
    assert args[args.index("-m") + 1] == "gpt-5.6-luna"
    assert captured_stdin.read_text(encoding="utf-8") == prompt


def test_task_run_lane_shorthand_optouts_enable_diagnostics(tmp_path: Path, monkeypatch) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "printf 'VALUE = 2\\n' > module.py")
    monkeypatch.setenv("TMPDIR", str(tmp_path / "runtime-base"))

    payload = task_run.run_task(
        repo,
        lane="diagnostic-lane",
        scopes=["module.py"],
        prompt="update the module",
        codex=str(executable),
        effort="medium",
        skip_prepare=True,
        allow_no_change=True,
        dry_run=True,
    )

    assert payload["status"] == "pass", payload
    assert payload["prepare"] is False
    assert payload["require_change"] is False


def test_task_run_cli_rejects_lane_and_explicit_identity_mix(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    result = run_cli_path(
        Path(__file__).resolve().parents[2] / "charness",
        "task",
        "run",
        "--repo-root",
        str(repo),
        "--lane",
        "ambiguous",
        "--path",
        str(tmp_path / "lane"),
        "--scope",
        "module.py",
        "--prompt",
        "noop",
        "--effort",
        "xhigh",
        cwd=repo,
    )

    assert result.returncode == 1
    assert "status: fail" in result.stdout
    assert "--lane cannot be combined with --path" in result.stdout


def test_task_run_cli_does_not_expose_host_override() -> None:
    cli = os.fspath(Path(__file__).resolve().parents[2] / "charness")
    help_result = run_cli_path(Path(cli), "task", "run", "--help")
    assert help_result.returncode == 0
    assert "--model" not in help_result.stdout
    assert "--codex" not in help_result.stdout
    assert "--codex-arg" not in help_result.stdout


def test_task_run_creates_named_lane_and_keeps_runtime_external(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "printf 'VALUE = 2\\n' > module.py")

    payload = _run(repo, tmp_path, executable)

    assert payload["status"] == "completed", payload
    assert payload["base_sha"] == _git(repo, "rev-parse", "HEAD").stdout.strip()
    assert payload["target_branch"] == "lane/task-run"
    assert payload["scope"]["disallowed_paths"] == []
    assert payload["parent"]["unchanged"] is True
    assert Path(payload["runtime_root"]).is_absolute()
    assert not Path(payload["runtime_root"]).is_relative_to(repo)
    assert not Path(payload["runtime_root"]).is_relative_to(payload["worktree_path"])
    assert (tmp_path / "lane" / "module.py").read_text(encoding="utf-8") == "VALUE = 2\n"


def test_task_run_reuses_doctor_checkout_dir_without_target_resnapshot(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "printf 'VALUE = 2\n' > module.py")
    original_snapshot = task_run._repo_snapshot
    snapshot_roots: list[Path] = []

    def observed_snapshot(path: Path) -> dict[str, object]:
        snapshot_roots.append(path.resolve())
        return original_snapshot(path)

    monkeypatch.setattr(task_run, "_repo_snapshot", observed_snapshot)
    payload = _run(repo, tmp_path, executable)

    assert payload["status"] == "completed", payload
    assert snapshot_roots == [repo.resolve()]
    assert Path(payload["git_worktree_dir"]).is_dir()


@pytest.mark.parametrize(
    "carrier",
    [None, {}, {"own_dir": None}, {"own_dir": "relative/.git"}],
)
def test_task_run_rejects_missing_or_malformed_checkout_carrier(carrier) -> None:
    with pytest.raises(task_run.TaskRunError):
        task_run._checkout_own_dir({"_checkout": carrier})


def test_task_run_assigns_distinct_lane_runtime_roots_and_leaves_worktrees_clean(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path,
        'mkdir -p "$CHARNESS_RUNTIME_ROOT"\n'
        'printf \'%s\\n\' "$CHARNESS_RUNTIME_ROOT" > "$CHARNESS_RUNTIME_ROOT/observed-root"\n'
        'printf \'%s\\n\' "$PYTHONPYCACHEPREFIX" "$TMPDIR" "$RUFF_CACHE_DIR" "$COVERAGE_FILE" "$XDG_CACHE_HOME" > "$CHARNESS_RUNTIME_ROOT/observed-paths"\n'
        "printf 'VALUE = 2\\n' > module.py\n"
        "git add -- module.py\n"
        "git -c user.email=test@example.com -c user.name=test commit -m 'update module'",
    )

    payloads = [
        task_run.run_task(
            repo,
            target_path=tmp_path / f"lane-{task_id}",
            branch=f"lane/{task_id}",
            base="HEAD",
            scopes=["module.py"],
            prompt="update the module",
            codex=str(executable),
            effort="medium",
            task_id=task_id,
        )
        for task_id in ("runtime-one", "runtime-two")
    ]

    execution_roots = [Path(payload["execution_runtime_root"]) for payload in payloads]
    assert len({root.resolve() for root in execution_roots}) == 2
    for payload, execution_root in zip(payloads, execution_roots):
        result_dir = Path(payload["result_path"]).parent
        assert execution_root == result_dir / "runtime"
        assert execution_root.is_dir()
        assert (execution_root / "observed-root").read_text(encoding="utf-8").strip() == str(
            execution_root
        )
        observed_paths = (
            (execution_root / "observed-paths").read_text(encoding="utf-8").splitlines()
        )
        assert all(Path(path).is_relative_to(execution_root) for path in observed_paths)
        assert task_run.task_status(repo, payload["task_id"]) == payload
        worktree = Path(payload["worktree_path"])
        assert (
            _git(worktree, "status", "--porcelain=v1", "--ignored", "--untracked-files=all").stdout
            == ""
        )

    assert _git(repo, "status", "--porcelain=v1", "--ignored", "--untracked-files=all").stdout == ""


def test_task_run_grants_codex_git_and_lane_runtime_dirs(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path)
    captured_args = tmp_path / "codex-args.txt"
    executable = _codex(
        tmp_path,
        f"printf '%s\\n' \"$@\" > {shlex.quote(os.fspath(captured_args))}",
    )

    payload = _run(
        repo,
        tmp_path,
        executable,
        require_change=False,
    )

    git_common_dir = Path(payload["git_common_dir"])
    git_worktree_dir = Path(payload["git_worktree_dir"])
    execution_runtime_root = Path(payload["execution_runtime_root"])
    args = captured_args.read_text(encoding="utf-8").splitlines()
    granted_dirs = [Path(args[index + 1]) for index, arg in enumerate(args) if arg == "--add-dir"]
    assert git_common_dir == repo / ".git"
    assert git_worktree_dir.parent == git_common_dir / "worktrees"
    assert granted_dirs == [git_common_dir, git_worktree_dir, execution_runtime_root]
    assert payload["codex"]["command"].count("--add-dir") == 3


def test_derived_task_ids_do_not_collide_after_slugging_or_truncation() -> None:
    assert task_run._task_id("lane-a", None) != task_run._task_id("lane/a", None)
    assert task_run._task_id("x" * 100 + "a", None) != task_run._task_id("x" * 100 + "b", None)
    assert len(task_run._task_id("x" * 200, None)) <= 96


def test_task_run_reports_ignored_output_without_blocking_candidate(tmp_path: Path) -> None:
    repo = _repo(tmp_path, ignored=True)
    executable = _codex(
        tmp_path,
        "printf 'VALUE = 2\\n' > module.py\nprintf 'diagnostic\\n' > ignored-output.txt",
    )

    payload = _run(repo, tmp_path, executable)

    assert payload["status"] == "completed", payload
    assert payload["populations"]["untracked"]["verdict"] == "pass"
    assert payload["populations"]["ignored"]["verdict"] == "warn"
    assert payload["generated_files"][0]["population"] == "ignored"
    assert payload["warnings"]


def test_task_run_blocks_new_untracked_output_and_retains_lane(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path,
        "printf 'VALUE = 2\\n' > module.py\nprintf 'leak\\n' > leak.txt",
    )

    payload = _run(repo, tmp_path, executable)

    assert payload["status"] == "failed"
    assert payload["scope"]["disallowed_paths"] == ["leak.txt"]
    assert "outside the declared scope" in payload["next_step"]
    assert (tmp_path / "lane" / "leak.txt").is_file()
    assert payload["parent"]["unchanged"] is True


def test_task_run_allows_new_scoped_candidate_file(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path,
        "printf 'VALUE = 2\\n' > module.py\nprintf 'def test_value(): pass\\n' > test_module.py",
    )

    payload = task_run.run_task(
        repo,
        target_path=tmp_path / "lane",
        branch="lane/new-file",
        base="HEAD",
        scopes=["module.py", "test_module.py"],
        prompt="add the focused test",
        codex=str(executable),
        effort="medium",
        require_change=True,
    )

    assert payload["status"] == "completed", payload
    assert payload["scope"]["disallowed_paths"] == []
    assert payload["populations"]["untracked"]["verdict"] == "pass"
    assert payload["generated_files"] == [
        {
            "population": "untracked",
            "path": "test_module.py",
            "classification": "candidate",
            "cause": "new candidate path is within the declared scope",
        }
    ]


def test_task_run_refuses_dirty_parent_before_worktree_creation(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "module.py").write_text("dirty\n", encoding="utf-8")
    executable = _codex(tmp_path, "exit 99")

    payload = _run(repo, tmp_path, executable)

    assert payload["status"] == "fail"
    assert "parent worktree must be clean" in payload["error"]
    assert not (tmp_path / "lane").exists()


def test_task_run_dry_run_has_no_worktree_or_runtime_side_effect(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "exit 99")

    payload = _run(repo, tmp_path, executable, dry_run=True)

    assert payload["status"] == "pass"
    assert payload["dry_run"] is True
    assert "git_worktree_dir" not in payload
    assert not (tmp_path / "lane").exists()
    assert not Path(payload["runtime_root"]).exists()


def test_task_run_cli_accepts_repo_root_after_subcommand(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _codex(tmp_path, "printf 'VALUE = 3\\n' > module.py")
    result = run_cli_path(
        Path(__file__).resolve().parents[2] / "charness",
        "task",
        "run",
        "--repo-root",
        str(repo),
        "--path",
        str(tmp_path / "lane"),
        "--branch",
        "lane/cli",
        "--base",
        "HEAD",
        "--scope",
        "module.py",
        "--prompt",
        "noop",
        "--effort",
        "medium",
        cwd=repo,
        env={
            **os.environ,
            "PATH": f"{tmp_path}{os.pathsep}{os.environ['PATH']}",
            "CHARNESS_STATE_HOME": str(tmp_path / "home" / ".local" / "state"),
            "PYTHONPYCACHEPREFIX": str(tmp_path / "launcher-pycache"),
        },
    )

    assert result.returncode == 0, result.stderr
    assert "status: completed" in result.stdout
    assert (tmp_path / "lane" / "module.py").read_text(encoding="utf-8") == "VALUE = 3\n"


def test_task_status_reads_the_external_result_store(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "printf 'VALUE = 4\\n' > module.py")
    payload = _run(repo, tmp_path, executable, task_id="status-check")

    result_path = Path(payload["runtime_root"]) / "task-run" / "status-check" / "result.json"
    assert result_path.is_file()
    status = run_cli_path(
        Path(__file__).resolve().parents[2] / "charness",
        "task",
        "status",
        "--repo-root",
        str(repo),
        "status-check",
        cwd=repo,
    )
    assert status.returncode == 0
    assert "status: completed" in status.stdout


def test_completion_scope_refresh_failure_persists_terminal_failed_result(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "printf 'VALUE = 2\\n' > module.py")

    def fail_refresh(*_args, **_kwargs):
        raise task_run.TaskRunError("scope refresh failed")

    monkeypatch.setattr(task_run._support, "_glob_matches", fail_refresh)
    payload = _run(
        repo,
        tmp_path,
        executable,
        task_id="completion-failure",
        scopes=["*.py"],
    )

    assert payload["status"] == "failed"
    assert payload["phase"] == "terminal"
    assert payload["approval_eligibility"] == "ineligible"
    assert payload["error"] == "task lifecycle failed: scope refresh failed"
    assert task_run.task_status(repo, "completion-failure") == payload


def test_post_create_setup_failure_persists_terminal_result(tmp_path: Path, monkeypatch) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "exit 0")

    original_create = task_run._worktree.run_create

    def fail_target_carrier(*args, **kwargs) -> dict[str, object]:
        payload = original_create(*args, **kwargs)
        payload["_checkout"] = {"own_dir": str(tmp_path / "missing-git-dir")}
        return payload

    monkeypatch.setattr(task_run._worktree, "run_create", fail_target_carrier)
    payload = _run(
        repo,
        tmp_path,
        executable,
        task_id="setup-failure",
        require_change=False,
    )

    assert payload["status"] == "failed"
    assert payload["phase"] == "terminal"
    assert payload["error"] == (
        "task lifecycle failed: worktree create payload checkout own_dir is not an existing "
        f"directory: {tmp_path / 'missing-git-dir'}"
    )
    assert task_run.task_status(repo, "setup-failure") == payload


def test_completion_interrupt_persists_terminal_result(tmp_path: Path, monkeypatch) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "printf 'VALUE = 2\\n' > module.py")

    def interrupt_completion(**_kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr(task_run, "_completion_evidence", interrupt_completion)
    payload = _run(repo, tmp_path, executable, task_id="completion-interrupt")

    assert payload["status"] == "interrupted"
    assert payload["phase"] == "terminal"
    assert task_run.task_status(repo, "completion-interrupt") == payload


def test_disjoint_parent_progress_is_reported_without_failing_lane(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path,
        f"printf 'VALUE = 2\\n' > module.py\nprintf 'parent\\n' > {repo / 'notes.txt'}",
    )

    payload = _run(repo, tmp_path, executable)

    assert payload["status"] == "completed", payload
    assert payload["parent"]["progress"]["classification"] == "concurrent-parent-progress"
    assert payload["parent"]["progress"]["paths"] == ["notes.txt"]
    assert payload["parent"]["progress"]["overlap_paths"] == []
    assert "parent made disjoint progress" in payload["warnings"][-1]


def test_overlapping_parent_progress_is_a_writer_conflict(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path,
        f"printf 'VALUE = 2\\n' > module.py\nprintf 'parent\\n' > {repo / 'module.py'}",
    )

    payload = _run(repo, tmp_path, executable)

    assert payload["status"] == "validated-partial-result"
    assert payload["approval_eligibility"] == "ineligible"
    assert payload["parent"]["progress"]["classification"] == "writer-conflict"
    assert payload["parent"]["progress"]["overlap_paths"] == ["module.py"]


def test_glob_scope_blocks_overlapping_parent_progress(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path,
        f"printf 'VALUE = 2\\n' > child.py\nprintf 'PARENT = 1\\n' > {repo / 'module.py'}",
    )

    payload = _run(repo, tmp_path, executable, scopes=["*.py"])

    assert payload["status"] == "validated-partial-result"
    assert payload["parent"]["progress"]["classification"] == "writer-conflict"
    assert payload["parent"]["progress"]["overlap_paths"] == ["module.py"]


def test_parent_ignored_residue_is_not_writer_progress(tmp_path: Path) -> None:
    repo = _repo(tmp_path, ignored=True)
    executable = _codex(
        tmp_path,
        f"printf 'VALUE = 2\\n' > module.py\nprintf 'cache\\n' > {repo / 'ignored-output.txt'}",
    )

    payload = _run(repo, tmp_path, executable)

    progress = payload["parent"]["progress"]
    assert payload["status"] == "completed", payload
    assert progress["classification"] == "normal"
    assert progress["ignored"]["added"] == ["ignored-output.txt"]


def test_timeout_commits_a_typed_wip_candidate_without_satisfying_completion(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "printf 'VALUE = 2\\n' > module.py\nsleep 5")

    payload = _run(repo, tmp_path, executable, timeout_seconds=1)

    worktree = Path(payload["worktree_path"])
    commit = payload["candidate"]["commit"]

    assert payload["status"] == "timed-out"
    assert payload["execution"]["status"] == "timed-out"
    assert payload["candidate"]["status"] == "wip"
    assert payload["candidate"]["state"] == "interrupted-mid-edit"
    assert payload["candidate"]["state_known"] is False
    assert payload["candidate"]["useful"] is True
    assert payload["candidate"]["changed_paths"] == ["module.py"]
    assert commit["status"] == "committed"
    assert commit["sha"] == payload["target_sha"]
    assert commit["message"] == ("task-run: WIP candidate — interrupted mid-edit — state unknown")
    assert commit["correctness_verified"] is False
    assert payload["scope"]["require_change"] is True
    assert payload["scope"]["verdict"] == "pass"
    assert payload["approval_eligibility"] == "ineligible"
    assert "interrupted mid-edit — state unknown" in payload["next_step"]
    assert "not a correctness claim" in payload["next_step"]
    assert _git(worktree, "status", "--porcelain=v1").stdout == ""
    assert (
        _git(worktree, "show", "-s", "--format=%s", commit["sha"]).stdout.strip()
        == commit["message"]
    )
    assert _git(repo, "rev-parse", "HEAD").stdout.strip() == payload["base_sha"]


def test_task_kills_same_group_background_descendants_before_evidence(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    late_write = tmp_path / "late-write.txt"
    executable = _codex(
        tmp_path,
        f"(sleep 1; printf late > {shlex.quote(os.fspath(late_write))}) &\n"
        "printf 'VALUE = 2\\n' > module.py",
    )

    payload = _run(repo, tmp_path, executable)
    time.sleep(1.2)

    assert payload["status"] == "completed", payload
    assert not late_write.exists()


def test_non_delivery_with_scoped_candidate_is_validated_partial_result(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "printf 'VALUE = 2\\n' > module.py", deliver=False)

    payload = _run(repo, tmp_path, executable)

    assert payload["status"] == "validated-partial-result"
    assert payload["execution"]["status"] == "non-delivery"
    assert payload["result_delivery"]["bytes"] == 0
