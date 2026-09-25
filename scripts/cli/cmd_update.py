"""Update command and its finalize phases."""

from __future__ import annotations

import argparse
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
    default_codex_cache_root,
    emit_progress,
    managed_checkout_root,
)
from scripts.cli.bootstrap_state import (  # noqa: E402
    build_version_provenance,
    compute_update_available,
    write_version_state,
)
from scripts.cli.cmd_doctor import (  # noqa: E402
    _print_claude_install_surface,
    _print_codex_cache,
    _print_codex_config,
    _print_codex_marketplace,
    _print_latest_release,
)
from scripts.cli.cmd_task import (  # noqa: E402
    project_runtime_response,
)
from scripts.cli.common import (  # noqa: E402
    emit_operational_response,
)
from scripts.cli.doctor_payload import (  # noqa: E402
    _mark_host_delivery_failure,
    build_doctor_payload,
    install_surface,
)
from scripts.cli.host_codex import (  # noqa: E402
    _codex_cache_entries,
    _record_post_delivery_readback,
    maybe_install_codex_host,
)
from scripts.cli.install_delivery import (  # noqa: E402
    _host_delivery_failed,
    write_host_state,
    write_install_state,
)
from scripts.cli.tool_commands import (  # noqa: E402
    _mark_external_tool_update_failure,
    _tool_update_lines,
    run_tool_update_flow,
)


def latest_release_for_current_version(
    latest_release: object, current_version: str | None
) -> dict[str, object] | None:
    if not isinstance(latest_release, dict):
        return None
    payload = dict(latest_release)
    payload["current_version"] = current_version
    payload["update_available"] = compute_update_available(
        current_version, payload.get("latest_version")
    )
    return payload


def codex_all_plugin_cache_entries(cache_root: Path) -> list[dict[str, str]]:
    return _codex_cache_entries(cache_root, plugin_glob="*")


def diff_cache_entries(
    before: list[dict[str, str]],
    after: list[dict[str, str]],
) -> dict[str, list[dict[str, str]]]:
    after_by_pair: dict[tuple[str, str], list[dict[str, str]]] = {}
    for entry in after:
        key = (entry.get("marketplace") or "", entry.get("plugin") or "")
        after_by_pair.setdefault(key, []).append(entry)
    removed: list[dict[str, str]] = []
    rotated: list[dict[str, str]] = []
    for entry in before:
        version_dir = entry.get("version_dir") or ""
        if version_dir and Path(version_dir).is_dir():
            continue
        key = (entry.get("marketplace") or "", entry.get("plugin") or "")
        successors = [
            successor
            for successor in after_by_pair.get(key, [])
            if successor.get("version_dir") != version_dir
        ]
        record = {
            "marketplace": entry.get("marketplace") or "",
            "plugin": entry.get("plugin") or "",
            "old_version": entry.get("version") or "",
            "old_version_dir": version_dir,
        }
        if successors:
            successor = successors[0]
            record["new_version"] = successor.get("version") or ""
            record["new_version_dir"] = successor.get("version_dir") or ""
            rotated.append(record)
        else:
            removed.append(record)
    before_dirs = {entry.get("version_dir") for entry in before}
    added = [
        {
            "marketplace": entry.get("marketplace") or "",
            "plugin": entry.get("plugin") or "",
            "version": entry.get("version") or "",
            "version_dir": entry.get("version_dir") or "",
        }
        for entry in after
        if entry.get("version_dir") not in before_dirs
    ]
    return {"rotated": rotated, "removed": removed, "added": added}


def session_staleness_payload(
    cache_diff: dict[str, list[dict[str, str]]],
    *,
    home_root: Path,
    repo_root: Path,
) -> dict[str, object] | None:
    rotated = cache_diff.get("rotated") or []
    removed = cache_diff.get("removed") or []
    if not rotated and not removed:
        return None
    resolver_path = repo_root / "scripts" / "adapters" / "capability_catalog.py"
    fallback_resolver_path = (
        managed_checkout_root(home_root) / "scripts" / "adapters" / "capability_catalog.py"
    )
    resolver = str(resolver_path if resolver_path.is_file() else fallback_resolver_path)
    affected = [
        f"{record.get('marketplace')}/{record.get('plugin')} {record.get('old_version')} -> {record.get('new_version', '(removed)')}"
        for record in [*rotated, *removed]
    ]
    return {
        "rotated": rotated,
        "removed": removed,
        "affected": affected,
        "message": (
            "Updated plugin caches were rotated. Active Codex/Claude sessions may have stale absolute skill paths "
            "injected into their system prompt. Restart those sessions, or re-resolve a stale charness skill path with "
            f"`python3 {resolver} resolve-skill-path --repo-root <repo> --skill-id <id> --reported-path <stale> "
            "[--marketplace <m> --plugin <p>]`."
        ),
        "resolver_path": resolver,
    }


def _print_next_actions(payload: dict[str, object]) -> None:
    preamble = payload.get("plugin_preamble")
    if isinstance(preamble, dict):
        root_surface = preamble.get("root_install_surface", {})
        ok = root_surface.get("ok")
        print(f"INSTALL_SURFACE: {'ok' if ok else 'warning'}")
    candidates: list[tuple[str | None, str]] = []
    next_action = payload.get("next_action")
    if isinstance(next_action, dict) and isinstance(next_action.get("message"), str):
        host = next_action.get("host")
        label = host if isinstance(host, str) and host else None
        if label is None and next_action.get("source") == "repo_onboarding":
            label = "repo"
        candidates.append((label, next_action["message"]))
    host_guidance = payload.get("codex_host_guidance")
    if isinstance(host_guidance, dict) and isinstance(host_guidance.get("message"), str):
        candidates.append(("codex", host_guidance["message"]))
    claude_guidance = payload.get("claude_host_guidance")
    if isinstance(claude_guidance, dict) and isinstance(claude_guidance.get("message"), str):
        candidates.append(("claude", claude_guidance["message"]))
    repo_onboarding = payload.get("repo_onboarding")
    if isinstance(repo_onboarding, dict) and isinstance(repo_onboarding.get("message"), str):
        candidates.append(("repo", repo_onboarding["message"]))
    seen_messages: set[str] = set()
    lines: list[str] = []
    for label, message in candidates:
        if message in seen_messages:
            continue
        seen_messages.add(message)
        prefix = f"{label}: " if label else ""
        lines.append(f"  - {prefix}{message}")
    if not lines:
        return
    print("NEXT:")
    for line in lines:
        print(line)


def print_human_summary(payload: dict[str, object]) -> None:
    print(f"PACKAGE: {payload['package_id']}")
    print(
        f"CHECKOUT: {'present' if payload['checkout_present'] else 'missing'} {payload['repo_root']}"
    )
    if payload.get("checkout_version"):
        print(f"VERSION: {payload['checkout_version']}")
    if payload.get("checkout_git_head"):
        print(f"GIT_HEAD: {payload['checkout_git_head']}")
    version_provenance = payload.get("version_provenance")
    if isinstance(version_provenance, dict):
        print(
            "VERSION_PROVENANCE: "
            f"{version_provenance.get('invocation_kind')} "
            f"{version_provenance.get('install_method') or ''}".rstrip()
        )
    _print_latest_release(payload.get("latest_release_check"))
    print(
        f"PLUGIN_ROOT: {'present' if payload['plugin_root_present'] else 'missing'} {payload['plugin_root']}"
    )
    if payload.get("codex_source_version"):
        print(f"CODEX_SOURCE_VERSION: {payload['codex_source_version']}")
    _print_codex_marketplace(payload)
    _print_codex_cache(payload)
    _print_codex_config(payload)
    _print_claude_install_surface(payload)
    _print_next_actions(payload)


def print_update_human_summary(payload: dict[str, object]) -> None:
    print(f"PACKAGE: {payload['package_id']}")
    previous_version = payload.get("previous_checkout_version")
    current_version = payload.get("checkout_version")
    if (
        isinstance(previous_version, str)
        and previous_version
        and previous_version != current_version
    ):
        print(f"VERSION: {previous_version} -> {current_version}")
    elif isinstance(current_version, str) and current_version:
        print(f"VERSION: {current_version}")
    checkout = payload.get("checkout")
    if isinstance(checkout, dict):
        state = "pulled" if checkout.get("pulled") else "current"
        print(f"CHECKOUT: {state} {checkout.get('repo_root')}")
    if payload.get("checkout_git_head"):
        print(f"GIT_HEAD: {payload['checkout_git_head']}")
    if payload.get("scope"):
        print(f"SCOPE: {payload['scope']}")
    completed_actions = payload.get("completed_actions")
    if isinstance(completed_actions, list) and completed_actions:
        print(f"COMPLETED: {', '.join(str(action) for action in completed_actions)}")
    _print_latest_release(payload.get("latest_release_check"))
    tool_update = payload.get("tool_update")
    if isinstance(tool_update, dict):
        lines = _tool_update_lines(tool_update)
        if lines:
            print("TOOLS:")
            for line in lines:
                print(line)
    _print_session_staleness(payload.get("session_staleness"))
    _print_next_actions(payload)


def _print_session_staleness(session_staleness: object) -> None:
    if not isinstance(session_staleness, dict):
        return
    affected = session_staleness.get("affected")
    message = session_staleness.get("message")
    if not isinstance(affected, list) or not affected:
        return
    print("SESSION_STALENESS: cache paths rotated for active sessions")
    for line in affected:
        print(f"  - {line}")
    if isinstance(message, str) and message:
        print(f"  -> {message}")


def finish_update(
    args: argparse.Namespace,
    *,
    home_root: Path,
    managed_checkout: bool,
    target_repo_root: Path,
    include_repo_onboarding: bool,
    previous_checkout_version: str | None,
    plugin_root: Path,
    codex_marketplace_path: Path,
    claude_wrapper_path: Path,
    cli_path: Path,
    checkout: dict[str, object],
    cli_reexec_state: dict[str, object] | None,
) -> int:
    # Snapshot before the refresh below mutates install state (home codex
    # cache is checkout-independent, so this can live in phase 2).
    pre_update_cache_entries = codex_all_plugin_cache_entries(default_codex_cache_root(home_root))
    emit_progress("STEP: refreshing install surface")
    selected_wrapper_path = None if args.skip_claude_wrapper else claude_wrapper_path
    payload = install_surface(
        Path(checkout["repo_root"]),
        home_root=home_root,
        plugin_root=plugin_root,
        codex_marketplace_path=codex_marketplace_path,
        claude_wrapper_path=selected_wrapper_path,
        cli_path=None if args.skip_cli_install else cli_path,
        update=True,
    )
    payload["home_root"] = str(home_root)
    payload["repo_root"] = str(Path(checkout["repo_root"]))
    if cli_reexec_state is not None:
        payload["cli_reexec"] = cli_reexec_state
    payload["previous_checkout_version"] = previous_checkout_version
    initial_doctor_payload = build_doctor_payload(
        home_root=home_root,
        repo_root=Path(checkout["repo_root"]),
        managed_checkout=managed_checkout,
        target_repo_root=target_repo_root,
        plugin_root=plugin_root,
        codex_marketplace_path=codex_marketplace_path,
        cli_path=cli_path,
        claude_wrapper_path=claude_wrapper_path,
        include_repo_onboarding=include_repo_onboarding,
    )
    emit_progress(
        "STEP: skipping Codex host cache refresh"
        if args.skip_codex_cache_refresh
        else "STEP: refreshing Codex host cache",
    )
    codex_cache_refresh = maybe_install_codex_host(
        home_root=home_root,
        codex_marketplace_path=codex_marketplace_path,
        doctor_payload=initial_doctor_payload,
        skip=args.skip_codex_cache_refresh,
    )
    doctor_payload = initial_doctor_payload
    if codex_cache_refresh.get("status") == "attempted":
        doctor_payload = build_doctor_payload(
            home_root=home_root,
            repo_root=Path(checkout["repo_root"]),
            managed_checkout=managed_checkout,
            target_repo_root=target_repo_root,
            plugin_root=plugin_root,
            codex_marketplace_path=codex_marketplace_path,
            cli_path=cli_path,
            claude_wrapper_path=claude_wrapper_path,
            include_repo_onboarding=include_repo_onboarding,
            include_latest_host_operation=False,
        )
        codex_cache_refresh["post_refresh_cache_manifest_version"] = doctor_payload.get(
            "codex_cache_manifest_version"
        )
        codex_cache_refresh["post_refresh_drift"] = doctor_payload.get("codex_source_cache_drift")
        post_status = doctor_payload.get("codex_host_guidance", {}).get("status")
        codex_cache_refresh["post_refresh_host_status"] = post_status
        _record_post_delivery_readback(codex_cache_refresh, doctor_payload, phase="update")
        if (
            codex_cache_refresh.get("delivery_verified") is not True
            or doctor_payload.get("codex_cache_manifest_status") != "valid"
            or doctor_payload.get("codex_source_cache_drift")
            or post_status != "installed"
        ):
            codex_cache_refresh["status"] = "failed"
            codex_cache_refresh["reason"] = (
                "install-incomplete"
                if codex_cache_refresh.get("action") == "install"
                else "cache-still-stale"
            )
            codex_cache_refresh["error"] = (
                "Codex app-server plugin/install returned success, but charness still does not appear as an installed current local plugin."
            )
        else:
            if codex_cache_refresh.get("action") == "install":
                codex_cache_refresh["status"] = "installed"
                payload.setdefault("completed_actions", []).append("codex_host_installed")
            else:
                codex_cache_refresh["status"] = "refreshed"
                payload.setdefault("completed_actions", []).append("codex_cache_refreshed")
    payload["codex_cache_refresh"] = codex_cache_refresh
    post_update_cache_entries = codex_all_plugin_cache_entries(default_codex_cache_root(home_root))
    cache_diff = diff_cache_entries(pre_update_cache_entries, post_update_cache_entries)
    session_staleness = session_staleness_payload(
        cache_diff,
        home_root=home_root,
        repo_root=Path(checkout["repo_root"]),
    )
    if session_staleness is not None:
        payload["session_staleness"] = session_staleness
    payload["codex_host_guidance"] = doctor_payload["codex_host_guidance"]
    payload["claude_host_guidance"] = doctor_payload["claude_host_guidance"]
    payload["grok_host_guidance"] = doctor_payload.get("grok_host_guidance") or {}
    payload["repo_onboarding"] = doctor_payload["repo_onboarding"]
    payload["host_next_steps"] = {
        **payload.get("host_next_steps", {}),
        **doctor_payload["host_next_steps"],
    }
    payload["next_action"] = doctor_payload["next_action"]
    payload["checkout_version"] = doctor_payload["checkout_version"]
    payload["codex_source_version"] = doctor_payload["codex_source_version"]
    payload["codex_cache_manifest_version"] = doctor_payload["codex_cache_manifest_version"]
    payload["codex_cache_manifest_status"] = doctor_payload.get("codex_cache_manifest_status")
    payload["codex_source_cache_drift"] = doctor_payload["codex_source_cache_drift"]
    payload["target_repo_root"] = str(target_repo_root)
    if _host_delivery_failed(codex_cache_refresh):
        _mark_host_delivery_failure(
            doctor_payload,
            codex_cache_refresh,
            command="update",
            scope=args.scope or "self",
        )
        payload["codex_host_guidance"] = doctor_payload["codex_host_guidance"]
        payload["host_next_steps"] = doctor_payload["host_next_steps"]
        payload["next_action"] = doctor_payload["next_action"]
    if managed_checkout:
        write_install_state(home_root, repo_root=Path(checkout["repo_root"]), managed_checkout=True)
    version_state = write_version_state(
        home_root,
        provenance=build_version_provenance(
            home_root=home_root,
            repo_root=Path(checkout["repo_root"]),
            managed_checkout=managed_checkout,
            cli_path=cli_path,
        ),
    )
    latest_release = latest_release_for_current_version(
        version_state.get("latest_release"),
        payload["checkout_version"] if isinstance(payload.get("checkout_version"), str) else None,
    )
    if latest_release is not None:
        payload["latest_release_check"] = latest_release
        write_version_state(home_root, latest_release=latest_release)
    payload["checkout"] = checkout
    payload["scope"] = args.scope or "self"
    tool_update_failed = False
    if args.scope == "all":
        tool_update_payload, tool_update_failed = run_tool_update_flow(
            repo_root=Path(checkout["repo_root"]),
            managed_checkout=managed_checkout,
            plugin_root=plugin_root,
            tool_ids=[],
            dry_run=False,
            skip_sync_support=False,
            upstream_checkouts=[],
            precomputed_support_results=payload.get("support_sync"),
        )
        payload["tool_update"] = tool_update_payload
        if tool_update_payload["results"] and not tool_update_failed:
            payload.setdefault("completed_actions", []).append("external_tools_updated")
    update_failed = tool_update_failed or _host_delivery_failed(codex_cache_refresh)
    if tool_update_failed:
        _mark_external_tool_update_failure(payload, scope=payload["scope"])
        doctor_payload["host_next_steps"] = payload.get("host_next_steps", {})
        doctor_payload["next_action"] = payload.get("next_action", {})
    write_host_state(
        home_root,
        key="last_update",
        payload=doctor_payload,
        delivery=codex_cache_refresh,
        operation_status="failed" if update_failed else "success",
        operation_scope=payload["scope"],
    )
    emit_progress(
        (
            "FAILED: update incomplete; inspect the typed YAML result and retry with `charness update all --detail`"
            if payload["scope"] == "all"
            else "FAILED: update incomplete; inspect the typed YAML result and retry with `charness update --detail`"
        )
        if update_failed
        else "DONE: update complete"
    )
    emit_operational_response(
        args,
        payload,
        event="update",
        projector=lambda data: project_runtime_response(data, event="update"),
    )
    return 1 if update_failed else 0
