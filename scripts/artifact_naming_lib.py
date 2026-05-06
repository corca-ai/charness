from __future__ import annotations

import re
from datetime import date

CURRENT_POINTER_FILENAME = "latest.md"
ROLLING_ARTIFACT_FILENAMES = {
    "handoff": "handoff.md",
}
CURRENT_POINTER_EXCEPTION_SKILL_IDS = frozenset(
    {
        "find-skills",
        "hitl",
        "init-repo",
    }
)
RECORD_PATTERN = "YYYY-MM-DD-<slug>.md"
SLUG_RE = re.compile(r"[^a-z0-9]+")


def current_artifact_filename(skill_id: str) -> str:
    return ROLLING_ARTIFACT_FILENAMES.get(skill_id, CURRENT_POINTER_FILENAME)


def record_artifact_supported(skill_id: str) -> bool:
    return skill_id not in ROLLING_ARTIFACT_FILENAMES and skill_id not in CURRENT_POINTER_EXCEPTION_SKILL_IDS


def slugify(value: str) -> str:
    slug = SLUG_RE.sub("-", value.strip().lower()).strip("-")
    return slug or "artifact"


def dated_artifact_filename(slug: str, *, artifact_date: date | None = None) -> str:
    day = artifact_date or date.today()
    return f"{day.isoformat()}-{slugify(slug)}.md"
