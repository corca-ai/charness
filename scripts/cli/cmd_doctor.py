"""Doctor command and payload builders."""

from __future__ import annotations

import argparse


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.cli.bootstrap import (  # noqa: E402
    resolve_repo_root,
    resolve_runtime_paths,
    resolve_target_repo_root,
)
from scripts.cli.bootstrap_state import (  # noqa: E402
    emit_yaml,
)
from scripts.cli.cmd_task import (  # noqa: E402
    project_runtime_response,
)
from scripts.cli.common import (  # noqa: E402
    emit_operational_response,
)
from scripts.cli.doctor_payload import (  # noqa: E402
    build_doctor_payload,
)
from scripts.cli.install_delivery import (  # noqa: E402
    write_host_state,
)


def _print_latest_release(latest_release: object) -> None:
    if not isinstance(latest_release, dict):
        return
    latest_tag = latest_release.get("latest_tag") or latest_release.get("latest_version")
    latest_status = latest_release.get("status")
    if latest_tag:
        print(f"LATEST_RELEASE: {latest_status} {latest_tag}")
    else:
        print(f"LATEST_RELEASE: {latest_status}")


def _print_codex_marketplace(payload: dict[str, object]) -> None:
    entry = payload.get("codex_marketplace_entry")
    if isinstance(entry, dict):
        source = entry.get("source", {})
        path = source.get("path") if isinstance(source, dict) else None
        print(f"CODEX_MARKETPLACE: present {payload['codex_marketplace_path']} -> {path}")
        return
    print(f"CODEX_MARKETPLACE: missing-entry {payload['codex_marketplace_path']}")


def _print_codex_cache(payload: dict[str, object]) -> None:
    cache_entries = payload.get("codex_cache_entries")
    if isinstance(cache_entries, list) and cache_entries:
        versions = ", ".join(
            f"{entry['marketplace']}:{entry['version']} manifest={entry.get('manifest_version') or 'unknown'}"
            for entry in cache_entries
            if isinstance(entry, dict) and "marketplace" in entry and "version" in entry
        )
        print(f"CODEX_CACHE: present {versions}")
    else:
        print(f"CODEX_CACHE: missing {payload['codex_cache_root']}")
    if payload.get("codex_cache_manifest_version"):
        print(f"CODEX_CACHE_VERSION: {payload['codex_cache_manifest_version']}")
    print(f"CODEX_SOURCE_CACHE_DRIFT: {'yes' if payload.get('codex_source_cache_drift') else 'no'}")


def _print_codex_config(payload: dict[str, object]) -> None:
    config_entries = payload.get("codex_config_entries")
    if isinstance(config_entries, list) and config_entries:
        details = ", ".join(
            f"{entry['plugin_id']} enabled={entry['enabled']}"
            for entry in config_entries
            if isinstance(entry, dict) and "plugin_id" in entry and "enabled" in entry
        )
        print(f"CODEX_CONFIG: present {details}")
        return
    print(f"CODEX_CONFIG: missing-entry {payload['codex_config_path']}")


def _print_claude_install_surface(payload: dict[str, object]) -> None:
    print(f"CLI: {'present' if payload['cli_present'] else 'missing'} {payload['cli_path']}")
    print(f"CLI_IN_PATH: {'yes' if payload['cli_in_path'] else 'no'}")
    print(
        f"CLAUDE_WRAPPER: {'present' if payload['claude_wrapper_present'] else 'missing'} {payload['claude_wrapper_path']}"
    )
    print(f"CLAUDE_WRAPPER_IN_PATH: {'yes' if payload['claude_wrapper_in_path'] else 'no'}")
    claude_marketplace_entry = payload.get("claude_marketplace_entry")
    if isinstance(claude_marketplace_entry, dict):
        print(
            f"CLAUDE_MARKETPLACE: present {payload['claude_known_marketplaces_path']} -> {payload['claude_marketplace_name']}"
        )
    else:
        print(f"CLAUDE_MARKETPLACE: missing-entry {payload['claude_known_marketplaces_path']}")
    claude_installed_entry = payload.get("claude_installed_entry")
    if isinstance(claude_installed_entry, dict):
        install_path = claude_installed_entry.get("installPath")
        print(f"CLAUDE_PLUGIN: present {payload['claude_plugin_ref']} -> {install_path}")
    else:
        print(f"CLAUDE_PLUGIN: missing-entry {payload['claude_installed_plugins_path']}")


def cmd_doctor(args: argparse.Namespace) -> int:
    home_root = args.home_root.resolve()
    repo_root, managed_checkout = resolve_repo_root(home_root, args.repo_root)
    target_repo_root = resolve_target_repo_root(args.target_repo_root)
    plugin_root, codex_marketplace_path, claude_wrapper_path, cli_path = resolve_runtime_paths(args)
    payload = build_doctor_payload(
        home_root=home_root,
        repo_root=repo_root,
        managed_checkout=managed_checkout,
        target_repo_root=target_repo_root,
        plugin_root=plugin_root,
        codex_marketplace_path=codex_marketplace_path,
        cli_path=cli_path,
        claude_wrapper_path=claude_wrapper_path,
    )
    if args.write_state:
        write_host_state(home_root, key="last_doctor", payload=payload)
    if args.next_action:
        next_action = payload.get("next_action")
        message = next_action.get("message") if isinstance(next_action, dict) else None
        emit_yaml(
            {
                "next_action": message
                if isinstance(message, str) and message
                else "No manual host action is currently required."
            }
        )
    else:
        emit_operational_response(
            args,
            payload,
            event="doctor",
            projector=lambda data: project_runtime_response(data, event="doctor"),
        )
    return 0
