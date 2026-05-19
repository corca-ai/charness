from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from pathlib import Path
from typing import Callable

import filelock

ROOT = Path(__file__).resolve().parents[1]


def _user_cache_root() -> Path:
    override = os.environ.get("CHARNESS_TEST_SEED_CACHE_ROOT")
    if override:
        return Path(override)
    xdg = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg) if xdg else Path.home() / ".cache"
    return base / "charness" / "test-seeds"


def _compute_source_hash(source_root: Path) -> str:
    digest = hashlib.sha256()
    head = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    digest.update(head.encode())
    digest.update(b"\n---DIFF---\n")
    diff = subprocess.run(
        ["git", "-C", str(source_root), "diff", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    digest.update(diff.encode())
    digest.update(b"\n---UNTRACKED---\n")
    untracked = subprocess.run(
        ["git", "-C", str(source_root), "ls-files", "--others", "--exclude-standard"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    for rel in sorted(untracked.splitlines()):
        rel = rel.strip()
        if not rel:
            continue
        full = source_root / rel
        if not full.is_file():
            continue
        digest.update(rel.encode())
        digest.update(b"\0")
        try:
            digest.update(full.read_bytes())
        except OSError:
            continue
    return digest.hexdigest()[:32]


_SOURCE_HASH: str | None = None


def source_hash() -> str:
    global _SOURCE_HASH
    if _SOURCE_HASH is None:
        _SOURCE_HASH = _compute_source_hash(ROOT)
    return _SOURCE_HASH


def get_or_build(name: str, builder: Callable[[Path], None]) -> Path:
    cache_dir = _user_cache_root() / source_hash()
    cache_dir.mkdir(parents=True, exist_ok=True)
    final = cache_dir / name
    ready = cache_dir / f"{name}.ready"
    lock_path = cache_dir / f"{name}.lock"
    with filelock.FileLock(str(lock_path)):
        if ready.is_file() and final.is_dir():
            return final
        if ready.exists():
            ready.unlink()
        if final.exists():
            shutil.rmtree(final)
        final.mkdir()
        builder(final)
        ready.write_text("ok", encoding="utf-8")
    return final
