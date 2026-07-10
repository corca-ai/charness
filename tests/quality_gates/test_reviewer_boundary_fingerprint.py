"""Tests for the #428 reviewer-boundary integrity fingerprint.

Three recorded shared-tree reviewer violations (staged+committed content, an
unauthorized child spawn, a no-write-brief doc edit) were not caught by prose
rules or the narrow #258 staged-reversion gate, because both trust the
reviewer's own report of what it touched. `reviewer_boundary_fingerprint.py`
instead snapshots the whole worktree+index state before a reviewer runs and
diffs it after, so drift is caught regardless of mutation shape.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .support import run_script

SCRIPT = "skills/shared/scripts/reviewer_boundary_fingerprint.py"


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def _repo(tmp_path: Path) -> Path:
    """A seeded repo with one tracked file and one pre-existing untracked file."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    (repo / "f.py").write_text("v1\n", encoding="utf-8")
    _git(repo, "add", "f.py")
    _git(repo, "commit", "-qm", "seed")
    (repo / "pre.txt").write_text("pre-existing untracked\n", encoding="utf-8")
    return repo


def _snapshot(repo: Path) -> subprocess.CompletedProcess[str]:
    return run_script(SCRIPT, "snapshot", "--repo-root", str(repo))


def _verify(repo: Path) -> tuple[int, dict]:
    result = run_script(SCRIPT, "verify", "--repo-root", str(repo))
    return result.returncode, json.loads(result.stdout)


def _drift_paths(payload: dict) -> set[tuple[str, str | None]]:
    return {(d["kind"], d["path"]) for d in payload["drift"]}


def test_clean_verify_is_ok(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    snap = _snapshot(repo)
    assert snap.returncode == 0, snap.stdout + snap.stderr
    assert json.loads(snap.stdout)["ok"] is True

    code, payload = _verify(repo)
    assert code == 0, payload
    assert payload == {"ok": True, "drift": [], "before_path": payload["before_path"]}


def test_tracked_file_modified_is_flagged(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _snapshot(repo)
    (repo / "f.py").write_text("v2\n", encoding="utf-8")

    code, payload = _verify(repo)
    assert code == 1
    assert payload["ok"] is False
    assert ("worktree", "f.py") in _drift_paths(payload)


def test_new_untracked_file_is_flagged(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _snapshot(repo)
    (repo / "new.txt").write_text("new\n", encoding="utf-8")

    code, payload = _verify(repo)
    assert code == 1
    assert ("untracked-added", "new.txt") in _drift_paths(payload)


def test_preexisting_untracked_file_modified_is_flagged(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _snapshot(repo)
    (repo / "pre.txt").write_text("changed\n", encoding="utf-8")

    code, payload = _verify(repo)
    assert code == 1
    assert ("untracked-modified", "pre.txt") in _drift_paths(payload)


def test_tracked_file_deleted_is_flagged(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _snapshot(repo)
    (repo / "f.py").unlink()

    code, payload = _verify(repo)
    assert code == 1
    assert ("worktree", "f.py") in _drift_paths(payload)


def test_index_mutation_with_same_worktree_content_is_flagged(tmp_path: Path) -> None:
    """git add of a modified file (worktree content unchanged after) must still
    drift: the index now differs from HEAD even though nothing on disk changed
    relative to the moment `git add` ran."""
    repo = _repo(tmp_path)
    _snapshot(repo)
    (repo / "f.py").write_text("v2\n", encoding="utf-8")
    _git(repo, "add", "f.py")

    code, payload = _verify(repo)
    assert code == 1
    assert ("index", "f.py") in _drift_paths(payload)


def test_head_moved_is_flagged(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _snapshot(repo)
    (repo / "f.py").write_text("v2\n", encoding="utf-8")
    _git(repo, "add", "f.py")
    _git(repo, "commit", "-qm", "move head")

    code, payload = _verify(repo)
    assert code == 1
    assert ("head", None) in _drift_paths(payload)


def test_resnapshot_over_stale_snapshot_stays_clean(tmp_path: Path) -> None:
    """The documented flow re-snapshots before each reviewer; the prior round's
    snapshot file (untracked in repos that do not gitignore it) must not be
    reported as the tool's own drift."""
    repo = _repo(tmp_path)
    _snapshot(repo)
    _snapshot(repo)

    code, payload = _verify(repo)
    assert code == 0, payload
    assert payload["drift"] == []


def test_missing_snapshot_file_exits_two(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    result = run_script(
        SCRIPT,
        "verify",
        "--repo-root",
        str(repo),
        "--before",
        str(repo / "does-not-exist.json"),
    )
    assert result.returncode == 2, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is False


def test_corrupt_snapshot_file_exits_two(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _snapshot(repo)
    snap_file = repo / ".charness" / "reviewer-boundary" / "snapshot.json"
    snap_file.write_text("{not json", encoding="utf-8")

    result = run_script(SCRIPT, "verify", "--repo-root", str(repo))
    assert result.returncode == 2, result.stdout + result.stderr
    assert json.loads(result.stdout)["ok"] is False


def test_staged_rename_is_flagged_without_crash(tmp_path: Path) -> None:
    """Porcelain v2 rename entries carry a NUL-separated origPath under -z;
    parsing must stay sound and the rename must still drift."""
    repo = _repo(tmp_path)
    _snapshot(repo)
    _git(repo, "mv", "f.py", "g.py")

    code, payload = _verify(repo)
    assert code == 1
    kinds = {d["kind"] for d in payload["drift"]}
    assert "index" in kinds


def test_non_utf8_filename_does_not_crash_the_rail(tmp_path: Path) -> None:
    """A reviewer-created file with a non-UTF8 name must produce the clean
    drift JSON (exit 1), not a UnicodeDecodeError traceback."""
    repo = _repo(tmp_path)
    _snapshot(repo)
    raw = str(repo).encode() + b"/caf\xe9.txt"
    with open(raw, "wb") as handle:
        handle.write(b"x\n")

    result = run_script(SCRIPT, "verify", "--repo-root", str(repo))
    assert result.returncode == 1, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert any(d["kind"].startswith("untracked") for d in payload["drift"])
