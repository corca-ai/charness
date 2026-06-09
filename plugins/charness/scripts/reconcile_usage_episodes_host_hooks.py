#!/usr/bin/env python3
"""Reconcile/install/uninstall/status command for usage-episodes host hooks.

Reads `.agents/usage-episodes-adapter.yaml` from `--repo-root` and applies
the recorded `host_hooks.{claude,codex}` intent against the resolved host
settings paths under `--home`. The `charness` CLI invokes this script during
`charness init` / `charness update` (mode=reconcile) and from the new
`charness session-capture` subcommand.

Exit code: 0 when the requested mode succeeds and (for status) intent matches
actual; 1 when status detects drift or a HostHookError occurs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import repo_root_from_script

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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="Charness source repo (contains the usage-episodes adapter).")
    parser.add_argument("--home", type=Path, default=Path.home(), help="User home directory; resolves host settings paths under it.")
    parser.add_argument("--mode", choices=["reconcile", "status", "install", "uninstall"], default="reconcile", help="Action to take.")
    parser.add_argument("--host", choices=["claude", "codex"], help="Restrict install/uninstall to a single host (mode=install|uninstall only).")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload to stdout.")
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
        exit_code = 0
    elif args.mode == "status":
        status = lib.session_capture_status(repo_root, adapter=adapter, home=home)
        find_skills_status = lib.find_skills_routing_status(repo_root, adapter=adapter, home=home)
        anchor_guard_status = lib.skill_anchor_guard_status(repo_root, adapter=adapter, home=home)
        payload = {
            "mode": "status",
            **status,
            "find_skills_routing": find_skills_status,
            "skill_anchor_edit_guard": anchor_guard_status,
        }
        extra_drift = [*find_skills_status["drift"], *anchor_guard_status["drift"]]
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
        exit_code = 0
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
        exit_code = 0
    else:  # pragma: no cover - argparse rejects other values
        return 1

    if args.json or args.mode in {"reconcile", "status"}:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for host, result in payload.get("results", payload.get("actions", {})).items():
            print(f"{host}: {json.dumps(result, ensure_ascii=False)}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
