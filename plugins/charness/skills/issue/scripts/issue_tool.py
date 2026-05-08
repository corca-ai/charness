#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


def _load_resolve_adapter():
    module_path = Path(__file__).resolve().parent / "resolve_adapter.py"
    spec = importlib.util.spec_from_file_location("issue_resolve_adapter", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_issue_runtime():
    module_path = Path(__file__).resolve().parent / "issue_runtime.py"
    spec = importlib.util.spec_from_file_location("issue_runtime", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ADAPTER = _load_resolve_adapter()
RUNTIME = _load_issue_runtime()
newest_open_issue = RUNTIME.newest_open_issue
parse_selector = RUNTIME.parse_selector
resolve_target = RUNTIME.resolve_target
split_resolve_args = RUNTIME.split_resolve_args


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def command_preflight(args: argparse.Namespace) -> int:
    gh_path = shutil.which("gh")
    payload: dict[str, Any] = {"gh_found": gh_path is not None, "gh_path": gh_path, "auth_status": None}
    ok = gh_path is not None
    if gh_path is not None:
        result = subprocess.run(["gh", "auth", "status"], check=False, capture_output=True, text=True)
        ok = result.returncode == 0
        payload["auth_status"] = {
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    payload["ok"] = ok
    if args.json:
        emit(payload)
    else:
        print("gh authenticated" if ok else "gh missing or unauthenticated")
    return 0 if ok else 1


def command_resolve_target(args: argparse.Namespace) -> int:
    adapter = ADAPTER.load_adapter(args.repo_root.resolve())
    if not adapter["valid"]:
        emit({"ok": False, "adapter": adapter})
        return 1
    try:
        target = resolve_target(args.repo_root.resolve(), args.target, adapter["data"])
    except ValueError as exc:
        emit({"ok": False, "error": str(exc), "adapter": adapter})
        return 2
    emit({"ok": True, "target": target, "adapter": adapter})
    return 0


def command_select(args: argparse.Namespace) -> int:
    try:
        numbers = parse_selector(args.selector)
        issue = None
        source = "selector"
        if numbers is None:
            issue = newest_open_issue(args.repo)
            numbers = [int(issue["number"])]
            source = "github-newest-open"
    except (RuntimeError, ValueError) as exc:
        emit({"ok": False, "error": str(exc), "repo": args.repo})
        return 1
    emit({"ok": True, "repo": args.repo, "numbers": numbers, "source": source, "issue": issue})
    return 0


def command_resolve_invocation(args: argparse.Namespace) -> int:
    adapter = ADAPTER.load_adapter(args.repo_root.resolve())
    if not adapter["valid"]:
        emit({"ok": False, "adapter": adapter})
        return 1
    try:
        target_arg, selector = split_resolve_args(args.values)
        target = resolve_target(args.repo_root.resolve(), target_arg, adapter["data"])
        numbers = parse_selector(selector)
    except ValueError as exc:
        emit({"ok": False, "error": str(exc), "adapter": adapter})
        return 2
    emit(
        {
            "ok": True,
            "target": target,
            "selector": selector,
            "numbers": numbers,
            "selector_source": "github-newest-open" if numbers is None else "argument",
            "adapter": adapter,
        }
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight = subparsers.add_parser("preflight")
    preflight.add_argument("--json", action="store_true")
    preflight.set_defaults(func=command_preflight)

    target = subparsers.add_parser("resolve-target")
    target.add_argument("--repo-root", type=Path, default=ADAPTER.REPO_ROOT)
    target.add_argument("--target")
    target.set_defaults(func=command_resolve_target)

    invocation = subparsers.add_parser("resolve-invocation")
    invocation.add_argument("--repo-root", type=Path, default=ADAPTER.REPO_ROOT)
    invocation.add_argument("values", nargs="*")
    invocation.set_defaults(func=command_resolve_invocation)

    select = subparsers.add_parser("select")
    select.add_argument("--repo", required=True)
    select.add_argument("--selector")
    select.set_defaults(func=command_select)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
