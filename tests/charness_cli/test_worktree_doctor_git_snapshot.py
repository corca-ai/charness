"""The single Git snapshot that feeds canonical worktree doctor checks."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts import worktree_doctor_checks as checks
from scripts import worktree_doctor_lib as lib
from tests.charness_cli.worktree_fixtures import copy_worktree_seed


@pytest.mark.boundary_contract(
    reason="exercise Git's own core.hooksPath resolution against the shared seed repository"
)
def _git(*args: str, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _repo(tmp_path: Path) -> Path:
    return copy_worktree_seed(tmp_path, "repo")


def test_canonical_doctor_reads_one_checkout_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    calls: list[tuple[str, ...]] = []

    def observed(repo_root: Path, *args: str) -> str | None:
        calls.append(args)
        return ".git\n.git\nfalse\n.git/hooks"

    monkeypatch.setattr(checks, "_git_output", observed)

    result = checks.run_canonical_checks(repo, disabled=set())

    assert all(item.status in {"pass", "skipped"} for item in result)
    assert calls == [
        (
            "rev-parse",
            "--git-common-dir",
            "--git-dir",
            "--is-bare-repository",
            "--git-path",
            "hooks",
        ),
    ]


def test_hook_checks_disabled_preserves_three_field_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    calls: list[tuple[str, ...]] = []

    def observed(repo_root: Path, *args: str) -> str | None:
        calls.append(args)
        return ".git\n.git\nfalse"

    monkeypatch.setattr(checks, "_git_output", observed)

    result = checks.run_canonical_checks(
        repo,
        disabled={"hooks_path", "lefthook_shim", "husky_dir"},
    )

    assert [item.id for item in result] == ["git_common_dir", "worktree_isolation"]
    assert calls == [
        (
            "rev-parse",
            "--git-common-dir",
            "--git-dir",
            "--is-bare-repository",
        )
    ]


def test_explicit_default_hooks_path_is_operationally_default(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _git("config", "core.hooksPath", ".git/hooks", cwd=repo)

    payload = lib.run_doctor(repo)
    hooks = next(check for check in payload["checks"] if check["id"] == "hooks_path")

    assert hooks["status"] == "skipped"
    assert "default directory" in hooks["detail"]


@pytest.mark.parametrize("absolute", [False, True])
def test_effective_custom_hooks_path_preserves_relative_and_absolute_targets(
    tmp_path: Path, absolute: bool
) -> None:
    repo = _repo(tmp_path)
    hooks_dir = repo / ("absolute-hooks" if absolute else "relative-hooks")
    hooks_dir.mkdir()
    _git("config", "core.hooksPath", str(hooks_dir) if absolute else hooks_dir.name, cwd=repo)

    facts = checks.git_checkout_facts(repo)
    assert facts.hooks_path == hooks_dir.resolve()
    assert facts.common_dir is not None
    assert facts.hooks_path != facts.common_dir / "hooks"

    payload = lib.run_doctor(repo)
    hooks = next(check for check in payload["checks"] if check["id"] == "hooks_path")
    assert hooks["status"] == "pass"
    assert str(hooks_dir.resolve()) in hooks["detail"]


def test_malformed_hooks_snapshot_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(checks, "_git_output", lambda *_args, **_kwargs: ".git\n.git\nfalse\n")

    facts = checks.git_checkout_facts(tmp_path)

    assert facts == checks.GitCheckoutFacts(None, None, None, None)
    result = checks.run_canonical_checks(tmp_path, disabled=set())
    hooks = next(check for check in result if check.id == "hooks_path")
    assert hooks.status == checks.FAIL
