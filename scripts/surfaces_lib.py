#!/usr/bin/env python3

from __future__ import annotations

import fnmatch
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from scripts.core.git_status_snapshot import GitStatusError
from scripts.core.git_status_snapshot import capture as capture_git_status
from scripts.core.git_status_snapshot import parse as parse_git_status

try:
    from scripts.core.subprocess_guard import run_process
except ImportError:  # flat layout: the repo root is not on sys.path
    _repo_root = next(
        ancestor
        for ancestor in Path(__file__).resolve().parents
        if (ancestor / "scripts" / "core" / "subprocess_guard.py").is_file()
    )
    if str(_repo_root) not in sys.path:
        sys.path.insert(0, str(_repo_root))
    from scripts.core.subprocess_guard import run_process

SURFACES_PATH = Path(".agents/surfaces.json")

# A `<dir>/**/*.X` pattern is the #331 closeout-matcher footgun: surface matching
# is fnmatch, where `*` already crosses `/`, so `**/*.X` requires an intermediate
# directory segment and silently misses a top-level `<dir>/<file>.X`. The lint
# below requires the strict-superset `<dir>/*.X` sibling to be present; it does
# NOT rewrite matching semantics (that was #331's rejected Option B).
# The optional `<dir>/` prefix also catches a root-level `**/*.X` (no directory),
# which is the same footgun: fnmatch `*` crosses `/`, so `**/*.py` misses a
# top-level `top.py`. Its required sibling is the bare `*.X`.
_RECURSIVE_EXTENSION_PATTERN = re.compile(r"^(?:(?P<dir>.+)/)?\*\*/\*(?P<ext>\.[^/*]+)$")


class SurfaceError(Exception):
    pass


@dataclass(frozen=True)
class WorkingTreeSnapshot:
    changed_paths: tuple[str, ...]
    deleted_paths: frozenset[str]


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


def _check_surface_idiom(patterns: list[str], field: str) -> None:
    pattern_set = set(patterns)
    for pattern in patterns:
        match = _RECURSIVE_EXTENSION_PATTERN.match(pattern)
        if match is None:
            continue
        directory = match.group("dir")
        sibling = f"{directory}/*{match.group('ext')}" if directory else f"*{match.group('ext')}"
        if sibling not in pattern_set:
            raise SurfaceError(
                f"`{field}` pattern `{pattern}` uses the non-recursive-fnmatch footgun "
                f"`<dir>/**/*.X` without its `<dir>/*.X` sibling `{sibling}`: surface matching "
                f"is fnmatch where `*` crosses `/`, so `**/*.X` requires an intermediate "
                f"directory and silently misses a top-level `<dir>/<file>{match.group('ext')}` "
                f"(#331). Add `{sibling}` (a strict superset) or replace the pattern with it."
            )


def _validate_generated_markdown_entry(entry: object, field: str) -> dict[str, str]:
    if not isinstance(entry, dict):
        raise SurfaceError(f"`{field}` must be an object")
    source_path = normalize_repo_path(
        _require_string(entry.get("source_path"), f"{field}.source_path")
    )
    derived_path = normalize_repo_path(
        _require_string(entry.get("derived_path"), f"{field}.derived_path")
    )
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
    source_paths = [
        normalize_repo_path(path)
        for path in _require_string_list(surface.get("source_paths"), f"{field}.source_paths")
    ]
    derived_paths = [
        normalize_repo_path(path)
        for path in _require_string_list(surface.get("derived_paths"), f"{field}.derived_paths")
    ]
    _check_surface_idiom(source_paths, f"{field}.source_paths")
    _check_surface_idiom(derived_paths, f"{field}.derived_paths")
    sync_commands = _require_string_list(surface.get("sync_commands"), f"{field}.sync_commands")
    verify_commands = _require_string_list(
        surface.get("verify_commands"), f"{field}.verify_commands"
    )
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


def load_surfaces(
    repo_root: Path, *, surfaces_path: Path = SURFACES_PATH, required: bool = True
) -> dict[str, Any] | None:
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


def resolve_trigger_surfaces(
    manifest: dict[str, Any], configured_ids: list[str]
) -> dict[str, list[str]]:
    declared_ids = {surface["surface_id"] for surface in manifest["surfaces"]}
    declared: list[str] = []
    unresolved: list[str] = []
    for surface_id in configured_ids:
        if surface_id in declared_ids:
            declared.append(surface_id)
        else:
            unresolved.append(surface_id)
    return {"declared": declared, "unresolved": unresolved}


def match_surfaces(manifest: dict[str, Any], changed_paths: list[str]) -> dict[str, Any]:
    normalized_paths = dedupe_preserve_order([normalize_repo_path(path) for path in changed_paths])
    matched_surfaces: list[dict[str, Any]] = []
    matched_path_set: set[str] = set()

    for surface in manifest["surfaces"]:
        matched_source_paths = [
            path
            for path in normalized_paths
            if path_matches_patterns(path, surface["source_paths"])
        ]
        matched_derived_paths = [
            path
            for path in normalized_paths
            if path_matches_patterns(path, surface["derived_paths"])
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


def lookup_generated_markdown(
    manifest: dict[str, Any] | None, derived_path: str
) -> dict[str, str] | None:
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
    """Enumerate paths NUL-separated, so the name git prints is the name on disk.

    `-z` is appended rather than optional. Without it git applies `core.quotepath`,
    whose DEFAULT is true, and any path with a non-ASCII or special byte comes back
    C-quoted -- `"\\355\\225\\234\\352\\270\\200.md"` instead of the real name. The
    identity builder already passes `-z`, so the two components disagreed about the
    same file: the identity bound the real path while this narrative carried the
    escaped spelling, which then matched no surface glob and reported a clean
    "no surfaces matched". Invisible on a maintainer machine whose gitconfig sets
    `core.quotepath=false`, and live on a fresh clone or CI runner that does not.
    """
    result = run_process(["git", *args, "-z"], cwd=repo_root, timeout_seconds=None)
    if result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        raise SurfaceError(stderr or stdout or "git command failed")
    return [entry for entry in result.stdout.split("\0") if entry]


def _parse_working_tree_status(output: bytes) -> WorkingTreeSnapshot:
    try:
        snapshot = parse_git_status(output)
    except GitStatusError as exc:
        raise SurfaceError(str(exc)) from exc
    return WorkingTreeSnapshot(tuple(snapshot.dirty_destination_paths()), snapshot.deleted_paths())


def collect_working_tree_snapshot(repo_root: Path) -> WorkingTreeSnapshot:
    try:
        snapshot = capture_git_status(repo_root)
    except GitStatusError as exc:
        raise SurfaceError(str(exc)) from exc
    except OSError as exc:
        raise SurfaceError(str(exc) or "git status failed") from exc
    deleted = {
        path
        for path in snapshot.deleted_paths()
        if not ((repo_root / path).exists() or (repo_root / path).is_symlink())
    }
    return WorkingTreeSnapshot(tuple(snapshot.dirty_destination_paths()), deleted)


def collect_changed_paths(repo_root: Path) -> list[str]:
    return list(collect_working_tree_snapshot(repo_root).changed_paths)


def collect_deleted_paths(repo_root: Path) -> set[str]:
    """Working-tree deletions from one status snapshot.

    A path staged as deleted and then RECREATED on disk is not a deletion to a
    reviewer: the file is there and the identity binds its present bytes.
    `exists()` follows a symlink, so a retained but broken pointer is kept.
    """
    return set(collect_working_tree_snapshot(repo_root).deleted_paths)


def collect_changed_paths_for_ref(repo_root: Path, ref: str) -> list[str]:
    ref = ref.strip()
    if not ref:
        raise SurfaceError("changed ref must be non-empty")
    if ".." in ref:
        return dedupe_preserve_order(_run_git(repo_root, "diff", "--name-only", ref))
    return dedupe_preserve_order(
        _run_git(repo_root, "diff-tree", "--root", "-m", "--no-commit-id", "--name-only", "-r", ref)
    )


def collect_deleted_paths_for_ref(repo_root: Path, ref: str) -> set[str]:
    """The subset of a ref's changed paths that the ref REMOVED.

    Kept separate from `collect_changed_paths_for_ref` rather than folded into it:
    surface matching must keep treating a removed file as belonging to its
    surface, because "which owning surface just lost a file" is the question a
    reviewer judging a removal is actually asking. This only supplies the marker
    that distinguishes a deletion from an edit in the rendered listing.
    """
    ref = ref.strip()
    if not ref:
        raise SurfaceError("changed ref must be non-empty")
    if ".." in ref:
        args = ("diff", "--name-only", "--diff-filter=D", ref)
    else:
        args = (
            "diff-tree",
            "--root",
            "-m",
            "--no-commit-id",
            "--name-only",
            "--diff-filter=D",
            "-r",
            ref,
        )
    return set(dedupe_preserve_order(_run_git(repo_root, *args)))


def _parse_name_status_records(records: list[str]) -> tuple[list[str], set[str]]:
    """(changed paths, deleted paths) from one `--name-status -z` record stream.

    A rename record carries three NUL-separated fields (`status`, old path, new
    path); every other status carries two (`status`, path). Only the LAST field
    is the path this reports, matching what `--name-only` alone would have
    printed for the same record: a rename shows only its destination, never its
    source, and a pure `D` record shows the one path it has.
    """
    changed: list[str] = []
    deleted: set[str] = set()
    index = 0
    while index < len(records):
        status = records[index]
        fields = 3 if status.startswith(("R", "C")) else 2
        path = records[index + fields - 1]
        index += fields
        changed.append(path)
        if status.startswith("D"):
            deleted.add(path)
    return dedupe_preserve_order(changed), deleted


def collect_changed_and_deleted_paths_for_ref(
    repo_root: Path, ref: str
) -> tuple[list[str], set[str]]:
    """`(changed_paths, deleted_paths)` for one ref, from a single git process.

    `collect_changed_paths_for_ref` and `collect_deleted_paths_for_ref` each ran
    their own diff over the identical ref -- a `--name-only` pass and a second
    `--name-only --diff-filter=D` pass -- for a caller that wants both. A single
    `--name-status` pass already carries the per-path status letter that
    `--diff-filter=D` used to need a second process to isolate.
    """
    ref = ref.strip()
    if not ref:
        raise SurfaceError("changed ref must be non-empty")
    if ".." in ref:
        args = ("diff", "--name-status", ref)
    else:
        args = (
            "diff-tree",
            "--root",
            "-m",
            "--no-commit-id",
            "--name-status",
            "-r",
            ref,
        )
    return _parse_name_status_records(_run_git(repo_root, *args))
