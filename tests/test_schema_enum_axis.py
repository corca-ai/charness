from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

import pytest

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[1]
_check = import_repo_module(
    ROOT / "scripts" / "gates" / "check_schema_enum_axis.py",
    "scripts.gates.check_schema_enum_axis",
)


def test_live_repo_generic_enums_declare_x_axis() -> None:
    assert _check.findings_for(ROOT) == []


def test_generic_kind_enum_without_axis_is_refused(tmp_path: Path) -> None:
    schema = {
        "type": "object",
        "properties": {
            "kind": {"type": "string", "enum": ["repair", "reflection", "simplification"]}
        },
    }
    path = tmp_path / "demo.schema.json"
    path.write_text(json.dumps(schema), encoding="utf-8")
    findings = _check.findings_for(tmp_path)
    assert findings
    assert "generic `kind` enum" in findings[0]
    assert "x-axis" in findings[0]


def test_named_axis_field_does_not_need_x_axis(tmp_path: Path) -> None:
    schema = {
        "type": "object",
        "properties": {
            "delivery_kind": {"type": "string", "enum": ["none", "release-notes"]}
        },
    }
    path = tmp_path / "demo.schema.json"
    path.write_text(json.dumps(schema), encoding="utf-8")
    assert _check.findings_for(tmp_path) == []


def test_generic_mode_enum_inside_oneof_needs_x_axis(tmp_path: Path) -> None:
    schema = {
        "type": "object",
        "properties": {
            "mode": {"oneOf": [{"type": "string", "enum": ["manual", "script"]}]}
        },
    }
    (tmp_path / "demo.schema.json").write_text(json.dumps(schema), encoding="utf-8")
    findings = _check.findings_for(tmp_path)
    assert findings
    assert "generic `mode` enum" in findings[0]


def test_generic_mode_ref_enum_needs_x_axis(tmp_path: Path) -> None:
    schema = {
        "type": "object",
        "properties": {"mode": {"$ref": "#/definitions/installMode"}},
        "definitions": {
            "installMode": {"type": "string", "enum": ["manual", "script"]}
        },
    }
    (tmp_path / "demo.schema.json").write_text(json.dumps(schema), encoding="utf-8")
    findings = _check.findings_for(tmp_path)
    assert findings
    assert "generic `mode` enum" in findings[0]


def test_generic_mode_oneof_with_wrapper_x_axis_passes(tmp_path: Path) -> None:
    schema = {
        "type": "object",
        "properties": {
            "mode": {
                "x-axis": "install-method",
                "oneOf": [{"type": "string", "enum": ["manual", "script"]}],
            }
        },
    }
    (tmp_path / "demo.schema.json").write_text(json.dumps(schema), encoding="utf-8")
    assert _check.findings_for(tmp_path) == []


def test_generic_mode_ref_with_wrapper_x_axis_passes(tmp_path: Path) -> None:
    schema = {
        "type": "object",
        "properties": {
            "mode": {"x-axis": "install-method", "$ref": "#/definitions/installMode"}
        },
        "definitions": {
            "installMode": {"type": "string", "enum": ["manual", "script"]}
        },
    }
    (tmp_path / "demo.schema.json").write_text(json.dumps(schema), encoding="utf-8")
    assert _check.findings_for(tmp_path) == []


def test_generic_mode_ref_enum_with_x_axis_passes(tmp_path: Path) -> None:
    schema = {
        "type": "object",
        "properties": {"mode": {"$ref": "#/definitions/installMode"}},
        "definitions": {
            "installMode": {
                "type": "string",
                "x-axis": "install-method",
                "enum": ["manual", "script"],
            }
        },
    }
    (tmp_path / "demo.schema.json").write_text(json.dumps(schema), encoding="utf-8")
    assert _check.findings_for(tmp_path) == []


def test_findings_skip_non_object_schema_documents(tmp_path: Path) -> None:
    (tmp_path / "list.schema.json").write_text("[]", encoding="utf-8")
    assert _check.findings_for(tmp_path) == []


def test_resolve_local_ref_refuses_non_fragment_and_missing_pointers() -> None:
    assert _check._resolve_local_ref({}, "definitions/x") is None
    assert _check._resolve_local_ref({"definitions": {}}, "#/definitions/missing") is None


def test_circular_local_ref_does_not_loop(tmp_path: Path) -> None:
    schema = {
        "type": "object",
        "properties": {"mode": {"$ref": "#/definitions/loop"}},
        "definitions": {"loop": {"$ref": "#/definitions/loop"}},
    }
    (tmp_path / "demo.schema.json").write_text(json.dumps(schema), encoding="utf-8")
    assert _check.findings_for(tmp_path) == []


def test_main_exits_nonzero_when_a_generic_enum_omits_x_axis(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    schema = {
        "type": "object",
        "properties": {"kind": {"type": "string", "enum": ["a", "b"]}},
    }
    (tmp_path / "demo.schema.json").write_text(json.dumps(schema), encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        ["check_schema_enum_axis.py", "--repo-root", str(tmp_path)],
    )
    assert _check.main() == 1
    assert "generic `kind` enum" in capsys.readouterr().err


def test_main_exits_zero_on_the_live_repo(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["check_schema_enum_axis.py", "--repo-root", str(ROOT)],
    )
    assert _check.main() == 0
    assert "All generic schema enums declare x-axis." in capsys.readouterr().out


def test_script_main_guard_exits_through_main(monkeypatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["check_schema_enum_axis.py", "--repo-root", str(ROOT)],
    )
    with pytest.raises(SystemExit) as exc_info:
        runpy.run_path(str(ROOT / "scripts" / "gates" / "check_schema_enum_axis.py"), run_name="__main__")
    assert exc_info.value.code == 0


def test_bootstrap_inserts_the_repo_root_when_missing(monkeypatch) -> None:
    root = str(ROOT)
    monkeypatch.setattr(sys, "path", [item for item in sys.path if item != root])
    _check._load_repo_runtime_bootstrap()
    assert root in sys.path


def test_manifest_action_mode_rejects_none_sentinel() -> None:
    schema = json.loads(
        (ROOT / "integrations" / "tools" / "manifest.schema.json").read_text(encoding="utf-8")
    )
    mode = schema["definitions"]["action"]["properties"]["mode"]
    assert "none" not in mode["enum"]
    assert mode["x-axis"] == "install-method"
