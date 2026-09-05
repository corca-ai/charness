from __future__ import annotations

import json
from pathlib import Path

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


def test_manifest_action_mode_rejects_none_sentinel() -> None:
    schema = json.loads(
        (ROOT / "integrations" / "tools" / "manifest.schema.json").read_text(encoding="utf-8")
    )
    mode = schema["definitions"]["action"]["properties"]["mode"]
    assert "none" not in mode["enum"]
    assert mode["x-axis"] == "install-method"
