from __future__ import annotations

import subprocess
from pathlib import Path

from scripts import worktree_cleanup_lib as lib


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


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


def _add_feature_worktree(repo: Path, tmp_path: Path) -> Path:
    feature_path = tmp_path / "feature"
    _git("worktree", "add", "-b", "feature", str(feature_path), cwd=repo)
    (feature_path / "feature.txt").write_text("feature\n", encoding="utf-8")
    _git("add", "feature.txt", cwd=feature_path)
    _git("commit", "-m", "feature", cwd=feature_path)
    return feature_path


def test_cleanup_dry_run_plans_safe_branch_deletion(tmp_path: Path) -> None:
    repo = _make_primary(tmp_path)
    feature_path = _add_feature_worktree(repo, tmp_path)
    _git("merge", "--no-ff", "feature", "-m", "merge feature", cwd=repo)

    payload = lib.run_cleanup(repo, target_path=feature_path, delete_merged_branch=True)

    assert payload["status"] == lib.PASS
    assert payload["dry_run"] is True
    assert payload["branch"] == "feature"
    actions = {action["id"]: action for action in payload["actions"]}
    assert actions["remove-worktree"]["status"] == "planned"
    assert actions["delete-branch"]["command"] == ["git", "branch", "-D", "feature"]
    assert "Re-run with `--yes`" in payload["next_action"]
    assert feature_path.exists()


def test_cleanup_executes_remove_branch_and_prune(tmp_path: Path) -> None:
    repo = _make_primary(tmp_path)
    feature_path = _add_feature_worktree(repo, tmp_path)
    _git("merge", "--no-ff", "feature", "-m", "merge feature", cwd=repo)

    payload = lib.run_cleanup(repo, target_path=feature_path, delete_merged_branch=True, yes=True)

    assert payload["status"] == lib.PASS, payload
    assert payload["dry_run"] is False
    assert {action["status"] for action in payload["actions"]} == {"done"}
    assert not feature_path.exists()
    branch = subprocess.run(
        ["git", "rev-parse", "--verify", "feature"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert branch.returncode != 0


def test_cleanup_refuses_unmerged_branch_deletion(tmp_path: Path) -> None:
    repo = _make_primary(tmp_path)
    feature_path = _add_feature_worktree(repo, tmp_path)

    payload = lib.run_cleanup(repo, target_path=feature_path, delete_merged_branch=True, yes=True)

    assert payload["status"] == lib.FAIL
    assert "refusing to delete branch" in payload["error"]
    assert feature_path.exists()


def test_cleanup_from_target_worktree_uses_primary_head_for_branch_safety(tmp_path: Path) -> None:
    repo = _make_primary(tmp_path)
    feature_path = _add_feature_worktree(repo, tmp_path)

    payload = lib.run_cleanup(feature_path, target_path=feature_path, delete_merged_branch=True, yes=True)

    assert payload["status"] == lib.FAIL
    assert payload["repo_root"] == str(repo.resolve())
    assert payload["requested_repo_root"] == str(feature_path.resolve())
    assert "refusing to delete branch" in payload["error"]
    assert feature_path.exists()


def test_cleanup_from_target_worktree_executes_from_primary_after_merge(tmp_path: Path) -> None:
    repo = _make_primary(tmp_path)
    feature_path = _add_feature_worktree(repo, tmp_path)
    _git("merge", "--no-ff", "feature", "-m", "merge feature", cwd=repo)

    payload = lib.run_cleanup(feature_path, target_path=feature_path, delete_merged_branch=True, yes=True)

    assert payload["status"] == lib.PASS, payload
    assert payload["repo_root"] == str(repo.resolve())
    assert payload["requested_repo_root"] == str(feature_path.resolve())
    assert not feature_path.exists()


def test_cleanup_refuses_primary_worktree(tmp_path: Path) -> None:
    repo = _make_primary(tmp_path)

    payload = lib.run_cleanup(repo, target_path=repo, yes=True)

    assert payload["status"] == lib.FAIL
    assert "primary worktree" in payload["error"]
