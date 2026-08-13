from __future__ import annotations

import copy
import io
import json
import runpy
from datetime import date
from pathlib import Path

import pytest

from scripts import check_lesson_evaluation_continuity as checker
from scripts import lesson_evaluation_continuity_lib as continuity
from scripts import open_lesson_session, validate_retro_artifact


def _disposition(**values: object) -> dict[str, object]:
    return values


def _markdown(value: dict[str, object], *, date_text: str = "2026-08-14") -> str:
    return (
        f"# Session Retro\nDate: {date_text}\n\n"
        "## North Star Alignment\n\n- P1 held.\n\n"
        "## Lesson Evaluation\n\n"
        f"{continuity.LINE_PREFIX}{json.dumps(value, sort_keys=True)}\n\n"
        "## Next Improvements\n\n- workflow: do it\n\n"
        "## Persisted\n\nPersisted: yes: charness-artifacts/retro/example.md\n"
    )


@pytest.mark.parametrize(
    "value",
    [
        _disposition(status="effect-recorded", session_id="s-1", score_event_count=1),
        _disposition(status="no-effect", session_id="s-1", score_event_count=0),
        _disposition(
            status="not-evaluated",
            reason="missing-start",
            session_id="none",
            score_event_count=0,
        ),
        _disposition(
            status="not-evaluated",
            reason="emission-unproven",
            session_id="s-1",
            score_event_count=0,
        ),
        _disposition(
            status="not-evaluated",
            reason="presentation-unproven",
            session_id="s-1",
            score_event_count=0,
        ),
    ],
)
def test_disposition_parser_accepts_only_truth_table_rows(value: dict[str, object]) -> None:
    assert continuity.parse_disposition(_markdown(value)) == value


@pytest.mark.parametrize(
    ("value", "message"),
    [
        (_disposition(status="effect-recorded", session_id="s", score_event_count=0), ">= 1"),
        (_disposition(status="no-effect", session_id="s", score_event_count=1), "requires score_event_count 0"),
        (
            _disposition(
                status="not-evaluated",
                reason="missing-start",
                session_id="s",
                score_event_count=0,
            ),
            "session_id `none`",
        ),
        (
            _disposition(
                status="not-evaluated",
                reason="emission-unproven",
                session_id="s",
                score_event_count=0,
                extra=True,
            ),
            "requires exactly keys",
        ),
    ],
)
def test_disposition_parser_rejects_impossible_states(
    value: dict[str, object], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        continuity.parse_disposition(_markdown(value))


def test_disposition_parser_rejects_duplicate_misplaced_and_placeholder_lines() -> None:
    valid = continuity.disposition_line(
        {"status": "no-effect", "session_id": "s", "score_event_count": 0}
    )
    with pytest.raises(ValueError, match="exactly one"):
        continuity.parse_disposition(
            f"## Lesson Evaluation\n\n{valid}\n\n## Lesson Evaluation\n\n{valid}\n"
        )
    with pytest.raises(ValueError, match="exactly one"):
        continuity.parse_disposition(f"## Context\n\n{valid}\n")
    with pytest.raises(ValueError, match="placeholder"):
        continuity.parse_disposition(
            "## Lesson Evaluation\n\nLesson evaluation: TODO choose a disposition\n"
        )


def test_disposition_parser_allows_explanatory_prose_but_not_a_second_machine_line() -> None:
    valid = continuity.disposition_line(
        {"status": "no-effect", "session_id": "s", "score_event_count": 0}
    )
    assert continuity.parse_disposition(
        f"## Lesson Evaluation\n\nAffirmatively reviewed; no effect observed.\n\n{valid}\n"
    )["status"] == "no-effect"
    with pytest.raises(ValueError, match="exactly one"):
        continuity.parse_disposition(
            f"## Lesson Evaluation\n\n{valid}\n\n## Context\n\n{valid}\n"
        )


def test_receipt_binds_ledger_snapshot_renderer_bytes_and_integrity(tmp_path: Path) -> None:
    stdout = "Lesson selection preview (1/1 eligible):\n- a — 안녕\n".encode()
    snapshot = "a" * 64
    receipt = continuity.build_receipt(
        session_id="s-1",
        snapshot_sha256=snapshot,
        stdout_bytes=stdout,
        emitted_at="2026-08-14T00:00:00Z",
    )
    continuity.write_bundle(continuity.bundle_path(tmp_path, "s-1"), stdout)
    assert receipt["stdout_byte_count"] == len(stdout)
    assert continuity.validate_receipt(
        receipt, sessions={"s-1": {"snapshot_sha256": snapshot}}, output_dir=tmp_path
    ) == receipt
    assert continuity.load_session_bundle(
        receipt, sessions={"s-1": {"snapshot_sha256": snapshot}}, output_dir=tmp_path
    ) == stdout

    for field, value in (("snapshot_sha256", "b" * 64), ("renderer_id", "changed"), ("stdout_byte_count", 1)):
        tampered = copy.deepcopy(receipt)
        tampered[field] = value
        with pytest.raises(ValueError):
            continuity.validate_receipt(
                tampered,
                sessions={"s-1": {"snapshot_sha256": snapshot}},
                output_dir=tmp_path,
            )


def test_open_session_writes_exact_bytes_before_atomic_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    snapshot = "a" * 64
    event = {"session_id": "s-1", "snapshot_sha256": snapshot}
    preview = {
        "eligible_count": 1,
        "items": [{"lesson_id": "a", "lesson": "lesson text"}],
    }
    monkeypatch.setattr(
        open_lesson_session._session,
        "declare_session",
        lambda **_kwargs: (event, preview),
    )
    stdout = io.BytesIO()
    result = open_lesson_session.open_session(
        repo_root=tmp_path,
        session_id="s-1",
        seed="seed",
        stdout=stdout,
        emitted_at="2026-08-14T00:00:00Z",
    )
    expected = continuity.render_preview_bytes(preview)
    assert stdout.getvalue() == expected
    bundle = tmp_path / result["bundle_path"]
    assert bundle.read_bytes() == expected
    path = tmp_path / result["receipt_path"]
    assert path.is_file()
    receipt = json.loads(path.read_text(encoding="utf-8"))
    assert continuity.validate_receipt(
        receipt,
        sessions={"s-1": event},
        output_dir=tmp_path / "charness-artifacts/retro",
    ) == receipt


def test_open_session_broken_stdout_never_writes_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    event = {"session_id": "s-1", "snapshot_sha256": "a" * 64}
    preview = {"eligible_count": 0, "items": []}
    monkeypatch.setattr(
        open_lesson_session._session,
        "declare_session",
        lambda **_kwargs: (event, preview),
    )

    class Broken:
        def write(self, _payload: bytes) -> None:
            raise BrokenPipeError("closed")

        def flush(self) -> None:
            raise AssertionError("flush must not follow failed write")

    with pytest.raises(BrokenPipeError):
        open_lesson_session.open_session(
            repo_root=tmp_path, session_id="s-1", seed="seed", stdout=Broken()
        )
    assert not continuity.receipt_path(
        tmp_path / "charness-artifacts/retro", "s-1"
    ).exists()
    assert continuity.bundle_path(
        tmp_path / "charness-artifacts/retro", "s-1"
    ).is_file()


def test_open_session_failed_flush_never_writes_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    event = {"session_id": "s-1", "snapshot_sha256": "a" * 64}
    preview = {"eligible_count": 0, "items": []}
    monkeypatch.setattr(
        open_lesson_session._session,
        "declare_session",
        lambda **_kwargs: (event, preview),
    )

    class FlushFails(io.BytesIO):
        def flush(self) -> None:
            raise OSError("flush failed")

    with pytest.raises(OSError, match="flush failed"):
        open_lesson_session.open_session(
            repo_root=tmp_path, session_id="s-1", seed="seed", stdout=FlushFails()
        )
    assert not continuity.receipt_path(
        tmp_path / "charness-artifacts/retro", "s-1"
    ).exists()
    assert continuity.bundle_path(
        tmp_path / "charness-artifacts/retro", "s-1"
    ).is_file()


def test_open_session_completes_short_writes_before_receipting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    event = {"session_id": "s-1", "snapshot_sha256": "a" * 64}
    preview = {"eligible_count": 1, "items": [{"lesson_id": "a", "lesson": "lesson"}]}
    monkeypatch.setattr(
        open_lesson_session._session,
        "declare_session",
        lambda **_kwargs: (event, preview),
    )

    class ShortWriter:
        def __init__(self) -> None:
            self.data = bytearray()

        def write(self, payload: bytes) -> int:
            amount = min(3, len(payload))
            self.data.extend(payload[:amount])
            return amount

        def flush(self) -> None:
            pass

    stdout = ShortWriter()
    open_lesson_session.open_session(
        repo_root=tmp_path,
        session_id="s-1",
        seed="seed",
        stdout=stdout,
        emitted_at="2026-08-14T00:00:00Z",
    )
    assert bytes(stdout.data) == continuity.render_preview_bytes(preview)


def test_open_session_rejects_unsafe_id_before_declaration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    called = False

    def declare(**_kwargs: object) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(open_lesson_session._session, "declare_session", declare)
    with pytest.raises(ValueError, match="path-safe"):
        open_lesson_session.open_session(
            repo_root=tmp_path,
            session_id="../../bad",
            seed="seed",
            stdout=io.BytesIO(),
        )
    assert called is False
    assert not (tmp_path / "charness-artifacts").exists()


@pytest.mark.parametrize("kind", ["receipt", "bundle"])
def test_atomic_replace_failure_leaves_no_output_or_temp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, kind: str
) -> None:
    path = tmp_path / "receipts" / ("s-1.json" if kind == "receipt" else "s-1.md")
    def replace_error(*_args: object) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr(continuity.os, "replace", replace_error)

    with pytest.raises(OSError, match="replace failed"):
        if kind == "receipt":
            continuity.write_receipt(path, _receipt())
        else:
            continuity.write_bundle(path, b"preview\n")

    assert not path.exists()
    assert not list(path.parent.glob(f".{path.name}.*"))


def _receipt(session_id: str = "s-1", emitted_at: str = "2026-08-14T00:00:00Z") -> dict:
    return continuity.build_receipt(
        session_id=session_id,
        snapshot_sha256="a" * 64,
        stdout_bytes=b"preview\n",
        emitted_at=emitted_at,
    )


def _write_bundle(output: Path, session_id: str = "s-1") -> None:
    path = continuity.bundle_path(output, session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"preview\n")


def test_reconciler_keeps_disposition_health_separate_from_score_volume() -> None:
    sessions = {"s-1": {"snapshot_sha256": "a" * 64}}
    clean = continuity.reconcile_records(
        retros=[
            (
                "charness-artifacts/retro/2026-08-14-a.md",
                {"status": "no-effect", "session_id": "s-1", "score_event_count": 0},
            )
        ],
        sessions=sessions,
        score_events=[],
        receipts={"s-1": _receipt()},
        receipt_violations=[],
        as_of=date(2026, 8, 14),
    )
    assert clean["ok"] is True
    assert clean["completed_evaluation_count"] == 1
    assert clean["score_event_count"] == 0


def test_presentation_unproven_requires_receipt_and_remains_visible() -> None:
    row = (
        "charness-artifacts/retro/2026-08-14-a.md",
        {
            "status": "not-evaluated",
            "reason": "presentation-unproven",
            "session_id": "s-1",
            "score_event_count": 0,
        },
    )
    sessions = {"s-1": {"snapshot_sha256": "a" * 64}}
    clean = continuity.reconcile_records(
        retros=[row],
        sessions=sessions,
        score_events=[],
        receipts={"s-1": _receipt()},
        receipt_violations=[],
        as_of=date(2026, 8, 14),
    )
    assert clean["ok"] is True
    assert clean["not_evaluated_reason_counts"]["presentation-unproven"] == 1
    assert clean["completed_evaluation_count"] == 0

    missing = continuity.reconcile_records(
        retros=[row],
        sessions=sessions,
        score_events=[],
        receipts={},
        receipt_violations=[],
        as_of=date(2026, 8, 14),
    )
    assert "emission-unproven" in {item["id"] for item in missing["violations"]}


@pytest.mark.parametrize(
    ("disposition", "scores", "with_receipt", "reason_count"),
    [
        (
            {"status": "effect-recorded", "session_id": "s-1", "score_event_count": 1},
            [{"session_id": "s-1", "source_retro": "charness-artifacts/retro/2026-08-14-a.md"}],
            True,
            None,
        ),
        (
            {"status": "no-effect", "session_id": "s-1", "score_event_count": 0},
            [],
            True,
            None,
        ),
        (
            {"status": "not-evaluated", "reason": "missing-start", "session_id": "none", "score_event_count": 0},
            [],
            False,
            "missing-start",
        ),
        (
            {"status": "not-evaluated", "reason": "emission-unproven", "session_id": "s-1", "score_event_count": 0},
            [],
            False,
            "emission-unproven",
        ),
        (
            {"status": "not-evaluated", "reason": "presentation-unproven", "session_id": "s-1", "score_event_count": 0},
            [],
            True,
            "presentation-unproven",
        ),
    ],
)
def test_reconciler_accepts_each_complete_truth_table_row(
    disposition: dict[str, object],
    scores: list[dict[str, str]],
    with_receipt: bool,
    reason_count: str | None,
) -> None:
    sessions = {"s-1": {"snapshot_sha256": "a" * 64}}
    report = continuity.reconcile_records(
        retros=[("charness-artifacts/retro/2026-08-14-a.md", disposition)],
        sessions=sessions,
        score_events=scores,
        receipts={"s-1": _receipt()} if with_receipt else {},
        receipt_violations=[],
        as_of=date(2026, 8, 14),
    )
    assert report["ok"] is True, report["violations"]
    if reason_count is not None:
        assert report["not_evaluated_reason_counts"][reason_count] == 1


def test_pre_activation_and_same_day_receipts_are_not_unclaimed() -> None:
    sessions = {
        "old": {"snapshot_sha256": "a" * 64},
        "today": {"snapshot_sha256": "a" * 64},
    }
    report = continuity.reconcile_records(
        retros=[],
        sessions=sessions,
        score_events=[],
        receipts={
            "old": _receipt("old", "2026-08-13T23:59:59Z"),
            "today": _receipt("today", "2026-08-15T00:00:00Z"),
        },
        receipt_violations=[],
        as_of=date(2026, 8, 15),
    )
    assert report["ok"] is True


def test_reconciler_names_duplicate_receiptless_score_and_unclaimed_emission() -> None:
    retros = [
        (
            "charness-artifacts/retro/2026-08-14-a.md",
            {
                "status": "not-evaluated",
                "reason": "emission-unproven",
                "session_id": "s-1",
                "score_event_count": 0,
            },
        ),
        (
            "charness-artifacts/retro/2026-08-14-b.md",
            {"status": "no-effect", "session_id": "s-1", "score_event_count": 0},
        ),
    ]
    report = continuity.reconcile_records(
        retros=retros,
        sessions={
            "s-1": {"snapshot_sha256": "a" * 64},
            "orphan": {"snapshot_sha256": "a" * 64},
        },
        score_events=[
            {
                "session_id": "s-1",
                "source_retro": "charness-artifacts/retro/other.md",
            }
        ],
        receipts={"orphan": _receipt("orphan")},
        receipt_violations=[],
        as_of=date(2026, 8, 15),
    )
    ids = {item["id"] for item in report["violations"]}
    assert {
        "duplicate-session-reference",
        "score-without-emission-proof",
        "foreign-score-source",
        "unclaimed-emission",
    } <= ids
    assert report["aggregate_violation_counts"] == {
        "score-count-mismatch": 0,
        "duplicate-session-reference": 1,
        "unclaimed-emission": 1,
    }


def test_retro_validator_activates_on_later_filename_or_body_date(tmp_path: Path) -> None:
    path = tmp_path / "2026-08-14-demo.md"
    path.write_text(
        _markdown(
            {"status": "no-effect", "session_id": "s", "score_event_count": 0},
            date_text="2026-01-01",
        ),
        encoding="utf-8",
    )
    validate_retro_artifact.validate_retro_artifact(path)

    missing = tmp_path / "2026-08-14-missing.md"
    missing.write_text(
        _markdown(
            {"status": "no-effect", "session_id": "s", "score_event_count": 0}
        ).replace("## Lesson Evaluation", "## Omitted"),
        encoding="utf-8",
    )
    with pytest.raises(validate_retro_artifact.ValidationError, match="Lesson Evaluation"):
        validate_retro_artifact.validate_retro_artifact(missing)

    body_later = tmp_path / "2026-01-01-body-later.md"
    body_later.write_text(
        _markdown(
            {"status": "no-effect", "session_id": "s", "score_event_count": 0},
            date_text="2026-08-14",
        ).replace("## Lesson Evaluation", "## Omitted"),
        encoding="utf-8",
    )
    with pytest.raises(validate_retro_artifact.ValidationError, match="Lesson Evaluation"):
        validate_retro_artifact.validate_retro_artifact(body_later)


def test_retro_validator_grandfathers_pre_activation_artifact(tmp_path: Path) -> None:
    path = tmp_path / "2026-08-13-old.md"
    path.write_text(
        "# Session Retro\nDate: 2026-08-13\n\n"
        "## North Star Alignment\n\n- P1 held.\n\n"
        "## Next Improvements\n\n- workflow: do it\n\n"
        "## Persisted\n\nPersisted: yes: charness-artifacts/retro/2026-08-13-old.md\n",
        encoding="utf-8",
    )
    validate_retro_artifact.validate_retro_artifact(path)


def test_reporter_on_disk_cohort_preserves_denominator_and_human_json_fields(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "charness-artifacts/retro"
    output.mkdir(parents=True)
    retro_path = output / "2026-08-14-demo.md"
    retro_path.write_text(
        _markdown({"status": "no-effect", "session_id": "s-1", "score_event_count": 0}),
        encoding="utf-8",
    )
    (output / "undated-legacy.md").write_text("# Legacy\n", encoding="utf-8")
    event = {"session_id": "s-1", "snapshot_sha256": "a" * 64}
    (output / "lesson-ledger.json").write_text(
        json.dumps(
            {
                "session_events": [event],
                "score_events": [],
            }
        ),
        encoding="utf-8",
    )
    receipt = _receipt()
    path = continuity.receipt_path(output, "s-1")
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(receipt), encoding="utf-8")
    _write_bundle(output)
    monkeypatch.setattr(checker._ledger, "validate_lesson_ledger", lambda **_kwargs: {})

    report = checker.build_report(tmp_path, as_of=date(2026, 8, 14))
    human = checker.render_human(report)

    assert report["ok"] is True
    assert report["eligible_retro_count"] == 1
    assert report["disposition_count"] == 1
    assert report["score_event_count"] == 0
    summary_lines = human.splitlines()
    assert len(summary_lines) == 1
    assert "eligible durable retros=1" in summary_lines[0]
    assert "score events (not a health measure)=0" in summary_lines[0]
    assert "presentation-unproven=0" in summary_lines[0]


def test_reporter_skips_generated_digest_and_prepare_packet(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "charness-artifacts/retro"
    output.mkdir(parents=True)
    (output / "recent-lessons.md").write_text("# Digest\n", encoding="utf-8")
    packet = output / "2026-08-14-packet.md"
    packet.write_text("# Retro Prepare Packet\n", encoding="utf-8")
    (output / "lesson-ledger.json").write_text(
        json.dumps(
            {
                "session_events": [],
                "score_events": [],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(checker._ledger, "validate_lesson_ledger", lambda **_kwargs: {})
    monkeypatch.setattr(
        checker._packet,
        "file_is_prepare_packet_markdown_kind",
        lambda path, **_kwargs: path == packet,
    )
    assert checker.build_report(tmp_path, as_of=date(2026, 8, 15))["eligible_retro_count"] == 0


def test_reporter_rejects_receipt_filename_session_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "charness-artifacts/retro"
    output.mkdir(parents=True)
    (output / "lesson-ledger.json").write_text(
        json.dumps(
            {
                "session_events": [{"session_id": "s-1", "snapshot_sha256": "a" * 64}],
                "score_events": [],
            }
        ),
        encoding="utf-8",
    )
    receipt_path = continuity.receipt_directory(output) / "wrong-name.json"
    receipt_path.parent.mkdir(parents=True)
    receipt_path.write_text(json.dumps(_receipt()), encoding="utf-8")
    monkeypatch.setattr(checker._ledger, "validate_lesson_ledger", lambda **_kwargs: {})

    report = checker.build_report(tmp_path, as_of=date(2026, 8, 15))

    assert report["violations"][0]["id"] == "invalid-receipt"
    assert "filename does not match" in report["violations"][0]["detail"]


def test_reporter_names_missing_disposition_and_invalid_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "charness-artifacts/retro"
    output.mkdir(parents=True)
    (output / "2026-08-14-missing.md").write_text(
        "# Session Retro\nDate: 2026-08-14\n\n## North Star Alignment\n\n- P1 held.\n",
        encoding="utf-8",
    )
    (output / "lesson-ledger.json").write_text(
        json.dumps(
            {
                "session_events": [{"session_id": "s-1", "snapshot_sha256": "a" * 64}],
                "score_events": [],
            }
        ),
        encoding="utf-8",
    )
    receipt_path = continuity.receipt_path(output, "s-1")
    receipt_path.parent.mkdir(parents=True)
    receipt_path.write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(checker._ledger, "validate_lesson_ledger", lambda **_kwargs: {})

    report = checker.build_report(tmp_path, as_of=date(2026, 8, 15))

    assert report["ok"] is False
    assert report["eligible_retro_count"] == 1
    assert report["disposition_count"] == 0
    assert {item["id"] for item in report["violations"]} >= {
        "missing-disposition",
        "invalid-receipt",
    }


def test_reconciler_names_foreign_session_and_score_count_mismatch() -> None:
    report = continuity.reconcile_records(
        retros=[
            (
                "charness-artifacts/retro/2026-08-14-foreign.md",
                {"status": "no-effect", "session_id": "foreign", "score_event_count": 0},
            ),
            (
                "charness-artifacts/retro/2026-08-14-mismatch.md",
                {"status": "effect-recorded", "session_id": "s-1", "score_event_count": 1},
            ),
        ],
        sessions={"s-1": {"snapshot_sha256": "a" * 64}},
        score_events=[],
        receipts={"s-1": _receipt()},
        receipt_violations=[],
        as_of=date(2026, 8, 14),
    )

    assert {item["id"] for item in report["violations"]} >= {
        "foreign-session",
        "score-count-mismatch",
    }


def test_many_scores_incomplete_is_not_healthier_than_zero_score_complete() -> None:
    path = "charness-artifacts/retro/2026-08-14-a.md"
    sessions = {"s-1": {"snapshot_sha256": "a" * 64}}
    complete = continuity.reconcile_records(
        retros=[(path, {"status": "no-effect", "session_id": "s-1", "score_event_count": 0})],
        sessions=sessions,
        score_events=[],
        receipts={"s-1": _receipt()},
        receipt_violations=[],
        as_of=date(2026, 8, 14),
    )
    incomplete = continuity.reconcile_records(
        retros=[(path, {"status": "effect-recorded", "session_id": "s-1", "score_event_count": 1})],
        sessions=sessions,
        score_events=[{"session_id": "s-1", "source_retro": path} for _ in range(5)],
        receipts={"s-1": _receipt()},
        receipt_violations=[],
        as_of=date(2026, 8, 14),
    )

    assert complete["ok"] is True
    assert complete["score_event_count"] == 0
    assert incomplete["ok"] is False
    assert incomplete["score_event_count"] == 5
    assert incomplete["aggregate_violation_counts"]["score-count-mismatch"] == 1
    assert "violations=0" in checker.render_human(complete).splitlines()[0]
    assert "score-count-mismatch=1" in checker.render_human(incomplete).splitlines()[0]
    assert "violations=1" in checker.render_human(incomplete).splitlines()[0]


def test_cli_json_snapshot_and_exit_status(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output = tmp_path / "charness-artifacts/retro"
    output.mkdir(parents=True)
    retro_path = output / "2026-08-14-demo.md"
    retro_path.write_text(
        _markdown({"status": "no-effect", "session_id": "s-1", "score_event_count": 0}),
        encoding="utf-8",
    )
    (output / "lesson-ledger.json").write_text(
        json.dumps(
            {
                "session_events": [{"session_id": "s-1", "snapshot_sha256": "a" * 64}],
                "score_events": [],
            }
        ),
        encoding="utf-8",
    )
    receipt_path = continuity.receipt_path(output, "s-1")
    receipt_path.parent.mkdir(parents=True)
    receipt_path.write_text(json.dumps(_receipt()), encoding="utf-8")
    _write_bundle(output)
    monkeypatch.setattr(checker._ledger, "validate_lesson_ledger", lambda **_kwargs: {})
    monkeypatch.setattr(
        checker.sys,
        "argv",
        ["check_lesson_evaluation_continuity.py", "--repo-root", str(tmp_path), "--as-of", "2026-08-14", "--json"],
    )

    assert checker.main() == 0
    clean = json.loads(capsys.readouterr().out)
    assert clean["denominator_label"] == "eligible durable retros"
    assert clean["eligible_retro_count"] == clean["disposition_count"] == 1
    assert clean["aggregate_violation_counts"] == {
        "score-count-mismatch": 0,
        "duplicate-session-reference": 0,
        "unclaimed-emission": 0,
    }
    assert clean["violation_count"] == 0

    retro_path.write_text(
        _markdown({"status": "no-effect", "session_id": "s-1", "score_event_count": 0}).replace(
            "## Lesson Evaluation", "## Omitted"
        ),
        encoding="utf-8",
    )
    assert checker.main() == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["eligible_retro_count"] == 1
    assert blocked["disposition_count"] == 0
    assert {item["id"] for item in blocked["violations"]} == {"missing-disposition"}

    retro_path.write_text(
        _markdown({"status": "effect-recorded", "session_id": "s-1", "score_event_count": 1}),
        encoding="utf-8",
    )
    assert checker.main() == 1
    mismatch = json.loads(capsys.readouterr().out)
    assert mismatch["aggregate_violation_counts"]["score-count-mismatch"] == 1
    assert {item["id"] for item in mismatch["violations"]} == {
        "effect-recorded-without-score",
        "score-count-mismatch",
    }


def test_reporter_cli_human_output_and_error_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    clean = continuity.reconcile_records(
        retros=[],
        sessions={},
        score_events=[],
        receipts={},
        receipt_violations=[],
        as_of=date(2026, 8, 14),
    )
    monkeypatch.setattr(checker, "build_report", lambda *_args, **_kwargs: clean)
    monkeypatch.setattr(
        checker.sys,
        "argv",
        ["check_lesson_evaluation_continuity.py", "--repo-root", str(tmp_path)],
    )
    assert checker.main() == 0
    assert capsys.readouterr().out.startswith("Lesson evaluation continuity:")

    monkeypatch.setattr(
        checker,
        "build_report",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("bad ledger")),
    )
    assert checker.main() == 1
    assert "bad ledger" in capsys.readouterr().err


def test_reporter_script_entrypoint_returns_nonzero_for_missing_repo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        checker.sys,
        "argv",
        ["check_lesson_evaluation_continuity.py", "--repo-root", str(tmp_path)],
    )
    with pytest.raises(SystemExit) as caught:
        runpy.run_path(str(Path(checker.__file__)), run_name="__main__")
    assert caught.value.code == 1


def test_open_session_cli_main_delegates_arguments(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: dict[str, object] = {}

    def fake_open_session(**kwargs: object) -> dict[str, object]:
        seen.update(kwargs)
        return {}

    monkeypatch.setattr(open_lesson_session, "open_session", fake_open_session)
    monkeypatch.setattr(
        open_lesson_session.sys,
        "argv",
        [
            "open_lesson_session.py",
            "--repo-root",
            str(tmp_path),
            "--session-id",
            "s-1",
            "--seed",
            "seed",
        ],
    )
    assert open_lesson_session.main() == 0
    assert seen["repo_root"] == tmp_path.resolve()
    assert seen["session_id"] == "s-1"
    assert seen["seed"] == "seed"


def test_open_session_script_entrypoint_reports_operational_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        open_lesson_session.sys,
        "argv",
        [
            "open_lesson_session.py",
            "--repo-root",
            str(tmp_path),
            "--session-id",
            "s-1",
            "--seed",
            "seed",
        ],
    )
    with pytest.raises(SystemExit) as caught:
        runpy.run_path(str(Path(open_lesson_session.__file__)), run_name="__main__")
    assert caught.value.code == 1
    assert capsys.readouterr().err
