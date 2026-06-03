from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "skills/public/quality/references/boundary-bypass-payload.example.json"
VALIDATOR = ROOT / "skills/public/quality/scripts/validate_boundary_bypass_payload.py"
SPEC = importlib.util.spec_from_file_location("validate_boundary_bypass_payload", VALIDATOR)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def test_validates_stack_neutral_boundary_bypass_example() -> None:
    payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    summary = validator.validate_payload(payload)
    assert summary["candidate_count"] == 3
    assert summary["candidate_key_count"] == 3
    assert summary["internal_boundary_count"] == 1


def test_rejects_summary_count_drift(tmp_path: Path) -> None:
    payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    payload["summary"]["convertible_count"] = 99
    path = tmp_path / "payload.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    loaded = json.loads(path.read_text(encoding="utf-8"))
    try:
        validator.validate_payload(loaded)
    except validator.ValidationError as exc:
        assert "summary.convertible_count" in str(exc)
    else:
        raise AssertionError("expected summary count drift to fail validation")


def test_rejects_clean_and_internal_target_overlap() -> None:
    payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    payload["candidates"][0]["internal_boundary_targets"] = payload["candidates"][0]["clean_inprocess_targets"]
    payload["summary"]["internal_boundary_count"] = 2
    try:
        validator.validate_payload(payload)
    except validator.ValidationError as exc:
        assert "both clean and internal-boundary" in str(exc)
    else:
        raise AssertionError("expected overlapping clean/internal targets to fail validation")
