#!/usr/bin/env python3
"""Reconcile/install/uninstall/status command for usage-episodes host hooks.

Reads `.agents/usage-episodes-adapter.yaml` from `--repo-root` and applies
the recorded `host_hooks.{claude,codex}` intent against the resolved host
settings paths under `--home`. The `charness` CLI invokes this script during
`charness init` / `charness update` (mode=reconcile) and from the new
`charness session-capture` subcommand.

Exit code: 0 when the requested mode succeeds and (for status) intent matches
actual; 1 when status detects drift, a dangling state-tracked hook script
(#343 liveness), a settings entry left behind by a deleted checkout
(settings_scan), or a HostHookError occurs.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import repo_root_from_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)
ADAPTER_RELATIVE = Path(".agents/usage-episodes-adapter.yaml")


def _load_adapter(repo_root: Path) -> dict[str, Any] | None:
    path = repo_root / ADAPTER_RELATIVE
    if not path.is_file():
        return None
    import yaml

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return None
    return data


def _import_lib():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import host_hook_install_lib  # type: ignore[import-not-found]

    return host_hook_install_lib


def _import_registry():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import host_hook_registry  # type: ignore[import-not-found]

    return host_hook_registry


def _error_hosts(actions: Any, prefix: str = "") -> list[str]:
    """Dotted keys of every result that carries an `error`, at any nesting depth.

    A `HostHookError` is caught per host and recorded as a string so one broken
    host does not abort the others. Reporting exit 0 anyway makes the refusal
    unreachable: the caller sees a successful run over a hook that was never
    installed. This module's docstring has always promised exit 1 here; only
    `--mode status` delivered it. Recursive because sibling-hook intents nest
    one level deeper than the canonical `{host: {...}}` shape.
    """
    failed: list[str] = []
    if not isinstance(actions, dict):
        return failed
    for key, value in actions.items():
        if not isinstance(value, dict):
            continue
        label = f"{prefix}{key}"
        if "error" in value:
            failed.append(label)
            continue
        failed.extend(_error_hosts(value, prefix=f"{label}."))
    return sorted(set(failed))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="Charness source repo (contains the usage-episodes adapter).")
    parser.add_argument("--home", type=Path, default=Path.home(), help="User home directory; resolves host settings paths under it.")
    parser.add_argument("--mode", choices=["reconcile", "status", "install", "uninstall"], default="reconcile", help="Action to take.")
    parser.add_argument("--host", choices=["claude", "codex"], help="Restrict install/uninstall to a single host (mode=install|uninstall only).")
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    home = args.home.resolve()
    lib = _import_lib()
    adapter = _load_adapter(repo_root) or {}

    payload: dict[str, Any]
    if args.mode == "reconcile":
        actions = lib.reconcile_host_hooks(repo_root, adapter=adapter, home=home)
        payload = {
            "mode": "reconcile",
            "adapter_present": (repo_root / ADAPTER_RELATIVE).is_file(),
            "actions": actions,
        }
        payload["failed_hosts"] = _error_hosts(actions)
        exit_code = 1 if payload["failed_hosts"] else 0
    elif args.mode == "status":
        registry = _import_registry()
        status = lib.session_capture_status(repo_root, adapter=adapter, home=home)
        sibling_statuses = registry.sibling_hook_statuses(repo_root, adapter=adapter, home=home)
        liveness = registry.hook_state_liveness(repo_root)
        settings_scan = registry.settings_file_scan(home)
        payload = {
            "mode": "status",
            **status,
            **sibling_statuses,
            "hook_liveness": liveness,
            "settings_scan": settings_scan,
        }
        extra_drift = [
            *(line for sibling in sibling_statuses.values() for line in sibling["drift"]),
            *liveness["dangling"],
            *settings_scan["dangling"],
        ]
        if extra_drift:
            payload["in_sync"] = False
            payload["drift"] = [*status["drift"], *extra_drift]
        exit_code = 0 if payload["in_sync"] else 1
    elif args.mode == "install":
        hosts = [args.host] if args.host else ["claude", "codex"]
        results: dict[str, Any] = {}
        for host in hosts:
            installer = lib.install_claude_hook if host == "claude" else lib.install_codex_hook
            try:
                results[host] = installer(repo_root, home=home)
            except lib.HostHookError as exc:
                results[host] = {"error": str(exc)}
        payload = {"mode": "install", "hosts": hosts, "results": results}
        payload["failed_hosts"] = _error_hosts(results)
        exit_code = 1 if payload["failed_hosts"] else 0
    elif args.mode == "uninstall":
        hosts = [args.host] if args.host else ["claude", "codex"]
        results = {}
        for host in hosts:
            uninstaller = lib.uninstall_claude_hook if host == "claude" else lib.uninstall_codex_hook
            try:
                results[host] = uninstaller(repo_root, home=home)
            except lib.HostHookError as exc:
                results[host] = {"error": str(exc)}
        payload = {"mode": "uninstall", "hosts": hosts, "results": results}
        payload["failed_hosts"] = _error_hosts(results)
        exit_code = 1 if payload["failed_hosts"] else 0
    else:  # pragma: no cover - argparse rejects other values
        return 1

    # One shape for every mode. `install`/`uninstall` used to fall back to a
    # per-host line, which was `results` reformatted and dropped `hosts`,
    # `failed_hosts`, and `mode` -- the three keys that say WHICH hosts were asked
    # for and which of them refused.
    emit_yaml(payload)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
