from __future__ import annotations

import json
import stat
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from .release_publish_fixtures import (
    PUBLISH_CLI,
    REPO_ROOT,
    _release_env,
    _run_publish_patch,
    _seed_publish_release_repo,
)
from .seeding_support import load_module

ROLLBACK_PATH = (
    REPO_ROOT / "skills" / "public" / "release" / "scripts" / "publish_release_rollback.py"
)


def _load_rollback():
    return load_module("publish_release_rollback_under_test", ROLLBACK_PATH)


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _failure_payload(stderr: str) -> dict:
    start = "BEGIN publish_release_failure_payload"
    end = "END publish_release_failure_payload"
    assert start in stderr and end in stderr, stderr
    return yaml.safe_load(stderr.split(start, 1)[1].split(end, 1)[0].strip())


def test_precommit_quality_failure_restores_clean_retryable_worktree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_print_failure_payload = PUBLISH_CLI._release_runtime.print_failure_payload

    def print_failure_payload(*args, **kwargs):
        kwargs["stream"] = sys.stderr
        return original_print_failure_payload(*args, **kwargs)

    monkeypatch.setattr(
        PUBLISH_CLI._release_runtime, "print_failure_payload", print_failure_payload
    )
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    quality_script = repo / "scripts" / "run-quality.sh"
    quality_script.write_text(
        "#!/usr/bin/env bash\nset -euo pipefail\ngit mv README.md RENAMED.md\n"
        "echo 'prepared quality failed' >&2\nexit 1\n",
        encoding="utf-8",
    )
    quality_script.chmod(0o755)
    _git(repo, "add", "scripts/run-quality.sh")
    _git(repo, "commit", "-m", "make release quality fail")

    head_before = _git(repo, "rev-parse", "HEAD")
    manifest = repo / "packaging" / "demo.json"
    manifest_before = manifest.read_bytes()

    result = _run_publish_patch(repo, _release_env(tmp_path, bin_dir))

    assert result.returncode != 0
    assert _git(repo, "rev-parse", "HEAD") == head_before
    assert _git(repo, "status", "--short") == ""
    assert manifest.read_bytes() == manifest_before
    assert (repo / "README.md").is_file()
    assert not (repo / "RENAMED.md").exists()
    assert _git(repo, "tag", "--list", "v0.0.1") == ""

    failure = _failure_payload(result.stderr)
    rollback = failure["precommit_rollback"]
    assert rollback["status"] == "restored"
    assert "packaging/demo.json" in rollback["restored_paths"]
    assert "charness-artifacts/release/latest.md" in rollback["quarantined_paths"]
    assert "RENAMED.md" in rollback["quarantined_paths"]
    quarantine = Path(rollback["quarantine_root"])
    assert (quarantine / "charness-artifacts" / "release" / "latest.md").is_file()
    record = failure["release_failure_record"]
    assert record["status"] == "persisted"
    record_path = Path(record["path"])
    record_payload = yaml.safe_load(record_path.read_text(encoding="utf-8"))
    assert (
        record_payload["release_failure"]["detail"]
        == "raw exception text omitted from durable local state"
    )
    assert "error" not in record_payload["release_failure"]
    assert stat.S_IMODE(record_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(record_path.parent.stat().st_mode) == 0o700
    assert "prepared quality failed" not in failure["release_failure"]["error"]

    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    assert not any(entry[:1] == ["push"] for entry in git_log)
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    assert not any(entry[:2] == ["release", "create"] for entry in gh_log)


def test_git_add_failure_before_release_commit_rolls_back(tmp_path: Path) -> None:
    rollback = _load_rollback()
    repo, _remote, _bin_dir = _seed_publish_release_repo(tmp_path)
    manifest = repo / "packaging" / "demo.json"
    manifest.write_text('{"version": "0.0.1"}\n', encoding="utf-8")
    artifact = repo / "charness-artifacts" / "release" / "latest.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("prepared release artifact\n", encoding="utf-8")
    head_before = _git(repo, "rev-parse", "HEAD")

    result = rollback.rollback_precommit_changes(
        repo,
        {"head_sha": head_before},
        tag_name="v0.0.1",
        run_command=lambda args, *, cwd, check=True: subprocess.run(
            args, cwd=cwd, check=check, capture_output=True, text=True
        ),
    )

    assert result["status"] == "restored"
    assert _git(repo, "rev-parse", "HEAD") == head_before
    assert _git(repo, "status", "--short") == ""
    assert result["restored_paths"] == ["packaging/demo.json"]
    assert result["quarantined_paths"] == ["charness-artifacts/release/latest.md"]


def test_restore_failure_does_not_claim_planned_paths_were_restored(tmp_path: Path) -> None:
    rollback = _load_rollback()
    repo, _remote, _bin_dir = _seed_publish_release_repo(tmp_path)
    manifest = repo / "packaging" / "demo.json"
    manifest.write_text('{"version": "0.0.1"}\n', encoding="utf-8")
    head_before = _git(repo, "rev-parse", "HEAD")

    def fail_restore(args, *, cwd, check=True):
        if args[:3] == ["git", "restore", "--source"]:
            raise RuntimeError("injected restore failure")
        return subprocess.run(args, cwd=cwd, check=check, capture_output=True, text=True)

    result = rollback.rollback_precommit_changes(
        repo, {"head_sha": head_before}, tag_name="v0.0.1", run_command=fail_restore
    )

    assert result["status"] == "failed"
    assert result["restored_paths"] == []
    assert result["remaining_status"]


def test_quarantine_reports_completed_moves_before_a_later_failure(
    tmp_path: Path,
    monkeypatch,
) -> None:
    rollback = _load_rollback()
    repo = tmp_path / "repo"
    quarantine_base = tmp_path / "git-data"
    repo.mkdir()
    (repo / "first.txt").write_text("first", encoding="utf-8")
    (repo / "second.txt").write_text("second", encoding="utf-8")
    real_move = rollback.shutil.move
    calls = 0

    def fail_second_move(source: str, target: str):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected second move failure")
        return real_move(source, target)

    monkeypatch.setattr(rollback.shutil, "move", fail_second_move)

    root, moved, errors = rollback._quarantine_new_paths(
        repo,
        ["first.txt", "second.txt"],
        quarantine_base=quarantine_base,
        tag_name="v1.2.3",
    )

    assert root is not None
    assert moved == ["first.txt"]
    assert errors and errors[0].startswith("second.txt: OSError:")
    assert (Path(root) / "first.txt").is_file()
    assert (repo / "second.txt").is_file()


def test_quarantine_noops_when_no_candidate_exists(tmp_path: Path) -> None:
    rollback = _load_rollback()
    repo = tmp_path / "repo"
    repo.mkdir()

    result = rollback._quarantine_new_paths(
        repo,
        ["missing.txt"],
        quarantine_base=tmp_path / "git-data",
        tag_name="v1.2.3",
    )

    assert result == (None, [], [])


def test_rollback_refuses_after_head_moves(tmp_path: Path) -> None:
    rollback = _load_rollback()

    def run_command(args, *, cwd, check=True):
        assert cwd == tmp_path
        assert check is True
        assert args == ["git", "rev-parse", "HEAD"]
        return subprocess.CompletedProcess(args, 0, stdout="moved-head\n")

    result = rollback.rollback_precommit_changes(
        tmp_path,
        {"head_sha": "starting-head"},
        tag_name="v1.2.3",
        run_command=run_command,
    )

    assert result == {
        "status": "refused_head_changed",
        "expected_head": "starting-head",
        "current_head": "moved-head",
        "reason": "HEAD moved; preserve the partial state for the resume contract",
    }


def test_snapshot_refuses_dirty_input_and_rejects_escaping_paths(tmp_path: Path) -> None:
    rollback = _load_rollback()
    responses = iter(
        [
            subprocess.CompletedProcess([], 0, stdout="abc123\n"),
            subprocess.CompletedProcess([], 0, stdout=" M dirty.txt\n"),
        ]
    )

    def run_command(_args, *, cwd):
        assert cwd == tmp_path
        return next(responses)

    try:
        rollback.snapshot_clean_head(tmp_path, run_command=run_command)
    except SystemExit as exc:
        assert "clean worktree" in str(exc)
    else:
        raise AssertionError("dirty rollback snapshot must be refused")

    try:
        rollback._safe_repo_path(tmp_path, "../outside.txt")
    except ValueError as exc:
        assert "unsafe rollback path" in str(exc)
    else:
        raise AssertionError("escaping rollback path must be refused")


def test_rollback_failure_reports_when_status_is_also_unavailable(tmp_path: Path) -> None:
    rollback = _load_rollback()

    def run_command(args, *, cwd, check=True):
        assert cwd == tmp_path
        if args == ["git", "rev-parse", "HEAD"]:
            raise RuntimeError("injected rollback failure")
        if args == ["git", "status", "--short"] and check is False:
            raise RuntimeError("injected status failure")
        raise AssertionError(args)

    result = rollback.rollback_precommit_changes(
        tmp_path,
        {"head_sha": "abc123"},
        tag_name="v1.2.3",
        run_command=run_command,
    )

    assert result["status"] == "failed"
    assert result["remaining_status"] == ["status unavailable after rollback failure"]
