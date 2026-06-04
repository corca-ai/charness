from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

ISSUE_ANCHOR_RE = re.compile(
    r"(?:"
    r"\b[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#\d+\b|"
    r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/issues/\d+\b|"
    r"\bissues/\d+\b|"
    r"\bissue-\d+\b|"
    r"\b(?:issue|bug|pr|pull request)s?\s+#\d+\b|"
    r"(?<![A-Za-z0-9_])#\d{3,}\b"
    r")",
    re.IGNORECASE,
)
DATED_INCIDENT_RE = re.compile(
    r"(?:20\d{2}-\d{2}-\d{2}.{0,80}\b(?:incident|miss|regression|trap|failure|bug|closeout|lesson)s?\b|"
    r"\b(?:incident|miss|regression|trap|failure|bug|closeout|lesson)s?\b.{0,80}20\d{2}-\d{2}-\d{2})",
    re.IGNORECASE,
)
HOST_SURFACE_REFERENCE_RE = re.compile(
    r"\b(?:Claude Code|Codex|settings\.json|host system prompt|host-managed checkout)\b|"
    r"(?:^|[^\w.])\.(?:claude|codex)(?:/|$)",
    re.IGNORECASE,
)
PACKAGE_TEXT_SUFFIXES = {
    ".bash",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".txt",
    ".yaml",
    ".yml",
    ".zsh",
}
PACKAGE_TEXT_FILENAMES = {"SKILL.md"}
ISSUE_VERSION_FIELD_RE = re.compile(r"defaults_version\b.*\bissue-\d+\b", re.IGNORECASE)
PLACEHOLDER_ISSUE_URL_RE = re.compile(r"\.\.\./issues/\d+\b")


def _is_package_text_file(path: Path) -> bool:
    return path.name in PACKAGE_TEXT_FILENAMES or path.suffix in PACKAGE_TEXT_SUFFIXES


def _iter_package_text_files(skill_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in skill_dir.rglob("*")
        if path.is_file()
        and _is_package_text_file(path)
        and "__pycache__" not in path.parts
        and ".pytest_cache" not in path.parts
    )


def _excerpt(line: str) -> str:
    return line.strip()[:160]


def _line_findings_for_pattern(
    repo_root: Path,
    skill_dir: Path,
    *,
    heuristic: str,
    pattern: re.Pattern[str],
    skip: Callable[[str], bool] | None = None,
) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for path in _iter_package_text_files(skill_dir):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for index, line in enumerate(lines, start=1):
            if not pattern.search(line):
                continue
            if skip is not None and skip(line):
                continue
            findings.append(
                {
                    "heuristic": heuristic,
                    "path": str(path.relative_to(repo_root)),
                    "line": index,
                    "excerpt": _excerpt(line),
                }
            )
    return findings


def is_allowed_issue_anchor_context(line: str) -> bool:
    return bool(ISSUE_VERSION_FIELD_RE.search(line) or PLACEHOLDER_ISSUE_URL_RE.search(line))


def issue_anchor_package_findings(repo_root: Path, skill_dir: Path) -> list[dict[str, object]]:
    return _line_findings_for_pattern(
        repo_root,
        skill_dir,
        heuristic="portable_package_issue_anchor",
        pattern=ISSUE_ANCHOR_RE,
        skip=is_allowed_issue_anchor_context,
    )


def dated_incident_package_findings(repo_root: Path, skill_dir: Path) -> list[dict[str, object]]:
    return _line_findings_for_pattern(
        repo_root,
        skill_dir,
        heuristic="portable_package_dated_incident",
        pattern=DATED_INCIDENT_RE,
    )


def host_surface_reference_findings(repo_root: Path, skill_dir: Path) -> list[dict[str, object]]:
    return _line_findings_for_pattern(
        repo_root,
        skill_dir,
        heuristic="portable_package_host_surface_reference",
        pattern=HOST_SURFACE_REFERENCE_RE,
    )


def reference_discoverability_findings(repo_root: Path, skill_path: Path, body: str) -> list[dict[str, object]]:
    references_dir = skill_path.parent / "references"
    if not references_dir.is_dir():
        return []
    findings: list[dict[str, object]] = []
    for path in sorted(references_dir.rglob("*")):
        if not path.is_file() or not _is_package_text_file(path):
            continue
        if "__pycache__" in path.parts or ".pytest_cache" in path.parts:
            continue
        relative_to_skill = path.relative_to(skill_path.parent).as_posix()
        if relative_to_skill in body:
            continue
        findings.append(
            {
                "heuristic": "reference_discoverability_gap",
                "path": str(path.relative_to(repo_root)),
                "line": 0,
                "excerpt": f"{relative_to_skill} is not listed in SKILL.md",
            }
        )
    return findings
