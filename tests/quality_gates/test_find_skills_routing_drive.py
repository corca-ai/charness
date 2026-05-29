from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_find_skills_skill_pins_routing_drive_contract() -> None:
    """find-skills must own driving the routed workflow, not stop at the inventory.

    This is the load-bearing contract for #240: a SessionStart hook can only
    inject a directive to call find-skills; the "what next" (pickup ->
    charness:handoff) must live in the skill. Removing the contract line fails
    this gate.
    """
    raw_skill_text = (
        ROOT / "skills" / "public" / "find-skills" / "SKILL.md"
    ).read_text(encoding="utf-8")
    routing_ref = (
        ROOT / "skills" / "public" / "find-skills" / "references" / "session-start-routing.md"
    ).read_text(encoding="utf-8")
    # Normalize whitespace so contract phrases match regardless of line wrapping.
    skill_text = " ".join(raw_skill_text.split())

    # The prescribed routing-drive contract is stated in the skill body.
    assert "drive the routed workflow from your result" in skill_text
    # The guardrail forbids stopping at the inventory on a pickup.
    assert "Do not stop after emitting the inventory" in skill_text
    # The pickup path names the handoff Workflow Trigger and the concrete skill.
    assert "Workflow Trigger" in skill_text
    assert "charness:handoff" in skill_text
    assert "pickup" in skill_text
    assert "SessionStart" in skill_text
    # The guardrail names the miss this skill prevents.
    assert "routing miss this" in skill_text
    # The reference the skill points to carries the pickup decision path and the
    # honest hook ceiling (a hook cannot invoke a Skill tool for the agent).
    assert "references/session-start-routing.md" in skill_text
    assert "Pickup decision path" in routing_ref
    assert "charness:handoff" in routing_ref
    assert "cannot" in routing_ref and "invoke a Skill tool" in routing_ref


def test_find_skills_routing_drive_contract_is_distinct_from_discovery_only() -> None:
    """The contract must preserve the discovery-only exception, not over-route."""
    skill_text = " ".join(
        (ROOT / "skills" / "public" / "find-skills" / "SKILL.md")
        .read_text(encoding="utf-8")
        .split()
    )
    # A pure "which skill handles X?" question still ends at the inventory answer.
    assert "which skill handles" in skill_text.lower()
    assert "is the deliverable" in skill_text or "ends at the inventory" in skill_text
