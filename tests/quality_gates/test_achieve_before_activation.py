from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACHIEVE = ROOT / "skills" / "public" / "achieve"


def _text(relative: str) -> str:
    return (ACHIEVE / relative).read_text(encoding="utf-8")


def test_public_achieve_exposes_one_issue_native_lifecycle() -> None:
    skill = _text("SKILL.md")
    before = _text("references/lifecycle-before.md")
    during = _text("references/lifecycle-during.md")
    after = _text("references/lifecycle-after.md")

    assert "complete local Goal Draft" in skill
    assert "immutable Goal Binding" in skill
    assert "`/goal #N`" in skill
    assert "goal_run_pickup.py" in skill
    assert "verified-target-roundtrip" in before
    assert "charness.goal-progress/v1" in during
    assert "guarded provider close" in after


def test_active_docs_do_not_advertise_retired_execution_authorities() -> None:
    surfaces = [_text("SKILL.md"), _text("references/lifecycle-before.md"), _text("references/lifecycle-during.md"), _text("references/lifecycle-after.md")]
    joined = "\n".join(surfaces)

    assert "/goal @" not in joined
    assert "append_slice_log.py" not in joined
    assert "Status: active" not in joined
    assert "Status: complete" not in joined
    assert "minimal local compatibility receipt" not in joined


def test_before_phase_binds_full_draft_and_refuses_unresolved_interview() -> None:
    before = _text("references/lifecycle-before.md")

    assert "interview.max_questions" in before
    assert "interview-cap-reached" in before
    assert "do not create or\nmutate a provider parent" in before
    assert "complete draft" in before
    assert "No provider mutation is authorized" in before


def test_during_phase_enters_the_parent_cursor_and_reserves_full_reconciliation() -> None:
    during = _text("references/lifecycle-during.md")

    assert "pickup does not read the child" in during
    assert "explicit progress sync/doctor" in during
    assert "one parent read" in during
    assert "no second local progress ledger" in during


def test_after_phase_keeps_closeout_evidence_distinct_from_state() -> None:
    after = _text("references/lifecycle-after.md")

    assert "closed is provider state, not proof" in after
    assert "distinct post-close readback" in after
    assert "Planning-only and not-goal-bound" in after
    assert "frozen Goal Draft remains unchanged" in after
