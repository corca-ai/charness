from __future__ import annotations

from .support import ROOT


def test_hitl_skill_requires_agent_assessment_before_decision() -> None:
    skill_text = (ROOT / "skills" / "public" / "hitl" / "SKILL.md").read_text(encoding="utf-8")

    assert "Agent Assessment" in skill_text
    assert "Recommended Disposition" in skill_text
    assert "non-binding" in skill_text
    assert "question-only chunks are not enough" in skill_text


def test_hitl_chunk_contract_lists_assessment_and_recommendation() -> None:
    chunk_contract = (ROOT / "skills" / "public" / "hitl" / "references" / "chunk-contract.md").read_text(
        encoding="utf-8"
    )

    assert "agent assessment" in chunk_contract
    assert "recommended disposition" in chunk_contract
    assert "display-only" in chunk_contract
    assert "Suggestions never auto-record as approval" in chunk_contract


def test_hitl_output_shape_orders_assessment_before_decision_needed() -> None:
    skill_text = (ROOT / "skills" / "public" / "hitl" / "SKILL.md").read_text(encoding="utf-8")

    assessment_index = skill_text.index("Agent Assessment")
    recommendation_index = skill_text.index("Recommended Disposition")
    decision_index = skill_text.index("Decision Needed")

    assert assessment_index < decision_index
    assert recommendation_index < decision_index
