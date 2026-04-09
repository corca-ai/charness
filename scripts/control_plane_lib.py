#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonschema
from packaging.version import InvalidVersion, Version

MANIFEST_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "integrations" / "tools" / "manifest.schema.json"
LOCK_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "integrations" / "locks" / "lock.schema.json"
LOCKS_DIR = Path("integrations/locks")
TOOLS_DIR = Path("integrations/tools")
GENERATED_SUPPORT_DIR = Path("skills/support/generated")
SEMVER_RE = re.compile(r"\b\d+(?:\.\d+){1,}\b")


@dataclass
class CommandResult:
    command: str
    exit_code: int
    stdout: str
    stderr: str


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_manifest_schema() -> dict[str, Any]:
    return json.loads(MANIFEST_SCHEMA_PATH.read_text(encoding="utf-8"))


def load_lock_schema() -> dict[str, Any]:
    return json.loads(LOCK_SCHEMA_PATH.read_text(encoding="utf-8"))


def manifest_paths(repo_root: Path) -> list[Path]:
    manifests = sorted((repo_root / TOOLS_DIR).glob("*.json"))
    return [path for path in manifests if path.name != "manifest.schema.json"]


def load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest_data(data: dict[str, Any], schema: dict[str, Any], path: Path) -> None:
    jsonschema.validate(data, schema)
    support = data.get("support_skill_source")
    if support and support.get("sync_strategy") == "generated_wrapper" and not support.get("wrapper_skill_id"):
        raise ValueError(f"{path}: generated_wrapper requires wrapper_skill_id")


def load_manifests(repo_root: Path) -> list[dict[str, Any]]:
    schema = load_manifest_schema()
    manifests: list[dict[str, Any]] = []
    seen_tool_ids: set[str] = set()
    for path in manifest_paths(repo_root):
        data = load_manifest(path)
        validate_manifest_data(data, schema, path)
        tool_id = data["tool_id"]
        if tool_id in seen_tool_ids:
            raise ValueError(f"duplicate manifest tool_id `{tool_id}`")
        seen_tool_ids.add(tool_id)
        data["_manifest_path"] = str(path.relative_to(repo_root))
        manifests.append(data)
    return manifests


def manifest_by_tool_id(repo_root: Path) -> dict[str, dict[str, Any]]:
    return {manifest["tool_id"]: manifest for manifest in load_manifests(repo_root)}


def run_shell(command: str, cwd: Path) -> CommandResult:
    completed = subprocess.run(
        command,
        shell=True,
        executable="/bin/bash",
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
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

    try:
        observed = Version(observed_version)
    except InvalidVersion:
        return {
            "status": "unknown",
            "constraint": version_expectation["constraint"],
            "observed_version": observed_version,
        }

    constraint = version_expectation["constraint"]
    if policy == "exact":
        expected = constraint.removeprefix("==")
        status = "matched" if observed == Version(expected) else "mismatched"
    elif policy == "minimum":
        expected = constraint.removeprefix(">=")
        status = "matched" if observed >= Version(expected) else "mismatched"
    elif policy == "range":
        lower, _, upper = constraint.partition(",")
        lower_ok = True
        upper_ok = True
        if lower:
            lower_ok = observed >= Version(lower.strip().removeprefix(">="))
        if upper:
            upper_ok = observed <= Version(upper.strip().removeprefix("<="))
        status = "matched" if lower_ok and upper_ok else "mismatched"
    else:
        status = "unknown"

    return {
        "status": status,
        "constraint": constraint,
        "observed_version": observed_version,
    }


def support_state_for_manifest(manifest: dict[str, Any]) -> str:
    support = manifest.get("support_skill_source")
    if not support:
        return "integration-only"
    strategy = support["sync_strategy"]
    if strategy == "generated_wrapper" or support["source_type"] == "local_wrapper":
        return "wrapped-upstream"
    return "upstream-consumed"


def validate_lock_data(data: dict[str, Any], schema: dict[str, Any], path: Path) -> None:
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
    validate_lock_data(data, load_lock_schema(), path)
    return data


def base_lock_payload(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "1",
        "tool_id": manifest["tool_id"],
        "manifest_path": manifest["_manifest_path"],
    }


def upsert_lock(
    repo_root: Path,
    manifest: dict[str, Any],
    *,
    support: dict[str, Any] | None = None,
    doctor: dict[str, Any] | None = None,
    update: dict[str, Any] | None = None,
) -> Path:
    payload = read_lock(repo_root, manifest["tool_id"]) or base_lock_payload(manifest)
    payload["schema_version"] = "1"
    payload["tool_id"] = manifest["tool_id"]
    payload["manifest_path"] = manifest["_manifest_path"]
    if support is not None:
        payload["support"] = support
    if doctor is not None:
        payload["doctor"] = doctor
    if update is not None:
        payload["update"] = update
    validate_lock_data(payload, load_lock_schema(), lock_path(repo_root, manifest["tool_id"]))
    path = lock_path(repo_root, manifest["tool_id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def selected_manifests(repo_root: Path, tool_ids: list[str]) -> list[dict[str, Any]]:
    manifests = manifest_by_tool_id(repo_root)
    if not tool_ids:
        return list(manifests.values())
    return [manifests[tool_id] for tool_id in tool_ids if tool_id in manifests]


def render_generated_wrapper(manifest: dict[str, Any]) -> str:
    tool_id = manifest["tool_id"]
    support = manifest["support_skill_source"]
    wrapper_id = support["wrapper_skill_id"]
    return "\n".join(
        [
            "---",
            f"name: {wrapper_id}",
            f'description: \"Generated wrapper for the upstream {tool_id} support surface.\"',
            "---",
            "",
            f"# {wrapper_id}",
            "",
            f"This generated wrapper points at the upstream `{tool_id}` support guidance.",
            "",
            f"- upstream repo: `{manifest['upstream_repo']}`",
            f"- upstream path: `{support['path']}`",
            f"- sync strategy: `{support['sync_strategy']}`",
            "",
            "Regenerate this file through `scripts/sync_support.py` instead of editing it by hand.",
            "",
        ]
    )


def render_reference_note(manifest: dict[str, Any]) -> str:
    support = manifest["support_skill_source"]
    return "\n".join(
        [
            f"# {manifest['tool_id']} Support Reference",
            "",
            "This generated reference records how `charness` consumes the upstream",
            "support surface without copying it into the local taxonomy.",
            "",
            f"- upstream repo: `{manifest['upstream_repo']}`",
            f"- upstream path: `{support['path']}`",
            f"- sync strategy: `{support['sync_strategy']}`",
            f"- support state: `{support_state_for_manifest(manifest)}`",
            "",
            "Regenerate this file through `scripts/sync_support.py` instead of",
            "editing it by hand.",
            "",
        ]
    )


def materialize_support(repo_root: Path, manifest: dict[str, Any]) -> list[str]:
    support = manifest.get("support_skill_source")
    if not support:
        return []
    strategy = support["sync_strategy"]
    if strategy == "generated_wrapper":
        wrapper_id = support["wrapper_skill_id"]
        skill_dir = repo_root / GENERATED_SUPPORT_DIR / wrapper_id
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_path = skill_dir / "SKILL.md"
        skill_path.write_text(render_generated_wrapper(manifest), encoding="utf-8")
        return [str(skill_path.relative_to(repo_root))]
    if strategy == "reference":
        reference_dir = repo_root / GENERATED_SUPPORT_DIR / manifest["tool_id"]
        reference_dir.mkdir(parents=True, exist_ok=True)
        reference_path = reference_dir / "REFERENCE.md"
        reference_path.write_text(render_reference_note(manifest), encoding="utf-8")
        return [str(reference_path.relative_to(repo_root))]
    raise ValueError(f"unsupported sync strategy `{strategy}` for local materialization")
