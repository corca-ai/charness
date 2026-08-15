"""Parse and reconcile the repo-local lesson-evaluation lifecycle."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import date, datetime
from pathlib import Path, PurePosixPath
from typing import Any

from scripts.critique_enforcement_scope import observed_date
from scripts.lesson_ledger_lib import canonical_json

ACTIVATION_DATE = date(2026, 8, 14)
SECTION_HEADING = "## Lesson Evaluation"
LINE_PREFIX = "Lesson evaluation: "
STATUSES = frozenset({"effect-recorded", "no-effect", "not-evaluated"})
REASONS = frozenset({"missing-start", "emission-unproven", "presentation-unproven"})
# The keys every disposition carries; `reason` joins them only for
# `not-evaluated`. Named once so the enforcing check and the refusal that
# teaches the grammar cannot drift apart.
BASE_DISPOSITION_KEYS = frozenset({"status", "session_id", "score_event_count"})
# The one disposition a repo that opened no lesson session can honestly write.
MISSING_START_DISPOSITION = {
    "reason": "missing-start",
    "score_event_count": 0,
    "session_id": "none",
    "status": "not-evaluated",
}
AGGREGATE_VIOLATION_IDS = (
    "score-count-mismatch",
    "duplicate-session-reference",
    "unclaimed-emission",
    "unrecurred-encounter",
    "duplicate-encounter",
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


def grammar_summary() -> str:
    """The whole authoring grammar, rendered INTO the refusals that demand it.

    Every rule below already names its own accepted values, but they are
    unreachable for the failure an author actually hits: the FIRST two refusals
    are the section-count and line-count checks in ``parse_disposition``, which
    named ZERO keys and pointed at ``references/lesson-evaluation.md`` -- a file
    that deliberately keeps the grammar repo-owned. The grammar's only prose home
    was ``docs/development.md``, which the plugin does not ship, so a consuming
    author paid two validator round-trips and a source dive to write one line
    (#623). Interpolated from the same constants the checks enforce, so the
    lesson cannot drift from the rule.
    """
    return (
        f"the JSON object takes exactly keys {sorted(BASE_DISPOSITION_KEYS)}, plus `reason` when "
        f"status is `not-evaluated`; status is one of {sorted(STATUSES)}; reason is one of "
        f"{sorted(REASONS)}; `missing-start` requires session_id `none` and score_event_count 0, "
        "`effect-recorded` requires score_event_count >= 1, and `no-effect` / `not-evaluated` "
        "require 0. A repo that opened no lesson session writes exactly: "
        f"`{LINE_PREFIX}{canonical_json(MISSING_START_DISPOSITION)}`"
    )


def _validate_disposition_value(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail("disposition JSON must be an object")
    status = value.get("status")
    if status not in STATUSES:
        _fail(f"status must be one of {sorted(STATUSES)}")
    expected = set(BASE_DISPOSITION_KEYS)
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
        _fail(
            f"expected exactly one `{SECTION_HEADING}` section, found {len(headings)}. "
            f"{grammar_summary()}"
        )
    start = headings[0] + 1
    end = next(
        (index for index in range(start, len(lines)) if lines[index].strip().startswith("## ")),
        len(lines),
    )
    matches = [raw.strip() for raw in lines[start:end] if raw.strip().startswith(LINE_PREFIX)]
    all_matches = [raw.strip() for raw in lines if raw.strip().startswith(LINE_PREFIX)]
    if len(matches) != 1 or len(all_matches) != 1:
        _fail(
            f"the artifact must contain exactly one `{LINE_PREFIX}<JSON object>` line, inside "
            f"`{SECTION_HEADING}`. {grammar_summary()}"
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


def bundle_path(output_dir: Path, session_id: str) -> Path:
    return receipt_directory(output_dir) / f"{validate_session_id(session_id)}.md"


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


def _validated_receipt_bundle(
    receipt: Any, *, sessions: dict[str, dict[str, Any]], output_dir: Path
) -> tuple[dict[str, Any], bytes]:
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
    path = bundle_path(output_dir, session_id)
    try:
        content = path.read_bytes()
    except OSError as exc:
        _fail(f"session bundle is unreadable at `{path}`: {exc}")
    if len(content) != receipt["stdout_byte_count"]:
        _fail(f"session bundle byte count does not match receipt `{session_id}`")
    if hashlib.sha256(content).hexdigest() != receipt["stdout_sha256"]:
        _fail(f"session bundle digest does not match receipt `{session_id}`")
    return receipt, content


def validate_receipt(
    receipt: Any, *, sessions: dict[str, dict[str, Any]], output_dir: Path
) -> dict[str, Any]:
    validated, _content = _validated_receipt_bundle(
        receipt, sessions=sessions, output_dir=output_dir
    )
    return validated


def load_session_bundle(
    receipt: Any, *, sessions: dict[str, dict[str, Any]], output_dir: Path
) -> bytes:
    """Return the exact frozen lesson bytes after receipt and ledger validation."""
    _validated, content = _validated_receipt_bundle(
        receipt, sessions=sessions, output_dir=output_dir
    )
    return content


def _write_once(path: Path, content: bytes, *, label: str) -> None:
    if path.exists() or path.is_symlink():
        _fail(f"{label} already exists at `{path}`")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "wb", dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def write_bundle(path: Path, content: bytes) -> None:
    _write_once(path, content, label="session bundle")


def write_receipt(path: Path, receipt: dict[str, Any]) -> None:
    content = (json.dumps(receipt, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    _write_once(path, content, label="receipt")


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
