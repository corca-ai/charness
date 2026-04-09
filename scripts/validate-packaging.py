#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import jsonschema

SLUG_RE = re.compile(r"^[a-z0-9]+(?:[.-][a-z0-9]+)*$")
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$")
PACKAGING_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "packaging" / "plugin.schema.json"


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


def validate_version(value: object, field: str) -> str:
    value = validate_string(value, field)
    if not VERSION_RE.fullmatch(value):
        raise ValidationError(f"`{field}` must be a semver-like string")
    return value


def validate_relative_path(value: object, field: str) -> str:
    value = validate_string(value, field)
    if value.startswith("/") or value.startswith("../") or "/../" in value:
        raise ValidationError(f"`{field}` must stay within the repo")
    return value


def require_file(path: Path, field: str) -> None:
    if not path.is_file():
        raise ValidationError(f"`{field}` references missing file `{path}`")


def require_dir(path: Path, field: str) -> None:
    if not path.is_dir():
        raise ValidationError(f"`{field}` references missing directory `{path}`")


def load_packaging_schema() -> dict[str, object]:
    return json.loads(PACKAGING_SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_source_paths(root: Path, source: object) -> None:
    if not isinstance(source, dict):
        raise ValidationError("`source` must be an object")

    file_fields = ("readme",)
    dir_fields = (
        "skills_dir",
        "public_skills_dir",
        "support_skills_dir",
        "profiles_dir",
        "presets_dir",
        "integrations_dir",
    )
    for field in file_fields:
        rel_path = validate_relative_path(source.get(field), f"source.{field}")
        require_file(root / rel_path, f"source.{field}")
    for field in dir_fields:
        rel_path = validate_relative_path(source.get(field), f"source.{field}")
        require_dir(root / rel_path, f"source.{field}")


def validate_codex(package_id: str, version: str, summary: str, data: object) -> None:
    if not isinstance(data, dict):
        raise ValidationError("`codex` must be an object")
    manifest_path = validate_string(data.get("manifest_path"), "codex.manifest_path")
    if manifest_path != ".codex-plugin/plugin.json":
        raise ValidationError("`codex.manifest_path` must be `.codex-plugin/plugin.json`")

    manifest = data.get("manifest")
    if not isinstance(manifest, dict):
        raise ValidationError("`codex.manifest` must be an object")
    if validate_slug(manifest.get("name"), "codex.manifest.name") != package_id:
        raise ValidationError("`codex.manifest.name` must match `package_id`")
    if validate_version(manifest.get("version"), "codex.manifest.version") != version:
        raise ValidationError("`codex.manifest.version` must match top-level `version`")
    if validate_string(manifest.get("description"), "codex.manifest.description") != summary:
        raise ValidationError("`codex.manifest.description` must match top-level `summary`")
    if validate_string(manifest.get("skills"), "codex.manifest.skills") != "./skills/":
        raise ValidationError("`codex.manifest.skills` must be `./skills/`")

    marketplace = data.get("repo_marketplace")
    if not isinstance(marketplace, dict):
        raise ValidationError("`codex.repo_marketplace` must be an object")
    if validate_string(marketplace.get("path"), "codex.repo_marketplace.path") != ".agents/plugins/marketplace.json":
        raise ValidationError(
            "`codex.repo_marketplace.path` must be `.agents/plugins/marketplace.json`"
        )
    default_source_path = validate_string(
        marketplace.get("default_source_path"), "codex.repo_marketplace.default_source_path"
    )
    if default_source_path != f"./plugins/{package_id}":
        raise ValidationError(
            "`codex.repo_marketplace.default_source_path` must point at "
            f"`./plugins/{package_id}`"
        )
    validate_string(marketplace.get("display_name"), "codex.repo_marketplace.display_name")
    validate_string(marketplace.get("category"), "codex.repo_marketplace.category")


def validate_claude(package_id: str, version: str, summary: str, repository: str, data: object) -> None:
    if not isinstance(data, dict):
        raise ValidationError("`claude` must be an object")
    manifest_path = validate_string(data.get("manifest_path"), "claude.manifest_path")
    if manifest_path != ".claude-plugin/plugin.json":
        raise ValidationError("`claude.manifest_path` must be `.claude-plugin/plugin.json`")

    manifest = data.get("manifest")
    if not isinstance(manifest, dict):
        raise ValidationError("`claude.manifest` must be an object")
    if validate_slug(manifest.get("name"), "claude.manifest.name") != package_id:
        raise ValidationError("`claude.manifest.name` must match `package_id`")
    if validate_version(manifest.get("version"), "claude.manifest.version") != version:
        raise ValidationError("`claude.manifest.version` must match top-level `version`")
    if validate_string(manifest.get("description"), "claude.manifest.description") != summary:
        raise ValidationError("`claude.manifest.description` must match top-level `summary`")
    if validate_string(manifest.get("repository"), "claude.manifest.repository") != repository:
        raise ValidationError("`claude.manifest.repository` must match top-level `repository`")


def validate_packaging_manifest(path: Path, root: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValidationError("packaging manifest must be a JSON object")
    jsonschema.validate(data, load_packaging_schema())

    if validate_string(data.get("schema_version"), "schema_version") != "1":
        raise ValidationError("`schema_version` must be `1`")
    package_id = validate_slug(data.get("package_id"), "package_id")
    if package_id != path.stem:
        raise ValidationError(f"`package_id` must match filename `{path.stem}`")
    validate_string(data.get("display_name"), "display_name")
    version = validate_version(data.get("version"), "version")
    summary = validate_string(data.get("summary"), "summary")

    author = data.get("author")
    if not isinstance(author, dict):
        raise ValidationError("`author` must be an object")
    validate_string(author.get("name"), "author.name")
    if "url" in author:
        validate_string(author.get("url"), "author.url")

    homepage = validate_string(data.get("homepage"), "homepage")
    repository = validate_string(data.get("repository"), "repository")
    if homepage != repository:
        raise ValidationError("`homepage` should match `repository` until a separate package homepage exists")

    validate_source_paths(root, data.get("source"))
    validate_codex(package_id, version, summary, data.get("codex"))
    validate_claude(package_id, version, summary, repository, data.get("claude"))


def iter_packaging_files(root: Path) -> list[Path]:
    packaging_dir = root / "packaging"
    return sorted(
        path
        for path in packaging_dir.glob("*.json")
        if path.name != "plugin.schema.json"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    files = iter_packaging_files(root)
    if not files:
        print("No packaging manifests found.")
        return 0

    for path in files:
        try:
            validate_packaging_manifest(path, root)
        except (ValidationError, json.JSONDecodeError) as exc:
            raise ValidationError(f"{path}: {exc}") from exc

    print(f"Validated {len(files)} packaging manifest(s).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
