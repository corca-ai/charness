#!/usr/bin/env python3
"""Where a standing pytest run's scratch tree lives, and what survives it.

SPLIT FROM `run_standing_pytest` (S6, 2026-08-15) when that file crossed its
length cap. Extracted as a CONCEPT rather than spilled to dodge the cap, which
`check_code_lengths` names as the wrong move: this module answers one question
the runner merely consumes the answer to -- where the basetemp goes, whether one
is still live, and which failed roots are kept for diagnosis. It has its own
dedicated tests in `tests/quality_gates/test_retention_refusal_coverage.py`,
which is what makes it a seam rather than a leftover.

The runner keeps the pytest COMMAND (targets, xdist, scheduling) and the RUN
itself (monitored child, run record). Nothing here spawns pytest or reads the
runner's arguments; the dependency points one way.
"""

from __future__ import annotations

import contextlib
import fcntl
import hashlib
import os
import re
import shutil
import sys
import time
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

try:
    from scripts.core.subprocess_guard import run_process
except ModuleNotFoundError:  # executed directly from scripts/
    from scripts.core.subprocess_guard import run_process

FAILED_BASETEMP_KEEP = 3
#: A run root carrying NO marker is one whose runner died before it could either
#: delete a pass or mark a failure, so nothing downstream will ever name it. Only
#: the newest is plausibly the corpse a live session is still looking at; the rest
#: are the 5.1 GB this repo's own key had leaked by 2026-09-03.
ORPHAN_BASETEMP_KEEP = 1
#: A key directory predating `REPO_ROOT_MARKER` (2026-09-03) names no repo root to
#: test for existence, so age is the only evidence it is dead. Two weeks is longer
#: than any plausible pause in an active worktree's standing-pytest runs.
LEGACY_KEY_MAX_AGE_DAYS = 14
REPO_ROOT_MARKER = ".charness-repo-root"
_RUN_BASETEMP_NAME = re.compile(r"^charness-run-[0-9]+$")
_FAILED_BASETEMP_MARKER = ".charness-failed-run"
_KEPT_BASETEMP_MARKER = ".charness-explicitly-kept-run"
_KEY_ROOT_NAME = "pytest-tmp"
_RUN_GLOB = "pytest-of-*/charness-run-*"
_RUN_LOCK_GLOB = "pytest-of-*/.charness-run-*.lock"


def repo_tmp_key(repo_root: Path) -> str:
    return hashlib.sha256(str(repo_root).encode()).hexdigest()[:12]


def default_temp_root(repo_root: Path, env: dict[str, str] | None = None) -> Path:
    env = os.environ if env is None else env
    if env.get("PYTEST_DEBUG_TEMPROOT"):
        return Path(env["PYTEST_DEBUG_TEMPROOT"])
    if env.get("CHARNESS_RUNTIME_ROOT"):
        return Path(env["CHARNESS_RUNTIME_ROOT"]) / "pytest-tmp" / repo_tmp_key(repo_root)
    cache_root = Path(env.get("XDG_CACHE_HOME") or Path(env.get("HOME", "/tmp")) / ".cache")
    return cache_root / "charness" / "pytest-tmp" / repo_tmp_key(repo_root)


def default_pytest_cache_dir(repo_root: Path, env: dict[str, str] | None = None) -> Path:
    env = os.environ if env is None else env
    if env.get("CHARNESS_PYTEST_CACHE_DIR"):
        return Path(env["CHARNESS_PYTEST_CACHE_DIR"])
    if env.get("CHARNESS_RUNTIME_ROOT"):
        return Path(env["CHARNESS_RUNTIME_ROOT"]) / "pytest-cache"
    if env.get("PYTEST_DEBUG_TEMPROOT"):
        return Path(env["PYTEST_DEBUG_TEMPROOT"]) / "pytest-cache"
    cache_root = Path(env.get("XDG_CACHE_HOME") or Path(env.get("HOME", "/tmp")) / ".cache")
    return cache_root / "charness" / "pytest-cache" / repo_tmp_key(repo_root)


def ensure_external_temp_root(repo_root: Path, temp_root: Path) -> None:
    resolved_repo = repo_root.resolve()
    resolved_temp = temp_root.resolve()
    try:
        resolved_temp.relative_to(resolved_repo)
    except ValueError:
        return
    raise SystemExit(
        "standing-pytest: pytest temp root "
        f"{str(temp_root)!r} is inside the repo {str(repo_root)!r}; point "
        "XDG_CACHE_HOME or PYTEST_DEBUG_TEMPROOT outside the repo"
    )


def default_basetemp(repo_root: Path, env: dict[str, str] | None = None) -> Path:
    temp_root = default_temp_root(repo_root, env)
    ensure_external_temp_root(repo_root, temp_root)
    user = (
        run_process(["id", "-un"], cwd=repo_root, timeout_seconds=None).stdout.strip() or "unknown"
    )
    # The leaf MUST NOT start with "pytest-". This basetemp lives under the shared
    # PYTEST_DEBUG_TEMPROOT/pytest-of-<user> rootdir, and nested pytest runs spawned
    # by tests inherit PYTEST_DEBUG_TEMPROOT and run pytest's numbered-dir cleanup
    # (make_numbered_dir_with_cleanup, prefix "pytest-") over that same rootdir at
    # process exit. pytest's explicit --basetemp branch creates this dir WITHOUT a
    # cleanup lock file, so a "pytest-*" name would be an unlocked deletion candidate
    # and a nested run's exit-time cleanup could rename+remove it — and every live
    # xdist worker's popen-gw* subdir — mid-run, producing mass FileNotFoundError in
    # tmp_path setup. A non-"pytest-" prefix is invisible to that cleanup glob.
    return temp_root / f"pytest-of-{user}" / f"charness-run-{time.time_ns()}"


def _failed_basetemp_keep(env: dict[str, str] | None = None) -> int:
    env = os.environ if env is None else env
    raw = env.get("CHARNESS_PYTEST_FAILED_BASETEMP_KEEP")
    if raw is None:
        return FAILED_BASETEMP_KEEP
    try:
        keep = int(raw)
    except ValueError:
        keep = 0
    if keep >= 1:
        return keep
    print(
        "standing-pytest: ignoring invalid CHARNESS_PYTEST_FAILED_BASETEMP_KEEP="
        f"{raw!r}; expected a positive integer, using {FAILED_BASETEMP_KEEP}",
        file=sys.stderr,
    )
    return FAILED_BASETEMP_KEEP


def _basetemp_lock_path(basetemp: Path) -> Path:
    return basetemp.parent / f".{basetemp.name}.lock"


@contextlib.contextmanager
def _hold_basetemp_lock(basetemp: Path):
    """Hold a sibling-visible liveness lock for one runner-owned basetemp."""
    lock_path = _basetemp_lock_path(basetemp)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    lock_path.unlink(missing_ok=True)


def _basetemp_is_active(basetemp: Path) -> bool:
    lock_path = _basetemp_lock_path(basetemp)
    try:
        with lock_path.open("a+", encoding="utf-8") as handle:
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return True
            finally:
                try:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
                except OSError:
                    pass
    except OSError:
        return True
    lock_path.unlink(missing_ok=True)
    return False


def _mark_basetemp(basetemp: Path, marker: str) -> None:
    try:
        (basetemp / marker).write_text(str(time.time_ns()), encoding="utf-8")
    except OSError:
        pass


def _failed_at(basetemp: Path) -> int:
    try:
        return (basetemp / _FAILED_BASETEMP_MARKER).stat().st_mtime_ns
    except OSError:
        return 0


def prune_failed_basetemps(
    parent: Path,
    *,
    current_failed: Path | None,
    keep: int,
) -> list[Path]:
    """Remove old marked failures while preserving active, explicit-kept, and legacy roots."""
    try:
        siblings = [
            path
            for path in parent.iterdir()
            if path.is_dir()
            and _RUN_BASETEMP_NAME.fullmatch(path.name)
            and path != current_failed
            and (path / _FAILED_BASETEMP_MARKER).is_file()
            and not (path / _KEPT_BASETEMP_MARKER).exists()
        ]
    except OSError:
        return []
    newest_other_count = max(0, keep - (1 if current_failed is not None else 0))
    siblings.sort(key=_failed_at, reverse=True)
    removed: list[Path] = []
    for stale in siblings[newest_other_count:]:
        if _basetemp_is_active(stale):
            continue
        try:
            shutil.rmtree(stale)
        except OSError:
            continue
        removed.append(stale)
    return removed


def _run_started_at(basetemp: Path) -> int:
    """When this run began, from the nanosecond `default_basetemp` stamped into the name."""
    suffix = basetemp.name.rsplit("-", 1)[-1]
    if suffix.isdigit():
        return int(suffix)
    try:
        return basetemp.stat().st_mtime_ns
    except OSError:
        return 0


def prune_orphan_basetemps(
    parent: Path,
    *,
    current: Path | None,
    keep: int,
) -> list[Path]:
    """Bound UNMARKED run roots: the residue of a runner killed before its own cleanup.

    `prune_failed_basetemps` deliberately preserves these -- it only considers roots
    carrying the failed marker -- and a passing run deletes its own root, so nothing
    else in this module ever reclaims them. They are the largest single occupant of the
    cache root; the ONE surviving orphan keeps a just-killed run diagnosable.
    """
    try:
        siblings = [
            path
            for path in parent.iterdir()
            if path.is_dir()
            and _RUN_BASETEMP_NAME.fullmatch(path.name)
            and path != current
            and not (path / _FAILED_BASETEMP_MARKER).exists()
            and not (path / _KEPT_BASETEMP_MARKER).exists()
        ]
    except OSError:
        return []
    siblings.sort(key=_run_started_at, reverse=True)
    removed: list[Path] = []
    for stale in siblings[max(0, keep) :]:
        if _basetemp_is_active(stale):
            continue
        try:
            shutil.rmtree(stale)
        except OSError:
            continue
        removed.append(stale)
    return removed


def record_repo_root_marker(temp_root: Path, repo_root: Path) -> None:
    """Name the repo this key hashes, so a later run can tell a dead key from a quiet one."""
    try:
        temp_root.mkdir(parents=True, exist_ok=True)
        (temp_root / REPO_ROOT_MARKER).write_text(f"{repo_root}\n", encoding="utf-8")
    except OSError:
        pass


def _key_repo_root(key: Path) -> str | None:
    try:
        return (key / REPO_ROOT_MARKER).read_text(encoding="utf-8").strip() or None
    except OSError:
        return None


def _key_is_active(key: Path) -> bool:
    """True while any run under this key still holds its liveness lock."""
    try:
        candidates = set(key.glob(_RUN_GLOB))
        for lock in key.glob(_RUN_LOCK_GLOB):
            candidates.add(lock.with_name(lock.name[1:].removesuffix(".lock")))
    except OSError:
        return True
    return any(_basetemp_is_active(path) for path in candidates)


def _shallow_entry_newer_than(root: Path, cutoff: float) -> bool:
    """The cheap half of the liveness question, asked before any deep walk.

    A run creates and removes its root directly under `<key>/pytest-of-<user>/`, so that
    directory's own mtime moves on every run. Answering from three stats keeps a live
    multi-gigabyte key off the `os.walk` path this runs on EVERY standing pytest run.
    """
    stack = [root]
    for _ in range(2):
        children: list[Path] = []
        for path in stack:
            try:
                if path.stat().st_mtime > cutoff:
                    return True
                children.extend(path.iterdir())
            except OSError:
                continue
        stack = children
    return any(_safe_mtime(path) > cutoff for path in stack)


def _safe_mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def _has_entry_newer_than(root: Path, cutoff: float) -> bool:
    """Walk until the first entry proves recent use; a live key exits early, a dead one does not."""
    if _shallow_entry_newer_than(root, cutoff):
        return True
    for parent, dirs, files in os.walk(root):
        for name in (*dirs, *files):
            try:
                if os.lstat(os.path.join(parent, name)).st_mtime > cutoff:
                    return True
            except OSError:
                continue
    try:
        return root.stat().st_mtime > cutoff
    except OSError:
        return True


def _tree_size_bytes(root: Path) -> int:
    total = 0
    for parent, _dirs, files in os.walk(root):
        for name in files:
            try:
                total += os.lstat(os.path.join(parent, name)).st_size
            except OSError:
                continue
    return total


def _key_is_dead(key: Path, cutoff: float) -> bool:
    recorded = _key_repo_root(key)
    if recorded is not None:
        return not Path(recorded).exists()
    return not _has_entry_newer_than(key, cutoff)


def prune_dead_repo_keys(
    temp_root: Path,
    *,
    max_age_days: float = LEGACY_KEY_MAX_AGE_DAYS,
    now: float | None = None,
    log=None,
) -> list[Path]:
    """Remove sibling key directories whose repo is gone, keeping this run's own key.

    One key per hashed repo root means every worktree, clone, and task-run lane this
    machine ever tested leaves one behind, and nothing before this reclaimed a key
    after its repo was deleted.
    """
    key_root = temp_root.parent
    if key_root.name != _KEY_ROOT_NAME:
        return []
    cutoff = (time.time() if now is None else now) - max_age_days * 86400
    try:
        siblings = sorted(key_root.iterdir())
    except OSError:
        return []
    mine = temp_root.resolve()
    removed: list[Path] = []
    for key in siblings:
        if key.is_symlink() or not key.is_dir() or key.resolve() == mine:
            continue
        if not _key_is_dead(key, cutoff) or _key_is_active(key):
            continue
        freed = _tree_size_bytes(key)
        try:
            shutil.rmtree(key)
        except OSError:
            continue
        removed.append(key)
        if log is not None:
            log(f"removed dead pytest temp key {key} ({freed // (1024 * 1024)} MiB)")
    return removed


def prepare_repo_key(repo_root: Path, temp_root: Path, *, log=None) -> list[Path]:
    """Claim this run's key by name, then reclaim the keys whose repos are gone."""
    record_repo_root_marker(temp_root, repo_root)
    return prune_dead_repo_keys(temp_root, log=log)
