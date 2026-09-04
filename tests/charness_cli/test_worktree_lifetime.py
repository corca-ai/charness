"""Ephemeral worktrees are labeled, capped, and unregistered; owned ones are not."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

from scripts.gates_support import runtime_root_retention as retention
from scripts.worktree import worktree_audit_lib as audit_lib
from scripts.worktree import worktree_create_lib as create_lib
from scripts.worktree import worktree_lifetime as lifetime
from tests.charness_cli.worktree_fixtures import copy_worktree_seed

DAY = 86400.0


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)


def _worktree_paths(repo: Path) -> set[Path]:
    result = _git("worktree", "list", "--porcelain", cwd=repo)
    assert result.returncode == 0, result.stderr
    return {
        Path(line[len("worktree ") :])
        for line in result.stdout.splitlines()
        if line.startswith("worktree ")
    }


def _age(path: Path, seconds: float, *, now: float) -> None:
    stamp = now - seconds
    for parent, dirs, files in os.walk(path):
        for name in (*dirs, *files):
            os.utime(os.path.join(parent, name), (stamp, stamp))
    os.utime(path, (stamp, stamp))


def test_throwaway_paths_are_ephemeral_and_sibling_owned_flag_wins(tmp_path: Path) -> None:
    throwaway = tmp_path / "eval-wt"
    assert lifetime.path_is_throwaway(throwaway)
    assert lifetime.resolve_kind(throwaway) == lifetime.KIND_EPHEMERAL
    assert lifetime.resolve_kind(throwaway, owned=True) == lifetime.KIND_OWNED
    feature = Path("/home/operator/src/feature-worktree")
    assert lifetime.resolve_kind(feature) == lifetime.KIND_OWNED
    assert lifetime.resolve_kind(feature, ephemeral=True) == lifetime.KIND_EPHEMERAL
    lane = tmp_path / "charness" / "runtime" / "key" / "task-run" / "lane" / "worktree"
    assert lifetime.path_is_task_run_lane(lane)
    assert lifetime.path_is_throwaway(
        Path("/home/hwidong/.cache/charness-captures/slice/worktree")
    )
    assert lifetime.path_is_throwaway(Path("/home/hwidong/codes/repo/.claude/worktrees/agent-1"))
    assert lifetime.path_is_throwaway(Path("/home/hwidong/.cache/tmp/charness/proof/x"))


def test_create_labels_tmp_ephemeral_and_owned_flag_is_not_reclaimed(tmp_path: Path) -> None:
    repo = copy_worktree_seed(tmp_path, "primary")
    ephemeral = tmp_path / "eval"
    owned = tmp_path / "feature"
    created = create_lib.run_create(repo, target_path=ephemeral, branch="eval", base="main")
    kept = create_lib.run_create(repo, target_path=owned, branch="feature", base="main", owned=True)

    assert created["created"] is True
    assert created["lifetime"]["kind"] == lifetime.KIND_EPHEMERAL
    assert kept["lifetime"]["kind"] == lifetime.KIND_OWNED
    assert lifetime.read_lifetime(ephemeral)["kind"] == lifetime.KIND_EPHEMERAL
    assert lifetime.read_lifetime(owned)["kind"] == lifetime.KIND_OWNED

    record = lifetime.read_lifetime(ephemeral)
    assert record is not None
    record["pid"] = 999_999_999
    marker = lifetime._marker_path(ephemeral)
    assert marker is not None
    marker.write_text(json.dumps(record), encoding="utf-8")

    reclaimed = lifetime.reclaim_expired(repo)
    assert any(Path(item["path"]) == ephemeral.resolve() for item in reclaimed)
    assert ephemeral.resolve() not in _worktree_paths(repo)
    assert owned.resolve() in _worktree_paths(repo)


def test_reclaim_does_not_touch_live_pid_or_unlabeled_worktrees(tmp_path: Path) -> None:
    repo = copy_worktree_seed(tmp_path, "primary")
    live = tmp_path / "live"
    unlabeled = tmp_path / "raw"
    create_lib.run_create(repo, target_path=live, branch="live", base="main")
    _git("worktree", "add", "-b", "raw", str(unlabeled), cwd=repo)
    record = lifetime.read_lifetime(live)
    assert record is not None
    record["pid"] = os.getpid()
    marker = lifetime._marker_path(live)
    assert marker is not None
    marker.write_text(json.dumps(record), encoding="utf-8")

    assert lifetime.reclaim_expired(repo) == []
    paths = _worktree_paths(repo)
    assert live.resolve() in paths
    assert unlabeled.resolve() in paths
    assert lifetime.read_lifetime(unlabeled) is None


def test_reclaim_removes_idle_unlabeled_throwaways_and_spares_fresh_and_owned(
    tmp_path: Path,
) -> None:
    repo = copy_worktree_seed(tmp_path, "primary")
    stale = tmp_path / "stale"
    fresh = tmp_path / "fresh"
    owned = tmp_path / "kept"
    _git("worktree", "add", "-b", "stale", str(stale), cwd=repo)
    _git("worktree", "add", "-b", "fresh", str(fresh), cwd=repo)
    created = create_lib.run_create(repo, target_path=owned, branch="kept", base="main", owned=True)
    assert created["created"] is True
    now = time.time()
    _age(stale, 2 * DAY, now=now)

    reclaimed = lifetime.reclaim_expired(repo, now=now)
    paths = _worktree_paths(repo)
    assert any(Path(item["path"]) == stale.resolve() for item in reclaimed)
    assert stale.resolve() not in paths
    assert fresh.resolve() in paths
    assert owned.resolve() in paths


def test_cap_evicts_oldest_ephemeral_and_refuses_when_live_lanes_fill_it(
    tmp_path: Path, monkeypatch
) -> None:
    repo = copy_worktree_seed(tmp_path, "primary")
    monkeypatch.setattr(create_lib._lifetime, "EPHEMERAL_CAP", 2)
    first = tmp_path / "one"
    second = tmp_path / "two"
    third = tmp_path / "three"
    create_lib.run_create(repo, target_path=first, branch="one", base="main")
    create_lib.run_create(repo, target_path=second, branch="two", base="main")
    create_lib.run_create(repo, target_path=third, branch="three", base="main")

    paths = _worktree_paths(repo)
    assert first.resolve() not in paths
    assert second.resolve() in paths
    assert third.resolve() in paths

    live_repo = copy_worktree_seed(tmp_path, "live-primary")
    lanes = tmp_path / "charness" / "runtime" / "key" / "task-run"
    for name in ("a", "b"):
        path = lanes / name / "worktree"
        path.parent.mkdir(parents=True)
        payload = create_lib.run_create(live_repo, target_path=path, branch=name, base="main")
        assert payload["created"] is True
        assert lifetime.read_lifetime(path)["pid"] == os.getpid()
    refused = create_lib.run_create(
        live_repo, target_path=lanes / "c" / "worktree", branch="c", base="main"
    )
    assert refused["created"] is False
    assert "cap" in refused["error"]


def test_audit_prune_reclaims_dead_pid_ephemeral(tmp_path: Path) -> None:
    repo = copy_worktree_seed(tmp_path, "primary")
    target = tmp_path / "stale"
    create_lib.run_create(repo, target_path=target, branch="stale", base="main")
    record = lifetime.read_lifetime(target)
    assert record is not None
    record["pid"] = 999_999_999
    marker = lifetime._marker_path(target)
    assert marker is not None
    marker.write_text(json.dumps(record), encoding="utf-8")

    pruned = audit_lib.run_prune(repo)
    assert pruned["status"] == audit_lib.PASS
    assert any(Path(item["path"]) == target.resolve() for item in pruned["reclaimed"])
    assert target.resolve() not in _worktree_paths(repo)


def test_lifetime_error_paths_and_cap_refusal(tmp_path: Path, monkeypatch) -> None:
    repo = copy_worktree_seed(tmp_path, "primary")
    assert lifetime.read_lifetime(tmp_path / "missing") is None
    assert lifetime.list_lifetime_records(tmp_path / "not-a-repo") == []
    assert lifetime.pid_is_live(None) is False
    assert lifetime.pid_is_live(-1) is False

    def kill_permission(_pid: int, _sig: int) -> None:
        raise PermissionError("denied")

    monkeypatch.setattr(os, "kill", kill_permission)
    assert lifetime.pid_is_live(1) is True

    def kill_oserror(_pid: int, _sig: int) -> None:
        raise OSError("boom")

    monkeypatch.setattr(os, "kill", kill_oserror)
    assert lifetime.pid_is_live(1) is False
    monkeypatch.undo()

    broken = tmp_path / "not-a-worktree"
    broken.mkdir()
    try:
        lifetime.write_lifetime(broken, kind=lifetime.KIND_EPHEMERAL)
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("expected FileNotFoundError")

    marker = tmp_path / "junk.json"
    monkeypatch.setattr(lifetime, "_marker_path", lambda _path: marker)
    marker.write_text("{not-json", encoding="utf-8")
    assert lifetime.read_lifetime(tmp_path) is None
    monkeypatch.undo()

    monkeypatch.setattr(create_lib._lifetime, "EPHEMERAL_CAP", 1)
    first = tmp_path / "charness" / "runtime" / "k" / "task-run" / "a" / "worktree"
    first.parent.mkdir(parents=True)
    create_lib.run_create(repo, target_path=first, branch="a", base="main")
    refused = create_lib.run_create(
        repo,
        target_path=tmp_path / "charness" / "runtime" / "k" / "task-run" / "b" / "worktree",
        branch="b",
        base="main",
    )
    assert refused["created"] is False
    assert "cap" in refused["error"]

    lifetime._load_repo_runtime_bootstrap()
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def test_lifetime_covers_remaining_error_branches(tmp_path: Path, monkeypatch) -> None:
    pytest_tmp = tmp_path / "pytest-tmp" / "wt"
    pytest_tmp.mkdir(parents=True)
    assert lifetime.path_is_throwaway(pytest_tmp) is True
    assert lifetime._marker_path(tmp_path) is None
    nope = tmp_path / "nope"
    nope.mkdir()
    assert lifetime._primary_path(nope) == nope.resolve()
    assert lifetime._registered_worktrees(nope) == []

    class Proc:
        returncode = 0
        stdout = "worktree /tmp/locked-wt\nlocked\n\nworktree /tmp/other-wt\n"
        stderr = ""

    monkeypatch.setattr(lifetime, "run_process", lambda *args, **kwargs: Proc())
    entries = lifetime._registered_worktrees(tmp_path)
    assert any(entry.get("locked") for entry in entries)
    assert lifetime._record_path({}) is None
    assert lifetime._is_idle(tmp_path / "missing", now=time.time(), idle_days=1.0) is True
    assert lifetime._worktree_is_dirty(tmp_path / "missing") is False
    owned = lifetime.prepare_create(tmp_path, kind=lifetime.KIND_OWNED)
    assert owned["refused"] is False
    lifetime._register_exit_remove(tmp_path / "missing")
    lifetime._EXIT_LEASES.append((tmp_path, tmp_path / "dirty"))
    lifetime._reclaim_exit_leases()


def test_unregister_falls_back_to_prune_and_skips_locked_entries(
    tmp_path: Path, monkeypatch
) -> None:
    repo = copy_worktree_seed(tmp_path, "primary")
    target = tmp_path / "ghost"
    _git("worktree", "add", "--detach", str(target), cwd=repo)
    import shutil

    shutil.rmtree(target)
    result = lifetime.unregister(target, repo_root=repo)
    assert result["removed"] is True

    locked = tmp_path / "locked"
    _git("worktree", "add", "-b", "locked", str(locked), cwd=repo)
    monkeypatch.setattr(
        lifetime,
        "_registered_worktrees",
        lambda _root: [{"path": locked, "locked": True}],
    )
    monkeypatch.setattr(lifetime, "path_is_throwaway", lambda _path: True)
    assert lifetime.reclaim_expired(repo, now=time.time() + 10 * DAY) == []
    assert locked.exists()


def test_sweep_unregisters_a_linked_lane_worktree(tmp_path: Path) -> None:
    now = time.time()
    repo = copy_worktree_seed(tmp_path, "primary")
    mine = tmp_path / "cache" / "charness" / "runtime" / "0000000000000001"
    lane = mine / "task-run" / "clean-lane"
    worktree = lane / "worktree"
    lane.mkdir(parents=True)
    added = _git("worktree", "add", "--detach", str(worktree), cwd=repo)
    assert added.returncode == 0, added.stderr
    (lane / "result.json").write_text(
        json.dumps({"phase": "terminal", "status": "completed"}), encoding="utf-8"
    )
    _age(mine, 30 * DAY, now=now)

    report = retention.sweep_runtime_root(repo, key_root=mine, now=now)
    by_path = {Path(entry["path"]): entry for entry in report["entries"]}
    assert by_path[worktree]["action"] == "removed"
    assert worktree.resolve() not in _worktree_paths(repo)
    assert (lane / "result.json").is_file()
