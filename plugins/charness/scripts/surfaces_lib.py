#!/usr/bin/env python3

from __future__ import annotations

import fnmatch
import json
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any

SURFACES_PATH = Path(".agents/surfaces.json")


class SurfaceError(Exception):
    pass


def normalize_repo_path(value: str) -> str:
    normalized = PurePosixPath(value).as_posix()
    if normalized.startswith("../") or normalized.startswith("/"):
        raise SurfaceError(f"surface path must stay within the repo: `{value}`")
    return normalized


def _require_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SurfaceError(f"`{field}` must be a non-empty string")
    return value


def _require_string_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list):
        raise SurfaceError(f"`{field}` must be a list")
    result: list[str] = []
    for index, item in enumerate(value):
        result.append(_require_string(item, f"{field}[{index}]"))
    return result


def _validate_generated_markdown_entry(entry: object, field: str) -> dict[str, str]:
    if not isinstance(entry, dict):
        raise SurfaceError(f"`{field}` must be an object")
    source_path = normalize_repo_path(_require_string(entry.get("source_path"), f"{field}.source_path"))
    derived_path = normalize_repo_path(_require_string(entry.get("derived_path"), f"{field}.derived_path"))
    generator = _require_string(entry.get("generator"), f"{field}.generator")
    sync_command = _require_string(entry.get("sync_command"), f"{field}.sync_command")
    return {
        "source_path": source_path,
        "derived_path": derived_path,
        "generator": generator,
        "sync_command": sync_command,
    }


def _validate_surface(surface: object, index: int) -> dict[str, Any]:
    field = f"surfaces[{index}]"
    if not isinstance(surface, dict):
        raise SurfaceError(f"`{field}` must be an object")
    surface_id = _require_string(surface.get("surface_id"), f"{field}.surface_id")
    description = _require_string(surface.get("description"), f"{field}.description")
    source_paths = [normalize_repo_path(path) for path in _require_string_list(surface.get("source_paths"), f"{field}.source_paths")]
    derived_paths = [normalize_repo_path(path) for path in _require_string_list(surface.get("derived_paths"), f"{field}.derived_paths")]
    sync_commands = _require_string_list(surface.get("sync_commands"), f"{field}.sync_commands")
    verify_commands = _require_string_list(surface.get("verify_commands"), f"{field}.verify_commands")
    notes = _require_string_list(surface.get("notes"), f"{field}.notes")
    generated_markdown_raw = surface.get("generated_markdown", [])
    if not isinstance(generated_markdown_raw, list):
        raise SurfaceError(f"`{field}.generated_markdown` must be a list")
    generated_markdown = [
        _validate_generated_markdown_entry(entry, f"{field}.generated_markdown[{item_index}]")
        for item_index, entry in enumerate(generated_markdown_raw)
    ]
    for entry in generated_markdown:
        if not path_matches_patterns(entry["source_path"], source_paths):
            raise SurfaceError(
                f"`{field}.generated_markdown` source `{entry['source_path']}` must also appear in `source_paths`"
            )
        if not path_matches_patterns(entry["derived_path"], derived_paths):
            raise SurfaceError(
                f"`{field}.generated_markdown` derived `{entry['derived_path']}` must also appear in `derived_paths`"
            )
    return {
        "surface_id": surface_id,
        "description": description,
        "source_paths": source_paths,
        "derived_paths": derived_paths,
        "sync_commands": sync_commands,
        "verify_commands": verify_commands,
        "notes": notes,
        "generated_markdown": generated_markdown,
    }


def load_surfaces(repo_root: Path, *, surfaces_path: Path = SURFACES_PATH, required: bool = True) -> dict[str, Any] | None:
    manifest_path = surfaces_path if surfaces_path.is_absolute() else repo_root / surfaces_path
    if not manifest_path.exists():
        if required:
            raise SurfaceError(f"missing surfaces manifest `{manifest_path}`")
        return None
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SurfaceError(f"invalid JSON in `{manifest_path}`: {exc}") from exc
    if not isinstance(raw, dict):
        raise SurfaceError("surfaces manifest must be a JSON object")
    version = raw.get("version")
    if version != 1:
        raise SurfaceError("surfaces manifest `version` must be 1")
    surfaces_raw = raw.get("surfaces")
    if not isinstance(surfaces_raw, list) or not surfaces_raw:
        raise SurfaceError("surfaces manifest `surfaces` must be a non-empty list")
    validated_surfaces: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, surface in enumerate(surfaces_raw):
        validated = _validate_surface(surface, index)
        if validated["surface_id"] in seen_ids:
            raise SurfaceError(f"duplicate surface id `{validated['surface_id']}`")
        seen_ids.add(validated["surface_id"])
        validated_surfaces.append(validated)
    return {"version": version, "surfaces": validated_surfaces, "path": str(manifest_path)}


def dedupe_preserve_order(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def path_matches_patterns(path: str, patterns: list[str]) -> bool:
    normalized = normalize_repo_path(path)
    return any(fnmatch.fnmatch(normalized, pattern) for pattern in patterns)


def match_surfaces(manifest: dict[str, Any], changed_paths: list[str]) -> dict[str, Any]:
    normalized_paths = dedupe_preserve_order([normalize_repo_path(path) for path in changed_paths])
    matched_surfaces: list[dict[str, Any]] = []
    matched_path_set: set[str] = set()

    for surface in manifest["surfaces"]:
        matched_source_paths = [
            path for path in normalized_paths if path_matches_patterns(path, surface["source_paths"])
        ]
        matched_derived_paths = [
            path for path in normalized_paths if path_matches_patterns(path, surface["derived_paths"])
        ]
        if not matched_source_paths and not matched_derived_paths:
            continue
        matched_path_set.update(matched_source_paths)
        matched_path_set.update(matched_derived_paths)
        matched_surfaces.append(
            {
                "surface_id": surface["surface_id"],
                "description": surface["description"],
                "matched_source_paths": matched_source_paths,
                "matched_derived_paths": matched_derived_paths,
                "source_paths": surface["source_paths"],
                "derived_paths": surface["derived_paths"],
                "sync_commands": surface["sync_commands"],
                "verify_commands": surface["verify_commands"],
                "notes": surface["notes"],
            }
        )

    sync_commands = dedupe_preserve_order(
        [command for surface in matched_surfaces for command in surface["sync_commands"]]
    )
    verify_commands = dedupe_preserve_order(
        [command for surface in matched_surfaces for command in surface["verify_commands"]]
    )
    unmatched_paths = [path for path in normalized_paths if path not in matched_path_set]
    return {
        "changed_paths": normalized_paths,
        "matched_surfaces": matched_surfaces,
        "sync_commands": sync_commands,
        "verify_commands": verify_commands,
        "unmatched_paths": unmatched_paths,
    }


def lookup_generated_markdown(manifest: dict[str, Any] | None, derived_path: str) -> dict[str, str] | None:
    if manifest is None:
        return None
    normalized = normalize_repo_path(derived_path)
    for surface in manifest["surfaces"]:
        for entry in surface["generated_markdown"]:
            if entry["derived_path"] == normalized:
                return entry
    return None


def render_generated_markdown_header(entry: dict[str, str]) -> str:
    return (
        "<!--\n"
        "generated_file: true\n"
        f"source_path: {entry['source_path']}\n"
        f"derived_path: {entry['derived_path']}\n"
        f"generator: {entry['generator']}\n"
        f"sync_command: {entry['sync_command']}\n"
        "-->\n\n"
    )


def apply_generated_markdown_header(body: str, entry: dict[str, str] | None) -> str:
    if entry is None:
        return body
    return render_generated_markdown_header(entry) + body


def _run_git(repo_root: Path, *args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SurfaceError(result.stderr.strip() or result.stdout.strip() or "git command failed")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def collect_changed_paths(repo_root: Path) -> list[str]:
    tracked = _run_git(repo_root, "diff", "--name-only")
    staged = _run_git(repo_root, "diff", "--name-only", "--cached")
    untracked = _run_git(repo_root, "ls-files", "--others", "--exclude-standard")
    return dedupe_preserve_order(tracked + staged + untracked)
