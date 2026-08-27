"""The lesson-evaluation READ side: disposition grammar, reconciliation, gate CLI.

What the optional lesson-continuity checker reports and exits with, and what the
reconciler concludes when lesson claims are checked against the ledger's sessions,
receipts and score events. The default and release retro contracts do not require
this optional section.

The counterpart WRITE side -- `open_lesson_session` emitting preview bytes and the
receipt/bundle that binds them -- lives in `test_lesson_session_emission.py`, which
was split out of this module. That split is cohesive rather than a length-cap
spill: nothing here calls `open_lesson_session`, and nothing there reads a retro
artifact or builds a report. Invalid-input refusals across both halves live in
`test_lesson_evaluation_contract_boundaries.py`.
"""

from __future__ import annotations

import json
import runpy
from datetime import date
from pathlib import Path

import pytest
import yaml

from scripts import check_lesson_evaluation_continuity as checker
from scripts import lesson_evaluation_continuity_lib as continuity
from scripts import lesson_evaluation_reconcile_lib as reconcile
from scripts import lesson_evaluation_records_lib as records
from scripts import validate_retro_artifact


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
    clean = reconcile.reconcile_records(
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
        recurrence_sources={},
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
    clean = reconcile.reconcile_records(
        retros=[row],
        sessions=sessions,
        score_events=[],
        receipts={"s-1": _receipt()},
        receipt_violations=[],
        as_of=date(2026, 8, 14),
        recurrence_sources={},
    )
    assert clean["ok"] is True
    assert clean["not_evaluated_reason_counts"]["presentation-unproven"] == 1
    assert clean["completed_evaluation_count"] == 0

    missing = reconcile.reconcile_records(
        retros=[row],
        sessions=sessions,
        score_events=[],
        receipts={},
        receipt_violations=[],
        as_of=date(2026, 8, 14),
        recurrence_sources={},
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
    report = reconcile.reconcile_records(
        retros=[("charness-artifacts/retro/2026-08-14-a.md", disposition)],
        sessions=sessions,
        score_events=scores,
        receipts={"s-1": _receipt()} if with_receipt else {},
        receipt_violations=[],
        as_of=date(2026, 8, 14),
        recurrence_sources={},
    )
    assert report["ok"] is True, report["violations"]
    if reason_count is not None:
        assert report["not_evaluated_reason_counts"][reason_count] == 1


def test_pre_activation_and_same_day_receipts_are_not_unclaimed() -> None:
    sessions = {
        "old": {"snapshot_sha256": "a" * 64},
        "today": {"snapshot_sha256": "a" * 64},
    }
    report = reconcile.reconcile_records(
        retros=[],
        sessions=sessions,
        score_events=[],
        receipts={
            "old": _receipt("old", "2026-08-13T23:59:59Z"),
            "today": _receipt("today", "2026-08-15T00:00:00Z"),
        },
        receipt_violations=[],
        as_of=date(2026, 8, 15),
        recurrence_sources={},
    )
    assert report["ok"] is True


def test_unclaimed_helper_window_excludes_pre_activation_claimed_and_future_receipts() -> None:
    """The window rule the gate and the retro router now SHARE, pinned directly.

    `before=as_of` is the gate's reading: a session declared today is owed a retro
    tonight, not now. `before=None` is the router's: that same session is exactly
    the work tonight's retro must do. One helper, two windows — a second spelling
    is how a router silently skips the session its gate later fails the repo over.
    """
    receipts = {
        "pre": _receipt("pre", "2026-08-13T12:00:00Z"),
        "claimed": _receipt("claimed", "2026-08-14T12:00:00Z"),
        "past": _receipt("past", "2026-08-14T12:00:00Z"),
        "today": _receipt("today", "2026-08-15T12:00:00Z"),
    }
    references = {"claimed": ["charness-artifacts/retro/2026-08-14-a.md"]}

    gate_view = reconcile.unclaimed_receipted_sessions(
        receipts=receipts, references=references, before=date(2026, 8, 15)
    )
    router_view = reconcile.unclaimed_receipted_sessions(
        receipts=receipts, references=references, before=None
    )

    assert gate_view == ["past"]
    assert router_view == ["past", "today"]


def test_reconcile_records_unclaimed_emissions_equal_the_shared_helper() -> None:
    """`reconcile_records` must be a pure consumer of the helper, not a second rule."""
    receipts = {
        "pre": _receipt("pre", "2026-08-13T12:00:00Z"),
        "claimed": _receipt("claimed", "2026-08-14T09:00:00Z"),
        "past": _receipt("past", "2026-08-14T12:00:00Z"),
        "today": _receipt("today", "2026-08-15T01:00:00Z"),
    }
    retros = [
        (
            "charness-artifacts/retro/2026-08-14-a.md",
            {
                "status": "not-evaluated",
                "reason": "presentation-unproven",
                "session_id": "claimed",
                "score_event_count": 0,
            },
        )
    ]
    as_of = date(2026, 8, 15)
    report = reconcile.reconcile_records(
        retros=retros,
        sessions={key: {"snapshot_sha256": "a" * 64} for key in receipts},
        score_events=[],
        receipts=receipts,
        receipt_violations=[],
        as_of=as_of,
        recurrence_sources={},
    )

    named = sorted(
        item["session_id"] for item in report["violations"] if item["id"] == "unclaimed-emission"
    )
    assert named == reconcile.unclaimed_receipted_sessions(
        receipts=receipts,
        references={"claimed": ["charness-artifacts/retro/2026-08-14-a.md"]},
        before=as_of,
    )
    assert named == ["past"]


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
    report = reconcile.reconcile_records(
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
        recurrence_sources={},
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
        "unrecurred-encounter": 0,
        "duplicate-encounter": 0,
    }


def test_retro_validator_does_not_require_optional_lesson_section(tmp_path: Path) -> None:
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
    validate_retro_artifact.validate_retro_artifact(missing)

    body_later = tmp_path / "2026-01-01-body-later.md"
    body_later.write_text(
        _markdown(
            {"status": "no-effect", "session_id": "s", "score_event_count": 0},
            date_text="2026-08-14",
        ).replace("## Lesson Evaluation", "## Omitted"),
        encoding="utf-8",
    )
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


def test_reporter_on_disk_cohort_preserves_denominator_and_payload_fields(
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
    monkeypatch.setattr(records.ledger_lib, "validate_lesson_ledger", lambda **_kwargs: {})

    report = checker.build_report(tmp_path, as_of=date(2026, 8, 14))
    payload = checker.report_payload(report)

    assert report["ok"] is True
    assert report["eligible_retro_count"] == 1
    assert report["disposition_count"] == 1
    assert report["score_event_count"] == 0
    # The retired summary line carried the denominator label, the score-count
    # non-claim, and every not-evaluated reason inline; each is a payload key now.
    assert payload["denominator_label"] == "eligible durable retros"
    assert payload["eligible_retro_count"] == 1
    assert payload["score_event_count"] == 0
    assert any("NOT a health measure" in claim for claim in payload["non_claims"])
    assert payload["not_evaluated_reason_counts"]["presentation-unproven"] == 0


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
    monkeypatch.setattr(records.ledger_lib, "validate_lesson_ledger", lambda **_kwargs: {})
    # The retro scan lives in `lesson_evaluation_records_lib` now, shared with the
    # retro run planner; patch it where the one implementation actually reads it.
    monkeypatch.setattr(
        records,
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
    monkeypatch.setattr(records.ledger_lib, "validate_lesson_ledger", lambda **_kwargs: {})

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
    monkeypatch.setattr(records.ledger_lib, "validate_lesson_ledger", lambda **_kwargs: {})

    report = checker.build_report(tmp_path, as_of=date(2026, 8, 15))

    assert report["ok"] is False
    assert report["eligible_retro_count"] == 1
    assert report["disposition_count"] == 0
    assert {item["id"] for item in report["violations"]} >= {
        "missing-disposition",
        "invalid-receipt",
    }


def test_reconciler_names_foreign_session_and_score_count_mismatch() -> None:
    report = reconcile.reconcile_records(
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
        recurrence_sources={},
    )

    assert {item["id"] for item in report["violations"]} >= {
        "foreign-session",
        "score-count-mismatch",
    }


def test_many_scores_incomplete_is_not_healthier_than_zero_score_complete() -> None:
    path = "charness-artifacts/retro/2026-08-14-a.md"
    sessions = {"s-1": {"snapshot_sha256": "a" * 64}}
    complete = reconcile.reconcile_records(
        retros=[(path, {"status": "no-effect", "session_id": "s-1", "score_event_count": 0})],
        sessions=sessions,
        score_events=[],
        receipts={"s-1": _receipt()},
        receipt_violations=[],
        as_of=date(2026, 8, 14),
        recurrence_sources={},
    )
    incomplete = reconcile.reconcile_records(
        retros=[(path, {"status": "effect-recorded", "session_id": "s-1", "score_event_count": 1})],
        sessions=sessions,
        score_events=[{"session_id": "s-1", "source_retro": path} for _ in range(5)],
        receipts={"s-1": _receipt()},
        receipt_violations=[],
        as_of=date(2026, 8, 14),
        recurrence_sources={},
    )

    assert complete["ok"] is True
    assert complete["score_event_count"] == 0
    assert incomplete["ok"] is False
    assert incomplete["score_event_count"] == 5
    assert incomplete["aggregate_violation_counts"]["score-count-mismatch"] == 1
    # The retired summary line reported `violations=N`; the payload carries the
    # same total, so the zero-score-complete row still reads as the healthier one.
    assert complete["violation_count"] == 0
    assert incomplete["violation_count"] == 1


def test_cli_yaml_snapshot_and_exit_status(
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
    monkeypatch.setattr(records.ledger_lib, "validate_lesson_ledger", lambda **_kwargs: {})
    monkeypatch.setattr(
        checker.sys,
        "argv",
        ["check_lesson_evaluation_continuity.py", "--repo-root", str(tmp_path), "--as-of", "2026-08-14"],
    )

    assert checker.main() == 0
    clean = yaml.safe_load(capsys.readouterr().out)
    assert clean["denominator_label"] == "eligible durable retros"
    assert clean["eligible_retro_count"] == clean["disposition_count"] == 1
    assert clean["aggregate_violation_counts"] == {
        "score-count-mismatch": 0,
        "duplicate-session-reference": 0,
        "unclaimed-emission": 0,
        "unrecurred-encounter": 0,
        "duplicate-encounter": 0,
    }
    assert clean["violation_count"] == 0

    retro_path.write_text(
        _markdown({"status": "no-effect", "session_id": "s-1", "score_event_count": 0}).replace(
            "## Lesson Evaluation", "## Omitted"
        ),
        encoding="utf-8",
    )
    assert checker.main() == 1
    blocked = yaml.safe_load(capsys.readouterr().out)
    assert blocked["eligible_retro_count"] == 1
    assert blocked["disposition_count"] == 0
    assert {item["id"] for item in blocked["violations"]} == {"missing-disposition"}

    retro_path.write_text(
        _markdown({"status": "effect-recorded", "session_id": "s-1", "score_event_count": 1}),
        encoding="utf-8",
    )
    assert checker.main() == 1
    mismatch = yaml.safe_load(capsys.readouterr().out)
    assert mismatch["aggregate_violation_counts"]["score-count-mismatch"] == 1
    assert {item["id"] for item in mismatch["violations"]} == {
        "effect-recorded-without-score",
        "score-count-mismatch",
    }


def test_reporter_cli_payload_output_and_error_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    clean = reconcile.reconcile_records(
        retros=[],
        sessions={},
        score_events=[],
        receipts={},
        receipt_violations=[],
        as_of=date(2026, 8, 14),
        recurrence_sources={},
    )
    monkeypatch.setattr(checker, "build_report", lambda *_args, **_kwargs: clean)
    monkeypatch.setattr(
        checker.sys,
        "argv",
        ["check_lesson_evaluation_continuity.py", "--repo-root", str(tmp_path)],
    )
    assert checker.main() == 0
    # The default (only) output mode is the YAML report payload; the retired
    # "Lesson evaluation continuity:" preamble is now `denominator_label`.
    emitted = yaml.safe_load(capsys.readouterr().out)
    assert emitted == checker.report_payload(clean)
    assert emitted["denominator_label"] == "eligible durable retros"

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
