from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from scripts.cautilus_adapter_lib import load_cautilus_adapter
from scripts.control_plane_lib import command_result_payload, run_check, run_shell
from scripts.upstream_release_lib import observed_version_from_detect, upgrade_advisory


def disabled_by_cautilus_adapter(repo_root: Path, manifest: dict[str, Any]) -> dict[str, Any] | None:
    if manifest.get("tool_id") != "cautilus":
        return None
    adapter = load_cautilus_adapter(repo_root)
    if not adapter["valid"]:
        return None
    data = adapter["data"]
    if data.get("run_mode") != "disabled":
        return None
    reason = data.get("disabled_reason")
    return {
        "tool_id": "cautilus",
        "reason": reason if isinstance(reason, str) and reason else "Cautilus is disabled by repo adapter.",
        "adapter_path": adapter["path"],
    }


def disabled_check_payload(disabled: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": False,
        "results": [],
        "failure_details": [f"disabled by repo adapter: {disabled['reason']}"],
        "failure_hint": "Re-enable `.agents/cautilus-adapter.yaml` before running Cautilus checks.",
    }


def failed_healthcheck(manifest: dict[str, Any], *, reason: str) -> dict[str, Any]:
    healthcheck = manifest.get("checks", {}).get("healthcheck", {})
    return {
        "ok": False,
        "results": [],
        "failure_details": [reason],
        "failure_hint": healthcheck.get("failure_hint") if isinstance(healthcheck, dict) else None,
    }


def skipped_healthcheck(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "status": "not-configured",
        "skipped": True,
        "results": [],
        "failure_details": [],
        "failure_hint": None,
    }


def detect_and_healthcheck(repo_root: Path, manifest: dict[str, Any], *, failure_reason: str) -> tuple[dict[str, Any], dict[str, Any]]:
    detect_result = run_check(manifest["checks"]["detect"], repo_root)
    healthcheck = manifest.get("checks", {}).get("healthcheck")
    healthcheck_result = (
        run_check(healthcheck, repo_root)
        if detect_result["ok"] and isinstance(healthcheck, dict)
        else skipped_healthcheck(manifest)
        if detect_result["ok"]
        else failed_healthcheck(manifest, reason=failure_reason)
    )
    return detect_result, healthcheck_result


def evaluate_readiness(manifest: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for check in manifest.get("readiness_checks", []):
        result = run_check(check, repo_root)
        checks.append({"check_id": check["check_id"], "summary": check["summary"], **result})
    return {
        "ok": all(check["ok"] for check in checks),
        "checks": checks,
        "failed_checks": [check["check_id"] for check in checks if not check["ok"]],
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


def healthcheck_attention_suffix(payload: dict[str, Any]) -> str:
    healthcheck = payload.get("healthcheck")
    if not isinstance(healthcheck, dict):
        return ""
    status = healthcheck.get("status")
    if isinstance(status, str) and status:
        return f" healthcheck={status}"
    if healthcheck.get("skipped") is True:
        return " healthcheck=skipped"
    return ""


def print_tool_statuses(results: list[dict[str, Any]], *, status_key: str = "status") -> None:
    for result in results:
        print(f"{result['tool_id']}: {result[status_key]}{healthcheck_attention_suffix(result)}")


def update_advisory_line(result: dict[str, Any]) -> str | None:
    advisory = result.get("update_advisory")
    if not isinstance(advisory, dict) or advisory.get("status") != "behind":
        return None
    detail = advisory.get("latest_tag") or advisory.get("latest_version")
    suffix = f" ({advisory['html_url']})" if advisory.get("html_url") else ""
    route = update_route_hint(result)
    return (
        f"{result['tool_id']}: update available — {advisory['observed_version']} installed, "
        f"{detail} latest; {route}{suffix}"
    )


def update_route_hint(result: dict[str, Any]) -> str:
    if result.get("mode") == "manual":
        docs_url = result.get("docs_url") or result.get("install_url")
        if docs_url:
            return f"manual update required; see {docs_url}"
        return "manual update required; use this tool's documented update route"

    install_route = result.get("install_route")
    if isinstance(install_route, dict) and install_route.get("mode") == "manual":
        docs_url = install_route.get("docs_url") or install_route.get("install_url")
        if docs_url:
            return f"manual update required; see {docs_url}"
        return "manual update required; use this tool's documented update route"

    commands = result.get("commands")
    if isinstance(commands, list) and commands and isinstance(commands[0], str):
        return f"run `{commands[0]}`"

    package_manager = result.get("package_manager")
    package_name = result.get("package_name")
    if isinstance(package_manager, str) and package_manager and isinstance(package_name, str) and package_name:
        return f"update `{package_name}` with {package_manager}"

    tool_id = result.get("tool_id")
    if isinstance(tool_id, str) and tool_id:
        return f"run `charness tool update {tool_id}` or use this tool's documented update route"
    return "use this tool's documented update route"


def print_update_advisories(results: list[dict[str, Any]], *, stream: Any = None) -> None:
    """Print a behind-latest advisory per tool so an advisory-policy manual tool does
    not silently lag. Written to stderr by default so JSON stdout stays clean."""
    out = stream if stream is not None else sys.stderr
    for result in results:
        line = update_advisory_line(result)
        if line:
            print(f"ADVISORY: {line}", file=out)


def has_any_status(results: list[dict[str, Any]], *, status_key: str, statuses: set[str]) -> bool:
    return any(result[status_key] in statuses for result in results)


def attach_release_metadata(result: dict[str, Any], *, provenance: dict[str, Any], release: dict[str, Any] | None) -> dict[str, Any]:
    result["provenance"] = provenance
    if release is not None:
        result["release"] = release
        version_block = result.get("version")
        observed = version_block.get("observed_version") if isinstance(version_block, dict) else None
        if not observed:
            observed = observed_version_from_detect(result.get("detect"))
        advisory = upgrade_advisory(observed, release)
        if advisory is not None:
            result["update_advisory"] = advisory
    return result
