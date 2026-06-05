"""Resume a partially-completed `publish_release` run (#305).

When the pre-push gate flakes after the local `Release ...` commit + tag are made
but before the push lands, the original run leaves a partial state: commit + tag
local, nothing on the remote, no GitHub release. Re-running the normal flow is
not idempotent (`git commit` hits "nothing to commit", `git tag` hits "tag
exists"). `--resume` detects that exact partial state, RE-VALIDATES the pre-push
gates (it must not blindly push a stale local commit), then continues with
push -> create-release -> verify -> finalize, skipping the commit/tag it already
has and skipping a release that already exists.

The resume flow reuses the CLI module's already-bound helpers (passed in as
``cli``) so there is no second copy of the publish tail to drift.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _git_out(cli: Any, repo_root: Path, args: list[str]) -> str:
    return cli.run(["git", *args], cwd=repo_root).stdout.strip()


def resumable_state(
    repo_root: Path,
    *,
    tag_name: str,
    commit_message: str,
    remote: str,
    backend: dict[str, Any],
    cli: Any,
) -> dict[str, Any]:
    head_subject = _git_out(cli, repo_root, ["log", "-1", "--format=%s"])
    head_sha = _git_out(cli, repo_root, ["rev-parse", "HEAD"])
    tag_state = cli._helpers.tag_exists(repo_root, tag_name, remote=remote)
    tag_sha = ""
    if tag_state["local"]:
        tag_sha = _git_out(cli, repo_root, ["rev-list", "-n", "1", tag_name])
    return {
        "head_is_release_commit": head_subject == commit_message,
        "head_sha": head_sha,
        "tag_local": tag_state["local"],
        "tag_remote": tag_state["remote"],
        "tag_points_at_head": bool(tag_sha) and tag_sha == head_sha,
        "release_exists": cli._helpers.release_exists(repo_root, tag_name, backend),
    }


def assert_resumable(state: dict[str, Any], *, tag_name: str) -> None:
    if not state["head_is_release_commit"]:
        raise SystemExit(
            f"--resume: HEAD is not the `{tag_name}` release commit; nothing to resume. "
            "Resume only continues a publish whose local release commit + tag already exist."
        )
    if not state["tag_local"]:
        raise SystemExit(f"--resume: local tag `{tag_name}` is missing; nothing to resume.")
    if not state["tag_points_at_head"]:
        raise SystemExit(
            f"--resume: tag `{tag_name}` does not point at HEAD; refusing to resume an inconsistent state."
        )
    if state["tag_remote"] and state["release_exists"]:
        raise SystemExit(
            f"--resume: tag `{tag_name}` is already on the remote and its GitHub release exists; "
            "the publish is already complete (nothing to resume)."
        )


def resume_publish(repo_root: Path, *, args: Any, plan: dict[str, Any], adapter_data: dict[str, Any], cli: Any) -> None:
    payload = plan["payload"]
    tag_name = plan["tag_name"]
    branch = plan["branch"]
    backend = plan["backend"]
    issue_repo = plan["issue_repo"]
    state = resumable_state(
        repo_root, tag_name=tag_name, commit_message=payload["commit_message"],
        remote=args.remote, backend=backend, cli=cli,
    )
    assert_resumable(state, tag_name=tag_name)
    payload["resume_state"] = state
    if not args.execute:
        payload["resume"] = "dry-run: would re-validate gates, then push/create/verify the existing commit+tag"
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    notes_file = args.notes_file.resolve() if args.notes_file else None
    cli.run(cli.backend_command(backend, "auth_check", ["gh", "auth", "status"]), cwd=repo_root)
    # RN2: re-validate the pre-push gates before continuing — never push a stale
    # local release commit unchecked. Refresh the release artifact first (mirroring
    # the normal flow's write -> narrative-audit order) so the audit sees the
    # current target. The original attempt already passed the file-triggered
    # adapter/real-host preflights on this unchanged worktree, so resume re-runs the
    # gates that can flake at push time, not those one-time file-delta checks.
    cli.preflight_release_issues(repo_root, repo=issue_repo, issue_numbers=args.close_issue, payload=payload, run=cli.run)
    cli.run_requested_review_gate(repo_root)
    cli.run_cli_skill_surface_gate(repo_root, adapter_data)
    cli.run_shell(str(adapter_data["quality_command"]), cwd=repo_root)
    fresh_checkout_payload = cli.run_fresh_checkout_probes(repo_root)
    payload["fresh_checkout_probe_status"] = fresh_checkout_payload["status"]
    expected_release_url = cli.expected_github_release_url(repo_root, backend, tag_name)
    payload["expected_release_url"] = expected_release_url
    host_payload = cli.safe_real_host_payload(
        repo_root, plan["release_content_paths"], build_payload=cli.build_real_host_payload
    )
    artifact_relpath = cli.write_current_artifact(
        repo_root, adapter_data, payload, host_payload,
        fresh_checkout_payload=fresh_checkout_payload, release_url=expected_release_url,
    )
    cli.run_narrative_audit(repo_root, target_tag=tag_name, notes_file=notes_file)

    if not state["tag_remote"]:
        cli.run(["git", "push", args.remote, branch, tag_name], cwd=repo_root)

    if state["release_exists"]:
        release_stdout = expected_release_url or ""
    else:
        release_stdout = cli.create_release(
            repo_root, backend, tag_name=tag_name, title=plan["title"], notes_file=notes_file
        ).stdout
    release_verify_result = cli.verify_release_visible(
        repo_root, tag_name, backend, backend_command=cli.backend_command, run=cli.run
    )
    cli.finalize_release_payload(
        repo_root, payload, artifact_relpath=artifact_relpath, host_payload=host_payload,
        release_stdout=release_stdout, expected_release_url=expected_release_url,
        release_verified=release_verify_result.returncode == 0,
    )
    cli.ensure_release_issues_closed(repo_root, repo=issue_repo, issue_numbers=args.close_issue, payload=payload, run=cli.run)
    cli.commit_final_release_artifact(
        repo_root, adapter_data=adapter_data, payload=payload, host_payload=host_payload,
        fresh_checkout_payload=fresh_checkout_payload, artifact_relpath=artifact_relpath,
        expected_release_url=expected_release_url, remote=args.remote, branch=branch,
        has_issue_closeout=bool(args.close_issue),
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
