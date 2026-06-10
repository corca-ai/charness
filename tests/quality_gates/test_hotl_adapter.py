from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

from .support import ROOT

REPO_ROOT = ROOT


def _load_hotl_module(name: str):
    module_path = ROOT / "skills" / "public" / "hotl" / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"hotl_{name}", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


resolve_adapter = _load_hotl_module("resolve_adapter")


def test_infer_repo_defaults_visible_posture(tmp_path: Path) -> None:
    defaults = resolve_adapter.infer_repo_defaults(tmp_path)

    assert defaults["output_dir"] == "charness-artifacts/hotl"
    assert defaults["surfaces"] == []
    assert defaults["proof_commands"] == []


def test_validate_adapter_accepts_the_shipped_example(tmp_path: Path) -> None:
    example = yaml.safe_load((REPO_ROOT / "skills" / "public" / "hotl" / "adapter.example.yaml").read_text(encoding="utf-8"))

    validated, errors, warnings = resolve_adapter.validate_adapter_data(example, tmp_path)

    assert errors == []
    # the example ships placeholder commands; the resolver must say so visibly
    assert any("placeholder text" in warning for warning in warnings)
    assert [entry["kind"] for entry in validated["proof_commands"]] == ["readiness", "readback", "live"]
    assert validated["proof_commands"][2]["boundary_reason_required"] is True
    assert validated["ledger_path"] == "charness-artifacts/hotl/proof-ledger.json"
    assert validated["completion_audit_command"].endswith("--json")


def test_validate_adapter_defaults_boundary_reason_by_kind(tmp_path: Path) -> None:
    data = {
        "proof_commands": [
            {"id": "go-live", "command": "x --json", "kind": "live"},
            {"id": "read", "command": "y --json", "kind": "readback"},
        ]
    }

    validated, errors, _warnings = resolve_adapter.validate_adapter_data(data, tmp_path)

    assert errors == []
    assert validated["proof_commands"][0]["boundary_reason_required"] is True
    assert validated["proof_commands"][1]["boundary_reason_required"] is False


def test_validate_adapter_rejects_malformed_proof_surface(tmp_path: Path) -> None:
    data = {
        "surfaces": ["chat", 3],
        "proof_commands": [
            "not-a-mapping",
            {"id": "", "command": "x", "kind": "live"},
            {"id": "a", "command": "", "kind": "live"},
            {"id": "b", "command": "x", "kind": "bogus"},
            {"id": "c", "command": "x", "kind": "live", "boundary_reason_required": "yes"},
        ],
    }

    _validated, errors, _warnings = resolve_adapter.validate_adapter_data(data, tmp_path)

    assert "surfaces must be a list of non-empty strings" in errors
    assert any("proof_commands[0] must be a mapping" in error for error in errors)
    assert any("proof_commands[1].id" in error for error in errors)
    assert any("proof_commands[2].command" in error for error in errors)
    assert any("proof_commands[3].kind" in error for error in errors)
    assert any("proof_commands[4].boundary_reason_required" in error for error in errors)


def test_validate_adapter_rejects_non_list_proof_commands_and_bad_fields(tmp_path: Path) -> None:
    data = {"proof_commands": "run-everything", "version": "one", "ledger_path": 3}

    _validated, errors, _warnings = resolve_adapter.validate_adapter_data(data, tmp_path)

    assert "proof_commands must be a list of mappings" in errors
    assert "version must be an integer" in errors
    assert "ledger_path must be a string" in errors


def test_validate_adapter_warns_on_placeholder_and_empty_proof_surface(tmp_path: Path) -> None:
    _validated, errors, warnings = resolve_adapter.validate_adapter_data({"repo": "CHANGE_ME"}, tmp_path)

    assert errors == []
    assert any("CHANGE_ME" in warning for warning in warnings)
    assert any("proof_commands is empty" in warning for warning in warnings)


def test_validate_adapter_rejects_unknown_artifact_class(tmp_path: Path) -> None:
    _validated, errors, _warnings = resolve_adapter.validate_adapter_data({"artifact_class": "bogus"}, tmp_path)

    assert "artifact_class must be one of: current, history, rolling" in errors


def test_resolve_adapter_visible_fallback_without_adapter(tmp_path: Path) -> None:
    payload = resolve_adapter.load_adapter(tmp_path)

    assert payload["found"] is False
    assert payload["valid"] is True
    assert payload["data"]["proof_commands"] == []
    assert any("visible inferred defaults" in warning for warning in payload["warnings"])


def test_init_adapter_scaffolds_empty_proof_surface(tmp_path: Path, monkeypatch, capsys) -> None:
    init_adapter = _load_hotl_module("init_adapter")
    monkeypatch.setattr(
        "sys.argv",
        ["init_adapter.py", "--repo-root", str(tmp_path)],
    )

    init_adapter.main()

    assert str(tmp_path / ".agents" / "hotl-adapter.yaml") in capsys.readouterr().out
    adapter = yaml.safe_load((tmp_path / ".agents" / "hotl-adapter.yaml").read_text(encoding="utf-8"))
    assert adapter["output_dir"] == "charness-artifacts/hotl"
    assert adapter["surfaces"] == []
    assert adapter["proof_commands"] == []
