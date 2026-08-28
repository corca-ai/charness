from __future__ import annotations

import json
import os
import shlex
import subprocess
from pathlib import Path

import pytest

from scripts import task_run
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
    executable = tmp_path / "fake-codex"
    delivery = "printf 'task complete\\n'" if deliver else ""
    executable.write_text(f"#!/bin/sh\n{body}\n{delivery}\n", encoding="utf-8")
    executable.chmod(0o755)
    return executable


def _run(repo: Path, tmp_path: Path, executable: Path, **kwargs):
    scopes = kwargs.pop("scopes", ["module.py"])
    require_change = kwargs.pop("require_change", True)
    return task_run.run_task(
        repo,
        target_path=tmp_path / "lane",
        branch="lane/task-run",
        base="HEAD",
        scopes=scopes,
        prompt="update the module",
        codex=str(executable),
        require_change=require_change,
        **kwargs,
    )


def test_codex_argument_shorthands_fix_luna_and_preserve_extra_host_arguments(tmp_path: Path) -> None:
    git_common_dir = tmp_path / ".git"
    git_common_dir.mkdir()
    assert task_run.build_codex_args(
        effort="xhigh",
        writable_dirs=[git_common_dir],
        extra=["--approve-for-me"],
    ) == [
        "--sandbox",
        "workspace-write",
        "--add-dir",
        str(git_common_dir),
        "--approve-for-me",
        "-m",
        "gpt-5.6-luna",
        "-c",
        "model_reasoning_effort=xhigh",
    ]


@pytest.mark.parametrize(
    "extra",
    [
        ["--model", "gpt-5.6-sol"],
        ["--model=gpt-5.6-sol"],
        ["-m", "gpt-5.6-sol"],
        ["-c", "model=gpt-5.6-sol"],
        ["-c", "model = gpt-5.6-sol"],
        ["-cmodel=gpt-5.6-sol"],
        ["--config=model=gpt-5.6-sol"],
    ],
)
def test_codex_extra_arguments_cannot_override_luna(extra: list[str]) -> None:
    with pytest.raises(task_run.TaskRunError, match="fixes the Codex model"):
        task_run.build_codex_args(extra=extra)


@pytest.mark.parametrize(
    ("extra", "message"),
    [
        (["--"], "option parsing"),
        (["-c", "model_reasoning_effort=high"], "reasoning effort"),
        (["--config", "model_reasoning_effort=high"], "reasoning effort"),
        (["-cmodel_reasoning_effort=high"], "reasoning effort"),
        (["-c=model_reasoning_effort=high"], "reasoning effort"),
        (["--config=model_reasoning_effort=high"], "reasoning effort"),
        (["--config model_reasoning_effort = high"], "reasoning effort"),
    ],
)
def test_codex_extra_arguments_cannot_escape_or_override_fixed_effort(
    extra: list[str], message: str
) -> None:
    with pytest.raises(task_run.TaskRunError, match=message):
        task_run.build_codex_args(effort="xhigh", extra=extra)


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
    command = payload["codex"]["command"]
    assert command[command.index("--sandbox") + 1] == "workspace-write"
    assert Path(command[command.index("--add-dir") + 1]) == repo / ".git"
    assert payload["codex"]["command"] == [
        str(executable),
        "exec",
        "--sandbox",
        "workspace-write",
        "--add-dir",
        str(repo / ".git"),
        "-m",
        "gpt-5.6-luna",
        "-c",
        "model_reasoning_effort=xhigh",
        "<prompt>",
    ]


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
    executable = _codex(tmp_path, "exit 0")
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
            "high",
            "--codex",
            str(executable),
        ],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "status: fail" in result.stdout
    assert "--lane cannot be combined with --path" in result.stdout


def test_task_run_cli_does_not_expose_model_override() -> None:
    cli = os.fspath(Path(__file__).resolve().parents[2] / "charness")
    help_result = subprocess.run(
        [cli, "task", "run", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert help_result.returncode == 0
    assert "--model" not in help_result.stdout


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


def test_task_run_grants_codex_both_common_and_linked_worktree_git_dirs(
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
    args = captured_args.read_text(encoding="utf-8").splitlines()
    granted_dirs = [Path(args[index + 1]) for index, arg in enumerate(args) if arg == "--add-dir"]
    assert git_common_dir == repo / ".git"
    assert git_worktree_dir.parent == git_common_dir / "worktrees"
    assert granted_dirs == [git_common_dir, git_worktree_dir]
    assert payload["codex"]["command"].count("--add-dir") == 2


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
    executable = _codex(tmp_path, "printf 'VALUE = 3\\n' > module.py")
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
            "--codex",
            str(executable),
        ],
        cwd=repo,
        env={**os.environ, "PYTHONPYCACHEPREFIX": str(tmp_path / "launcher-pycache")},
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
        [os.fspath(Path(__file__).resolve().parents[2] / "charness"), "task", "--repo-root", str(repo), "status", "status-check"],
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
    assert payload["error"] == "completion evidence failed: scope refresh failed"
    assert task_run.task_status(repo, "completion-failure") == payload


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
    executable = _codex(
        tmp_path,
        "grep '\"status\": \"running\"' \"$CHARNESS_RUNTIME_ROOT/task-run/running-check/result.json\" > running.txt\nprintf 'VALUE = 2\\n' > module.py",
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
