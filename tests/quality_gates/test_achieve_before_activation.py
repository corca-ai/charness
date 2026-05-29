from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACHIEVE = ROOT / "skills" / "public" / "achieve"


def _norm(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_achieve_before_phase_pins_mode_disambiguation_question() -> None:
    """#239: ambiguous mode (artifact-only vs implementation-continuation) gets a question."""
    skill = _norm(ACHIEVE / "SKILL.md")
    lifecycle = _norm(ACHIEVE / "references" / "lifecycle.md")

    # The mode-ambiguity question rule is stated in the skill body.
    assert "artifact-only" in skill and "implementation-continuation" in skill
    assert "ask at least one" in skill
    # Stating the assumption is the allowed alternative to asking.
    assert "state the assumed mode" in skill
    # The lifecycle reference carries the full mode-disambiguation contract.
    assert "Mode disambiguation" in lifecycle
    assert "artifact-only" in lifecycle and "implementation-continuation" in lifecycle


def test_achieve_before_phase_pins_activation_closeout_clarity() -> None:
    """#239: the activation line + inert-until-/goal status must be impossible to miss."""
    skill = _norm(ACHIEVE / "SKILL.md")
    lifecycle = _norm(ACHIEVE / "references" / "lifecycle.md")

    # The skill body names the closeout shape (Goal file: / Activation: / inert).
    assert "`Goal file:`" in skill
    assert "`Activation:`" in skill
    assert "inert-until-`/goal`" in skill
    # The lifecycle reference carries the activation-closeout checklist.
    assert "Activation-closeout clarity" in lifecycle
    assert "Goal file:" in lifecycle and "Activation:" in lifecycle
