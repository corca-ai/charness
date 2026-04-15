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


def render_repo_followup(repo_root: Path, install_action: dict[str, Any]) -> dict[str, Any] | None:
    repo_followup = install_action.get("repo_followup")
    if not isinstance(repo_followup, dict):
        return None
    command_template = repo_followup.get("command_template")
    if not isinstance(command_template, str) or not command_template:
        return None
    return {
        "summary": repo_followup.get("summary"),
        "command_template": command_template,
        "rendered_command": command_template.format(repo_root=str(repo_root)),
        "docs_url": repo_followup.get("docs_url"),
        "when": repo_followup.get("when"),
        "optional": repo_followup.get("optional", False),
    }


def select_by_tool_id(items: list[dict[str, Any]], tool_ids: list[str]) -> list[dict[str, Any]]:
    if not tool_ids:
        return list(items)
    requested = set(tool_ids)
    return [item for item in items if item["tool_id"] in requested]


def print_tool_statuses(results: list[dict[str, Any]], *, status_key: str = "status") -> None:
    for result in results:
        print(f"{result['tool_id']}: {result[status_key]}")


def has_any_status(results: list[dict[str, Any]], *, status_key: str, statuses: set[str]) -> bool:
    return any(result[status_key] in statuses for result in results)


def attach_release_metadata(result: dict[str, Any], *, provenance: dict[str, Any], release: dict[str, Any] | None) -> dict[str, Any]:
    result["provenance"] = provenance
    if release is not None:
        result["release"] = release
    return result
