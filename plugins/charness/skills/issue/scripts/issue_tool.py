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
CREATE = _load_local("issue_create")
VERIFY = _load_local("issue_verify_closeout")
VALIDATE_DRAFT = _load_local("issue_validate_closeout_draft")
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
        target = RUNTIME.resolve_target(args.repo_root.resolve(), args.target, adapter["data"])
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
        numbers = RUNTIME.parse_selector(args.selector)
        issue = None
        source = "selector"
        if numbers is None:
            issue = RUNTIME.newest_open_issue(args.repo, backend)
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
        result = CLOSE.close_with_comment(
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
        result = VERIFY.verify_closeout(
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
    try:
        payload = BRIEF.build_brief_path_payload(args.repo_root.resolve(), args.number, args.date)
    except ValueError as exc:
        emit({"ok": False, "error": str(exc), "number": args.number})
        return 1
    emit(payload)
    return 0


def resolve_milestone(requested: str | None, existing: list[str]) -> dict[str, Any]:
    """Resolve a requested milestone against the repo's existing milestone titles.

    The skill must never invent a milestone. This guard assigns only when the
    requested title exactly matches one the repository already has; otherwise it
    leaves the issue unassigned and says so, so the agent cannot silently create
    a fake milestone (corca-ai/charness#202).
    """
    existing_titles = [title for title in existing if title]
    requested_title = (requested or "").strip()
    if not requested_title:
        return {
            "ok": True,
            "assignable": False,
            "milestone": None,
            "action": "leave-unassigned",
            "reason": "no milestone requested",
            "existing": existing_titles,
        }
    if requested_title in existing_titles:
        return {
            "ok": True,
            "assignable": True,
            "milestone": requested_title,
            "action": "assign",
            "reason": f"`{requested_title}` is an existing repository milestone",
            "existing": existing_titles,
        }
    return {
        "ok": True,
        "assignable": False,
        "milestone": None,
        "action": "leave-unassigned",
        "reason": (
            f"no existing repository milestone titled `{requested_title}`; "
            "not creating a new one — state this explicitly to the operator"
        ),
        "existing": existing_titles,
    }


def command_resolve_milestone(args: argparse.Namespace) -> int:
    emit(resolve_milestone(args.requested, args.existing or []))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    cwd_default = Path.cwd()
    preflight = subparsers.add_parser("preflight", help="Inspect the issue adapter and host readiness before invoking the backend")
    preflight.add_argument("--json", action="store_true", help="Emit the full preflight payload as JSON")
    preflight.add_argument("--repo-root", type=Path, default=cwd_default, help="Repo root used to resolve the issue adapter")
    preflight.set_defaults(func=command_preflight)

    target = subparsers.add_parser("resolve-target", help="Resolve an issue target selector (owner/repo[#number]) against the adapter")
    target.add_argument("--repo-root", type=Path, default=cwd_default, help="Repo root used to resolve the issue adapter")
    target.add_argument("--target", help="Target selector (owner/repo or owner/repo#number); defaults to current repo")
    target.set_defaults(func=command_resolve_target)

    invocation = subparsers.add_parser("resolve-invocation", help="Interpret raw skill invocation values into a structured target and selector")
    invocation.add_argument("--repo-root", type=Path, default=cwd_default, help="Repo root used to resolve the issue adapter")
    invocation.add_argument("values", nargs="*", help="Raw skill invocation values to interpret")
    invocation.set_defaults(func=command_resolve_invocation)

    select = subparsers.add_parser("select", help="Select one or more issues by number, comma list, or newest-open default")
    select.add_argument("--repo", required=True, help="Target repository in owner/repo form")
    select.add_argument("--selector", help="Issue selector (number, comma list, or omit to pick newest open)")
    select.add_argument("--repo-root", type=Path, default=cwd_default, help="Repo root used to resolve the issue adapter")
    select.set_defaults(func=command_select)

    close = subparsers.add_parser("close-with-comment", help="Close an issue with a comment body sourced from --body-file")
    close.add_argument("--repo", required=True, help="Target repository in owner/repo form")
    close.add_argument("--number", type=int, required=True, help="Issue number to close")
    close.add_argument("--body-file", type=Path, required=True, help="Path to the closing comment body file")
    close.add_argument("--reason", default="completed", help="Close reason passed to the backend (default: completed)")
    close.add_argument("--repo-root", type=Path, default=cwd_default, help="Repo root used to resolve the issue adapter")
    close.set_defaults(func=command_close_with_comment)

    verify = subparsers.add_parser("verify-closeout", help="Verify a closeout's classification, carrier, and backend state for one or more issues")
    verify.add_argument("--repo", required=True, help="Target repository in owner/repo form")
    verify.add_argument("--number", action="append", type=int, required=True, help="Issue number to verify; repeat for multiple issues")
    verify.add_argument("--classification", choices=VERIFY.CLASSIFICATIONS, required=True, help="Fix-unit classification recorded for the closeout")
    verify.add_argument("--carrier", choices=VERIFY.CARRIERS, required=True, help="Carrier that delivered the fix (direct-commit, pr-body, or manual-fallback)")
    verify.add_argument("--commit-ref", help="Commit ref carrying the fix when carrier is commit-based")
    verify.add_argument("--body-file", type=Path, help="Path to the closing comment body file used for verification")
    verify.add_argument("--manual-fallback-reason", choices=VERIFY.MANUAL_FALLBACK_REASONS, help="Reason code when falling back to a manual closeout carrier")
    verify.add_argument("--expect-state", choices=("CLOSED",), help="Expected backend issue state after closeout")
    verify.add_argument("--repo-root", type=Path, default=cwd_default, help="Repo root used to resolve the issue adapter")
    verify.set_defaults(func=command_verify_closeout)

    VALIDATE_DRAFT.register_validate_closeout_draft_subparser(
        subparsers,
        cwd_default,
        resolve_backend=_resolve_backend,
        emit=emit,
        verifier=VERIFY,
    )

    brief = subparsers.add_parser("brief-path", help="Print the durable brief path for an issue number on the given date")
    brief.add_argument("--number", type=int, required=True, help="Issue number whose brief path should be returned")
    brief.add_argument("--repo-root", type=Path, default=cwd_default, help="Repo root used to resolve the issue adapter")
    brief.add_argument("--date", help="ISO date (YYYY-MM-DD); defaults to today")
    brief.set_defaults(func=command_brief_path)

    milestone = subparsers.add_parser(
        "resolve-milestone",
        help="Decide whether a requested milestone is assignable from the repo's existing milestones (never invents one)",
    )
    milestone.add_argument("--requested", help="Milestone title the operator asked for; omit when none was requested")
    milestone.add_argument(
        "--existing",
        action="append",
        help="An existing repository milestone title (fetch via the backend, e.g. `gh api repos/{repo}/milestones`); repeat per milestone",
    )
    milestone.set_defaults(func=command_resolve_milestone)

    CREATE.register_create_subparser(subparsers, cwd_default)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
