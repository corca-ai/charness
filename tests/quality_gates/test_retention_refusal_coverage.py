from __future__ import annotations

import os
import runpy
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from scripts import manage_mutation_reports as reports
from scripts.gates_support import run_standing_pytest as runner
from scripts.gates_support import standing_pytest_basetemp as basetemp_lib

ROOT = Path(__file__).resolve().parents[2]


def _old_file(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("old", encoding="utf-8")
    stamp = time.time() - 60 * 86400
    os.utime(path, (stamp, stamp))
    return path


def test_managed_paths_refuses_an_invalid_quality_adapter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        reports,
        "load_quality_adapter_strict",
        lambda _repo_root: {"valid": False, "errors": ["broken", "missing"]},
    )
    with pytest.raises(SystemExit, match="broken; missing"):
        reports.managed_paths(tmp_path)


def test_inventory_refuses_symlink_and_non_directory_report_roots(tmp_path: Path) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    target = tmp_path / "outside"
    target.mkdir()
    report_root = reports_dir / "mutation"
    report_root.symlink_to(target, target_is_directory=True)
    with pytest.raises(SystemExit, match="must not be a symlink"):
        reports.inventory(tmp_path, older_than_days=30)

    report_root.unlink()
    report_root.write_text("not a directory", encoding="utf-8")
    with pytest.raises(SystemExit, match="must be a directory"):
        reports.inventory(tmp_path, older_than_days=30)


def test_inventory_skips_an_entry_that_disappears_during_lstat(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    candidate = _old_file(tmp_path / "reports/mutation/old.json")
    monkeypatch.setattr(reports, "managed_paths", lambda _repo_root: set())
    original = Path.lstat

    def disappearing(path: Path):
        if path == candidate:
            raise OSError("gone")
        return original(path)

    monkeypatch.setattr(Path, "lstat", disappearing)
    payload = reports.inventory(tmp_path, older_than_days=30)
    assert payload["records"] == []


def test_execute_refuses_changed_root_identity_and_escaped_candidate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _old_file(tmp_path / "reports/mutation/old.json")
    monkeypatch.setattr(reports, "managed_paths", lambda _repo_root: set())
    payload = reports.inventory(tmp_path, older_than_days=30)
    original_fstat = reports.os.fstat
    monkeypatch.setattr(
        reports.os,
        "fstat",
        lambda fd: SimpleNamespace(
            st_dev=original_fstat(fd).st_dev + 1,
            st_ino=original_fstat(fd).st_ino,
        ),
    )
    with pytest.raises(SystemExit, match="report root changed"):
        reports.execute_prune(
            tmp_path,
            payload,
            confirmed_candidate_set_sha256=str(payload["candidate_set_sha256"]),
        )

    monkeypatch.setattr(reports.os, "fstat", original_fstat)
    payload["records"][0]["path"] = "reports/escaped.json"
    with pytest.raises(SystemExit, match="candidate escaped report root"):
        reports.execute_prune(
            tmp_path,
            payload,
            confirmed_candidate_set_sha256=str(payload["candidate_set_sha256"]),
        )


def test_execute_refuses_candidate_removed_after_inventory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    candidate = _old_file(tmp_path / "reports/mutation/old.json")
    monkeypatch.setattr(reports, "managed_paths", lambda _repo_root: set())
    payload = reports.inventory(tmp_path, older_than_days=30)
    candidate.unlink()
    with pytest.raises(SystemExit, match="candidate changed after inventory"):
        reports.execute_prune(
            tmp_path,
            payload,
            confirmed_candidate_set_sha256=str(payload["candidate_set_sha256"]),
        )


def test_main_rejects_negative_age_and_script_entrypoint_is_read_only(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit, match="greater than or equal to 0"):
        reports.main(["--repo-root", str(tmp_path), "--older-than-days", "-1"])

    monkeypatch.setattr(
        sys,
        "argv",
        ["manage_mutation_reports.py", "--repo-root", str(ROOT), "--older-than-days", "0"],
    )
    with pytest.raises(SystemExit) as exit_result:
        runpy.run_path(str(ROOT / "scripts/manage_mutation_reports.py"), run_name="__main__")
    assert exit_result.value.code == 0
    # The entrypoint's stdout is YAML now; parse it rather than substring-matching,
    # and keep asserting the field that proves the default run pruned nothing.
    assert yaml.safe_load(capsys.readouterr().out)["executed"] is False


def test_basetemp_helpers_preserve_on_os_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    basetemp = tmp_path / "charness-run-1"
    basetemp.mkdir()
    original_flock = basetemp_lib.fcntl.flock

    def fail_unlock(fd: int, operation: int) -> None:
        if operation == basetemp_lib.fcntl.LOCK_UN:
            raise OSError("unlock failed")
        original_flock(fd, operation)

    monkeypatch.setattr(basetemp_lib.fcntl, "flock", fail_unlock)
    assert basetemp_lib._basetemp_is_active(basetemp) is False

    original_open = Path.open

    def fail_lock_open(path: Path, *args: object, **kwargs: object):
        if path == basetemp_lib._basetemp_lock_path(basetemp):
            raise OSError("open failed")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fail_lock_open)
    assert basetemp_lib._basetemp_is_active(basetemp) is True


def test_basetemp_marker_age_inventory_and_prune_tolerate_os_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    basetemp = tmp_path / "charness-run-1"
    basetemp.mkdir()
    original_write = Path.write_text

    def fail_marker_write(path: Path, *args: object, **kwargs: object):
        if path.parent == basetemp:
            raise OSError("read only")
        return original_write(path, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", fail_marker_write)
    basetemp_lib._mark_basetemp(basetemp, basetemp_lib._FAILED_BASETEMP_MARKER)
    assert not (basetemp / basetemp_lib._FAILED_BASETEMP_MARKER).exists()
    assert basetemp_lib._failed_at(basetemp) == 0

    parent = tmp_path / "pytest-of-user"
    parent.mkdir()
    original_iterdir = Path.iterdir

    def fail_iterdir(path: Path):
        if path == parent:
            raise OSError("unreadable")
        return original_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", fail_iterdir)
    assert basetemp_lib.prune_failed_basetemps(parent, current_failed=None, keep=3) == []


def test_failed_basetemp_prune_skips_an_unremovable_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    parent = tmp_path / "pytest-of-user"
    stale = parent / "charness-run-1"
    stale.mkdir(parents=True)
    basetemp_lib._mark_basetemp(stale, basetemp_lib._FAILED_BASETEMP_MARKER)
    # Patch the OWNING module: `prune_failed_basetemps` resolves this name in
    # `standing_pytest_basetemp`'s globals, so patching the runner's re-export
    # bound nothing and this test passed while asserting nothing about the
    # branch it names (round-1 finding).
    monkeypatch.setattr(basetemp_lib, "_basetemp_is_active", lambda _path: False)
    monkeypatch.setattr(basetemp_lib.shutil, "rmtree", lambda _path: (_ for _ in ()).throw(OSError("busy")))
    assert basetemp_lib.prune_failed_basetemps(parent, current_failed=None, keep=0) == []
    assert stale.is_dir()


def test_successful_explicit_keep_marks_runner_owned_basetemp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    basetemp = tmp_path / "pytest-of-user/charness-run-1"
    monkeypatch.setattr(runner, "default_basetemp", lambda _repo_root: basetemp)
    monkeypatch.setattr(runner, "build_pytest_command", lambda *_args, **_kwargs: ["pytest"])

    def succeed(command: list[str], **_kwargs: object) -> SimpleNamespace:
        basetemp.mkdir(parents=True)
        return SimpleNamespace(
            returncode=0, timed_out=False, elapsed_seconds=1.0, stdout="", stderr=""
        )

    # Seam moved to the monitored primitive (S6/SC11); the retention behavior
    # under test is unchanged.
    monkeypatch.setattr(runner, "run_monitored_phase", succeed)
    result = runner.run_standing_pytest(
        SimpleNamespace(
            repo_root=repo,
            basetemp=None,
            include_release_only=False,
            mode="read-only",
            print_command=False,
            keep_basetemp=True,
            pytest_target=[],
            extra_pytest_target=[],
            timeout_seconds=None,
        )
    )
    assert result == 0
    assert (basetemp / basetemp_lib._KEPT_BASETEMP_MARKER).is_file()
