"""External tool update flow (#873).

Split from tool_commands.py: update-mode suffix/lines, failure marking,
the shared update flow runner, and the human summary printer.
"""

from __future__ import annotations

from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.cli.bootstrap import (  # noqa: E402
    emit_progress,
)
from scripts.cli.cmd_meta import (  # noqa: E402
    _version_transition_suffix,
)
from scripts.cli.process import (  # noqa: E402
    invoke_repo_json_script,
)
from scripts.cli.tool_next_steps import (  # noqa: E402
    _healthcheck_attention_suffix,
    tool_next_step,
)
from scripts.cli.tool_response import (  # noqa: E402
    _print_tool_result_block,
    _tool_result_failure_phases,
    tool_result_map,
)


def _mark_external_tool_update_failure(payload: dict[str, object], *, scope: str) -> None:
    tool_update = payload.get("tool_update")
    if not isinstance(tool_update, dict):
        return
    results = tool_update.get("results")
    failed_tool_ids: list[str] = []
    failure_phases: dict[str, list[str]] = {}
    if isinstance(results, dict):
        for tool_id, result in results.items():
            if not isinstance(tool_id, str) or not isinstance(result, dict):
                continue
            failed_for_tool = _tool_result_failure_phases(result)
            if failed_for_tool:
                failed_tool_ids.append(tool_id)
                failure_phases[tool_id] = failed_for_tool
    failed_tool_ids.sort()
    tool_update["status"] = "failed"
    tool_update["failure_scope"] = scope
    tool_update["failed_tool_ids"] = failed_tool_ids
    tool_update["failure_phases"] = {
        tool_id: failure_phases[tool_id] for tool_id in failed_tool_ids
    }
    command = "charness update all --detail" if scope == "all" else "charness update --detail"
    message = f"External tool update failed for scope `{scope}`. Inspect the typed YAML result and retry with `{command}`."
    host_next_steps = payload.get("host_next_steps")
    if not isinstance(host_next_steps, dict):
        host_next_steps = {}
        payload["host_next_steps"] = host_next_steps
    host_next_steps["external-tools"] = message
    next_action = payload.get("next_action")
    if not isinstance(next_action, dict):
        next_action = {
            "kind": "manual",
            "host": "external-tools",
            "status": "failed",
            "manual_action_required": True,
            "message": message,
        }
        payload["next_action"] = next_action
    else:
        existing_message = next_action.get("message")
        next_action["message"] = (
            f"{existing_message} Also, {message}"
            if isinstance(existing_message, str) and existing_message
            else message
        )
        next_action["kind"] = "manual"
        next_action["status"] = "failed"
        next_action["manual_action_required"] = True
    next_action["scope"] = scope
    next_action["recovery_command"] = command
    next_action["failed_tool_ids"] = failed_tool_ids
    home_root = payload.get("home_root")
    repo_root = payload.get("repo_root")
    recovery_args = ["charness", "update"]
    if scope != "self":
        recovery_args.append(scope)
    if isinstance(home_root, str) and home_root:
        recovery_args.extend(["--home-root", home_root])
    if isinstance(repo_root, str) and repo_root:
        recovery_args.extend(["--repo-root", repo_root])
    recovery_args.append("--detail")
    next_action["recovery_command_args"] = recovery_args
    next_action["recovery_context"] = {"home_root": home_root, "repo_root": repo_root}


def _tool_update_mode_suffix(update: dict[str, object] | None) -> str:
    if not isinstance(update, dict):
        return ""
    mode = update.get("mode")
    if mode == "script":
        return " (script)"
    if mode == "package_manager":
        package_manager = update.get("package_manager")
        package_name = update.get("package_name")
        if (
            isinstance(package_manager, str)
            and package_manager
            and isinstance(package_name, str)
            and package_name
        ):
            return f" ({package_manager}: {package_name})"
    return ""


def _tool_update_lines(payload: dict[str, object]) -> list[str]:
    results = payload.get("results")
    if not isinstance(results, dict) or not results:
        return []
    lines: list[str] = []
    for tool_id in sorted(results):
        result = results.get(tool_id)
        if not isinstance(result, dict):
            continue
        status = None
        update = result.get("update")
        if isinstance(update, dict) and isinstance(update.get("status"), str):
            status = update["status"]
        doctor = result.get("doctor")
        if (
            status is None
            and isinstance(doctor, dict)
            and isinstance(doctor.get("doctor_status"), str)
        ):
            status = doctor["doctor_status"]
        support = result.get("support")
        if status is None and isinstance(support, dict) and isinstance(support.get("status"), str):
            status = support["status"]
        status = status or "unknown"
        update = update if isinstance(update, dict) else None
        version_suffix = _version_transition_suffix(update, status)
        mode_suffix = _tool_update_mode_suffix(update)
        healthcheck_suffix = ""
        if isinstance(update, dict):
            healthcheck_suffix = _healthcheck_attention_suffix(update)
        if not healthcheck_suffix and isinstance(doctor, dict):
            healthcheck_suffix = _healthcheck_attention_suffix(doctor)
        lines.append(f"  - {tool_id}: {status}{version_suffix}{mode_suffix}{healthcheck_suffix}")
    return lines


def run_tool_update_flow(
    *,
    repo_root: Path,
    managed_checkout: bool,
    plugin_root: Path,
    tool_ids: list[str],
    dry_run: bool,
    skip_sync_support: bool,
    upstream_checkouts: list[str],
    precomputed_support_results: object | None = None,
) -> tuple[dict[str, object], bool]:
    emit_progress("STEP: updating tracked external tools")
    update_args = ["--repo-root", str(repo_root)]
    for tool_id in tool_ids:
        update_args.extend(["--tool-id", tool_id])
    if not dry_run:
        update_args.append("--execute")
    update_results = invoke_repo_json_script(
        repo_root, "scripts/update_tools.py", *update_args, allow_failure=True
    )
    support_results: object = []
    if not skip_sync_support:
        emit_progress("STEP: syncing support surfaces")
        can_reuse_support = (
            precomputed_support_results is not None
            and not dry_run
            and not tool_ids
            and not upstream_checkouts
        )
        if can_reuse_support:
            support_results = precomputed_support_results
        else:
            support_args = ["--repo-root", str(repo_root), "--plugin-root", str(plugin_root)]
            for tool_id in tool_ids:
                support_args.extend(["--tool-id", tool_id])
            for upstream_checkout in upstream_checkouts:
                support_args.extend(["--upstream-checkout", upstream_checkout])
            if not dry_run:
                support_args.append("--execute")
            support_results = invoke_repo_json_script(
                repo_root, "scripts/sync_support.py", *support_args, allow_failure=True
            )
    emit_progress("STEP: refreshing tool doctor state")
    doctor_args = ["--repo-root", str(repo_root), "--plugin-root", str(plugin_root)]
    for tool_id in tool_ids:
        doctor_args.extend(["--tool-id", tool_id])
    if not dry_run:
        doctor_args.append("--write-locks")
    doctor_results = invoke_repo_json_script(
        repo_root, "scripts/doctor.py", *doctor_args, allow_failure=True
    )
    update_map = tool_result_map(update_results)
    support_map = tool_result_map(support_results)
    doctor_map = tool_result_map(doctor_results)
    result_payloads: dict[str, dict[str, object]] = {
        tool_id: {
            "update": update_map.get(tool_id),
            "support": support_map.get(tool_id),
            "doctor": doctor_map.get(tool_id),
            "next_step": tool_next_step(
                tool_id, update_map.get(tool_id), doctor_map.get(tool_id), support_map.get(tool_id)
            ),
        }
        for tool_id in sorted(set([*update_map.keys(), *support_map.keys(), *doctor_map.keys()]))
    }
    payload = {
        "repo_root": str(repo_root),
        "managed_checkout": managed_checkout,
        "tool_ids": tool_ids,
        "results": result_payloads,
    }
    failed_tool_ids: list[str] = []
    failure_phases: dict[str, list[str]] = {}
    for tool_id, result in result_payloads.items():
        phases = _tool_result_failure_phases(result)
        if phases:
            failed_tool_ids.append(tool_id)
            failure_phases[tool_id] = phases
    failed_tool_ids.sort()
    failed = bool(failed_tool_ids)
    payload["failed_tool_ids"] = failed_tool_ids
    payload["failure_phases"] = {tool_id: failure_phases[tool_id] for tool_id in failed_tool_ids}
    return payload, failed


def print_tool_human_summary(payload: dict[str, object]) -> None:
    print(f"REPO_ROOT: {payload['repo_root']}")
    print(f"MANAGED_CHECKOUT: {'yes' if payload['managed_checkout'] else 'no'}")
    tool_ids = payload.get("tool_ids", [])
    if isinstance(tool_ids, list):
        print(f"TOOLS: {', '.join(tool_ids) if tool_ids else 'all'}")
    results = payload.get("results", {})
    if not isinstance(results, dict):
        return
    for tool_id, result in results.items():
        if not isinstance(result, dict):
            continue
        _print_tool_result_block(tool_id, result)
