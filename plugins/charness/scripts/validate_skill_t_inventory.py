#!/usr/bin/env python3
"""Validate the Skill-T mechanism inventory artifact (Leg 1).

Acceptance check coverage:

* A1.1 — schema conformance (version, kind, required columns per row).
* A1.2 — every public skill discovered under ``skills/public/`` has a row.
* S1.3 — Tier C column either has the explicit ``"awaiting events"`` marker
  or a populated payload with positive ``event_count`` and non-empty
  ``event_types``.

Exits non-zero when any check fails. JSON details are emitted on stdout so
the caller can route failures into a quality gate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module

_skill_iter_module = import_repo_module(__file__, "scripts.skill_iter")
iter_skill_ids = _skill_iter_module.iter_skill_ids

REQUIRED_TOP_KEYS = {"version", "kind", "tier_c_marker", "skills"}
REQUIRED_ROW_KEYS = {
    "skill_id",
    "lesson_cite_chain",
    "lifecycle_survival",
    "anchor_wiring",
    "tier_c_events",
}
TIER_C_AWAITING = "awaiting events"
TIER_C_POPULATED = "populated"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--inventory-path", type=Path, default=None)
    return parser.parse_args()


def _list_public_skill_ids(repo_root: Path) -> list[str]:
    return iter_skill_ids(repo_root / "skills" / "public")


def _check_top_shape(payload: Any, errors: list[str]) -> bool:
    if not isinstance(payload, dict):
        errors.append("inventory payload is not an object")
        return False
    missing = REQUIRED_TOP_KEYS - set(payload.keys())
    if missing:
        errors.append(f"top-level missing keys: {sorted(missing)}")
    if payload.get("version") != 1:
        errors.append(f"unexpected version: {payload.get('version')!r}")
    if payload.get("kind") != "skill-t-mechanism-inventory":
        errors.append(f"unexpected kind: {payload.get('kind')!r}")
    if payload.get("tier_c_marker") != TIER_C_AWAITING:
        errors.append(
            f"tier_c_marker must be {TIER_C_AWAITING!r}, got "
            f"{payload.get('tier_c_marker')!r}"
        )
    skills = payload.get("skills")
    if not isinstance(skills, list):
        errors.append("skills must be a list")
        return False
    return True


def _check_rows(
    rows: list[Any],
    expected_skill_ids: list[str],
    errors: list[str],
) -> None:
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            errors.append(f"row is not an object: {row!r}")
            continue
        missing = REQUIRED_ROW_KEYS - set(row.keys())
        if missing:
            errors.append(
                f"row missing required keys: {sorted(missing)} "
                f"(skill_id={row.get('skill_id')!r})"
            )
            continue
        skill_id = row["skill_id"]
        if not isinstance(skill_id, str):
            errors.append(f"skill_id must be a string: {row!r}")
            continue
        if skill_id in seen:
            errors.append(f"duplicate row for skill_id: {skill_id!r}")
        seen.add(skill_id)
        _check_lesson_cite_chain(row["lesson_cite_chain"], skill_id, errors)
        _check_lifecycle_survival(row["lifecycle_survival"], skill_id, errors)
        _check_anchor_wiring(row["anchor_wiring"], skill_id, errors)
        _check_tier_c_events(row["tier_c_events"], skill_id, errors)
    expected = set(expected_skill_ids)
    missing_skills = expected - seen
    if missing_skills:
        errors.append(
            f"missing rows for public skills: {sorted(missing_skills)}"
        )
    extra_skills = seen - expected
    if extra_skills:
        errors.append(
            f"unexpected rows not matching public skills: {sorted(extra_skills)}"
        )


def _check_lesson_cite_chain(value: Any, skill_id: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{skill_id}: lesson_cite_chain is not an object")
        return
    if value.get("tier") != "B":
        errors.append(f"{skill_id}: lesson_cite_chain.tier must be 'B'")
    if not isinstance(value.get("retro_artifacts"), list):
        errors.append(f"{skill_id}: lesson_cite_chain.retro_artifacts must be a list")
    if not isinstance(value.get("retro_artifact_count"), int):
        errors.append(
            f"{skill_id}: lesson_cite_chain.retro_artifact_count must be an int"
        )


def _check_lifecycle_survival(value: Any, skill_id: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{skill_id}: lifecycle_survival is not an object")
        return
    if value.get("tier") != "B+":
        errors.append(f"{skill_id}: lifecycle_survival.tier must be 'B+'")
    for required in ("matched_lesson_count", "max_source_count"):
        if not isinstance(value.get(required), int):
            errors.append(
                f"{skill_id}: lifecycle_survival.{required} must be an int"
            )
    age = value.get("freshest_age_days")
    if age is not None and not isinstance(age, int):
        errors.append(
            f"{skill_id}: lifecycle_survival.freshest_age_days must be int or null"
        )


def _check_anchor_wiring(value: Any, skill_id: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{skill_id}: anchor_wiring is not an object")
        return
    if value.get("orthogonal_to_t_tier") is not True:
        errors.append(
            f"{skill_id}: anchor_wiring.orthogonal_to_t_tier must be true"
        )
    anchors = value.get("anchors")
    if not isinstance(anchors, list) or not all(isinstance(a, str) for a in anchors):
        errors.append(f"{skill_id}: anchor_wiring.anchors must be a list of strings")


def _check_tier_c_events(value: Any, skill_id: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{skill_id}: tier_c_events is not an object")
        return
    status = value.get("status")
    if status not in (TIER_C_AWAITING, TIER_C_POPULATED):
        errors.append(
            f"{skill_id}: tier_c_events.status must be "
            f"{TIER_C_AWAITING!r} or {TIER_C_POPULATED!r}, got {status!r}"
        )
        return
    event_count = value.get("event_count")
    if not isinstance(event_count, int):
        errors.append(f"{skill_id}: tier_c_events.event_count must be an int")
        return
    event_types = value.get("event_types")
    if not isinstance(event_types, dict):
        errors.append(f"{skill_id}: tier_c_events.event_types must be an object")
        return
    if status == TIER_C_AWAITING:
        if event_count != 0 or event_types:
            errors.append(
                f"{skill_id}: tier_c_events shows '{TIER_C_AWAITING}' but has "
                "non-zero count or non-empty types"
            )
    else:
        if event_count <= 0:
            errors.append(
                f"{skill_id}: tier_c_events shows '{TIER_C_POPULATED}' but "
                "event_count is not positive"
            )
        if not event_types:
            errors.append(
                f"{skill_id}: tier_c_events shows '{TIER_C_POPULATED}' but "
                "event_types is empty"
            )


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    inventory_path = (
        Path(args.inventory_path)
        if args.inventory_path is not None
        else repo_root / "charness-artifacts" / "skill-t-mechanism" / "inventory.json"
    )
    errors: list[str] = []
    if not inventory_path.is_file():
        errors.append(f"inventory not found: {inventory_path}")
        report = {"valid": False, "errors": errors, "inventory_path": str(inventory_path)}
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1
    try:
        payload = json.loads(inventory_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"inventory is not valid JSON: {exc}")
        report = {"valid": False, "errors": errors, "inventory_path": str(inventory_path)}
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1
    if _check_top_shape(payload, errors):
        _check_rows(
            payload["skills"],
            _list_public_skill_ids(repo_root),
            errors,
        )
    valid = not errors
    report = {
        "valid": valid,
        "inventory_path": str(inventory_path.relative_to(repo_root) if str(inventory_path).startswith(str(repo_root)) else inventory_path),
        "errors": errors,
        "skill_count": len(payload.get("skills", [])) if isinstance(payload, dict) else 0,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
