from __future__ import annotations

import os
import runpy
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from scripts.gates_support import run_standing_pytest as runner
from scripts.gates_support import standing_pytest_basetemp as basetemp_lib
from scripts.mutation import manage_mutation_reports as reports

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
        runpy.run_path(str(ROOT / "scripts/mutation/manage_mutation_reports.py"), run_name="__main__")
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


def _key(root: Path, name: str, *, repo_root: str | None = None) -> Path:
    key = root / name
    (key / "pytest-of-user").mkdir(parents=True)
    if repo_root is not None:
        (key / basetemp_lib.REPO_ROOT_MARKER).write_text(f"{repo_root}\n", encoding="utf-8")
    return key


def _age(path: Path, days: float) -> None:
    stamp = time.time() - days * 86400
    for entry in sorted(path.rglob("*"), reverse=True):
        os.utime(entry, (stamp, stamp))
    os.utime(path, (stamp, stamp))


def test_dead_repo_keys_are_reclaimed_and_live_ones_survive(tmp_path: Path) -> None:
    root = tmp_path / "pytest-tmp"
    root.mkdir()
    live_repo = tmp_path / "live-repo"
    live_repo.mkdir()
    mine = _key(root, "mine")
    dead = _key(root, "dead", repo_root=str(tmp_path / "deleted-worktree"))
    live = _key(root, "live", repo_root=str(live_repo))
    legacy_old = _key(root, "legacy-old")
    legacy_fresh = _key(root, "legacy-fresh")
    (legacy_old / "pytest-of-user" / "charness-run-1").mkdir()
    (legacy_fresh / "pytest-of-user" / "charness-run-2").mkdir()
    _age(legacy_old, basetemp_lib.LEGACY_KEY_MAX_AGE_DAYS + 1)

    removed = basetemp_lib.prune_dead_repo_keys(mine)

    assert set(removed) == {dead, legacy_old}
    assert mine.is_dir() and live.is_dir() and legacy_fresh.is_dir()
    assert not dead.exists() and not legacy_old.exists()


def test_a_dead_key_whose_run_still_holds_its_lock_is_left_alone(tmp_path: Path) -> None:
    root = tmp_path / "pytest-tmp"
    root.mkdir()
    mine = _key(root, "mine")
    busy = _key(root, "busy", repo_root=str(tmp_path / "gone"))
    (busy / "pytest-of-user" / "charness-run-9").mkdir()
    logged: list[str] = []

    with basetemp_lib._hold_basetemp_lock(busy / "pytest-of-user" / "charness-run-9"):
        assert basetemp_lib.prune_dead_repo_keys(mine, log=logged.append) == []
    assert busy.is_dir()
    assert logged == []

    removed = basetemp_lib.prune_dead_repo_keys(mine, log=logged.append)
    assert removed == [busy]
    assert logged and "removed dead pytest temp key" in logged[0]


def test_prepare_repo_key_claims_this_key_before_reclaiming_siblings(tmp_path: Path) -> None:
    root = tmp_path / "pytest-tmp"
    root.mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    dead = _key(root, "dead", repo_root=str(tmp_path / "gone"))
    mine = root / "mine"

    assert basetemp_lib.prepare_repo_key(repo, mine) == [dead]
    assert (mine / basetemp_lib.REPO_ROOT_MARKER).read_text(encoding="utf-8").strip() == str(repo)
    # A root that is not a `pytest-tmp` key parent is not a key namespace to sweep.
    assert basetemp_lib.prune_dead_repo_keys(tmp_path / "elsewhere" / "key") == []


def test_orphan_basetemps_keep_only_the_newest_unmarked_root(tmp_path: Path) -> None:
    parent = tmp_path / "pytest-of-user"
    parent.mkdir()
    orphans = [parent / f"charness-run-{stamp}" for stamp in (100, 200, 300)]
    for orphan in orphans:
        orphan.mkdir()
    failed = parent / "charness-run-50"
    failed.mkdir()
    basetemp_lib._mark_basetemp(failed, basetemp_lib._FAILED_BASETEMP_MARKER)
    kept = parent / "charness-run-60"
    kept.mkdir()
    basetemp_lib._mark_basetemp(kept, basetemp_lib._KEPT_BASETEMP_MARKER)

    removed = basetemp_lib.prune_orphan_basetemps(
        parent, current=None, keep=basetemp_lib.ORPHAN_BASETEMP_KEEP
    )

    assert set(removed) == {orphans[0], orphans[1]}
    assert orphans[2].is_dir() and failed.is_dir() and kept.is_dir()


def test_orphan_prune_spares_the_current_root_an_active_root_and_a_bad_parent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    parent = tmp_path / "pytest-of-user"
    parent.mkdir()
    current = parent / "charness-run-900"
    active = parent / "charness-run-800"
    unnamed = parent / "charness-run-legacy"
    for path in (current, active, unnamed):
        path.mkdir()

    with basetemp_lib._hold_basetemp_lock(active):
        removed = basetemp_lib.prune_orphan_basetemps(parent, current=current, keep=0)
    # `charness-run-legacy` does not match the run-root name, so it is not a candidate.
    assert removed == []
    assert current.is_dir() and active.is_dir() and unnamed.is_dir()

    monkeypatch.setattr(Path, "iterdir", _raise_os_error)
    assert basetemp_lib.prune_orphan_basetemps(parent, current=None, keep=0) == []


def _raise_os_error(*_args: object, **_kwargs: object):
    raise OSError("unreadable")


def test_run_started_at_falls_back_to_mtime_for_an_unstamped_name(tmp_path: Path) -> None:
    stamped = tmp_path / "charness-run-4242"
    stamped.mkdir()
    assert basetemp_lib._run_started_at(stamped) == 4242
    unstamped = tmp_path / "charness-run-x"
    unstamped.mkdir()
    assert basetemp_lib._run_started_at(unstamped) == unstamped.stat().st_mtime_ns
    assert basetemp_lib._run_started_at(tmp_path / "charness-run-gone") == 0


def test_the_runner_claims_its_key_and_bounds_orphans_around_a_passing_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The keyed namespace this sweep exists for is the one the quality engine builds:
    # it exports `--print-temp-root` as `PYTEST_DEBUG_TEMPROOT`, so the runner inherits
    # `<cache>/pytest-tmp/<repo-key>`. Redirect it, because this suite itself runs under
    # a live `PYTEST_DEBUG_TEMPROOT` pointing at the real cache.
    temp_root = tmp_path / "pytest-tmp" / "mine"
    monkeypatch.setenv("PYTEST_DEBUG_TEMPROOT", str(temp_root))
    repo = tmp_path / "repo"
    repo.mkdir()
    assert basetemp_lib.default_temp_root(repo, dict(os.environ)) == temp_root
    dead = _key(temp_root.parent, "dead", repo_root=str(tmp_path / "gone"))
    orphan = temp_root / "pytest-of-user" / "charness-run-1"
    orphan.mkdir(parents=True)
    basetemp = temp_root / "pytest-of-user" / "charness-run-2"

    monkeypatch.setattr(runner, "default_basetemp", lambda _repo_root: basetemp)
    monkeypatch.setattr(runner, "build_pytest_command", lambda *_a, **_k: ["pytest"])

    def succeed(command: list[str], **_kwargs: object) -> SimpleNamespace:
        basetemp.mkdir(parents=True)
        return SimpleNamespace(
            returncode=0, timed_out=False, elapsed_seconds=1.0, stdout="", stderr=""
        )

    monkeypatch.setattr(runner, "run_monitored_phase", succeed)
    result = runner.run_standing_pytest(
        SimpleNamespace(
            repo_root=repo,
            basetemp=None,
            include_release_only=False,
            mode="read-only",
            print_command=False,
            keep_basetemp=False,
            pytest_target=[],
            extra_pytest_target=[],
            timeout_seconds=None,
        )
    )

    assert result == 0
    assert (temp_root / basetemp_lib.REPO_ROOT_MARKER).read_text(encoding="utf-8").strip() == str(
        repo
    )
    assert not dead.exists()
    # The passing run removed its own root; the pre-existing orphan is now the newest
    # unmarked root, so `ORPHAN_BASETEMP_KEEP` keeps exactly it.
    assert not basetemp.exists()
    assert orphan.is_dir()


def _set_mtime(paths: "list[Path]", *, days_ago: float) -> None:
    """Age directories without touching their parents' mtimes.

    `_age` above walks with `rglob` and `os.utime`, which follows symlinks; these
    cases deliberately seed a dangling one, so they stamp exactly the directories
    whose age the liveness answer turns on.
    """
    stamp = time.time() - days_ago * 86400
    for path in paths:
        os.utime(path, (stamp, stamp))


def test_repo_root_marker_write_gives_up_on_a_key_path_that_is_a_file(tmp_path: Path) -> None:
    """A key path already taken by a file is not a reason to fail a whole run.

    The marker is an OPTIMIZATION: without it a key falls back to the age test.
    So `record_repo_root_marker` swallows the write failure, and this pins that
    it neither raises nor destroys whatever already occupies the path.
    """
    blocked = tmp_path / "pytest-tmp" / "mine"
    blocked.parent.mkdir(parents=True)
    blocked.write_text("not a directory", encoding="utf-8")

    basetemp_lib.record_repo_root_marker(blocked, tmp_path / "repo")

    assert blocked.read_text(encoding="utf-8") == "not a directory"


def test_a_key_that_cannot_be_listed_is_assumed_live(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Unreadable must mean "leave it alone", because the sweep deletes.

    `Path.glob` swallows a real permission error internally, so there is no
    filesystem condition that reaches this branch; the seam is patched at the one
    path under test and delegates everywhere else.
    """
    key = tmp_path / "pytest-tmp" / "opaque"
    (key / "pytest-of-user").mkdir(parents=True)
    original_glob = Path.glob

    def fail_glob(path: Path, pattern: str):
        if path == key:
            raise OSError("unreadable")
        return original_glob(path, pattern)

    monkeypatch.setattr(Path, "glob", fail_glob)

    assert basetemp_lib._key_is_active(key) is True


def test_shallow_liveness_skips_an_unreadable_child_and_a_dangling_entry(tmp_path: Path) -> None:
    """The cheap liveness half must survive the tree it is asked to skim.

    Both conditions are real: a directory the runner cannot list, and an entry
    whose `stat` follows a link to nothing. Neither may be read as "recently
    used", or the sweep would spare every key it cannot fully inspect.
    """
    key = tmp_path / "key"
    unreadable = key / "pytest-of-user"
    unreadable.mkdir(parents=True)
    listable = key / "pytest-of-other"
    listable.mkdir()
    (listable / "charness-run-1").symlink_to(tmp_path / "never-created")
    _set_mtime([listable, unreadable, key], days_ago=60)
    unreadable.chmod(0o000)
    try:
        answer = basetemp_lib._shallow_entry_newer_than(key, time.time() - 30 * 86400)
    finally:
        unreadable.chmod(0o755)

    assert answer is False
    assert basetemp_lib._safe_mtime(listable / "charness-run-1") == 0.0


def test_deep_liveness_answers_from_a_late_entry_and_from_a_vanished_root(tmp_path: Path) -> None:
    """The walk exists for exactly the entry the three-stat skim cannot reach.

    The fresh directory sits one level below the skim's horizon, so a key that
    the cheap half calls dead is still proven live here. A root that no longer
    exists is the opposite refusal: unknown is never "safe to delete".
    """
    key = tmp_path / "key"
    run = key / "pytest-of-user" / "charness-run-1"
    (run / "fresh").mkdir(parents=True)
    cutoff = time.time() - 30 * 86400
    _set_mtime([run, key / "pytest-of-user", key], days_ago=60)

    assert basetemp_lib._shallow_entry_newer_than(key, cutoff) is False
    assert basetemp_lib._has_entry_newer_than(key, cutoff) is True
    assert basetemp_lib._has_entry_newer_than(tmp_path / "gone", cutoff) is True


def test_liveness_and_size_skip_an_entry_that_disappears_mid_walk(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A run deleting its own scratch tree under the sweep is the ordinary race.

    `os.walk` names an entry that `os.lstat` then cannot see. Neither the
    liveness answer nor the freed-bytes figure may blow up on it: the walk keeps
    going and the vanished entry simply contributes nothing.
    """
    key = tmp_path / "key"
    run = key / "pytest-of-user" / "charness-run-1"
    run.mkdir(parents=True)
    (run / "vanishing-entry").write_text("x" * 16, encoding="utf-8")
    cutoff = time.time() - 30 * 86400
    _set_mtime([run, key / "pytest-of-user", key], days_ago=60)
    original_lstat = basetemp_lib.os.lstat

    def vanishing(path, *args: object, **kwargs: object):
        if str(path).endswith("vanishing-entry"):
            raise OSError("gone")
        return original_lstat(path, *args, **kwargs)

    monkeypatch.setattr(basetemp_lib.os, "lstat", vanishing)

    assert basetemp_lib._has_entry_newer_than(key, cutoff) is False
    assert basetemp_lib._tree_size_bytes(key) == 0


def test_key_sweep_returns_nothing_when_the_key_namespace_is_absent(tmp_path: Path) -> None:
    """The first standing run of a fresh worktree has no namespace to sweep yet."""
    assert basetemp_lib.prune_dead_repo_keys(tmp_path / "pytest-tmp" / "mine") == []


def test_a_dead_key_survives_when_its_namespace_is_not_writable(tmp_path: Path) -> None:
    """An unremovable key is skipped, not reported as reclaimed and not fatal.

    Removal genuinely fails here -- the namespace directory denies the final
    `rmdir` -- so this is the real condition rather than a patched `rmtree`. The
    key must stay out of the returned list, because the caller logs that list as
    space it reclaimed.
    """
    root = tmp_path / "pytest-tmp"
    root.mkdir()
    mine = _key(root, "mine")
    dead = _key(root, "dead", repo_root=str(tmp_path / "gone"))
    logged: list[str] = []
    root.chmod(0o500)
    try:
        removed = basetemp_lib.prune_dead_repo_keys(mine, log=logged.append)
    finally:
        root.chmod(0o755)

    assert removed == []
    assert logged == []
    assert dead.is_dir()


def test_an_orphan_root_that_cannot_be_removed_is_left_in_place(tmp_path: Path) -> None:
    """The orphan sweep's own unremovable case, alongside the failed and key sweeps.

    Removal fails for real: the orphan holds a directory that denies the unlink
    `rmtree` needs. The orphan must stay off the returned list, since the caller
    reads that list as roots it actually reclaimed.
    """
    parent = tmp_path / "pytest-of-user"
    orphan = parent / "charness-run-1"
    locked = orphan / "locked"
    locked.mkdir(parents=True)
    (locked / "held").write_text("x", encoding="utf-8")
    locked.chmod(0o500)
    try:
        removed = basetemp_lib.prune_orphan_basetemps(parent, current=None, keep=0)
    finally:
        locked.chmod(0o755)

    assert removed == []
    assert orphan.is_dir()
