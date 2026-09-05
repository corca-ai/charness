#!/usr/bin/env python3
"""Refuse generic kind/mode/type/strategy/profile/target enums that omit x-axis.

A catch-all `kind` or `mode` is the mixed-axis hatch: purpose, method, and
absence land in one list. The field name is the axis when it is already
`delivery_kind` or `access_modes`. A generic name must declare `x-axis` from
the closed set below. A new axis is a new field, not a new enum value.
"""

from __future__ import annotations

import argparse
import json
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

from scripts.runtime_bootstrap import repo_root_from_script  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

GENERIC_ENUM_FIELDS = frozenset({"kind", "mode", "type", "strategy", "profile", "target"})
AXES = frozenset(
    {
        "packaging",
        "install-method",
        "lock-entry-class",
        "purpose",
        "method",
        "evidence-source",
        "trigger",
        "objective",
        "selection-policy",
    }
)
SKIP_DIR_NAMES = frozenset(
    {".git", "plugins", "charness-artifacts", "node_modules", "__pycache__", "mutants"}
)


def schema_paths(repo_root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in repo_root.rglob("*.schema.json"):
        if SKIP_DIR_NAMES.intersection(path.parts):
            continue
        paths.append(path)
    return sorted(paths)


def _enum_values(node: dict) -> list[object] | None:
    values = node.get("enum")
    if isinstance(values, list) and len(values) >= 2:
        return values
    return None


def _resolve_local_ref(document: dict, ref: str) -> object | None:
    if not isinstance(ref, str) or not ref.startswith("#/"):
        return None
    node: object = document
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def _walk_into(
    node: object,
    path: str,
    *,
    field_name: str | None,
    findings: list[str],
    document: dict,
    visiting: set[tuple[str, str | None]],
) -> None:
    _walk_schema(
        node,
        path,
        field_name=field_name,
        findings=findings,
        document=document,
        visiting=visiting,
    )


def _follow_ref(
    node: dict,
    path: str,
    *,
    field_name: str | None,
    findings: list[str],
    document: dict,
    visiting: set[tuple[str, str | None]],
) -> None:
    ref = node.get("$ref")
    if not isinstance(ref, str) or not ref.startswith("#/"):
        return
    visit_key = (ref, field_name)
    if visit_key in visiting:
        return
    visiting.add(visit_key)
    resolved = _resolve_local_ref(document, ref)
    if resolved is not None:
        _walk_into(
            resolved,
            f"{path}($ref)",
            field_name=field_name,
            findings=findings,
            document=document,
            visiting=visiting,
        )
    visiting.discard(visit_key)


def _record_generic_enum(node: dict, path: str, field_name: str | None, findings: list[str]) -> None:
    values = _enum_values(node)
    if field_name not in GENERIC_ENUM_FIELDS or values is None:
        return
    if node.get("x-axis") not in AXES:
        findings.append(
            f"{path}: generic `{field_name}` enum {values!r} needs "
            f"`x-axis` from {sorted(AXES)}"
        )


def _walk_children(
    node: dict,
    path: str,
    *,
    field_name: str | None,
    findings: list[str],
    document: dict,
    visiting: set[tuple[str, str | None]],
) -> None:
    properties = node.get("properties")
    if isinstance(properties, dict):
        for name, schema in properties.items():
            _walk_into(
                schema,
                f"{path}.properties.{name}",
                field_name=str(name),
                findings=findings,
                document=document,
                visiting=visiting,
            )
    for key in ("definitions", "$defs"):
        defs = node.get(key)
        if isinstance(defs, dict):
            for name, schema in defs.items():
                _walk_into(
                    schema,
                    f"{path}.{key}.{name}",
                    field_name=None,
                    findings=findings,
                    document=document,
                    visiting=visiting,
                )
    for key in ("items", "additionalProperties", "not"):
        if key in node:
            _walk_into(
                node[key],
                f"{path}.{key}",
                field_name=None,
                findings=findings,
                document=document,
                visiting=visiting,
            )
    for key in ("oneOf", "anyOf", "allOf"):
        if key in node:
            _walk_into(
                node[key],
                f"{path}.{key}",
                field_name=field_name,
                findings=findings,
                document=document,
                visiting=visiting,
            )


def _walk_schema(
    node: object,
    path: str,
    *,
    field_name: str | None,
    findings: list[str],
    document: dict,
    visiting: set[tuple[str, str | None]],
) -> None:
    if isinstance(node, list):
        for index, item in enumerate(node):
            _walk_into(
                item,
                f"{path}[{index}]",
                field_name=field_name,
                findings=findings,
                document=document,
                visiting=visiting,
            )
        return
    if not isinstance(node, dict):
        return
    _follow_ref(
        node,
        path,
        field_name=field_name,
        findings=findings,
        document=document,
        visiting=visiting,
    )
    _record_generic_enum(node, path, field_name, findings)
    _walk_children(
        node,
        path,
        field_name=field_name,
        findings=findings,
        document=document,
        visiting=visiting,
    )


def findings_for(repo_root: Path) -> list[str]:
    findings: list[str] = []
    for path in schema_paths(repo_root):
        document = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            continue
        relative = path.relative_to(repo_root).as_posix()
        _walk_schema(
            document,
            relative,
            field_name=None,
            findings=findings,
            document=document,
            visiting=set(),
        )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="Repo root to scan.")
    args = parser.parse_args()
    findings = findings_for(args.repo_root.resolve())
    if findings:
        for finding in findings:
            print(finding, file=sys.stderr)
        return 1
    print("All generic schema enums declare x-axis.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
