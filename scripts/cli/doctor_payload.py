"""Doctor payload builders and the install surface."""

from __future__ import annotations

import shutil
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
    PACKAGE_ID,
    default_codex_cache_root,
    default_install_state_path,
    has_source_manifest,
    packaging_version,
)
from scripts.cli.bootstrap_state import (  # noqa: E402
    build_version_provenance,
    default_version_state_path,
    git_head,
    read_version_state,
)
from scripts.cli.capability_support import (  # noqa: E402
    build_repo_onboarding_payload,
)
from scripts.cli.common import (  # noqa: E402
    default_claude_installed_plugins_path,
    default_claude_known_marketplaces_path,
    default_codex_config_path,
    default_grok_plugin_root,
    default_host_state_path,
    parse_repo_script_payload,
)
from scripts.cli.host_claude import (  # noqa: E402
    build_claude_host_guidance,
    build_grok_host_guidance,
    claude_enabled_status,
    claude_installed_plugin,
    claude_known_marketplace,
    claude_marketplace_name,
    claude_plugin_ref,
    ensure_claude_marketplace,
    ensure_claude_plugin,
    ensure_grok_plugin,
    install_cli_binary,
    wrapper_in_path,
    write_claude_wrapper,
)
from scripts.cli.host_codex import (  # noqa: E402
    build_codex_host_guidance,
    codex_cache_entries,
    codex_config_entries,
    codex_enabled_plugin_ids,
    codex_marketplace_entry,
    codex_primary_cache_entry,
    codex_source_manifest_path,
    codex_source_version,
)
from scripts.cli.install_delivery import (  # noqa: E402
    _latest_host_operation,
    build_host_next_steps,
)
from scripts.cli.process import (  # noqa: E402
    invoke_repo_json_script,
    invoke_repo_script,
)


def _mark_host_delivery_failure(
    doctor_payload: dict[str, object],
    delivery: dict[str, object],
    *,
    command: str,
    scope: str | None = None,
) -> None:
    reason = delivery.get("reason")
    reason_text = reason if isinstance(reason, str) and reason else "unknown"
    guidance = doctor_payload.get("codex_host_guidance")
    if not isinstance(guidance, dict):
        guidance = {}
    command_text = command if not scope or scope == "self" else f"{command} {scope}"
    guidance.update(
        {
            "status": "failed",
            "manual_action_required": True,
            "message": (
                f"Codex host delivery failed during `charness {command_text}` ({reason_text}). "
                f"Inspect the typed YAML result and retry with `charness {command_text} --detail`."
            ),
        }
    )
    doctor_payload["codex_host_guidance"] = guidance
    doctor_payload["host_next_steps"] = build_host_next_steps(doctor_payload)
    doctor_payload["next_action"] = build_doctor_next_action(doctor_payload)
    home_root = doctor_payload.get("home_root")
    repo_root = doctor_payload.get("repo_root")
    recovery_args = ["charness", command]
    if scope and scope != "self":
        recovery_args.append(scope)
    if isinstance(home_root, str) and home_root:
        recovery_args.extend(["--home-root", home_root])
    if isinstance(repo_root, str) and repo_root:
        recovery_args.extend(["--repo-root", repo_root])
    recovery_args.append("--detail")
    next_action = doctor_payload.get("next_action")
    if isinstance(next_action, dict):
        next_action["recovery_command_args"] = recovery_args
        next_action["recovery_context"] = {
            "home_root": home_root,
            "repo_root": repo_root,
            "codex_cache_root": doctor_payload.get("codex_cache_root"),
            "codex_marketplace_path": doctor_payload.get("codex_marketplace_path"),
        }


def build_doctor_next_action(doctor_payload: dict[str, object]) -> dict[str, object]:
    candidates: list[tuple[int, int, dict[str, object]]] = []
    for host_index, host in enumerate(("codex", "claude", "grok")):
        guidance = doctor_payload.get(f"{host}_host_guidance")
        if not isinstance(guidance, dict):
            continue
        message = guidance.get("message")
        status = guidance.get("status")
        if not isinstance(message, str) or not message:
            continue
        if not isinstance(status, str) or not status:
            status = "unknown"
        manual_action_required = guidance.get("manual_action_required") is True
        if manual_action_required:
            priority = 100
            kind = "manual"
        elif status == "installed":
            priority = 50
            kind = "restart"
        elif status in {"host-unavailable", "unavailable"}:
            priority = 0
            kind = "none"
        else:
            priority = 20
            kind = "inspect"
        candidates.append(
            (
                priority,
                -host_index,
                {
                    "kind": kind,
                    "host": host,
                    "status": status,
                    "manual_action_required": manual_action_required,
                    "message": message,
                    "source": f"{host}_host_guidance",
                },
            )
        )
    repo_onboarding = doctor_payload.get("repo_onboarding")
    if isinstance(repo_onboarding, dict):
        message = repo_onboarding.get("message")
        status = repo_onboarding.get("status")
        manual_action_required = repo_onboarding.get("manual_action_required") is True
        if isinstance(message, str) and message and manual_action_required and status == "required":
            candidates.append(
                (
                    40,
                    -10,
                    {
                        "kind": "repo-init",
                        "host": None,
                        "status": status,
                        "manual_action_required": True,
                        "message": message,
                        "source": "repo_onboarding",
                    },
                )
            )
    actionable = [candidate for candidate in candidates if candidate[0] > 0]
    if actionable:
        return max(actionable, key=lambda candidate: (candidate[0], candidate[1]))[2]
    return {
        "kind": "none",
        "host": None,
        "status": "no-action",
        "manual_action_required": False,
        "message": "No manual host action is currently required. See `host_next_steps` for host-specific status.",
        "source": "host_next_steps",
    }


def install_surface(
    repo_root: Path,
    *,
    home_root: Path,
    plugin_root: Path,
    codex_marketplace_path: Path,
    claude_wrapper_path: Path | None,
    cli_path: Path | None,
    update: bool,
) -> dict[str, object]:
    invoke_repo_script(
        repo_root, "scripts/plugin_export/validate_packaging.py", "--repo-root", str(repo_root)
    )
    invoke_repo_script(
        repo_root,
        "scripts/plugin_export/sync_root_plugin_manifests.py",
        "--repo-root",
        str(repo_root),
    )
    install_output = invoke_repo_script(
        repo_root,
        "scripts/install_machine_local.py",
        "--repo-root",
        str(repo_root),
        "--home-root",
        str(home_root),
        "--plugin-root",
        str(plugin_root),
        "--codex-marketplace-path",
        str(codex_marketplace_path),
    )
    payload = parse_repo_script_payload(install_output, "scripts/install_machine_local.py")
    completed_actions = ["codex_source_prepared", "codex_marketplace_registered"]
    support_sync_results = invoke_repo_json_script(
        repo_root,
        "scripts/sync_support.py",
        "--repo-root",
        str(repo_root),
        "--plugin-root",
        str(plugin_root),
        "--execute",
    )
    payload["support_sync"] = support_sync_results
    if isinstance(support_sync_results, list) and any(
        isinstance(item, dict) and item.get("status") == "synced" for item in support_sync_results
    ):
        completed_actions.append("upstream_support_skills_synced")
    if cli_path is not None:
        install_cli_binary(cli_path, source_path=repo_root / "charness")
        payload["cli_path"] = str(cli_path)
    else:
        payload["cli_path"] = None
    if claude_wrapper_path is not None:
        write_claude_wrapper(claude_wrapper_path, plugin_root)
        payload["claude_wrapper_path"] = str(claude_wrapper_path)
    else:
        payload["claude_wrapper_path"] = None
    claude_marketplace_actions, claude_marketplace_message = ensure_claude_marketplace(
        repo_root, home_root=home_root
    )
    claude_plugin_actions, claude_plugin_message = ensure_claude_plugin(
        repo_root, home_root=home_root, update=update
    )
    grok_plugin_actions, grok_plugin_message = ensure_grok_plugin(
        home_root=home_root, plugin_root=plugin_root
    )
    completed_actions.extend(claude_marketplace_actions)
    completed_actions.extend(claude_plugin_actions)
    completed_actions.extend(grok_plugin_actions)
    payload["completed_actions"] = completed_actions
    payload["host_next_steps"]["claude"] = claude_plugin_message
    payload["host_next_steps"]["grok"] = grok_plugin_message
    payload["claude_marketplace_message"] = claude_marketplace_message
    return payload


def _apply_latest_host_operation(payload: dict[str, object], *, home_root: Path) -> None:
    latest = _latest_host_operation(home_root)
    if latest is None:
        return
    key, entry = latest
    delivery = entry.get("delivery")
    latest_summary: dict[str, object] = {
        "key": key,
        "recorded_at": entry.get("recorded_at"),
        "operation_status": entry.get("operation_status"),
        "operation_scope": entry.get("operation_scope"),
        "delivery_status": entry.get("delivery_status"),
        "delivery_verified": entry.get("delivery_verified"),
    }
    if isinstance(delivery, dict):
        latest_summary["delivery_reason"] = delivery.get("reason")
        latest_summary["delivery_error"] = delivery.get("error")
    payload["latest_host_operation"] = latest_summary
    delivery_status = entry.get("delivery_status")
    delivery_failed = (
        delivery_status == "failed"
        or (isinstance(delivery, dict) and delivery.get("status") == "failed")
        or (
            entry.get("delivery_verified") is not True
            and delivery_status in {"attempted", "installed", "refreshed"}
        )
    )
    if not delivery_failed:
        return
    guidance = payload.get("codex_host_guidance")
    hosts = payload.get("hosts")
    if (
        not isinstance(guidance, dict)
        or not isinstance(hosts, dict)
        or hosts.get("codex") is not True
    ):
        return
    reason = (
        latest_summary.get("delivery_reason")
        or latest_summary.get("delivery_status")
        or "unverified"
    )
    scope = entry.get("operation_scope")
    command = "update all" if scope == "all" else "update"
    guidance.update(
        {
            "status": "failed",
            "manual_action_required": True,
            "reason": "latest-operation-failed",
            "message": (
                f"The latest Codex host operation (`charness {command}`) is not verified ({reason}). "
                "Do not treat the cache as installed; inspect `charness doctor --detail` and retry the recorded recovery command."
            ),
        }
    )
    payload["codex_host_guidance"] = guidance
    payload["host_next_steps"] = build_host_next_steps(payload)
    payload["next_action"] = build_doctor_next_action(payload)


def build_doctor_payload(
    *,
    home_root: Path,
    repo_root: Path,
    managed_checkout: bool,
    target_repo_root: Path,
    plugin_root: Path,
    codex_marketplace_path: Path,
    cli_path: Path,
    claude_wrapper_path: Path,
    include_repo_onboarding: bool = True,
    include_latest_host_operation: bool = True,
) -> dict[str, object]:
    source_manifest_present = has_source_manifest(repo_root)
    version_provenance = build_version_provenance(
        home_root=home_root,
        repo_root=repo_root,
        managed_checkout=managed_checkout,
        cli_path=cli_path,
    )
    version_state = read_version_state(home_root)
    payload: dict[str, object] = {
        "package_id": PACKAGE_ID,
        "home_root": str(home_root),
        "repo_root": str(repo_root),
        "managed_checkout": managed_checkout,
        "target_repo_root": str(target_repo_root),
        "install_state_path": str(default_install_state_path(home_root)),
        "host_state_path": str(default_host_state_path(home_root)),
        "version_state_path": str(default_version_state_path(home_root)),
        "checkout_present": source_manifest_present,
        "checkout_git_head": git_head(repo_root) if source_manifest_present else None,
        "checkout_version": packaging_version(repo_root) if source_manifest_present else None,
        "version_provenance": version_provenance,
        "latest_release_check": version_state.get("latest_release"),
        "plugin_root": str(plugin_root),
        "plugin_root_present": plugin_root.is_dir(),
        "codex_marketplace_path": str(codex_marketplace_path),
        "codex_marketplace_entry": codex_marketplace_entry(codex_marketplace_path),
        "codex_source_manifest_path": str(codex_source_manifest_path(plugin_root)),
        "codex_source_version": codex_source_version(plugin_root),
        "codex_config_path": str(default_codex_config_path(home_root)),
        "codex_config_entries": codex_config_entries(default_codex_config_path(home_root)),
        "codex_cache_root": str(default_codex_cache_root(home_root)),
        "codex_cache_entries": codex_cache_entries(default_codex_cache_root(home_root)),
        "cli_path": str(cli_path),
        "cli_present": cli_path.is_file(),
        "cli_in_path": wrapper_in_path(cli_path),
        "claude_wrapper_path": str(claude_wrapper_path),
        "claude_wrapper_present": claude_wrapper_path.is_file(),
        "claude_wrapper_in_path": wrapper_in_path(claude_wrapper_path),
        "claude_known_marketplaces_path": str(default_claude_known_marketplaces_path(home_root)),
        "claude_installed_plugins_path": str(default_claude_installed_plugins_path(home_root)),
        "hosts": {
            "codex": shutil.which("codex") is not None,
            "claude": shutil.which("claude") is not None,
            "grok": shutil.which("grok") is not None,
        },
        "grok_plugin_root": str(default_grok_plugin_root(home_root)),
        "grok_plugin_root_present": default_grok_plugin_root(home_root).is_dir(),
    }
    payload["claude_marketplace_name"] = (
        claude_marketplace_name(repo_root) if source_manifest_present else None
    )
    payload["claude_plugin_ref"] = claude_plugin_ref(repo_root) if source_manifest_present else None
    payload["claude_marketplace_entry"] = (
        claude_known_marketplace(
            default_claude_known_marketplaces_path(home_root), payload["claude_marketplace_name"]
        )
        if payload["claude_marketplace_name"]
        else None
    )
    payload["claude_enabled_status"] = (
        claude_enabled_status(repo_root, home_root=home_root) if source_manifest_present else None
    )
    claude_listed = (
        payload["claude_enabled_status"].get("present")
        if isinstance(payload.get("claude_enabled_status"), dict)
        else False
    )
    payload["claude_installed_entry"] = (
        claude_installed_plugin(
            default_claude_installed_plugins_path(home_root), payload["claude_plugin_ref"]
        )
        if payload["claude_plugin_ref"] and claude_listed
        else None
    )
    if source_manifest_present:
        preamble_output = invoke_repo_script(
            repo_root,
            "scripts/plugin_export/plugin_preamble.py",
            "--repo-root",
            str(repo_root),
            "--consumer-root",
            str(home_root),
        )
        payload["plugin_preamble"] = parse_repo_script_payload(
            preamble_output, "scripts/plugin_export/plugin_preamble.py"
        )
    else:
        payload["plugin_preamble"] = None
    payload["codex_enabled_plugin_ids"] = codex_enabled_plugin_ids(payload["codex_config_entries"])
    primary_cache, primary_plugin_id = codex_primary_cache_entry(
        payload["codex_cache_entries"],
        enabled_plugin_ids=payload["codex_enabled_plugin_ids"],
        source_version=payload["codex_source_version"],
    )
    payload["codex_cache_manifest_version"] = (
        primary_cache.get("manifest_version") if isinstance(primary_cache, dict) else None
    )
    payload["codex_cache_manifest_status"] = (
        primary_cache.get("manifest_status")
        if isinstance(primary_cache, dict)
        and primary_cache.get("manifest_status") in {"valid", "invalid"}
        else (
            "valid"
            if payload["codex_cache_manifest_version"]
            else "invalid"
            if primary_cache
            else None
        )
    )
    payload["codex_enabled_plugin_id"] = primary_plugin_id
    payload["codex_source_cache_drift"] = bool(
        payload["codex_source_version"]
        and payload["codex_cache_manifest_version"]
        and payload["codex_source_version"] != payload["codex_cache_manifest_version"]
    )
    payload["codex_host_guidance"] = build_codex_host_guidance(
        codex_available=payload["hosts"]["codex"],
        codex_marketplace_path=codex_marketplace_path,
        source_version=payload["codex_source_version"],
        cache_entries=payload["codex_cache_entries"],
        config_entries=payload["codex_config_entries"],
    )
    payload["claude_host_guidance"] = build_claude_host_guidance(
        repo_root=repo_root,
        home_root=home_root,
        source_manifest_present=source_manifest_present,
        marketplace_entry=payload["claude_marketplace_entry"],
        installed_entry=payload["claude_installed_entry"],
        enabled_status=payload["claude_enabled_status"],
    )
    payload["grok_host_guidance"] = build_grok_host_guidance(
        grok_available=payload["hosts"]["grok"],
        grok_plugin_root=default_grok_plugin_root(home_root),
    )
    if include_repo_onboarding:
        payload["repo_onboarding"] = build_repo_onboarding_payload(
            source_repo_root=repo_root,
            target_repo_root=target_repo_root,
        )
    else:
        payload["repo_onboarding"] = {
            "target_repo_root": str(target_repo_root),
            "status": "skipped",
            "manual_action_required": False,
            "message": None,
            "source": "repo_onboarding",
            "reason": "skipped during update unless --target-repo-root is provided",
        }
    payload["host_next_steps"] = build_host_next_steps(payload)
    payload["next_action"] = build_doctor_next_action(payload)
    if include_latest_host_operation:
        _apply_latest_host_operation(payload, home_root=home_root)
    return payload
