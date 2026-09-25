"""External tool command runners."""

from __future__ import annotations

import argparse
import json
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
    AGENT_BROWSER_REPAIR_CAVEAT,
    BLOCKING_DOCTOR_DISPOSITIONS,
    REPAIRABLE_TOOL_IDS,
    CharnessError,
    default_plugin_root,
)
from scripts.cli.bootstrap_state import (  # noqa: E402
    resolve_tool_repo_root,
)
from scripts.cli.common import (  # noqa: E402
    emit_operational_response,
)
from scripts.cli.process import (  # noqa: E402
    _run_repo_json_command,
    invoke_repo_json_script,
    resolve_repo_python,
)
from scripts.cli.tool_next_steps import (  # noqa: E402
    tool_next_step,
)
from scripts.cli.tool_response import (  # noqa: E402
    project_tool_response,
    tool_ids_from_args,
    tool_result_map,
)
from scripts.cli.tool_update import (  # noqa: E402
    _mark_external_tool_update_failure as _mark_external_tool_update_failure,
)
from scripts.cli.tool_update import (  # noqa: E402
    _tool_update_lines as _tool_update_lines,
)
from scripts.cli.tool_update import (  # noqa: E402
    _tool_update_mode_suffix as _tool_update_mode_suffix,
)
from scripts.cli.tool_update import (  # noqa: E402
    print_tool_human_summary as print_tool_human_summary,
)
from scripts.cli.tool_update import (  # noqa: E402
    run_tool_update_flow as run_tool_update_flow,
)


def selected_tool_ids_from_args(args: argparse.Namespace, repo_root: Path) -> list[str]:
    explicit_tool_ids = tool_ids_from_args(args)
    recommend_for_skill = getattr(args, "recommend_for_skill", None)
    recommendation_role = getattr(args, "recommendation_role", None)
    next_skill_id = getattr(args, "next_skill_id", None)
    if not recommend_for_skill and not recommendation_role:
        return explicit_tool_ids
    if explicit_tool_ids:
        raise CharnessError("Pass either explicit tool ids or recommendation filters, not both.")
    selected: list[str] = []
    tools_dir = repo_root / "integrations" / "tools"
    for manifest_path in sorted(tools_dir.glob("*.json")):
        if manifest_path.name == "manifest.schema.json":
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        supported_skills = manifest.get("supports_public_skills", [])
        if recommendation_role and manifest.get("recommendation_role") != recommendation_role:
            continue
        skill_filter = recommend_for_skill or next_skill_id
        if skill_filter and skill_filter not in supported_skills:
            continue
        tool_id = manifest.get("tool_id")
        if isinstance(tool_id, str):
            selected.append(tool_id)
    if not selected:
        filters = []
        if recommend_for_skill:
            filters.append(f"--recommend-for-skill {recommend_for_skill}")
        if recommendation_role:
            filters.append(f"--recommendation-role {recommendation_role}")
        if next_skill_id:
            filters.append(f"--next-skill-id {next_skill_id}")
        raise CharnessError("No tools matched recommendation filters: " + " ".join(filters))
    return selected


def tool_selection_payload(
    args: argparse.Namespace, tool_ids: list[str]
) -> dict[str, object] | None:
    recommend_for_skill = getattr(args, "recommend_for_skill", None)
    recommendation_role = getattr(args, "recommendation_role", None)
    if not recommend_for_skill and not recommendation_role:
        return None
    return {
        "recommend_for_skill": recommend_for_skill,
        "recommendation_role": recommendation_role,
        "next_skill_id": getattr(args, "next_skill_id", None),
        "selected_tool_ids": tool_ids,
    }


def cmd_tool_doctor(args: argparse.Namespace) -> int:
    repo_root, managed_checkout = resolve_tool_repo_root(args)
    plugin_root = (
        args.plugin_root.resolve()
        if args.plugin_root
        else default_plugin_root(args.home_root.resolve())
    )
    script_args = ["--repo-root", str(repo_root), "--plugin-root", str(plugin_root)]
    for tool_id in tool_ids_from_args(args):
        script_args.extend(["--tool-id", tool_id])
    if not args.no_write_locks:
        script_args.append("--write-locks")
    doctor_results = invoke_repo_json_script(
        repo_root, "scripts/doctor.py", *script_args, allow_failure=True
    )
    payload = {
        "repo_root": str(repo_root),
        "managed_checkout": managed_checkout,
        "tool_ids": tool_ids_from_args(args),
        "results": {
            tool_id: {"doctor": result, "next_step": tool_next_step(tool_id, None, result, None)}
            for tool_id, result in tool_result_map(doctor_results).items()
        },
    }
    emit_operational_response(
        args,
        payload,
        event="tool-doctor",
        projector=lambda data: project_tool_response(data, event="tool-doctor"),
    )
    doctor_map = tool_result_map(doctor_results)
    if any(
        result.get("doctor_disposition") in BLOCKING_DOCTOR_DISPOSITIONS
        for result in doctor_map.values()
    ):
        return 1
    return 0


def _repair_agent_browser(
    repo_root: Path, plugin_root: Path, *, execute: bool
) -> dict[str, object]:
    python_executable = resolve_repo_python(repo_root)
    repair_command = [
        python_executable,
        "scripts/evidence/agent_browser_runtime_guard.py",
        "--repo-root",
        str(repo_root),
        "--cleanup-orphans",
    ]
    if execute:
        repair_command.append("--execute")
    repair_payload, repair_rc, repair_stderr = _run_repo_json_command(repo_root, repair_command)
    doctor_args = [
        "--repo-root",
        str(repo_root),
        "--plugin-root",
        str(plugin_root),
        "--tool-id",
        "agent-browser",
    ]
    if execute:
        doctor_args.append("--write-locks")
    doctor_results = invoke_repo_json_script(
        repo_root, "scripts/doctor.py", *doctor_args, allow_failure=True
    )
    doctor_result = tool_result_map(doctor_results).get("agent-browser")
    doctor_disposition = (
        doctor_result.get("doctor_disposition") if isinstance(doctor_result, dict) else None
    )
    repair_status = "executed" if execute else "preview"
    if execute and (repair_rc != 0 or doctor_disposition in BLOCKING_DOCTOR_DISPOSITIONS):
        repair_status = "failed"
    elif not execute and isinstance(repair_payload, dict) and repair_payload.get("target_pids"):
        repair_status = "would-repair"
    next_step = (
        f"Repair executed and post-doctor verification reports `agent-browser` ready. {AGENT_BROWSER_REPAIR_CAVEAT}"
        if execute and repair_status == "executed"
        else (
            "Run `charness tool repair --execute agent-browser` to remove owned "
            f"orphan daemon trees and refresh doctor state. {AGENT_BROWSER_REPAIR_CAVEAT}"
        )
        if not execute and repair_status == "would-repair"
        else f"{tool_next_step('agent-browser', None, doctor_result, None)} {AGENT_BROWSER_REPAIR_CAVEAT}"
        if isinstance(doctor_result, dict)
        else f"Inspect the repair payload and rerun `charness tool doctor agent-browser`. {AGENT_BROWSER_REPAIR_CAVEAT}"
    )
    return {
        "repair": {
            "status": repair_status,
            "execute": execute,
            "caveat": AGENT_BROWSER_REPAIR_CAVEAT,
            "command": " ".join(repair_command),
            "exit_code": repair_rc,
            "stderr": repair_stderr.strip(),
            "cleanup": repair_payload,
        },
        "doctor": doctor_result,
        "next_step": next_step,
    }


def cmd_tool_repair(args: argparse.Namespace) -> int:
    repo_root, managed_checkout = resolve_tool_repo_root(args)
    plugin_root = (
        args.plugin_root.resolve()
        if args.plugin_root
        else default_plugin_root(args.home_root.resolve())
    )
    selected_tool_ids = tool_ids_from_args(args) or sorted(REPAIRABLE_TOOL_IDS)
    results: dict[str, dict[str, object]] = {}
    failed = False
    for tool_id in selected_tool_ids:
        if tool_id not in REPAIRABLE_TOOL_IDS:
            failed = True
            results[tool_id] = {
                "repair": {
                    "status": "unsupported",
                    "execute": args.execute,
                    "cleanup": None,
                },
                "next_step": f"No repo-owned repair action is declared for `{tool_id}`. Run `charness tool doctor {tool_id}`.",
            }
            continue
        results[tool_id] = _repair_agent_browser(repo_root, plugin_root, execute=args.execute)
        repair = results[tool_id].get("repair")
        if isinstance(repair, dict) and repair.get("status") == "failed":
            failed = True
    payload = {
        "repo_root": str(repo_root),
        "managed_checkout": managed_checkout,
        "tool_ids": selected_tool_ids,
        "execute": args.execute,
        "results": results,
    }
    emit_operational_response(
        args,
        payload,
        event="tool-repair",
        projector=lambda data: project_tool_response(data, event="tool-repair"),
    )
    return 1 if failed else 0


def cmd_tool_sync_support(args: argparse.Namespace) -> int:
    repo_root, managed_checkout = resolve_tool_repo_root(args)
    plugin_root = (
        args.plugin_root.resolve()
        if args.plugin_root
        else default_plugin_root(args.home_root.resolve())
    )
    script_args = ["--repo-root", str(repo_root), "--plugin-root", str(plugin_root)]
    for tool_id in tool_ids_from_args(args):
        script_args.extend(["--tool-id", tool_id])
    for upstream_checkout in args.upstream_checkout:
        script_args.extend(["--upstream-checkout", upstream_checkout])
    if not args.dry_run:
        script_args.append("--execute")
    support_results = invoke_repo_json_script(
        repo_root, "scripts/sync_support.py", *script_args, allow_failure=True
    )
    doctor_args = ["--repo-root", str(repo_root), "--plugin-root", str(plugin_root)]
    for tool_id in tool_ids_from_args(args):
        doctor_args.extend(["--tool-id", tool_id])
    if not args.dry_run:
        doctor_args.append("--write-locks")
    doctor_results = invoke_repo_json_script(
        repo_root, "scripts/doctor.py", *doctor_args, allow_failure=True
    )
    support_map = tool_result_map(support_results)
    doctor_map = tool_result_map(doctor_results)
    payload = {
        "repo_root": str(repo_root),
        "managed_checkout": managed_checkout,
        "tool_ids": tool_ids_from_args(args),
        "results": {
            tool_id: {
                "support": support_map.get(tool_id),
                "doctor": doctor_map.get(tool_id),
                "next_step": tool_next_step(
                    tool_id, None, doctor_map.get(tool_id), support_map.get(tool_id)
                ),
            }
            for tool_id in sorted(set([*support_map.keys(), *doctor_map.keys()]))
        },
    }
    emit_operational_response(
        args,
        payload,
        event="tool-sync-support",
        projector=lambda data: project_tool_response(data, event="tool-sync-support"),
    )
    if any(
        isinstance(result, dict)
        and isinstance(result.get("doctor"), dict)
        and result["doctor"].get("doctor_disposition") in BLOCKING_DOCTOR_DISPOSITIONS
        for result in payload["results"].values()
    ):
        return 1
    return 0


def cmd_tool_install(args: argparse.Namespace) -> int:
    repo_root, managed_checkout = resolve_tool_repo_root(args)
    plugin_root = (
        args.plugin_root.resolve()
        if args.plugin_root
        else default_plugin_root(args.home_root.resolve())
    )
    selected_tool_ids = selected_tool_ids_from_args(args, repo_root)
    install_args = ["--repo-root", str(repo_root)]
    for tool_id in selected_tool_ids:
        install_args.extend(["--tool-id", tool_id])
    if not args.dry_run:
        install_args.append("--execute")
    install_results = invoke_repo_json_script(
        repo_root, "scripts/install_tools.py", *install_args, allow_failure=True
    )
    support_results: object = []
    if not args.skip_sync_support:
        support_args = ["--repo-root", str(repo_root), "--plugin-root", str(plugin_root)]
        for tool_id in selected_tool_ids:
            support_args.extend(["--tool-id", tool_id])
        for upstream_checkout in args.upstream_checkout:
            support_args.extend(["--upstream-checkout", upstream_checkout])
        if not args.dry_run:
            support_args.append("--execute")
        support_results = invoke_repo_json_script(
            repo_root, "scripts/sync_support.py", *support_args, allow_failure=True
        )
    doctor_args = ["--repo-root", str(repo_root), "--plugin-root", str(plugin_root)]
    for tool_id in selected_tool_ids:
        doctor_args.extend(["--tool-id", tool_id])
    if not args.dry_run:
        doctor_args.append("--write-locks")
    doctor_results = invoke_repo_json_script(
        repo_root, "scripts/doctor.py", *doctor_args, allow_failure=True
    )
    install_map = tool_result_map(install_results)
    support_map = tool_result_map(support_results)
    doctor_map = tool_result_map(doctor_results)
    payload = {
        "repo_root": str(repo_root),
        "managed_checkout": managed_checkout,
        "tool_ids": selected_tool_ids,
        "tool_selection": tool_selection_payload(args, selected_tool_ids),
        "results": {
            tool_id: {
                "install": install_map.get(tool_id),
                "support": support_map.get(tool_id),
                "doctor": doctor_map.get(tool_id),
                "next_step": tool_next_step(
                    tool_id,
                    install_map.get(tool_id),
                    doctor_map.get(tool_id),
                    support_map.get(tool_id),
                ),
            }
            for tool_id in sorted(
                set([*install_map.keys(), *support_map.keys(), *doctor_map.keys()])
            )
        },
    }
    emit_operational_response(
        args,
        payload,
        event="tool-install",
        projector=lambda data: project_tool_response(data, event="tool-install"),
    )
    if any(
        isinstance(result, dict)
        and isinstance(result.get("install"), dict)
        and result["install"].get("status") in {"failed", "installed-not-ready"}
        for result in payload["results"].values()
    ):
        return 1
    return 0


def cmd_tool_update(args: argparse.Namespace) -> int:
    repo_root, managed_checkout = resolve_tool_repo_root(args)
    plugin_root = (
        args.plugin_root.resolve()
        if args.plugin_root
        else default_plugin_root(args.home_root.resolve())
    )
    payload, failed = run_tool_update_flow(
        repo_root=repo_root,
        managed_checkout=managed_checkout,
        plugin_root=plugin_root,
        tool_ids=tool_ids_from_args(args),
        dry_run=args.dry_run,
        skip_sync_support=args.skip_sync_support,
        upstream_checkouts=args.upstream_checkout,
    )
    emit_operational_response(
        args,
        payload,
        event="tool-update",
        projector=lambda data: project_tool_response(data, event="tool-update"),
    )
    return 1 if failed else 0
