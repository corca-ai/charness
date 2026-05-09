"""Library helpers for write_record.py."""

from __future__ import annotations

import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class WriteError(Exception):
    pass


def validate_slug(slug: str) -> None:
    if not SLUG_RE.match(slug):
        raise WriteError(
            f"--slug {slug!r} must be lowercase letters, digits, and hyphens only"
        )


def validate_date(date: str) -> None:
    if not DATE_RE.match(date):
        raise WriteError(f"--date {date!r} must be ISO YYYY-MM-DD")


def today_iso(now: datetime | None = None) -> str:
    return (now or datetime.now(timezone.utc)).strftime("%Y-%m-%d")


def same_symlink_target(pointer_path: Path, record_path: Path) -> bool:
    if not pointer_path.is_symlink():
        return False
    raw_target = Path(os.readlink(pointer_path))
    target_path = raw_target if raw_target.is_absolute() else pointer_path.parent / raw_target
    try:
        return target_path.resolve() == record_path.resolve()
    except FileNotFoundError:
        return False


def refresh_current_pointer(
    pointer_path: Path,
    record_path: Path,
    output_dir: Path,
    *,
    execute: bool,
) -> dict[str, Any]:
    """Inline symlink-aware pointer refresh.

    Mirrors the safety contract in `scripts/refresh_current_pointer.py`
    but stays in-process so the writer does not depend on a
    parent-harness shell-out that may not be available in every consumer
    layout. Refuses to operate on a symlink whose target escapes
    `output_dir`. See corca-ai/charness#138.
    """
    payload: dict[str, Any] = {
        "pointer_path": str(pointer_path),
        "record_path": str(record_path),
        "execute": execute,
        "status": "planned",
    }
    pointer_is_symlink = pointer_path.is_symlink()
    payload["pointer_is_symlink"] = pointer_is_symlink
    if pointer_path.exists() and not pointer_is_symlink and pointer_path.is_dir():
        payload["status"] = "blocked"
        payload["reason"] = "pointer path is a directory"
        return payload
    if pointer_is_symlink:
        existing_target = (pointer_path.parent / Path(os.readlink(pointer_path))).resolve()
        try:
            existing_target.relative_to(output_dir.resolve())
        except ValueError:
            payload["status"] = "blocked"
            payload["reason"] = "existing pointer symlink targets outside output_dir"
            return payload
        if same_symlink_target(pointer_path, record_path):
            payload["status"] = "noop"
            payload["reason"] = "pointer already targets the record"
            return payload
        relative_target = os.path.relpath(record_path, start=pointer_path.parent)
        payload["target"] = relative_target
        if execute:
            pointer_path.unlink()
            pointer_path.symlink_to(relative_target)
            payload["status"] = "updated"
        return payload
    if (
        pointer_path.exists()
        and pointer_path.is_file()
        and pointer_path.read_bytes() == record_path.read_bytes()
    ):
        payload["status"] = "noop"
        payload["reason"] = "pointer already matches the record"
        return payload
    if execute:
        if pointer_path.exists() or pointer_path.is_symlink():
            pointer_path.unlink()
        shutil.copyfile(record_path, pointer_path)
        payload["status"] = "updated"
    return payload


def compute_record_path(output_dir: Path, date: str, slug: str) -> Path:
    """Compute the dated record path and verify it stays inside output_dir."""
    record_filename = f"{date}-{slug}.md"
    record_path = (output_dir / record_filename).resolve()
    try:
        record_path.relative_to(output_dir.resolve())
    except ValueError as exc:
        raise WriteError(
            "computed record path escapes output_dir; check --slug / --date"
        ) from exc
    return record_path
