from __future__ import annotations

import json
import os
import shlex
import subprocess
import time
from pathlib import Path

import pytest

from scripts import task_run, task_run_support
from skills.shared.scripts import reviewer_lifecycle


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def _repo(tmp_path: Path, *, ignored: bool = False) -> Path:
    repo = tmp_path / "parent"
    repo.mkdir()
    _git(repo, "init", "--initial-branch=main")
    (repo / "module.py").write_text("VALUE = 1\n", encoding="utf-8")
    if ignored:
        (repo / ".gitignore").write_text("ignored-output.txt\n", encoding="utf-8")
        _git(repo, "add", "module.py", ".gitignore")
    else:
        _git(repo, "add", "module.py")
    _git(
        repo,
        "-c",
        "user.email=test@example.com",
        "-c",
        "user.name=test",
        "commit",
        "-m",
        "seed",
    )
    return repo


def _commit(repo: Path, message: str, *paths: str) -> str:
    _git(repo, "add", "--", *paths)
    _git(
        repo,
        "-c",
        "user.email=test@example.com",
        "-c",
        "user.name=test",
        "commit",
        "-m",
        message,
    )
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


def _codex(tmp_path: Path, body: str, *, deliver: bool = True) -> Path:
    executable = tmp_path / "codex"
    delivery = "printf 'task complete\\n'" if deliver else ""
    executable.write_text(f"#!/bin/sh\n{body}\n{delivery}\n", encoding="utf-8")
    executable.chmod(0o755)
    return executable


def _run(repo: Path, tmp_path: Path, executable: Path, **kwargs):
    scopes = kwargs.pop("scopes", ["module.py"])
    require_change = kwargs.pop("require_change", True)
    effort = kwargs.pop("effort", "medium")
    return task_run.run_task(
        repo,
        target_path=tmp_path / "lane",
        branch="lane/task-run",
        base="HEAD",
        scopes=scopes,
        prompt="update the module",
        codex=str(executable),
        effort=effort,
        require_change=require_change,
        **kwargs,
    )


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


def test_task_run_lane_shorthand_owns_safe_defaults_and_external_target(tmp_path: Path, monkeypatch) -> None:
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
    assert Path(payload["worktree_path"]) == Path(payload["runtime_root"]) / "task-run" / "short-lane" / "worktree"
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
    result = subprocess.run(
        [
            os.fspath(Path(__file__).resolve().parents[2] / "charness"),
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
        ],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "status: fail" in result.stdout
    assert "--lane cannot be combined with --path" in result.stdout


def test_task_run_cli_does_not_expose_host_override() -> None:
    cli = os.fspath(Path(__file__).resolve().parents[2] / "charness")
    help_result = subprocess.run(
        [cli, "task", "run", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
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


def test_task_run_assigns_distinct_lane_runtime_roots_and_leaves_worktrees_clean(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path,
        "mkdir -p \"$CHARNESS_RUNTIME_ROOT\"\n"
        "printf '%s\\n' \"$CHARNESS_RUNTIME_ROOT\" > \"$CHARNESS_RUNTIME_ROOT/observed-root\"\n"
        "printf '%s\\n' \"$PYTHONPYCACHEPREFIX\" \"$TMPDIR\" \"$RUFF_CACHE_DIR\" \"$COVERAGE_FILE\" \"$XDG_CACHE_HOME\" > \"$CHARNESS_RUNTIME_ROOT/observed-paths\"\n"
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
        assert (execution_root / "observed-root").read_text(encoding="utf-8").strip() == str(execution_root)
        observed_paths = (execution_root / "observed-paths").read_text(encoding="utf-8").splitlines()
        assert all(Path(path).is_relative_to(execution_root) for path in observed_paths)
        assert task_run.task_status(repo, payload["task_id"]) == payload
        worktree = Path(payload["worktree_path"])
        assert _git(worktree, "status", "--porcelain=v1", "--ignored", "--untracked-files=all").stdout == ""

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


def test_task_run_accepts_a_clean_committed_candidate(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path,
        "printf 'VALUE = 2\\n' > module.py\n"
        "git add -- module.py\n"
        "git -c user.email=test@example.com -c user.name=test commit -m 'update module'",
    )

    payload = _run(repo, tmp_path, executable)

    worktree = Path(payload["worktree_path"])
    assert payload["status"] == "completed", payload
    assert payload["target_sha"] != payload["base_sha"]
    assert payload["scope"]["changed_paths"] == ["module.py"]
    assert _git(worktree, "status", "--short").stdout == ""


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
    result = subprocess.run(
        [
            os.fspath(Path(__file__).resolve().parents[2] / "charness"),
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
        ],
        cwd=repo,
        env={
            **os.environ,
            "PATH": f"{tmp_path}{os.pathsep}{os.environ['PATH']}",
            "PYTHONPYCACHEPREFIX": str(tmp_path / "launcher-pycache"),
        },
        check=False,
        capture_output=True,
        text=True,
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
    status = subprocess.run(
        [os.fspath(Path(__file__).resolve().parents[2] / "charness"), "task", "status", "--repo-root", str(repo), "status-check"],
        cwd=repo, check=False, capture_output=True, text=True,
    )
    assert status.returncode == 0
    assert "status: completed" in status.stdout


def test_directory_scope_includes_descendants(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "pkg").mkdir()
    (repo / "pkg/base.py").write_text("BASE = 1\n", encoding="utf-8")
    _git(repo, "add", "pkg/base.py")
    _git(repo, "-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "add package")
    executable = _codex(tmp_path, "printf 'CHILD = 1\\n' > pkg/child.py")

    payload = _run(repo, tmp_path, executable, scopes=["pkg"])

    assert payload["status"] == "completed", payload
    assert payload["scope"]["specs"] == [{"path": "pkg", "kind": "directory"}]
    assert payload["scope"]["changed_paths"] == ["pkg/child.py"]


def test_explicit_base_scope_resolution_uses_selected_tree_for_dry_run(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "pkg").mkdir()
    (repo / "pkg/base.py").write_text("BASE = 1\n", encoding="utf-8")
    (repo / "literal[1].py").write_text("VALUE = 1\n", encoding="utf-8")
    selected_base = _commit(repo, "add selected base paths", "pkg", "literal[1].py")
    (repo / "current-only.py").write_text("CURRENT = 1\n", encoding="utf-8")
    _commit(repo, "add current-only path", "current-only.py")
    executable = _codex(tmp_path, "exit 99")

    payload = task_run.run_task(
        repo,
        target_path=tmp_path / "lane",
        branch="lane/base-dry-run",
        base=selected_base,
        scopes=["pkg", "literal[1].py", "current-only", "*.py"],
        prompt="inspect the selected base",
        codex=str(executable),
        effort="medium",
        dry_run=True,
    )

    specs = {spec["path"]: spec for spec in payload["scope_specs"]}
    assert specs["pkg"] == {"path": "pkg", "kind": "directory"}
    assert specs["literal[1].py"] == {"path": "literal[1].py", "kind": "exact"}
    assert specs["current-only"] == {"path": "current-only", "kind": "exact"}
    assert specs["*.py"]["kind"] == "glob"
    assert "current-only.py" not in specs["*.py"]["matches"]
    assert payload["status"] == "pass"
    assert not (tmp_path / "lane").exists()


def test_task_creation_uses_the_preflight_resolved_base_sha(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _repo(tmp_path)
    frozen_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _git(repo, "branch", "moving-base", frozen_sha)
    (repo / "later.py").write_text("LATER = 1\n", encoding="utf-8")
    later_sha = _commit(repo, "advance main", "later.py")
    executable = _codex(tmp_path, "printf 'VALUE = 2\\n' > module.py")
    original_run_create = task_run._worktree.run_create
    observed: dict[str, str | None] = {}

    def move_ref_then_create(*args, **kwargs):
        observed["base"] = kwargs.get("base")
        _git(repo, "update-ref", "refs/heads/moving-base", later_sha)
        return original_run_create(*args, **kwargs)

    monkeypatch.setattr(task_run._worktree, "run_create", move_ref_then_create)
    payload = task_run.run_task(
        repo,
        target_path=tmp_path / "lane",
        branch="lane/frozen-base",
        base="moving-base",
        scopes=["module.py"],
        prompt="update the module",
        codex=str(executable),
        effort="medium",
    )

    assert payload["status"] == "completed", payload
    assert payload["base"] == "moving-base"
    assert payload["base_sha"] == frozen_sha
    assert observed["base"] == frozen_sha
    assert _git(Path(payload["worktree_path"]), "rev-parse", "HEAD").stdout.strip() == frozen_sha


def test_explicit_base_glob_does_not_use_current_parent_head(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    selected_base = _git(repo, "rev-parse", "HEAD").stdout.strip()
    (repo / "current-only.py").write_text("CURRENT = 1\n", encoding="utf-8")
    _commit(repo, "add current-only path", "current-only.py")
    executable = _codex(tmp_path, "exit 0")

    payload = task_run.run_task(
        repo,
        target_path=tmp_path / "lane",
        branch="lane/base-glob-refusal",
        base=selected_base,
        scopes=["current-*.py"],
        prompt="inspect the selected base",
        codex=str(executable),
        effort="medium",
        dry_run=True,
    )

    assert payload["status"] == "fail"
    assert payload["phase"] == "preflight"
    assert "scope glob matched no paths" in payload["error"]
    assert not (tmp_path / "lane").exists()


def test_literal_metacharacter_file_takes_exact_precedence(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "literal[1].py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "literal1.py").write_text("OTHER = 1\n", encoding="utf-8")
    _commit(repo, "add literal metacharacter paths", "literal[1].py", "literal1.py")
    executable = _codex(tmp_path, "printf 'VALUE = 2\\n' > 'literal[1].py'")

    payload = _run(repo, tmp_path, executable, scopes=["literal[1].py"])

    assert payload["status"] == "completed", payload
    assert payload["scope_specs"] == [{"path": "literal[1].py", "kind": "exact"}]
    assert payload["scope"]["changed_paths"] == ["literal[1].py"]


def test_literal_metacharacter_directory_takes_directory_precedence(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "pkg*").mkdir()
    (repo / "pkg*/base.py").write_text("BASE = 1\n", encoding="utf-8")
    _commit(repo, "add literal metacharacter directory", "pkg*")
    executable = _codex(tmp_path, "printf 'CHILD = 1\\n' > 'pkg*/child.py'")

    payload = _run(repo, tmp_path, executable, scopes=["pkg*"])

    assert payload["status"] == "completed", payload
    assert payload["scope_specs"] == [{"path": "pkg*", "kind": "directory"}]
    assert payload["scope"]["changed_paths"] == ["pkg*/child.py"]


def test_bare_double_star_scope_includes_top_level_files(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "printf 'VALUE = 2\\n' > module.py")

    payload = _run(repo, tmp_path, executable, scopes=["**"])

    assert payload["status"] == "completed", payload
    assert payload["scope_specs"][0]["kind"] == "glob"
    assert "module.py" in payload["scope_specs"][0]["matches"]
    assert payload["scope"]["disallowed_paths"] == []


def test_glob_scope_does_not_mix_ignored_external_symlink_into_candidate_verdict(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path)
    (repo / ".gitignore").write_text(".venv/\n", encoding="utf-8")
    _commit(repo, "ignore local runtime", ".gitignore")
    executable = _codex(
        tmp_path,
        "mkdir -p .venv/bin\nln -s /usr/bin/python3 .venv/bin/python3",
    )

    payload = _run(
        repo,
        tmp_path,
        executable,
        scopes=["**"],
        require_change=False,
    )

    assert payload["status"] == "completed", payload
    assert payload["scope"]["verdict"] == "pass"
    assert payload["scope"]["changed_paths"] == []
    assert payload["populations"]["ignored"]["verdict"] == "warn"
    assert payload["populations"]["ignored"]["added"] == [".venv/"]


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

    def fail_git_dir(_target: Path) -> Path:
        raise RuntimeError("git-dir setup failed")

    monkeypatch.setattr(task_run, "_git_dir", fail_git_dir)
    payload = _run(
        repo,
        tmp_path,
        executable,
        task_id="setup-failure",
        require_change=False,
    )

    assert payload["status"] == "failed"
    assert payload["phase"] == "terminal"
    assert payload["error"] == "task lifecycle failed: git-dir setup failed"
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


def test_glob_scope_freezes_matches_and_allows_new_matching_files(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "pkg").mkdir()
    (repo / "pkg/base.py").write_text("BASE = 1\n", encoding="utf-8")
    _git(repo, "add", "pkg/base.py")
    _git(
        repo,
        "-c",
        "user.email=test@example.com",
        "-c",
        "user.name=test",
        "commit",
        "-m",
        "add package",
    )
    executable = _codex(
        tmp_path,
        "mkdir -p pkg/sub\nprintf 'CHILD = 1\\n' > pkg/sub/child.py",
    )

    payload = _run(repo, tmp_path, executable, scopes=["pkg/**/*.py"])

    assert payload["status"] == "completed", payload
    assert payload["scope_specs"] == [
        {
            "path": "pkg/**/*.py",
            "kind": "glob",
            "matches": ["pkg/base.py"],
            "match_count": 1,
            "directory_matches": [],
        }
    ]
    assert payload["scope"]["specs"][0]["matches"] == [
        "pkg/base.py",
        "pkg/sub/child.py",
    ]
    assert payload["scope"]["changed_paths"] == ["pkg/sub/child.py"]


def test_glob_scope_that_matches_a_directory_includes_descendants(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "pkg").mkdir()
    (repo / "pkg/base.txt").write_text("base\n", encoding="utf-8")
    _git(repo, "add", "pkg/base.txt")
    _git(
        repo,
        "-c",
        "user.email=test@example.com",
        "-c",
        "user.name=test",
        "commit",
        "-m",
        "add package",
    )
    executable = _codex(tmp_path, "printf 'child\\n' > pkg/child.txt")

    payload = _run(repo, tmp_path, executable, scopes=["pkg*"])

    assert payload["status"] == "completed", payload
    assert payload["scope_specs"][0]["directory_matches"] == ["pkg"]
    assert payload["scope"]["changed_paths"] == ["pkg/child.txt"]


def test_new_glob_matching_directory_does_not_widen_to_descendants(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "base.py").write_text("BASE = 1\n", encoding="utf-8")
    _commit(repo, "add base match", "base.py")
    executable = _codex(
        tmp_path,
        "mkdir escape.py\nprintf 'not python\n' > escape.py/secret.txt",
    )

    payload = _run(repo, tmp_path, executable, scopes=["*.py"])

    assert payload["status"] == "failed"
    assert payload["scope"]["disallowed_paths"] == ["escape.py/secret.txt"]
    assert payload["scope"]["specs"][0]["directory_matches"] == []


def test_zero_match_glob_fails_before_worktree_creation(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "exit 0")

    payload = _run(repo, tmp_path, executable, scopes=["missing/**/*.py"])

    assert payload["status"] == "fail"
    assert payload["phase"] == "preflight"
    assert "scope glob matched no paths" in payload["error"]
    assert not (tmp_path / "lane").exists()


def test_absent_scope_remains_exact_when_command_creates_a_directory(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "mkdir newdir\nprintf 'VALUE = 1\\n' > newdir/item.py")

    payload = _run(repo, tmp_path, executable, scopes=["newdir"])

    assert payload["status"] == "failed"
    assert payload["scope"]["specs"] == [{"path": "newdir", "kind": "exact"}]
    assert payload["scope"]["disallowed_paths"] == ["newdir/item.py"]


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


def test_timeout_with_scoped_candidate_is_validated_partial_result(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "printf 'VALUE = 2\\n' > module.py\nsleep 5")

    payload = _run(repo, tmp_path, executable, timeout_seconds=1)

    assert payload["status"] == "validated-partial-result"
    assert payload["execution"]["status"] == "timed-out"
    assert payload["candidate"]["useful"] is True
    assert payload["approval_eligibility"] == "ineligible"


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


def test_task_result_exposes_schema_bearing_delivery_without_interpreting_it(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path,
        "printf 'VALUE = 2\\n' > module.py\nprintf 'schema_version: charness.reviewer_lifecycle.v1\\napproval_eligible: false\\ndelivery_state: findings-received\\n'",
        deliver=False,
    )

    payload = _run(repo, tmp_path, executable, task_id="structured-review")

    delivery = payload["result_delivery"]
    assert delivery["structured_status"] == "valid"
    assert delivery["structured"] == {
        "schema_version": "charness.reviewer_lifecycle.v1",
        "approval_eligible": False,
        "delivery_state": "findings-received",
    }
    assert payload["reviewer_lifecycle"] == delivery["structured"]


def test_task_result_reports_malformed_schema_bearing_delivery(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path,
        "printf 'VALUE = 2\\n' > module.py\nprintf 'schema_version: broken\\nvalue: [\\n'",
        deliver=False,
    )

    payload = _run(repo, tmp_path, executable, task_id="structured-invalid")

    assert payload["result_delivery"]["structured_status"] == "invalid"
    assert "structured" not in payload["result_delivery"]


def test_task_result_rejects_non_json_yaml_without_breaking_terminal_receipt(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path,
        "printf 'VALUE = 2\\n' > module.py\n"
        "printf 'schema_version: example.v1\\nwhen: 2026-08-28\\n'",
        deliver=False,
    )

    payload = _run(repo, tmp_path, executable, task_id="non-json-yaml")

    assert payload["status"] == "completed", payload
    assert payload["result_delivery"]["structured_status"] == "invalid"
    assert task_run.task_status(repo, "non-json-yaml") == payload


def _reviewer_lifecycle_codex(tmp_path: Path, carrier: dict[str, object]) -> Path:
    encoded = shlex.quote(json.dumps(carrier, separators=(",", ":")))
    return _codex(
        tmp_path,
        f"printf '%s\\n' {encoded}\nprintf 'VALUE = 2\\n' > module.py",
        deliver=False,
    )


@pytest.mark.parametrize(
    ("name", "carrier"),
    [
        (
            "preflight-blocked",
            reviewer_lifecycle.build_lifecycle(
                status="runner-invalid",
                error="reviewer boundary unavailable",
                reviewer_started=False,
            ),
        ),
        (
            "started-timed-out",
            reviewer_lifecycle.build_lifecycle(
                status="runner-timeout",
                error="canonical runner timed out",
                returncode=124,
                reviewer_started=True,
            ),
        ),
        (
            "terminal-delivered-block",
            reviewer_lifecycle.build_lifecycle(
                status="runner-completed",
                report={
                    "schema_version": "charness.reviewer_worker_report.v1",
                    "delivery_state": "findings-received",
                    "review_verdict": "block",
                    "classification": "contract",
                    "approval_eligible": False,
                },
                returncode=0,
                reviewer_started=True,
            ),
        ),
    ],
)
def test_task_result_projects_canonical_reviewer_lifecycle_exactly(
    tmp_path: Path, name: str, carrier: dict[str, object]
) -> None:
    repo = _repo(tmp_path)
    executable = _reviewer_lifecycle_codex(tmp_path, carrier)

    payload = _run(repo, tmp_path, executable, task_id=name)
    status = task_run.task_status(repo, name)

    assert payload["result_delivery"]["structured"] == carrier
    assert payload["reviewer_lifecycle"] is payload["result_delivery"]["structured"]
    assert payload["reviewer_lifecycle"] == carrier
    assert status == payload


def test_task_result_does_not_project_non_review_schema(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    carrier = {
        "schema_version": "charness.other_result.v1",
        "status": "complete",
        "review_verdict": "block",
    }
    executable = _reviewer_lifecycle_codex(tmp_path, carrier)

    payload = _run(repo, tmp_path, executable, task_id="non-review-schema")

    assert payload["result_delivery"]["structured"] == carrier
    assert "reviewer_lifecycle" not in payload


def test_running_result_is_visible_to_the_child(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    result_path = task_run_support.task_runtime_root(repo) / "task-run" / "running-check" / "result.json"
    executable = _codex(
        tmp_path,
        f"grep '\"status\": \"running\"' {shlex.quote(str(result_path))} > running.txt\nprintf 'VALUE = 2\\n' > module.py",
    )

    payload = _run(
        repo,
        tmp_path,
        executable,
        task_id="running-check",
        scopes=["module.py", "running.txt"],
    )

    assert payload["status"] == "completed", payload
    assert (tmp_path / "lane/running.txt").read_text(encoding="utf-8").strip() == '"status": "running",'


def test_interruption_is_a_distinct_terminal_state(tmp_path: Path, monkeypatch) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "exit 0")
    monkeypatch.setattr(
        task_run,
        "_execute_codex",
        lambda *_args, **_kwargs: {
            "exit_code": None,
            "timed_out": False,
            "interrupted": True,
        },
    )

    payload = _run(repo, tmp_path, executable, require_change=False)

    assert payload["status"] == "interrupted"
    assert payload["execution"]["status"] == "interrupted"
    assert payload["phase"] == "terminal"
