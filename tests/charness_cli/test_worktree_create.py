from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import worktree_create_lib as lib  # noqa: E402


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _git_commit_no_hooks(message: str, *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-c", "core.hooksPath=/dev/null", "commit", "-m", message],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


def _make_primary(tmp_path: Path) -> Path:
    repo = tmp_path / "primary"
    repo.mkdir()
    _git("init", "--initial-branch=main", cwd=repo)
    _git("config", "user.email", "wt-test@example.com", cwd=repo)
    _git("config", "user.name", "Worktree Test", cwd=repo)
    (repo / "README.md").write_text("seed\n", encoding="utf-8")
    _git("add", "README.md", cwd=repo)
    _git("commit", "-m", "seed", cwd=repo)
    return repo


def _install_lefthook_shim(repo: Path) -> None:
    hooks_dir = repo / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    shim = hooks_dir / "pre-commit"
    shim.write_text("#!/bin/sh\nexec lefthook run pre-commit\n", encoding="utf-8")
    shim.chmod(0o755)


def test_create_dry_run_plans_git_worktree_add(tmp_path: Path) -> None:
    repo = _make_primary(tmp_path)
    target = tmp_path / "feature"

    payload = lib.run_create(repo, target_path=target, branch="feature", base="main", dry_run=True)

    assert payload["status"] == lib.PASS
    assert payload["dry_run"] is True
    assert payload["created"] is False
    assert payload["actions"] == [
        {
            "id": "create-worktree",
            "command": ["git", "worktree", "add", "-b", "feature", str(target.resolve()), "main"],
            "status": "planned",
        }
    ]
    assert not target.exists()


def test_create_runs_doctor_and_warns_for_unprepared_worktree(tmp_path: Path, monkeypatch) -> None:
    repo = _make_primary(tmp_path)
    _install_lefthook_shim(repo)
    target = tmp_path / "feature"
    monkeypatch.setenv(
        "PATH",
        str(Path(sys.executable).resolve().parent) + os.pathsep + "/usr/bin" + os.pathsep + "/bin",
    )

    payload = lib.run_create(repo, target_path=target, branch="feature", base="main")

    assert payload["status"] == lib.WARN
    assert payload["created"] is True
    assert target.exists()
    assert payload["doctor"]["status"] == "fail"
    assert "charness worktree prepare" in payload["next_action"]


def test_create_prepare_runs_adapter_and_returns_pass(tmp_path: Path, monkeypatch) -> None:
    repo = _make_primary(tmp_path)
    _install_lefthook_shim(repo)
    (repo / ".agents").mkdir()
    (repo / ".agents" / "worktree-adapter.yaml").write_text(
        (
            "version: 1\n"
            "prepare:\n"
            "  commands:\n"
            "    - id: install-lefthook\n"
            "      argv:\n"
            "        - sh\n"
            "        - -c\n"
            "        - 'mkdir -p node_modules/lefthook-linux-x64/bin && printf \"#!/bin/sh\\nexit 0\\n\" > node_modules/lefthook-linux-x64/bin/lefthook && chmod +x node_modules/lefthook-linux-x64/bin/lefthook'\n"
        ),
        encoding="utf-8",
    )
    _git("add", ".agents/worktree-adapter.yaml", cwd=repo)
    _git_commit_no_hooks("add worktree adapter", cwd=repo)
    target = tmp_path / "feature"
    monkeypatch.setenv(
        "PATH",
        str(Path(sys.executable).resolve().parent) + os.pathsep + "/usr/bin" + os.pathsep + "/bin",
    )

    payload = lib.run_create(repo, target_path=target, branch="feature", base="main", prepare=True)

    assert payload["status"] == lib.PASS, payload
    assert payload["created"] is True
    assert payload["prepare"]["status"] == "pass"
    assert payload["doctor"]["status"] == "pass"


def test_cli_worktree_create_and_add_are_discoverable(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "charness"), "worktree", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "create" in result.stdout
    assert "add" in result.stdout

    create_help = subprocess.run(
        [sys.executable, str(ROOT / "charness"), "worktree", "create", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert create_help.returncode == 0, create_help.stderr
    assert "--prepare" in create_help.stdout
    assert "--path" in create_help.stdout

    add_help = subprocess.run(
        [sys.executable, str(ROOT / "charness"), "worktree", "add", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert add_help.returncode == 0, add_help.stderr
    assert "--prepare" in add_help.stdout
    assert "--path" in add_help.stdout


def test_cli_worktree_create_json_executes_and_reports_doctor(tmp_path: Path) -> None:
    repo = _make_primary(tmp_path)
    target = tmp_path / "cli-feature"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "charness"),
            "worktree",
            "create",
            "--repo-root",
            str(repo),
            "--path",
            str(target),
            "--branch",
            "cli-feature",
            "--base",
            "main",
            "--json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == lib.PASS
    assert payload["created"] is True
    assert payload["doctor"]["status"] == "pass"
    assert target.exists()
