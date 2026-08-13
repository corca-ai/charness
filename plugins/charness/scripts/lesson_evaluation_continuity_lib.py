"""Parse and reconcile the repo-local lesson-evaluation lifecycle."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import date, datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from scripts.critique_enforcement_scope import observed_date
from scripts.lesson_ledger_lib import canonical_json

ACTIVATION_DATE = date(2026, 8, 14)
SECTION_HEADING = "## Lesson Evaluation"
LINE_PREFIX = "Lesson evaluation: "
STATUSES = frozenset({"effect-recorded", "no-effect", "not-evaluated"})
REASONS = frozenset({"missing-start", "emission-unproven", "presentation-unproven"})
AGGREGATE_VIOLATION_IDS = (
    "score-count-mismatch",
    "duplicate-session-reference",
    "unclaimed-emission",
)

RECEIPT_KIND = "charness.lesson-session-emission-receipt"
RECEIPT_VERSION = 1
RENDERER_ID = "charness.lesson-session-preview.text.v1"
RECEIPT_DIRNAME = "lesson-session-receipts"
_RECEIPT_BODY_KEYS = {
    "kind",
    "schema_version",
    "session_id",
    "snapshot_sha256",
    "renderer_id",
    "stdout_sha256",
    "stdout_byte_count",
    "emitted_at",
}
_RECEIPT_KEYS = _RECEIPT_BODY_KEYS | {"receipt_sha256"}
_SESSION_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
_DIGEST = re.compile(r"[0-9a-f]{64}")
_FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})")


class LessonEvaluationError(ValueError):
    """A typed authoring or reconciliation contract failure."""


def _fail(message: str) -> None:
    raise LessonEvaluationError(f"lesson evaluation invalid: {message}")


def validate_session_id(session_id: Any) -> str:
    if not isinstance(session_id, str) or not _SESSION_ID.fullmatch(session_id):
        _fail("session_id must be path-safe ASCII alphanumeric with internal `._-`")
    return session_id


def canonical_retro_path(value: Any) -> str:
    if not isinstance(value, str) or not value:
        _fail("retro identity must be a non-empty repo-relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or str(path) != value:
        _fail(f"retro identity `{value}` is not canonical repo-relative POSIX form")
    if len(path.parts) != 3 or path.parts[:2] != ("charness-artifacts", "retro"):
        _fail(f"retro identity `{value}` must name one root-level retro artifact")
    if path.suffix != ".md" or path.name == "recent-lessons.md":
        _fail(f"retro identity `{value}` must name a session markdown artifact")
    return value


def _outside_fence_lines(text: str) -> list[str]:
    output: list[str] = []
    marker: str | None = None
    for raw in text.splitlines():
        match = _FENCE.match(raw)
        if match and marker is None:
            marker = match.group(1)[0]
            output.append("")
        elif match and marker == match.group(1)[0]:
            marker = None
            output.append("")
        else:
            output.append("" if marker else raw)
    return output


def _validate_disposition_value(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail("disposition JSON must be an object")
    status = value.get("status")
    if status not in STATUSES:
        _fail(f"status must be one of {sorted(STATUSES)}")
    expected = {"status", "session_id", "score_event_count"}
    if status == "not-evaluated":
        expected.add("reason")
    if set(value) != expected:
        _fail(f"status `{status}` requires exactly keys {sorted(expected)}")
    count = value.get("score_event_count")
    if type(count) is not int or count < 0:
        _fail("score_event_count must be a nonnegative integer")
    session_id = value.get("session_id")
    reason = value.get("reason")
    if status == "not-evaluated" and reason not in REASONS:
        _fail(f"not-evaluated reason must be one of {sorted(REASONS)}")
    if status == "not-evaluated" and reason == "missing-start":
        if session_id != "none" or count != 0:
            _fail("missing-start requires session_id `none` and score_event_count 0")
    else:
        validate_session_id(session_id)
    if status == "effect-recorded" and count < 1:
        _fail("effect-recorded requires score_event_count >= 1")
    if status == "no-effect" and count != 0:
        _fail("no-effect requires score_event_count 0")
    if status == "not-evaluated" and count != 0:
        _fail("not-evaluated requires score_event_count 0")
    return value


def parse_disposition(text: str) -> dict[str, Any]:
    """Read the one authoritative disposition line from its exact H2 section."""
    lines = _outside_fence_lines(text)
    headings = [index for index, raw in enumerate(lines) if raw.strip() == SECTION_HEADING]
    if len(headings) != 1:
        _fail(f"expected exactly one `{SECTION_HEADING}` section, found {len(headings)}")
    start = headings[0] + 1
    end = next(
        (index for index in range(start, len(lines)) if lines[index].strip().startswith("## ")),
        len(lines),
    )
    matches = [raw.strip() for raw in lines[start:end] if raw.strip().startswith(LINE_PREFIX)]
    all_matches = [raw.strip() for raw in lines if raw.strip().startswith(LINE_PREFIX)]
    if len(matches) != 1 or len(all_matches) != 1:
        _fail(
            f"the artifact must contain exactly one `{LINE_PREFIX}<JSON object>` line, inside `{SECTION_HEADING}`"
        )
    raw_json = matches[0][len(LINE_PREFIX) :]
    if raw_json.startswith(("TODO", "TBD", "<")):
        _fail("lesson disposition placeholder must be replaced")
    try:
        return _validate_disposition_value(json.loads(raw_json))
    except json.JSONDecodeError as exc:
        _fail(f"disposition JSON is invalid: {exc.msg}")


def disposition_line(value: dict[str, Any]) -> str:
    """Render the authoring form after validating it through the real parser."""
    line = LINE_PREFIX + canonical_json(value)
    parse_disposition(f"{SECTION_HEADING}\n\n{line}\n")
    return line


def render_preview_bytes(preview: dict[str, Any]) -> bytes:
    items = preview.get("items")
    eligible = preview.get("eligible_count")
    if not isinstance(items, list) or type(eligible) is not int:
        _fail("renderer needs preview items and integer eligible_count")
    lines = [f"Lesson selection preview ({len(items)}/{eligible} eligible):"]
    for item in items:
        if not isinstance(item, dict):
            _fail("renderer item must be an object")
        lesson_id, lesson = item.get("lesson_id"), item.get("lesson")
        if not isinstance(lesson_id, str) or not isinstance(lesson, str):
            _fail("renderer item needs string lesson_id and lesson")
        lines.append(f"- {lesson_id} — {lesson}")
    return ("\n".join(lines) + "\n").encode("utf-8")


def receipt_directory(output_dir: Path) -> Path:
    return output_dir / RECEIPT_DIRNAME


def receipt_path(output_dir: Path, session_id: str) -> Path:
    return receipt_directory(output_dir) / f"{validate_session_id(session_id)}.json"


def build_receipt(
    *, session_id: str, snapshot_sha256: str, stdout_bytes: bytes, emitted_at: str
) -> dict[str, Any]:
    validate_session_id(session_id)
    if not isinstance(snapshot_sha256, str) or not _DIGEST.fullmatch(snapshot_sha256):
        _fail("snapshot_sha256 must be a lowercase SHA-256 digest")
    try:
        parsed_time = datetime.fromisoformat(emitted_at.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        _fail("emitted_at must be an RFC 3339 timestamp")
    if parsed_time.tzinfo is None:
        _fail("emitted_at must include a timezone")
    body: dict[str, Any] = {
        "kind": RECEIPT_KIND,
        "schema_version": RECEIPT_VERSION,
        "session_id": session_id,
        "snapshot_sha256": snapshot_sha256,
        "renderer_id": RENDERER_ID,
        "stdout_sha256": hashlib.sha256(stdout_bytes).hexdigest(),
        "stdout_byte_count": len(stdout_bytes),
        "emitted_at": emitted_at,
    }
    return {**body, "receipt_sha256": hashlib.sha256(canonical_json(body).encode()).hexdigest()}


def validate_receipt(receipt: Any, *, sessions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(receipt, dict) or set(receipt) != _RECEIPT_KEYS:
        _fail(f"receipt requires exactly keys {sorted(_RECEIPT_KEYS)}")
    session_id = validate_session_id(receipt.get("session_id"))
    if receipt.get("kind") != RECEIPT_KIND or receipt.get("schema_version") != RECEIPT_VERSION:
        _fail("receipt kind or schema_version is unsupported")
    if receipt.get("renderer_id") != RENDERER_ID:
        _fail("receipt renderer_id is unsupported")
    for field in ("snapshot_sha256", "stdout_sha256", "receipt_sha256"):
        if not isinstance(receipt.get(field), str) or not _DIGEST.fullmatch(receipt[field]):
            _fail(f"receipt {field} must be a lowercase SHA-256 digest")
    if type(receipt.get("stdout_byte_count")) is not int or receipt["stdout_byte_count"] < 0:
        _fail("receipt stdout_byte_count must be a nonnegative integer")
    try:
        parsed_time = datetime.fromisoformat(str(receipt.get("emitted_at")).replace("Z", "+00:00"))
    except ValueError:
        _fail("receipt emitted_at must be an RFC 3339 timestamp")
    if parsed_time.tzinfo is None:
        _fail("receipt emitted_at must include a timezone")
    session = sessions.get(session_id)
    if session is None:
        _fail(f"receipt names unknown session `{session_id}`")
    if receipt["snapshot_sha256"] != session.get("snapshot_sha256"):
        _fail(f"receipt snapshot does not match ledger session `{session_id}`")
    body = {key: receipt[key] for key in _RECEIPT_BODY_KEYS}
    expected = hashlib.sha256(canonical_json(body).encode()).hexdigest()
    if receipt["receipt_sha256"] != expected:
        _fail(f"receipt integrity digest does not match session `{session_id}`")
    return receipt


def write_receipt(path: Path, receipt: dict[str, Any]) -> None:
    if path.exists():
        _fail(f"receipt already exists at `{path}`")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
            json.dump(receipt, temporary, ensure_ascii=False, indent=2)
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def is_eligible_retro(path: Path, text: str) -> bool:
    value = observed_date(path, text)
    return value is not None and value >= ACTIVATION_DATE


def violation(identifier: str, *, path: str | None = None, session_id: str | None = None, detail: str) -> dict[str, str]:
    item = {"id": identifier, "detail": detail}
    if path is not None:
        item["path"] = path
    if session_id is not None:
        item["session_id"] = session_id
    return item


def _reconcile_retro_row(
    *,
    path: str,
    disposition: dict[str, Any],
    sessions: dict[str, dict[str, Any]],
    score_events: list[dict[str, Any]],
    receipts: dict[str, dict[str, Any]],
) -> list[dict[str, str]]:
    status = disposition["status"]
    session_id = disposition["session_id"]
    if session_id not in sessions:
        return [
            violation(
                "foreign-session",
                path=path,
                session_id=session_id,
                detail="disposition names no ledger session",
            )
        ]
    matching = [
        event
        for event in score_events
        if event.get("session_id") == session_id and event.get("source_retro") == path
    ]
    session_scores = [event for event in score_events if event.get("session_id") == session_id]
    has_receipt = session_id in receipts
    rows: list[dict[str, str]] = []
    if len(matching) != disposition["score_event_count"]:
        rows.append(
            violation(
                "score-count-mismatch",
                path=path,
                session_id=session_id,
                detail=f"declared {disposition['score_event_count']}, observed {len(matching)}",
            )
        )
    if len(session_scores) != len(matching):
        rows.append(
            violation(
                "foreign-score-source",
                path=path,
                session_id=session_id,
                detail="session has score events cited by another retro path",
            )
        )
    if status in {"effect-recorded", "no-effect"} and not has_receipt:
        rows.append(
            violation(
                "emission-unproven",
                path=path,
                session_id=session_id,
                detail=f"{status} requires a valid emission receipt",
            )
        )
    if status == "effect-recorded" and not matching:
        rows.append(
            violation(
                "effect-recorded-without-score",
                path=path,
                session_id=session_id,
                detail="effect-recorded requires at least one matching score",
            )
        )
    if status == "no-effect" and matching:
        rows.append(
            violation(
                "no-effect-with-score",
                path=path,
                session_id=session_id,
                detail="no-effect requires zero matching scores",
            )
        )
    reason = disposition.get("reason")
    if status == "not-evaluated" and reason == "emission-unproven" and has_receipt:
        rows.append(
            violation(
                "unexpected-emission-proof",
                path=path,
                session_id=session_id,
                detail="emission-unproven cannot cite a valid receipt",
            )
        )
    if status == "not-evaluated" and reason == "presentation-unproven" and not has_receipt:
        rows.append(
            violation(
                "emission-unproven",
                path=path,
                session_id=session_id,
                detail="presentation-unproven requires a valid emission receipt",
            )
        )
    if not has_receipt and session_scores:
        rows.append(
            violation(
                "score-without-emission-proof",
                path=path,
                session_id=session_id,
                detail="receiptless session has score events",
            )
        )
    return rows


def reconcile_records(
    *,
    retros: Iterable[tuple[str, dict[str, Any]]],
    sessions: dict[str, dict[str, Any]],
    score_events: list[dict[str, Any]],
    receipts: dict[str, dict[str, Any]],
    receipt_violations: list[dict[str, str]],
    as_of: date,
) -> dict[str, Any]:
    """Pure reconciliation core used by the CLI and seeded matrix tests."""
    retro_rows = list(retros)
    violations = list(receipt_violations)
    references: dict[str, list[str]] = {}
    status_counts = {status: 0 for status in sorted(STATUSES)}
    total_scores = len(score_events)

    for path, disposition in retro_rows:
        status = disposition["status"]
        status_counts[status] += 1
        session_id = disposition["session_id"]
        if session_id == "none":
            continue
        references.setdefault(session_id, []).append(path)
        violations.extend(
            _reconcile_retro_row(
                path=path,
                disposition=disposition,
                sessions=sessions,
                score_events=score_events,
                receipts=receipts,
            )
        )

    for session_id, paths in references.items():
        if len(paths) > 1:
            violations.append(violation("duplicate-session-reference", session_id=session_id, detail=f"session is cited by {len(paths)} retros: {', '.join(sorted(paths))}"))
    for session_id, receipt in receipts.items():
        emitted = datetime.fromisoformat(receipt["emitted_at"].replace("Z", "+00:00")).date()
        if emitted >= ACTIVATION_DATE and emitted < as_of and session_id not in references:
            violations.append(violation("unclaimed-emission", session_id=session_id, detail=f"receipt from {emitted.isoformat()} has no in-cohort retro disposition"))

    completed = status_counts["effect-recorded"] + status_counts["no-effect"]
    aggregate_violation_counts = {
        identifier: sum(item["id"] == identifier for item in violations)
        for identifier in AGGREGATE_VIOLATION_IDS
    }
    not_evaluated_reasons = {reason: 0 for reason in sorted(REASONS)}
    for _, disposition in retro_rows:
        if disposition["status"] == "not-evaluated":
            not_evaluated_reasons[disposition["reason"]] += 1
    return {
        "kind": "charness.lesson-evaluation-continuity-report",
        "schema_version": 1,
        "activation_date": ACTIVATION_DATE.isoformat(),
        "as_of": as_of.isoformat(),
        "denominator_label": "eligible durable retros",
        "eligible_retro_count": len(retro_rows),
        "disposition_count": len(retro_rows),
        "completed_evaluation_count": completed,
        "status_counts": status_counts,
        "not_evaluated_reason_counts": not_evaluated_reasons,
        "score_event_count": total_scores,
        "aggregate_violation_counts": aggregate_violation_counts,
        "violation_count": len(violations),
        "violations": sorted(violations, key=lambda item: (item["id"], item.get("path", ""), item.get("session_id", ""))),
        "ok": not violations,
    }
