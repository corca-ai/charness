"""Host capability detection for the standing pytest command planner."""

from __future__ import annotations

import importlib.metadata
import os


def usable_cpu_count() -> int:
    """Return CPUs available to this process, respecting affinity limits."""
    try:
        return len(os.sched_getaffinity(0)) or 1
    except (AttributeError, OSError):
        return os.cpu_count() or 1


def xdist_version() -> tuple[int, ...]:
    """Return this interpreter's pytest-xdist version, or ``()`` when unknown."""
    try:
        raw = importlib.metadata.version("pytest-xdist")
    except importlib.metadata.PackageNotFoundError:
        return ()
    parts: list[int] = []
    for chunk in raw.split(".")[:3]:
        digits = ""
        for char in chunk:
            if not char.isdigit():
                break
            digits += char
        if not digits:
            break
        parts.append(int(digits))
    return tuple(parts)
