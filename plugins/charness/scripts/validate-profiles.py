#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import jsonschema
from jsonschema import ValidationError as JsonSchemaValidationError

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.eval_registry import scenario_ids

SLUG_RE = re.compile(r"^[a-z0-9]+(?:[.-][a-z0-9]+)*$")
PROFILE_SCHEMA_PATH = REPO_ROOT / "profiles" / "profile.schema.json"


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


def validate_unique_strings(
    value: object,
    field: str,
    *,
    require_non_empty: bool = False,
) -> list[str]:
    if not isinstance(value, list) or (require_non_empty and not value):
        qualifier = "a non-empty list" if require_non_empty else "a list"
        raise ValidationError(f"`{field}` must be {qualifier} of strings")
    items: list[str] = []
    seen: set[str] = set()
    for item in value:
        string_item = validate_string(item, field)
        if string_item in seen:
            raise ValidationError(f"`{field}` must not contain duplicates")
        seen.add(string_item)
        items.append(string_item)
    return items


def require_file(path: Path, field: str, value: str) -> None:
    if not path.exists():
        raise ValidationError(f"`{field}` references missing artifact `{value}`")


def load_profile_schema() -> dict[str, object]:
    return json.loads(PROFILE_SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_profile(path: Path, root: Path) -> None:
    profile_ids = {profile_path.stem for profile_path in iter_profile_files(root)}
    known_eval_scenarios = scenario_ids()
    public_skills_dir = root / "skills" / "public"
    support_skills_dir = root / "skills" / "support"
    presets_dir = root / "presets"
    integrations_dir = root / "integrations" / "tools"

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValidationError("profile must be a JSON object")
    jsonschema.validate(data, load_profile_schema())

    validate_string(data.get("schema_version"), "schema_version")
    profile_id = validate_slug(data.get("profile_id"), "profile_id")
    validate_string(data.get("display_name"), "display_name")
    validate_string(data.get("purpose"), "purpose")
    if profile_id != path.stem:
        raise ValidationError(f"`profile_id` must match filename `{path.stem}`")

    extends = data.get("extends", [])
    if extends is not None:
        for base_profile in validate_unique_strings(extends, "extends"):
            base_profile = validate_slug(base_profile, "extends[]")
            if base_profile == profile_id:
                raise ValidationError("`extends[]` must not include the profile itself")
            if base_profile not in profile_ids:
                raise ValidationError(f"`extends[]` references missing artifact `{base_profile}`")

    bundles = data.get("bundles")
    if not isinstance(bundles, dict):
        raise ValidationError("`bundles` must be an object")

    public_skills = validate_unique_strings(
        bundles.get("public_skills"),
        "bundles.public_skills",
        require_non_empty=True,
    )
    for skill_id in public_skills:
        skill_id = validate_slug(skill_id, "bundles.public_skills[]")
        require_file(public_skills_dir / skill_id / "SKILL.md", "bundles.public_skills[]", skill_id)

    for field, base, suffix in (
        ("support_skills", support_skills_dir, "SKILL.md"),
        ("preset_ids", presets_dir, ".md"),
        ("integration_ids", integrations_dir, ".json"),
    ):
        items = bundles.get(field, [])
        if items is None:
            continue
        for item in validate_unique_strings(items, f"bundles.{field}"):
            item = validate_slug(item, f"bundles.{field}[]")
            target = base / item / suffix if suffix == "SKILL.md" else base / f"{item}{suffix}"
            require_file(target, f"bundles.{field}[]", item)

    activation = data.get("activation")
    if activation is not None:
        if not isinstance(activation, dict):
            raise ValidationError("`activation` must be an object")
        default = activation.get("default")
        if default is not None and not isinstance(default, bool):
            raise ValidationError("`activation.default` must be a boolean")
        for field in ("recommended_when", "avoid_when"):
            if field in activation:
                validate_string_list(activation[field], f"activation.{field}")

    validation = data.get("validation")
    if validation is not None:
        if not isinstance(validation, dict):
            raise ValidationError("`validation` must be an object")
        required_integrations = validation.get("required_integrations", [])
        if required_integrations is not None:
            for integration_id in validate_unique_strings(
                required_integrations,
                "validation.required_integrations",
            ):
                integration_id = validate_slug(integration_id, "validation.required_integrations[]")
                require_file(
                    integrations_dir / f"{integration_id}.json",
                    "validation.required_integrations[]",
                    integration_id,
                )
        smoke_scenarios = validation.get("smoke_scenarios", [])
        if smoke_scenarios is not None:
            for scenario_id in validate_unique_strings(
                smoke_scenarios,
                "validation.smoke_scenarios",
            ):
                validate_string(scenario_id, "validation.smoke_scenarios[]")
                if scenario_id not in known_eval_scenarios:
                    raise ValidationError(
                        f"`validation.smoke_scenarios[]` references unknown eval scenario `{scenario_id}`"
                    )

    notes = data.get("notes")
    if notes is not None:
        validate_string_list(notes, "notes")


def iter_profile_files(root: Path) -> list[Path]:
    profiles_dir = root / "profiles"
    return sorted(
        path for path in profiles_dir.glob("*.json") if path.name != "profile.schema.json"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    files = iter_profile_files(root)
    if not files:
        print("No profile instances found.")
        return 0

    for path in files:
        try:
            validate_profile(path, root)
        except (ValidationError, json.JSONDecodeError, JsonSchemaValidationError) as exc:
            raise ValidationError(f"{path}: {exc}") from exc

    print(f"Validated {len(files)} profile instances.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
