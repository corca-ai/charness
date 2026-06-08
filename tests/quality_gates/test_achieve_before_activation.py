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
    assert "resolve or explicitly ask" in skill
    assert "resolve or explicitly ask" in lifecycle
    assert "shape_ready" in lifecycle
    assert "activation_ready" in lifecycle
    assert "must be false while consequential discussion is only surfaced" in lifecycle


def test_host_goal_completion_is_downstream_of_artifact_closeout() -> None:
    """#268: host green status cannot replace the checked goal artifact floor."""
    skill = _norm(ACHIEVE / "SKILL.md")
    lifecycle = _norm(ACHIEVE / "references" / "lifecycle.md")

    assert "before any host-level goal completion" in skill
    assert "Status: complete" in skill
    assert "Host-level goal completion is downstream of the artifact" in lifecycle
    assert "update_goal(status=complete)" in lifecycle
    assert "check_goal_artifact.py --goal-path <artifact>" in lifecycle


def test_drafting_does_not_consume_host_goal_slot() -> None:
    """#336: the Before-phase is artifact-only and must not consume the host
    active-goal slot; the slot is consumed only at `/goal` pursuit. This is the
    symmetric Before-phase counterpart of the #268 completion-downstream rule.
    Pin it on the skill, lifecycle, and adapter-contract surfaces so it cannot
    silently regress back to draft-consumes-slot friction."""
    skill = _norm(ACHIEVE / "SKILL.md")
    lifecycle = _norm(ACHIEVE / "references" / "lifecycle.md")
    adapter = _norm(ACHIEVE / "references" / "adapter-contract.md")

    # SKILL.md core names the rule and the pursue-only consumption point.
    assert "must not consume the host active-goal slot" in skill
    assert "only `/goal` pursuit does" in skill
    # The lifecycle reference carries the full contract + host-owned determination
    # + the honest host-runtime residual boundary.
    assert "Drafting does not consume the host goal slot" in lifecycle
    assert "host-owned" in lifecycle
    assert "consumed **only** at `/goal @artifact` pursuit" in lifecycle
    assert "host-runtime" in lifecycle and "non-claim" in lifecycle
    # The adapter contract documents the host goal-slot boundary and that no
    # adapter knob exists (a no-op knob would fake portability).
    assert "Host Goal-Slot Boundary" in adapter
    assert "needs no adapter knob" in adapter


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
    assert "actual waste from this run" in lifecycle
    assert "Do not include routine publication/push prompts by default" in lifecycle


def test_timebox_goal_contract_is_explicit() -> None:
    skill = _norm(ACHIEVE / "SKILL.md")
    lifecycle = _norm(ACHIEVE / "references" / "lifecycle.md")
    artifact = _norm(ACHIEVE / "references" / "goal-artifact.md")

    assert "Timebox:" in skill and "Timebox:" in lifecycle and "Timebox:" in artifact
    assert "Activation time:" in skill and "Activation time:" in lifecycle
    assert "Closeout reserve:" in skill and "Closeout reserve:" in lifecycle
    assert "Done-early policy: continue_next_improvement" in skill
    assert "Done-early policy: continue_next_improvement" in lifecycle
    assert "Slice-Boundary Continuation" in lifecycle
    assert "No safe next slice:" in skill and "No safe next slice:" in artifact
    assert "cannot flip to `complete` before" in lifecycle


def test_external_side_effect_approval_is_phase_scoped() -> None:
    """#316: external publication/apply approval is scoped to the phase or bundle
    that requested it, and done-early test-only quality continuation is local by
    default. The rule must land in all three surfaces: SKILL.md, lifecycle.md,
    and the goal-artifact template's ## Boundaries seed.
    """
    skill = _norm(ACHIEVE / "SKILL.md")
    lifecycle = _norm(ACHIEVE / "references" / "lifecycle.md")
    template = _norm(ACHIEVE / "scripts" / "goal_artifact_template.md")

    # (1) Phase/bundle-scoped approval that does not carry forward.
    for surface in (skill, lifecycle, template):
        assert "phase or bundle" in surface or "phase-scoped" in surface
        assert "carry forward" in surface or "does not carry forward" in surface

    # (2) Local-by-default done-early test-only continuation.
    for surface in (skill, lifecycle, template):
        assert "local by default" in surface
        assert "done-early" in surface

    # (3) Per-slice remote publication only when the operator asks or a
    # runtime-affecting slice needs it earlier.
    for surface in (skill, lifecycle, template):
        assert "operator explicitly asks" in surface
        assert "runtime-affecting" in surface

    # The template seeds the boundary under ## Boundaries so a fresh goal sees it.
    boundary_template = (ACHIEVE / "scripts" / "goal_artifact_template.md").read_text(
        encoding="utf-8"
    )
    boundaries_start = boundary_template.index("## Boundaries")
    user_acceptance = boundary_template.index("## User Acceptance")
    boundaries_block = boundary_template[boundaries_start:user_acceptance]
    assert "External side-effect scope" in boundaries_block

    # No new deterministic word-list gate was introduced for this rule: the
    # boundary stays prose+template (the gate-over-fire failure mode is the
    # explicitly out-of-scope direction for #316).
    scripts_dir = ROOT / "scripts"
    for gate in scripts_dir.glob("*.py"):
        body = gate.read_text(encoding="utf-8")
        assert "publication_approval_carryforward" not in body
        assert "carry_forward_approval_gate" not in body
