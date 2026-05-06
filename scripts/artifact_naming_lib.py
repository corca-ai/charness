from __future__ import annotations

import re
from datetime import date

CURRENT_POINTER_FILENAME = "latest.md"
ROLLING_ARTIFACT_FILENAMES = {
    "handoff": "handoff.md",
}
RECORD_PATTERN = "YYYY-MM-DD-<slug>.md"
SLUG_RE = re.compile(r"[^a-z0-9]+")
ARTIFACT_CLASS_HISTORY = "history"
ARTIFACT_CLASS_CURRENT = "current"
ARTIFACT_CLASS_ROLLING = "rolling"
ARTIFACT_CLASSES = frozenset({ARTIFACT_CLASS_HISTORY, ARTIFACT_CLASS_CURRENT, ARTIFACT_CLASS_ROLLING})
DEFAULT_ARTIFACT_CLASS = ARTIFACT_CLASS_HISTORY


class ArtifactClassError(ValueError):
    pass


def current_artifact_filename(skill_id: str) -> str:
    return ROLLING_ARTIFACT_FILENAMES.get(skill_id, CURRENT_POINTER_FILENAME)


def normalize_artifact_class(value: object, *, default: str = DEFAULT_ARTIFACT_CLASS) -> str:
    if isinstance(value, str) and value in ARTIFACT_CLASSES:
        return value
    return default


def artifact_class_from_adapter(adapter: dict[str, object], *, default: str = DEFAULT_ARTIFACT_CLASS) -> str:
    data = adapter.get("data", {})
    data_class = data.get("artifact_class") if isinstance(data, dict) else None
    declared_class = adapter.get("artifact_class") or data_class
    if declared_class is None:
        return default
    if isinstance(declared_class, str) and declared_class in ARTIFACT_CLASSES:
        return declared_class
    raise ArtifactClassError(f"artifact_class must be one of: {', '.join(sorted(ARTIFACT_CLASSES))}")


def record_artifact_supported(artifact_class: object) -> bool:
    return normalize_artifact_class(artifact_class) == ARTIFACT_CLASS_HISTORY


def slugify(value: str) -> str:
    slug = SLUG_RE.sub("-", value.strip().lower()).strip("-")
    return slug or "artifact"


def dated_artifact_filename(slug: str, *, artifact_date: date | None = None) -> str:
    day = artifact_date or date.today()
    return f"{day.isoformat()}-{slugify(slug)}.md"
