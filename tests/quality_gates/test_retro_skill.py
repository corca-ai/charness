from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

RETRO_SKILL = (ROOT / "skills" / "public" / "retro" / "SKILL.md").read_text(encoding="utf-8")


def test_retro_skill_triggers_on_present_but_undeclared_invariants() -> None:
    reference_text = (
        ROOT / "skills" / "public" / "retro" / "references" / "trigger-and-persistence.md"
    ).read_text(encoding="utf-8")

    assert "fresh-eye reader misread an invariant" in RETRO_SKILL
    assert "check_auto_trigger.py" in RETRO_SKILL
    assert "auto_session_trigger_surfaces" in RETRO_SKILL
    assert "present invariant as absent" in reference_text


def test_retro_efficiency_waste_is_phase_aware() -> None:
    section_text = (
        ROOT / "skills" / "public" / "retro" / "references" / "section-guide.md"
    ).read_text(encoding="utf-8")
    efficiency_text = (
        ROOT / "skills" / "public" / "retro" / "references" / "phase-aware-efficiency.md"
    ).read_text(encoding="utf-8")

    assert "references/phase-aware-efficiency.md" in RETRO_SKILL
    assert "phase intent and the triage lock" in RETRO_SKILL
    assert "audit_codex_session.py" in RETRO_SKILL
    assert "Broad" in section_text and "not waste solely because it was broad" in section_text
    assert "Classify high-cost activity by phase" in efficiency_text
    assert "Exploration -> Triage -> Implementation -> Verification" in efficiency_text
    assert "`fix now`, `deferred`, `needs user call`, and" in efficiency_text
    assert "measured, proxy, and unavailable signals" in efficiency_text
    assert "audit_codex_session.py" in efficiency_text
    assert "Do not store one session's scope narrowing" in efficiency_text
    assert "Cached input tokens are not a waste conclusion by themselves" in efficiency_text
    assert "issue-resolution carrier" in efficiency_text
    assert "lifecycle/audit artifact" in efficiency_text


def test_retro_consumes_prepare_packets_when_adapter_declares_sections() -> None:
    adapter_text = (
        ROOT / "skills" / "public" / "retro" / "references" / "adapter-contract.md"
    ).read_text(encoding="utf-8")
    packet_text = (
        ROOT / "skills" / "public" / "retro" / "references" / "prepare-packet.md"
    ).read_text(encoding="utf-8")

    assert "prepare_packet.py" in RETRO_SKILL
    assert "Packet Consumed" in RETRO_SKILL
    assert "packet_sections" in adapter_text
    assert "charness.retro_prepare_packet" in packet_text
    assert "CHARNESS_RETRO_CHANGED_REF" in packet_text
