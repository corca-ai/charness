"""Runtime-root retention (#787): keys are siblings, finished lanes keep only their record,
and the sweep removes what the written rule names, logs it, and reaches nothing else."""

from __future__ import annotations

import json
import os
import subprocess
import tarfile
import time
from pathlib import Path

import pytest

from scripts import runtime_bootstrap
from scripts.gates_support import runtime_root_retention as retention
from tests.quality_gates.repo_shapes import install_committed_repo

DAY = 86400.0


# --- the bootstrap: keys are siblings ---------------------------------------


def test_a_child_bootstrapped_from_a_key_lands_beside_it_not_inside_it(tmp_path: Path) -> None:
    base = tmp_path / "cache"
    parent_repo = tmp_path / "parent"
    child_repo = tmp_path / "child"
    parent_repo.mkdir()
    child_repo.mkdir()
    parent_env = runtime_bootstrap.configure_runtime_environment(
        parent_repo, {"XDG_CACHE_HOME": str(base)}
    )
    parent_key = Path(parent_env["CHARNESS_RUNTIME_ROOT"])
    assert parent_key.parent == base / "charness" / "runtime"
    # A configured cache home is kept; a bootstrap that found none exports its own.
    assert parent_env["XDG_CACHE_HOME"] == str(base)
    exported = runtime_bootstrap.configure_runtime_environment(parent_repo, {"TMPDIR": str(base)})
    assert exported["XDG_CACHE_HOME"] == str(parent_key / "xdg-cache")
    parent_env = exported

    # The shape that nested 23,401 keys: a child for ANOTHER repo inherits the
    # parent's exported environment, including its auto key and its xdg-cache.
    child_root = runtime_bootstrap.runtime_root(child_repo, dict(parent_env))
    assert child_root.parent == parent_key.parent
    assert child_root != parent_key
    assert not str(child_root).startswith(str(parent_key))

    # The `task run` preview shape: the auto-root variables stripped, xdg inherited.
    preview = {k: v for k, v in parent_env.items() if not k.startswith("CHARNESS_RUNTIME_")}
    assert runtime_bootstrap.runtime_root(child_repo, preview).parent == parent_key.parent

    # A lane's private runtime exports its own xdg-cache one level deeper still.
    lane_env = {"XDG_CACHE_HOME": str(parent_key / "task-run" / "lane" / "runtime" / "xdg-cache")}
    assert runtime_bootstrap.runtime_root(child_repo, lane_env).parent == parent_key.parent


def test_a_plain_cache_home_is_used_as_is_even_inside_a_key(tmp_path: Path) -> None:
    """Only the bootstrap's own `xdg-cache` export is rewritten.

    pytest's `tmp_path` lives under this run's own key, so a cache home a test
    points there sits inside a `charness/runtime` tree by construction; it is
    still used as given, or every fixture in the suite would write into the
    live tree. (This is the live-tree assumption the #787 body asked to name.)
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    plain = tmp_path / "plain"
    root = runtime_bootstrap.runtime_root(repo, {"XDG_CACHE_HOME": str(plain)})
    assert root.parent == plain / "charness" / "runtime"
    # A key's own export under that plain base is hoisted to the plain base, not higher.
    export = plain / "charness" / "runtime" / "abc" / "xdg-cache"
    assert runtime_bootstrap.runtime_root(repo, {"XDG_CACHE_HOME": str(export)}).parent == (
        plain / "charness" / "runtime"
    )
    # An `xdg-cache` directory outside any runtime tree is used as given (a path
    # under `tmp_path` would sit inside this run's own tree, so it is spelled out).
    loose = Path("/nonexistent-charness-base/elsewhere/xdg-cache")
    assert runtime_bootstrap.runtime_root(repo, {"XDG_CACHE_HOME": str(loose)}).parent == (
        loose / "charness" / "runtime"
    )


def test_the_bootstrap_records_the_repo_root_marker_once(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    env = runtime_bootstrap.configure_runtime_environment(repo, {"XDG_CACHE_HOME": str(tmp_path / "c")})
    marker = Path(env["CHARNESS_RUNTIME_ROOT"]) / runtime_bootstrap.REPO_ROOT_MARKER
    assert marker.read_text(encoding="utf-8").strip() == str(repo.resolve())
    marker.write_text("kept\n", encoding="utf-8")
    runtime_bootstrap.configure_runtime_environment(repo, {"XDG_CACHE_HOME": str(tmp_path / "c")})
    assert marker.read_text(encoding="utf-8") == "kept\n"
    # An explicit, non-auto root records nothing.
    explicit = tmp_path / "explicit"
    runtime_bootstrap.configure_runtime_environment(repo, {"CHARNESS_RUNTIME_ROOT": str(explicit)})
    assert not (explicit / runtime_bootstrap.REPO_ROOT_MARKER).exists()


# --- the sweep ----------------------------------------------------------------


def _age(path: Path, seconds: float, *, now: float) -> None:
    stamp = now - seconds
    for parent, dirs, files in os.walk(path):
        for name in (*dirs, *files):
            os.utime(os.path.join(parent, name), (stamp, stamp))
    os.utime(path, (stamp, stamp))


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)


def _tree(tmp_path: Path, *, now: float) -> tuple[Path, Path]:
    """`<base>/charness/runtime/<mine>` plus the shapes the rule names, all idle."""
    keys = tmp_path / "cache" / "charness" / "runtime"
    mine = keys / "0000000000000001"
    repo = tmp_path / "repo"
    repo.mkdir()
    # a finished lane with a clean commit-carried worktree
    clean = mine / "task-run" / "clean-lane"
    install_committed_repo(clean / "worktree", {"a.py": "A = 1\n"})
    (clean / "runtime" / "tmp").mkdir(parents=True)
    (clean / "runtime" / "tmp" / "scratch").write_text("x", encoding="utf-8")
    (clean / "result.json").write_text(json.dumps({"phase": "terminal", "status": "completed"}), encoding="utf-8")
    (clean / "codex.stdout.log").write_text("done\n", encoding="utf-8")
    # a finished lane whose worktree holds uncommitted edits and an untracked file
    dirty = mine / "task-run" / "dirty-lane"
    install_committed_repo(dirty / "worktree", {"a.py": "A = 1\n"})
    (dirty / "worktree" / "a.py").write_text("A = 2\n", encoding="utf-8")
    (dirty / "worktree" / "new.txt").write_text("untracked\n", encoding="utf-8")
    (dirty / "result.json").write_text(json.dumps({"phase": "terminal", "status": "validated-partial-result"}), encoding="utf-8")
    # a running lane (non-terminal result, fresh)
    running = mine / "task-run" / "running-lane"
    (running / "worktree").mkdir(parents=True)
    (running / "result.json").write_text(json.dumps({"phase": "exec", "status": "running"}), encoding="utf-8")
    # nested keys inside xdg-cache
    nested = mine / retention.NESTED_KEYS_REL / "0000000000000009"
    (nested / "pycache").mkdir(parents=True)
    (nested / "pycache" / "x.pyc").write_bytes(b"\x00" * 10)
    # idle and fresh rebuilt-on-demand subtrees
    (mine / "pycache").mkdir(parents=True)
    (mine / "pycache" / "old.pyc").write_bytes(b"\x00" * 100)
    (mine / "coverage").mkdir()
    (mine / "coverage" / ".coverage").write_bytes(b"\x00" * 100)
    # sibling keys: dead (repo gone), live (repo exists), legacy idle, legacy fresh
    dead = keys / "0000000000000002"
    dead.mkdir(parents=True)
    (dead / retention.REPO_ROOT_MARKER).write_text(str(tmp_path / "gone"), encoding="utf-8")
    (dead / "pycache").mkdir()
    (dead / "pycache" / "x.pyc").write_bytes(b"\x00" * 50)
    live = keys / "0000000000000003"
    live.mkdir()
    (live / retention.REPO_ROOT_MARKER).write_text(str(repo), encoding="utf-8")
    (live / "pycache").mkdir()
    (live / "pycache" / "x.pyc").write_bytes(b"\x00" * 50)
    legacy_idle = keys / "0000000000000004"
    (legacy_idle / "tmp").mkdir(parents=True)
    (legacy_idle / "tmp" / "f").write_text("x", encoding="utf-8")
    legacy_fresh = keys / "0000000000000005"
    (legacy_fresh / "tmp").mkdir(parents=True)
    (legacy_fresh / "tmp" / "f").write_text("x", encoding="utf-8")
    # something OUTSIDE the tree that must never be touched
    outside = tmp_path / "cache" / "charness" / "support-skills"
    outside.mkdir(parents=True)
    (outside / "keep").write_text("x", encoding="utf-8")

    _age(keys, 30 * DAY, now=now)
    _age(outside, 30 * DAY, now=now)
    # fresh again: the running lane, the live key's own activity, the fresh legacy key,
    # and this run's coverage file
    _age(running, 0, now=now)
    _age(legacy_fresh, 0, now=now)
    _age(mine / "coverage", 0, now=now)
    return mine, repo


def test_the_sweep_removes_what_the_rule_names_and_nothing_else(tmp_path: Path) -> None:
    now = time.time()
    mine, repo = _tree(tmp_path, now=now)
    keys = mine.parent
    lines: list[str] = []

    report = retention.sweep_runtime_root(repo, key_root=mine, now=now, log=lines.append)

    by_path = {Path(e["path"]): e for e in report["entries"]}
    lanes = mine / "task-run"
    # finished clean lane: worktree and runtime gone, record and log kept
    assert by_path[lanes / "clean-lane" / "worktree"]["action"] == "removed"
    assert by_path[lanes / "clean-lane" / "runtime"]["action"] == "removed"
    assert by_path[lanes / "clean-lane" / "worktree"]["salvage"] == {"status": "clean", "head": by_path[lanes / "clean-lane" / "worktree"]["salvage"]["head"]}
    assert (lanes / "clean-lane" / "result.json").is_file()
    assert (lanes / "clean-lane" / "codex.stdout.log").is_file()
    assert not (lanes / "clean-lane" / "worktree").exists()
    # finished dirty lane: salvaged, verified, then removed
    salvage = by_path[lanes / "dirty-lane" / "worktree"]["salvage"]
    assert salvage["status"] == "salvaged" and salvage["patch_verified"] is True
    patch = (lanes / "dirty-lane" / retention.SALVAGE_PATCH).read_text(encoding="utf-8")
    assert "-A = 1" in patch and "+A = 2" in patch
    with tarfile.open(lanes / "dirty-lane" / retention.SALVAGE_TAR) as tar:
        assert tar.getnames() == ["new.txt"]
    record = json.loads((lanes / "dirty-lane" / retention.SALVAGE_RECORD).read_text(encoding="utf-8"))
    assert record["untracked"] == ["new.txt"]
    assert not (lanes / "dirty-lane" / "worktree").exists()
    # running lane skipped with its reason
    assert by_path[lanes / "running-lane"]["action"] == "skipped"
    assert "not terminal" in by_path[lanes / "running-lane"]["reason"]
    assert (lanes / "running-lane" / "worktree").is_dir()
    # nested key removed
    nested = mine / retention.NESTED_KEYS_REL / "0000000000000009"
    assert by_path[nested]["action"] == "removed"
    assert not nested.exists()
    # idle pycache removed, fresh coverage kept
    assert by_path[mine / "pycache"]["action"] == "removed"
    assert (mine / "coverage" / ".coverage").is_file()
    assert mine / "coverage" not in by_path
    # siblings: dead removed, live kept, legacy idle removed, legacy fresh skipped
    assert by_path[keys / "0000000000000002"]["action"] == "removed"
    assert "no longer exists" in by_path[keys / "0000000000000002"]["reason"]
    # a live key stays, and its own idle subtrees are reclaimed under the subtree rule
    assert (keys / "0000000000000003" / retention.REPO_ROOT_MARKER).exists()
    assert keys / "0000000000000003" not in by_path
    assert by_path[keys / "0000000000000003" / "pycache"]["action"] == "removed"
    assert by_path[keys / "0000000000000004"]["action"] == "removed"
    assert by_path[keys / "0000000000000005"]["action"] == "skipped"
    assert (keys / "0000000000000005" / "tmp" / "f").exists()
    # outside the tree: untouched, never even a candidate
    assert (tmp_path / "cache" / "charness" / "support-skills" / "keep").exists()
    assert all(Path(e["path"]).is_relative_to(keys) for e in report["entries"])
    # the marker for this run's key was written; the log names bytes and reasons
    assert (mine / retention.REPO_ROOT_MARKER).read_text(encoding="utf-8").strip() == str(repo.resolve())
    assert report["removed_bytes"] > 0
    assert report["counts"]["removed"] >= 7
    log = json.loads(Path(report["log_path"]).read_text(encoding="utf-8"))
    assert log["entries"] == report["entries"]
    assert any("removed" in line and "MiB" in line for line in lines)


def test_the_sweep_does_not_delete_a_keep_worktree_named_copy(tmp_path: Path) -> None:
    now = time.time()
    keys = tmp_path / "cache" / "charness" / "runtime"
    mine = keys / "0000000000000001"
    repo = tmp_path / "repo"
    repo.mkdir()
    lane = mine / "task-run" / "kept-lane"
    install_committed_repo(lane / "worktree", {"a.py": "A = 1\n"})
    (lane / "worktree" / "a.py").write_text("A = 2\n", encoding="utf-8")
    (lane / "worktree" / "new.txt").write_text("untracked\n", encoding="utf-8")
    (lane / "runtime").mkdir(parents=True)
    (lane / "result.json").write_text(
        json.dumps(
            {
                "phase": "terminal",
                "status": "validated-partial-result",
                "keep_worktree": True,
                "candidate": {
                    "useful": True,
                    "carrier_kind": "worktree-only",
                    "head_is_complete": False,
                },
            }
        ),
        encoding="utf-8",
    )
    _age(mine, 30 * DAY, now=now)

    report = retention.sweep_runtime_root(repo, key_root=mine, now=now)

    entry = next(e for e in report["entries"] if e["path"] == str(lane / "worktree"))
    assert entry["action"] == "skipped"
    assert "keep_worktree retains the named worktree" in entry["reason"]
    assert entry["salvage"]["status"] == "salvaged"
    assert (lane / "worktree" / "a.py").is_file()
    assert (lane / "worktree" / "new.txt").is_file()
    assert (lane / retention.SALVAGE_PATCH).is_file()
    assert (lane / retention.SALVAGE_TAR).is_file()
    assert (lane / "runtime").is_dir()


def test_a_dry_run_plans_the_same_and_removes_nothing(tmp_path: Path) -> None:
    now = time.time()
    mine, repo = _tree(tmp_path, now=now)
    before = sorted(str(p) for p in tmp_path.rglob("*"))

    report = retention.sweep_runtime_root(repo, key_root=mine, now=now, dry_run=True)

    assert report["dry_run"] is True
    assert report["removed_bytes"] == 0
    assert report["log_path"] is None
    assert report["counts"]["would-remove"] >= 7
    assert "removed" not in report["counts"]
    dirty = next(e for e in report["entries"] if e["path"].endswith("dirty-lane/worktree"))
    assert dirty["salvage"]["status"] == "would-salvage"
    after = sorted(str(p) for p in tmp_path.rglob("*") if not p.name.startswith(".charness-repo-root"))
    assert [p for p in before if not p.endswith(".charness-repo-root")] == after


def test_an_unverifiable_salvage_keeps_the_worktree(tmp_path: Path, monkeypatch) -> None:
    now = time.time()
    mine, repo = _tree(tmp_path, now=now)
    real = retention.Sweep._git

    def failing_apply(cwd: Path, *args: str):
        if args[:2] == ("apply", "--check"):
            return subprocess.CompletedProcess(args, 1, "", "patch does not apply")
        return real(cwd, *args)

    report = retention.sweep_runtime_root(repo, key_root=mine, now=now, git=failing_apply)

    entry = next(e for e in report["entries"] if e["path"].endswith("dirty-lane/worktree"))
    assert entry["action"] == "skipped"
    assert "could not be salvaged verifiably" in entry["reason"]
    assert (mine / "task-run" / "dirty-lane" / "worktree" / "a.py").exists()


def test_a_key_with_a_live_pytest_run_lock_is_skipped(tmp_path: Path) -> None:
    from scripts.gates_support import standing_pytest_basetemp as basetemp

    now = time.time()
    mine, repo = _tree(tmp_path, now=now)
    locked = mine.parent / "0000000000000002"
    basetemp_dir = locked / basetemp._KEY_ROOT_NAME / "abc" / "pytest-of-me" / "charness-run-1"
    basetemp_dir.mkdir(parents=True)
    _age(locked, 30 * DAY, now=now)
    with basetemp._hold_basetemp_lock(basetemp_dir):
        report = retention.sweep_runtime_root(repo, key_root=mine, now=now)
    entry = next(e for e in report["entries"] if e["path"] == str(locked))
    assert entry["action"] == "skipped"
    assert "live" in entry["reason"]
    assert locked.exists()


def test_an_explicit_runtime_root_has_no_siblings_and_is_skipped(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    lines: list[str] = []
    report = retention.sweep_runtime_root(repo, key_root=tmp_path / "explicit", log=lines.append)
    assert report["entries"] == []
    assert "not a charness runtime key" in report["skipped"]
    assert lines and "explicit CHARNESS_RUNTIME_ROOT" in lines[0]


def test_the_cli_reports_counts_and_writes_its_log(tmp_path: Path, capsys) -> None:
    import yaml

    now = time.time()
    mine, repo = _tree(tmp_path, now=now)
    assert retention.main(["--repo-root", str(repo), "--key-root", str(mine), "--dry-run"]) == 0
    dry = yaml.safe_load(capsys.readouterr().out)
    assert dry["counts"]["would-remove"] >= 7 and "(dry run)" in dry["summary"]
    assert "entries" not in dry
    assert retention.main(["--repo-root", str(repo), "--key-root", str(mine), "--verbose"]) == 0
    report = yaml.safe_load(capsys.readouterr().out)
    assert report["counts"]["removed"] >= 7
    assert any(entry["action"] == "removed" for entry in report["entries"])
    assert Path(report["log_path"]).is_file()
    assert Path(report["log_path"]).parent == mine / retention.LOG_DIR_NAME


def test_read_only_files_inside_a_removed_tree_do_not_stop_the_removal(tmp_path: Path) -> None:
    now = time.time()
    mine, repo = _tree(tmp_path, now=now)
    manifest = mine / "task-run" / "clean-lane" / "runtime" / "tmp" / "manifest.json"
    manifest.write_text("{}", encoding="utf-8")
    manifest.chmod(0o444)
    manifest.parent.chmod(0o555)
    _age(mine / "task-run" / "clean-lane", 30 * DAY, now=now)

    retention.sweep_runtime_root(repo, key_root=mine, now=now)

    assert not manifest.exists()


@pytest.mark.parametrize("phase", ["exec", None])
def test_an_idle_lane_that_never_reached_terminal_is_released_with_its_reason(tmp_path: Path, phase) -> None:
    now = time.time()
    mine, repo = _tree(tmp_path, now=now)
    stale = mine / "task-run" / "stale-lane"
    (stale / "worktree").mkdir(parents=True)
    (stale / "runtime").mkdir()
    if phase is not None:
        (stale / "result.json").write_text(json.dumps({"phase": phase}), encoding="utf-8")
    _age(stale, 30 * DAY, now=now)

    report = retention.sweep_runtime_root(repo, key_root=mine, now=now)

    entry = next(e for e in report["entries"] if e["path"] == str(stale / "runtime"))
    assert entry["action"] == "removed"
    assert "idle" in entry["reason"]
    assert not (stale / "worktree").exists()


def test_sweep_logs_are_bounded_to_the_newest_keep(tmp_path: Path, monkeypatch) -> None:
    now = time.time()
    mine, repo = _tree(tmp_path, now=now)
    monkeypatch.setattr(retention, "SWEEP_LOG_KEEP", 3)
    for offset in range(5):
        retention.sweep_runtime_root(repo, key_root=mine, now=now + offset)
    logs = sorted(p.name for p in (mine / retention.LOG_DIR_NAME).glob("sweep-*.json"))
    assert logs == [f"sweep-{int(now) + offset}.json" for offset in (2, 3, 4)]


# --- the branches the changed-line gate named ---------------------------------


def test_bootstrap_shim_inserts_the_repo_root_when_it_is_absent(monkeypatch) -> None:
    import sys

    root = Path(__file__).resolve().parents[1]
    stripped = [entry for entry in sys.path if entry and Path(entry).resolve() != root]
    monkeypatch.setattr(sys, "path", stripped)
    retention._load_repo_runtime_bootstrap()
    assert str(root) in sys.path


def test_a_path_outside_the_tree_is_refused_and_a_failed_removal_is_logged(
    tmp_path: Path, monkeypatch
) -> None:
    now = time.time()
    mine, repo = _tree(tmp_path, now=now)
    sweep = retention.Sweep(mine, now=now)
    outside = tmp_path / "cache" / "charness" / "support-skills"
    assert sweep._remove_tree(outside, "seeded") is False
    assert sweep.entries[-1]["action"] == "refused"
    assert outside.exists()

    def refuse(_path: Path) -> None:
        raise OSError("device busy")

    monkeypatch.setattr(retention, "_rmtree_writable", refuse)
    assert sweep._remove_tree(mine / "pycache", "seeded") is False
    failed = sweep.entries[-1]
    assert failed["action"] == "failed" and "device busy" in failed["reason"]
    assert failed["bytes"] == 100
    assert (mine / "pycache" / "old.pyc").exists()


def test_files_beside_lane_records_and_nested_keys_are_ignored_and_a_fresh_recordless_lane_is_skipped(
    tmp_path: Path,
) -> None:
    now = time.time()
    mine, repo = _tree(tmp_path, now=now)
    (mine / "task-run" / "stray.txt").write_text("x", encoding="utf-8")
    (mine / retention.NESTED_KEYS_REL / "stray.txt").write_text("x", encoding="utf-8")
    fresh = mine / "task-run" / "fresh-no-result"
    (fresh / "worktree").mkdir(parents=True)

    report = retention.sweep_runtime_root(repo, key_root=mine, now=now)

    paths = {e["path"] for e in report["entries"]}
    assert str(mine / "task-run" / "stray.txt") not in paths
    assert str(mine / retention.NESTED_KEYS_REL / "stray.txt") not in paths
    entry = next(e for e in report["entries"] if e["path"] == str(fresh))
    assert entry["action"] == "skipped"
    assert entry["reason"] == "no readable result.json and the record is fresh"
    assert (fresh / "worktree").is_dir()


def test_unreadable_directories_and_missing_markers_read_as_empty(tmp_path: Path) -> None:
    assert retention._children(tmp_path / "missing") == []
    assert retention._read_text(tmp_path / "missing") is None
    assert retention._read_marker(tmp_path / "missing-key") is None


def test_a_legacy_marker_under_pytest_tmp_still_names_the_dead_repo(tmp_path: Path) -> None:
    from scripts.gates_support import standing_pytest_basetemp as basetemp

    now = time.time()
    mine, repo = _tree(tmp_path, now=now)
    legacy = mine.parent / "0000000000000006"
    tmp_key = legacy / basetemp._KEY_ROOT_NAME / "abc"
    tmp_key.mkdir(parents=True)
    (tmp_key / retention.REPO_ROOT_MARKER).write_text(str(tmp_path / "gone-too"), encoding="utf-8")
    _age(legacy, 2 * DAY, now=now)

    report = retention.sweep_runtime_root(repo, key_root=mine, now=now)

    entry = next(e for e in report["entries"] if e["path"] == str(legacy))
    assert entry["action"] == "removed"
    assert "gone-too" in entry["reason"]


@pytest.mark.parametrize("failing", ["rev-parse", "status", "diff"])
def test_a_git_failure_during_salvage_keeps_the_worktree(tmp_path: Path, failing: str) -> None:
    now = time.time()
    mine, repo = _tree(tmp_path, now=now)
    real = retention.Sweep._git

    def git(cwd: Path, *args: str):
        if args[0] == failing:
            return subprocess.CompletedProcess(args, 128, "", f"{failing} exploded")
        return real(cwd, *args)

    report = retention.sweep_runtime_root(repo, key_root=mine, now=now, git=git)

    entry = next(e for e in report["entries"] if e["path"].endswith("dirty-lane/worktree"))
    assert entry["action"] == "skipped"
    assert f"{failing} exploded" in entry["reason"] or "failed" in entry["reason"]
    assert (mine / "task-run" / "dirty-lane" / "worktree" / "a.py").exists()


def test_a_log_directory_that_cannot_be_written_leaves_log_path_empty(tmp_path: Path) -> None:
    now = time.time()
    mine, repo = _tree(tmp_path, now=now)
    (mine / retention.LOG_DIR_NAME).write_text("not a directory", encoding="utf-8")

    report = retention.sweep_runtime_root(repo, key_root=mine, now=now)

    assert report["log_path"] is None
    assert report["counts"]["removed"] >= 7


def test_the_module_main_guard_executes(tmp_path: Path, monkeypatch) -> None:
    import runpy
    import sys

    now = time.time()
    mine, repo = _tree(tmp_path, now=now)
    root = Path(__file__).resolve().parents[1]
    monkeypatch.setattr(
        sys,
        "argv",
        ["runtime_root_retention.py", "--repo-root", str(repo), "--key-root", str(mine), "--dry-run"],
    )
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(str(root / "scripts/gates_support/runtime_root_retention.py"), run_name="__main__")
    assert excinfo.value.code == 0


def test_a_marker_that_cannot_be_written_does_not_stop_the_bootstrap(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    base = tmp_path / "base"
    key = runtime_bootstrap.runtime_root(repo, {"XDG_CACHE_HOME": str(base)})
    # A directory where the marker file would go: `is_file()` is false, the write raises.
    (key / runtime_bootstrap.REPO_ROOT_MARKER).mkdir(parents=True)

    env = runtime_bootstrap.configure_runtime_environment(repo, {"XDG_CACHE_HOME": str(base)})

    assert env["CHARNESS_RUNTIME_ROOT"] == str(key)
    assert (key / runtime_bootstrap.REPO_ROOT_MARKER).is_dir()


def test_the_sweep_marker_write_tolerates_an_unwritable_key(tmp_path: Path) -> None:
    key = tmp_path / "cache" / "charness" / "runtime" / "0000000000000007"
    (key / retention.REPO_ROOT_MARKER).mkdir(parents=True)
    retention.record_repo_root_marker(key, tmp_path / "repo")
    assert (key / retention.REPO_ROOT_MARKER).is_dir()


def test_salvage_keeps_every_untracked_path_git_names_including_awkward_ones(tmp_path: Path) -> None:
    """The porcelain form quotes a space, a quote, a backslash, or non-ASCII; `-z` does not."""
    now = time.time()
    mine, repo = _tree(tmp_path, now=now)
    worktree = mine / "task-run" / "dirty-lane" / "worktree"
    awkward = ["with space.txt", 'quo"te.txt', "back\\slash.txt", "한글.txt", "nested/dir/file.txt"]
    for rel in awkward:
        (worktree / rel).parent.mkdir(parents=True, exist_ok=True)
        (worktree / rel).write_text(rel, encoding="utf-8")
    _age(worktree, 30 * DAY, now=now)

    report = retention.sweep_runtime_root(repo, key_root=mine, now=now)

    entry = next(e for e in report["entries"] if e["path"] == str(worktree))
    assert entry["action"] == "removed", entry
    with tarfile.open(mine / "task-run" / "dirty-lane" / retention.SALVAGE_TAR) as tar:
        names = set(tar.getnames())
    assert {"new.txt", *awkward} <= names
    record = json.loads((mine / "task-run" / "dirty-lane" / retention.SALVAGE_RECORD).read_text(encoding="utf-8"))
    assert sorted(record["untracked"]) == sorted(["new.txt", *awkward])


def test_a_salvage_whose_archive_misses_a_path_keeps_the_worktree(tmp_path: Path, monkeypatch) -> None:
    now = time.time()
    mine, repo = _tree(tmp_path, now=now)
    real = retention.Sweep._git

    def git(cwd: Path, *args: str):
        result = real(cwd, *args)
        if args[:2] == ("status", "--porcelain"):
            # git names a path that is not on disk: the salvage must not claim it.
            result = subprocess.CompletedProcess(args, 0, result.stdout + "?? ghost.txt\0", "")
        return result

    report = retention.sweep_runtime_root(repo, key_root=mine, now=now, git=git)

    entry = next(e for e in report["entries"] if e["path"].endswith("dirty-lane/worktree"))
    assert entry["action"] == "skipped"
    assert "ghost.txt" in entry["reason"]
    assert (mine / "task-run" / "dirty-lane" / "worktree" / "a.py").exists()


def test_porcelain_z_entries_drop_the_old_name_of_a_rename() -> None:
    stdout = "R  new.txt\0old.txt\0?? loose.txt\0 M a.py\0"
    assert retention._porcelain_z_entries(stdout) == ["R  new.txt", "?? loose.txt", " M a.py"]


def test_a_salvage_archive_that_lost_a_member_keeps_the_worktree(tmp_path: Path, monkeypatch) -> None:
    now = time.time()
    mine, repo = _tree(tmp_path, now=now)
    real_getnames = tarfile.TarFile.getnames

    def lossy(self):
        return real_getnames(self)[1:]

    monkeypatch.setattr(tarfile.TarFile, "getnames", lossy)

    report = retention.sweep_runtime_root(repo, key_root=mine, now=now)

    entry = next(e for e in report["entries"] if e["path"].endswith("dirty-lane/worktree"))
    assert entry["action"] == "skipped"
    assert "archive is missing" in entry["reason"]
    assert (mine / "task-run" / "dirty-lane" / "worktree" / "a.py").exists()
