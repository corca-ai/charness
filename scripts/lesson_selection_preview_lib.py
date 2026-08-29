"""Build the read-only, deterministic preview over the cited lesson ledger."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from pathlib import Path
from typing import Any

from scripts.lesson_ledger_lib import (
    lesson_ledger_path,
    migrate_ledger_payload,
    validate_lesson_ledger,
)
from scripts.recent_lessons_lib import build_lesson_selection_index, check_lesson_selection_index

KIND = "charness.lesson-selection-preview"
SCHEMA_VERSION = 1
# 3 fills the archive-resurrection slot from the uncertainty ordering when the
# archive is empty. Bumped because the same seed over the same ledger now selects
# a different set, and a frozen snapshot must not be readable as though this
# policy produced it.
SELECTION_POLICY_VERSION = 3
BUCKETS = ("recent", "value", "uncertainty", "archive", "archive_fallback_uncertainty")


def _fail(message: str) -> None:
    raise ValueError(f"lesson selection preview invalid: {message}")


def _load_validated_ledger(repo_root: Path, output_dir: Path, summary_path: Path) -> dict[str, Any]:
    validate_lesson_ledger(repo_root=repo_root, output_dir=output_dir, summary_path=summary_path)
    payload = json.loads(lesson_ledger_path(output_dir).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("lessons"), dict):
        _fail("validated ledger could not be loaded")
    # Normalize IN MEMORY, exactly as validation just did. Validation deliberately
    # does not write -- a session-start READ must not upgrade a consumer's ledger to
    # a schema the previously released version cannot read -- so the bytes on disk may
    # still be the older schema and lack fields this preview reads.
    payload, _migrated = migrate_ledger_payload(payload)
    return payload


def _candidate_rows(index: dict[str, Any], lessons: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    candidates = index.get("candidates")
    if not isinstance(candidates, list):
        _fail("rebuilt lesson index has no candidate list")
    for candidate in candidates:
        if not isinstance(candidate, dict):
            _fail("rebuilt lesson index has a non-object candidate")
        lesson_id = candidate.get("recurrence_class")
        if not isinstance(lesson_id, str) or lesson_id not in lessons:
            continue
        if lesson_id in seen:
            _fail(f"rebuilt lesson index has duplicate recurrence-class `{lesson_id}`")
        lesson = lessons[lesson_id]
        if not isinstance(lesson, dict):
            _fail(f"validated ledger lesson `{lesson_id}` is not an object")
        try:
            score_total = lesson["score_total"]
            score_count = lesson["score_count"]
            lesson_text = candidate["lesson"]
            source_path = candidate["latest_source_path"]
        except KeyError as exc:
            _fail(f"candidate or lesson `{lesson_id}` lacks `{exc.args[0]}`")
        if type(score_total) is not int or type(score_count) is not int:
            _fail(f"validated ledger lesson `{lesson_id}` has non-integer score fields")
        if not isinstance(lesson_text, str) or not isinstance(source_path, str):
            _fail(f"candidate `{lesson_id}` has invalid rendered fields")
        seen.add(lesson_id)
        rows.append(
            {
                "lesson_id": lesson_id,
                "lesson": lesson_text,
                "latest_source_path": source_path,
                "latest_source_date": candidate.get("latest_source_date"),
                "selection_weight": candidate.get("selection_weight"),
                "score_total": score_total,
                "score_count": score_count,
                "state": lesson.get("state"),
            }
        )
    if seen != set(lessons):
        _fail("every seeded lesson must map to exactly one rebuilt recurrence-class candidate")
    return rows


def _recent_key(row: dict[str, Any]) -> tuple[int, int, float, str]:
    raw_date = row["latest_source_date"]
    try:
        ordinal = date.fromisoformat(raw_date).toordinal() if isinstance(raw_date, str) else 0
    except ValueError:
        ordinal = 0
    weight = row["selection_weight"]
    if not isinstance(weight, (int, float)) or isinstance(weight, bool):
        _fail(f"candidate `{row['lesson_id']}` has invalid selection_weight")
    return (0 if ordinal else 1, -ordinal, -float(weight), row["lesson_id"])


def _value(row: dict[str, Any]) -> float:
    return row["score_total"] / (row["score_count"] + 2)


def _uncertainty(row: dict[str, Any], total_score_count: int) -> float:
    return _value(row) + math.sqrt(math.log(max(total_score_count, 2)) / (row["score_count"] + 1))


def _take(rows: list[dict[str, Any]], selected_ids: set[str], count: int) -> list[dict[str, Any]]:
    chosen = [row for row in rows if row["lesson_id"] not in selected_ids][:count]
    selected_ids.update(row["lesson_id"] for row in chosen)
    return chosen


def _shuffled_items(seed: str, rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    def key(row: dict[str, Any]) -> tuple[str, str]:
        digest = hashlib.sha256(f"{seed}\0{row['lesson_id']}".encode("utf-8")).hexdigest()
        return digest, row["lesson_id"]

    return [
        {"lesson_id": row["lesson_id"], "lesson": row["lesson"], "latest_source_path": row["latest_source_path"]}
        for row in sorted(rows, key=key)
    ]


def build_lesson_selection_preview(*, repo_root: Path, output_dir: Path, summary_path: Path, seed: str) -> dict[str, Any]:
    """Return a flat, deterministic preview without recording a shown set."""
    if not isinstance(seed, str) or not seed:
        _fail("seed must be a non-empty string")
    check_lesson_selection_index(repo_root, output_dir, summary_path)
    ledger = _load_validated_ledger(repo_root, output_dir, summary_path)
    rows = _candidate_rows(
        build_lesson_selection_index(repo_root=repo_root, output_dir=output_dir, summary_path=summary_path),
        ledger["lessons"],
    )
    selected_ids: set[str] = set()
    if any(row["state"] not in {"active", "archived"} for row in rows):
        _fail("validated ledger lesson has invalid lifecycle state")
    active_rows = [row for row in rows if row["state"] == "active"]
    archived_rows = [row for row in rows if row["state"] == "archived"]
    total_score_count = sum(row["score_count"] for row in rows)
    recent = _take(sorted(active_rows, key=_recent_key), selected_ids, 3)
    value = _take(
        sorted(active_rows, key=lambda row: (-_value(row), row["lesson_id"])),
        selected_ids,
        3,
    )
    uncertainty_rows = sorted(
        active_rows,
        key=lambda row: (-_uncertainty(row, total_score_count), row["lesson_id"]),
    )
    uncertainty = _take(uncertainty_rows, selected_ids, 3)
    archive_rows = sorted(
        archived_rows,
        key=lambda row: (-_uncertainty(row, total_score_count), row["lesson_id"]),
    )
    archive = _take(archive_rows, selected_ids, 1)
    # THE TENTH SLOT, restored (#626). Filling from the uncertainty ordering
    # rather than leaving the slot empty keeps the preview at ten items when the
    # archive is empty, while the separate count keeps that fact visible.
    archive_fallback = _take(uncertainty_rows, selected_ids, 1 - len(archive))
    selected = recent + value + uncertainty + archive + archive_fallback
    return {
        "kind": KIND,
        "schema_version": SCHEMA_VERSION,
        "mode": "preview",
        "seed": seed,
        "eligible_count": len(rows),
        "bucket_counts": {
            "recent": len(recent),
            "value": len(value),
            "uncertainty": len(uncertainty),
            "archive": len(archive),
            "archive_fallback_uncertainty": len(archive_fallback),
        },
        "items": _shuffled_items(seed, selected),
    }
