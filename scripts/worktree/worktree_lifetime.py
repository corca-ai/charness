"""Lifetime for git worktrees charness created.

Identity, before any rule:

- A worktree is **ephemeral** when charness wrote ``charness-lifetime`` with
  ``kind: ephemeral``, or when it is unlabeled (raw ``git worktree add``) and
  the path is a throwaway. ``kind: owned`` and unlabeled feature paths are
  never auto-removed. Unlabeled throwaways idle past
  ``UNLABELED_IDLE_DAYS`` are residue even if they predate this marker.
- Kind is ``owned`` when the caller asked for it; ``ephemeral`` when the
  caller asked for it, or when the path is a throwaway (temp, pytest, or a
  ``charness/runtime`` tree). Everything else is owned. Feature paths such as
  ``../feature-worktree`` stay owned without a flag.
- A live ``pid`` is recorded only for a task-run lane path
  (``.../task-run/<id>/worktree``). That process owns the lease: a clean
  interpreter exit unregisters it (dirty trees stay for the salvage sweep).
  SIGTERM/SIGKILL leave a dead pid, which the next ``create`` or
  ``audit --prune`` unregisters. Create CLI ephemerals store no pid; the cap
  is their balloon brake.
- The cap is 32 because that is the host live-children ceiling; the 33rd
  ephemeral is residue, not concurrency. Live-pid lanes are never evicted to
  make room. Cap eviction uses ``git worktree remove --force``.

``create`` reclaims expired ephemerals and enforces the cap before ``git
worktree add``. ``audit --prune`` reclaims expired ephemerals, then prunes
missing directories. The runtime sweep unregisters a linked worktree with
``git worktree remove`` rather than only ``rmtree``. Doctor stays read-only.
"""

from __future__ import annotations

import atexit
import json
import os
import shutil
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.core.git_checkout import git_dir_at, layout_from_files  # noqa: E402
from scripts.core.subprocess_guard import run_process  # noqa: E402

KIND_EPHEMERAL = "ephemeral"
KIND_OWNED = "owned"
MARKER_NAME = "charness-lifetime"
# Host live-children cap (workflow parallel panel). Beyond this, an ephemeral
# worktree is residue, not a concurrent lane.
EPHEMERAL_CAP = 32
# Same basis as runtime_root_retention.ACTIVE_WINDOW_DAYS: a live pytest or
# agent session may still be using an unlabeled throwaway; older is residue.
UNLABELED_IDLE_DAYS = 1.0

_EXIT_LEASES: list[tuple[Path, Path]] = []
_ATEXIT_INSTALLED = False


def path_is_runtime_tree(path: Path) -> bool:
    parts = path.resolve().parts
    return any(
        parts[index] == "charness" and parts[index + 1] == "runtime"
        for index in range(len(parts) - 1)
    )


def path_is_task_run_lane(path: Path) -> bool:
    parts = path.resolve().parts
    return len(parts) >= 3 and parts[-1] == "worktree" and parts[-3] == "task-run"


def path_is_throwaway(path: Path) -> bool:
    resolved = path.resolve()
    if path_is_runtime_tree(resolved):
        return True
    parts = resolved.parts
    if any(part.startswith("pytest-of-") or part == "pytest-tmp" for part in parts):
        return True
    if "charness-captures" in parts:
        return True
    if ".claude" in parts and "worktrees" in parts:
        return True
    posix = resolved.as_posix()
    if "/.cache/tmp/" in posix or posix.endswith("/.cache/tmp"):
        return True
    roots = [Path(tempfile.gettempdir())]
    for name in ("TMPDIR", "TMP", "TEMP"):
        raw = os.environ.get(name)
        if raw:
            roots.append(Path(raw))
    roots.extend((Path("/tmp"), Path("/var/tmp")))
    for root in roots:
        try:
            base = root.resolve()
        except OSError:
            continue
        if resolved == base or base in resolved.parents:
            return True
    return False


def resolve_kind(path: Path, *, ephemeral: bool = False, owned: bool = False) -> str:
    if owned:
        return KIND_OWNED
    if ephemeral or path_is_throwaway(path):
        return KIND_EPHEMERAL
    return KIND_OWNED


def pid_is_live(pid: int | None) -> bool:
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _marker_path(worktree: Path) -> Path | None:
    git_dir = git_dir_at(worktree)
    if git_dir is None:
        return None
    try:
        git_dir = git_dir.resolve()
    except OSError:
        return None
    if not git_dir.is_dir() or git_dir.name == ".git":
        return None
    return git_dir / MARKER_NAME


def _common_dir(repo_root: Path) -> Path | None:
    layout = layout_from_files(repo_root)
    return None if layout is None else layout.common_dir


def read_lifetime(worktree: Path) -> dict[str, Any] | None:
    marker = _marker_path(worktree)
    if marker is None or not marker.is_file():
        return None
    try:
        payload = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def write_lifetime(
    worktree: Path,
    *,
    kind: str,
    pid: int | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    marker = _marker_path(worktree)
    if marker is None:
        raise FileNotFoundError(f"no linked-worktree admin dir for {worktree}")
    record = {
        "kind": kind,
        "path": str(worktree.resolve()),
        "created_at": created_at or datetime.now(timezone.utc).isoformat(),
        "pid": pid,
    }
    marker.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


def list_lifetime_records(repo_root: Path) -> list[dict[str, Any]]:
    common = _common_dir(repo_root)
    if common is None:
        return []
    root = common / "worktrees"
    if not root.is_dir():
        return []
    records: list[dict[str, Any]] = []
    for admin in sorted(root.iterdir()):
        marker = admin / MARKER_NAME
        if not marker.is_file():
            continue
        try:
            payload = json.loads(marker.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(payload, dict):
            continue
        payload = dict(payload)
        payload["_admin"] = str(admin)
        records.append(payload)
    return records


def _git_dir_cmd(common: Path, *args: str) -> Any:
    cwd = common.parent if common.name == ".git" else common
    return run_process(
        ["git", "--git-dir", str(common), *args],
        cwd=cwd,
        timeout_seconds=None,
    )


def unregister(path: Path, *, repo_root: Path | None = None) -> dict[str, Any]:
    """Drop a linked worktree with ``git worktree remove``, then prune if needed."""
    target = path.resolve()
    common = None
    if target.exists():
        layout = layout_from_files(target)
        common = None if layout is None else layout.common_dir
    if common is None and repo_root is not None:
        common = _common_dir(repo_root)
    if common is not None:
        result = _git_dir_cmd(common, "worktree", "remove", "--force", str(target))
        if result.returncode == 0:
            return {"removed": True, "via": "git-worktree-remove", "path": str(target)}
        _git_dir_cmd(common, "worktree", "prune")
        if not target.exists():
            return {"removed": True, "via": "git-worktree-prune", "path": str(target)}
    if target.exists():
        shutil.rmtree(target, ignore_errors=True)
        if common is not None:
            _git_dir_cmd(common, "worktree", "prune")
    return {"removed": not target.exists(), "via": "rmtree-prune", "path": str(target)}


def _worktree_is_dirty(path: Path) -> bool:
    if not path.exists():
        return False
    result = run_process(
        ["git", "status", "--porcelain", "-z", "--untracked-files=all"],
        cwd=path,
        timeout_seconds=None,
    )
    return result.returncode == 0 and bool(result.stdout)


def _record_path(record: dict[str, Any]) -> Path | None:
    raw = record.get("path")
    if not isinstance(raw, str) or not raw:
        return None
    return Path(raw)


def _created_stamp(record: dict[str, Any]) -> str:
    raw = record.get("created_at")
    return raw if isinstance(raw, str) else ""


def _primary_path(repo_root: Path) -> Path:
    layout = layout_from_files(repo_root)
    if layout is not None and layout.common_dir.name == ".git":
        return layout.common_dir.parent.resolve()
    return repo_root.resolve()


def _registered_worktrees(repo_root: Path) -> list[dict[str, Any]]:
    proc = run_process(
        ["git", "worktree", "list", "--porcelain"],
        cwd=repo_root,
        timeout_seconds=None,
    )
    if proc.returncode != 0:
        return []
    entries: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    for raw in proc.stdout.splitlines():
        if not raw:
            if current:
                entries.append(current)
                current = {}
            continue
        if raw.startswith("worktree "):
            if current:
                entries.append(current)
            current = {"path": Path(raw[len("worktree ") :])}
        elif raw == "locked" or raw.startswith("locked "):
            current["locked"] = True
        elif raw == "prunable" or raw.startswith("prunable "):
            current["prunable"] = True
    if current:
        entries.append(current)
    return entries


def _is_idle(path: Path, *, now: float, idle_days: float) -> bool:
    if not path.exists():
        return True
    try:
        age = now - path.stat().st_mtime
    except OSError:
        return True
    return age >= idle_days * 86400


def reclaim_expired(
    repo_root: Path, *, now: float | None = None
) -> list[dict[str, Any]]:
    """Unregister dead-pid ephemerals and idle unlabeled throwaways."""
    moment = time.time() if now is None else now
    actions: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for record in list_lifetime_records(repo_root):
        if record.get("kind") != KIND_EPHEMERAL:
            continue
        pid = record.get("pid")
        if pid is None or pid_is_live(pid if isinstance(pid, int) else None):
            continue
        target = _record_path(record)
        if target is None:
            continue
        result = unregister(target, repo_root=repo_root)
        result["reason"] = "ephemeral pid is dead"
        actions.append(result)
        seen.add(target.resolve())
    primary = _primary_path(repo_root)
    for entry in _registered_worktrees(repo_root):
        path = Path(entry["path"]).resolve()
        if path in seen or path == primary or entry.get("locked"):
            continue
        record = read_lifetime(path) if path.exists() else None
        if record is not None:
            continue
        if not path_is_throwaway(path):
            continue
        if not entry.get("prunable") and not _is_idle(
            path, now=moment, idle_days=UNLABELED_IDLE_DAYS
        ):
            continue
        result = unregister(path, repo_root=repo_root)
        result["reason"] = "unlabeled throwaway is idle residue"
        actions.append(result)
    return actions


def enforce_cap(
    repo_root: Path, *, cap: int | None = None, reserve: int = 1
) -> dict[str, Any]:
    """Evict oldest no-live-pid ephemerals until ``reserve`` slots are free.

    Live-pid lanes are never evicted. If they alone fill the cap, creation
    must refuse rather than kill running work.
    """
    if cap is None:
        cap = EPHEMERAL_CAP
    expired = reclaim_expired(repo_root)
    evicted: list[dict[str, Any]] = []
    while True:
        remaining = [
            record
            for record in list_lifetime_records(repo_root)
            if record.get("kind") == KIND_EPHEMERAL
        ]
        if len(remaining) + reserve <= cap:
            return {
                "expired": expired,
                "evicted": evicted,
                "remaining": len(remaining),
                "refused": False,
            }
        eligible = [
            record
            for record in remaining
            if not pid_is_live(record.get("pid") if isinstance(record.get("pid"), int) else None)
        ]
        if not eligible:
            return {
                "expired": expired,
                "evicted": evicted,
                "remaining": len(remaining),
                "refused": True,
            }
        oldest = min(eligible, key=_created_stamp)
        target = _record_path(oldest)
        if target is None:
            break
        result = unregister(target, repo_root=repo_root)
        result["reason"] = f"ephemeral cap {cap}"
        evicted.append(result)
        if not result.get("removed"):
            break
    return {
        "expired": expired,
        "evicted": evicted,
        "remaining": len(
            [r for r in list_lifetime_records(repo_root) if r.get("kind") == KIND_EPHEMERAL]
        ),
        "refused": True,
    }


def prepare_create(
    repo_root: Path, *, kind: str, cap: int | None = None
) -> dict[str, Any]:
    if cap is None:
        cap = EPHEMERAL_CAP
    if kind != KIND_EPHEMERAL:
        expired = reclaim_expired(repo_root)
        return {
            "expired": expired,
            "evicted": [],
            "remaining": len(
                [r for r in list_lifetime_records(repo_root) if r.get("kind") == KIND_EPHEMERAL]
            ),
            "refused": False,
        }
    return enforce_cap(repo_root, cap=cap, reserve=1)


def bind_created(worktree: Path, *, kind: str) -> dict[str, Any]:
    pid = os.getpid() if kind == KIND_EPHEMERAL and path_is_task_run_lane(worktree) else None
    record = write_lifetime(worktree, kind=kind, pid=pid)
    if pid == os.getpid():
        _register_exit_remove(worktree)
    return record


def _register_exit_remove(worktree: Path) -> None:
    global _ATEXIT_INSTALLED
    layout = layout_from_files(worktree)
    if layout is None:
        return
    repo_root = layout.common_dir.parent if layout.common_dir.name == ".git" else layout.common_dir
    lease = (repo_root.resolve(), worktree.resolve())
    if lease not in _EXIT_LEASES:
        _EXIT_LEASES.append(lease)
    if not _ATEXIT_INSTALLED:
        atexit.register(_reclaim_exit_leases)
        _ATEXIT_INSTALLED = True


def _reclaim_exit_leases() -> None:
    while _EXIT_LEASES:
        repo_root, worktree = _EXIT_LEASES.pop()
        if _worktree_is_dirty(worktree):
            continue
        unregister(worktree, repo_root=repo_root)
