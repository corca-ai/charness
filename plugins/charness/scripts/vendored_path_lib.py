from __future__ import annotations

from pathlib import Path
from typing import Iterable


def _normalize_prefix(prefix: str) -> str:
    cleaned = prefix.strip().strip("/")
    if cleaned.endswith("/SKILL.md"):
        cleaned = cleaned[: -len("/SKILL.md")]
    elif cleaned == "SKILL.md":
        cleaned = ""
    return cleaned


def vendored_prefixes(values: list[str] | None) -> list[str]:
    if not values:
        return []
    seen: set[str] = set()
    prefixes: list[str] = []
    for value in values:
        if not isinstance(value, str):
            continue
        normalized = _normalize_prefix(value)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        prefixes.append(normalized)
    return prefixes


def relative_posix(repo_root: Path, path: Path) -> str | None:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return None


def is_vendored_relative(rel_posix: str, prefixes: list[str]) -> bool:
    if not prefixes:
        return False
    for prefix in prefixes:
        if rel_posix == prefix or rel_posix.startswith(f"{prefix}/"):
            return True
    return False


def is_vendored(repo_root: Path, path: Path, prefixes: list[str]) -> bool:
    if not prefixes:
        return False
    rel = relative_posix(repo_root, path)
    if rel is None:
        return False
    return is_vendored_relative(rel, prefixes)


def filter_vendored(repo_root: Path, paths: Iterable[Path], prefixes: list[str]) -> list[Path]:
    if not prefixes:
        return list(paths)
    return [path for path in paths if not is_vendored(repo_root, path, prefixes)]
