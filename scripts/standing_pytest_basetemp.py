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

try:
    from scripts.core.subprocess_guard import run_process
except ModuleNotFoundError:  # executed directly from scripts/
    from scripts.core.subprocess_guard import run_process

FAILED_BASETEMP_KEEP = 3
_RUN_BASETEMP_NAME = re.compile(r"^charness-run-[0-9]+$")
_FAILED_BASETEMP_MARKER = ".charness-failed-run"
_KEPT_BASETEMP_MARKER = ".charness-explicitly-kept-run"


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
