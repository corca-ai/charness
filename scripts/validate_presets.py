#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

_scripts_repo_file_listing_module = import_repo_module(__file__, "scripts.core.repo_file_listing")
iter_matching_repo_files = _scripts_repo_file_listing_module.iter_matching_repo_files

PRESET_NAME_RE = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
REQUIRED_FIELDS = ("name", "description", "preset_kind", "install_scope")
ALLOWED_PRESET_KINDS = {"portable-defaults", "sample-vocabulary", "product-slice"}
ALLOWED_INSTALL_SCOPES = {"maintainer", "organization"}


class ValidationError(Exception):
    pass


def extract_frontmatter(contents: str) -> list[str]:
    lines = contents.splitlines()
    if len(lines) < 3 or lines[0] != "---":
        raise ValidationError("missing YAML frontmatter delimited by ---")

    frontmatter: list[str] = []
    for line in lines[1:]:
        if line == "---":
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
        if raw[0].isspace():
            continue
        if ":" not in raw:
            raise ValidationError(f"invalid YAML-like frontmatter line {index}: missing ':'")
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValidationError(f"invalid YAML-like frontmatter line {index}: empty key")
        if not value and key != "reconciliation":
            raise ValidationError(f"invalid YAML-like frontmatter line {index}: empty value")
        data[key] = value
    for field in REQUIRED_FIELDS:
        if field not in data:
            raise ValidationError(f"missing field `{field}`")
    return data


def parse_frontmatter_data(path: Path) -> dict[str, object]:
    """Return the same strict-delimited front matter as structured YAML."""
    from scripts.adapter_lib import load_yaml

    try:
        data = load_yaml("\n".join(extract_frontmatter(path.read_text(encoding="utf-8"))))
    except (OSError, ValueError, TypeError) as exc:
        raise ValidationError(f"invalid YAML frontmatter: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError("frontmatter must be a mapping")
    return data


def validate_reconciliation_frontmatter(data: dict[str, object]) -> None:
    """Accept only the lifecycle's typed, nested prescription vocabulary."""
    if "reconciliation" not in data:
        return
    reconciliation = data.get("reconciliation")
    required = (
        reconciliation.get("required_adapter_commands")
        if isinstance(reconciliation, dict)
        else None
    )
    if (
        not isinstance(required, list)
        or not required
        or not all(isinstance(item, str) and item.strip() for item in required)
    ):
        raise ValidationError(
            "reconciliation.required_adapter_commands must be a non-empty string list"
        )


def validate_quoted_string(field: str, value: str) -> None:
    if len(value) < 2 or not (value.startswith('"') and value.endswith('"')):
        raise ValidationError(
            f"`{field}` must be double-quoted so standard YAML parsers accept punctuation safely"
        )


def validate_preset(path: Path) -> dict[str, object]:
    data = parse_frontmatter(path)
    structured_data = parse_frontmatter_data(path)
    name = data["name"]
    if not re.fullmatch(PRESET_NAME_RE, name):
        raise ValidationError("`name` must be a lowercase slug")
    if name != path.stem:
        raise ValidationError(f"`name` must match file name `{path.stem}`")

    validate_quoted_string("description", data["description"])
    validate_reconciliation_frontmatter(structured_data)

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
        raise ValidationError(
            "product-slice presets must include an `## Exposure Contract` section"
        )
    return structured_data


def iter_presets(root: Path, *, require_git: bool = False) -> list[Path]:
    return sorted(
        path
        for path in iter_matching_repo_files(root, ("presets/*.md",), require_git=require_git)
        if path.name != "README.md"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--require-git-file-listing", action="store_true")
    args = parser.parse_args()

    root = args.repo_root.resolve()
    preset_paths = iter_presets(root, require_git=args.require_git_file_listing)
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
