from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.control_plane_lib import CommandResult, run_check, run_shell


def failed_healthcheck(manifest: dict[str, Any], *, reason: str) -> dict[str, Any]:
    return {
        "ok": False,
        "results": [],
        "failure_details": [reason],
        "failure_hint": manifest["checks"]["healthcheck"].get("failure_hint"),
    }


def detect_and_healthcheck(repo_root: Path, manifest: dict[str, Any], *, failure_reason: str) -> tuple[dict[str, Any], dict[str, Any]]:
    detect_result = run_check(manifest["checks"]["detect"], repo_root)
    healthcheck_result = (
        run_check(manifest["checks"]["healthcheck"], repo_root)
        if detect_result["ok"]
        else failed_healthcheck(manifest, reason=failure_reason)
    )
    return detect_result, healthcheck_result


def command_result_payload(result: CommandResult) -> dict[str, Any]:
    return {
        "command": result.command,
        "exit_code": result.exit_code,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def run_command_payloads(commands: list[str], repo_root: Path) -> list[dict[str, Any]]:
    return [command_result_payload(run_shell(command, repo_root)) for command in commands]


def attach_release_metadata(result: dict[str, Any], *, provenance: dict[str, Any], release: dict[str, Any] | None) -> dict[str, Any]:
    result["provenance"] = provenance
    if release is not None:
        result["release"] = release
    return result
