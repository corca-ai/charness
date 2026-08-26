from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/public/achieve/scripts/interview_contract.py"


def _load():
    spec = importlib.util.spec_from_file_location("achieve_interview_contract", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


contract = _load()


def _question(index: int, *, answered: bool = True) -> dict[str, object]:
    question: dict[str, object] = {
        "decision": f"decision {index}",
        "options": [
            {"id": "A", "summary": "recommended", "tradeoff": "blocks on outage"},
            {"id": "B", "summary": "alternative", "tradeoff": "can split authority"},
        ],
        "recommendation": {"option": "A", "reason": "keeps one authority"},
    }
    if answered:
        question["answer"] = {"option": "A", "reason": "operator accepted recommendation"}
        question["rejected_alternatives"] = [
            {"option": "B", "reason": "operator selected the safer authority rule"}
        ]
    return question


def test_zero_question_fully_resolved_interview_is_complete() -> None:
    result = contract.validate_record(
        {"version": 1, "questions": [], "remaining_consequential_decisions": []},
        max_questions=15,
    )

    assert result["ok"] is True
    assert result["status"] == "interview-complete"
    assert result["parent_creation_ready"] is True


def test_few_questions_stop_before_the_ceiling() -> None:
    result = contract.validate_record(
        {"version": 1, "questions": [_question(1)], "remaining_consequential_decisions": []},
        max_questions=15,
    )

    assert result["question_count"] == 1
    assert result["status"] == "interview-complete"


def test_exact_ceiling_with_remaining_decisions_refuses_parent_creation() -> None:
    result = contract.validate_record(
        {
            "version": 1,
            "questions": [_question(index) for index in range(3)],
            "remaining_consequential_decisions": ["one more policy choice"],
        },
        max_questions=3,
    )

    assert result["ok"] is True
    assert result["status"] == "interview-cap-reached"
    assert result["parent_creation_ready"] is False
    assert "raise interview.max_questions" in result["next_action"]


def test_question_count_cannot_overrun_ceiling() -> None:
    result = contract.validate_record(
        {
            "version": 1,
            "questions": [_question(index) for index in range(4)],
            "remaining_consequential_decisions": [],
        },
        max_questions=3,
    )

    assert result["ok"] is False
    assert result["status"] == "invalid"
    assert "exceeds configured maximum" in result["errors"][0]


def test_unanswered_question_is_in_progress() -> None:
    result = contract.validate_record(
        {"version": 1, "questions": [_question(1, answered=False)], "remaining_consequential_decisions": []},
        max_questions=15,
    )

    assert result["ok"] is True
    assert result["status"] == "interview-in-progress"
    assert result["unanswered_question_indexes"] == [0]


def test_answer_requires_reasons_for_every_rejected_option() -> None:
    question = _question(1)
    question["rejected_alternatives"] = []

    result = contract.validate_record(
        {"version": 1, "questions": [question], "remaining_consequential_decisions": []},
        max_questions=15,
    )

    assert result["ok"] is False
    assert any("every non-selected option" in error for error in result["errors"])
