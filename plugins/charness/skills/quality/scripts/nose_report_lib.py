#!/usr/bin/env python3
"""Run nose and parse/summarize its versioned JSON report.

Split out of `inventory_nose_clones.py` (cohesion + length cap): turning a nose
invocation into a normalized `{status, families, scope, ranking, ...}` payload is
its own concern, separate from command building, the advisory-interpretation
contract, and rendering. The nose command + JSON shape are pinned here — the one
resolver shared by the clone advisory and the dup-ratchet gate.

nose 0.13.3 removed the deprecated `nose scan` subcommand, so the code path runs
`nose query` instead. The migration is isolated to this resolver:

- `nose query <path> all top=N sort=K --mode M --min-size S --format json`. `all`,
  `top=`, and `sort=` are query TERMS (positional), NOT flags — passing
  `--top`/`--sort` to `query` errors and yields zero families.
- `query` accepts ONE path root per call, so a multi-root scope is scanned per
  path and merged here (`collect_families`), deduped by family identity. A
  cross-root clone family that scan would have grouped is split per path; this is
  accepted query semantics (re-baseline per scanner version).
- The `--format json` family array is `families` (with the `all` term) under both
  schema_version 2 (nose 0.13.0 query) and schema_version 3 (0.13.3 query); the
  no-`all` dashboard emits `top_candidates`. `extract_report` reads either, plus
  the legacy bare-array / scan-object shapes still used by test fixtures.
- Family identity is `id` in query output (a stable 16-hex content hash), named
  `family_id` in the removed `scan` output; `family_summary` normalizes to
  `family_id`. Locations use `start`/`end` (query) vs `start_line`/`end_line`
  (scan). `query` carries no top-level `tool_version`, so it is stamped from
  `nose --version` (`resolve_tool_version`) when the report omits it.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

NOSE_TIMEOUT_SECONDS = 180
_VERSION_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)")


def resolve_tool_version(nose_bin: str) -> str:
    """Best-effort `nose --version` string ("" on failure). The `query` JSON omits
    the version that the removed `scan` report carried, so the advisory stamps it
    from here when a report does not supply one."""
    try:
        completed = subprocess.run(
            [nose_bin, "--version"], check=False, capture_output=True, text=True, timeout=30
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    match = _VERSION_RE.search(completed.stdout or "")
    return match.group(0) if match else ""


def build_query_command(
    nose_bin: str,
    path: str,
    *,
    mode: str,
    min_size: int,
    top: int,
    sort: str,
    exclude: list[str] | None = None,
    ignore_file: str | None = None,
) -> list[str]:
    """One single-path `nose query` command. `all`/`top=`/`sort=` are query terms
    (positional after the path); `--mode`/`--min-size`/`--exclude`/`--ignore-file`/
    `--format` are flags. `query` takes one path root per call, so the multi-root
    scope is looped in `collect_families`, never passed as several positional roots
    (a sibling root would be parsed as an unknown query term and error)."""
    command = [
        nose_bin,
        "query",
        path,
        "all",
        f"top={top}",
        f"sort={sort}",
        "--mode",
        mode,
        "--min-size",
        str(min_size),
    ]
    for pattern in exclude or []:
        command.extend(["--exclude", pattern])
    if ignore_file:
        command.extend(["--ignore-file", ignore_file])
    command.extend(["--format", "json"])
    return command


def family_identity(family: dict[str, Any]) -> str | None:
    """Normalized clone-family identity: query's `id` or scan's `family_id`."""
    identity = family.get("family_id") or family.get("id")
    return str(identity) if identity else None


def collect_families(
    repo_root: Path,
    nose_bin: str,
    paths: list[str],
    *,
    mode: str,
    min_size: int,
    top: int,
    sort: str,
    exclude: list[str] | None = None,
    ignore_file: str | None = None,
) -> dict[str, Any]:
    """Run `nose query` per path (query takes one root) and merge the families,
    deduped by identity. Any errored path makes the WHOLE result `error` so a
    consumer degrades to advisory rather than under-reporting a broken scan as a
    clean pass. Each merged family carries a normalized `family_id`."""
    merged: dict[str, dict[str, Any]] = {}
    unkeyed: list[dict[str, Any]] = []
    errors: list[str] = []
    total_ranked = 0
    have_total = False
    exit_code = 0
    json_version = ""
    for path in paths:
        command = build_query_command(
            nose_bin, path, mode=mode, min_size=min_size, top=top, sort=sort,
            exclude=exclude, ignore_file=ignore_file,
        )
        result = run_nose(repo_root, command)
        if result["status"] == "error":
            errors.append(f"{path}: {result.get('stderr', '')[:120]}")
            exit_code = result.get("exit_code") or exit_code or 1
            continue
        if not json_version and result.get("tool_version"):
            json_version = str(result["tool_version"])
        ranked = (result.get("ranking") or {}).get("total_families")
        if isinstance(ranked, int):
            total_ranked += ranked
            have_total = True
        for family in result["families"]:
            identity = family_identity(family)
            if identity:
                family.setdefault("family_id", identity)
                merged.setdefault(identity, family)
            else:
                unkeyed.append(family)
    families = list(merged.values()) + unkeyed
    tool_version = json_version or resolve_tool_version(nose_bin)
    status = "error" if errors else ("findings" if families else "clean")
    return {
        "status": status,
        "exit_code": exit_code,
        "stdout": "",
        "stderr": "; ".join(errors),
        "families": families,
        "tool_version": tool_version,
        "scope": {"paths": list(paths)},
        "ranking": {
            "total_families": total_ranked if have_total else len(families),
            "shown_families": len(families),
        },
    }


def family_summary(family: dict[str, Any]) -> dict[str, Any]:
    """Normalize one clone family across scan (`family_id`/`start_line`/`dup_lines`)
    and query (`id`/`start`/derived) shapes. `dup_lines` is derived from the member
    location spans when the report omits it (query carries no `dup_lines`); it stays
    a display proxy, never a reduction target."""
    locations = family.get("locations", [])
    files = []
    derived_dup_lines = 0
    have_span = False
    if isinstance(locations, list):
        for location in locations:
            if not isinstance(location, dict):
                continue
            file = location.get("file")
            if not isinstance(file, str):
                continue
            start = location.get("start_line", location.get("start"))
            end = location.get("end_line", location.get("end"))
            if isinstance(start, int) and isinstance(end, int):
                derived_dup_lines += max(0, end - start + 1)
                have_span = True
            if len(files) < 6:
                files.append(
                    {
                        "file": file,
                        "start_line": start,
                        "end_line": end,
                        "name": location.get("name"),
                        "kind": location.get("kind"),
                    }
                )
    dup_lines = family.get("dup_lines")
    if not isinstance(dup_lines, int):
        dup_lines = derived_dup_lines if have_span else None
    shared_lines = family.get("shared_lines")
    if not isinstance(shared_lines, int):
        shared_lines = family.get("shared")
    return {
        "family_id": family.get("family_id") or family.get("id"),
        "value": family.get("value"),
        "members": family.get("members"),
        "files": family.get("files"),
        "modules": family.get("modules"),
        "languages": family.get("languages"),
        "mean_score": family.get("mean_score"),
        "dup_lines": dup_lines,
        "shared_lines": shared_lines,
        "params": family.get("params"),
        "sample_locations": files,
    }


def run_nose(repo_root: Path, command: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=NOSE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "error",
            "exit_code": 124,
            "stdout": str(exc.stdout or ""),
            "stderr": f"nose timed out after {NOSE_TIMEOUT_SECONDS}s",
            "families": [],
            "tool_version": "",
        }
    except OSError as exc:
        # An explicitly-set-but-invalid NOSE_BIN (resolve_nose_bin returns the
        # override unchecked) must degrade to advisory, not crash — FD8: a broken
        # tool never false-blocks. Symmetric with resolve_tool_version's guard.
        return {
            "status": "error",
            "exit_code": 1,
            "stdout": "",
            "stderr": f"nose could not be executed: {exc}",
            "families": [],
            "tool_version": "",
        }
    try:
        parsed = json.loads(completed.stdout) if completed.stdout.strip() else []
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": f"nose emitted invalid JSON: {exc}; stderr: {completed.stderr.strip()}",
            "families": [],
            "tool_version": "",
        }
    families, tool_version, scope, ranking = extract_report(parsed)
    status = "findings" if families else "clean"
    if completed.returncode != 0:
        status = "error"
    return {
        "status": status,
        "exit_code": completed.returncode,
        "stdout": "",
        "stderr": completed.stderr.strip(),
        "families": families,
        "tool_version": tool_version,
        "scope": scope,
        "ranking": ranking,
    }


def extract_report(parsed: Any) -> tuple[list[dict[str, Any]], str, dict[str, Any], dict[str, Any]]:
    """Return report fields across nose's JSON shapes.

    `nose query <path> all --format json` emits a top-level object with `families`
    (schema_version 2 on 0.13.0, 3 on 0.13.3); the no-`all` dashboard emits
    `top_candidates` instead. The removed `nose scan` emitted `families` with a
    `tool_version` (and 0.4 emitted a bare top-level array). Reading the wrong key
    silently yielded zero families, under-reporting the live scan. When only a
    `summary` block is present, ranking is derived from it for the advisory's
    "showing N of M" line.
    """
    families: Any = []
    tool_version = ""
    scope: Any = {}
    ranking: Any = {}
    if isinstance(parsed, dict):
        families = parsed.get("families")
        if not isinstance(families, list):
            families = parsed.get("top_candidates")
        tool_version = str(parsed.get("tool_version") or "")
        scope = parsed.get("scope")
        ranking = parsed.get("ranking")
        if not isinstance(ranking, dict):
            summary = parsed.get("summary")
            if isinstance(summary, dict):
                ranking = {
                    "total_families": summary.get("families"),
                    "shown_families": summary.get("shown"),
                }
    elif isinstance(parsed, list):
        families = parsed
    if not isinstance(families, list):
        families = []
    if not isinstance(scope, dict):
        scope = {}
    if not isinstance(ranking, dict):
        ranking = {}
    return [family for family in families if isinstance(family, dict)], tool_version, scope, ranking
