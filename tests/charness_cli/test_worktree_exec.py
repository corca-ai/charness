from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import worktree_exec_lib as lib

ROOT = Path(__file__).resolve().parents[2]


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _make_primary(tmp_path: Path) -> Path:
    repo = tmp_path / "primary"
    repo.mkdir()
    _git("init", "--initial-branch=main", cwd=repo)
    (repo / "README.md").write_text("seed\n", encoding="utf-8")
    _git("add", "README.md", cwd=repo)
    _git("-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "seed", cwd=repo)
    return repo


def _status(repo: Path, *extra: str) -> str:
    return _git("status", "--porcelain=v1", "--untracked-files=all", *extra, cwd=repo).stdout


def test_exec_environment_routes_runtime_outputs_outside_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    runtime = tmp_path / "runtime"
    configured = lib.prepare_exec_environment(
        repo,
        {
            "CHARNESS_RUNTIME_ROOT": str(runtime),
            "CHARNESS_REPO_ROOT": str(tmp_path / "outer-worktree"),
            "PYTHONPYCACHEPREFIX": str(repo / "local-pycache"),
            "TMPDIR": str(repo / "local-tmp"),
            "TMP": str(repo / "local-tmp"),
            "TEMP": str(repo / "local-tmp"),
            "PYTEST_DEBUG_TEMPROOT": str(repo / "local-pytest-tmp"),
            "CHARNESS_PYTEST_CACHE_DIR": str(repo / "local-pytest-cache"),
            "COVERAGE_FILE": str(repo / ".coverage"),
            "PYTEST_ADDOPTS": "-q",
        },
    )

    for key in (
        "PYTHONPYCACHEPREFIX",
        "TMPDIR",
        "TMP",
        "TEMP",
        "PYTEST_DEBUG_TEMPROOT",
        "CHARNESS_PYTEST_CACHE_DIR",
        "COVERAGE_FILE",
    ):
        value = Path(configured[key])
        if key == "COVERAGE_FILE":
            value = value.parent
        assert repo.resolve() not in value.resolve().parents
        assert value.exists()
    assert f"cache_dir={runtime / 'pytest-cache'}" in configured["PYTEST_ADDOPTS"]
    assert "CHARNESS_REPO_ROOT" not in configured


def test_explicit_runtime_root_replaces_all_inherited_managed_paths(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    inherited = tmp_path / "shared-runtime"
    lane_runtime = tmp_path / "lane-runtime"
    configured = lib.prepare_exec_environment(
        repo,
        {
            "CHARNESS_RUNTIME_ROOT": str(inherited),
            "PYTHONPYCACHEPREFIX": str(inherited / "pycache"),
            "TMPDIR": str(inherited / "tmp"),
            "RUFF_CACHE_DIR": str(inherited / "ruff"),
            "COVERAGE_FILE": str(inherited / "coverage" / ".coverage"),
            "XDG_CACHE_HOME": str(inherited / "xdg-cache"),
        },
        runtime_root=lane_runtime,
    )

    for key in (
        "CHARNESS_RUNTIME_ROOT",
        "PYTHONPYCACHEPREFIX",
        "TMPDIR",
        "RUFF_CACHE_DIR",
        "COVERAGE_FILE",
        "XDG_CACHE_HOME",
    ):
        assert Path(configured[key]).is_relative_to(lane_runtime)


def test_exec_refuses_primary_worktree_by_default(tmp_path: Path) -> None:
    repo = _make_primary(tmp_path)
    with pytest.raises(lib.WorktreeExecError, match="primary worktree"):
        lib.run_exec(repo, ["/bin/true"])


def test_exec_preflight_reads_one_topology_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _make_primary(tmp_path)
    calls: list[tuple[str, ...]] = []
    original = lib._doctor_checks._git_output

    def observed(repo_root: Path, *args: str) -> str | None:
        calls.append(args)
        return original(repo_root, *args)

    monkeypatch.setattr(lib._doctor_checks, "_git_output", observed)

    with pytest.raises(lib.WorktreeExecError, match="primary worktree"):
        lib.run_exec(repo, ["/bin/true"])

    assert calls == [
        (
            "rev-parse",
            "--git-common-dir",
            "--git-dir",
            "--is-bare-repository",
        )
    ]


def test_cli_exec_in_linked_worktree_keeps_python_outputs_external(tmp_path: Path) -> None:
    repo = _make_primary(tmp_path)
    (repo / "module.py").write_text("VALUE = 7\n", encoding="utf-8")
    (repo / "test_module.py").write_text(
        "import module\n\n\n"
        "def test_value(tmp_path):\n"
        "    assert tmp_path.is_dir()\n"
        "    assert module.VALUE == 7\n",
        encoding="utf-8",
    )
    _git("add", "module.py", "test_module.py", cwd=repo)
    _git("-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "tests", cwd=repo)
    linked = tmp_path / "linked"
    _git("worktree", "add", "-b", "slice", str(linked), cwd=repo)

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "charness"),
            "worktree",
            "exec",
            "--repo-root",
            str(linked),
            "--",
            sys.executable,
            "-m",
            "pytest",
            "-q",
        ],
        cwd=ROOT,
        env={
            **os.environ,
            "CHARNESS_STATE_HOME": str(tmp_path / "home" / ".local" / "state"),
            "PYTHONPYCACHEPREFIX": str(tmp_path / "launcher-pycache"),
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        },
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert _status(linked) == ""
    assert _status(linked, "--ignored") == ""
    assert not (linked / "__pycache__").exists()
    assert not (linked / ".pytest_cache").exists()
    assert not (linked / ".coverage").exists()


def test_cli_worktree_exec_help_and_primary_refusal(tmp_path: Path) -> None:
    help_result = subprocess.run(
        [sys.executable, str(ROOT / "charness"), "worktree", "exec", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert help_result.returncode == 0, help_result.stderr
    assert "external runtime caches" in help_result.stdout

    repo = _make_primary(tmp_path)
    refusal = subprocess.run(
        [
            sys.executable,
            str(ROOT / "charness"),
            "worktree",
            "exec",
            "--repo-root",
            str(repo),
            "--",
            "/bin/true",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert refusal.returncode == 2
    assert "primary worktree" in refusal.stdout
