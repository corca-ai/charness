#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


def _load_local(module_name: str, alias: str | None = None):
    module_path = Path(__file__).resolve().parent / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(alias or module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ADAPTER = _load_local("resolve_adapter", "issue_resolve_adapter")
RUNTIME = _load_local("issue_runtime")
BRIEF = _load_local("issue_brief")
CLOSE = _load_local("issue_close")
VERIFY = _load_local("issue_verify_closeout")
newest_open_issue = RUNTIME.newest_open_issue
parse_selector = RUNTIME.parse_selector
resolve_target = RUNTIME.resolve_target
close_with_comment = CLOSE.close_with_comment
verify_closeout = VERIFY.verify_closeout
BACKEND_PROBE_TIMEOUT_SECONDS = 60


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def _resolve_backend(repo_root: Path) -> dict[str, Any]:
    adapter = ADAPTER.load_adapter(repo_root)
    if not adapter["valid"]:
        return {"adapter": adapter, "backend": ADAPTER.default_backend(), "adapter_ok": False}
    backend = dict(adapter["data"].get("issue_backend") or ADAPTER.default_backend())
    return {"adapter": adapter, "backend": backend, "adapter_ok": True}


def _run_probe(binary: str, args: list[str]) -> dict[str, Any]:
    try:
        result = subprocess.run(
            [binary, *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=BACKEND_PROBE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "exit_code": 124,
            "stdout": str(exc.stdout or "").strip(),
            "stderr": f"timed out after {BACKEND_PROBE_TIMEOUT_SECONDS}s",
        }
    return {"exit_code": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}


def _probe_backend(backend: dict[str, Any]) -> dict[str, Any]:
    binary = backend.get("binary") or backend.get("id")
    if not binary:
        raise RuntimeError(
            "issue_backend produced no binary; configure issue_backend.id and "
            "issue_backend.binary in .agents/issue-adapter.yaml."
        )
    binary_path = shutil.which(binary)
    selected: dict[str, Any] = {
        "id": backend.get("id", "gh"), "binary": binary, "binary_path": binary_path,
        "found": binary_path is not None, "commands": backend.get("commands"),
        "auth_status": None, "version": None,
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
    resolved = _resolve_backend(args.repo_root.resolve())
    try:
        selected = _probe_backend(resolved["backend"])
    except RuntimeError as exc:
        payload = {"ok": False, "error": str(exc), "adapter": resolved["adapter"],
                   "selected_backend": resolved["backend"]}
        if args.json:
            emit(payload)
        else:
            print(str(exc))
        return 1
    ok = resolved["adapter_ok"] and _backend_ok(selected)
    payload: dict[str, Any] = {"ok": ok, "selected_backend": selected, "adapter": resolved["adapter"]}
    if selected["id"] == "gh":
        payload.update(gh_found=selected["found"], gh_path=selected["binary_path"],
                       auth_status=selected["auth_status"])
    if not selected["found"]:
        payload["error"] = (
            f"issue_backend binary {selected['binary']!r} not found on PATH. "
            f"Install the declared backend or update issue_backend in "
            f".agents/issue-adapter.yaml so it matches a backend the host exposes."
        )
    if args.json:
        emit(payload)
    elif ok:
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
    repo_root = args.repo_root.resolve()
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
    emit({"ok": True, "repo": args.repo, "numbers": numbers, "source": source,
          "issue": issue, "selected_backend": backend})
    return 0


def command_close_with_comment(args: argparse.Namespace) -> int:
    resolved = _resolve_backend(args.repo_root.resolve())
    if not resolved["adapter_ok"]:
        emit({"ok": False, "adapter": resolved["adapter"]})
        return 1
    try:
        result = close_with_comment(
            args.repo, args.number, args.body_file.resolve(),
            backend=resolved["backend"], reason=args.reason,
        )
    except RuntimeError as exc:
        emit({"ok": False, "error": str(exc), "selected_backend": resolved["backend"]})
        return 2
    result["selected_backend"] = resolved["backend"]
    emit(result)
    return 0


def command_verify_closeout(args: argparse.Namespace) -> int:
    resolved = _resolve_backend(args.repo_root.resolve())
    if not resolved["adapter_ok"]:
        emit({"ok": False, "adapter": resolved["adapter"]})
        return 1
    try:
        result = verify_closeout(
            repo_root=args.repo_root.resolve(),
            repo=args.repo,
            numbers=args.number,
            classification=args.classification,
            carrier=args.carrier,
            backend=resolved["backend"],
            commit_ref=args.commit_ref,
            body_file=args.body_file.resolve() if args.body_file else None,
            manual_fallback_reason=args.manual_fallback_reason,
            expect_state=args.expect_state,
        )
    except RuntimeError as exc:
        emit({"ok": False, "error": str(exc), "selected_backend": resolved["backend"]})
        return 2
    result["selected_backend"] = resolved["backend"]
    emit(result)
    return 0 if result["ok"] else 2


def command_resolve_invocation(args: argparse.Namespace) -> int:
    adapter = ADAPTER.load_adapter(args.repo_root.resolve())
    if not adapter["valid"]:
        emit({"ok": False, "adapter": adapter})
        return 1
    try:
        payload = BRIEF.build_invocation_payload(args.repo_root.resolve(), args.values, adapter,
            ADAPTER.DEFAULT_FEATURE_BRIEF_PAUSE)
    except ValueError as exc:
        emit({"ok": False, "error": str(exc), "adapter": adapter})
        return 2
    emit(payload)
    return 0


def command_brief_path(args: argparse.Namespace) -> int:
    emit(BRIEF.build_brief_path_payload(args.repo_root.resolve(), args.number, args.date))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    cwd_default = Path.cwd()
    preflight = subparsers.add_parser("preflight")
    preflight.add_argument("--json", action="store_true")
    preflight.add_argument("--repo-root", type=Path, default=cwd_default)
    preflight.set_defaults(func=command_preflight)

    target = subparsers.add_parser("resolve-target")
    target.add_argument("--repo-root", type=Path, default=cwd_default)
    target.add_argument("--target")
    target.set_defaults(func=command_resolve_target)

    invocation = subparsers.add_parser("resolve-invocation")
    invocation.add_argument("--repo-root", type=Path, default=cwd_default)
    invocation.add_argument("values", nargs="*")
    invocation.set_defaults(func=command_resolve_invocation)

    select = subparsers.add_parser("select")
    select.add_argument("--repo", required=True)
    select.add_argument("--selector")
    select.add_argument("--repo-root", type=Path, default=cwd_default)
    select.set_defaults(func=command_select)

    close = subparsers.add_parser("close-with-comment")
    close.add_argument("--repo", required=True)
    close.add_argument("--number", type=int, required=True)
    close.add_argument("--body-file", type=Path, required=True)
    close.add_argument("--reason", default="completed")
    close.add_argument("--repo-root", type=Path, default=cwd_default)
    close.set_defaults(func=command_close_with_comment)

    verify = subparsers.add_parser("verify-closeout")
    verify.add_argument("--repo", required=True)
    verify.add_argument("--number", action="append", type=int, required=True)
    verify.add_argument("--classification", choices=VERIFY.CLASSIFICATIONS, required=True)
    verify.add_argument("--carrier", choices=VERIFY.CARRIERS, required=True)
    verify.add_argument("--commit-ref")
    verify.add_argument("--body-file", type=Path)
    verify.add_argument("--manual-fallback-reason", choices=VERIFY.MANUAL_FALLBACK_REASONS)
    verify.add_argument("--expect-state", choices=("CLOSED",))
    verify.add_argument("--repo-root", type=Path, default=cwd_default)
    verify.set_defaults(func=command_verify_closeout)

    brief = subparsers.add_parser("brief-path")
    brief.add_argument("--number", type=int, required=True)
    brief.add_argument("--repo-root", type=Path, default=cwd_default)
    brief.add_argument("--date", help="ISO date (YYYY-MM-DD); defaults to today")
    brief.set_defaults(func=command_brief_path)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
