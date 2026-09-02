"""Issue-tracker CLI orchestration and immutable provider observations."""

from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))[
    "sibling_loader"
](__file__)
BACKEND = _load_local("issue_backend", "issue_tracker_cli_backend")
PROVIDER = _load_local("issue_provider_selection", "issue_tracker_cli_provider")
READ = _load_local("issue_read", "issue_tracker_cli_read")
TRACKER = _load_local("issue_tracker")
TRACKER_OBSERVATION = _load_local("issue_tracker_observation")
PARSER = _load_local("issue_tracker_cli_parser")
PREFLIGHT = _load_local("issue_tracker_cli_preflight")
GOAL_RUN = _load_local("issue_goal_run")
GOAL_RUN_CLOSE = _load_local("issue_goal_run_close")
_render_yaml = _load_local("issue_yaml_output", "issue_tracker_cli_yaml").render_yaml


def emit(payload: dict[str, Any]) -> None:
    sys.stdout.write(_render_yaml(payload))


def _resolve_backend(repo_root: Path, target_repo: str | None = None) -> dict[str, Any]:
    return PROVIDER.resolve_backend(repo_root, target_repo=target_repo)


def _tracker_parent_number(args: argparse.Namespace) -> int:
    for field in ("goal_run_parent", "parent_number", "number"):
        value = getattr(args, field, None)
        if type(value) is int and value > 0:
            return value
    raise RuntimeError("tracker mutation requires an exact Goal Run parent number")


def _tracker_target(args: argparse.Namespace, repo: str | None = None) -> dict[str, Any]:
    target: dict[str, Any] = {"repo": repo or args.repo}
    for field in ("number", "sub_issue_number", "work_item_key"):
        value = getattr(args, field, None)
        if value is not None:
            target[field] = value
    return target


def _run_tracker_backend_command(args: argparse.Namespace, operation: str, call: Any) -> int:
    try:
        resolved = _resolve_backend(args.repo_root.resolve(), args.repo)
    except RuntimeError as exc:
        emit({"ok": False, "status": "provider-selection-invalid", "error": str(exc)})
        return 2
    if not resolved["adapter_ok"]:
        emit(
            {
                "ok": False,
                "status": "adapter-invalid",
                "outcome": "refused",
                "mutation_invoked": False,
                "adapter": resolved["adapter"],
            }
        )
        return 1
    target_repo = str(resolved.get("target_repo") or args.repo)
    try:
        parent_number = _tracker_parent_number(args)
        started = TRACKER_OBSERVATION.begin(
            repo_root=args.repo_root.resolve(),
            observation_dir=args.observation_dir,
            attempt_id=args.attempt_id,
            draft_sha256=args.draft_sha256,
            binding_sha256=args.binding_sha256,
            repo=target_repo,
            parent_number=parent_number,
            operation=operation,
            target=_tracker_target(args, target_repo),
            submitted_body_sha256=None,
            backend=resolved["backend"],
        )
    except RuntimeError as exc:
        result = {
            "ok": False,
            "status": "refused",
            "outcome": "refused",
            "mutation_invoked": False,
            "error": str(exc),
            "next_action": "repair-input-or-readiness-before-retry",
            "selected_backend": resolved["backend"],
        }
        emit(result)
        return 2
    try:
        result = call(resolved)
    except RuntimeError as exc:
        result = {
            "ok": False,
            "status": "refused",
            "outcome": "refused",
            "mutation_invoked": False,
            "error": str(exc),
            "next_action": "repair-input-or-readiness-before-retry",
        }
    result["selected_backend"] = resolved["backend"]
    try:
        terminal = TRACKER_OBSERVATION.finish(
            repo_root=args.repo_root.resolve(),
            observation_dir=args.observation_dir,
            attempt_id=args.attempt_id,
            started=started,
            result=result,
        )
        result["observation"] = {
            "started_path": started["path"],
            "started_sha256": started["payload"]["receipt_sha256"],
            "terminal_path": terminal["path"],
            "terminal_sha256": terminal["payload"]["receipt_sha256"],
        }
    except RuntimeError as exc:
        result = {
            "ok": False,
            "status": "unverified-write" if result.get("mutation_invoked") else "refused",
            "outcome": "unverified-write" if result.get("mutation_invoked") else "refused",
            "mutation_invoked": bool(result.get("mutation_invoked")),
            "error": f"terminal provider observation could not be persisted: {exc}",
            "next_action": "stop-and-preserve-started-observation",
            "selected_backend": resolved["backend"],
            "started_observation": started,
        }
    emit(result)
    return 0 if result["ok"] else 2


def _run_tracker_read_command(args: argparse.Namespace, call: Any) -> int:
    try:
        resolved = _resolve_backend(args.repo_root.resolve(), args.repo)
    except RuntimeError as exc:
        emit({"ok": False, "status": "provider-selection-invalid", "error": str(exc)})
        return 2
    if not resolved["adapter_ok"]:
        emit(
            {
                "ok": False,
                "status": "adapter-invalid",
                "outcome": "refused",
                "mutation_invoked": False,
                "adapter": resolved["adapter"],
            }
        )
        return 1
    try:
        result = call(resolved)
    except RuntimeError as exc:
        result = {
            "ok": False,
            "status": "refused",
            "outcome": "refused",
            "mutation_invoked": False,
            "error": str(exc),
        }
    result["selected_backend"] = resolved["backend"]
    emit(result)
    return 0 if result["ok"] else 2


def command_tracker_preflight(args: argparse.Namespace) -> int:
    def resolve_for_target(repo_root: Path) -> dict[str, Any]:
        return _resolve_backend(repo_root, args.repo)

    return PREFLIGHT.run(
        args,
        resolve_backend=resolve_for_target,
        emit=emit,
        tracker=TRACKER,
        backend_owner=BACKEND,
        issue_reader=READ,
    )


def command_update(args: argparse.Namespace) -> int:
    return _run_tracker_backend_command(
        args,
        "update-body",
        lambda resolved: TRACKER.update_issue_body(
            str(resolved.get("target_repo") or args.repo),
            args.number,
            args.body_file.resolve(),
            backend=resolved["backend"],
        ),
    )


def command_create_or_reuse_child(args: argparse.Namespace) -> int:
    return _run_tracker_backend_command(
        args,
        "create-child",
        lambda resolved: TRACKER.create_or_reuse_child(
            str(resolved.get("target_repo") or args.repo),
            args.parent_number,
            args.work_item_key,
            args.title,
            args.body_file.resolve(),
            backend=resolved["backend"],
            prior_unresolved_observation=TRACKER_OBSERVATION.find_unresolved_create(
                repo_root=args.repo_root.resolve(),
                observation_dir=args.observation_dir,
                repo=str(resolved.get("target_repo") or args.repo),
                parent_number=args.parent_number,
                work_item_key=args.work_item_key,
                submitted_body_sha256=None,
                exclude_attempt_id=args.attempt_id,
                compare_submitted_body=False,
            ),
        ),
    )


def command_list_sub_issues(args: argparse.Namespace) -> int:
    def build(resolved: dict[str, Any]) -> dict[str, Any]:
        target_repo = str(resolved.get("target_repo") or args.repo)
        result = TRACKER.list_sub_issues(target_repo, args.number, backend=resolved["backend"])
        expected_source = None
        if args.expect_child_file is not None:
            expected_source = TRACKER.load_expected_child_set(
                args.expect_child_file.resolve(), repo=target_repo, parent_number=args.number
            )
            expected = expected_source["children"]
        else:
            expected = sorted(set(args.expect_child or []))
        expectation_supplied = args.expect_child_file is not None or args.expect_child is not None
        actual = sorted(child["number"] for child in result["children"])
        result["expected_children"] = expected if expectation_supplied else None
        result["expected_children_source"] = expected_source
        result["missing_children"] = [number for number in expected if number not in actual]
        result["unexpected_children"] = (
            [number for number in actual if number not in expected] if expectation_supplied else []
        )
        result["all_children_closed"] = result["open"] == 0
        if expectation_supplied and (result["missing_children"] or result["unexpected_children"]):
            result.update(
                ok=False, status="graph-mismatch", next_action="reconcile-exact-child-identities"
            )
        if args.expect_all_closed and not result["all_children_closed"]:
            result.update(
                ok=False,
                status="linked-open-children",
                completion_refusal="linked-open-children",
                next_action="return-open-child-state-to-lifecycle-policy-owner",
            )
        return result

    return _run_tracker_read_command(args, build)


def command_add_sub_issue(args: argparse.Namespace) -> int:
    return _run_tracker_backend_command(
        args,
        "add-sub-issue",
        lambda resolved: TRACKER.add_sub_issue(
            str(resolved.get("target_repo") or args.repo),
            args.number,
            args.sub_issue_number,
            backend=resolved["backend"],
        ),
    )


def command_remove_sub_issue(args: argparse.Namespace) -> int:
    return _run_tracker_backend_command(
        args,
        "remove-sub-issue",
        lambda resolved: TRACKER.remove_sub_issue(
            str(resolved.get("target_repo") or args.repo),
            args.number,
            args.sub_issue_number,
            backend=resolved["backend"],
        ),
    )


def command_goal_run_preflight(args: argparse.Namespace) -> int:
    return GOAL_RUN.command_preflight(
        args,
        resolve_backend=lambda root, target_repo=None: _resolve_backend(
            root, target_repo or args.repo
        ),
        emit=emit,
    )


def command_goal_run_read(args: argparse.Namespace) -> int:
    return GOAL_RUN.command_read(
        args,
        resolve_backend=lambda root, target_repo=None: _resolve_backend(
            root, target_repo or args.repo
        ),
        emit=emit,
    )


def command_goal_run_apply(args: argparse.Namespace) -> int:
    return GOAL_RUN.command_apply(
        args,
        resolve_backend=lambda root, target_repo=None: _resolve_backend(
            root, target_repo or args.repo
        ),
        emit=emit,
    )


def command_goal_run_close(args: argparse.Namespace) -> int:
    return GOAL_RUN_CLOSE.command_close(
        args,
        resolve_backend=lambda root, target_repo=None: _resolve_backend(
            root, target_repo or args.repo
        ),
        emit=emit,
    )


def register_subparsers(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser], cwd_default: Path
) -> None:
    PARSER.register_subparsers(
        subparsers,
        cwd_default,
        handlers={
            "command_tracker_preflight": command_tracker_preflight,
            "command_update": command_update,
            "command_create_or_reuse_child": command_create_or_reuse_child,
            "command_list_sub_issues": command_list_sub_issues,
            "command_add_sub_issue": command_add_sub_issue,
            "command_remove_sub_issue": command_remove_sub_issue,
            "command_goal_run_preflight": command_goal_run_preflight,
            "command_goal_run_read": command_goal_run_read,
            "command_goal_run_apply": command_goal_run_apply,
            "command_goal_run_close": command_goal_run_close,
        },
    )
