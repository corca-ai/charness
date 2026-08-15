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
        # A disclosure is MANDATORY as of the #584 slice; an undisclosed read is
        # its own test below, not the shape every other case is built on.
        "required_reads": [
            ENV.disclose_read_measurement(
                ENV.read("references/x.md", "why", kind="reference", base="skill"), size_bytes=12
            )
        ],
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


def test_read_measurement_disclosures_are_strict_and_additive() -> None:
    item = ENV.read("p", "w")
    assert ENV.disclose_read_measurement(item, size_bytes=0)["size_bytes"] == 0
    unavailable = ENV.disclose_read_measurement(item, unavailable_reason="missing")
    assert unavailable["measurement_state"] == "unavailable"
    assert unavailable["unavailable_reason"] == "missing"
    with pytest.raises(ENV.EnvelopeError, match="exactly one"):
        ENV.disclose_read_measurement(item)


@pytest.mark.parametrize(
    "read",
    [
        {"path": "p", "why": "w", "size_bytes": -1},
        {"path": "p", "why": "w", "size_bytes": True},
        {"path": "p", "why": "w", "size_bytes": 1, "unavailable_reason": "missing"},
        {"path": "p", "why": "w", "measurement_state": "available", "unavailable_reason": "missing"},
        {"path": "p", "why": "w", "measurement_state": "unavailable", "unavailable_reason": "other"},
    ],
)
def test_validate_envelope_rejects_invalid_read_measurement(read: dict) -> None:
    kwargs = _valid_kwargs()
    kwargs["required_reads"] = [read]
    with pytest.raises(ENV.EnvelopeError, match="measurement|size_bytes|unavailable_reason"):
        ENV.build_envelope(**kwargs)


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
        required_reads=[ENV.disclose_read_measurement(ENV.read("references/a.md", "primer"), size_bytes=7)],
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


def test_a_read_disclosing_no_measurement_is_refused() -> None:
    """#584: the planner already resolved the path, so an unpriced read is the defect.

    Before this slice the validator `continue`d past an undisclosed read, which is
    why the original rollout stopped at three planners and five kept emitting
    unpriced reads with nothing red.
    """
    kwargs = _valid_kwargs()
    kwargs["required_reads"] = [ENV.read("references/x.md", "why")]
    with pytest.raises(ENV.EnvelopeError, match="discloses no measurement"):
        ENV.build_envelope(**kwargs)


def test_measure_read_prices_a_real_file_from_its_declared_base(tmp_path) -> None:
    target = tmp_path / "references" / "a.md"
    target.parent.mkdir(parents=True)
    target.write_text("hello", encoding="utf-8")
    measured = ENV.measure_read(ENV.read("references/a.md", "why", base="skill"), {"skill": tmp_path})
    assert measured["size_bytes"] == 5


def test_measure_read_types_every_way_it_could_not_measure(tmp_path) -> None:
    """An unmeasurable read carries a typed reason; silence is what #584 reports."""
    (tmp_path / "dir").mkdir()
    cases = {
        "unknown-base": (ENV.read("a.md", "w", base="nowhere"), {"skill": tmp_path}),
        "missing": (ENV.read("absent.md", "w", base="skill"), {"skill": tmp_path}),
        "not-a-file": (ENV.read("dir", "w", base="skill"), {"skill": tmp_path}),
        "outside-declared-base": (ENV.read("../escape.md", "w", base="skill"), {"skill": tmp_path}),
    }
    for expected, (item, bases) in cases.items():
        measured = ENV.measure_read(item, bases)
        assert measured["measurement_state"] == "unavailable"
        assert measured["unavailable_reason"] == expected, expected
        # Every one of these still validates, so an unmeasurable read is disclosed
        # rather than blocking a planner that legitimately cannot stat.
        ENV.validate_envelope({**_valid_kwargs(), "envelope_version": ENV.ENVELOPE_VERSION,
                               "required_reads": [measured]})


def test_a_base_may_declare_a_wider_containment_root(tmp_path) -> None:
    """gather anchors at its own skill dir and deliberately reads a sibling package."""
    skill = tmp_path / "public" / "gather"
    sibling = tmp_path / "support" / "web-fetch" / "references"
    sibling.mkdir(parents=True)
    skill.mkdir(parents=True)
    (sibling / "routing-table.md").write_text("route", encoding="utf-8")
    item = ENV.read("../../support/web-fetch/references/routing-table.md", "why")
    assert ENV.measure_read(item, {None: skill})["unavailable_reason"] == "outside-declared-base"
    assert ENV.measure_read(item, {None: (skill, tmp_path)})["size_bytes"] == 5
