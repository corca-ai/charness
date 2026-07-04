from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FIND_SKILLS_SKILL = (
    ROOT / "skills" / "public" / "find-skills" / "SKILL.md"
).read_text(encoding="utf-8")


def test_find_skills_skill_pins_routing_drive_contract() -> None:
    """find-skills must still drive the routed workflow whenever it is invoked.

    This is the load-bearing contract carried over from #240 into the
    2026-07-04 front-load revision: the `SessionStart` hook now front-loads
    the pickup/discovery/otherwise routing rule directly, so `find-skills` is
    invoked mainly for capability discovery or a genuinely unclear route --
    but whenever it IS invoked, it must still drive the routed workflow
    rather than stop at the inventory. Removing the contract line fails this
    gate.
    """
    routing_ref = (
        ROOT / "skills" / "public" / "find-skills" / "references" / "session-start-routing.md"
    ).read_text(encoding="utf-8")
    # Normalize whitespace so contract phrases match regardless of line wrapping.
    skill_text = " ".join(FIND_SKILLS_SKILL.split())

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
    # The reference the skill points to carries the pickup decision path.
    assert "references/session-start-routing.md" in skill_text
    assert "Pickup decision path" in routing_ref
    assert "charness:handoff" in routing_ref
    # The 2026-07-04 revision section names why the front-load design was
    # adopted and carries the three #240 protections forward explicitly,
    # replacing the old "honest ceiling ... deliberately not chosen" pin
    # (that design is no longer the one in force).
    assert "2026-07-04 revision" in routing_ref
    assert "protections carried over" in routing_ref
    assert "deterministically drive into the handoff-named" in routing_ref
    assert "discovery stays owned by" in routing_ref
    assert "still drives the routed workflow" in routing_ref


def test_find_skills_routing_drive_contract_is_distinct_from_discovery_only() -> None:
    """The contract must preserve the discovery-only exception, not over-route."""
    skill_text = " ".join(FIND_SKILLS_SKILL.split())
    # A pure "which skill handles X?" question still ends at the inventory answer.
    assert "which skill handles" in skill_text.lower()
    assert "is the deliverable" in skill_text or "ends at the inventory" in skill_text
