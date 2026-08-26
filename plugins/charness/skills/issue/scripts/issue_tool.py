#!/usr/bin/env python3
from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))[
    "sibling_loader"
](__file__)
ADAPTER = _load_local("resolve_adapter", "issue_resolve_adapter")
RUNTIME = _load_local("issue_runtime")
BRIEF = _load_local("issue_brief")
CLOSE = _load_local("issue_close")
CREATE = _load_local("issue_create")
BACKEND = _load_local("issue_backend", "issue_tool_backend")
READ = _load_local("issue_read")
VERIFY = _load_local("issue_verify_closeout")
VERIFY_BODY = _load_local("issue_verify_closeout_body")
# The rung-1 floors live beside the body reader, not inside it.
CLOSEOUT_FLOORS = _load_local("issue_closeout_rung1_floors")
VALIDATE_DRAFT = _load_local("issue_validate_closeout_draft")
PLAN = _load_local("issue_plan")
TRACKER_CLI = _load_local("issue_tracker_cli")
MILESTONE = _load_local("issue_milestone")
PARSER = _load_local("issue_tool_parser")
TRACKER = TRACKER_CLI.TRACKER

_run_tracker_backend_command = TRACKER_CLI._run_tracker_backend_command
_run_tracker_read_command = TRACKER_CLI._run_tracker_read_command
command_tracker_preflight = TRACKER_CLI.command_tracker_preflight
command_update = TRACKER_CLI.command_update
command_create_or_reuse_child = TRACKER_CLI.command_create_or_reuse_child
command_list_sub_issues = TRACKER_CLI.command_list_sub_issues
command_add_sub_issue = TRACKER_CLI.command_add_sub_issue
command_remove_sub_issue = TRACKER_CLI.command_remove_sub_issue


_render_yaml = _load_local("issue_yaml_output", "issue_tool_yaml_output").render_yaml


def emit(payload: dict[str, Any]) -> None:
    """Write one payload to stdout as YAML.

    Every subcommand's whole output. There is no output-format flag: repo-owned
    command output is unconditionally YAML. `gh`'s own `--json` (read by the
    backend helpers) is a third-party native API and is untouched by this.
    """
    sys.stdout.write(_render_yaml(payload))


def _resolve_backend(repo_root: Path) -> dict[str, Any]:
    adapter = ADAPTER.load_adapter(repo_root)
    if not adapter["valid"]:
        return {"adapter": adapter, "backend": ADAPTER.default_backend(), "adapter_ok": False}
    backend = dict(adapter["data"].get("issue_backend") or ADAPTER.default_backend())
    return {"adapter": adapter, "backend": backend, "adapter_ok": True}


def _run_backend_command(args: argparse.Namespace, call: Any, exit_code: Any) -> int:
    resolved = _resolve_backend(args.repo_root.resolve())
    if not resolved["adapter_ok"]:
        emit({"ok": False, "adapter": resolved["adapter"]})
        return 1
    try:
        result = call(resolved)
    except RuntimeError as exc:
        emit({"ok": False, "error": str(exc), "selected_backend": resolved["backend"]})
        return 2
    result["selected_backend"] = resolved["backend"]
    emit(result)
    return exit_code(result)


def _run_adapter_payload(args: argparse.Namespace, call: Any, error_key: str = "adapter") -> int:
    adapter = ADAPTER.load_adapter(args.repo_root.resolve())
    if not adapter["valid"]:
        emit({"ok": False, error_key: adapter})
        return 1
    try:
        payload = call(adapter)
    except ValueError as exc:
        emit({"ok": False, "error": str(exc), error_key: adapter})
        return 2
    emit(payload)
    return 0


def command_preflight(args: argparse.Namespace) -> int:
    resolved = _resolve_backend(args.repo_root.resolve())
    payload = BACKEND.build_preflight_payload(resolved)
    payload["preflight_status"] = _preflight_status(payload)
    emit(payload)
    return 0 if payload["ok"] else 1


def _preflight_status(payload: dict[str, Any]) -> str:
    """The one-word diagnosis the former text line carried.

    `ok: false` alone does not say WHICH of the three failures happened, and the
    three want different actions: probe the backend, authenticate it, or install
    it. Folded into the payload because there is no second human channel to carry
    it any more.
    """
    selected = payload["selected_backend"]
    if "found" not in selected:
        return "backend-probe-failed"
    if payload["ok"]:
        return "ready"
    if selected["found"]:
        return "found-but-not-authenticated-or-unhealthy"
    return "backend-binary-missing"


def command_resolve_target(args: argparse.Namespace) -> int:
    return _run_adapter_payload(
        args,
        lambda adapter: {
            "ok": True,
            "target": RUNTIME.resolve_target(
                args.repo_root.resolve(), args.target, adapter["data"]
            ),
            "adapter": adapter,
        },
    )


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


def command_read(args: argparse.Namespace) -> int:
    return _run_backend_command(
        args,
        lambda resolved: READ.read_issue_with_comments(
            args.repo, args.number, backend=resolved["backend"]
        ),
        lambda _result: 0,
    )


def _refuse_foreign_copy(repo_root: Path) -> None:
    """Refuse a drifted foreign copy before closing an issue.

    Closing is irreversible in the sense that matters here: a reopened issue was
    already read as done by everything downstream. The guard is scoped to this
    command rather than the whole tool so the read-only subcommands stay usable
    from an installed copy.
    """
    bootstrap = next(
        (
            ancestor / "skill_runtime_bootstrap.py"
            for ancestor in Path(__file__).resolve().parents
            if (ancestor / "skill_runtime_bootstrap.py").is_file()
        ),
        None,
    )
    if bootstrap is None:
        return
    runpy.run_path(str(bootstrap))["refuse_foreign_entrypoint"](__file__, repo_root)


def command_close_with_comment(args: argparse.Namespace) -> int:
    _refuse_foreign_copy(args.repo_root.resolve())
    return _run_backend_command(
        args,
        lambda resolved: CLOSE.close_with_comment(
            args.repo,
            args.number,
            args.body_file.resolve(),
            repo_root=args.repo_root.resolve(),
            classification=args.classification,
            backend=resolved["backend"],
            reason=args.reason,
            manual_target_declaration=args.manual_target_declaration,
        ),
        lambda _result: 0,
    )


def command_verify_closeout(args: argparse.Namespace) -> int:
    return _run_backend_command(
        args,
        lambda resolved: VERIFY.verify_closeout(
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
        ),
        lambda result: 0 if result["ok"] else 2,
    )


def command_check_source_preservation(args: argparse.Namespace) -> int:
    body_file = args.body_file.resolve()
    if not body_file.is_file():
        emit({"ok": False, "error": f"body file not found: {body_file}"})
        return 2
    result = CLOSEOUT_FLOORS.evaluate_source_preservation(body_file.read_text(encoding="utf-8"))
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
    return _run_adapter_payload(
        args,
        lambda adapter: BRIEF.build_invocation_payload(
            args.repo_root.resolve(),
            args.values,
            adapter,
            ADAPTER.DEFAULT_FEATURE_BRIEF_PAUSE,
        ),
    )


def command_brief_path(args: argparse.Namespace) -> int:
    try:
        payload = BRIEF.build_brief_path_payload(args.repo_root.resolve(), args.number, args.date)
    except ValueError as exc:
        emit({"ok": False, "error": str(exc), "number": args.number})
        return 1
    emit(payload)
    return 0


resolve_milestone = MILESTONE.resolve


def command_resolve_milestone(args: argparse.Namespace) -> int:
    emit(resolve_milestone(args.requested, args.existing or []))
    return 0


def build_parser() -> argparse.ArgumentParser:
    return PARSER.build_parser(
        modules={
            "plan": PLAN,
            "adapter": ADAPTER,
            "runtime": RUNTIME,
            "brief": BRIEF,
            "backend": BACKEND,
            "tracker_cli": TRACKER_CLI,
            "verify": VERIFY,
            "validate_draft": VALIDATE_DRAFT,
            "create": CREATE,
        },
        handlers={
            "preflight": command_preflight,
            "resolve_target": command_resolve_target,
            "resolve_invocation": command_resolve_invocation,
            "select": command_select,
            "read": command_read,
            "close_with_comment": command_close_with_comment,
            "verify_closeout": command_verify_closeout,
            "check_source_preservation": command_check_source_preservation,
            "brief_path": command_brief_path,
            "resolve_milestone": command_resolve_milestone,
            "resolve_backend": _resolve_backend,
            "run_backend_command": _run_backend_command,
            "emit": emit,
        },
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
