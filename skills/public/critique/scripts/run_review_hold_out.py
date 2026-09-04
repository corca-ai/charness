#!/usr/bin/env python3
"""Hide named in-progress paths from a critique worker tree for one run."""

from __future__ import annotations

import shutil
import tempfile
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def hold_out(
    root: Path,
    relative_paths: list[str],
    *,
    resolve_path: Callable[..., Path],
    error_cls: type[Exception],
) -> Iterator[None]:
    staging = Path(tempfile.mkdtemp(prefix="charness-hold-out-"))
    moved: list[tuple[Path, Path]] = []
    try:
        for index, value in enumerate(relative_paths):
            src = resolve_path(root, value, label="hold-out path")
            if not src.exists():
                raise error_cls(
                    "hold-out-missing",
                    f"hold-out path does not exist: {value}",
                    details={"path": value},
                )
            dest = staging / f"{index}-{src.name}"
            src.rename(dest)
            moved.append((src, dest))
        yield
    finally:
        for src, dest in reversed(moved):
            if dest.exists() and not src.exists():
                dest.rename(src)
        shutil.rmtree(staging, ignore_errors=True)
