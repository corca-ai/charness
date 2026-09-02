#!/usr/bin/env python3

"""Consumer-relative command-carrier checks for exported skill packages."""

from __future__ import annotations

import re
from pathlib import Path

from runtime_bootstrap import import_repo_module

_markdown_doc_scan = import_repo_module(__file__, "scripts.core.markdown_doc_scan")
iter_doc_lines = _markdown_doc_scan.iter_doc_lines

BACKTICK_CONTENT_RE = re.compile(r"`([^`\n]+)`")
COMMAND_TARGET_RE = re.compile(
    r"(?:^|[\s|(\"'=&;])(?:python3?\s+|bash\s+|sh\s+|\./)"
    r"([A-Za-z0-9._<>/-]+\.(?:py|sh))"
)
REPO_REFERENCE_PREFIXES = (
    ".agents/",
    "charness-artifacts/",
    "docs/",
    "evals/",
    "packaging/",
    "plugins/",
    "presets/",
    "profiles/",
    "scripts/",
    "skills/",
    "tests/",
)


def _looks_like_repo_reference(candidate: str) -> bool:
    stripped = candidate.split("#", 1)[0].strip()
    while stripped.startswith("./"):
        stripped = stripped[2:]
    return stripped.startswith(REPO_REFERENCE_PREFIXES)


def iter_unresolved_command_targets(
    root: Path,
    doc: Path,
    package_root: Path | None,
    known_repo_paths: set[str] | None = None,
) -> list[tuple[int, str]]:
    """Find repo-owned script targets named by commands that do not exist."""
    matches: list[tuple[int, str]] = []

    def resolves(rel_posix: str) -> bool:
        if known_repo_paths is not None:
            return rel_posix in known_repo_paths
        return (root / rel_posix).exists()

    for lineno, line, in_fence in iter_doc_lines(doc):
        carriers = (
            [line]
            if in_fence
            else [span.group(1) for span in BACKTICK_CONTENT_RE.finditer(line)]
        )
        for carrier in carriers:
            for match in COMMAND_TARGET_RE.finditer(carrier):
                candidate = match.group(1)
                if "<" in candidate or ">" in candidate:
                    continue
                if not _looks_like_repo_reference(candidate):
                    continue
                if resolves(candidate):
                    continue
                if package_root is not None:
                    packaged = (package_root.relative_to(root) / candidate).as_posix()
                    if resolves(packaged):
                        continue
                matches.append((lineno, candidate))
    return matches


def _shipped_path(candidate: str) -> str | None:
    for source_prefix, shipped_prefix in (
        ("skills/public/", "skills/"),
        ("skills/support/", "support/"),
        ("skills/shared/", "shared/"),
    ):
        if candidate.startswith(source_prefix):
            return shipped_prefix + candidate.removeprefix(source_prefix)
    return None


def iter_unportable_command_targets(
    root: Path,
    doc: Path,
    package_root: Path | None,
    known_repo_paths: set[str] | None = None,
) -> list[tuple[int, str, str, bool]]:
    """Find source-existing kind-bearing command paths in a portable doc.

    The source checkout can resolve ``skills/public/<skill>/...`` even though
    export presents that package as ``<plugin-dir>/skills/<skill>/...``. Source
    existence therefore cannot bless the command. Explicit ``$SKILL_DIR`` and
    ``<plugin-dir>`` forms do not match this detector.
    """
    if package_root is None:
        return []

    plugin_root = root / "plugins"
    plugin_packages = (
        [package for package in plugin_root.iterdir() if package.is_dir()]
        if plugin_root.is_dir()
        else []
    )
    matches: list[tuple[int, str, str, bool]] = []
    for lineno, line, in_fence in iter_doc_lines(doc):
        carriers = (
            [line]
            if in_fence
            else [span.group(1) for span in BACKTICK_CONTENT_RE.finditer(line)]
        )
        for carrier in carriers:
            for match in COMMAND_TARGET_RE.finditer(carrier):
                candidate = match.group(1)
                shipped = _shipped_path(candidate)
                if shipped is None or "<" in candidate or ">" in candidate:
                    continue
                source_exists = (
                    candidate in known_repo_paths
                    if known_repo_paths is not None
                    else (root / candidate).is_file()
                )
                if not source_exists:
                    continue
                shipped_exists = any(
                    (package / shipped).is_file() for package in plugin_packages
                )
                matches.append((lineno, candidate, shipped, shipped_exists))
    return matches
