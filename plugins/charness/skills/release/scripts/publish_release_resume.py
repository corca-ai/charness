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
import runpy
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
_claims_review = runpy.run_path(str(Path(__file__).resolve().with_name("publish_release_claims_review.py")))
_resume_publish = runpy.run_path(str(Path(__file__).resolve().with_name("publish_release_resume_publish.py")))


def _git_out(cli: Any, repo_root: Path, args: list[str]) -> str:
    return cli.run(["git", *args], cwd=repo_root).stdout.strip()


def _optional_git_out(cli: Any, repo_root: Path, args: list[str]) -> str:
    result = cli.run(["git", *args], cwd=repo_root, check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def _is_claims_evidence_commit(cli: Any, repo_root: Path, *, prepared_commit: str, evidence_commit: str) -> bool:
    changed = cli.run(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", prepared_commit, evidence_commit],
        cwd=repo_root,
    ).stdout.splitlines()
    return len(changed) == 1 and changed[0].startswith("charness-artifacts/release-review/") and changed[0].endswith(".json")


def _claims_evidence_child(cli: Any, repo_root: Path, *, prepared_commit: str) -> str:
    # ``rev-list --children -n 1`` selects a traversal tip, not necessarily P;
    # inspect all reachable parent relationships so a remote-only R is found.
    for line in _git_out(cli, repo_root, ["rev-list", "--all", "--parents"]).splitlines():
        parts = line.split()
        if len(parts) < 2 or prepared_commit not in parts[1:]:
            continue
        candidate = parts[0]
        if _is_claims_evidence_commit(
            cli, repo_root, prepared_commit=prepared_commit, evidence_commit=candidate
        ):
            return candidate
    return ""


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
    tag_is_ancestor_head = bool(tag_sha) and cli.run(
        ["git", "merge-base", "--is-ancestor", tag_name, "HEAD"], cwd=repo_root, check=False
    ).returncode == 0
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
    prepared_head = _claims_review["prepared_record"](repo_root, commit=head_sha, run=cli.run)
    prepared = _claims_review["prepared_record"](repo_root, commit=parent_sha, run=cli.run) if parent_sha else None
    tagged_prepared = _claims_review["prepared_record"](repo_root, commit=tag_sha, run=cli.run) if tag_sha else None
    claims_evidence_commit = ""
    tagged_claims_evidence = (
        _claims_evidence_child(cli, repo_root, prepared_commit=tagged_prepared["commit"])
        if tagged_prepared
        else ""
    )
    if tag_sha and parent_sha == tag_sha and close_refs:
        phase = "post-publication-carrier"
    elif prepared_head and head_subject == commit_message:
        # A marked P is a deliberate pause, never a legacy partial-publish
        # recovery; no claims artifact can be inferred from P alone.
        phase = "prepared-claims-review"
        prepared = prepared_head
    elif tagged_prepared and parent_sha == tagged_claims_evidence and close_refs:
        phase = "post-publication-claims-carrier"
        prepared = tagged_prepared
        claims_evidence_commit = tagged_claims_evidence
    elif (
        tagged_prepared
        and grandparent_sha == tagged_claims_evidence
        and parent_close_refs
        and head_subject == f"Record release issue closeout for {tag_name}"
    ):
        phase = "post-publication-claims-final"
        prepared = tagged_prepared
        claims_evidence_commit = tagged_claims_evidence
    elif tagged_prepared and tagged_claims_evidence == head_sha:
        phase = "prepared-claims-review"
        prepared = tagged_prepared
        claims_evidence_commit = tagged_claims_evidence
    elif (
        tag_sha
        and grandparent_sha == tag_sha
        and parent_close_refs
        and head_subject == f"Record release issue closeout for {tag_name}"
    ):
        phase = "post-publication-final"
    elif (
        prepared
        and parent_message.splitlines()[0:1] == [commit_message]
        and _is_claims_evidence_commit(cli, repo_root, prepared_commit=prepared["commit"], evidence_commit=head_sha)
    ):
        phase = "prepared-claims-review"
        claims_evidence_commit = head_sha
    prepared_parent_sha = (
        _optional_git_out(cli, repo_root, ["rev-parse", f"{prepared['commit']}^"])
        if isinstance(prepared, dict)
        else ""
    )
    remote_is_prepared_base = bool(remote_branch_sha and prepared_parent_sha) and cli.run(
        ["git", "merge-base", "--is-ancestor", remote_branch_sha, prepared_parent_sha],
        cwd=repo_root,
        check=False,
    ).returncode == 0
    return {
        "head_is_release_commit": head_subject == commit_message,
        "phase": phase,
        "prepared": prepared,
        "claims_evidence_commit": claims_evidence_commit,
        "prepared_parent_sha": prepared_parent_sha,
        "remote_is_prepared_base": remote_is_prepared_base,
        "head_sha": head_sha,
        "head_message": head_message,
        "head_close_refs": close_refs,
        "tag_sha": tag_sha,
        "head_parent_is_tag": bool(tag_sha) and parent_sha == tag_sha,
        "parent_sha": parent_sha,
        "grandparent_sha": grandparent_sha,
        "parent_message": parent_message,
        "head_grandparent_is_tag": bool(tag_sha) and grandparent_sha == tag_sha,
        "remote_branch_sha": remote_branch_sha,
        "tag_local": tag_state["local"],
        "tag_remote": tag_state["remote"],
        "remote_tag_sha": tag_state["remote_tag_sha"],
        "tag_points_at_head": bool(tag_sha) and tag_sha == head_sha,
        "tag_is_ancestor_head": tag_is_ancestor_head,
        "release_exists": cli._helpers.release_exists(repo_root, tag_name, backend),
    }


def _assert_post_publication_resumable(state: dict[str, Any], *, tag_name: str) -> bool:
    post_publication_phases = {
        "post-publication-carrier",
        "post-publication-final",
        "post-publication-claims-carrier",
        "post-publication-claims-final",
    }
    if state["phase"] not in post_publication_phases:
        return False
    if not (state["tag_local"] and state["tag_remote"] and state["release_exists"]):
        raise SystemExit(f"--resume: `{tag_name}` carrier HEAD lacks confirmed tag/release publication state.")
    claims_evidence = state.get("claims_evidence_commit", "")
    expected_parent = (
        claims_evidence
        if state["phase"] == "post-publication-claims-carrier"
        else state["tag_sha"] if state["phase"] == "post-publication-carrier" else state["parent_sha"]
    )
    if state["phase"] == "post-publication-carrier":
        valid, message = state["head_parent_is_tag"], "carrier HEAD is not directly based on its release tag."
    elif state["phase"] == "post-publication-final":
        valid, message = state["head_grandparent_is_tag"], "final closeout HEAD is not based on its carrier and release tag."
    elif state["phase"] == "post-publication-claims-carrier":
        valid, message = state["parent_sha"] == claims_evidence, "claims carrier is not directly based on its claims evidence."
    else:
        valid, message = state["grandparent_sha"] == claims_evidence, "claims final HEAD is not based on its carrier and evidence."
    if not valid:
        raise SystemExit(f"--resume: `{tag_name}` {message}")
    if state["remote_branch_sha"] not in {expected_parent, state["head_sha"]}:
        raise SystemExit(
            "--resume: remote branch is neither the release-content nor local carrier commit; "
            "refusing ambiguous closeout recovery."
        )
    return True


def assert_resumable(state: dict[str, Any], *, tag_name: str) -> None:
    if state["tag_local"] and state["tag_remote"] and state["remote_tag_sha"] != state["tag_sha"]:
        raise SystemExit(
            f"--resume: remote tag `{tag_name}` does not resolve to the local release commit; "
            "refusing ambiguous recovery."
        )
    if _assert_post_publication_resumable(state, tag_name=tag_name):
        return
    if state["phase"] == "prepared-claims-review":
        prepared = state.get("prepared")
        if not isinstance(prepared, dict):
            raise SystemExit("--resume: marked prepared state lacks its release-record binding")
        if state["tag_local"] and state["tag_sha"] != prepared["commit"]:
            raise SystemExit(f"--resume: local tag `{tag_name}` does not point at the prepared release record")
        if state["tag_remote"] and state["remote_tag_sha"] != prepared["commit"]:
            raise SystemExit(f"--resume: remote tag `{tag_name}` does not point at the prepared release record")
        allowed_remote_heads = {
            state.get("prepared_parent_sha", ""),
            prepared["commit"],
            state.get("claims_evidence_commit", "") or state["head_sha"],
        }
        if (
            state["remote_branch_sha"]
            and state["remote_branch_sha"] not in allowed_remote_heads
            and not state.get("remote_is_prepared_base", False)
        ):
            raise SystemExit(
                "--resume: remote branch is not the prepared record, claims evidence, or their known base; "
                "refusing unrelated advancement before publication."
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
    if state["phase"] in {
        "prepared-claims-review",
        "post-publication-claims-carrier",
        "post-publication-claims-final",
    }:
        state["claims_review"] = _claims_review["validate_claims_review"](
            repo_root, prepared=state["prepared"], evidence_commit=state.get("claims_evidence_commit") or state["head_sha"],
            artifact_path=args.claims_review_artifact, target_version=current_version, tag_name=tag_name, run=cli.run,
        )
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
    _resume_publish["resume_publish"](
        repo_root, args=args, plan=plan, adapter_data=adapter_data, cli=cli, state=state,
        resumable_state=resumable_state, assert_resumable=assert_resumable, common=_common,
        resume_closeout=_resume_closeout, commit_artifact_before_push=_commit_artifact_before_push,
    )
