#!/usr/bin/env python3
"""Validate the quality reference index and planner catalog stay aligned."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
QUALITY_SKILL_DIR = Path("skills/public/quality")
INDEX_PATH = QUALITY_SKILL_DIR / "references" / "index.md"
CATALOG_PATH = QUALITY_SKILL_DIR / "references" / "catalog.yaml"
INDEX_SECTION_ROLES = {
    "Required And Scope Primers": {"required-primer", "scope-primer"},
    "On-Demand Review Detail": {"on-demand"},
}
KNOWN_ROLES = {"required-primer", "scope-primer", "on-demand"}
REQUIRED_GATE_FIELDS = ("id", "command", "purpose", "trust_model", "cost_tier", "parallel_group")
REFERENCE_BULLET_RE = re.compile(r"^- `(?P<path>references/[^`]+\.md)`")

_adapter_lib = import_repo_module(__file__, "scripts.adapter_lib")
load_yaml_file = _adapter_lib.load_yaml_file


class ValidationError(Exception):
    pass


def _index_catalog_roles(index_text: str) -> dict[str, set[str]]:
    section: str | None = None
    paths: dict[str, set[str]] = {}
    for line in index_text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        if section not in INDEX_SECTION_ROLES:
            continue
        match = REFERENCE_BULLET_RE.match(line)
        if match:
            paths[match.group("path")] = set(INDEX_SECTION_ROLES[section])
    return paths


def _catalog_reference_roles(catalog: dict[str, Any]) -> dict[str, str]:
    references = catalog.get("references")
    if not isinstance(references, list):
        raise ValidationError(f"{CATALOG_PATH}: `references` must be a list")
    paths: dict[str, str] = {}
    for index, ref in enumerate(references, start=1):
        if not isinstance(ref, dict):
            raise ValidationError(f"{CATALOG_PATH}: reference #{index} must be a mapping")
        path = ref.get("path")
        role = ref.get("role")
        if not isinstance(path, str) or not path.endswith(".md"):
            raise ValidationError(f"{CATALOG_PATH}: reference #{index} needs a markdown `path`")
        if role not in KNOWN_ROLES:
            raise ValidationError(f"{CATALOG_PATH}: {path} has unknown role `{role}`")
        if role in {"required-primer", "scope-primer"} and not ref.get("why"):
            raise ValidationError(f"{CATALOG_PATH}: {path} needs `why`")
        if role == "on-demand" and not ref.get("trigger"):
            raise ValidationError(f"{CATALOG_PATH}: {path} needs `trigger`")
        paths[path] = role
    return paths


def _validate_gate_packets(catalog: dict[str, Any]) -> None:
    gates = catalog.get("gates")
    if not isinstance(gates, list):
        raise ValidationError(f"{CATALOG_PATH}: `gates` must be a list")
    for index, gate in enumerate(gates, start=1):
        if not isinstance(gate, dict):
            raise ValidationError(f"{CATALOG_PATH}: gate #{index} must be a mapping")
        for field in REQUIRED_GATE_FIELDS:
            if not gate.get(field):
                raise ValidationError(f"{CATALOG_PATH}: gate #{index} needs `{field}`")


def validate_quality_reference_catalog(repo_root: Path) -> None:
    skill_dir = repo_root / QUALITY_SKILL_DIR
    index_path = repo_root / INDEX_PATH
    catalog_path = repo_root / CATALOG_PATH
    if not index_path.is_file():
        raise ValidationError(f"{INDEX_PATH}: missing quality reference index")
    if not catalog_path.is_file():
        raise ValidationError(f"{CATALOG_PATH}: missing quality reference catalog")

    index_roles = _index_catalog_roles(index_path.read_text(encoding="utf-8"))
    catalog = load_yaml_file(catalog_path)
    catalog_roles = _catalog_reference_roles(catalog)
    _validate_gate_packets(catalog)

    index_paths = set(index_roles)
    catalog_paths = set(catalog_roles)
    missing_from_catalog = sorted(index_paths - catalog_paths)
    missing_from_index = sorted(catalog_paths - index_paths)
    if missing_from_catalog:
        formatted = ", ".join(f"`{path}`" for path in missing_from_catalog)
        raise ValidationError(f"{CATALOG_PATH}: index reference(s) missing from catalog: {formatted}")
    if missing_from_index:
        formatted = ", ".join(f"`{path}`" for path in missing_from_index)
        raise ValidationError(f"{INDEX_PATH}: catalog reference(s) missing from index sections: {formatted}")
    role_mismatches = sorted(
        (path, catalog_roles[path], sorted(index_roles[path]))
        for path in index_paths & catalog_paths
        if catalog_roles[path] not in index_roles[path]
    )
    if role_mismatches:
        formatted = ", ".join(
            f"`{path}` catalog role `{role}` not in index role(s) {expected}"
            for path, role, expected in role_mismatches
        )
        raise ValidationError(f"{CATALOG_PATH}: index/catalog role mismatch: {formatted}")

    for rel_path in sorted(catalog_paths | index_paths):
        if not (skill_dir / rel_path).is_file():
            raise ValidationError(f"{QUALITY_SKILL_DIR}: missing referenced file `{rel_path}`")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    validate_quality_reference_catalog(args.repo_root.resolve())
    print("Validated quality reference catalog/index parity.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
