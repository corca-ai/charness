from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

_runtime = runpy.run_path(str(Path(__file__).resolve().with_name("publish_release_runtime.py")))
_evaluate_baton_reconcile = runpy.run_path(
    str(Path(__file__).resolve().with_name("publish_release_baton.py"))
)["evaluate_baton_reconcile"]


def _capture_lifecycle(repo_root: Path, *, tag_name: str) -> dict[str, Any]:
    """Best-effort capture after the distinct-channel publication proof."""

    helper_path = next(
        (
            parent / "scripts" / "lifecycle_usage_capture.py"
            for parent in Path(__file__).resolve().parents
            if (parent / "scripts" / "lifecycle_usage_capture.py").is_file()
        ),
        None,
    )
    if helper_path is None:
        return {"status": "capture_error", "appended": False, "errors": ["lifecycle capture helper unavailable"]}
    try:
        capture = runpy.run_path(str(helper_path))["capture_lifecycle_outcome"]
        return capture(repo_root=repo_root, lifecycle_kind="release_publish", evidence_locator=tag_name)
    except Exception as exc:  # telemetry must never undo a completed publication
        return {"status": "capture_error", "appended": False, "errors": [f"{exc.__class__.__name__}: {exc}"]}


def timed(payload: dict[str, Any], key: str, func):
    return _runtime["timed"](payload, key, func)


def _baton_reconcile_record(repo_root: Path, adapter_data: dict[str, Any], *, target_version: str) -> dict[str, Any]:
    """Best-effort baton observation after the distinct-channel publication proof."""

    try:
        return _evaluate_baton_reconcile(repo_root, adapter_data, target_version=target_version)
    except Exception as exc:  # the observation must never undo a completed publication
        return {
            "status": "capture_error",
            "path": str(adapter_data.get("post_publish_baton_path", "") or "").strip(),
            "target_version": target_version,
            "errors": [f"{exc.__class__.__name__}: {exc}"],
        }


def preflight_close_issue_carrier(repo_root: Path, *, args: Any, issue_repo: str, payload: dict[str, Any], cli: Any) -> None:
    cli.preflight_release_issues(
        repo_root,
        repo=issue_repo,
        issue_numbers=args.close_issue,
        payload=payload,
        run=cli.run,
        behavior_lines=args.close_issue_behavior,
        classification=args.close_issue_classification,
        carrier_file=args.close_issue_carrier_file.resolve() if args.close_issue_carrier_file else None,
    )


def run_pre_push_quality_gates(repo_root: Path, adapter_data: dict[str, Any], payload: dict[str, Any], *, cli: Any) -> None:
    payload["requested_review_gate"] = timed(
        payload, "requested_review_gate", lambda: cli.run_requested_review_gate(repo_root)
    )
    timed(payload, "cli_skill_surface_gate", lambda: cli.run_cli_skill_surface_gate(repo_root, adapter_data))
    timed(payload, "quality_command", lambda: cli.run_shell(str(adapter_data["quality_command"]), cwd=repo_root))


def run_distinct_channel_floor(
    repo_root: Path,
    *,
    args: Any,
    adapter_data: dict[str, Any],
    state: dict[str, Any],
    payload: dict[str, Any],
    cli: Any,
) -> None:
    timed(
        payload,
        "distinct_channel_verification",
        lambda: cli.confirm_release_via_distinct_channel(
            repo_root,
            payload,
            adapter_data=adapter_data,
            run_shell=cli.run_shell,
            tag_name=state["tag_name"],
            expected_release_url=state["expected_release_url"],
            backend=state["backend"],
            backend_command=cli.backend_command,
        ),
    )
    if cli.evaluate_release_distinct_channel(payload)["ok"]:
        return
    _commit_final_release_artifact(
        repo_root,
        args=args,
        adapter_data=adapter_data,
        state=state,
        payload=payload,
        cli=cli,
        has_issue_closeout=False,
    )
    cli.fail_release_distinct_channel_floor(payload)


def _commit_final_release_artifact(
    repo_root: Path,
    *,
    args: Any,
    adapter_data: dict[str, Any],
    state: dict[str, Any],
    payload: dict[str, Any],
    cli: Any,
    has_issue_closeout: bool,
) -> None:
    cli.commit_final_release_artifact(
        repo_root,
        adapter_data=adapter_data,
        payload=payload,
        host_payload=state["host_payload"],
        fresh_checkout_payload=state["fresh_checkout_payload"],
        artifact_relpath=state["artifact_relpath"],
        expected_release_url=state["expected_release_url"],
        remote=args.remote,
        branch=state["branch"],
        has_issue_closeout=has_issue_closeout,
    )


def close_issues_install_refresh_and_commit(
    repo_root: Path,
    *,
    args: Any,
    adapter_data: dict[str, Any],
    state: dict[str, Any],
    issue_repo: str,
    payload: dict[str, Any],
    cli: Any,
) -> None:
    timed(
        payload,
        "issue_closeout",
        lambda: cli.ensure_release_issues_closed(
            repo_root,
            repo=issue_repo,
            issue_numbers=args.close_issue,
            payload=payload,
            run=cli.run,
            behavior_lines=args.close_issue_behavior,
        ),
    )
    payload["install_refresh"] = timed(
        payload,
        "post_publish_install_refresh",
        lambda: cli.run_post_publish_install_refresh(
            repo_root,
            command=adapter_data.get("post_publish_install_refresh", ""),
            run_shell=cli.run_shell,
        ),
    )
    _commit_final_release_artifact(
        repo_root,
        args=args,
        adapter_data=adapter_data,
        state=state,
        payload=payload,
        has_issue_closeout=bool(args.close_issue),
        cli=cli,
    )


def run_release_closeout_tail(
    repo_root: Path,
    *,
    args: Any,
    adapter_data: dict[str, Any],
    state: dict[str, Any],
    issue_repo: str,
    payload: dict[str, Any],
    cli: Any,
) -> None:
    run_distinct_channel_floor(repo_root, args=args, adapter_data=adapter_data, state=state, payload=payload, cli=cli)
    payload["lifecycle_capture"] = _capture_lifecycle(repo_root, tag_name=state["tag_name"])
    payload["baton_reconcile"] = _baton_reconcile_record(
        repo_root, adapter_data, target_version=str(payload.get("target_version", ""))
    )
    close_issues_install_refresh_and_commit(
        repo_root,
        args=args,
        adapter_data=adapter_data,
        state=state,
        issue_repo=issue_repo,
        payload=payload,
        cli=cli,
    )
