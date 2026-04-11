#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.repo_file_listing import iter_matching_repo_files

PRESET_NAME_RE = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
REQUIRED_FIELDS = ("name", "description", "preset_kind", "install_scope")
ALLOWED_PRESET_KINDS = {"portable-defaults", "sample-vocabulary", "product-slice"}
ALLOWED_INSTALL_SCOPES = {"maintainer", "organization"}


class ValidationError(Exception):
    pass


def extract_frontmatter(contents: str) -> list[str]:
    lines = contents.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        raise ValidationError("missing YAML frontmatter delimited by ---")

    frontmatter: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            if not frontmatter:
                raise ValidationError("frontmatter is empty")
            return frontmatter
        frontmatter.append(line)
    raise ValidationError("frontmatter is missing closing --- delimiter")


def parse_frontmatter(path: Path) -> dict[str, str]:
    contents = path.read_text(encoding="utf-8")
    data: dict[str, str] = {}
    for index, raw in enumerate(extract_frontmatter(contents), start=2):
        if not raw.strip():
            continue
        if ":" not in raw:
            raise ValidationError(f"invalid YAML-like frontmatter line {index}: missing ':'")
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValidationError(f"invalid YAML-like frontmatter line {index}: empty key")
        if not value:
            raise ValidationError(f"invalid YAML-like frontmatter line {index}: empty value")
        data[key] = value
    for field in REQUIRED_FIELDS:
        if field not in data:
            raise ValidationError(f"missing field `{field}`")
    return data


def validate_quoted_string(field: str, value: str) -> None:
    if len(value) < 2 or not (value.startswith('"') and value.endswith('"')):
        raise ValidationError(
            f"`{field}` must be double-quoted so standard YAML parsers accept punctuation safely"
        )


def validate_preset(path: Path) -> None:
    import re

    data = parse_frontmatter(path)
    name = data["name"]
    if not re.fullmatch(PRESET_NAME_RE, name):
        raise ValidationError("`name` must be a lowercase slug")
    if name != path.stem:
        raise ValidationError(f"`name` must match file name `{path.stem}`")

    validate_quoted_string("description", data["description"])

    preset_kind = data["preset_kind"]
    if preset_kind not in ALLOWED_PRESET_KINDS:
        allowed = ", ".join(sorted(ALLOWED_PRESET_KINDS))
        raise ValidationError(f"`preset_kind` must be one of: {allowed}")

    install_scope = data["install_scope"]
    if install_scope not in ALLOWED_INSTALL_SCOPES:
        allowed = ", ".join(sorted(ALLOWED_INSTALL_SCOPES))
        raise ValidationError(f"`install_scope` must be one of: {allowed}")

    contents = path.read_text(encoding="utf-8")
    if "## Intended Use" not in contents:
        raise ValidationError("missing `## Intended Use` section")

    if install_scope == "organization" and preset_kind != "product-slice":
        raise ValidationError("organization-scope presets must use `preset_kind: product-slice`")
    if preset_kind == "product-slice" and "## Exposure Contract" not in contents:
        raise ValidationError("product-slice presets must include an `## Exposure Contract` section")


def iter_presets(root: Path) -> list[Path]:
    return sorted(
        path for path in iter_matching_repo_files(root, ("presets/*.md",)) if path.name != "README.md"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    preset_paths = iter_presets(root)
    if not preset_paths:
        print("No presets found.")
        return 0

    for path in preset_paths:
        try:
            validate_preset(path)
        except ValidationError as exc:
            raise ValidationError(f"{path}: {exc}") from exc

    print(f"Validated {len(preset_paths)} preset file(s).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
