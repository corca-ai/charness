from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class CurrentPointerWriteError(Exception):
    pass


def _same_bytes(path: Path, content: bytes) -> bool:
    try:
        return path.is_file() and path.read_bytes() == content
    except OSError:
        return False


def write_current_pointer_bytes(path: Path, content: bytes) -> dict[str, Any]:
    """Replace a current-pointer file without following an existing symlink.

    This is for `current`/`rolling` snapshot surfaces. If `path` is a
    symlink, the symlink itself is replaced with a regular file and the old
    target is left untouched. History-default record writers that want to keep
    a symlink pointer should use `refresh_current_pointer.py` instead.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.is_dir():
        raise CurrentPointerWriteError(f"current pointer path is a directory: {path}")
    pointer_was_symlink = path.is_symlink()
    if not path.is_symlink() and _same_bytes(path, content):
        return {
            "path": str(path),
            "status": "noop",
            "pointer_was_symlink": False,
        }

    tmp = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    try:
        tmp.write_bytes(content)
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()
    return {
        "path": str(path),
        "status": "updated",
        "pointer_was_symlink": pointer_was_symlink,
    }


def write_current_pointer_text(path: Path, text: str, *, encoding: str = "utf-8") -> dict[str, Any]:
    return write_current_pointer_bytes(path, text.encode(encoding))


def write_current_pointer_json(path: Path, payload: Any) -> dict[str, Any]:
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    return write_current_pointer_text(path, text)
