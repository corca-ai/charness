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
