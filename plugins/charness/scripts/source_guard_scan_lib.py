from __future__ import annotations

import re
from pathlib import Path
from typing import Any

SOURCE_GUARD_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*fixed\s*\|\s*([^|]+?)\s*\|")
DEFAULT_SOURCE_GUARD_SCAN_ROOTS = (
    Path("AGENTS.md"),
    Path("README.md"),
    Path("docs"),
    Path("specs"),
)


def relative_path(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def _path_is_ignored(path: Path, repo_root: Path) -> bool:
    ignored_parts = {".git", ".charness", "node_modules", "__pycache__"}
    try:
        relative_parts = path.relative_to(repo_root).parts
    except ValueError:
        return True
    return any(part in ignored_parts or part.startswith(".") for part in relative_parts)


def iter_markdown_files(repo_root: Path, scan_roots: list[Path]) -> list[Path]:
    files: dict[str, Path] = {}
    for root in scan_roots:
        scan_root = repo_root / root
        if _path_is_ignored(scan_root, repo_root):
            continue
        if scan_root.is_file() or scan_root.is_symlink():
            candidates = [scan_root] if scan_root.suffix == ".md" else []
        elif scan_root.is_dir():
            candidates = sorted(scan_root.rglob("*.md"))
        else:
            candidates = []
        for path in candidates:
            if _path_is_ignored(path, repo_root):
                continue
            files[path.as_posix()] = path
    return [files[key] for key in sorted(files)]


def fixed_source_guard_rows(repo_root: Path, scan_roots: list[Path]) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    rows: list[dict[str, str]] = []
    warnings: list[dict[str, Any]] = []
    for spec_path in iter_markdown_files(repo_root, scan_roots):
        try:
            text = spec_path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            warnings.append(
                {
                    "type": "source_guard_markdown_unreadable",
                    "path": relative_path(spec_path, repo_root),
                    "message": f"Skipped unreadable markdown while scanning source guards: {exc.strerror or exc}",
                }
            )
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            match = SOURCE_GUARD_RE.match(line)
            if not match:
                continue
            target, pattern = (part.strip() for part in match.groups())
            rows.append(
                {
                    "spec_path": relative_path(spec_path, repo_root),
                    "line": str(line_no),
                    "target_path": target,
                    "pattern": pattern,
                }
            )
    return rows, warnings
