"""Durably promote complete evidence out of an owned scratch root."""

from __future__ import annotations

import hashlib
import os
import tempfile
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

from scripts import runtime_scratch as _scratch  # noqa: E402

ScratchError = _scratch.ScratchError
_contains_path = _scratch._contains_path
_read_owner = _scratch._read_owner


def promote_file(
    owner: Any,
    source: str | Path,
    destination: str | Path,
    *,
    complete: bool = True,
) -> Path:
    """Atomically publish one complete proof and keep retry bytes on failure."""
    if not owner._opened:
        raise ScratchError("cannot promote evidence before the scratch root is opened")
    if not complete:
        raise ScratchError("refusing to promote incomplete evidence")
    source_path = Path(source).expanduser().resolve()
    destination_path = Path(destination).expanduser().resolve()
    if not source_path.is_file() or not _contains_path(owner.path, source_path):
        raise ScratchError("evidence source must be a file inside the owned scratch root")
    if _contains_path(owner.path, destination_path):
        raise ScratchError("durable evidence must be outside the scratch root")
    # A promotion is a two-file publication: evidence bytes and their durable
    # ownership receipt. Until both read back, retained scratch is the retry
    # source and owner.close() must not remove it.
    owner._retained = True
    owner.retention = "retained-evidence"
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=f".{destination_path.name}.", suffix=".tmp", dir=destination_path.parent
    )
    temporary_path = Path(temporary)
    digest = hashlib.sha256()
    durable_receipt = destination_path.with_name(
        f".{destination_path.name}.charness-receipt.json"
    )
    try:
        with source_path.open("rb") as source_handle, os.fdopen(fd, "wb") as target_handle:
            for chunk in iter(lambda: source_handle.read(1024 * 1024), b""):
                digest.update(chunk)
                target_handle.write(chunk)
            target_handle.flush()
            os.fsync(target_handle.fileno())
        os.replace(temporary_path, destination_path)
        _scratch._write_json(
            durable_receipt,
            owner._receipt(
                state="retained",
                evidence_path=str(destination_path),
                evidence_sha256=digest.hexdigest(),
                source_scratch_root=str(owner.path),
                source_receipt=str(owner.receipt_path),
            ),
        )
        saved_receipt = _read_owner(durable_receipt)
        if (
            saved_receipt is None
            or saved_receipt.get("evidence_path") != str(destination_path)
            or saved_receipt.get("evidence_sha256") != digest.hexdigest()
        ):
            raise ScratchError("durable evidence receipt failed read-back verification")
    except BaseException as exc:
        owner._promoted = False
        try:
            _scratch._write_json(
                owner.receipt_path,
                owner._receipt_preserving(state="retained", promotion_error=str(exc)),
            )
        except OSError:
            pass
        raise
    finally:
        temporary_path.unlink(missing_ok=True)
    owner._promoted = True
    return durable_receipt
