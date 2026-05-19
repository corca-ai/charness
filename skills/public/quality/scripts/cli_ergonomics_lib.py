from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def schema_namespace(schema_id: str) -> str | None:
    parts = schema_id.split(".")
    if len(parts) < 2:
        return None
    token = parts[1].split("_", 1)[0]
    return token or None


def fixture_namespace(path: str) -> str | None:
    match = re.match(r"([a-z0-9]+)[-_]", Path(path).name)
    return match.group(1) if match else None


def subcommand_namespace(command: str) -> str | None:
    pieces = [piece for piece in command.strip().split() if not piece.startswith("--")]
    if not pieces:
        return None
    return pieces[-1]


def inventory_registry(repo_root: Path, path: Path, *, threshold: int) -> dict[str, object]:
    payload = load_json(path)
    commands = payload.get("commands", []) if isinstance(payload, dict) else []
    command_entries = [entry for entry in commands if isinstance(entry, dict)]
    command_count = len(command_entries)
    groups_present = any(isinstance(entry.get("group"), str) and entry.get("group") for entry in command_entries)
    namespaces = sorted({path_parts[0] for entry in command_entries for path_parts in [entry.get("path")] if isinstance(path_parts, list) and path_parts})
    findings: list[dict[str, object]] = []
    if command_count > threshold and not groups_present:
        findings.append({
            "type": "flat_help_without_grouping",
            "path": str(path.relative_to(repo_root)),
            "command_count": command_count,
            "flat_help_threshold": threshold,
            "suggestion": "Add a grouping field to the command registry and render grouped help output so first-time readers can pick a purpose path.",
        })
    return {"path": str(path.relative_to(repo_root)), "command_count": command_count, "groups_present": groups_present, "namespaces": namespaces, "findings": findings}


def _archetype_entry(entry: dict, *, path: Path, repo_root: Path, index: int, findings: list[dict[str, object]]) -> dict[str, object]:
    subcommand = str(entry.get("subcommand", "")).strip()
    schema_ids = [schema for schema in entry.get("accepted_schema_ids", []) if isinstance(schema, str)]
    fixtures = [fixture for fixture in entry.get("example_fixtures", []) if isinstance(fixture, str)]
    schema_namespaces = sorted({namespace for schema in schema_ids if (namespace := schema_namespace(schema))})
    sub_ns = subcommand_namespace(subcommand)
    fixture_namespaces = sorted({namespace for fixture in fixtures if (namespace := fixture_namespace(fixture))})
    rel = str(path.relative_to(repo_root))
    if len(schema_namespaces) > 1:
        findings.append({"type": "cross_archetype_schema_overlap", "path": rel, "entry_index": index, "subcommand": subcommand, "schema_namespaces": schema_namespaces, "suggestion": "Split the command by archetype or re-examine whether the archetypes are truly separate user-facing concepts."})
    if sub_ns and schema_namespaces and sub_ns not in schema_namespaces:
        findings.append({"type": "subcommand_schema_namespace_mismatch", "path": rel, "entry_index": index, "subcommand": subcommand, "subcommand_namespace": sub_ns, "schema_namespaces": schema_namespaces})
    if schema_namespaces:
        for fixture in fixtures:
            fns = fixture_namespace(fixture)
            if fns and fns not in schema_namespaces:
                findings.append({"type": "fixture_schema_namespace_mismatch", "path": rel, "entry_index": index, "subcommand": subcommand, "fixture": fixture, "fixture_namespace": fns, "schema_namespaces": schema_namespaces})
    return {"subcommand": subcommand, "accepted_schema_ids": schema_ids, "schema_namespaces": schema_namespaces, "example_fixtures": fixtures, "fixture_namespaces": fixture_namespaces}


def inventory_archetype_contract(repo_root: Path, path: Path) -> dict[str, object]:
    payload = load_json(path)
    entries = payload.get("entries", []) if isinstance(payload, dict) else []
    findings: list[dict[str, object]] = []
    rendered_entries: list[dict[str, object]] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        rendered_entries.append(_archetype_entry(entry, path=path, repo_root=repo_root, index=index, findings=findings))
    return {"path": str(path.relative_to(repo_root)), "entries": rendered_entries, "findings": findings}


def scope_status(scanned: int, requested: bool) -> dict[str, str]:
    if scanned > 0:
        return {"status": "clean", "scope_classification": "scanned"}
    if requested:
        return {
            "status": "clean",
            "scope_classification": "advisory_only_requested_scope_empty",
            "reason": "Explicit --registry-file or --archetype-contract-file arguments yielded no readable files.",
        }
    return {
        "status": "unconfigured",
        "scope_classification": "advisory_only_no_cli_surface",
        "reason": "No CLI command-registry.json or command-archetypes.json files were discovered. Provide --registry-file/--archetype-contract-file or commit a registry under repo-visible paths.",
    }
