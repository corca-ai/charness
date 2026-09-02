"""Focused coverage for the live lesson score vocabulary.

The ledger keeps durable score history and selection statistics. The former
receipt/evaluator continuity layer is deliberately outside this surface.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.lessons import lesson_score_outcome_lib as outcome_lib
from scripts.lessons import record_lesson_score as scorer
from tests.test_lesson_ledger import _ledger, _retro, _validate


def _score(path: Path, *, outcome: str = "changed-an-action", anchor: str | None = None) -> dict:
    if anchor is None:
        anchor = "used the measured path rather than the assumed one, which would have shipped a false result"
    return scorer.append_score(
        repo_root=path.parents[2],
        output_dir=path.parent,
        summary_path=path.parent / "recent-lessons.md",
        event_id=f"event-{outcome}",
        lesson_id="a",
        source_retro="charness-artifacts/retro/encounter.md",
        outcome=outcome,
        anchor=anchor,
    )


def test_score_vocabulary_and_routing_are_explicit() -> None:
    assert outcome_lib.SCORE_OUTCOMES == {
        "changed-an-action": "graduate",
        "read-but-not-applied": "rewrite-in-place",
        "not-consulted": "strengthen-binding",
        "pushed-a-wrong-action": "rewrite-in-place",
    }
    assert outcome_lib.outcome_counts([]) == {
        "changed-an-action": 0,
        "not-consulted": 0,
        "pushed-a-wrong-action": 0,
        "read-but-not-applied": 0,
        "legacy-scalar": 0,
    }


@pytest.mark.parametrize(
    ("event", "expected"),
    [
        ({"outcome": "changed-an-action"}, 1),
        ({"outcome": "read-but-not-applied"}, -1),
        ({"outcome": "not-consulted"}, -1),
        ({"outcome": "pushed-a-wrong-action"}, -1),
        ({"score": 3}, 1),
        ({"score": -2}, -1),
    ],
)
def test_valence_keeps_legacy_sign_and_current_outcomes(event: dict, expected: int) -> None:
    assert outcome_lib.valence(event) == expected


@pytest.mark.parametrize(
    "citation",
    [
        None,
        "",
        "charness-artifacts/retro/recent-lessons.md",
        "charness-artifacts/retro/nested/encounter.md",
        "charness-artifacts/retro/encounter.txt",
        "charness-artifacts/retro/../escape.md",
    ],
)
def test_citation_shape_is_small_and_deterministic(citation: object) -> None:
    assert outcome_lib.canonical_retro_citation(citation) is False
    assert outcome_lib.canonical_retro_citation("charness-artifacts/retro/encounter.md") is True


def test_writer_records_an_encounter_without_continuity_receipts(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path)

    event = _score(path)

    assert event["source_retro"] == "charness-artifacts/retro/encounter.md"
    assert _validate(tmp_path)["score_event_count"] == 1
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["lessons"]["a"]["outcome_counts"]["changed-an-action"] == 1


def test_not_consulted_is_a_plain_score_outcome(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path)

    event = _score(
        path,
        outcome="not-consulted",
        anchor="did not revisit the lesson at the decision",
    )

    assert event["outcome"] == "not-consulted"
    assert _validate(tmp_path)["score_event_count"] == 1
