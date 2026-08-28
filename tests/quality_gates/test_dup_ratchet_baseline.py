"""Item-5 slice D: gate-baseline schema v3 (dup_ratchet_baseline_lib).

Split out of ``test_dup_ratchet.py`` (test-file length cap), mirroring the source
split: ``dup_ratchet_baseline_lib`` owns the ``dup-ratchet-baseline.json`` schema
(build/load/validate, per-family ``{fingerprint, member_hashes}``, tool/algo version
stamps) as its own concern from the two-arm policy and the CLI. See
``charness-artifacts/spec/boy-scout-dup-ratchet.md`` (Slice 4, S4-Defer-3).
"""

from __future__ import annotations

from .support import ROOT
from .seeding_support import load_module

SCRIPTS = ROOT / "skills" / "public" / "quality" / "scripts"


def _load(name: str):
    return load_module(f"{name}_inproc", SCRIPTS / f"{name}.py")


baseline_lib = _load("dup_ratchet_baseline_lib")


# --------------------------------------------------------------------------- #
# Gate baseline (schema v3) build/load/validate
# --------------------------------------------------------------------------- #
def test_build_and_load_gate_baseline_roundtrip() -> None:
    baseline = baseline_lib.build_gate_baseline({"b": ["b1", "b2"], "a": ["a1"], "": ["ignored"]})
    assert baseline["code_families"] == [
        {"fingerprint": "a", "member_hashes": ["a1"]},
        {"fingerprint": "b", "member_hashes": ["b1", "b2"]},
    ]  # sorted by fingerprint, empty fingerprint dropped
    assert baseline["schemaVersion"] == baseline_lib.GATE_BASELINE_SCHEMA_VERSION
    assert baseline_lib.validate_gate_baseline(baseline) == []
    assert baseline_lib.load_gate_baseline_ids(baseline) == {"a", "b"}
    assert baseline_lib.load_gate_baseline_members(baseline) == {"a": ["a1"], "b": ["b1", "b2"]}


def test_load_gate_baseline_ids_none_on_malformed_or_legacy() -> None:
    assert baseline_lib.load_gate_baseline_ids(None) is None
    assert baseline_lib.load_gate_baseline_ids({"code_families": "nope"}) is None
    assert baseline_lib.load_gate_baseline_ids([1, 2]) is None
    assert baseline_lib.load_gate_baseline_ids({"code_families": ["not-a-dict"]}) is None
    # A legacy v1 baseline (code_family_ids) or v2 baseline (code_family_fingerprints)
    # reads as None (no dual-read), so the gate degrades to advisory until a deliberate
    # re-baseline mints v3 per-family member hashes.
    assert baseline_lib.load_gate_baseline_ids({"code_family_ids": ["a", "b"]}) is None
    assert baseline_lib.load_gate_baseline_ids({"code_family_fingerprints": ["a", "b"]}) is None


def test_load_gate_baseline_members_none_on_malformed_or_missing_hashes() -> None:
    assert baseline_lib.load_gate_baseline_members(None) is None
    assert baseline_lib.load_gate_baseline_members({"code_families": [{"fingerprint": "a"}]}) is None
    assert baseline_lib.load_gate_baseline_members({"code_family_fingerprints": ["a"]}) is None
    # A non-dict entry in code_families -> None (same defensive shape guard as
    # load_gate_baseline_ids, but exercised here for load_gate_baseline_members).
    assert baseline_lib.load_gate_baseline_members({"code_families": ["not-a-dict"]}) is None
    baseline = baseline_lib.build_gate_baseline({"a": ["h1", "h2"]})
    assert baseline_lib.load_gate_baseline_members(baseline) == {"a": ["h1", "h2"]}


def test_validate_gate_baseline_rejects_non_dict_top_level() -> None:
    assert baseline_lib.validate_gate_baseline("nope") == ["gate baseline must be a JSON object"]
    assert baseline_lib.validate_gate_baseline(None) == ["gate baseline must be a JSON object"]
    assert baseline_lib.validate_gate_baseline([1, 2]) == ["gate baseline must be a JSON object"]


def test_validate_gate_baseline_flags_bad_schema_and_shape() -> None:
    errors = baseline_lib.validate_gate_baseline(
        {"schemaVersion": "wrong", "code_families": [{"fingerprint": "", "member_hashes": []}, "not-a-dict"]}
    )
    joined = " ".join(errors)
    assert "schemaVersion" in joined
    assert "code_families[0].fingerprint" in joined and "code_families[0].member_hashes" in joined
    assert "code_families[1] must be an object" in joined


def test_validate_gate_baseline_flags_non_string_member_hash() -> None:
    baseline = {
        "schemaVersion": baseline_lib.GATE_BASELINE_SCHEMA_VERSION,
        "code_families": [{"fingerprint": "a", "member_hashes": ["ok", 5, ""]}],
    }
    errors = baseline_lib.validate_gate_baseline(baseline)
    assert any("code_families[0].member_hashes[1]" in e for e in errors)
    assert any("code_families[0].member_hashes[2]" in e for e in errors)


def test_validate_gate_baseline_rejects_non_list_code_families() -> None:
    errors = baseline_lib.validate_gate_baseline(
        {"schemaVersion": baseline_lib.GATE_BASELINE_SCHEMA_VERSION, "code_families": "nope"}
    )
    assert any("code_families must be a list" in e for e in errors)


# --------------------------------------------------------------------------- #
# Scanner tool_version stamp (issue #391): build stamps it, validate accepts it as
# an optional string, the read path exposes it for skew detection.
# --------------------------------------------------------------------------- #
def test_build_gate_baseline_stamps_and_reads_tool_and_algo_version() -> None:
    assert "tool_version" not in baseline_lib.build_gate_baseline({"a": ["a1"]})  # unknown stays unstamped
    assert "fingerprint_algo_version" not in baseline_lib.build_gate_baseline({"a": ["a1"]})
    stamped = baseline_lib.build_gate_baseline(
        {"b": ["b1"], "a": ["a1"]}, tool_version="0.15.0", algo_version="2"
    )
    assert stamped["tool_version"] == "0.15.0"
    assert baseline_lib.load_gate_baseline_ids(stamped) == {"a", "b"}
    assert stamped["fingerprint_algo_version"] == "2"
    assert baseline_lib.validate_gate_baseline(stamped) == []
    assert baseline_lib.load_gate_baseline_tool_version(stamped) == "0.15.0"
    assert baseline_lib.load_gate_baseline_algo_version(stamped) == "2"


def test_algo_version_skew_warns_on_mismatch_else_none() -> None:
    assert baseline_lib.algo_version_skew("1", "2") is not None
    assert baseline_lib.algo_version_skew("1", "1") is None
    assert baseline_lib.algo_version_skew("", "1") is None  # missing stamp is "unknown", not a mismatch
    assert baseline_lib.algo_version_skew("1", "") is None


def test_load_gate_baseline_versions_empty_on_absent_or_nonstring() -> None:
    assert baseline_lib.load_gate_baseline_tool_version({"code_families": []}) == ""
    assert baseline_lib.load_gate_baseline_tool_version({"tool_version": 14}) == ""
    assert baseline_lib.load_gate_baseline_algo_version({"fingerprint_algo_version": 1}) == ""
    assert baseline_lib.load_gate_baseline_algo_version(None) == ""


def test_validate_gate_baseline_rejects_nonstring_version_stamps() -> None:
    errors = baseline_lib.validate_gate_baseline(
        {"schemaVersion": baseline_lib.GATE_BASELINE_SCHEMA_VERSION, "tool_version": 14,
         "fingerprint_algo_version": 1, "code_families": [{"fingerprint": "a", "member_hashes": ["a1"]}]}
    )
    assert any("tool_version" in e for e in errors)
    assert any("fingerprint_algo_version" in e for e in errors)
