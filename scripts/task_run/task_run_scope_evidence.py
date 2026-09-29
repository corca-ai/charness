#!/usr/bin/env python3
"""Suggest repository paths named by task-run and quality failure evidence."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_PATH_TOKEN = re.compile(
    r"(?<![\w.-])(?P<path>(?:/?[\w.-]+/)+[\w.-]+(?:\.[A-Za-z][A-Za-z0-9]*)?"
    r"|[\w.-]+\.[A-Za-z][A-Za-z0-9]*)(?::(?P<line>\d+)(?::\d+)?)?"
)
_TRACEBACK_FRAME = re.compile(r"File [\"']([^\"']+)[\"'], line \d+")
_INLINE_CODE = re.compile(r"`([^`]+)`")
_REJECTED_OWNER_AFTER = re.compile(
    r"^\s*(?:would\s+)?substitut\w*\s+(?:the\s+)?wrong"
    r"(?:\s+[\w-]+){0,2}\s+owner\b",
    re.IGNORECASE,
)
_FILE_TAIL = re.compile(r"\.[A-Za-z][A-Za-z0-9]*$")


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if parent.joinpath("scripts", "task_run").is_dir():
            return parent
    return Path.cwd()


def _repo_top_level_names(root: Path) -> set[str]:
    try:
        return {entry.name for entry in root.iterdir()}
    except OSError:
        return set()


def _relative_path(raw: str, root: Path, top_level_names: set[str]) -> str | None:
    """Return a repo-relative path, discarding external absolute prefixes."""
    value = raw.strip().rstrip(".,;:").replace("\\", "/")
    if not value:
        return None
    if re.match(r"^[A-Za-z]:/", value):
        value = value[2:]

    path = Path(value)
    if path.is_absolute():
        resolved = path.resolve()
        resolved_root = root.resolve()
        try:
            path = resolved.relative_to(resolved_root)
        except ValueError:
            parts = resolved.parts
            anchor = next(
                (index for index, part in enumerate(parts) if index > 0 and part in top_level_names),
                None,
            )
            if anchor is None:
                return None
            path = Path(*parts[anchor:])

    normalized = path.as_posix().removeprefix("./")
    if not normalized or normalized.startswith("/") or ".." in Path(normalized).parts:
        return None
    if normalized.startswith("quality-failure-logs/") and normalized.endswith(".log"):
        return None
    return normalized


def _is_inline_code_span(text: str, start: int, end: int) -> bool:
    return any(
        match.start(1) <= start and end <= match.end(1)
        for match in _INLINE_CODE.finditer(text)
    )


def _is_rejected_owner_mention(text: str, end: int) -> bool:
    after = text[end : end + 100].lstrip("`'\".,;:)]} ")
    return bool(_REJECTED_OWNER_AFTER.match(after))


def _looks_like_file(normalized: str) -> bool:
    """Whether a slash token names a file rather than a ref or a scope."""
    if "/" not in normalized:
        return False
    return bool(_FILE_TAIL.search(normalized.rsplit("/", 1)[1]))


def _keep_candidate(normalized: str, *, root: Path, top_level_names: set[str]) -> bool:
    """Keep a relative candidate only when the repository admits it (#879).

    Dotted identifiers (``issue.create``) and slash tokens whose first
    segment is not a top-level repository name (``origin/main``,
    ``corca-org/ceal``) are not paths. A new file under a real top-level
    directory still counts through its first segment, an existing path
    counts even when the root listing failed, and a file-shaped slash
    token stays advisory recall for not-yet-existing files (#880).
    """
    first = normalized.split("/", 1)[0]
    return first in top_level_names or (root / normalized).exists() or _looks_like_file(normalized)


def suggest_scopes(evidence_text: str, *, repo_root: Path | None = None) -> list[str]:
    """Return sorted, deduplicated path candidates found in textual evidence.

    Paths are suggestions only. This function does not verify ownership or
    modify a declared task scope. ``repo_root`` is the repository the
    evidence is about; it defaults to the checkout carrying this script.
    """
    root = repo_root if repo_root is not None else _repo_root()
    top_level_names = _repo_top_level_names(root)
    candidates: set[str] = set()

    # Traceback frames can contain absolute paths or root-level filenames.
    for match in _TRACEBACK_FRAME.finditer(evidence_text):
        path = _relative_path(match.group(1), root, top_level_names)
        if path is not None and _keep_candidate(path, root=root, top_level_names=top_level_names):
            candidates.add(path)

    for match in _PATH_TOKEN.finditer(evidence_text):
        raw = match.group("path")
        has_directory = "/" in raw or "\\" in raw
        is_code = _is_inline_code_span(evidence_text, *match.span("path"))
        is_path_line = match.group("line") is not None
        if not (has_directory or is_code or is_path_line):
            continue
        if _is_rejected_owner_mention(evidence_text, match.end("path")):
            continue
        path = _relative_path(raw, root, top_level_names)
        if path is not None and _keep_candidate(path, root=root, top_level_names=top_level_names):
            candidates.add(path)

    return sorted(candidates)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Suggest repository paths named by task-run or quality evidence."
    )
    parser.add_argument("evidence_file", nargs="?", help="read evidence from this file (default: stdin)")
    args = parser.parse_args()
    evidence_text = (
        Path(args.evidence_file).read_text(encoding="utf-8")
        if args.evidence_file
        else sys.stdin.read()
    )
    for path in suggest_scopes(evidence_text):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
