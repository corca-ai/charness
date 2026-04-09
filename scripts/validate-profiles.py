#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PROFILES_DIR = ROOT / "profiles"
PUBLIC_SKILLS_DIR = ROOT / "skills" / "public"
SUPPORT_SKILLS_DIR = ROOT / "skills" / "support"
PRESETS_DIR = ROOT / "presets"
INTEGRATIONS_DIR = ROOT / "integrations" / "tools"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:[.-][a-z0-9]+)*$")


class ValidationError(Exception):
    pass


def validate_slug(value: object, field: str) -> str:
    if not isinstance(value, str) or not SLUG_RE.fullmatch(value):
        raise ValidationError(f"`{field}` must be a slug string")
    return value


def validate_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"`{field}` must be a non-empty string")
    return value


def validate_string_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValidationError(f"`{field}` must be a non-empty list of strings")
    items: list[str] = []
    for item in value:
        items.append(validate_string(item, field))
    return items


def require_file(path: Path, field: str, value: str) -> None:
    if not path.exists():
        raise ValidationError(f"`{field}` references missing artifact `{value}`")


def validate_profile(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValidationError("profile must be a JSON object")

    validate_string(data.get("schema_version"), "schema_version")
    profile_id = validate_slug(data.get("profile_id"), "profile_id")
    validate_string(data.get("display_name"), "display_name")
    validate_string(data.get("purpose"), "purpose")
    if profile_id != path.stem:
        raise ValidationError(f"`profile_id` must match filename `{path.stem}`")

    bundles = data.get("bundles")
    if not isinstance(bundles, dict):
        raise ValidationError("`bundles` must be an object")

    public_skills = bundles.get("public_skills")
    if not isinstance(public_skills, list) or not public_skills:
        raise ValidationError("`bundles.public_skills` must be a non-empty list")
    for skill_id in public_skills:
        skill_id = validate_slug(skill_id, "bundles.public_skills[]")
        require_file(PUBLIC_SKILLS_DIR / skill_id / "SKILL.md", "bundles.public_skills[]", skill_id)

    for field, base, suffix in (
        ("support_skills", SUPPORT_SKILLS_DIR, "SKILL.md"),
        ("preset_ids", PRESETS_DIR, ".md"),
        ("integration_ids", INTEGRATIONS_DIR, ".json"),
    ):
        items = bundles.get(field, [])
        if items is None:
            continue
        if not isinstance(items, list):
            raise ValidationError(f"`bundles.{field}` must be a list")
        for item in items:
            item = validate_slug(item, f"bundles.{field}[]")
            target = base / item / suffix if suffix == "SKILL.md" else base / f"{item}{suffix}"
            require_file(target, f"bundles.{field}[]", item)

    activation = data.get("activation")
    if activation is not None:
        if not isinstance(activation, dict):
            raise ValidationError("`activation` must be an object")
        for field in ("recommended_when", "avoid_when"):
            if field in activation:
                validate_string_list(activation[field], f"activation.{field}")

    notes = data.get("notes")
    if notes is not None:
        validate_string_list(notes, "notes")


def iter_profile_files() -> list[Path]:
    return sorted(
        path
        for path in PROFILES_DIR.glob("*.json")
        if path.name != "profile.schema.json"
    )


def main() -> int:
    files = iter_profile_files()
    if not files:
        print("No profile instances found.")
        return 0

    for path in files:
        try:
            validate_profile(path)
        except (ValidationError, json.JSONDecodeError) as exc:
            raise ValidationError(f"{path}: {exc}") from exc

    print(f"Validated {len(files)} profile instances.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
