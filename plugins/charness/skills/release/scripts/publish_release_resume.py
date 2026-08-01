"""Resume a partially-completed `publish_release` run.

When the pre-push gate flakes after the local `Release ...` commit is made but
before the push lands, the original run leaves a partial state: a local commit,
an optional local tag, nothing on the remote, and no GitHub release. Re-running the normal flow is
not idempotent (`git commit` hits "nothing to commit", `git tag` hits "tag
exists"). `--resume` detects that exact partial state, RE-VALIDATES the pre-push
gates (it must not blindly push a stale local commit), then continues with
push -> create-release -> verify -> finalize, skipping the commit/tag it already
has and skipping a release that already exists.

The resume flow reuses the CLI module's already-bound helpers (passed in as
``cli``) so there is no second copy of the publish tail to drift.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


def _load_release_common():
    module_path = Path(__file__).resolve().with_name("publish_release_common.py")
    spec = importlib.util.spec_from_file_location("publish_release_common_for_resume", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_common = _load_release_common()


def _load_resume_closeout():
    module_path = Path(__file__).resolve().with_name("publish_release_resume_closeout.py")
    spec = importlib.util.spec_from_file_location("publish_release_resume_closeout", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_resume_closeout = _load_resume_closeout()


def _git_out(cli: Any, repo_root: Path, args: list[str]) -> str:
    return cli.run(["git", *args], cwd=repo_root).stdout.strip()


def _optional_git_out(cli: Any, repo_root: Path, args: list[str]) -> str:
    result = cli.run(["git", *args], cwd=repo_root, check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def _commit_artifact_before_push(repo_root: Path, *, cli: Any, tag_name: str) -> None:
    # B1: the resume refresh of charness-artifacts/release/latest.md (and
    # any retro-trigger artifact) must be committed BEFORE the push, mirroring the
    # normal flow's release commit. Otherwise charness-artifacts/ is dirty at push
    # time and .githooks/pre-push's `git diff --quiet -- charness-artifacts` blocks
    # with a false "mutated during a read-only quality run" attribution. Guarded on
    # a real change (modified or new files) so an unchanged refresh stays
    # idempotent ("nothing to commit").
    status = cli.run(
        ["git", "status", "--porcelain", "--", "charness-artifacts"], cwd=repo_root
    ).stdout.strip()
    if not status:
        return
    cli.run(["git", "add", "--", "charness-artifacts"], cwd=repo_root)
    cli.run(
        ["git", "commit", "-m", f"chore(release): commit {tag_name} artifact before resume push"],
        cwd=repo_root,
    )


def resumable_state(
    repo_root: Path,
    *,
    tag_name: str,
    commit_message: str,
    remote: str,
    branch: str,
    backend: dict[str, Any],
    cli: Any,
) -> dict[str, Any]:
    head_subject = _git_out(cli, repo_root, ["log", "-1", "--format=%s"])
    head_sha = _git_out(cli, repo_root, ["rev-parse", "HEAD"])
    head_message = _git_out(cli, repo_root, ["show", "-s", "--format=%B", "HEAD"])
    tag_state = cli._helpers.tag_exists(repo_root, tag_name, remote=remote)
    tag_sha = ""
    if tag_state["local"]:
        tag_sha = _git_out(cli, repo_root, ["rev-list", "-n", "1", tag_name])
    parent_sha = _optional_git_out(cli, repo_root, ["rev-parse", "HEAD^"]) if head_sha != tag_sha else ""
    grandparent_sha = (
        _optional_git_out(cli, repo_root, ["rev-parse", "HEAD^^"])
        if tag_sha and parent_sha and parent_sha != tag_sha
        else ""
    )
    parent_message = _git_out(cli, repo_root, ["show", "-s", "--format=%B", "HEAD^"]) if parent_sha else ""
    remote_result = cli.run(
        ["git", "ls-remote", "--heads", remote, f"refs/heads/{branch}"],
        cwd=repo_root,
        check=False,
    )
    remote_branch_sha = remote_result.stdout.split(maxsplit=1)[0] if remote_result.returncode == 0 and remote_result.stdout.strip() else ""
    close_refs = cli.release_content_close_keyword_refs(head_message)
    parent_close_refs = cli.release_content_close_keyword_refs(parent_message)
    phase = "release-content"
    if tag_sha and parent_sha == tag_sha and close_refs:
        phase = "post-publication-carrier"
    elif (
        tag_sha
        and grandparent_sha == tag_sha
        and parent_close_refs
        and head_subject == f"Record release issue closeout for {tag_name}"
    ):
        phase = "post-publication-final"
    return {
        "head_is_release_commit": head_subject == commit_message,
        "phase": phase,
        "head_sha": head_sha,
        "head_message": head_message,
        "head_close_refs": close_refs,
        "tag_sha": tag_sha,
        "head_parent_is_tag": bool(tag_sha) and parent_sha == tag_sha,
        "parent_sha": parent_sha,
        "parent_message": parent_message,
        "head_grandparent_is_tag": bool(tag_sha) and grandparent_sha == tag_sha,
        "remote_branch_sha": remote_branch_sha,
        "tag_local": tag_state["local"],
        "tag_remote": tag_state["remote"],
        "remote_tag_sha": tag_state["remote_tag_sha"],
        "tag_points_at_head": bool(tag_sha) and tag_sha == head_sha,
        "release_exists": cli._helpers.release_exists(repo_root, tag_name, backend),
    }


def assert_resumable(state: dict[str, Any], *, tag_name: str) -> None:
    if state["tag_local"] and state["tag_remote"] and state["remote_tag_sha"] != state["tag_sha"]:
        raise SystemExit(
            f"--resume: remote tag `{tag_name}` does not resolve to the local release commit; "
            "refusing ambiguous recovery."
        )
    if state["phase"] in {"post-publication-carrier", "post-publication-final"}:
        if not (state["tag_local"] and state["tag_remote"] and state["release_exists"]):
            raise SystemExit(
                f"--resume: `{tag_name}` carrier HEAD lacks confirmed tag/release publication state."
            )
        expected_parent = state["tag_sha"] if state["phase"] == "post-publication-carrier" else state["parent_sha"]
        if state["phase"] == "post-publication-carrier" and not state["head_parent_is_tag"]:
            raise SystemExit(f"--resume: `{tag_name}` carrier HEAD is not directly based on its release tag.")
        if state["phase"] == "post-publication-final" and not state["head_grandparent_is_tag"]:
            raise SystemExit(f"--resume: `{tag_name}` final closeout HEAD is not based on its carrier and release tag.")
        if state["remote_branch_sha"] not in {expected_parent, state["head_sha"]}:
            raise SystemExit(
                "--resume: remote branch is neither the release-content nor local carrier commit; "
                "refusing ambiguous closeout recovery."
            )
        return
    if not state["head_is_release_commit"]:
        raise SystemExit(
            f"--resume: HEAD is not the `{tag_name}` release commit; nothing to resume. "
            "Resume only continues a publish whose local release commit already exists."
        )
    if not state["tag_local"]:
        if state["tag_remote"] or state["release_exists"]:
            raise SystemExit(
                f"--resume: local tag `{tag_name}` is missing while remote publication state exists; "
                "refusing to reconstruct an ambiguous tag."
            )
    elif not state["tag_points_at_head"]:
        raise SystemExit(
            f"--resume: tag `{tag_name}` does not point at HEAD; refusing to resume an inconsistent state."
        )
    if state["tag_remote"] and state["release_exists"]:
        raise SystemExit(
            f"--resume: tag `{tag_name}` is already on the remote and its GitHub release exists; "
            "the publish is already complete (nothing to resume)."
        )


def preflight_resume_state(
    repo_root: Path,
    *,
    args: Any,
    adapter_data: dict[str, Any],
    cli: Any,
) -> dict[str, Any]:
    current_version = cli.build_release_payload(repo_root)["surface_versions"]["packaging_manifest"]
    if not isinstance(current_version, str):
        raise SystemExit("current_release did not report a packaging manifest version")
    # NOT gated on the release surface here, and that is a KNOWN GAP, not a decision this
    # slice is entitled to make: resume is the other path to `create_release`, so a
    # surface deleted or corrupted between the failed attempt and the resume reaches
    # publish unchecked. Pre-existing for `drift` as well as for D48's corroboration
    # arm. Adding the gate is a real contract change -- every resume fixture exercises a
    # repo with no generated tree at all -- so it is recorded rather than half-shipped.
    tag_name = f"v{current_version}"
    state = resumable_state(
        repo_root,
        tag_name=tag_name,
        commit_message=f"Release {adapter_data['package_id']} {current_version}",
        remote=args.remote,
        branch=_git_out(cli, repo_root, ["rev-parse", "--abbrev-ref", "HEAD"]),
        backend=adapter_data["release_backend"],
        cli=cli,
    )
    assert_resumable(state, tag_name=tag_name)
    return state


def resume_publish(
    repo_root: Path,
    *,
    args: Any,
    plan: dict[str, Any],
    adapter_data: dict[str, Any],
    cli: Any,
    state: dict[str, Any] | None = None,
) -> None:
    payload = plan["payload"]
    tag_name = plan["tag_name"]
    branch = plan["branch"]
    backend = plan["backend"]
    issue_repo = plan["issue_repo"]
    state = state or resumable_state(
        repo_root, tag_name=tag_name, commit_message=payload["commit_message"],
        remote=args.remote, branch=branch, backend=backend, cli=cli,
    )
    assert_resumable(state, tag_name=tag_name)
    payload["resume_state"] = state
    if state["phase"] in {"post-publication-carrier", "post-publication-final"}:
        _resume_closeout.resume_post_publication_closeout(
            repo_root,
            args=args,
            plan=plan,
            adapter_data=adapter_data,
            state=state,
            common=_common,
            cli=cli,
        )
        return
    if not args.execute:
        payload["resume"] = (
            "dry-run: would re-validate gates, create the missing local tag when needed, "
            "then push/create/verify the existing release commit"
        )
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
    _common.preflight_close_issue_carrier(repo_root, args=args, issue_repo=issue_repo, payload=payload, cli=cli)
    if args.close_issue:
        head_commit_message = cli.run(
            ["git", "show", "-s", "--format=%B", "HEAD"], cwd=repo_root
        ).stdout
        close_refs = cli.release_content_close_keyword_refs(head_commit_message)
        payload["resume_head_release_content_close_refs"] = close_refs
        if close_refs:
            raise SystemExit(
                "--resume: release-content HEAD contains issue close keywords before "
                f"post-publication observer evidence: {close_refs}"
            )
    _common.run_pre_push_quality_gates(repo_root, adapter_data, payload, cli=cli)
    fresh_checkout_payload = _common.timed(
        payload, "fresh_checkout_probes_resume", lambda: cli.run_fresh_checkout_probes(repo_root)
    )
    payload["fresh_checkout_probe_status"] = fresh_checkout_payload["status"]
    expected_release_url = cli.expected_github_release_url(repo_root, backend, tag_name)
    payload["expected_release_url"] = expected_release_url
    host_payload = cli.safe_real_host_payload(
        repo_root, plan["release_content_paths"], build_payload=cli.build_real_host_payload
    )
    # B1: build the EXECUTED retro-trigger evaluation (written /
    # final_release_paths), mirroring the normal flow, so the resumed artifact
    # does not regress to the plan's dry-run (would_write / release_content_paths)
    # payload. This also persists the retro artifact before it is committed below.
    payload["retro_trigger_evaluation"] = cli.build_retro_trigger_evaluation(
        repo_root, plan["release_content_paths"],
        evaluated_at="final_release_paths", tag_name=tag_name, execute=True,
    )
    artifact_relpath = cli.write_current_artifact(
        repo_root, adapter_data, payload, host_payload,
        fresh_checkout_payload=fresh_checkout_payload, release_url=expected_release_url,
    )
    cli.run_narrative_audit(repo_root, target_tag=tag_name, notes_file=notes_file)

    # B1: commit the refreshed artifact before pushing so the pre-push gate
    # does not block on a dirty charness-artifacts/ left by the resume refresh.
    _commit_artifact_before_push(repo_root, cli=cli, tag_name=tag_name)

    def push_create_verify_release() -> tuple[str, Any]:
        if not state["tag_local"]:
            cli.run(["git", "tag", tag_name, state["head_sha"]], cwd=repo_root)
            state["tag_local"] = True
            state["tag_points_at_head"] = True
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
        return release_stdout, release_verify_result

    release_stdout, release_verify_result = _common.timed(
        payload, "push_create_verify_release", push_create_verify_release
    )
    cli.finalize_release_payload(
        repo_root, payload, artifact_relpath=artifact_relpath, host_payload=host_payload,
        release_stdout=release_stdout, expected_release_url=expected_release_url,
        release_verified=release_verify_result.returncode == 0,
    )
    state.update(
        {
            "artifact_relpath": artifact_relpath,
            "backend": backend,
            "branch": branch,
            "expected_release_url": expected_release_url,
            "fresh_checkout_payload": fresh_checkout_payload,
            "host_payload": host_payload,
            "tag_name": tag_name,
        }
    )
    # WS-1: the resumed publish crosses the same irreversible issue-close boundary,
    # so it gets the same rung-2 distinct-channel observer + rung-1 presence floor.
    # A resumed publish is still a verified publish: auto-run the adapter-declared
    # install-refresh before the final artifact commit so the result is durable.
    _common.run_release_closeout_tail(
        repo_root,
        args=args,
        adapter_data=adapter_data,
        state=state,
        issue_repo=issue_repo,
        payload=payload,
        cli=cli,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
