from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.lessons import lesson_ledger_lib as ledger
from scripts.lessons import lesson_score_outcome_lib as outcome_lib
from scripts.lessons import lesson_selection_preview_lib as preview
from scripts.lessons import record_lesson_lifecycle as lifecycle_recorder
from tests.test_lesson_ledger import _ledger, _retro


def _lesson() -> dict[str, object]:
    return {"state": "active", "last_lifecycle_event_id": None}


def _event(**updates: object) -> dict[str, object]:
    event: dict[str, object] = {
        "sequence": 1,
        "event_id": "archive-a",
        "lesson_id": "a",
        "action": "archive",
        "decision_ref": "decision.md",
        "rationale": "Reviewed.",
    }
    event.update(updates)
    return event


def test_lifecycle_replay_rejects_closed_event_shapes(tmp_path: Path) -> None:
    (tmp_path / "decision.md").write_text("# Decision\n", encoding="utf-8")
    assert ledger.canonical_markdown_ref(tmp_path, "") is False
    outside = tmp_path.parent / "outside.md"
    outside.write_text("# Outside\n", encoding="utf-8")
    assert ledger.canonical_markdown_ref(tmp_path, "../outside.md") is False
    cases = [
        ([], 49, "active_lesson_budget"),
        ([{}], 50, "unexpected or missing"),
        ([_event(sequence=2)], 50, "sequences must start"),
        ([_event(rationale="")], 50, "non-empty identity"),
        ([_event(lesson_id="missing")], 50, "unseeded lesson"),
        ([_event(decision_ref="missing.md")], 50, "existing canonical Markdown"),
    ]
    for events, budget, message in cases:
        with pytest.raises(ValueError, match=message):
            ledger._replay_lifecycle(events, {"a": _lesson()}, budget=budget, repo_root=tmp_path)
    with pytest.raises(ValueError, match="duplicate lifecycle event_id"):
        ledger._replay_lifecycle(
            [_event(), _event(sequence=2)], {"a": _lesson()}, budget=50, repo_root=tmp_path
        )


def test_committed_lesson_budget_rewrite_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    monkeypatch.setattr(
        ledger,
        "_committed_state",
        lambda *_args: (
            payload["transitions"],
            payload["score_events"],
            49,
            payload["lifecycle_events"],
        ),
    )
    with pytest.raises(ValueError, match="active_lesson_budget was rewritten"):
        ledger.replay_validated_ledger_payload(
            repo_root=tmp_path,
            output_dir=path.parent,
            summary_path=path.parent / "recent-lessons.md",
            path=path,
            payload=payload,
        )


def test_lifecycle_operator_rejects_missing_blank_and_unknown_action(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="missing lesson ledger"):
        lifecycle_recorder.append_lifecycle_event(
            repo_root=tmp_path, event_id="e", lesson_id="a", action="archive",
            decision_ref="d.md", rationale="r",
        )
    _retro(tmp_path, "source.md", "a")
    _ledger(tmp_path)
    with pytest.raises(ValueError, match="must be non-empty"):
        lifecycle_recorder.append_lifecycle_event(
            repo_root=tmp_path, event_id=" ", lesson_id="a", action="archive",
            decision_ref="d.md", rationale="r",
        )
    with pytest.raises(
        ValueError, match="action must be one of archive, graduate, resurrect"
    ):
        lifecycle_recorder.append_lifecycle_event(
            repo_root=tmp_path, event_id="e", lesson_id="a", action="other",
            decision_ref="d.md", rationale="r",
        )


def test_preview_refuses_a_validated_lesson_with_unknown_lifecycle_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    row = {
        "lesson_id": "a",
        "lesson": "A",
        "latest_source_path": "source.md",
        "latest_source_date": None,
        "selection_weight": 1,
        "score_total": 0,
        "score_count": 0,
        "outcome_counts": outcome_lib.outcome_counts([]),
        "state": "unknown",
    }
    monkeypatch.setattr(preview, "check_lesson_selection_index", lambda *_args: None)
    monkeypatch.setattr(preview, "_load_validated_ledger", lambda *_args: {"lessons": {"a": {}}})
    monkeypatch.setattr(preview, "build_lesson_selection_index", lambda **_kwargs: {})
    monkeypatch.setattr(preview, "_candidate_rows", lambda *_args: [row])
    with pytest.raises(ValueError, match="invalid lifecycle state"):
        preview.build_lesson_selection_preview(
            repo_root=tmp_path,
            output_dir=tmp_path,
            summary_path=tmp_path / "recent-lessons.md",
            seed="seed",
        )
