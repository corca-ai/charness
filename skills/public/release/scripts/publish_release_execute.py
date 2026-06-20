from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _prepare_release_attempt(
    args: argparse.Namespace,
    repo_root: Path,
    plan: dict[str, Any],
    adapter_data: dict[str, Any],
    *,
    cli: Any,
) -> dict[str, Any]:
    payload = plan["payload"]
    next_version = plan["next_version"]
    tag_name = plan["tag_name"]
    backend = plan["backend"]
    release_content_paths = plan["release_content_paths"]
    adapter_preflight_payload = plan["adapter_preflight_payload"]
    issue_repo = plan["issue_repo"]

    notes_file = args.notes_file.resolve() if args.notes_file else None
    cli.run_notes_file_preflight(repo_root, target_tag=tag_name, notes_file=notes_file)

    cli.run(cli.backend_command(backend, "auth_check", ["gh", "auth", "status"]), cwd=repo_root)
    expected_release_url = cli.expected_github_release_url(repo_root, backend, tag_name)
    payload["expected_release_url"] = expected_release_url
    cli.preflight_release_issues(repo_root, repo=issue_repo, issue_numbers=args.close_issue, payload=payload, run=cli.run)
    cli.run_release_adapter_preflight(repo_root, adapter_preflight_payload, run_command=cli.run)
    cli.run_bump(args, repo_root)
    cli.ensure_release_surface(repo_root, next_version)

    final_release_paths = sorted(set(release_content_paths + cli.changed_paths(repo_root)))
    host_payload = cli.safe_real_host_payload(repo_root, final_release_paths, build_payload=cli.build_real_host_payload)
    payload["retro_trigger_evaluation"] = cli.build_retro_trigger_evaluation(
        repo_root,
        final_release_paths,
        evaluated_at="final_release_paths",
        tag_name=tag_name,
        execute=True,
    )
    fresh_checkout_plan = cli.build_fresh_checkout_payload(repo_root, run_probes=False)
    cli.write_current_artifact(
        repo_root,
        adapter_data,
        payload,
        host_payload=host_payload,
        release_url=expected_release_url,
        quality_status="is queued for this publish attempt",
        fresh_checkout_payload=fresh_checkout_plan,
    )
    cli.run_requested_review_gate(repo_root)
    cli.run_cli_skill_surface_gate(repo_root, adapter_data)
    cli.run_shell(str(adapter_data["quality_command"]), cwd=repo_root)
    return {
        "payload": payload,
        "branch": plan["branch"],
        "tag_name": tag_name,
        "title": plan["title"],
        "backend": backend,
        "issue_repo": issue_repo,
        "notes_file": notes_file,
        "expected_release_url": expected_release_url,
        "host_payload": host_payload,
        "fresh_checkout_plan": fresh_checkout_plan,
    }


def _commit_release_artifact(
    args: argparse.Namespace,
    repo_root: Path,
    state: dict[str, Any],
    adapter_data: dict[str, Any],
    *,
    cli: Any,
) -> dict[str, Any]:
    payload = state["payload"]
    tag_name = state["tag_name"]
    notes_file = state["notes_file"]
    expected_release_url = state["expected_release_url"]
    host_payload = state["host_payload"]
    fresh_checkout_plan = state["fresh_checkout_plan"]

    artifact_relpath = cli.write_current_artifact(
        repo_root,
        adapter_data,
        payload,
        host_payload,
        fresh_checkout_payload=fresh_checkout_plan,
        release_url=expected_release_url,
    )
    cli.run_narrative_audit(repo_root, target_tag=tag_name, notes_file=notes_file)
    cli.run(["git", "add", "-A"], cwd=repo_root)
    commit_command = ["git", "commit", "-m", payload["commit_message"]]
    for body_line in cli.release_commit_body(payload, args.close_issue):
        commit_command.extend(["-m", body_line])
    cli.run(commit_command, cwd=repo_root)
    fresh_checkout_payload = cli.run_fresh_checkout_probes(repo_root)
    payload["fresh_checkout_probe_status"] = fresh_checkout_payload["status"]
    if fresh_checkout_payload["status"] == "passed":
        cli.amend_fresh_checkout_artifact(
            repo_root,
            write_artifact=lambda **kwargs: cli.write_current_artifact(
                repo_root, adapter_data, payload, host_payload, **kwargs
            ),
            fresh_checkout_payload=fresh_checkout_payload,
            release_url=expected_release_url,
            artifact_relpath=artifact_relpath,
            tag_name=tag_name,
            notes_file=notes_file,
            run_narrative_audit=cli.run_narrative_audit,
            run_command=cli.run,
        )
        fresh_checkout_payload = cli.run_fresh_checkout_probes(repo_root)
        payload["fresh_checkout_probe_status"] = fresh_checkout_payload["status"]
    state["fresh_checkout_payload"] = fresh_checkout_payload
    state["artifact_relpath"] = artifact_relpath
    return state


def _create_release_commit(
    args: argparse.Namespace,
    repo_root: Path,
    plan: dict[str, Any],
    adapter_data: dict[str, Any],
    *,
    cli: Any,
) -> dict[str, Any]:
    state = _prepare_release_attempt(args, repo_root, plan, adapter_data, cli=cli)
    return _commit_release_artifact(args, repo_root, state, adapter_data, cli=cli)


def _publish_and_finalize(
    args: argparse.Namespace,
    repo_root: Path,
    state: dict[str, Any],
    adapter_data: dict[str, Any],
    *,
    cli: Any,
) -> None:
    payload = state["payload"]
    branch = state["branch"]
    tag_name = state["tag_name"]
    title = state["title"]
    backend = state["backend"]
    issue_repo = state["issue_repo"]
    notes_file = state["notes_file"]
    expected_release_url = state["expected_release_url"]
    host_payload = state["host_payload"]
    fresh_checkout_payload = state["fresh_checkout_payload"]
    artifact_relpath = state["artifact_relpath"]

    cli.run(["git", "tag", tag_name], cwd=repo_root)
    cli.run(["git", "push", args.remote, branch, tag_name], cwd=repo_root)

    release_result = cli.create_release(repo_root, backend, tag_name=tag_name, title=title, notes_file=notes_file)
    release_verify_result = cli.verify_release_visible(
        repo_root, tag_name, backend, backend_command=cli.backend_command, run=cli.run
    )
    release_verified = release_verify_result.returncode == 0
    cli.finalize_release_payload(
        repo_root,
        payload,
        artifact_relpath=artifact_relpath,
        host_payload=host_payload,
        release_stdout=release_result.stdout,
        expected_release_url=expected_release_url,
        release_verified=release_verified,
    )
    if not release_verified:
        cli.commit_final_release_artifact(
            repo_root,
            adapter_data=adapter_data,
            payload=payload,
            host_payload=host_payload,
            fresh_checkout_payload=fresh_checkout_payload,
            artifact_relpath=artifact_relpath,
            expected_release_url=expected_release_url,
            remote=args.remote,
            branch=branch,
            has_issue_closeout=False,
        )
        cli.fail_after_post_create_verification(payload, verification_result=release_verify_result)
    # WS-1 rung-2 distinct-channel observer + rung-1 presence floor: confirm the
    # published release through a channel distinct from `gh release view`, recording
    # the verdict BEFORE the irreversible issue close. Issue-close advances on
    # rung-1 record-PRESENCE only (a confirmation or a typed disposition pass it
    # equally, F2a); a silent record refuses the close.
    cli.confirm_release_via_distinct_channel(
        repo_root, payload, adapter_data=adapter_data, run_shell=cli.run_shell,
        tag_name=tag_name, expected_release_url=expected_release_url,
    )
    if not cli.evaluate_release_distinct_channel(payload)["ok"]:
        cli.commit_final_release_artifact(
            repo_root, adapter_data=adapter_data, payload=payload, host_payload=host_payload,
            fresh_checkout_payload=fresh_checkout_payload, artifact_relpath=artifact_relpath,
            expected_release_url=expected_release_url, remote=args.remote, branch=branch,
            has_issue_closeout=False,
        )
        cli.fail_release_distinct_channel_floor(payload)
    cli.ensure_release_issues_closed(repo_root, repo=issue_repo, issue_numbers=args.close_issue, payload=payload, run=cli.run)
    payload["install_refresh"] = cli.run_post_publish_install_refresh(
        repo_root,
        command=adapter_data.get("post_publish_install_refresh", ""),
        run_shell=cli.run_shell,
    )
    cli.commit_final_release_artifact(
        repo_root,
        adapter_data=adapter_data,
        payload=payload,
        host_payload=host_payload,
        fresh_checkout_payload=fresh_checkout_payload,
        artifact_relpath=artifact_relpath,
        expected_release_url=expected_release_url,
        remote=args.remote,
        branch=branch,
        has_issue_closeout=bool(args.close_issue),
    )


def execute_publish_plan(
    args: argparse.Namespace,
    repo_root: Path,
    plan: dict[str, Any],
    adapter_data: dict[str, Any],
    *,
    cli: Any,
) -> None:
    state = _create_release_commit(args, repo_root, plan, adapter_data, cli=cli)
    _publish_and_finalize(args, repo_root, state, adapter_data, cli=cli)
    payload = state["payload"]
    print(json.dumps(payload, ensure_ascii=False, indent=2))
