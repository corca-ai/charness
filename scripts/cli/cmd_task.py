"""Task lane commands."""

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
    CharnessError,
)
from scripts.cli.bootstrap_state import (  # noqa: E402
    emit_yaml,
)
from scripts.cli.install_delivery import (  # noqa: E402
    _compact_guidance,
    _compact_host_refresh,
    _compact_next_action,
    _compact_release_check,
    _compact_session_staleness,
)
from scripts.cli.process import (  # noqa: E402
    _load_task_run_lib,
)
from scripts.cli.tool_response import (  # noqa: E402
    _compact_mapping,
    project_tool_response,
)


def cmd_task_status(args: argparse.Namespace) -> int:
    repo_root = args.repo_root.resolve()
    payload = _load_task_run_lib(args).task_status(repo_root, args.task_id)
    emit_yaml(payload)
    return 1 if payload.get("status") == "missing" else 0


def cmd_task_executors(args: argparse.Namespace) -> int:
    _load_task_run_lib(args)
    from scripts.task_run import task_run_contract, task_run_runtime

    task_status = task_run_runtime.task_status(args.repo_root.resolve())
    task_results = task_status.get("tasks", [])
    executors = []
    for kind in task_run_contract.TASK_EXECUTORS:
        observed_limits = []
        for record in task_results:
            attempts = record.get("attempts")
            for attempt in attempts if isinstance(attempts, list) else []:
                if (
                    isinstance(attempt, dict)
                    and attempt.get("executor") == kind
                    and attempt.get("failure_kind") == "executor-unavailable"
                ):
                    observed_limits.append(
                        {
                            "task_id": record.get("task_id"),
                            "retry_after": attempt.get("retry_after"),
                            "observed_at": attempt.get("started_at"),
                        }
                    )
            failure = record.get("failure")
            runner = record.get("executor")
            if (
                isinstance(failure, dict)
                and isinstance(runner, dict)
                and runner.get("kind") == kind
                and failure.get("kind") == "executor-unavailable"
            ):
                observed_limits.append(
                    {
                        "task_id": record.get("task_id"),
                        "retry_after": failure.get("retry_after"),
                        "observed_at": record.get("timestamps", {}).get("finished_at"),
                    }
                )
        last_observed_limit = max(
            observed_limits,
            key=lambda item: item.get("observed_at") or "",
            default=None,
        )
        try:
            executable = task_run_runtime.resolve_executor_executable(kind, executor=kind)
        except task_run_contract.TaskRunError as exc:
            executors.append(
                {
                    "kind": kind,
                    "availability": "unavailable",
                    "executable": None,
                    "reason": str(exc),
                    "quota_state": "unknown",
                    "last_observed_usage_limit": last_observed_limit,
                }
            )
        else:
            executors.append(
                {
                    "kind": kind,
                    "availability": "available",
                    "executable": executable,
                    "quota_state": "unknown",
                    "last_observed_usage_limit": last_observed_limit,
                }
            )
    emit_yaml(
        {
            "probe": "executable-resolution-only",
            "lane_started": False,
            "executors": executors,
        }
    )
    return 0


def cmd_task_report(args: argparse.Namespace) -> int:
    _load_task_run_lib(args)
    from scripts.task_run import (
        task_run_runtime,
        task_run_status_report,
        task_run_train_stats,
    )

    repo_root = args.repo_root.resolve()
    report = task_run_status_report.render_period_status(
        runtime_path=task_run_runtime.task_runtime_root(repo_root),
        repo_root=repo_root,
        window_hours=task_run_train_stats.parse_window(args.window),
    )
    print(report)
    return 0


def cmd_task_steer(args: argparse.Namespace) -> int:
    _load_task_run_lib(args)
    from scripts.task_run import (
        task_run_lane_runner,
        task_run_runtime,
        task_run_scope,
        task_run_state,
    )

    repo_root = args.repo_root.resolve()
    runtime_root = task_run_runtime.task_runtime_root(repo_root)
    payload = task_run_runtime.read_task_result(runtime_root, args.task_id)
    if payload is None:
        record = {
            "kind": task_run_lane_runner.STEER_ENVELOPE_KIND,
            "task_id": args.task_id,
            "disposition": "nacked",
            "reason_code": "task-not-found",
            "queued_at": task_run_runtime.utc_now_iso(),
        }
        kind = task_run_state.ResultKind.FAILED
    elif args.message is not None:
        liveness = task_run_runtime.runner_liveness(payload)
        if payload.get("status") != "running" or liveness.get("alive") is not True:
            record = {
                "kind": task_run_lane_runner.STEER_ENVELOPE_KIND,
                "task_id": args.task_id,
                "disposition": "nacked",
                "reason_code": "task-not-running",
                "queued_at": task_run_runtime.utc_now_iso(),
            }
            kind = task_run_state.ResultKind.FAILED
        else:
            record = task_run_lane_runner.enqueue_steer(
                task_run_runtime.task_execution_runtime_root(runtime_root, args.task_id)
                / "steer.queue.jsonl",
                args.task_id,
                args.message,
                reason=getattr(args, "reason", None),
                actor=getattr(args, "actor", None),
            )
            kind = (
                task_run_state.ResultKind.SUCCESS
                if record["disposition"] == "accepted"
                else task_run_state.ResultKind.FAILED
            )
    else:
        now = task_run_runtime.utc_now_iso()
        worktree_value = payload.get("worktree_path")
        worktree = Path(str(worktree_value or ""))
        if (
            payload.get("status") == "running"
            or not worktree_value
            or not worktree.is_dir()
            or not isinstance(payload.get("base_sha"), str)
            or not isinstance(payload.get("scope_specs"), list)
        ):
            record = {
                "kind": task_run_lane_runner.STEER_ENVELOPE_KIND,
                "task_id": args.task_id,
                "queued_at": now,
                "disposition": "nacked",
                "reason_code": "same-candidate-unavailable",
            }
            kind = task_run_state.ResultKind.FAILED
        else:
            amended = task_run_scope.rescope_result(
                worktree,
                payload["base_sha"],
                payload["scope_specs"],
                args.amend_scope,
                bool(payload.get("require_change")),
                head=payload.get("target_sha"),
                branch=payload.get("target_branch"),
            )
            accepted = amended.get("verdict") == task_run_scope.PASS
            record = {
                "kind": task_run_lane_runner.STEER_ENVELOPE_KIND,
                "task_id": args.task_id,
                "queued_at": now,
                "delivered_at": now,
                "disposition": "accepted" if accepted else "nacked",
                "reason_code": None if accepted else "candidate-still-out-of-scope",
                "same_candidate": True,
                "executor_relaunched": False,
                "target_sha": payload.get("target_sha"),
                "scope": amended,
                "reason": getattr(args, "reason", None),
                "actor": getattr(args, "actor", None),
            }
            kind = (
                task_run_state.ResultKind.SUCCESS if accepted else task_run_state.ResultKind.FAILED
            )
            record["result_kind"] = kind.value
            payload.setdefault("scope_amendments", []).append(record)
            if accepted:
                payload["scope_specs"] = amended["specs"]
                payload["scope"] = amended
                if isinstance(payload.get("candidate"), dict):
                    candidate = payload["candidate"]
                    candidate["changed_paths"] = amended["changed_paths"]
                    candidate["disallowed_paths"] = amended["disallowed_paths"]
                    candidate["status"] = "validated" if amended["changed_paths"] else "absent"
                    candidate["useful"] = bool(amended["changed_paths"])
            payload.setdefault("timestamps", {})["updated_at"] = now
            task_run_runtime.write_task_result(runtime_root, payload)
    output = {**record, "result_kind": kind.value}
    emit_yaml(output)
    return task_run_state.exit_code_for_result_kind(kind)


def project_runtime_response(payload: dict[str, object], *, event: str) -> dict[str, object]:
    """Return the compact public view for init, update, and doctor commands."""
    response: dict[str, object] = {
        "event": event,
        "response_level": "summary",
        "detail_available": True,
    }
    for key in (
        "package_id",
        "repo_root",
        "managed_checkout",
        "target_repo_root",
        "scope",
        "previous_checkout_version",
        "checkout_version",
        "checkout_git_head",
        "codex_source_version",
        "codex_cache_manifest_version",
        "codex_cache_manifest_status",
        "codex_source_cache_drift",
        "codex_enabled_plugin_id",
        "codex_enabled_plugin_ids",
        "completed_actions",
        "cli_reexec",
    ):
        if key in payload:
            response[key] = payload[key]
    checkout = _compact_mapping(payload.get("checkout"), ("repo_root", "pulled", "cloned"))
    if checkout is not None:
        response["checkout"] = checkout
    latest_release_check = _compact_release_check(payload.get("latest_release_check"))
    if latest_release_check is not None:
        response["latest_release_check"] = latest_release_check
    for source, target in (
        ("codex_cache_refresh", "codex_cache_refresh"),
        ("codex_host_install", "codex_host_install"),
    ):
        compact = _compact_host_refresh(payload.get(source))
        if compact is not None:
            response[target] = compact
    for host in ("codex", "claude", "grok"):
        guidance = _compact_guidance(payload.get(f"{host}_host_guidance"))
        if guidance is not None:
            response[f"{host}_host_guidance"] = guidance
    host_next_steps = payload.get("host_next_steps")
    if isinstance(host_next_steps, dict):
        response["host_next_steps"] = host_next_steps
    repo_onboarding = _compact_guidance(payload.get("repo_onboarding"))
    if repo_onboarding is not None:
        response["repo_onboarding"] = repo_onboarding
    next_action = _compact_next_action(payload.get("next_action"))
    if next_action is not None:
        response["next_action"] = next_action
    session_staleness = _compact_session_staleness(payload.get("session_staleness"))
    if session_staleness is not None:
        response["session_staleness"] = session_staleness
    tool_update = payload.get("tool_update")
    if isinstance(tool_update, dict):
        response["tool_update"] = project_tool_response(tool_update, event="tool-update")
    return response


def cmd_task_run_detached(args: argparse.Namespace) -> int:
    _load_task_run_lib(args)
    from scripts.task_run import task_run_detach

    try:
        payload, code = task_run_detach.launch_detached_command(args)
    except ValueError as exc:
        raise CharnessError(str(exc)) from exc
    emit_yaml(payload)
    return code


def cmd_task_wait(args: argparse.Namespace) -> int:
    _load_task_run_lib(args)
    from scripts.task_run import task_run_detach

    payload, code = task_run_detach.wait_command(args)
    emit_yaml(payload)
    return code


def cmd_task_run(args: argparse.Namespace) -> int:
    if args.detach:
        return cmd_task_run_detached(args)
    lib = _load_task_run_lib(args)
    from scripts.task_run import task_run_state as result_state

    prompt_text = args.prompt
    if args.prompt_file is not None:
        try:
            prompt_text = args.prompt_file.read_text(encoding="utf-8")
        except OSError as exc:
            raise CharnessError(f"could not read --prompt-file {args.prompt_file}: {exc}") from exc
    payload = lib.run_task(
        args.repo_root.resolve(),
        target_path=args.path,
        branch=args.branch,
        base=args.base,
        lane=args.lane,
        scopes=args.scope,
        prompt=prompt_text or "",
        executor=args.executor,
        effort=args.effort,
        task_id=args.task_id,
        prepare=args.prepare,
        require_change=args.require_change,
        skip_prepare=args.skip_prepare,
        allow_no_change=args.allow_no_change,
        timeout_seconds=args.timeout_seconds,
        dry_run=args.dry_run,
        rules_files=args.rules_file,
        grant_writable=args.grant_writable,
        report_only=args.report_only,
        no_progress_seconds=args.no_progress_seconds,
        self_review_policy=args.self_review_policy,
        prelaunch={
            "brief_critique": True,
            "critical_lane": args.critical_lane,
            "acceptance_skeleton": args.acceptance_skeleton,
            "premise_checks": args.premise_check,
        },
    )
    kind = result_state.result_kind_for_receipt(payload)
    payload["result_kind"] = kind.value
    payload["blocker"] = result_state.blocker_for_receipt(payload)
    emit_yaml(payload)
    return result_state.exit_code_for_result_kind(kind)
