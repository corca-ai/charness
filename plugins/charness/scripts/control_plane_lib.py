#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonschema
from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

from scripts.repo_layout import (
    integrations_locks_dir,
    integrations_tools_dir,
    support_capability_paths,
    support_capability_schema_path,
)
from scripts.runtime_bootstrap import repo_root_from_script
from scripts.subprocess_guard import run_process

LOCKS_DIR = Path("integrations/locks")
SEMVER_RE = re.compile(r"(?<!\d)\d+(?:\.\d+){1,}(?!\d)")

@dataclass
class CommandResult:
    command: str
    exit_code: int
    stdout: str
    stderr: str
def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
def load_manifest_schema(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root if repo_root is not None else repo_root_from_script(__file__)
    return json.loads((integrations_tools_dir(root) / "manifest.schema.json").read_text(encoding="utf-8"))
def load_lock_schema(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root if repo_root is not None else repo_root_from_script(__file__)
    return json.loads((integrations_locks_dir(root) / "lock.schema.json").read_text(encoding="utf-8"))
def load_support_capability_schema(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root if repo_root is not None else repo_root_from_script(__file__)
    return json.loads(support_capability_schema_path(root).read_text(encoding="utf-8"))

_NON_MANIFEST_TOOLS_FILES = {"manifest.schema.json", "dependencies.json", "dependencies.schema.json"}


def manifest_paths(repo_root: Path) -> list[Path]:
    return [path for path in sorted(integrations_tools_dir(repo_root).glob("*.json")) if path.name not in _NON_MANIFEST_TOOLS_FILES]


def _plugin_fallback_root() -> Path:
    return repo_root_from_script(__file__)


def plugin_fallback_manifest_paths() -> list[Path]:
    if os.environ.get("CHARNESS_DISABLE_PLUGIN_FALLBACK_MANIFESTS"):
        return []
    fallback_dir = integrations_tools_dir(_plugin_fallback_root())
    if not fallback_dir.is_dir():
        return []
    return [path for path in sorted(fallback_dir.glob("*.json")) if path.name not in _NON_MANIFEST_TOOLS_FILES]
def load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def validate_manifest_data(data: dict[str, Any], schema: dict[str, Any], path: Path) -> None:
    jsonschema.validate(data, schema)
    support = data.get("support_skill_source")
    if not support:
        return
    if support["source_type"] == "local_wrapper" and not support.get("wrapper_skill_id"):
        raise ValueError(f"{path}: local_wrapper requires wrapper_skill_id")
    if support["source_type"] == "upstream_repo" and Path(support["path"]).name == "SKILL.md":
        raise ValueError(f"{path}: upstream_repo support path must point at a skill root directory, not `SKILL.md`")

def validate_support_capability_data(data: dict[str, Any], schema: dict[str, Any], path: Path, repo_root: Path) -> None:
    jsonschema.validate(data, schema)
    expected_skill_path = str((path.parent / "SKILL.md").relative_to(repo_root))
    if data["support_skill_path"] != expected_skill_path:
        raise ValueError(
            f"{path}: support_skill_path must match colocated support skill `{expected_skill_path}`"
        )

def normalize_support_capability(data: dict[str, Any], path: Path, repo_root: Path) -> dict[str, Any]:
    return {
        "tool_id": data["capability_id"],
        "kind": data["kind"],
        "display_name": data["display_name"],
        "summary": data["summary"],
        "checks": data["checks"],
        "access_modes": data["access_modes"],
        "capability_requirements": data.get("capability_requirements", {}),
        "readiness_checks": data.get("readiness_checks", []),
        "config_layers": data.get("config_layers", []),
        "version_expectation": data["version_expectation"],
        "host_notes": data.get("host_notes", []),
        "support_skill_path": data["support_skill_path"],
        "supports_public_skills": data.get("supports_public_skills", []),
        "intent_triggers": data.get("intent_triggers", []),
        "_manifest_path": str(path.relative_to(repo_root)),
        "_capability_family": "support",
    }


def _load_manifests_merged(repo_root: Path, *, validate: bool) -> list[dict[str, Any]]:
    schema = load_manifest_schema() if validate else None
    manifests: list[dict[str, Any]] = []
    seen_tool_ids: set[str] = set()
    for path in manifest_paths(repo_root):
        data = load_manifest(path)
        if validate:
            validate_manifest_data(data, schema, path)
        tool_id = data["tool_id"]
        if tool_id in seen_tool_ids:
            raise ValueError(f"duplicate manifest tool_id `{tool_id}`")
        seen_tool_ids.add(tool_id)
        data["_manifest_path"] = str(path.relative_to(repo_root))
        data["_manifest_origin"] = "user-repo"
        manifests.append(data)
    plugin_root = _plugin_fallback_root().resolve()
    if plugin_root != repo_root.resolve():
        for path in plugin_fallback_manifest_paths():
            data = load_manifest(path)
            if validate:
                validate_manifest_data(data, schema, path)
            tool_id = data["tool_id"]
            if tool_id in seen_tool_ids:
                continue
            seen_tool_ids.add(tool_id)
            try:
                rel = str(path.relative_to(repo_root))
            except ValueError:
                rel = str(path)
            data["_manifest_path"] = rel
            data["_manifest_origin"] = "plugin-fallback"
            manifests.append(data)
    return manifests


def load_manifests(repo_root: Path) -> list[dict[str, Any]]:
    return _load_manifests_merged(repo_root, validate=True)


def load_manifests_for_discovery(repo_root: Path) -> list[dict[str, Any]]:
    return _load_manifests_merged(repo_root, validate=False)


def dependencies_path(repo_root: Path) -> Path:
    return integrations_tools_dir(repo_root) / "dependencies.json"


def dependencies_schema_path(repo_root: Path) -> Path:
    return integrations_tools_dir(repo_root) / "dependencies.schema.json"


def load_dependencies_schema() -> dict[str, Any]:
    plugin_root = _plugin_fallback_root()
    candidate = dependencies_schema_path(plugin_root)
    if candidate.is_file():
        return json.loads(candidate.read_text(encoding="utf-8"))
    repo_candidate = dependencies_schema_path(repo_root_from_script(__file__))
    return json.loads(repo_candidate.read_text(encoding="utf-8"))


def load_dependencies(repo_root: Path) -> dict[str, Any] | None:
    path = dependencies_path(repo_root)
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    jsonschema.validate(data, load_dependencies_schema())
    return data


def staged_tool_ids(repo_root: Path) -> set[str] | None:
    data = load_dependencies(repo_root)
    if data is None:
        return None
    return set(data["tool_dependencies"])


def add_dependency(repo_root: Path, tool_id: str) -> bool:
    path = dependencies_path(repo_root)
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {"schema_version": 1, "tool_dependencies": []}
    deps = list(data.get("tool_dependencies", []))
    if tool_id in deps:
        return False
    deps.append(tool_id)
    deps.sort()
    data["tool_dependencies"] = deps
    jsonschema.validate(data, load_dependencies_schema())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return True


def load_support_capabilities(repo_root: Path) -> list[dict[str, Any]]:
    capabilities: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    schema: dict[str, Any] | None = None
    for path in support_capability_paths(repo_root):
        if schema is None:
            schema = load_support_capability_schema(repo_root)
        data = load_manifest(path)
        validate_support_capability_data(data, schema, path, repo_root)
        capability_id = data["capability_id"]
        if capability_id in seen_ids:
            raise ValueError(f"duplicate support capability id `{capability_id}`")
        seen_ids.add(capability_id)
        capabilities.append(normalize_support_capability(data, path, repo_root))
    return capabilities


def load_capabilities(repo_root: Path) -> list[dict[str, Any]]:
    items = [*load_manifests(repo_root), *load_support_capabilities(repo_root)]
    seen_ids: set[str] = set()
    for item in items:
        tool_id = item["tool_id"]
        if tool_id in seen_ids:
            raise ValueError(f"duplicate capability id `{tool_id}`")
        seen_ids.add(tool_id)
    return items


def run_shell(command: str, cwd: Path) -> CommandResult:
    completed = run_process(
        command,
        cwd=cwd,
        shell=True,
        executable="/bin/bash",
    )
    return CommandResult(
        command=command,
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def evaluate_success_criteria(result: CommandResult, criteria: list[str]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for criterion in criteria:
        if criterion.startswith("exit_code:"):
            expected = int(criterion.split(":", 1)[1])
            if result.exit_code != expected:
                failures.append(f"expected exit_code {expected}, got {result.exit_code}")
        elif criterion.startswith("stdout_contains:"):
            expected = criterion.split(":", 1)[1]
            if expected not in result.stdout:
                failures.append(f"stdout missing `{expected}`")
        elif criterion.startswith("stderr_contains:"):
            expected = criterion.split(":", 1)[1]
            if expected not in result.stderr:
                failures.append(f"stderr missing `{expected}`")
        else:
            failures.append(f"unsupported success criterion `{criterion}`")
    return not failures, failures


def run_check(check: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    command_results = [run_shell(command, repo_root) for command in check["commands"]]
    ok = True
    failure_details: list[str] = []
    for result in command_results:
        passed, failures = evaluate_success_criteria(result, check["success_criteria"])
        if not passed:
            ok = False
            failure_details.extend(failures)
    return {
        "ok": ok,
        "results": [
            {
                "command": result.command,
                "exit_code": result.exit_code,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
            }
            for result in command_results
        ],
        "failure_details": failure_details,
        "failure_hint": check.get("failure_hint"),
    }


def extract_version(text: str) -> str | None:
    match = SEMVER_RE.search(text)
    if not match:
        return None
    return match.group(0)


def evaluate_version(manifest: dict[str, Any], detect_result: dict[str, Any]) -> dict[str, Any]:
    version_expectation = manifest["version_expectation"]
    policy = version_expectation["policy"]
    detected_by = version_expectation.get("detected_by", "manual")
    observed_version: str | None = None
    if detected_by == "stdout":
        outputs = [item["stdout"] for item in detect_result["results"]]
        observed_version = extract_version("\n".join(outputs))

    if policy == "advisory":
        return {
            "status": "advisory",
            "constraint": version_expectation["constraint"],
            "observed_version": observed_version,
        }

    if detected_by != "stdout" or observed_version is None:
        return {
            "status": "unknown",
            "constraint": version_expectation["constraint"],
            "observed_version": observed_version,
        }

    if policy not in {"exact", "minimum", "range"}:
        return {
            "status": "unknown",
            "constraint": version_expectation["constraint"],
            "observed_version": observed_version,
        }

    constraint = version_expectation["constraint"]
    try:
        observed = Version(observed_version)
        specifier = SpecifierSet(constraint)
    except (InvalidVersion, InvalidSpecifier):
        return {
            "status": "unknown",
            "constraint": constraint,
            "observed_version": observed_version,
        }

    return {
        "status": "matched" if observed in specifier else "mismatched",
        "constraint": constraint,
        "observed_version": observed_version,
    }


def validate_lock_data(data: dict[str, Any], schema: dict[str, Any]) -> None:
    jsonschema.validate(data, schema)


def lock_paths(repo_root: Path) -> list[Path]:
    return sorted(path for path in (repo_root / LOCKS_DIR).glob("*.json") if path.name != "lock.schema.json")


def lock_path(repo_root: Path, tool_id: str) -> Path:
    return repo_root / LOCKS_DIR / f"{tool_id}.json"


def read_lock(repo_root: Path, tool_id: str) -> dict[str, Any] | None:
    path = lock_path(repo_root, tool_id)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    try:
        validate_lock_data(data, load_lock_schema())
    except jsonschema.ValidationError as exc:
        sys.stderr.write(
            f"[charness] stale lock at {path} fails schema validation ({exc.message}); "
            "treating as missing so the next writer can regenerate it.\n"
        )
        return None
    return data


def upsert_lock(repo_root: Path, manifest: dict[str, Any], *, support: dict[str, Any] | None = None, doctor: dict[str, Any] | None = None, release: dict[str, Any] | None = None, provenance: dict[str, Any] | None = None, install: dict[str, Any] | None = None, update: dict[str, Any] | None = None) -> Path:
    payload = read_lock(repo_root, manifest["tool_id"]) or {}
    payload["schema_version"] = "1"
    payload["tool_id"] = manifest["tool_id"]
    payload["manifest_path"] = manifest["_manifest_path"]
    if support is not None:
        payload["support"] = support
    if doctor is not None:
        payload["doctor"] = doctor
    if release is not None:
        payload["release"] = release
    if provenance is not None:
        payload["provenance"] = provenance
    if install is not None:
        payload["install"] = install
    if update is not None:
        payload["update"] = update
    validate_lock_data(payload, load_lock_schema())
    path = lock_path(repo_root, manifest["tool_id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
