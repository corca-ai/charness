"""No-increase ratchet for the repo-local boundary-bypass inventory."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RATCHET_SCHEMA_VERSION = "charness.quality.boundary_bypass_ratchet.v1"
DEFAULT_BASELINE_PATH = Path("scripts/boundary-bypass-baseline.json")
DEFAULT_EXEMPTIONS_PATH = Path("scripts/boundary-bypass-exemptions.txt")
COUNT_FIELDS = (
    "candidate_count",
    "convertible_count",
    "internal_boundary_count",
    "keep_boundary_count",
    "candidate_key_count",
)


class RatchetError(ValueError):
    """Raised when ratchet input files are malformed."""


def candidate_key(test_file: str, target: str) -> str:
    return f"{test_file}::{target}"


def candidate_keys(payload: dict[str, Any]) -> list[str]:
    keys: list[str] = []
    for row in payload.get("candidates", []):
        test_file = str(row.get("test_file", ""))
        for target in row.get("import_safe_targets", []):
            if test_file and isinstance(target, str):
                keys.append(candidate_key(test_file, target))
    return sorted(set(keys))


def load_exemptions(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    exemptions: dict[str, str] = {}
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, marker, why = line.partition("# why:")
        if not marker or not key.strip() or not why.strip():
            raise RatchetError(f"{path}:{line_number}: exemption must be `<test_file>::<target> # why: <rationale>`")
        rendered_key = key.strip()
        if "::" not in rendered_key:
            raise RatchetError(f"{path}:{line_number}: exemption key must use `<test_file>::<target>`")
        exemptions[rendered_key] = why.strip()
    return exemptions


def filtered_summary(payload: dict[str, Any], exemptions: dict[str, str]) -> dict[str, int]:
    rows = []
    key_count = 0
    for row in payload.get("candidates", []):
        test_file = str(row.get("test_file", ""))
        targets = [
            target
            for target in row.get("import_safe_targets", [])
            if isinstance(target, str) and candidate_key(test_file, target) not in exemptions
        ]
        if not targets:
            continue
        clean = [
            target
            for target in row.get("clean_inprocess_targets", [])
            if isinstance(target, str) and target in targets
        ]
        internal = [
            target
            for target in row.get("internal_boundary_targets", [])
            if isinstance(target, str) and target in targets
        ]
        rows.append({"likely_keep_boundary": bool(row.get("likely_keep_boundary")), "clean": clean, "internal": internal})
        key_count += len(targets)
    keep_boundary = sum(1 for row in rows if row["likely_keep_boundary"])
    return {
        "candidate_count": len(rows),
        "convertible_count": sum(1 for row in rows if (not row["likely_keep_boundary"]) and row["clean"]),
        "internal_boundary_count": sum(1 for row in rows if row["internal"]),
        "keep_boundary_count": keep_boundary,
        "candidate_key_count": key_count,
    }


def build_baseline(payload: dict[str, Any], exemptions: dict[str, str] | None = None) -> dict[str, Any]:
    exemptions = exemptions or {}
    keys = [key for key in candidate_keys(payload) if key not in exemptions]
    return {
        "schemaVersion": RATCHET_SCHEMA_VERSION,
        "policy": "no_increase",
        "inventory_schemaVersion": payload.get("schemaVersion"),
        "summary": filtered_summary(payload, exemptions),
        "candidate_keys": keys,
    }


def load_baseline(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RatchetError(f"baseline not found: {path}")
    try:
        baseline = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RatchetError(f"{path}: invalid JSON: {exc}") from exc
    if baseline.get("schemaVersion") != RATCHET_SCHEMA_VERSION:
        raise RatchetError(f"{path}: unexpected schemaVersion {baseline.get('schemaVersion')!r}")
    if baseline.get("policy") != "no_increase":
        raise RatchetError(f"{path}: expected policy `no_increase`")
    if not isinstance(baseline.get("summary"), dict) or not isinstance(baseline.get("candidate_keys"), list):
        raise RatchetError(f"{path}: expected `summary` object and `candidate_keys` list")
    return baseline


def check_payload(payload: dict[str, Any], baseline: dict[str, Any], exemptions: dict[str, str]) -> dict[str, Any]:
    schema_mismatch = None
    baseline_inventory_schema = baseline.get("inventory_schemaVersion")
    current_inventory_schema = payload.get("schemaVersion")
    if baseline_inventory_schema != current_inventory_schema:
        schema_mismatch = {
            "baseline": baseline_inventory_schema,
            "current": current_inventory_schema,
        }
    current_keys = [key for key in candidate_keys(payload) if key not in exemptions]
    baseline_keys = {str(key) for key in baseline.get("candidate_keys", [])}
    current_summary = filtered_summary(payload, exemptions)
    baseline_summary = baseline["summary"]
    count_increases = {
        field: {"baseline": int(baseline_summary.get(field, 0)), "current": current_summary[field]}
        for field in COUNT_FIELDS
        if current_summary[field] > int(baseline_summary.get(field, 0))
    }
    new_keys = sorted(set(current_keys) - baseline_keys)
    return {
        "ok": not schema_mismatch and not count_increases and not new_keys,
        "policy": "no_increase",
        "schema_mismatch": schema_mismatch,
        "summary": current_summary,
        "baseline_summary": {field: int(baseline_summary.get(field, 0)) for field in COUNT_FIELDS},
        "new_candidate_keys": new_keys,
        "count_increases": count_increases,
        "exempted_count": len(exemptions),
    }
