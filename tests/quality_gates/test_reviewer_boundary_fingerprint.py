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


def _snapshot(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return run_script(SCRIPT, "snapshot", "--repo-root", str(repo), *args)


def _verify(repo: Path, *args: str) -> tuple[int, dict]:
    result = run_script(
        SCRIPT,
        "verify",
        "--repo-root",
        str(repo),
        "--before",
        str(repo / ".charness" / "reviewer-boundary" / "snapshot.json"),
        *args,
    )
    return result.returncode, json.loads(result.stdout)


def _verify_default(repo: Path, *args: str) -> tuple[int, dict]:
    result = run_script(SCRIPT, "verify", "--repo-root", str(repo), *args)
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
    assert payload["ok"] is True
    assert payload["verdict"] == "clean"
    assert payload["drift"] == []
    assert payload["parent_attributed_drift"] == []
    assert payload["window"]["id"] == json.loads(snap.stdout)["window"]["id"]


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

    result = run_script(
        SCRIPT,
        "verify",
        "--repo-root",
        str(repo),
        "--before",
        str(snap_file),
    )
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


def test_parent_declared_path_is_attributed_not_failed(tmp_path: Path) -> None:
    """The observed false alarm: the parent applied review findings before
    verifying, and the resulting `ok: false` was shaped exactly like a reviewer
    boundary violation. A declared parent path is reported, not failed."""
    repo = _repo(tmp_path)
    _snapshot(repo)
    (repo / "f.py").write_text("parent applied a fix\n", encoding="utf-8")

    code, payload = _verify(repo, "--parent-path", "f.py")
    assert code == 3, payload
    assert payload["ok"] is True
    assert payload["verdict"] == "parent-attributed"
    assert payload["drift"] == []
    assert ("worktree", "f.py") in _drift_paths({"drift": payload["parent_attributed_drift"]})
    assert payload["unmatched_parent_paths"] == []
    assert payload["parent_declared"]["paths"] == ["f.py"]


def test_undeclared_drift_still_fails_alongside_a_declared_path(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _snapshot(repo)
    (repo / "f.py").write_text("parent applied a fix\n", encoding="utf-8")
    (repo / "reviewer.txt").write_text("a reviewer wrote this\n", encoding="utf-8")

    code, payload = _verify(repo, "--parent-path", "f.py")
    assert code == 1
    assert payload["ok"] is False
    assert payload["verdict"] == "boundary-drift"
    assert ("untracked-added", "reviewer.txt") in _drift_paths(payload)
    assert ("worktree", "f.py") not in _drift_paths(payload)


def test_head_move_needs_its_own_declaration(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _snapshot(repo)
    (repo / "f.py").write_text("v2\n", encoding="utf-8")
    _git(repo, "add", "f.py")
    _git(repo, "commit", "-qm", "parent commit")

    code, payload = _verify(repo, "--parent-path", "f.py")
    assert code == 1, payload
    assert ("head", None) in _drift_paths(payload)

    code, payload = _verify(repo, "--parent-path", "f.py", "--parent-head-moved")
    assert code == 3, payload
    assert ("head", None) in _drift_paths({"drift": payload["parent_attributed_drift"]})


def test_index_drift_needs_its_own_declaration(tmp_path: Path) -> None:
    """A reviewer that stages a path the parent also edited is the #258 trap.
    One `--parent-path` must not excuse it: index drift is a separate class no
    read-only reviewer can legitimately produce."""
    repo = _repo(tmp_path)
    _snapshot(repo)
    (repo / "f.py").write_text("parent applied a fix\n", encoding="utf-8")
    _git(repo, "add", "f.py")

    code, payload = _verify(repo, "--parent-path", "f.py")
    assert code == 1, payload
    assert ("index", "f.py") in _drift_paths(payload)

    code, payload = _verify(repo, "--parent-path", "f.py", "--parent-staged", "f.py")
    assert code == 3, payload
    assert payload["drift"] == []


def test_declared_path_that_never_drifted_is_reported(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _snapshot(repo)

    code, payload = _verify(repo, "--parent-path", "untouched.py")
    assert code == 3, payload
    assert payload["unmatched_parent_paths"] == ["untouched.py"]


def test_already_dirty_file_edited_again_is_named(tmp_path: Path) -> None:
    """A file already modified at snapshot time keeps the same porcelain XY when
    it is edited again, so XY alone saw nothing. That is the normal mid-task
    parent tree, and without per-path content the second edit was invisible
    whenever any other path also drifted — attributable to nobody."""
    repo = _repo(tmp_path)
    (repo / "f.py").write_text("modified before the window\n", encoding="utf-8")
    _snapshot(repo)
    (repo / "f.py").write_text("a reviewer edited it again\n", encoding="utf-8")
    (repo / "parent.txt").write_text("parent work\n", encoding="utf-8")

    code, payload = _verify(repo, "--parent-path", "parent.txt")
    assert code == 1, payload
    assert ("worktree", "f.py") in _drift_paths(payload)


def test_mode_only_change_on_a_changed_path_is_caught(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "f.py").write_text("dirty\n", encoding="utf-8")
    _snapshot(repo)
    (repo / "f.py").chmod(0o755)

    code, payload = _verify(repo)
    assert code == 1, payload
    assert ("worktree", "f.py") in _drift_paths(payload)


def test_pathless_drift_is_never_parent_attributable(tmp_path: Path) -> None:
    """The aggregate patch backstop names no surface, so no declaration can
    match it."""
    repo = _repo(tmp_path)
    _snapshot(repo)
    snap_file = repo / ".charness" / "reviewer-boundary" / "snapshot.json"
    stored = json.loads(snap_file.read_text(encoding="utf-8"))
    stored["worktree_patch_sha256"] = "0" * 64
    snap_file.write_text(json.dumps(stored), encoding="utf-8")

    code, payload = _verify(repo, "--parent-path", "f.py")
    assert code == 1, payload
    assert ("worktree", None) in _drift_paths(payload)
    assert payload["parent_attributed_drift"] == []


def test_truncated_snapshot_refuses_as_json(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _snapshot(repo)
    snap_file = repo / ".charness" / "reviewer-boundary" / "snapshot.json"
    stored = json.loads(snap_file.read_text(encoding="utf-8"))
    stored.pop("status")
    snap_file.write_text(json.dumps(stored), encoding="utf-8")

    code, payload = _verify(repo)
    assert code == 2, payload
    assert payload["ok"] is False
    assert "missing keys" in payload["error"]


def test_verify_refuses_a_snapshot_from_another_window(tmp_path: Path) -> None:
    """A snapshot certifies one interval; answering across two is the drift
    report that cannot attribute drift in either direction."""
    repo = _repo(tmp_path)
    _snapshot(repo, "--window-id", "round-1")

    code, payload = _verify_default(repo, "--window-id", "round-2")
    assert code == 2, payload
    assert payload["ok"] is False
    assert "round-1" in payload["error"] and "round-2" in payload["error"]

    code, payload = _verify_default(repo, "--window-id", "round-1")
    assert code == 0, payload
    assert payload["window"]["id"] == "round-1"


def test_default_verify_requires_explicit_snapshot_identity(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _snapshot(repo, "--window-id", "round-1")

    code, payload = _verify_default(repo)
    assert code == 2, payload
    assert payload["ok"] is False
    assert "default snapshot" in payload["error"]
    assert "round-1" in payload["error"]
    assert "--window-id" in payload["error"]


def test_explicit_before_path_can_verify_without_window_id(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _snapshot(repo, "--window-id", "round-1")

    code, payload = _verify(repo)
    assert code == 0, payload
    assert payload["window"]["id"] == "round-1"


def test_legacy_snapshot_without_a_window_still_verifies(tmp_path: Path) -> None:
    """Snapshots written before the window binding must not become unreadable."""
    repo = _repo(tmp_path)
    _snapshot(repo)
    snap_file = repo / ".charness" / "reviewer-boundary" / "snapshot.json"
    legacy = json.loads(snap_file.read_text(encoding="utf-8"))
    legacy.pop("window")
    snap_file.write_text(json.dumps(legacy), encoding="utf-8")

    code, payload = _verify(repo)
    assert code == 0, payload
    assert payload["window"] == {}
    assert payload["content_comparison"] == "per-path"


def test_snapshot_without_per_path_content_says_so(tmp_path: Path) -> None:
    """A pre-per-path snapshot cannot see an edit to an already-dirty file; the
    verdict must name the weaker comparison instead of reading like the full one."""
    repo = _repo(tmp_path)
    _snapshot(repo)
    snap_file = repo / ".charness" / "reviewer-boundary" / "snapshot.json"
    legacy = json.loads(snap_file.read_text(encoding="utf-8"))
    legacy.pop("changed_content")
    snap_file.write_text(json.dumps(legacy), encoding="utf-8")

    code, payload = _verify(repo)
    assert code == 0, payload
    assert payload["content_comparison"] == "unavailable-legacy-snapshot"


def test_non_utf8_filename_does_not_crash_the_rail(tmp_path: Path) -> None:
    """A reviewer-created file with a non-UTF8 name must produce the clean
    drift JSON (exit 1), not a UnicodeDecodeError traceback."""
    repo = _repo(tmp_path)
    _snapshot(repo)
    raw = str(repo).encode() + b"/caf\xe9.txt"
    with open(raw, "wb") as handle:
        handle.write(b"x\n")

    result = run_script(
        SCRIPT,
        "verify",
        "--repo-root",
        str(repo),
        "--before",
        str(repo / ".charness" / "reviewer-boundary" / "snapshot.json"),
    )
    assert result.returncode == 1, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert any(d["kind"].startswith("untracked") for d in payload["drift"])
