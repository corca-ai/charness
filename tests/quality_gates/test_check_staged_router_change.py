"""Tests for the router-change pre-commit refusal.

The gate (`scripts/hooks/check_staged_router_change.py`) refuses a commit that stages
`AGENTS.md` or `CLAUDE.md` until the operator has approved it. What these pin:

- the refusal fires on a router edit and NOT on ordinary work, so the boundary is
  a stop-and-ask rather than a tax on every commit;
- the symlink alias collapses to one router, so `CLAUDE.md -> AGENTS.md` does not
  read as two independent instruction surfaces;
- an unreadable index reports `unestablished` and exits non-zero rather than
  printing a clean verdict over a scope it never read (the empty-scope rule);
- the escape is acknowledged in the payload and its message says the approval
  must be the operator's, because a silent bypass is the failure this gate exists
  to make impossible.
"""

from __future__ import annotations

import importlib
import os
import subprocess
from pathlib import Path

import yaml

from tests.script_main import run_loaded_script_main

csrc = importlib.import_module("scripts.hooks.check_staged_router_change")


def run_gate(*args: str, env: dict[str, str] | None = None):
    """Drive the gate's `main()` in-process.

    Subprocess, not in-process, is what this repo ratchets down: a nested CLI per
    behavior is what made the suite process-bound. Every assertion here is about
    the payload and the exit code, both of which `main()` returns directly.
    """
    return run_loaded_script_main("check_staged_router_change.py", csrc, *args, env=env)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def _repo(tmp_path: Path) -> Path:
    from .repo_shapes import install_committed_repo

    return install_committed_repo(
        tmp_path / "repo",
        {"AGENTS.md": "# Router\n", "app.py": "x = 1\n"},
    )


def test_ordinary_work_is_not_a_router_change(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "app.py").write_text("x = 2\n", encoding="utf-8")
    _git(repo, "add", "app.py")
    assert csrc.staged_router_paths(str(repo)) == []


def test_staged_router_edit_is_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "AGENTS.md").write_text("# Router\n\nA new standing rule.\n", encoding="utf-8")
    _git(repo, "add", "AGENTS.md")
    assert csrc.staged_router_paths(str(repo)) == ["AGENTS.md"]

    result = run_gate("--repo-root", str(repo))
    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["state"] == "blocked"
    assert payload["routers"] == ["AGENTS.md"]
    # The refusal must tell the agent to stop and ask. Naming only the flag turns
    # the boundary into a speed bump with a documented way around it.
    assert "STOP and ask the operator" in payload["detail"]
    assert "second operating manual" in payload["detail"]


def test_staged_router_deletion_is_refused(tmp_path: Path) -> None:
    """No realpath to resolve; removing the router still has to be asked about."""
    repo = _repo(tmp_path)
    _git(repo, "rm", "-q", "AGENTS.md")
    assert csrc.staged_router_paths(str(repo)) == ["AGENTS.md"]


def test_symlink_alias_collapses_to_one_router(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "CLAUDE.md").symlink_to("AGENTS.md")
    _git(repo, "add", "CLAUDE.md")
    _git(repo, "commit", "-qm", "alias")

    (repo / "AGENTS.md").write_text("# Router\n\nEdited.\n", encoding="utf-8")
    _git(repo, "add", "AGENTS.md", "CLAUDE.md")
    # Both names are guarded, but they are one file: the verdict counts routers,
    # not index entries.
    assert csrc.staged_router_paths(str(repo)) == ["AGENTS.md"]


def test_independent_claude_md_is_its_own_router(tmp_path: Path) -> None:
    """A consumer repo whose CLAUDE.md is a real file, not a link to AGENTS.md."""
    repo = _repo(tmp_path)
    (repo / "CLAUDE.md").write_text("# Separate router\n", encoding="utf-8")
    _git(repo, "add", "CLAUDE.md")
    assert csrc.staged_router_paths(str(repo)) == ["CLAUDE.md"]


def test_operator_approval_exits_clean_and_stays_acknowledged(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "AGENTS.md").write_text("# Router\n\nApproved edit.\n", encoding="utf-8")
    _git(repo, "add", "AGENTS.md")

    result = run_gate("--repo-root", str(repo), "--allow-router-change")
    assert result.returncode == 0
    payload = yaml.safe_load(result.stdout)
    assert payload["state"] == "allowed"
    assert "operator-approved" in payload["detail"]


def test_env_bypass_is_honored_and_zero_is_not_truthy(tmp_path: Path) -> None:
    """`=0` is the spelling an operator uses to keep the guard ON.

    Its sibling `check_staged_worktree_consistency` shipped with `=0` read as
    truthy, which turned the bypass on instead of off; the same defect here would
    disarm the boundary in the exact moment someone tried to arm it.
    """
    repo = _repo(tmp_path)
    (repo / "AGENTS.md").write_text("# Router\n\nEdited.\n", encoding="utf-8")
    _git(repo, "add", "AGENTS.md")

    args = ("--repo-root", str(repo))

    blocked = run_gate(*args, env={**os.environ, "CHARNESS_ALLOW_ROUTER_CHANGE": "0"})
    assert blocked.returncode == 1
    assert yaml.safe_load(blocked.stdout)["state"] == "blocked"

    allowed = run_gate(*args, env={**os.environ, "CHARNESS_ALLOW_ROUTER_CHANGE": "1"})
    assert allowed.returncode == 0
    assert yaml.safe_load(allowed.stdout)["state"] == "allowed"


def test_the_two_empty_answers_are_not_collapsed(tmp_path: Path) -> None:
    """An empty index established nothing; a non-router index answered the question.

    Collapsing them is what puts a detector in this repo's
    `positive-verdict-over-zero` bucket: `state: clean` over a scope it never
    read is indistinguishable from `state: clean` over a scope it did.
    """
    repo = _repo(tmp_path)

    nothing_staged = run_gate("--repo-root", str(repo))
    assert nothing_staged.returncode == 0
    empty = yaml.safe_load(nothing_staged.stdout)
    assert empty["staged_paths_inspected"] == 0
    assert "nothing was checked" in empty["detail"]

    (repo / "app.py").write_text("x = 2\n", encoding="utf-8")
    _git(repo, "add", "app.py")
    discovered = run_gate("--repo-root", str(repo))
    assert discovered.returncode == 0
    answered = yaml.safe_load(discovered.stdout)
    assert answered["staged_paths_inspected"] == 1
    assert "nothing was checked" not in answered["detail"]
    assert "none of them is" in answered["detail"]


def test_unreadable_index_is_unestablished_not_clean(tmp_path: Path) -> None:
    not_a_repo = tmp_path / "plain"
    not_a_repo.mkdir()

    result = run_gate("--repo-root", str(not_a_repo))
    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["state"] == "unestablished"
    assert "no router verdict was reached" in payload["detail"]


def test_pre_commit_hook_arms_the_refusal() -> None:
    """A gate the hook does not run is prose with a YAML formatter attached."""
    hook = (Path(__file__).resolve().parents[2] / ".githooks" / "pre-commit").read_text(
        encoding="utf-8"
    )
    assert 'scripts/hooks/check_staged_router_change.py --repo-root "$REPO_ROOT"' in hook
    assert 'check_staged_router_change.py --repo-root "$REPO_ROOT" || true' not in hook
