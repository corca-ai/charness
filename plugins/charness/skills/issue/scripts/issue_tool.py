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


def _resolve_backend(repo_root: Path) -> dict[str, Any]:
    adapter = ADAPTER.load_adapter(repo_root)
    if not adapter["valid"]:
        return {"adapter": adapter, "backend": ADAPTER.default_backend(), "adapter_ok": False}
    backend = dict(adapter["data"].get("issue_backend") or ADAPTER.default_backend())
    return {"adapter": adapter, "backend": backend, "adapter_ok": True}


def _run_probe(binary: str, args: list[str]) -> dict[str, Any]:
    result = subprocess.run([binary, *args], check=False, capture_output=True, text=True)
    return {"exit_code": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}


def _probe_backend(backend: dict[str, Any]) -> dict[str, Any]:
    binary = backend.get("binary") or backend.get("id") or "gh"
    binary_path = shutil.which(binary)
    selected: dict[str, Any] = {
        "id": backend.get("id", "gh"),
        "binary": binary,
        "binary_path": binary_path,
        "found": binary_path is not None,
        "commands": backend.get("commands"),
        "auth_status": None,
        "version": None,
    }
    if binary_path is None:
        return selected
    if selected["id"] == "gh":
        selected["auth_status"] = _run_probe(binary, ["auth", "status"])
    else:
        selected["version"] = _run_probe(binary, ["--version"])
    return selected


def _backend_ok(selected: dict[str, Any]) -> bool:
    if not selected["found"]:
        return False
    if selected["id"] == "gh":
        return bool(selected["auth_status"]) and selected["auth_status"]["exit_code"] == 0
    return True


def command_preflight(args: argparse.Namespace) -> int:
    repo_root = args.repo_root.resolve() if args.repo_root else ADAPTER.REPO_ROOT
    resolved = _resolve_backend(repo_root)
    selected = _probe_backend(resolved["backend"])
    ok = resolved["adapter_ok"] and _backend_ok(selected)
    payload: dict[str, Any] = {
        "ok": ok,
        "selected_backend": selected,
        "adapter": resolved["adapter"],
    }
    if selected["id"] == "gh":
        payload["gh_found"] = selected["found"]
        payload["gh_path"] = selected["binary_path"]
        payload["auth_status"] = selected["auth_status"]
    if not selected["found"]:
        payload["error"] = (
            f"issue_backend binary {selected['binary']!r} not found on PATH. "
            f"Install it, configure issue_backend in .agents/issue-adapter.yaml, or fall back to gh."
        )
    if args.json:
        emit(payload)
    else:
        if ok:
            print(f"{selected['id']} backend ready")
        elif selected["found"]:
            print(f"{selected['id']} found but not authenticated/healthy")
        else:
            print(f"{selected['id']} backend binary {selected['binary']!r} missing")
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
    repo_root = args.repo_root.resolve() if args.repo_root else ADAPTER.REPO_ROOT
    resolved = _resolve_backend(repo_root)
    backend = resolved["backend"]
    try:
        numbers = parse_selector(args.selector)
        issue = None
        source = "selector"
        if numbers is None:
            issue = newest_open_issue(args.repo, backend)
            numbers = [int(issue["number"])]
            source = "github-newest-open"
    except (RuntimeError, ValueError) as exc:
        emit({"ok": False, "error": str(exc), "repo": args.repo, "selected_backend": backend})
        return 1
    emit(
        {
            "ok": True,
            "repo": args.repo,
            "numbers": numbers,
            "source": source,
            "issue": issue,
            "selected_backend": backend,
        }
    )
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
    preflight.add_argument("--repo-root", type=Path, default=ADAPTER.REPO_ROOT)
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
    select.add_argument("--repo-root", type=Path, default=ADAPTER.REPO_ROOT)
    select.set_defaults(func=command_select)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
