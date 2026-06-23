#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))["sibling_loader"](__file__)
ADAPTER = _load_local("resolve_adapter", "issue_resolve_adapter")
RUNTIME = _load_local("issue_runtime")
BRIEF = _load_local("issue_brief")
CLOSE = _load_local("issue_close")
CREATE = _load_local("issue_create")
BACKEND = _load_local("issue_backend", "issue_tool_backend")
READ = _load_local("issue_read")
VERIFY = _load_local("issue_verify_closeout")
VERIFY_BODY = _load_local("issue_verify_closeout_body")
VALIDATE_DRAFT = _load_local("issue_validate_closeout_draft")
PLAN = _load_local("issue_plan")


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def _resolve_backend(repo_root: Path) -> dict[str, Any]:
    adapter = ADAPTER.load_adapter(repo_root)
    if not adapter["valid"]:
        return {"adapter": adapter, "backend": ADAPTER.default_backend(), "adapter_ok": False}
    backend = dict(adapter["data"].get("issue_backend") or ADAPTER.default_backend())
    return {"adapter": adapter, "backend": backend, "adapter_ok": True}


def command_preflight(args: argparse.Namespace) -> int:
    resolved = _resolve_backend(args.repo_root.resolve())
    payload = BACKEND.build_preflight_payload(resolved)
    selected = payload["selected_backend"]
    ok = payload["ok"]
    if args.json:
        emit(payload)
    elif "found" not in selected:
        print(payload["error"])
    elif ok:
        print(f"{selected['id']} backend ready")
    elif selected["found"]:
        print(f"{selected['id']} found but not authenticated/healthy")
    else:
        print(f"{selected['id']} backend binary {selected['binary']!r} missing")
    return 0 if ok else 1


def command_plan(args: argparse.Namespace) -> int:
    repo_root = args.repo_root.resolve()
    adapter = ADAPTER.load_adapter(repo_root)
    resolved = _resolve_backend(repo_root)
    preflight = BACKEND.build_preflight_payload(resolved)
    if not adapter["valid"]:
        emit({"ok": False, "adapter": adapter, "next_action": "repair_issue_adapter"})
        return 1
    try:
        if args.intent == "new":
            target = RUNTIME.resolve_target(repo_root, args.target, adapter["data"])
            payload = PLAN.build_new_plan(repo_root, target, adapter, preflight)
        else:
            if args.target:
                emit({
                    "ok": False,
                    "error": "`--target` is only valid with `--intent new`; pass resolve repo/selector as positional values",
                    "adapter": adapter,
                })
                return 2
            invocation = BRIEF.build_invocation_payload(
                repo_root,
                args.values,
                adapter,
                ADAPTER.DEFAULT_FEATURE_BRIEF_PAUSE,
            )
            payload = PLAN.build_resolve_plan(repo_root, invocation, preflight)
    except ValueError as exc:
        emit({"ok": False, "error": str(exc), "adapter": adapter})
        return 2
    payload["ok"] = bool(payload.get("backend_ready"))
    emit(payload)
    return 0 if payload["ok"] else 1


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


def command_read(args: argparse.Namespace) -> int:
    resolved = _resolve_backend(args.repo_root.resolve())
    if not resolved["adapter_ok"]:
        emit({"ok": False, "adapter": resolved["adapter"]})
        return 1
    try:
        result = READ.read_issue_with_comments(args.repo, args.number, backend=resolved["backend"])
    except RuntimeError as exc:
        emit({"ok": False, "error": str(exc), "selected_backend": resolved["backend"]})
        return 2
    result["selected_backend"] = resolved["backend"]
    emit(result)
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


def command_check_source_preservation(args: argparse.Namespace) -> int:
    body_file = args.body_file.resolve()
    if not body_file.is_file():
        emit({"ok": False, "error": f"body file not found: {body_file}"})
        return 2
    result = VERIFY_BODY.evaluate_source_preservation(body_file.read_text(encoding="utf-8"))
    require_external = bool(args.require_external)
    external_missing = require_external and not result["external_sourced"]
    ok = result["ok"] and not external_missing
    payload: dict[str, Any] = {
        **result,
        "ok": ok,
        "require_external": require_external,
        "external_marker_missing": external_missing,
        "body_file": str(body_file),
    }
    emit(payload)
    return 0 if ok else 1


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
    a fake milestone.
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

    plan = subparsers.add_parser("plan", help="Plan an issue new/resolve run before reading, mutating, or closing")
    plan.add_argument("--repo-root", type=Path, default=cwd_default, help="Repo root used to resolve the issue adapter")
    plan.add_argument("--intent", choices=("new", "resolve"), required=True, help="Issue operation to plan")
    plan.add_argument("--target", help="Target repo for issue new; defaults through adapter/git remote")
    plan.add_argument("values", nargs="*", help="Raw issue resolve invocation values when --intent resolve")
    plan.set_defaults(func=command_plan)

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

    read = subparsers.add_parser("read", help="Read an issue body and comments through the selected backend")
    read.add_argument("--repo", required=True, help="Target repository in owner/repo form")
    read.add_argument("--number", type=int, required=True, help="Issue number to read")
    read.add_argument("--repo-root", type=Path, default=cwd_default, help="Repo root used to resolve the issue adapter")
    read.set_defaults(func=command_read)

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

    source = subparsers.add_parser(
        "check-source-preservation",
        help="Check a created issue body / artifact for the provider-neutral source-preservation contract",
    )
    source.add_argument("--body-file", type=Path, required=True, help="Path to the issue body or local artifact to check")
    source.add_argument(
        "--require-external",
        action="store_true",
        help="Fail when no `Source origin:` marker is present (assert the issue is externally sourced)",
    )
    source.set_defaults(func=command_check_source_preservation)

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
