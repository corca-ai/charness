#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--registry-file", action="append", default=[])
    parser.add_argument("--archetype-contract-file", action="append", default=[])
    parser.add_argument("--flat-help-threshold", type=int, default=10)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_visible_repo_files(repo_root: Path) -> set[Path] | None:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=repo_root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    return {repo_root / rel.decode("utf-8") for rel in result.stdout.split(b"\0") if rel}


def _default_paths(repo_root: Path, patterns: list[str]) -> list[Path]:
    visible_files = _git_visible_repo_files(repo_root)
    seen: set[Path] = set()
    found: list[Path] = []
    for pattern in patterns:
        for path in sorted(repo_root.glob(pattern)):
            if path.is_file() and path not in seen and (visible_files is None or path in visible_files):
                seen.add(path)
                found.append(path)
    return found


def _schema_namespace(schema_id: str) -> str | None:
    parts = schema_id.split(".")
    if len(parts) < 2:
        return None
    token = parts[1].split("_", 1)[0]
    return token or None


def _fixture_namespace(path: str) -> str | None:
    match = re.match(r"([a-z0-9]+)[-_]", Path(path).name)
    return match.group(1) if match else None


def _subcommand_namespace(command: str) -> str | None:
    pieces = [piece for piece in command.strip().split() if not piece.startswith("--")]
    if not pieces:
        return None
    return pieces[-1]


def _inventory_registry(repo_root: Path, path: Path, *, threshold: int) -> dict[str, object]:
    payload = _load_json(path)
    commands = payload.get("commands", []) if isinstance(payload, dict) else []
    command_entries = [entry for entry in commands if isinstance(entry, dict)]
    command_count = len(command_entries)
    groups_present = any(isinstance(entry.get("group"), str) and entry.get("group") for entry in command_entries)
    namespaces = sorted(
        {
            path_parts[0]
            for entry in command_entries
            for path_parts in [entry.get("path")]
            if isinstance(path_parts, list) and path_parts
        }
    )
    findings: list[dict[str, object]] = []
    if command_count > threshold and not groups_present:
        findings.append(
            {
                "type": "flat_help_without_grouping",
                "path": str(path.relative_to(repo_root)),
                "command_count": command_count,
                "flat_help_threshold": threshold,
                "suggestion": "Add a grouping field to the command registry and render grouped help output so first-time readers can pick a purpose path.",
            }
        )
    return {
        "path": str(path.relative_to(repo_root)),
        "command_count": command_count,
        "groups_present": groups_present,
        "namespaces": namespaces,
        "findings": findings,
    }


def _inventory_archetype_contract(repo_root: Path, path: Path) -> dict[str, object]:
    payload = _load_json(path)
    entries = payload.get("entries", []) if isinstance(payload, dict) else []
    findings: list[dict[str, object]] = []
    rendered_entries: list[dict[str, object]] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        subcommand = str(entry.get("subcommand", "")).strip()
        schema_ids = [schema for schema in entry.get("accepted_schema_ids", []) if isinstance(schema, str)]
        fixtures = [fixture for fixture in entry.get("example_fixtures", []) if isinstance(fixture, str)]
        schema_namespaces = sorted({namespace for schema in schema_ids if (namespace := _schema_namespace(schema))})
        subcommand_namespace = _subcommand_namespace(subcommand)
        fixture_namespaces = sorted({namespace for fixture in fixtures if (namespace := _fixture_namespace(fixture))})
        rendered_entries.append(
            {
                "subcommand": subcommand,
                "accepted_schema_ids": schema_ids,
                "schema_namespaces": schema_namespaces,
                "example_fixtures": fixtures,
                "fixture_namespaces": fixture_namespaces,
            }
        )
        if len(schema_namespaces) > 1:
            findings.append(
                {
                    "type": "cross_archetype_schema_overlap",
                    "path": str(path.relative_to(repo_root)),
                    "entry_index": index,
                    "subcommand": subcommand,
                    "schema_namespaces": schema_namespaces,
                    "suggestion": "Split the command by archetype or re-examine whether the archetypes are truly separate user-facing concepts.",
                }
            )
        if subcommand_namespace and schema_namespaces and subcommand_namespace not in schema_namespaces:
            findings.append(
                {
                    "type": "subcommand_schema_namespace_mismatch",
                    "path": str(path.relative_to(repo_root)),
                    "entry_index": index,
                    "subcommand": subcommand,
                    "subcommand_namespace": subcommand_namespace,
                    "schema_namespaces": schema_namespaces,
                }
            )
        if schema_namespaces:
            for fixture in fixtures:
                fixture_namespace = _fixture_namespace(fixture)
                if fixture_namespace and fixture_namespace not in schema_namespaces:
                    findings.append(
                        {
                            "type": "fixture_schema_namespace_mismatch",
                            "path": str(path.relative_to(repo_root)),
                            "entry_index": index,
                            "subcommand": subcommand,
                            "fixture": fixture,
                            "fixture_namespace": fixture_namespace,
                            "schema_namespaces": schema_namespaces,
                        }
                    )
    return {
        "path": str(path.relative_to(repo_root)),
        "entries": rendered_entries,
        "findings": findings,
    }


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    registry_paths = (
        [(repo_root / path).resolve() for path in args.registry_file]
        if args.registry_file
        else _default_paths(repo_root, ["**/command-registry.json", "**/*command-registry*.json"])
    )
    archetype_contract_paths = (
        [(repo_root / path).resolve() for path in args.archetype_contract_file]
        if args.archetype_contract_file
        else _default_paths(repo_root, ["**/command-archetypes.json", "**/*archetype-contract*.json"])
    )

    registries = [
        _inventory_registry(repo_root, path, threshold=args.flat_help_threshold)
        for path in registry_paths
    ]
    archetype_contracts = [
        _inventory_archetype_contract(repo_root, path) for path in archetype_contract_paths
    ]
    findings = [
        finding
        for section in [*registries, *archetype_contracts]
        for finding in section["findings"]
    ]
    payload = {
        "repo_root": str(repo_root),
        "flat_help_threshold": args.flat_help_threshold,
        "registries": registries,
        "archetype_contracts": archetype_contracts,
        "findings": findings,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for finding in findings:
            print(f"{finding['type']}: {finding['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
