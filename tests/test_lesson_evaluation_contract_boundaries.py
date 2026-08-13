from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from scripts import lesson_evaluation_continuity_lib as continuity
from scripts import open_lesson_session


def _receipt() -> dict[str, object]:
    return continuity.build_receipt(
        session_id="s-1",
        snapshot_sha256="a" * 64,
        stdout_bytes=b"preview\n",
        emitted_at="2026-08-14T00:00:00Z",
    )


@pytest.mark.parametrize(
    ("bundle_bytes", "message"),
    [
        (None, "session bundle is unreadable"),
        (b"short\n", "session bundle byte count does not match receipt"),
        (b"PREVIEW\n", "session bundle digest does not match receipt"),
    ],
)
def test_validate_receipt_rejects_missing_or_tampered_bundle(
    tmp_path: Path, bundle_bytes: bytes | None, message: str
) -> None:
    receipt = _receipt()
    if bundle_bytes is not None:
        continuity.write_bundle(continuity.bundle_path(tmp_path, "s-1"), bundle_bytes)

    with pytest.raises(continuity.LessonEvaluationError, match=message):
        continuity.validate_receipt(
            receipt,
            sessions={"s-1": {"snapshot_sha256": "a" * 64}},
            output_dir=tmp_path,
        )


@pytest.mark.parametrize(
    ("value", "message"),
    [
        (None, "must be an object"),
        ({"status": "unknown"}, "status must be one of"),
        (
            {"status": "no-effect", "session_id": "s", "score_event_count": True},
            "nonnegative integer",
        ),
        (
            {
                "status": "not-evaluated",
                "reason": "unknown",
                "session_id": "s",
                "score_event_count": 0,
            },
            "reason must be one of",
        ),
        (
            {
                "status": "not-evaluated",
                "reason": "emission-unproven",
                "session_id": "s",
                "score_event_count": 1,
            },
            "score_event_count 0",
        ),
    ],
)
def test_disposition_parser_rejects_invalid_json_values(
    value: object, message: str
) -> None:
    text = f"{continuity.SECTION_HEADING}\n\n{continuity.LINE_PREFIX}{json.dumps(value)}\n"
    with pytest.raises(ValueError, match=message):
        continuity.parse_disposition(text)


def test_disposition_parser_ignores_machine_lines_inside_fences() -> None:
    valid = continuity.disposition_line(
        {"status": "no-effect", "session_id": "s", "score_event_count": 0}
    )
    text = (
        "```json\n"
        f"{continuity.LINE_PREFIX}{{}}\n"
        "```\n\n"
        f"{continuity.SECTION_HEADING}\n\n{valid}\n"
    )
    assert continuity.parse_disposition(text)["status"] == "no-effect"


def test_disposition_parser_rejects_malformed_json() -> None:
    text = f"{continuity.SECTION_HEADING}\n\n{continuity.LINE_PREFIX}{{bad}}\n"
    with pytest.raises(ValueError, match="JSON is invalid"):
        continuity.parse_disposition(text)


@pytest.mark.parametrize(
    ("value", "message"),
    [
        (None, "non-empty"),
        ("/absolute.md", "canonical"),
        ("charness-artifacts/retro/../bad.md", "canonical"),
        ("docs/retro/demo.md", "root-level retro"),
        ("charness-artifacts/retro/recent-lessons.md", "session markdown"),
        ("charness-artifacts/retro/demo.txt", "session markdown"),
    ],
)
def test_canonical_retro_path_rejects_noncanonical_identity(
    value: object, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        continuity.canonical_retro_path(value)


def test_canonical_retro_path_accepts_root_session_markdown() -> None:
    value = "charness-artifacts/retro/2026-08-14-demo.md"
    assert continuity.canonical_retro_path(value) == value


@pytest.mark.parametrize(
    "preview",
    [
        {},
        {"items": [], "eligible_count": True},
        {"items": ["bad"], "eligible_count": 1},
        {"items": [{}], "eligible_count": 1},
    ],
)
def test_preview_renderer_rejects_malformed_snapshot(preview: dict[str, object]) -> None:
    with pytest.raises(ValueError, match="renderer"):
        continuity.render_preview_bytes(preview)


@pytest.mark.parametrize(
    ("snapshot", "emitted_at", "message"),
    [
        ("bad", "2026-08-14T00:00:00Z", "snapshot_sha256"),
        ("a" * 64, "not-a-time", "RFC 3339"),
        ("a" * 64, "2026-08-14T00:00:00", "timezone"),
    ],
)
def test_build_receipt_rejects_invalid_snapshot_or_time(
    snapshot: str, emitted_at: str, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        continuity.build_receipt(
            session_id="s-1",
            snapshot_sha256=snapshot,
            stdout_bytes=b"preview\n",
            emitted_at=emitted_at,
        )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("kind", "wrong", "unsupported"),
        ("snapshot_sha256", "bad", "lowercase SHA-256"),
        ("stdout_byte_count", -1, "nonnegative integer"),
        ("emitted_at", "not-a-time", "RFC 3339"),
        ("emitted_at", "2026-08-14T00:00:00", "timezone"),
    ],
)
def test_validate_receipt_rejects_invalid_contract_fields(
    tmp_path: Path, field: str, value: object, message: str
) -> None:
    receipt = _receipt()
    continuity.write_bundle(continuity.bundle_path(tmp_path, "s-1"), b"preview\n")
    receipt[field] = value
    with pytest.raises(ValueError, match=message):
        continuity.validate_receipt(
            receipt,
            sessions={"s-1": {"snapshot_sha256": "a" * 64}},
            output_dir=tmp_path,
        )


def test_validate_receipt_rejects_unknown_session(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown session"):
        continuity.validate_receipt(_receipt(), sessions={}, output_dir=tmp_path)


@pytest.mark.parametrize("progress", [None, 0, True, 999])
def test_open_session_rejects_invalid_stdout_progress(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, progress: object
) -> None:
    event = {"session_id": "s-1", "snapshot_sha256": "a" * 64}
    preview = {"eligible_count": 0, "items": []}
    monkeypatch.setattr(
        open_lesson_session._session,
        "declare_session",
        lambda **_kwargs: (event, preview),
    )

    class InvalidWriter:
        def write(self, _payload: bytes) -> object:
            return progress

        def flush(self) -> None:
            raise AssertionError("flush must not follow invalid write progress")

    with pytest.raises(OSError, match="no valid write progress"):
        open_lesson_session.open_session(
            repo_root=tmp_path,
            session_id="s-1",
            seed="seed",
            stdout=InvalidWriter(),
        )


def test_receipt_writer_refuses_overwrite(tmp_path: Path) -> None:
    path = tmp_path / "receipts" / "s-1.json"
    path.parent.mkdir(parents=True)
    path.write_text("existing\n", encoding="utf-8")
    with pytest.raises(ValueError, match="already exists"):
        continuity.write_receipt(path, _receipt())


@pytest.mark.parametrize(
    ("disposition", "scores", "violation_id"),
    [
        (
            {"status": "no-effect", "session_id": "s-1", "score_event_count": 0},
            [
                {
                    "session_id": "s-1",
                    "source_retro": "charness-artifacts/retro/2026-08-14-a.md",
                }
            ],
            "no-effect-with-score",
        ),
        (
            {
                "status": "not-evaluated",
                "reason": "emission-unproven",
                "session_id": "s-1",
                "score_event_count": 0,
            },
            [],
            "unexpected-emission-proof",
        ),
    ],
)
def test_reconciler_rejects_contradictory_disposition_evidence(
    disposition: dict[str, object],
    scores: list[dict[str, str]],
    violation_id: str,
) -> None:
    report = continuity.reconcile_records(
        retros=[("charness-artifacts/retro/2026-08-14-a.md", disposition)],
        sessions={"s-1": {"snapshot_sha256": "a" * 64}},
        score_events=scores,
        receipts={"s-1": _receipt()},
        receipt_violations=[],
        as_of=date(2026, 8, 14),
    )
    assert violation_id in {item["id"] for item in report["violations"]}
