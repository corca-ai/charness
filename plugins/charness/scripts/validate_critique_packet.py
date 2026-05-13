#!/usr/bin/env python3
"""Validate that a critique prepare packet matches `charness.critique_prepare_packet.v1`.

Usage:

    python3 scripts/validate_critique_packet.py path/to/<slug>-packet.json

Exits 0 when the envelope matches the schema; non-zero with one error
message per line otherwise. The validator owns shape only — section
content correctness stays the producer's responsibility.

Schema lives in `skills/public/critique/references/prepare-packet.md`.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

PACKET_KIND = "charness.critique_prepare_packet"
PACKET_VERSION = 1
TOP_KEYS = {
    "kind",
    "version",
    "repo",
    "generated_at",
    "prepared_for",
    "adapter_path",
    "sections",
    "section_count",
    "ok",
}
SECTION_KEYS = {"id", "title", "content_kind", "producer", "content", "ok", "errors"}
VALID_CONTENT_KINDS = {"static", "script"}


def _validate_top_level(payload: dict, errors: list[str]) -> None:
    missing = TOP_KEYS - set(payload.keys())
    if missing:
        errors.append(f"top-level missing keys: {sorted(missing)}")
    if payload.get("kind") != PACKET_KIND:
        errors.append(f"kind must be {PACKET_KIND!r}, got {payload.get('kind')!r}")
    if payload.get("version") != PACKET_VERSION:
        errors.append(f"version must be {PACKET_VERSION}, got {payload.get('version')!r}")
    repo = payload.get("repo")
    if not isinstance(repo, str) or not repo:
        errors.append("repo must be a non-empty string")
    generated_at = payload.get("generated_at")
    if not isinstance(generated_at, str) or not generated_at:
        errors.append("generated_at must be a non-empty string")


def _validate_section_shape(
    section: object, *, prefix: str, seen_ids: set[str], errors: list[str]
) -> None:
    if not isinstance(section, dict):
        errors.append(f"{prefix} must be an object")
        return
    section_missing = SECTION_KEYS - set(section.keys())
    if section_missing:
        errors.append(f"{prefix} missing keys: {sorted(section_missing)}")
    section_id = section.get("id")
    if not isinstance(section_id, str) or not section_id:
        errors.append(f"{prefix}.id must be a non-empty string")
    elif section_id in seen_ids:
        errors.append(f"{prefix}.id duplicates earlier section `{section_id}`")
    else:
        seen_ids.add(section_id)
    kind = section.get("content_kind")
    if kind not in VALID_CONTENT_KINDS:
        errors.append(
            f"{prefix}.content_kind must be one of: {sorted(VALID_CONTENT_KINDS)}; got {kind!r}"
        )
    if not isinstance(section.get("content"), str):
        errors.append(f"{prefix}.content must be a string")
    if not isinstance(section.get("ok"), bool):
        errors.append(f"{prefix}.ok must be a boolean")
    if not isinstance(section.get("errors"), list):
        errors.append(f"{prefix}.errors must be a list")


def _validate_section_aggregates(
    payload: dict, sections: list, errors: list[str]
) -> None:
    expected_count = len(sections)
    actual_count = payload.get("section_count")
    if actual_count != expected_count:
        errors.append(
            f"section_count must equal len(sections) ({expected_count}), got {actual_count!r}"
        )
    expected_ok = all(
        isinstance(section, dict) and section.get("ok") is True for section in sections
    ) if sections else True
    actual_ok = payload.get("ok")
    if not isinstance(actual_ok, bool):
        errors.append(f"ok must be a boolean, got {actual_ok!r}")
    elif actual_ok != expected_ok:
        errors.append(
            f"ok must equal all-sections-ok ({expected_ok}), got {actual_ok}"
        )


def validate_packet(payload: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["packet must be a JSON object"]
    _validate_top_level(payload, errors)
    sections = payload.get("sections")
    if not isinstance(sections, list):
        errors.append("sections must be a list")
        return errors
    seen_ids: set[str] = set()
    for index, section in enumerate(sections):
        _validate_section_shape(section, prefix=f"sections[{index}]",
                                seen_ids=seen_ids, errors=errors)
    _validate_section_aggregates(payload, sections, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet_path", type=Path,
                        help="Path to the JSON packet emitted by prepare_packet.py")
    args = parser.parse_args()
    if not args.packet_path.is_file():
        print(f"packet not found: {args.packet_path}")
        return 1
    try:
        payload = json.loads(args.packet_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"packet is not valid JSON: {exc}")
        return 1
    errors = validate_packet(payload)
    if errors:
        for err in errors:
            print(err)
        return 1
    print(f"OK ({payload['section_count']} section(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
