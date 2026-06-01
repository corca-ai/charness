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

    # The mode-ambiguity question rule is stated in the skill body. (The bare
    # word "mode" is intentionally avoided in the SKILL.md body to satisfy the
    # skill-ergonomics mode-pressure gate; the cases are named directly.)
    assert "artifact-only" in skill and "implementation-continuation" in skill
    assert "ask at least one" in skill
    # Stating the assumption is the allowed alternative to asking.
    assert "state the assumed interpretation" in skill
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


def test_goal_activation_is_pursue_only_and_failfast() -> None:
    """`/goal` is pure pursue; shaping is the Before-phase's job (`/achieve`);
    `/goal` fail-fasts on an unshaped goal instead of shaping it. Pin the contract
    on both surfaces so it cannot silently regress to shape-then-run."""
    skill = _norm(ACHIEVE / "SKILL.md")
    lifecycle = _norm(ACHIEVE / "references" / "lifecycle.md")

    # /goal pursues only; the lifecycle states it verbatim.
    assert "pure pursue" in lifecycle
    # The deterministic guard the prose leans on is named on both surfaces.
    assert "pursue-ready" in skill and "pursue-ready" in lifecycle
    # Unshaped -> fail-fast and route to the Before-phase, never shape in /goal.
    assert "fail-fast" in skill and "fail-fast" in lifecycle
    assert "/achieve" in skill and "/achieve" in lifecycle


def test_consequential_defaults_need_discussion_before_activation() -> None:
    """Structural pursue-readiness cannot hide operator decisions."""
    skill = _norm(ACHIEVE / "SKILL.md")
    lifecycle = _norm(ACHIEVE / "references" / "lifecycle.md")

    assert "Discuss before activation:" in skill
    assert "Discuss before activation:" in lifecycle
    assert "live/prod proof" in skill and "live/prod proof" in lifecycle
    assert "issue close/split" in skill and "issue close/split" in lifecycle
    assert "operator-ready" in lifecycle


def test_host_goal_completion_is_downstream_of_artifact_closeout() -> None:
    """#268: host green status cannot replace the checked goal artifact floor."""
    skill = _norm(ACHIEVE / "SKILL.md")
    lifecycle = _norm(ACHIEVE / "references" / "lifecycle.md")

    assert "before any host-level goal completion" in skill
    assert "Status: complete" in skill
    assert "Host-level goal completion is downstream of the artifact" in lifecycle
    assert "update_goal(status=complete)" in lifecycle
    assert "check_goal_artifact.py --goal-path <artifact>" in lifecycle


def test_long_goal_efficiency_contract_is_explicit() -> None:
    skill = _norm(ACHIEVE / "SKILL.md")
    lifecycle = _norm(ACHIEVE / "references" / "lifecycle.md")
    artifact = _norm(ACHIEVE / "references" / "goal-artifact.md")

    assert "Active Operating Frame" in skill
    assert "Active Operating Frame" in lifecycle
    assert "Active Operating Frame" in artifact
    assert "cheap deterministic checks at commit boundaries" in lifecycle
    assert "Slice review packet" in artifact
    assert "measured signals" in lifecycle and "proxy signals" in lifecycle
    assert "Cached input alone is not a waste conclusion" in lifecycle
