"""Validate repo-backed skill ergonomics counts cited by quality artifacts.

This module owns the cross-check between a quality record's claimed skill
pressure and the current skill tree. Keeping the filesystem measurement and
claim parsing together stops a quality artifact from reporting stale counts
while leaving the main artifact validator focused on its section rules.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

from runtime_bootstrap import import_repo_module

_artifact_validator = import_repo_module(__file__, "scripts.artifact_validator")
_skill_markdown_lib = import_repo_module(__file__, "scripts.core.skill_markdown_lib")
ValidationError = _artifact_validator.ValidationError

SKILL_ERGONOMICS_COUNT_RE = re.compile(
    r"`?core_nonempty_lines=(?P<core>\d+)`?.{0,120}?"
    r"`?reference_file_count=(?P<refs>\d+)`?.{0,120}?"
    r"`?script_file_count=(?P<scripts>\d+)`?",
    re.DOTALL,
)
BACKTICKED_TOKEN_RE = re.compile(r"`([a-z0-9-]+)`")
PRESSURE_EXEMPT_H2_SECTIONS = {"Load-Bearing Anchors", "References"}


def _count_files(path: Path) -> int:
    if not path.is_dir():
        return 0
    return sum(1 for candidate in path.rglob("*") if candidate.is_file())


def _skill_ergonomics_counts(repo_root: Path, skill_id: str) -> dict[str, int]:
    skill_path = repo_root / "skills" / "public" / skill_id / "SKILL.md"
    if not skill_path.is_file():
        raise ValidationError(
            f"quality artifact cites skill ergonomics counts for missing skill `{skill_id}`"
        )
    skill_dir = skill_path.parent
    body_lines: list[str] = []
    active_section: str | None = None
    for raw in _skill_markdown_lib.strip_frontmatter(
        skill_path.read_text(encoding="utf-8")
    ).splitlines():
        stripped = raw.strip()
        if stripped.startswith("## "):
            active_section = stripped[3:].strip()
        if active_section not in PRESSURE_EXEMPT_H2_SECTIONS:
            body_lines.append(raw)
    return {
        "core_nonempty_lines": sum(1 for line in body_lines if line.strip()),
        "reference_file_count": _count_files(skill_dir / "references"),
        "script_file_count": _count_files(skill_dir / "scripts"),
    }


def _claim_skill_id(repo_root: Path, claim_text: str) -> str:
    candidates = [
        match.group(1)
        for match in BACKTICKED_TOKEN_RE.finditer(claim_text)
        if (repo_root / "skills" / "public" / match.group(1) / "SKILL.md").is_file()
    ]
    if not candidates:
        raise ValidationError(
            "quality artifact has explicit skill ergonomics counts but no backticked public skill id "
            "in the same bullet"
        )
    return candidates[0]


def validate_skill_ergonomics_count_claims(
    lines: list[str], repo_root: Path, *, collect_bullets: Callable[[list[str]], list[str]]
) -> None:
    for claim_text in collect_bullets(lines):
        match = SKILL_ERGONOMICS_COUNT_RE.search(claim_text)
        if not match:
            continue
        skill_id = _claim_skill_id(repo_root, claim_text)
        claimed = {
            "core_nonempty_lines": int(match.group("core")),
            "reference_file_count": int(match.group("refs")),
            "script_file_count": int(match.group("scripts")),
        }
        actual = _skill_ergonomics_counts(repo_root, skill_id)
        if claimed != actual:
            raise ValidationError(
                f"quality artifact has stale skill ergonomics counts for `{skill_id}`: "
                f"claimed {claimed}, actual {actual}"
            )
