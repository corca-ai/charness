"""Tests for the #339 proof-semantics adapter boundary.

The portable core learns NO domain proof concept: the adapter declares the proof
levels and the acceptance->proof map, and Charness only does generic
rank/incomparability lookups. These tests drive behavior with a SYNTHETIC adapter
(no Slack/Workspace/receipt/channel term) and prove the missing-adapter
degradation path.
"""
from __future__ import annotations

from pathlib import Path

from scripts import proof_semantics_adapter_lib as psa


def _write_adapter(repo_root: Path, body: str) -> None:
    target = repo_root / ".agents" / "proof-semantics-adapter.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")


_SYNTHETIC = """version: 1
repo: synthetic
proof_levels:
  - lint
  - smoke
  - integration
  - live
incomparable:
  - lint, smoke
acceptance_map:
  reliability: integration
  safety: live
verifier_refs:
  integration: pytest tests/integration
  live: provider roundtrip observed
gap_policy:
  acceptable:
    - perf
  out_of_scope:
    - telemetry
  needs_issue: true
"""


# --- resolution: missing / valid / invalid ---------------------------------


def test_missing_adapter_degrades_not_absent(tmp_path: Path) -> None:
    adapter = psa.load_adapter(tmp_path)
    assert adapter["found"] is False
    assert adapter["valid"] is True  # degraded, not a hard error
    assert adapter["data"]["acceptance_map"] == {}
    assert adapter["data"]["proof_levels"] == []
    assert any("degrades" in w for w in adapter["warnings"])
    # the degradation signal Slice-3 keys on:
    assert psa.acceptance_map_available(adapter) is False


def test_valid_synthetic_adapter_parses_all_sections(tmp_path: Path) -> None:
    _write_adapter(tmp_path, _SYNTHETIC)
    adapter = psa.load_adapter(tmp_path)
    assert adapter["found"] is True and adapter["valid"] is True, adapter["errors"]
    data = adapter["data"]
    assert data["proof_levels"] == ["lint", "smoke", "integration", "live"]
    assert data["incomparable"] == [["lint", "smoke"]]
    assert data["acceptance_map"] == {"reliability": "integration", "safety": "live"}
    assert data["verifier_refs"]["integration"] == "pytest tests/integration"
    assert data["gap_policy"]["acceptable"] == ["perf"]
    assert data["gap_policy"]["out_of_scope"] == ["telemetry"]
    assert data["gap_policy"]["needs_issue"] is True
    assert psa.acceptance_map_available(adapter) is True


def test_acceptance_map_referencing_undeclared_level_is_invalid(tmp_path: Path) -> None:
    _write_adapter(tmp_path, "proof_levels:\n  - smoke\nacceptance_map:\n  reliability: integration\n")
    adapter = psa.load_adapter(tmp_path)
    assert adapter["valid"] is False
    assert any("undeclared proof level `integration`" in e for e in adapter["errors"])
    assert psa.acceptance_map_available(adapter) is False  # invalid -> not available


def test_acceptance_map_without_proof_levels_is_invalid(tmp_path: Path) -> None:
    _write_adapter(tmp_path, "acceptance_map:\n  reliability: integration\n")
    adapter = psa.load_adapter(tmp_path)
    assert adapter["valid"] is False
    assert any("acceptance_map is declared but proof_levels is empty" in e for e in adapter["errors"])


def test_incomparable_validation_errors(tmp_path: Path) -> None:
    # self-pair + undeclared level
    _write_adapter(
        tmp_path,
        "proof_levels:\n  - smoke\n  - live\nincomparable:\n  - smoke, smoke\n  - smoke, ghost\n",
    )
    adapter = psa.load_adapter(tmp_path)
    assert adapter["valid"] is False
    joined = " ".join(adapter["errors"])
    assert "pairs a level with itself" in joined
    assert "undeclared proof level `ghost`" in joined


def test_duplicate_proof_level_and_bad_types_are_invalid(tmp_path: Path) -> None:
    _write_adapter(tmp_path, "proof_levels:\n  - smoke\n  - smoke\n")
    assert any("duplicate level `smoke`" in e for e in psa.load_adapter(tmp_path)["errors"])
    _write_adapter(tmp_path, "version: notanint\nproof_levels:\n  - smoke\n")
    assert any("version must be an integer" in e for e in psa.load_adapter(tmp_path)["errors"])


# --- generic partial-order queries (the proof math, domain-blind) ----------


def _data(tmp_path: Path) -> dict:
    _write_adapter(tmp_path, _SYNTHETIC)
    return psa.load_adapter(tmp_path)["data"]


def test_level_satisfies_respects_rank_and_incomparability(tmp_path: Path) -> None:
    data = _data(tmp_path)
    # equal satisfies
    assert psa.level_satisfies(data, "integration", "integration") is True
    # higher backbone rank satisfies a lower requirement
    assert psa.level_satisfies(data, "live", "integration") is True
    # lower rank does NOT satisfy a higher requirement (the mismatch case)
    assert psa.level_satisfies(data, "smoke", "integration") is False
    # a declared-incomparable pair never satisfies, in EITHER direction, despite rank
    assert psa.level_satisfies(data, "smoke", "lint") is False
    assert psa.level_satisfies(data, "lint", "smoke") is False
    # an undeclared level -> None (degraded / no-map, never a silent pass)
    assert psa.level_satisfies(data, "ghost", "integration") is None
    assert psa.level_satisfies(data, "live", "ghost") is None


def test_level_rank_and_incomparable_helpers(tmp_path: Path) -> None:
    data = _data(tmp_path)
    assert psa.proof_level_rank(data, "lint") == 0
    assert psa.proof_level_rank(data, "live") == 3
    assert psa.proof_level_rank(data, "ghost") is None
    assert psa.levels_incomparable(data, "smoke", "lint") is True
    assert psa.levels_incomparable(data, "lint", "smoke") is True  # order-insensitive
    assert psa.levels_incomparable(data, "smoke", "live") is False


def test_min_level_for_acceptance_and_gap_disposition(tmp_path: Path) -> None:
    data = _data(tmp_path)
    assert psa.min_level_for_acceptance(data, "reliability") == "integration"
    assert psa.min_level_for_acceptance(data, "safety") == "live"
    assert psa.min_level_for_acceptance(data, "unmapped") is None
    # gap policy lookup
    assert psa.gap_disposition_for(data, "perf") == "acceptable"
    assert psa.gap_disposition_for(data, "telemetry") == "out-of-scope"
    assert psa.gap_disposition_for(data, "reliability") == "needs-issue"  # unclassified, needs_issue=true


def test_gap_disposition_default_when_needs_issue_false(tmp_path: Path) -> None:
    _write_adapter(tmp_path, "proof_levels:\n  - smoke\ngap_policy:\n  needs_issue: false\n")
    data = psa.load_adapter(tmp_path)["data"]
    assert psa.gap_disposition_for(data, "anything") == "acceptable"


def test_acceptance_classes_accessor(tmp_path: Path) -> None:
    # Slice-3 condition (i) reads declared classes through this accessor.
    data = _data(tmp_path)
    assert psa.acceptance_classes(data) == ["reliability", "safety"]
    # missing adapter -> no declared classes (degraded)
    assert psa.acceptance_classes(psa.load_adapter(tmp_path.parent / "nope")["data"]) == []


def test_gap_policy_double_listed_class_warns_acceptable_wins(tmp_path: Path) -> None:
    _write_adapter(
        tmp_path,
        "proof_levels:\n  - smoke\ngap_policy:\n  acceptable:\n    - perf\n  out_of_scope:\n    - perf\n",
    )
    adapter = psa.load_adapter(tmp_path)
    assert adapter["valid"] is True  # a warning, not a hard error
    assert any("both `acceptable` and `out_of_scope`" in w for w in adapter["warnings"])
    assert psa.gap_disposition_for(adapter["data"], "perf") == "acceptable"  # acceptable wins


# --- the cardinal Non-Goal: NO domain concept enters portable core ----------


def test_validate_adapter_data_type_errors_each_section(tmp_path: Path) -> None:
    # Direct validate_adapter_data drive of every type-error branch (the minimal
    # YAML loader cannot express some malformed shapes, so go through the dict API).
    root = tmp_path

    def errs(data: dict) -> str:
        return " ".join(psa.validate_adapter_data(data, root)[1])

    assert "repo must be a string" in errs({"repo": 123})
    assert "proof_levels must be a list of strings" in errs({"proof_levels": 123})
    assert "incomparable must be a list" in errs({"proof_levels": ["a"], "incomparable": "x"})
    assert "must be a level pair" in errs({"proof_levels": ["a"], "incomparable": [123]})
    assert "acceptance_map must be a mapping" in errs({"proof_levels": ["a"], "acceptance_map": "x"})
    assert "must name a proof level" in errs({"proof_levels": ["a"], "acceptance_map": {"r": 5}})
    assert "verifier_refs must be a mapping" in errs({"proof_levels": ["a"], "verifier_refs": "x"})
    assert "verifier_refs.a must be a string" in errs({"proof_levels": ["a"], "verifier_refs": {"a": 123}})
    assert "undeclared proof level `ghost`" in errs({"proof_levels": ["a"], "verifier_refs": {"ghost": "x"}})
    assert "gap_policy must be a mapping" in errs({"gap_policy": "x"})
    assert "gap_policy.acceptable must be a list" in errs({"gap_policy": {"acceptable": "x"}})
    assert "gap_policy.needs_issue must be a boolean" in errs({"gap_policy": {"needs_issue": "x"}})


def test_validate_adapter_data_incomparable_list_form_and_change_me_warning(tmp_path: Path) -> None:
    # The [a, b] list form of an incomparable pair (a host with a full YAML loader).
    validated, errors, warnings = psa.validate_adapter_data(
        {"proof_levels": ["lint", "smoke"], "incomparable": [["lint", "smoke"]]}, tmp_path
    )
    assert errors == []
    assert validated["incomparable"] == [["lint", "smoke"]]
    # CHANGE_ME repo placeholder warns.
    _, _, warns2 = psa.validate_adapter_data({"repo": "CHANGE_ME"}, tmp_path)
    assert any("CHANGE_ME" in w for w in warns2)


def test_load_adapter_non_canonical_path_and_non_mapping_file(tmp_path: Path) -> None:
    # A compatibility-fallback path (.codex/...) warns to prefer the canonical path.
    fallback = tmp_path / ".codex" / "proof-semantics-adapter.yaml"
    fallback.parent.mkdir(parents=True, exist_ok=True)
    fallback.write_text("proof_levels:\n  - smoke\n", encoding="utf-8")
    adapter = psa.load_adapter(tmp_path)
    assert adapter["found"] is True
    assert any("compatibility fallback" in w for w in adapter["warnings"])


def test_load_adapter_non_mapping_yaml_uses_defaults(tmp_path: Path, monkeypatch) -> None:
    # Defensive branch: a YAML loader that returns a non-mapping -> warn + defaults.
    target = tmp_path / ".agents" / "proof-semantics-adapter.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("- a\n- b\n", encoding="utf-8")
    monkeypatch.setattr(psa, "load_yaml_file", lambda path: ["not", "a", "mapping"])
    adapter = psa.load_adapter(tmp_path)
    assert adapter["found"] is True
    assert any("did not contain a mapping" in w for w in adapter["warnings"])
    assert adapter["data"]["proof_levels"] == []  # inferred defaults


def test_core_module_is_domain_blind() -> None:
    # The adapter declares domain tokens as DATA; the core code must contain none.
    source = Path(psa.__file__).read_text(encoding="utf-8").lower()
    forbidden = (
        "slack", "workspace", "receipt", "channel", "app_mention",
        "ceal-dev", "reliability", "smoke", "integration", "telemetry",
    )
    hits = [term for term in forbidden if term in source]
    assert hits == [], f"portable proof-semantics core leaked domain tokens: {hits}"
