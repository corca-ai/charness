"""Shared JSONL parsing and validation for usage-episode stream consumers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonschema
from usage_episode_feedback import semantic_feedback_errors

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STORAGE = Path(".charness/usage-episodes")
EVENT_FILENAME = "usage_episode.jsonl"


def schema_root(repo_root: Path) -> Path:
    candidate = repo_root / "integrations" / "usage-episodes"
    if (candidate / "manifest.schema.json").is_file() and (candidate / "episode.schema.json").is_file():
        return candidate
    return REPO_ROOT / "integrations" / "usage-episodes"


def resolve_records_path(
    repo_root: Path,
    adapter: dict[str, Any],
    explicit: Path | None,
) -> Path:
    if explicit is not None:
        candidate = explicit if explicit.is_absolute() else repo_root / explicit
        return candidate.resolve()
    storage_path = adapter.get("storage_path")
    storage_dir = repo_root / storage_path if isinstance(storage_path, str) else repo_root / DEFAULT_STORAGE
    return (storage_dir / EVENT_FILENAME).resolve()


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def read_valid_records(
    path: Path,
    record_schema: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    validator = jsonschema.Draft7Validator(
        record_schema,
        format_checker=jsonschema.FormatChecker(),
    )
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            row = json.loads(stripped)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{line_number}: invalid JSON: {exc}")
            continue
        try:
            validator.validate(row)
        except jsonschema.ValidationError as exc:
            path_text = ".".join(str(part) for part in exc.absolute_path)
            suffix = f" at {path_text}" if path_text else ""
            errors.append(f"{path}:{line_number}: schema error{suffix}: {exc.message}")
            continue
        try:
            parse_timestamp(row["timestamp"])
        except ValueError:
            errors.append(
                f"{path}:{line_number}: schema error at timestamp: "
                f"{row['timestamp']!r} is not date-time"
            )
            continue
        records.append(row)
    if not errors:
        errors.extend(semantic_feedback_errors(records))
    return records, errors
