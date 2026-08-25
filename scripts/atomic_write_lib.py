"""Small durable write-once primitive shared by artifact boundaries."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


def write_once(path: Path, content: bytes, *, label: str) -> None:
    """Atomically create ``path`` once, refusing replacement or partial writes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    # The existence check and final replace must share an ownership lock.  A
    # plain ``exists(); replace()`` sequence lets two writers both pass the
    # check and the later writer silently replace the first receipt.  The lock
    # is deliberately a create-once sidecar: a concurrent writer fails closed,
    # and a crashed writer leaves a visible stale lock rather than overwriting
    # a durable receipt on recovery.
    lock_path = path.with_name(f".{path.name}.lock")
    try:
        lock_fd = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise ValueError(f"{label} write is already claimed at `{path}`") from exc
    os.close(lock_fd)
    temporary_path: Path | None = None
    try:
        if path.exists() or path.is_symlink():
            raise ValueError(f"{label} already exists at `{path}`")
        with tempfile.NamedTemporaryFile(
            "wb", dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        lock_path.unlink(missing_ok=True)
