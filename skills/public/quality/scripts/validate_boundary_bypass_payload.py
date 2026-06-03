#!/usr/bin/env python3
"""Validate a stack-neutral boundary-bypass inventory payload."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "charness.quality.boundary_bypass_inventory.v1"
SUMMARY_FIELDS = (
    "scanned_test_files",
    "candidate_count",
    "convertible_count",
    "keep_boundary_count",
    "internal_boundary_count",
)


class ValidationError(ValueError):
    pass


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValidationError(f"`{field}` must be a list of strings")
    return value


def _bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise ValidationError(f"`{field}` must be a boolean")
    return value


def _nonnegative_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValidationError(f"`{field}` must be a non-negative integer")
    return value


def _validate_candidate(row: Any, index: int) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise ValidationError(f"`candidates[{index}]` must be an object")
    test_file = row.get("test_file")
    if not isinstance(test_file, str) or not test_file:
        raise ValidationError(f"`candidates[{index}].test_file` must be a non-empty string")
    import_safe = _string_list(row.get("import_safe_targets"), f"candidates[{index}].import_safe_targets")
    clean = _string_list(row.get("clean_inprocess_targets"), f"candidates[{index}].clean_inprocess_targets")
    internal = _string_list(row.get("internal_boundary_targets"), f"candidates[{index}].internal_boundary_targets")
    if not import_safe:
        raise ValidationError(f"`candidates[{index}].import_safe_targets` must not be empty")
    if not set(clean).issubset(import_safe):
        raise ValidationError(f"`candidates[{index}].clean_inprocess_targets` must be a subset of import_safe_targets")
    if not set(internal).issubset(import_safe):
        raise ValidationError(f"`candidates[{index}].internal_boundary_targets` must be a subset of import_safe_targets")
    _bool(row.get("has_lib"), f"candidates[{index}].has_lib")
    _bool(row.get("behavior_assert"), f"candidates[{index}].behavior_assert")
    return {
        "likely_keep_boundary": _bool(row.get("likely_keep_boundary"), f"candidates[{index}].likely_keep_boundary"),
        "clean": clean,
        "internal": internal,
    }


def validate_payload(payload: dict[str, Any]) -> dict[str, int]:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValidationError(f"`schemaVersion` must be `{SCHEMA_VERSION}`")
    if payload.get("status") not in {"advisory", "ratchet"}:
        raise ValidationError("`status` must be `advisory` or `ratchet`")
    summary = payload.get("summary")
    candidates = payload.get("candidates")
    if not isinstance(summary, dict):
        raise ValidationError("`summary` must be an object")
    if not isinstance(candidates, list):
        raise ValidationError("`candidates` must be a list")
    for field in SUMMARY_FIELDS:
        _nonnegative_int(summary.get(field), f"summary.{field}")

    keep_boundary = 0
    convertible = 0
    internal_boundary = 0
    for index, row in enumerate(candidates):
        candidate = _validate_candidate(row, index)
        if candidate["likely_keep_boundary"]:
            keep_boundary += 1
        if (not candidate["likely_keep_boundary"]) and candidate["clean"]:
            convertible += 1
        if candidate["internal"]:
            internal_boundary += 1

    derived = {
        "candidate_count": len(candidates),
        "convertible_count": convertible,
        "keep_boundary_count": keep_boundary,
        "internal_boundary_count": internal_boundary,
    }
    for field, value in derived.items():
        if summary[field] != value:
            raise ValidationError(f"`summary.{field}` is {summary[field]}, expected {value}")
    return {field: int(summary[field]) for field in SUMMARY_FIELDS}


def _load_json(path: Path | None) -> dict[str, Any]:
    text = sys.stdin.read() if path is None else path.read_text(encoding="utf-8")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValidationError("top-level payload must be an object")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Payload JSON path; omit to read stdin")
    parser.add_argument("--json", action="store_true", help="Emit validation summary as JSON")
    args = parser.parse_args()
    try:
        summary = validate_payload(_load_json(args.input))
    except ValidationError as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    report = {"ok": True, "summary": summary}
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            "Validated boundary-bypass payload: "
            f"{summary['candidate_count']} candidates, {summary['convertible_count']} clean-convertible"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
