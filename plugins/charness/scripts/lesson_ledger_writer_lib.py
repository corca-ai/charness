"""Shared cooperative lock and atomic replacement for lesson-ledger writers."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

try:
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None
try:
    import msvcrt
except ImportError:  # pragma: no cover
    msvcrt = None


def _fail(message: str) -> None:
    raise ValueError(f"lesson ledger writer: {message}")


@contextmanager
def ledger_lock(path: Path) -> Iterator[None]:
    digest = hashlib.sha256(str(path.resolve()).encode("utf-8")).hexdigest()
    lock_path = Path(tempfile.gettempdir()) / "charness-lesson-ledger-locks" / f"{digest}.lock"
    try:
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        lock = lock_path.open("a+", encoding="utf-8")
    except OSError as exc:
        _fail(f"unable to open lesson-ledger lock: {exc}")
    with lock:
        if fcntl is not None:
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            except OSError as exc:
                _fail(f"unable to acquire lesson-ledger lock: {exc}")
            try:
                yield
            finally:
                try:
                    fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
                except OSError as exc:
                    _fail(f"unable to release lesson-ledger lock: {exc}")
            return
        if msvcrt is not None:
            try:
                lock.seek(0, os.SEEK_END)
                if lock.tell() == 0:
                    lock.write("0")
                    lock.flush()
                lock.seek(0)
                msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
            except OSError as exc:
                _fail(f"unable to acquire lesson-ledger lock: {exc}")
            try:
                yield
            finally:
                try:
                    lock.seek(0)
                    msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
                except OSError as exc:
                    _fail(f"unable to release lesson-ledger lock: {exc}")
            return
        _fail("no supported platform file-locking primitive is available")


def replace_payload(path: Path, payload: dict[str, Any]) -> None:
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
            json.dump(payload, temporary, ensure_ascii=False, indent=2)
            temporary.write("\n")
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
