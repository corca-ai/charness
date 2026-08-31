"""Tests for the #428 reviewer-boundary integrity fingerprint.

Three recorded shared-tree reviewer violations (staged+committed content, an
unauthorized child spawn, a no-write-brief doc edit) were not caught by prose
rules or the narrow #258 staged-reversion gate, because both trust the
reviewer's own report of what it touched. `reviewer_boundary_fingerprint.py`
instead snapshots the whole worktree+index state before a reviewer runs and
diffs it after, so drift is caught regardless of mutation shape.
"""
from __future__ import annotations

import copy
import io
import json
import subprocess
from contextlib import redirect_stdout
from pathlib import Path

import yaml

from .repo_shapes import replace_with_committed_repo
from .seeding_support import git
from .support import ROOT, _load_script_module, run_script

SCRIPT = "skills/shared/scripts/reviewer_boundary_fingerprint.py"
_FINGERPRINT = _load_script_module(
    "tests.quality_gates.reviewer_boundary_fingerprint_under_test",
    ROOT / SCRIPT,
)


def _repo(tmp_path: Path) -> Path:
    """A seeded repo with one tracked file and one pre-existing untracked file."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "f.py").write_text("v1\n", encoding="utf-8")
    replace_with_committed_repo(repo)
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
    return result.returncode, yaml.safe_load(result.stdout)


def _verify_default(repo: Path, *args: str) -> tuple[int, dict]:
    result = run_script(SCRIPT, "verify", "--repo-root", str(repo), *args)
    return result.returncode, yaml.safe_load(result.stdout)


def _drift_paths(payload: dict) -> set[tuple[str, str | None]]:
    return {(d["kind"], d["path"]) for d in payload["drift"]}


def _status(path: str, xy: str) -> str:
    """A porcelain-v2 change entry for pure comparison tests.

    The Git parser is exercised by the small real-repository representatives;
    the matrix below only needs the state contract consumed by comparison.
    """
    return (
        f"1 {xy} N... 100644 100644 100644 {'0' * 40} {'0' * 40} {path}"
    )


def _state(
    *,
    head: str = "head",
    statuses: tuple[str, ...] = (),
    untracked: dict[str, str] | None = None,
    changed_content: dict[str, str] | None = None,
    staged_patch: str = "staged",
    worktree_patch: str = "worktree",
    window_id: str = "round-1",
) -> dict:
    return {
        "window": {"id": window_id},
        "head": head,
        "status": list(statuses),
        "staged_patch_sha256": staged_patch,
        "worktree_patch_sha256": worktree_patch,
        "changed_content": changed_content or {},
        "untracked": untracked or {},
    }


def _compare(
    before: dict,
    after: dict,
    *,
    parent_paths: tuple[str, ...] = (),
    parent_staged: tuple[str, ...] = (),
    parent_head_moved: bool = False,
) -> tuple[list[dict], list[dict]]:
    drift = _FINGERPRINT.compare_snapshots(before, after)
    return _FINGERPRINT.split_parent_attributed(
        drift,
        list(parent_paths),
        parent_head_moved,
        list(parent_staged),
    )


def _invoke(*args: str, build_state: dict | None = None) -> tuple[int, dict]:
    """Run the CLI in-process, optionally against one immutable state payload."""
    previous = _FINGERPRINT.build_snapshot
    if build_state is not None:
        _FINGERPRINT.build_snapshot = lambda *unused, **kwargs: copy.deepcopy(build_state)
    output = io.StringIO()
    try:
        with redirect_stdout(output):
            code = _FINGERPRINT.main(list(args))
    finally:
        _FINGERPRINT.build_snapshot = previous
    return code, yaml.safe_load(output.getvalue())


def _pure_snapshot(tmp_path: Path, state: dict, *args: str) -> tuple[Path, dict]:
    path = tmp_path / "snapshot.json"
    code, payload = _invoke(
        "snapshot",
        "--repo-root",
        str(tmp_path),
        "--out",
        str(path),
        *args,
        build_state=state,
    )
    assert code == 0, payload
    return path, payload


def _pure_verify(repo: Path, before: Path, after: dict, *args: str) -> tuple[int, dict]:
    return _invoke(
        "verify",
        "--repo-root",
        str(repo),
        "--before",
        str(before),
        *args,
        build_state=after,
    )


def test_file_backed_round_runtime_outputs_are_gitignored() -> None:
    """Worker receipts/results are evidence inputs, not parent worktree edits."""
    result = subprocess.run(
        [
            "git",
            "check-ignore",
            "--no-index",
            "--verbose",
            "--",
            ".charness/reviewer-round-2/example/result.json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert ".charness/reviewer-round-2/" in result.stdout


def test_clean_verify_is_ok(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    snap = _snapshot(repo)
    assert snap.returncode == 0, snap.stdout + snap.stderr
    snapshot_payload = yaml.safe_load(snap.stdout)
    assert snapshot_payload["ok"] is True
    assert snapshot_payload["verify_before"] == snapshot_payload["out"]
    assert snapshot_payload["verify_args"] == [
        "verify",
        "--repo-root",
        str(repo),
        "--before",
        snapshot_payload["out"],
        "--window-id",
        snapshot_payload["window"]["id"],
    ]

    code, payload = _verify(repo)
    assert code == 0, payload
    assert payload["ok"] is True
    assert payload["verdict"] == "clean"
    assert payload["drift"] == []
    assert payload["parent_attributed_drift"] == []
    assert payload["window"]["id"] == yaml.safe_load(snap.stdout)["window"]["id"]


def test_custom_snapshot_receipt_exposes_the_verify_before_handoff(tmp_path: Path) -> None:
    custom = tmp_path / "review-window.json"
    code, payload = _invoke(
        "snapshot",
        "--repo-root",
        str(tmp_path),
        "--window-id",
        "custom-window",
        "--out",
        str(custom),
        build_state=_state(window_id="custom-window"),
    )

    assert code == 0, payload
    assert payload["out"] == str(custom)
    assert payload["verify_before"] == str(custom)
    assert payload["verify_args"][-4:] == [
        "--before",
        str(custom),
        "--window-id",
        "custom-window",
    ]


def test_tracked_file_modified_is_flagged(tmp_path: Path) -> None:
    before = _state()
    after = _state(statuses=(_status("f.py", ".M"),))
    undeclared, attributed = _compare(before, after)
    assert ("worktree", "f.py") in {(d["kind"], d["path"]) for d in undeclared}
    assert attributed == []


def test_new_untracked_file_is_flagged(tmp_path: Path) -> None:
    before = _state()
    after = _state(untracked={"new.txt": "new"})
    undeclared, _ = _compare(before, after)
    assert ("untracked-added", "new.txt") in {
        (d["kind"], d["path"]) for d in undeclared
    }


def test_preexisting_untracked_file_modified_is_flagged(tmp_path: Path) -> None:
    before = _state(untracked={"pre.txt": "before"})
    after = _state(untracked={"pre.txt": "after"})
    undeclared, _ = _compare(before, after)
    assert ("untracked-modified", "pre.txt") in {
        (d["kind"], d["path"]) for d in undeclared
    }


def test_tracked_file_deleted_is_flagged(tmp_path: Path) -> None:
    before = _state(statuses=(_status("f.py", ".M"),))
    after = _state(statuses=(_status("f.py", "D."),))
    undeclared, _ = _compare(before, after)
    assert ("worktree", "f.py") in {
        (d["kind"], d["path"]) for d in undeclared
    }


def test_index_mutation_with_same_worktree_content_is_flagged(tmp_path: Path) -> None:
    """git add of a modified file (worktree content unchanged after) must still
    drift: the index now differs from HEAD even though nothing on disk changed
    relative to the moment `git add` ran."""
    before = _state(statuses=(_status("f.py", ".M"),))
    after = _state(statuses=(_status("f.py", "M."),))
    undeclared, _ = _compare(before, after)
    assert ("index", "f.py") in {
        (d["kind"], d["path"]) for d in undeclared
    }


def test_head_moved_is_flagged(tmp_path: Path) -> None:
    before = _state(head="head-1")
    after = _state(head="head-2")
    undeclared, _ = _compare(before, after)
    assert ("head", None) in {(d["kind"], d["path"]) for d in undeclared}


def test_resnapshot_over_stale_snapshot_stays_clean(tmp_path: Path) -> None:
    """The documented flow re-snapshots before each reviewer; the prior round's
    snapshot file (untracked in repos that do not gitignore it) must not be
    reported as the tool's own drift."""
    state = _state()
    before, _ = _pure_snapshot(tmp_path, state)
    _pure_snapshot(tmp_path, state)
    code, payload = _pure_verify(tmp_path, before, state)
    assert code == 0, payload
    assert payload["drift"] == []


def test_missing_snapshot_file_exits_two(tmp_path: Path) -> None:
    code, payload = _invoke(
        "verify",
        "--repo-root",
        str(tmp_path),
        "--before",
        str(tmp_path / "does-not-exist.json"),
    )
    assert code == 2, payload
    assert payload["ok"] is False


def test_corrupt_snapshot_file_exits_two(tmp_path: Path) -> None:
    snap_file = tmp_path / "snapshot.json"
    snap_file.write_text("{not json", encoding="utf-8")
    code, payload = _invoke(
        "verify",
        "--repo-root",
        str(tmp_path),
        "--before",
        str(snap_file),
    )
    assert code == 2, payload
    assert payload["ok"] is False


def test_staged_rename_is_flagged_without_crash(tmp_path: Path) -> None:
    """Porcelain v2 rename entries carry a NUL-separated origPath under -z;
    parsing must stay sound and the rename must still drift."""
    repo = _repo(tmp_path)
    _snapshot(repo)
    git(repo, "mv", "f.py", "g.py")

    code, payload = _verify(repo)
    assert code == 1
    kinds = {d["kind"] for d in payload["drift"]}
    assert "index" in kinds


def test_parent_declared_path_is_attributed_not_failed(tmp_path: Path) -> None:
    """The observed false alarm: the parent applied review findings before
    verifying, and the resulting `ok: false` was shaped exactly like a reviewer
    boundary violation. A declared parent path is reported, not failed."""
    before, _ = _pure_snapshot(tmp_path, _state())
    after = _state(statuses=(_status("f.py", ".M"),))
    code, payload = _pure_verify(tmp_path, before, after, "--parent-path", "f.py")
    assert code == 3, payload
    assert payload["ok"] is True
    assert payload["verdict"] == "parent-attributed"
    assert payload["drift"] == []
    assert ("worktree", "f.py") in _drift_paths(
        {"drift": payload["parent_attributed_drift"]}
    )
    assert payload["unmatched_parent_paths"] == []
    assert payload["parent_declared"]["paths"] == ["f.py"]


def test_undeclared_drift_still_fails_alongside_a_declared_path(tmp_path: Path) -> None:
    before, _ = _pure_snapshot(tmp_path, _state())
    after = _state(
        statuses=(_status("f.py", ".M"),),
        untracked={"reviewer.txt": "reviewer"},
    )
    code, payload = _pure_verify(tmp_path, before, after, "--parent-path", "f.py")
    assert code == 1
    assert payload["ok"] is False
    assert payload["verdict"] == "boundary-drift"
    assert ("untracked-added", "reviewer.txt") in _drift_paths(payload)
    assert ("worktree", "f.py") not in _drift_paths(payload)


def test_head_move_needs_its_own_declaration(tmp_path: Path) -> None:
    before, _ = _pure_snapshot(tmp_path, _state())
    after = _state(head="head-2")
    code, payload = _pure_verify(tmp_path, before, after, "--parent-path", "f.py")
    assert code == 1, payload
    assert ("head", None) in _drift_paths(payload)

    code, payload = _pure_verify(
        tmp_path,
        before,
        after,
        "--parent-path",
        "f.py",
        "--parent-head-moved",
    )
    assert code == 3, payload
    assert ("head", None) in _drift_paths({"drift": payload["parent_attributed_drift"]})


def test_index_drift_needs_its_own_declaration(tmp_path: Path) -> None:
    """A reviewer that stages a path the parent also edited is the #258 trap.
    One `--parent-path` must not excuse it: index drift is a separate class no
    read-only reviewer can legitimately produce."""
    before, _ = _pure_snapshot(tmp_path, _state())
    after = _state(statuses=(_status("f.py", "M."),))
    code, payload = _pure_verify(tmp_path, before, after, "--parent-path", "f.py")
    assert code == 1, payload
    assert ("index", "f.py") in _drift_paths(payload)

    code, payload = _pure_verify(
        tmp_path,
        before,
        after,
        "--parent-path",
        "f.py",
        "--parent-staged",
        "f.py",
    )
    assert code == 3, payload
    assert payload["drift"] == []


def test_declared_path_that_never_drifted_is_reported(tmp_path: Path) -> None:
    before, _ = _pure_snapshot(tmp_path, _state())
    code, payload = _pure_verify(
        tmp_path,
        before,
        _state(),
        "--parent-path",
        "untouched.py",
    )
    assert code == 3, payload
    assert payload["unmatched_parent_paths"] == ["untouched.py"]


def test_already_dirty_file_edited_again_is_named(tmp_path: Path) -> None:
    """A file already modified at snapshot time keeps the same porcelain XY when
    it is edited again, so XY alone saw nothing. That is the normal mid-task
    parent tree, and without per-path content the second edit was invisible
    whenever any other path also drifted — attributable to nobody."""
    before, _ = _pure_snapshot(
        tmp_path,
        _state(
            statuses=(_status("f.py", ".M"),),
            changed_content={"f.py": "before"},
        ),
    )
    after = _state(
        statuses=(_status("f.py", ".M"),),
        changed_content={"f.py": "reviewer"},
        untracked={"parent.txt": "parent"},
    )
    code, payload = _pure_verify(
        tmp_path,
        before,
        after,
        "--parent-path",
        "parent.txt",
    )
    assert code == 1, payload
    assert ("worktree", "f.py") in _drift_paths(payload)


def test_mode_only_change_on_a_changed_path_is_caught(tmp_path: Path) -> None:
    before = _state(
        statuses=(_status("f.py", ".M"),),
        changed_content={"f.py": "-:same"},
    )
    after = _state(
        statuses=(_status("f.py", ".M"),),
        changed_content={"f.py": "x:same"},
    )
    undeclared, _ = _compare(before, after)
    assert ("worktree", "f.py") in {
        (d["kind"], d["path"]) for d in undeclared
    }


def test_pathless_drift_is_never_parent_attributable(tmp_path: Path) -> None:
    """The aggregate patch backstop names no surface, so no declaration can
    match it."""
    before = _state()
    after = _state(worktree_patch="changed")
    undeclared, attributed = _compare(before, after, parent_paths=("f.py",))
    assert ("worktree", None) in {
        (d["kind"], d["path"]) for d in undeclared
    }
    assert attributed == []


def test_truncated_snapshot_refuses_as_yaml(tmp_path: Path) -> None:
    snap_file, _ = _pure_snapshot(tmp_path, _state())
    stored = json.loads(snap_file.read_text(encoding="utf-8"))
    stored.pop("status")
    snap_file.write_text(json.dumps(stored), encoding="utf-8")

    code, payload = _pure_verify(tmp_path, snap_file, _state())
    assert code == 2, payload
    assert payload["ok"] is False
    assert "missing keys" in payload["error"]


def test_verify_refuses_a_snapshot_from_another_window(tmp_path: Path) -> None:
    """A snapshot certifies one interval; answering across two is the drift
    report that cannot attribute drift in either direction."""
    state = _state(window_id="round-1")
    _invoke(
        "snapshot",
        "--repo-root",
        str(tmp_path),
        "--window-id",
        "round-1",
        build_state=state,
    )

    code, payload = _invoke(
        "verify",
        "--repo-root",
        str(tmp_path),
        "--window-id",
        "round-2",
    )
    assert code == 2, payload
    assert payload["ok"] is False
    assert "round-1" in payload["error"] and "round-2" in payload["error"]

    code, payload = _invoke(
        "verify",
        "--repo-root",
        str(tmp_path),
        "--window-id",
        "round-1",
        build_state=state,
    )
    assert code == 0, payload
    assert payload["window"]["id"] == "round-1"


def test_default_verify_requires_explicit_snapshot_identity(tmp_path: Path) -> None:
    _invoke(
        "snapshot",
        "--repo-root",
        str(tmp_path),
        "--window-id",
        "round-1",
        build_state=_state(window_id="round-1"),
    )
    code, payload = _invoke("verify", "--repo-root", str(tmp_path))
    assert code == 2, payload
    assert payload["ok"] is False
    assert "default snapshot" in payload["error"]
    assert "round-1" in payload["error"]
    assert "--window-id" in payload["error"]


def test_explicit_before_path_can_verify_without_window_id(tmp_path: Path) -> None:
    before, _ = _pure_snapshot(tmp_path, _state(window_id="round-1"), "--window-id", "round-1")
    code, payload = _pure_verify(tmp_path, before, _state(window_id="round-1"))
    assert code == 0, payload
    assert payload["window"]["id"] == "round-1"


def test_legacy_snapshot_without_a_window_still_verifies(tmp_path: Path) -> None:
    """Snapshots written before the window binding must not become unreadable."""
    snap_file, _ = _pure_snapshot(tmp_path, _state())
    legacy = json.loads(snap_file.read_text(encoding="utf-8"))
    legacy.pop("window")
    snap_file.write_text(json.dumps(legacy), encoding="utf-8")

    code, payload = _pure_verify(tmp_path, snap_file, _state())
    assert code == 0, payload
    assert payload["window"] == {}
    assert payload["content_comparison"] == "per-path"


def test_snapshot_without_per_path_content_says_so(tmp_path: Path) -> None:
    """A pre-per-path snapshot cannot see an edit to an already-dirty file; the
    verdict must name the weaker comparison instead of reading like the full one."""
    snap_file, _ = _pure_snapshot(tmp_path, _state())
    legacy = json.loads(snap_file.read_text(encoding="utf-8"))
    legacy.pop("changed_content")
    snap_file.write_text(json.dumps(legacy), encoding="utf-8")

    code, payload = _pure_verify(tmp_path, snap_file, _state())
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
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert any(d["kind"].startswith("untracked") for d in payload["drift"])
