from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

from scripts import worktree_audit_lib as lib


def _git(*args: str, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


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


def test_parse_porcelain_extracts_attributes() -> None:
    text = (
        "worktree /a/primary\n"
        "HEAD abc123\n"
        "branch refs/heads/main\n"
        "\n"
        "worktree /a/feature\n"
        "HEAD def456\n"
        "detached\n"
        "\n"
        "worktree /a/missing\n"
        "HEAD 000000\n"
        "detached\n"
        "prunable gitdir file points to non-existent location\n"
    )
    entries = lib.parse_porcelain(text)
    assert len(entries) == 3
    assert entries[0]["worktree"] == "/a/primary"
    assert entries[0]["branch"] == "refs/heads/main"
    assert entries[1]["detached"] is True
    assert entries[2]["prunable"] is True
    assert "non-existent location" in entries[2]["prunable_reason"]


def test_audit_reports_only_primary_for_clean_repo(tmp_path: Path) -> None:
    repo = _make_primary(tmp_path)
    payload = lib.run_audit(repo)
    assert payload["status"] == lib.PASS
    assert payload["summary"]["primary"] == 1
    assert payload["summary"]["total"] == 1
    assert payload["next_action"] is None


def test_audit_classifies_active_and_prunable(tmp_path: Path) -> None:
    repo = _make_primary(tmp_path)

    active_path = tmp_path / "feature"
    _git("worktree", "add", "-b", "feature", str(active_path), cwd=repo)

    missing_path = tmp_path / "missing"
    _git("worktree", "add", "--detach", str(missing_path), cwd=repo)
    # Simulate the bench/eval pattern: directory removed without `git worktree remove`.
    import shutil

    shutil.rmtree(missing_path)

    payload = lib.run_audit(repo)
    assert payload["status"] == lib.WARN
    assert payload["summary"]["primary"] == 1
    assert payload["summary"]["active"] == 1
    assert payload["summary"]["prunable"] == 1
    assert payload["next_action"] is not None
    assert "audit --prune" in payload["next_action"]

    classifications = {Path(e["path"]).name: e["classification"] for e in payload["entries"]}
    assert classifications["primary"] == lib.CLASSIFICATION_PRIMARY
    assert classifications["feature"] == lib.CLASSIFICATION_ACTIVE
    assert classifications["missing"] == lib.CLASSIFICATION_PRUNABLE


def test_audit_doctor_surfaces_active_unprepared_worktree(tmp_path: Path, monkeypatch) -> None:
    repo = _make_primary(tmp_path)
    active_path = tmp_path / "feature"
    _git("worktree", "add", "-b", "feature", str(active_path), cwd=repo)

    hooks_dir = repo / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    shim = hooks_dir / "pre-commit"
    shim.write_text("#!/bin/sh\nexec lefthook run pre-commit\n", encoding="utf-8")
    shim.chmod(0o755)
    binary_dir = repo / "node_modules" / "lefthook-linux-x64" / "bin"
    binary_dir.mkdir(parents=True)
    binary = binary_dir / "lefthook"
    binary.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    binary.chmod(0o755)
    monkeypatch.setenv(
        "PATH",
        str(Path(sys.executable).resolve().parent) + os.pathsep + "/usr/bin" + os.pathsep + "/bin",
    )

    payload = lib.run_audit(repo, include_doctor=True)

    assert payload["status"] == lib.WARN
    assert payload["doctor_summary"] == {"pass": 1, "fail": 1, "skipped": 0}
    active = next(entry for entry in payload["entries"] if Path(entry["path"]) == active_path)
    assert active["classification"] == lib.CLASSIFICATION_ACTIVE
    assert active["doctor"]["status"] == lib.FAIL
    assert active["doctor"]["failed_checks"][0]["id"] == "lefthook_shim"
    assert "worktree prepare --repo-root <path>" in payload["next_action"]


def test_audit_text_shows_primary_readiness_failure(tmp_path: Path, monkeypatch) -> None:
    repo = _make_primary(tmp_path)
    hooks_dir = repo / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    shim = hooks_dir / "pre-commit"
    shim.write_text("#!/bin/sh\nexec lefthook run pre-commit\n", encoding="utf-8")
    shim.chmod(0o755)
    monkeypatch.setenv(
        "PATH",
        str(Path(sys.executable).resolve().parent) + os.pathsep + "/usr/bin" + os.pathsep + "/bin",
    )

    payload = lib.run_audit(repo, include_doctor=True)
    rendered = lib.render_audit_text(payload)

    assert payload["doctor_summary"]["fail"] == 1
    assert f"[{lib.CLASSIFICATION_PRIMARY}] {repo.resolve()}" in rendered
    assert "readiness=fail" in rendered


def test_audit_classifies_stale_detached_head(tmp_path: Path) -> None:
    repo = _make_primary(tmp_path)
    stale_path = tmp_path / "stale"
    _git("worktree", "add", "--detach", str(stale_path), cwd=repo)

    old_time = time.time() - (30 * 86400)
    os.utime(stale_path, (old_time, old_time))

    payload = lib.run_audit(repo, stale_days=14)
    stale_entries = [e for e in payload["entries"] if e["classification"] == lib.CLASSIFICATION_STALE]
    assert len(stale_entries) == 1
    assert stale_entries[0]["age_days"] >= 14
    assert payload["status"] == lib.WARN


def test_audit_marks_locked_detached_as_active_not_stale(tmp_path: Path) -> None:
    repo = _make_primary(tmp_path)
    locked_path = tmp_path / "locked"
    _git("worktree", "add", "--detach", str(locked_path), cwd=repo)
    _git("worktree", "lock", "--reason", "pinned for release", str(locked_path), cwd=repo)

    old_time = time.time() - (60 * 86400)
    os.utime(locked_path, (old_time, old_time))

    payload = lib.run_audit(repo, stale_days=14)
    classifications = {Path(e["path"]).name: e["classification"] for e in payload["entries"]}
    assert classifications["locked"] == lib.CLASSIFICATION_ACTIVE, payload
    assert payload["summary"]["stale"] == 0


def test_audit_primary_resolution_works_from_linked_worktree(tmp_path: Path) -> None:
    repo = _make_primary(tmp_path)
    feature_path = tmp_path / "feature"
    _git("worktree", "add", "-b", "feature", str(feature_path), cwd=repo)

    payload = lib.run_audit(feature_path)
    assert Path(payload["primary_worktree"]) == repo.resolve()
    classifications = {Path(e["path"]).name: e["classification"] for e in payload["entries"]}
    assert classifications["primary"] == lib.CLASSIFICATION_PRIMARY
    assert classifications["feature"] == lib.CLASSIFICATION_ACTIVE


def test_prune_count_uses_audit_diff_not_regex(tmp_path: Path) -> None:
    repo = _make_primary(tmp_path)
    a_path = tmp_path / "ghost-a"
    b_path = tmp_path / "ghost-b"
    _git("worktree", "add", "--detach", str(a_path), cwd=repo)
    _git("worktree", "add", "--detach", str(b_path), cwd=repo)
    import shutil

    shutil.rmtree(a_path)
    shutil.rmtree(b_path)

    prune_payload = lib.run_prune(repo)
    assert prune_payload["pruned_count"] == 2
    assert prune_payload["remaining_after_prune"]["prunable"] == 0


def test_audit_stale_threshold_respected(tmp_path: Path) -> None:
    repo = _make_primary(tmp_path)
    fresh_path = tmp_path / "fresh"
    _git("worktree", "add", "--detach", str(fresh_path), cwd=repo)
    # Just-created detached worktree is active, not stale, with default 14-day threshold.

    payload = lib.run_audit(repo, stale_days=14)
    assert payload["summary"]["stale"] == 0
    assert payload["summary"]["active"] == 1


def test_prune_drops_metadata_for_missing_worktrees(tmp_path: Path) -> None:
    repo = _make_primary(tmp_path)
    missing_path = tmp_path / "missing"
    _git("worktree", "add", "--detach", str(missing_path), cwd=repo)
    import shutil

    shutil.rmtree(missing_path)

    audit_before = lib.run_audit(repo)
    assert audit_before["summary"]["prunable"] == 1

    prune_payload = lib.run_prune(repo)
    assert prune_payload["status"] == lib.PASS
    assert prune_payload["pruned_count"] == 1

    audit_after = lib.run_audit(repo)
    assert audit_after["summary"]["prunable"] == 0
    assert audit_after["status"] == lib.PASS


def test_audit_emits_json_when_requested(tmp_path: Path) -> None:
    import io
    import json

    repo = _make_primary(tmp_path)
    payload = lib.run_audit(repo)

    buf = io.StringIO()
    sys_stdout = sys.stdout
    try:
        sys.stdout = buf
        lib.emit_payload(payload, json_mode=True, renderer=lib.render_audit_text)
    finally:
        sys.stdout = sys_stdout

    decoded = json.loads(buf.getvalue())
    assert decoded["repo_root"] == str(repo.resolve())
    assert decoded["summary"]["primary"] == 1
