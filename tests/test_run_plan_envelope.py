from __future__ import annotations

import runpy
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
ENVELOPE_PATH = ROOT / "skills" / "shared" / "scripts" / "run_plan_envelope.py"


def load_envelope() -> SimpleNamespace:
    return SimpleNamespace(**runpy.run_path(str(ENVELOPE_PATH)))


ENV = load_envelope()


def _valid_kwargs() -> dict:
    return {
        "schema_version": "demo.run_plan.v1",
        "required_reads": [ENV.read("references/x.md", "why", kind="reference", base="skill")],
        "next_action": ENV.next_action("do_thing", reason="because"),
        "gate_packets": [ENV.gate_packet("g1", "deterministic; trust failures")],
    }


def test_read_emits_only_supplied_optional_fields() -> None:
    minimal = ENV.read("p", "w")
    assert minimal == {"path": "p", "why": "w"}
    full = ENV.read("p", "w", kind="reference", base="skill", trigger="t", role="r")
    assert full == {
        "path": "p",
        "why": "w",
        "kind": "reference",
        "base": "skill",
        "trigger": "t",
        "role": "r",
    }


def test_gate_packet_has_core_keys_and_extensions() -> None:
    packet = ENV.gate_packet("g", "trust", cost_tier="network", available=False, run_when="always")
    assert packet["id"] == "g"
    assert packet["trust_model"] == "trust"
    assert packet["cost_tier"] == "network"
    assert packet["available"] is False
    assert packet["run_when"] == "always"


def test_next_action_always_carries_kind() -> None:
    action = ENV.next_action("scaffold", command="run it")
    assert action["kind"] == "scaffold"
    assert action["command"] == "run it"


def test_build_envelope_stamps_version_and_passes_extensions() -> None:
    envelope = ENV.build_envelope(**_valid_kwargs(), repo_root="/tmp/repo", mode="fresh")
    assert envelope["envelope_version"] == ENV.ENVELOPE_VERSION
    assert envelope["schema_version"] == "demo.run_plan.v1"
    assert envelope["repo_root"] == "/tmp/repo"
    assert envelope["mode"] == "fresh"
    # All canonical keys present.
    for key in ENV.REQUIRED_ENVELOPE_KEYS:
        assert key in envelope


def test_build_linear_envelope_has_no_fabricated_branches() -> None:
    envelope = ENV.build_linear_envelope(
        schema_version="linear.run_plan.v1",
        required_reads=[ENV.read("references/a.md", "primer")],
        next_action_kind="read_primer",
        next_action_reason="open the primer before acting",
    )
    assert envelope["next_action"] == {"kind": "read_primer", "reason": "open the primer before acting"}
    assert envelope["gate_packets"] == []
    ENV.validate_envelope(envelope)


def test_validate_envelope_rejects_string_next_action() -> None:
    kwargs = _valid_kwargs()
    kwargs["next_action"] = "do_thing"
    with pytest.raises(ENV.EnvelopeError, match="next_action"):
        ENV.build_envelope(**kwargs)


def test_validate_envelope_rejects_next_action_without_kind() -> None:
    envelope = ENV.build_envelope(**_valid_kwargs())
    envelope["next_action"] = {"command": "x"}
    with pytest.raises(ENV.EnvelopeError, match="kind"):
        ENV.validate_envelope(envelope)


def test_validate_envelope_rejects_read_missing_why() -> None:
    kwargs = _valid_kwargs()
    kwargs["required_reads"] = [{"path": "p"}]
    with pytest.raises(ENV.EnvelopeError, match="why"):
        ENV.build_envelope(**kwargs)


def test_validate_envelope_rejects_gate_packet_missing_core_key() -> None:
    kwargs = _valid_kwargs()
    kwargs["gate_packets"] = [{"id": "g", "trust_model": "t"}]  # missing cost_tier
    with pytest.raises(ENV.EnvelopeError, match="cost_tier"):
        ENV.build_envelope(**kwargs)


def test_validate_envelope_rejects_wrong_envelope_version() -> None:
    envelope = ENV.build_envelope(**_valid_kwargs())
    envelope["envelope_version"] = "charness.run_plan_envelope.v99"
    with pytest.raises(ENV.EnvelopeError, match="envelope_version"):
        ENV.validate_envelope(envelope)


def test_validate_envelope_rejects_missing_required_key() -> None:
    envelope = ENV.build_envelope(**_valid_kwargs())
    del envelope["gate_packets"]
    with pytest.raises(ENV.EnvelopeError, match="gate_packets"):
        ENV.validate_envelope(envelope)
