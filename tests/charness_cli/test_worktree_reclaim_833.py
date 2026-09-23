"""Task-run worktree reclamation by patch-equivalence (#833).

A cherry-picked lane carries different SHAs, so ancestry alone reports it
unmerged forever and its worktree lingers. Integrated means
ancestry-merged or patch-equivalent: cleanup admits it for branch
deletion, audit prune reclaims integrated-and-clean task worktrees, and
task end releases worktrees with no commits and no changes. Dirty trees
and unintegrated branches are never removed; they are reported with age.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.task_run import task_run_retention
from scripts.worktree import worktree_audit_lib as audit_lib
from scripts.worktree import worktree_cleanup_lib as cleanup_lib
from tests.charness_cli.worktree_fixtures import copy_worktree_seed


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    )


def _commit(repo: Path, message: str, *paths: str) -> str:
    _git("add", "--", *paths, cwd=repo)
    _git(
        "-c",
        "user.email=test@example.com",
        "-c",
        "user.name=test",
        "commit",
        "-m",
        message,
        cwd=repo,
    )
    return _git("rev-parse", "HEAD", cwd=repo).stdout.strip()


def _git_config(repo: Path) -> None:
    _git("config", "user.email", "test@example.com", cwd=repo)
    _git("config", "user.name", "test", cwd=repo)


def _cherry_pick(repo: Path, sha: str) -> None:
    """Cherry-pick with a distinct committer so the pick never shares a SHA.

    Test hermeticity pins GIT_COMMITTER_* env vars, which override `git -c`,
    so the committer must be overridden via env as well. Patch equivalence
    is content-based and unaffected.
    """
    env = os.environ.copy()
    env["GIT_COMMITTER_NAME"] = "picker"
    env["GIT_COMMITTER_EMAIL"] = "picker@example.com"
    subprocess.run(
        ["git", "cherry-pick", sha],
        cwd=repo,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )


def _task_worktree(repo: Path, tmp_path: Path, name: str) -> Path:
    path = tmp_path / name
    _git("worktree", "add", "-b", f"task/{name}", str(path), cwd=repo)
    _git_config(path)
    return path


def test_cleanup_accepts_cherry_picked_branch_for_deletion(
    tmp_path: Path,
) -> None:
    repo = copy_worktree_seed(tmp_path, "primary")
    _git_config(repo)
    lane = _task_worktree(repo, tmp_path, "lane")
    (lane / "lane.txt").write_text("lane\n", encoding="utf-8")
    sha = _commit(lane, "lane work", "lane.txt")
    _cherry_pick(repo, sha)

    payload = cleanup_lib.run_cleanup(
        repo, target_path=lane, delete_merged_branch=True
    )

    assert payload["status"] == cleanup_lib.PASS, payload
    actions = {action["id"]: action for action in payload["actions"]}
    assert actions["delete-branch"]["status"] == "planned"


def test_cleanup_still_refuses_unintegrated_branch(tmp_path: Path) -> None:
    repo = copy_worktree_seed(tmp_path, "primary")
    _git_config(repo)
    lane = _task_worktree(repo, tmp_path, "lane")
    (lane / "lane.txt").write_text("lane\n", encoding="utf-8")
    _commit(lane, "lane work", "lane.txt")

    payload = cleanup_lib.run_cleanup(
        repo, target_path=lane, delete_merged_branch=True
    )

    assert payload["status"] == cleanup_lib.FAIL, payload
    assert "not contained" in payload["error"]


def test_audit_prune_reclaims_integrated_clean_task_worktree(
    tmp_path: Path,
) -> None:
    repo = copy_worktree_seed(tmp_path, "primary")
    _git_config(repo)
    lane = _task_worktree(repo, tmp_path, "lane")
    (lane / "lane.txt").write_text("lane\n", encoding="utf-8")
    sha = _commit(lane, "lane work", "lane.txt")
    _cherry_pick(repo, sha)

    payload = audit_lib.run_prune(repo)

    assert payload["status"] == audit_lib.PASS, payload
    reclaimed = {item["path"]: item for item in payload["reclaimed_task_worktrees"]}
    assert str(lane.resolve()) in reclaimed
    assert reclaimed[str(lane.resolve())]["branch"] == "task/lane"
    assert not lane.exists()
    assert (
        _git("branch", "--list", "task/lane", cwd=repo).stdout.strip() == ""
    )


def test_audit_prune_reports_dirty_and_unintegrated_task_worktrees(
    tmp_path: Path,
) -> None:
    repo = copy_worktree_seed(tmp_path, "primary")
    _git_config(repo)
    dirty = _task_worktree(repo, tmp_path, "dirty")
    (dirty / "dirty.txt").write_text("dirty\n", encoding="utf-8")
    _commit(dirty, "dirty work", "dirty.txt")
    (dirty / "uncommitted.txt").write_text("uncommitted\n", encoding="utf-8")
    pending = _task_worktree(repo, tmp_path, "pending")
    (pending / "pending.txt").write_text("pending\n", encoding="utf-8")
    _commit(pending, "pending work", "pending.txt")

    payload = audit_lib.run_prune(repo)

    assert payload["status"] == audit_lib.PASS, payload
    assert payload["reclaimed_task_worktrees"] == []
    skipped = {item["path"]: item for item in payload["skipped_task_worktrees"]}
    assert "dirty or unreadable worktree" in skipped[str(dirty.resolve())]["reason"]
    assert "age_days" in skipped[str(dirty.resolve())]
    assert "unintegrated branch" in skipped[str(pending.resolve())]["reason"]
    assert "age_days" in skipped[str(pending.resolve())]
    assert dirty.exists() and pending.exists()


def _retention_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = copy_worktree_seed(tmp_path, "primary")
    _git_config(repo)
    base = _git("rev-parse", "HEAD", cwd=repo).stdout.strip()
    return repo, base


def _real_git(root: Path, *args: str) -> SimpleNamespace:
    proc = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    )
    return SimpleNamespace(
        returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr
    )


def _record_dir(tmp_path: Path, name: str) -> Path:
    record = tmp_path / name
    record.mkdir(parents=True, exist_ok=True)
    (record / "codex.stdout.log").write_text("", encoding="utf-8")
    return record


def test_empty_failed_lane_worktree_is_released_at_task_end(
    tmp_path: Path,
) -> None:
    repo, base = _retention_repo(tmp_path)
    lane = tmp_path / "lane"
    _git("worktree", "add", "-b", "task/empty", str(lane), cwd=repo)
    record = _record_dir(tmp_path, "record")
    payload = {
        "status": "failed",
        "base_sha": base,
        "candidate": {"changed_paths": [], "disallowed_paths": []},
    }

    retention = task_run_retention.release_finished_lane(
        payload,
        resolved_repo=repo,
        resolved_target=lane,
        record_dir=record,
        git=_real_git,
    )

    assert retention is not None and retention["worktree"] == "removed"
    assert "empty lane" in retention["reason"]
    assert not lane.exists()


def test_branch_integrated_reports_patch_equivalence_directly(
    tmp_path: Path,
) -> None:
    repo = copy_worktree_seed(tmp_path, "primary")
    _git_config(repo)
    lane = _task_worktree(repo, tmp_path, "lane")
    (lane / "lane.txt").write_text("lane\n", encoding="utf-8")
    sha = _commit(lane, "lane work", "lane.txt")
    _cherry_pick(repo, sha)

    integrated, how = cleanup_lib.branch_integrated(repo, "task/lane", "HEAD")

    assert integrated
    assert "patch-equivalent" in how


def test_empty_lane_removal_survives_unobservable_git(tmp_path: Path) -> None:
    repo, base = _retention_repo(tmp_path)
    record = _record_dir(tmp_path, "record")

    def _boom(_root: Path, *args: str) -> SimpleNamespace:
        raise OSError("no git")

    payload = {
        "status": "failed",
        "base_sha": base,
        "candidate": {"changed_paths": [], "disallowed_paths": []},
    }

    assert (
        task_run_retention.release_finished_lane(
            payload,
            resolved_repo=repo,
            resolved_target=repo,
            record_dir=record,
            git=_boom,
        )
        is None
    )


def test_empty_lane_removal_records_runtime_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, base = _retention_repo(tmp_path)
    lane = tmp_path / "lane"
    _git("worktree", "add", "-b", "task/empty", str(lane), cwd=repo)
    record = _record_dir(tmp_path, "record")
    (record / "runtime").mkdir()
    monkeypatch.setattr(
        task_run_retention,
        "_rmtree_writable",
        lambda _path: (_ for _ in ()).throw(OSError("busy")),
    )
    payload = {
        "status": "failed",
        "base_sha": base,
        "candidate": {"changed_paths": [], "disallowed_paths": []},
    }

    retention = task_run_retention.release_finished_lane(
        payload,
        resolved_repo=repo,
        resolved_target=lane,
        record_dir=record,
        git=_real_git,
    )

    assert retention is not None and retention["worktree"] == "removed"
    assert "runtime removal failed" in retention["reason"]
    assert not lane.exists()


def test_audit_reclaim_skips_unlistable_and_unremovable_worktrees(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = copy_worktree_seed(tmp_path, "primary")
    _git_config(repo)

    def _broken_list(_repo_root: Path) -> tuple[int, str, str]:
        return 1, "", "list failed"

    monkeypatch.setattr(
        audit_lib, "_run_git_worktree_list", _broken_list
    )
    assert audit_lib._reclaim_integrated_task_worktrees(repo) == {
        "reclaimed": [],
        "skipped": [],
    }


def test_audit_reclaim_skips_missing_unreadable_and_locked_task_worktrees(
    tmp_path: Path,
) -> None:
    repo = copy_worktree_seed(tmp_path, "primary")
    _git_config(repo)
    gone = _task_worktree(repo, tmp_path, "gone")
    (gone / "gone.txt").write_text("gone\n", encoding="utf-8")
    _commit(gone, "gone work", "gone.txt")
    locked = _task_worktree(repo, tmp_path, "locked")
    (locked / "locked.txt").write_text("locked\n", encoding="utf-8")
    _commit(locked, "locked work", "locked.txt")
    blind = _task_worktree(repo, tmp_path, "blind")
    (blind / "blind.txt").write_text("blind\n", encoding="utf-8")
    _commit(blind, "blind work", "blind.txt")
    _cherry_pick(
        repo, _git("rev-parse", "HEAD", cwd=locked).stdout.strip()
    )
    _git("worktree", "lock", str(locked), cwd=repo)
    (blind / ".git").unlink()
    subprocess.run(["rm", "-rf", str(gone)], check=True)

    result = audit_lib._reclaim_integrated_task_worktrees(repo)

    skipped = {item["path"]: item for item in result["skipped"]}
    assert str(gone.resolve()) in skipped
    assert str(locked.resolve()) in skipped
    assert "locked working tree" in skipped[str(locked.resolve())]["reason"]
    assert str(blind.resolve()) in skipped
    assert "dirty or unreadable worktree" in skipped[str(blind.resolve())]["reason"]


def test_dirty_tree_without_candidate_metadata_is_kept(tmp_path: Path) -> None:
    """The empty-lane gate never trusts missing metadata over a dirty tree."""
    repo, base = _retention_repo(tmp_path)
    lane = tmp_path / "lane"
    _git("worktree", "add", "-b", "task/dirty", str(lane), cwd=repo)
    (lane / "untracked.txt").write_text("untracked\n", encoding="utf-8")
    payload = {"status": "aborted", "base_sha": base}

    assert (
        task_run_retention.release_finished_lane(
            payload,
            resolved_repo=repo,
            resolved_target=lane,
            record_dir=_record_dir(tmp_path, "record"),
            git=_real_git,
        )
        is None
    )
    assert lane.exists()


def test_unobservable_status_keeps_the_lane(tmp_path: Path) -> None:
    repo, base = _retention_repo(tmp_path)

    def _blind_status(root: Path, *args: str) -> SimpleNamespace:
        if args[:1] == ("status",):
            return SimpleNamespace(returncode=1, stdout="", stderr="blind")
        return _real_git(root, *args)

    payload = {
        "status": "failed",
        "base_sha": base,
        "candidate": {"changed_paths": [], "disallowed_paths": []},
    }

    assert (
        task_run_retention.release_finished_lane(
            payload,
            resolved_repo=repo,
            resolved_target=repo,
            record_dir=_record_dir(tmp_path, "record"),
            git=_blind_status,
        )
        is None
    )


def test_stale_metadata_alone_keeps_the_lane(tmp_path: Path) -> None:
    """Candidate metadata claiming changes a clean tree does not have wins."""
    repo, base = _retention_repo(tmp_path)
    lane = tmp_path / "lane"
    _git("worktree", "add", "-b", "task/stale", str(lane), cwd=repo)
    payload = {
        "status": "failed",
        "base_sha": base,
        "candidate": {"changed_paths": ["ghost.py"], "disallowed_paths": []},
    }

    assert (
        task_run_retention.release_finished_lane(
            payload,
            resolved_repo=repo,
            resolved_target=lane,
            record_dir=_record_dir(tmp_path, "record"),
            git=_real_git,
        )
        is None
    )
    assert lane.exists()


def test_lane_with_stray_file_or_commits_is_kept(tmp_path: Path) -> None:
    repo, base = _retention_repo(tmp_path)
    stray_lane = tmp_path / "stray"
    _git("worktree", "add", "-b", "task/stray", str(stray_lane), cwd=repo)
    (stray_lane / "stray.py").write_text("STRAY = 1\n", encoding="utf-8")
    stray_payload = {
        "status": "failed",
        "base_sha": base,
        "candidate": {"changed_paths": ["stray.py"], "disallowed_paths": ["stray.py"]},
    }

    assert (
        task_run_retention.release_finished_lane(
            stray_payload,
            resolved_repo=repo,
            resolved_target=stray_lane,
            record_dir=_record_dir(tmp_path, "record-stray"),
            git=_real_git,
        )
        is None
    )
    assert stray_lane.exists()

    committed_lane = tmp_path / "committed"
    _git("worktree", "add", "-b", "task/committed", str(committed_lane), cwd=repo)
    (committed_lane / "work.py").write_text("x = 1\n", encoding="utf-8")
    _git("add", "work.py", cwd=committed_lane)
    _git("commit", "-m", "lane work", cwd=committed_lane)
    committed_payload = {
        "status": "failed",
        "base_sha": base,
        "candidate": {"changed_paths": [], "disallowed_paths": []},
    }

    assert (
        task_run_retention.release_finished_lane(
            committed_payload,
            resolved_repo=repo,
            resolved_target=committed_lane,
            record_dir=_record_dir(tmp_path, "record-committed"),
            git=_real_git,
        )
        is None
    )
    assert committed_lane.exists()
