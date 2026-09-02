from __future__ import annotations

from pathlib import Path


def repo_relative(repo_root: Path, path: Path) -> str:
    """Render paths stored in repo artifacts without absolute host prefixes."""
    resolved_root = repo_root.resolve()
    resolved_path = path if path.is_absolute() else resolved_root / path
    try:
        return resolved_path.resolve().relative_to(resolved_root).as_posix()
    except ValueError:
        return str(path)


def resolve_within_repo(repo_root: Path, raw: str) -> str | None:
    """``raw`` (absolute or repo-relative) as a repo-relative POSIX path, or ``None``
    when it resolves outside the repo or cannot be resolved at all.

    Three callers had grown their own copy of this resolve-and-relativize core, each
    with a DIFFERENT failure disposition — raise, stay silent, echo the raw path — and
    a duplication gate grouped them. The disposition is the part that legitimately
    differs and stays with the caller; only the resolution is shared. ``OSError`` is
    caught alongside ``ValueError`` because a broken symlink or an unreadable parent
    makes ``resolve()`` raise on some platforms, and every caller wants that to be
    "not a path inside this repo", never a traceback.
    """
    path = Path(raw)
    if not path.is_absolute():
        path = repo_root / path
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return None
