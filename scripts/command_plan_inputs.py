"""Load command plans and resolve their repo-owned input identities.

This module owns the input side of command-plan preflight: reading the plan,
resolving target paths from the inspectable repo inventory, and verifying git
refs before any owner command is probed. Keeping that boundary together makes
the preflight's refusal-before-fan-out contract explicit.
"""

from __future__ import annotations

import fnmatch
import json
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module

_path_portability = import_repo_module(__file__, "scripts.core.path_portability_lib")
run_process = import_repo_module(__file__, "scripts.core.subprocess_guard").run_process

PLAN_VERSION = 1


def _repo_relative(root: Path, path: Path) -> str:
    relative = _path_portability.resolve_within_repo(root, str(path))
    if relative is None:
        raise ValueError(f"path must stay under repo root: {path}")
    return relative


def _error(code: str, message: str, **details: Any) -> dict[str, Any]:
    failure = {"code": code, "message": message}
    failure.update(details)
    return failure


def _load_plan(root: Path, plan_path: Path) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    try:
        relative = _repo_relative(root, plan_path)
    except ValueError as exc:
        return None, [_error("plan-outside-repo", str(exc))]
    if not plan_path.is_file():
        return None, [_error("plan-missing", f"plan does not exist: {relative}")]
    try:
        value = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, [_error("plan-invalid-json", f"could not read JSON plan {relative}: {exc}")]
    if not isinstance(value, dict):
        return None, [_error("plan-shape", "plan root must be an object")]
    if value.get("schema_version") != PLAN_VERSION:
        errors.append(
            _error(
                "unsupported-plan-version",
                f"schema_version must be {PLAN_VERSION}",
                actual=value.get("schema_version"),
            )
        )
    for field in ("targets", "refs", "commands"):
        if not isinstance(value.get(field), list):
            errors.append(_error("plan-shape", f"{field} must be a list"))
    return value, errors


def _repo_files(root: Path) -> tuple[list[str], dict[str, Any] | None]:
    try:
        result = run_process(
            ["rg", "--files", "--hidden", "--glob", "!.git/**"],
            cwd=root,
            timeout_seconds=None,
        )
    except OSError as exc:
        return [], _error("rg-unavailable", f"could not run rg --files: {exc}")
    if result.returncode not in (0, 1):
        return [], _error(
            "rg-files-failed",
            "rg --files failed; no command fan-out may start",
            exit_code=result.returncode,
            stderr=result.stderr.strip(),
        )
    return [
        line.strip().removeprefix("./") for line in result.stdout.splitlines() if line.strip()
    ], None


def _target_matches(query: str, files: list[str]) -> list[str]:
    normalized = query.removeprefix("./")
    if normalized in files:
        return [normalized]
    if "/" not in normalized:
        return sorted(path for path in files if Path(path).name == normalized)
    return sorted(path for path in files if fnmatch.fnmatch(path, normalized))


def _resolve_targets(root: Path, raw_targets: Any) -> tuple[dict[str, str], list[dict[str, Any]]]:
    resolved: dict[str, str] = {}
    errors: list[dict[str, Any]] = []
    if not isinstance(raw_targets, list):
        return resolved, [_error("plan-shape", "targets must be a list")]
    files, inventory_error = _repo_files(root)
    if inventory_error:
        return resolved, [inventory_error]
    for item in raw_targets:
        if not isinstance(item, dict):
            errors.append(_error("target-shape", "each target must be an object"))
            continue
        target_id = item.get("id")
        query = item.get("query")
        expected = item.get("expected_path")
        if not isinstance(target_id, str) or not target_id:
            errors.append(_error("target-shape", "target id must be a non-empty string"))
            continue
        if target_id in resolved:
            errors.append(_error("duplicate-target", f"target id is repeated: {target_id}"))
            continue
        if not isinstance(query, str) or not query:
            errors.append(_error("target-shape", f"{target_id}: query must be a non-empty string"))
            continue
        if expected is not None and (not isinstance(expected, str) or not expected):
            errors.append(_error("target-shape", f"{target_id}: expected_path must be a string"))
            continue
        matches = _target_matches(query, files)
        if isinstance(expected, str) and expected.removeprefix("./") not in matches:
            errors.append(
                _error(
                    "target-mismatch",
                    f"{target_id}: expected_path is not one of the rg --files matches",
                    query=query,
                    expected_path=expected,
                    matches=matches,
                )
            )
            continue
        if not matches:
            same_name = sorted(path for path in files if Path(path).name == Path(query).name)
            errors.append(
                _error(
                    "target-not-found",
                    f"{target_id}: rg --files found no target for {query}",
                    query=query,
                    candidates=same_name[:12],
                )
            )
            continue
        if len(matches) != 1:
            errors.append(
                _error(
                    "target-ambiguous",
                    f"{target_id}: target query resolves to multiple files; add expected_path",
                    query=query,
                    matches=matches,
                )
            )
            continue
        resolved[target_id] = matches[0]
    return resolved, errors


def _verify_refs(root: Path, raw_refs: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    observations: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    if not isinstance(raw_refs, list):
        return observations, [_error("plan-shape", "refs must be a list")]
    for item in raw_refs:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("id"), str)
            or not isinstance(item.get("ref"), str)
        ):
            errors.append(_error("ref-shape", "each ref needs string id and ref fields"))
            continue
        ref_id = item["id"]
        ref = item["ref"]
        result = run_process(
            ["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
            cwd=root,
            timeout_seconds=None,
        )
        resolved = result.stdout.strip()
        observation = {
            "id": ref_id,
            "ref": ref,
            "status": "pass" if result.returncode == 0 else "fail",
        }
        if result.returncode == 0 and resolved:
            observation["resolved_commit"] = resolved
            observations.append(observation)
        else:
            observation["exit_code"] = result.returncode
            observation["stderr"] = result.stderr.strip()
            observations.append(observation)
            errors.append(
                _error(
                    "ref-unresolved",
                    f"{ref_id}: git rev-parse --verify could not resolve {ref}",
                    ref=ref,
                    exit_code=result.returncode,
                    stderr=result.stderr.strip(),
                )
            )
    return observations, errors
