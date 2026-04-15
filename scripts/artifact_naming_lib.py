from __future__ import annotations

import re
from datetime import date
from pathlib import Path

CURRENT_POINTER_FILENAME = "latest.md"
ROLLING_ARTIFACT_FILENAMES = {
    "handoff": "handoff.md",
}
RECORD_PATTERN = "YYYY-MM-DD-<slug>.md"
SLUG_RE = re.compile(r"[^a-z0-9]+")


def current_artifact_filename(skill_id: str) -> str:
    return ROLLING_ARTIFACT_FILENAMES.get(skill_id, CURRENT_POINTER_FILENAME)


def slugify(value: str) -> str:
    slug = SLUG_RE.sub("-", value.strip().lower()).strip("-")
    return slug or "artifact"


def dated_artifact_filename(slug: str, *, artifact_date: date | None = None) -> str:
    day = artifact_date or date.today()
    return f"{day.isoformat()}-{slugify(slug)}.md"


def dated_artifact_path(output_dir: str | Path, slug: str, *, artifact_date: date | None = None) -> Path:
    return Path(output_dir) / dated_artifact_filename(slug, artifact_date=artifact_date)
