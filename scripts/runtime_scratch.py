#!/usr/bin/env python3
"""Own short-lived Charness scratch roots and reclaim only what they own.

The process environment already routes ordinary tool caches to the external
runtime key.  This module gives directory-producing carriers one stronger
contract: a per-run root, an owner receipt, an active lock, and a lifecycle
that can be inspected without scanning or guessing about ``/tmp``.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
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

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows has no fcntl
    fcntl = None

try:
    from scripts.runtime_bootstrap import import_repo_module, runtime_root
except ModuleNotFoundError:  # direct ``python scripts/runtime_scratch.py``
    _root = Path(__file__).resolve().parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    from scripts.runtime_bootstrap import import_repo_module, runtime_root

_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _guard.run_process


SCHEMA = "charness.runtime-scratch-owner/v1"
SCRATCH_DIR_NAME = "scratch"
OWNER_RECEIPT_NAME = ".charness-owner.json"
OWNER_LOCK_NAME = ".charness-owner.lock"
DEFAULT_RETENTION_SECONDS = 24 * 60 * 60
RETENTION_CLASSES = frozenset({"scratch", "retained-evidence"})
TERMINAL_STATES = frozenset({"succeeded", "failed", "cancelled", "timed-out", "retained"})
_RECEIPT_CORE_FIELDS = frozenset(
    {
        "schema",
        "owner",
        "producer",
        "repo_root",
        "repo_identity",
        "run_id",
        "pid",
        "created_at",
        "updated_at",
        "state",
        "retention",
        "expires_at",
    }
)
_TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class ScratchError(RuntimeError):
    """Raised when an owner boundary cannot be established safely."""


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _token(value: str, *, label: str) -> str:
    if not isinstance(value, str) or not _TOKEN.fullmatch(value):
        raise ScratchError(f"{label} must be a simple owner token: {value!r}")
    return value


def _repo_identity(repo_root: Path) -> str:
    return hashlib.sha256(str(repo_root.resolve()).encode("utf-8")).hexdigest()[:16]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def _read_owner(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _tree_inventory(root: Path, *, max_entries: int) -> tuple[int, int, bool]:
    entries = 0
    size = 0
    truncated = False
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            children = list(os.scandir(current))
        except OSError:
            continue
        for entry in children:
            entries += 1
            if entries > max_entries:
                return entries, size, True
            try:
                if entry.is_symlink():
                    continue
                if entry.is_dir(follow_symlinks=False):
                    stack.append(Path(entry.path))
                elif entry.is_file(follow_symlinks=False):
                    size += entry.stat(follow_symlinks=False).st_size
            except OSError:
                truncated = True
    return entries, size, truncated


def _lock_is_active(lock_path: Path) -> bool:
    if not lock_path.is_file():
        return False
    try:
        handle = lock_path.open("a+")
    except OSError:
        return True
    try:
        if fcntl is None:
            return False
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (BlockingIOError, OSError):
            return True
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        return False
    finally:
        handle.close()


def _pid_is_alive(value: object) -> bool:
    if not isinstance(value, int) or value <= 0:
        return False
    try:
        os.kill(value, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _registered_worktrees(repo_root: Path) -> list[Path]:
    try:
        result = run_process(
            ["git", "worktree", "list", "--porcelain"],
            cwd=repo_root,
            timeout_seconds=10,
        )
    except OSError as exc:
        raise ScratchError(f"cannot inspect registered worktrees: {exc}") from exc
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "git worktree list failed"
        raise ScratchError(f"cannot inspect registered worktrees: {detail}")
    paths: list[Path] = []
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            paths.append(Path(line.removeprefix("worktree ")).resolve())
    return paths


def _contains_path(parent: Path, child: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def _rmtree_writable(path: Path) -> None:
    """Remove owned trees even when a read-only worker input was materialized."""
    for parent, dirs, files in os.walk(path):
        for name in (*dirs, *files):
            target = os.path.join(parent, name)
            if not os.path.islink(target):
                os.chmod(target, 0o700 if os.path.isdir(target) else 0o600)
        os.chmod(parent, 0o700)
    shutil.rmtree(path)


class OwnedScratch:
    """A single producer/run directory with a receipt and a held owner lock."""

    def __init__(
        self,
        repo_root: str | Path,
        producer: str,
        *,
        run_id: str | None = None,
        retention: str = "scratch",
        runtime_root_path: str | Path | None = None,
        retention_seconds: int = DEFAULT_RETENTION_SECONDS,
    ) -> None:
        self.repo_root = Path(repo_root).expanduser().resolve()
        self.producer = _token(producer, label="producer")
        self.run_id = _token(run_id or f"{os.getpid()}-{time.time_ns()}", label="run_id")
        if retention not in RETENTION_CLASSES:
            raise ScratchError(f"unknown retention class: {retention!r}")
        if retention_seconds <= 0:
            raise ScratchError("retention_seconds must be positive")
        base = (
            Path(runtime_root_path).expanduser().resolve()
            if runtime_root_path is not None
            else runtime_root(self.repo_root)
        )
        self.runtime_root = base
        self.path = base / SCRATCH_DIR_NAME / self.producer / self.run_id
        self.receipt_path = self.path / OWNER_RECEIPT_NAME
        self.lock_path = self.path / OWNER_LOCK_NAME
        self.retention = retention
        self.retention_seconds = retention_seconds
        self._lock: Any = None
        self._retained = retention == "retained-evidence"
        self._promoted = False
        self._opened = False

    def _receipt(self, *, state: str, **extra: Any) -> dict[str, Any]:
        now = _utc_now()
        payload: dict[str, Any] = {
            "schema": SCHEMA,
            "owner": "charness",
            "producer": self.producer,
            "repo_root": str(self.repo_root),
            "repo_identity": _repo_identity(self.repo_root),
            "run_id": self.run_id,
            "pid": os.getpid(),
            "created_at": getattr(self, "created_at", now),
            "updated_at": _iso(now),
            "state": state,
            "retention": self.retention,
            "expires_at": _iso(now + timedelta(seconds=self.retention_seconds)),
        }
        payload.update(extra)
        return payload

    def _receipt_preserving(self, *, state: str, **extra: Any) -> dict[str, Any]:
        """Change lifecycle fields without dropping recovery metadata.

        Recovery commands, packet identities, and promotion diagnostics are
        written before owner close.  Rebuilding a terminal receipt from only
        the fixed owner fields used to erase those fields at the exact point
        where retained evidence became useful to a retry.
        """
        existing = _read_owner(self.receipt_path) or {}
        preserved = {
            key: value
            for key, value in existing.items()
            if key not in _RECEIPT_CORE_FIELDS
        }
        preserved.update(extra)
        return self._receipt(state=state, **preserved)

    def open(self) -> Path:
        if self._opened:
            return self.path
        if self.path.exists():
            raise ScratchError(f"scratch run already exists: {self.path}")
        self.path.mkdir(parents=True)
        self.created_at = _iso(_utc_now())
        try:
            self._lock = self.lock_path.open("a+")
            if fcntl is not None:
                fcntl.flock(self._lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self._lock.write(f"pid={os.getpid()}\n")
            self._lock.flush()
            _write_json(self.receipt_path, self._receipt(state="active"))
        except BaseException as exc:
            # Establishing an owner is one transaction.  If the first receipt
            # write fails, leave a typed retained receipt so the bytes remain
            # inspectable and retryable; do not strand an unreceipted root.
            self._retained = True
            self.retention = "retained-evidence"
            try:
                _write_json(
                    self.receipt_path,
                    self._receipt(state="failed", owner_open_error=str(exc)),
                )
            except BaseException:
                # No caller can safely identify this root without a receipt,
                # and open() has not returned a payload path yet.  Remove only
                # this empty, newly-created owner root rather than leaving an
                # unknown directory for GC to guess about.
                self._close_lock()
                self._opened = False
                shutil.rmtree(self.path, ignore_errors=True)
                raise
            self._opened = True
            self._close_lock()
            raise
        self._opened = True
        return self.path

    def __enter__(self) -> Path:
        return self.open()

    def retain(self) -> None:
        if not self._opened:
            raise ScratchError("cannot retain a scratch root before it is opened")
        self._retained = True
        self.retention = "retained-evidence"
        _write_json(self.receipt_path, self._receipt_preserving(state="retained"))

    def retain_with(self, **extra: Any) -> None:
        """Retain a failed run with the identity needed for a later recovery."""
        if not self._opened:
            raise ScratchError("cannot retain a scratch root before it is opened")
        self._retained = True
        self.retention = "retained-evidence"
        _write_json(self.receipt_path, self._receipt_preserving(state="retained", **extra))

    def retain_failed_promotion(self, **extra: Any) -> None:
        """Keep the source when a caller cannot verify durable promotion."""
        self._promoted = False
        self.retain_with(**extra)

    def update(self, **extra: Any) -> None:
        """Persist active-run metadata needed for crash recovery."""
        if not self._opened:
            raise ScratchError("cannot update a scratch root before it is opened")
        _write_json(self.receipt_path, self._receipt_preserving(state="active", **extra))

    def reopen_existing(self) -> Path:
        """Acquire an abandoned retained root for an identity-checked retry."""
        if self._opened:
            return self.path
        owner = _read_owner(self.receipt_path)
        if owner is None or owner.get("schema") != SCHEMA:
            raise ScratchError(f"cannot reopen an unknown scratch owner: {self.path}")
        if owner.get("repo_identity") != _repo_identity(self.repo_root):
            raise ScratchError("refusing to reopen scratch owned by another repository")
        if owner.get("producer") != self.producer or owner.get("run_id") != self.run_id:
            raise ScratchError("refusing to reopen scratch with a different owner identity")
        if owner.get("retention") != "retained-evidence" or owner.get("state") not in {
            "retained",
            # Registry recovery deliberately records an abandoned active owner
            # as failed.  Failed retained evidence is still a supported retry
            # input; treating only the happy-path terminal state as reopenable
            # strands exactly the bytes recovery promised to preserve.
            "failed",
        }:
            raise ScratchError(
                "scratch root is not retained retry evidence: "
                f"state={owner.get('state')!r}, retention={owner.get('retention')!r}"
            )
        if _pid_is_alive(owner.get("pid")):
            raise ScratchError("refusing to reopen scratch while its owner process is alive")
        try:
            self._lock = self.lock_path.open("a+")
            if fcntl is not None:
                fcntl.flock(self._lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (OSError, BlockingIOError) as exc:
            if self._lock is not None:
                self._lock.close()
                self._lock = None
            raise ScratchError(f"refusing to reopen active scratch root: {self.path}") from exc
        self.created_at = owner.get("created_at", _iso(_utc_now()))
        self._retained = True
        self.retention = "retained-evidence"
        self._opened = True
        _write_json(
            self.receipt_path,
            self._receipt_preserving(state="active", recovery_of=owner.get("run_id")),
        )
        return self.path

    def promote_file(self, source: str | Path, destination: str | Path, *, complete: bool = True) -> Path:
        """Promote complete evidence through the cohesive promotion owner."""
        from scripts.runtime_scratch_promotion import promote_file

        return promote_file(self, source, destination, complete=complete)

    def _close_lock(self) -> None:
        if self._lock is None:
            return
        try:
            if fcntl is not None:
                fcntl.flock(self._lock.fileno(), fcntl.LOCK_UN)
        finally:
            self._lock.close()
            self._lock = None

    def close(self, *, state: str = "succeeded", remove_retained: bool = False) -> None:
        if not self._opened:
            return
        if state not in TERMINAL_STATES:
            raise ScratchError(f"invalid terminal scratch state: {state!r}")
        if self._promoted:
            _write_json(self.receipt_path, self._receipt_preserving(state="retained"))
            self._close_lock()
            _rmtree_writable(self.path)
        elif self._retained and not remove_retained:
            _write_json(self.receipt_path, self._receipt_preserving(state="retained"))
            self._close_lock()
        else:
            _write_json(self.receipt_path, self._receipt_preserving(state=state))
            self._close_lock()
            _rmtree_writable(self.path)
        self._opened = False

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        self.close(state="failed" if exc_type is not None else "succeeded")
        return False


def owned_scratch(
    repo_root: str | Path,
    producer: str,
    *,
    run_id: str | None = None,
    retention: str = "scratch",
    runtime_root_path: str | Path | None = None,
    retention_seconds: int = DEFAULT_RETENTION_SECONDS,
) -> OwnedScratch:
    return OwnedScratch(
        repo_root,
        producer,
        run_id=run_id,
        retention=retention,
        runtime_root_path=runtime_root_path,
        retention_seconds=retention_seconds,
    )


def _registry_module():
    return import_repo_module(__file__, "scripts.runtime_scratch_registry")


def inspect_scratch_roots(
    repo_root: str | Path,
    *,
    runtime_root_path: str | Path | None = None,
    max_roots: int = 256,
    max_entries: int = 100_000,
) -> dict[str, Any]:
    return _registry_module().inspect_scratch_roots(
        sys.modules[__name__],
        repo_root,
        runtime_root_path=runtime_root_path,
        max_roots=max_roots,
        max_entries=max_entries,
    )


def gc_scratch_roots(
    repo_root: str | Path,
    *,
    runtime_root_path: str | Path | None = None,
    dry_run: bool = True,
    max_roots: int = 256,
    max_entries: int = 100_000,
) -> dict[str, Any]:
    return _registry_module().gc_scratch_roots(
        sys.modules[__name__],
        repo_root,
        runtime_root_path=runtime_root_path,
        dry_run=dry_run,
        max_roots=max_roots,
        max_entries=max_entries,
    )


def recover_scratch_roots(
    repo_root: str | Path,
    *,
    runtime_root_path: str | Path | None = None,
    dry_run: bool = True,
    max_roots: int = 256,
    max_entries: int = 100_000,
) -> dict[str, Any]:
    return _registry_module().recover_scratch_roots(
        sys.modules[__name__],
        repo_root,
        runtime_root_path=runtime_root_path,
        dry_run=dry_run,
        max_roots=max_roots,
        max_entries=max_entries,
    )


def main(argv: list[str] | None = None) -> int:
    cli = import_repo_module(__file__, "scripts.runtime_scratch_cli")
    return cli.main(sys.modules[__name__], argv)


if __name__ == "__main__":
    raise SystemExit(main())
