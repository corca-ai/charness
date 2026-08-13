"""Classify a release-resume HEAD into its resume phase.

One concept, split out of `publish_release_resume.py` (which reached its length cap): given
a repo, a tag, and the adapter-derived release record path, decide WHICH partial-publish
state HEAD is in — legacy release-content, a marked prepared stop awaiting its claims
review, or one of the four post-publication closeout phases — and report every fact the
callers downstream assert on.

Deliberately separate from the refusals. This module answers "what state is this?"; the
`assert_*` functions next door answer "may we proceed from it?", and keeping the observer
apart from the judge is what lets the judge run its checks in whatever order is safest
without the classification quietly depending on that order.
"""
from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

_claims_review = runpy.run_path(str(Path(__file__).resolve().with_name("publish_release_claims_review.py")))


def git_out(cli: Any, repo_root: Path, args: list[str]) -> str:
    return cli.run(["git", *args], cwd=repo_root).stdout.strip()


def optional_git_out(cli: Any, repo_root: Path, args: list[str]) -> str:
    result = cli.run(["git", *args], cwd=repo_root, check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def is_claims_evidence_commit(cli: Any, repo_root: Path, *, prepared_commit: str, evidence_commit: str) -> bool:
    parents = optional_git_out(cli, repo_root, ["show", "-s", "--format=%P", evidence_commit]).split()
    if parents != [prepared_commit]:
        return False
    changed = [line for line in cli.run(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", prepared_commit, evidence_commit],
        cwd=repo_root,
    ).stdout.splitlines() if line]
    # The claims-review schema's `pass` verdict carries the review's own narrative
    # alongside the JSON record, so R is one record plus at most its narrative -- never
    # anything else. The shape rule has one owner; `validate_claims_review` is what binds
    # the second path to the one the record actually names.
    return _claims_review["claims_record_in_change_set"](changed) is not None


def claims_evidence_child(cli: Any, repo_root: Path, *, prepared_commit: str) -> str:
    # ``rev-list --children -n 1`` selects a traversal tip, not necessarily P;
    # inspect all reachable parent relationships so a remote-only R is found.
    for line in git_out(cli, repo_root, ["rev-list", "--all", "--parents"]).splitlines():
        parts = line.split()
        if len(parts) != 2 or parts[1] != prepared_commit:
            continue
        candidate = parts[0]
        if is_claims_evidence_commit(
            cli, repo_root, prepared_commit=prepared_commit, evidence_commit=candidate
        ):
            return candidate
    return ""


def resumable_state(
    repo_root: Path,
    *,
    tag_name: str,
    commit_message: str,
    remote: str,
    branch: str,
    backend: dict[str, Any],
    record_path: str,
    cli: Any,
) -> dict[str, Any]:
    head_subject = git_out(cli, repo_root, ["log", "-1", "--format=%s"])
    head_sha = git_out(cli, repo_root, ["rev-parse", "HEAD"])
    head_message = git_out(cli, repo_root, ["show", "-s", "--format=%B", "HEAD"])
    tag_state = cli._helpers.tag_exists(repo_root, tag_name, remote=remote)
    tag_sha = ""
    if tag_state["local"]:
        tag_sha = git_out(cli, repo_root, ["rev-list", "-n", "1", tag_name])
    tag_is_ancestor_head = bool(tag_sha) and cli.run(
        ["git", "merge-base", "--is-ancestor", tag_name, "HEAD"], cwd=repo_root, check=False
    ).returncode == 0
    parent_sha = optional_git_out(cli, repo_root, ["rev-parse", "HEAD^"]) if head_sha != tag_sha else ""
    grandparent_sha = (
        optional_git_out(cli, repo_root, ["rev-parse", "HEAD^^"])
        if tag_sha and parent_sha and parent_sha != tag_sha
        else ""
    )
    parent_message = git_out(cli, repo_root, ["show", "-s", "--format=%B", "HEAD^"]) if parent_sha else ""
    remote_result = cli.run(
        ["git", "ls-remote", "--heads", remote, f"refs/heads/{branch}"],
        cwd=repo_root,
        check=False,
    )
    remote_branch_sha = remote_result.stdout.split(maxsplit=1)[0] if remote_result.returncode == 0 and remote_result.stdout.strip() else ""
    close_refs = cli.release_content_close_keyword_refs(head_message)
    parent_close_refs = cli.release_content_close_keyword_refs(parent_message)
    phase = "release-content"
    def _prepared(commit: str) -> dict[str, str] | None:
        return _claims_review["prepared_record"](repo_root, commit=commit, record_path=record_path, run=cli.run)

    prepared_head = _prepared(head_sha)
    prepared = _prepared(parent_sha) if parent_sha else None
    tagged_prepared = _prepared(tag_sha) if tag_sha else None
    claims_evidence_commit = ""
    tagged_claims_evidence = (
        claims_evidence_child(cli, repo_root, prepared_commit=tagged_prepared["commit"])
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
        and is_claims_evidence_commit(cli, repo_root, prepared_commit=prepared["commit"], evidence_commit=head_sha)
    ):
        phase = "prepared-claims-review"
        claims_evidence_commit = head_sha
    prepared_parent_sha = (
        optional_git_out(cli, repo_root, ["rev-parse", f"{prepared['commit']}^"])
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
        "record_path": record_path,
        "marker_at_head": _claims_review["marker_at_commit"](
            repo_root, commit=head_sha, record_path=record_path, run=cli.run
        ),
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
