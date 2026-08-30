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
from pathlib import Path, PurePosixPath
from typing import Any

_claims_evidence = runpy.run_path(
    str(Path(__file__).resolve().with_name("claims_review_evidence.py"))
)
_claims_review = runpy.run_path(
    str(Path(__file__).resolve().with_name("publish_release_claims_review.py"))
)


def git_out(cli: Any, repo_root: Path, args: list[str]) -> str:
    return cli.run(["git", *args], cwd=repo_root).stdout.strip()


def optional_git_out(cli: Any, repo_root: Path, args: list[str]) -> str:
    result = cli.run(["git", *args], cwd=repo_root, check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def artifact_commit_candidates(record_path: str) -> list[str]:
    """Return the release-owned pathspecs that may be refreshed before resume push.

    The release adapter owns the record location.  Keep the author's generated
    inventory under ``charness-artifacts`` in scope as well, but derive the
    consumer-specific path from the adapter record rather than assuming that
    every consumer uses the author's directory layout.
    """
    record_dir = str(PurePosixPath(record_path).parent)
    paths = ["charness-artifacts"]
    if record_dir in {".", ""}:
        paths.append(record_path)
    elif record_dir not in paths and not record_dir.startswith("charness-artifacts/"):
        paths.append(record_dir)
    return paths


def _artifact_path_matches(path: str, candidate: str) -> bool:
    """Match a changed file against a directory pathspec without prefix aliases."""
    return path == candidate or path.startswith(f"{candidate}/")


def is_claims_evidence_commit(
    cli: Any, repo_root: Path, *, prepared_commit: str, evidence_commit: str
) -> bool:
    parents = optional_git_out(
        cli, repo_root, ["show", "-s", "--format=%P", evidence_commit]
    ).split()
    if parents != [prepared_commit]:
        return False
    changed = [
        line
        for line in cli.run(
            [
                "git",
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                prepared_commit,
                evidence_commit,
            ],
            cwd=repo_root,
        ).stdout.splitlines()
        if line
    ]
    # The claims-review schema's `pass` verdict carries the review's own narrative
    # alongside the JSON record, so R is one record plus at most its narrative -- never
    # anything else. The shape rule has one owner; `validate_claims_review` is what binds
    # the second path to the one the record actually names.
    return _claims_evidence["claims_record_in_change_set"](changed) is not None


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


def release_artifact_commit_subject(tag_name: str) -> str:
    """The exact subject `commit_artifact_before_push` writes. One spelling, one owner."""
    return f"chore(release): commit {tag_name} artifact before resume push"


#: How many generated artifact commits may sit between R and the carrier before this
#: stops walking. The resume makes at most one per attempt, and a retried resume can
#: make another, so a handful is generous; an unbounded walk would let an arbitrary
#: history be read as "adjacent to the claims record", which is the thing the direct-
#: parent rule exists to prevent.
_MAX_ARTIFACT_COMMITS = 4

#: Returned when the walk runs out of budget. Not a commit id, and deliberately not
#: `""` -- an empty string is also what a failed `rev-parse` yields, and the two mean
#: different things to a reader debugging a refused resume.
_BOUNDARY_WALK_EXHAUSTED = "boundary-walk-exhausted"


def _is_generated_artifact_commit(
    cli: Any, repo_root: Path, commit: str, *, tag_name: str, record_path: str
) -> bool:
    """Whether `commit` has the resume's generated-commit shape.

    This is a recovery classifier, not cryptographic authorship proof: an operator
    with write access can imitate a subject and allowed path. Requiring both still
    prevents unrelated commits from being silently walked past, while the claims
    record's parent and change-set checks remain the publication evidence boundary.
    The subject is the one thing an operator can read off `git log` and copy, so
    `git commit --allow-empty -m "chore(release): commit <tag> artifact before resume
    push"` alone is not enough. The allowed content is derived from the adapter's
    record path plus the explicitly generated `charness-artifacts` companion tree.
    """
    if optional_git_out(
        cli, repo_root, ["show", "-s", "--format=%s", commit]
    ) != release_artifact_commit_subject(tag_name):
        return False
    changed = [
        line
        for line in optional_git_out(
            cli, repo_root, ["diff-tree", "--no-commit-id", "--name-only", "-r", commit]
        ).splitlines()
        if line.strip()
    ]
    # An EMPTY change set is refused too: `--allow-empty` is the cheapest imitation,
    # and an empty diff is not evidence of a regenerated artifact.
    candidates = artifact_commit_candidates(record_path)
    return bool(changed) and all(
        any(_artifact_path_matches(path, candidate) for candidate in candidates) for path in changed
    )


def claims_evidence_boundary(
    cli: Any, repo_root: Path, commit: str, *, tag_name: str, record_path: str
) -> str:
    """`commit`, or the first ancestor of it that is not a generated artifact commit.

    WHY THIS EXISTS. The resume lane re-runs the full quality gate, which REGENERATES
    tracked inventory under `charness-artifacts/`, and `commit_artifact_before_push`
    commits that churn so the pre-push hook does not see a dirty worktree. That commit
    C lands between the claims record R and the closeout carrier. The classifier below
    was written against `P -> R -> carrier` and tested with that commit stubbed out, so
    with C present EVERY post-publication branch fell through to `release-content` and
    `--resume` answered "HEAD is not the release commit; nothing to resume" -- after the
    tag was already pushed. A partially-closed issue set with no recovery lane is the
    worst state this whole path can reach, and it was reachable by the tool's own
    routine behavior rather than by operator error.

    Deliberately narrow. Only a commit whose subject is EXACTLY the generated one for
    THIS tag is walked through, and only a few of them. A commit outside the adapter-
    derived record scope or the generated companion tree stops the walk. This is a
    shape-based recovery hint, not a proof that the local operator did not author the
    commit; the claims record's own identity is still proven by
    `is_claims_evidence_commit`. This only decides which commit that check is asked about.
    """
    current = commit
    for _ in range(_MAX_ARTIFACT_COMMITS):
        if not current or not _is_generated_artifact_commit(
            cli, repo_root, current, tag_name=tag_name, record_path=record_path
        ):
            return current
        current = optional_git_out(cli, repo_root, ["rev-parse", f"{current}^"])
    # Budget exhausted while still standing on a generated commit. Returning `current`
    # would classify as legacy `release-content`, i.e. "nothing to resume" after a
    # pushed tag -- the worst state on this path, produced by the guard meant to avoid
    # it. The sentinel cannot equal any commit id, so the caller's comparison fails
    # loudly-by-classification instead of silently resolving to the wrong phase.
    return _BOUNDARY_WALK_EXHAUSTED


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
    tag_is_ancestor_head = (
        bool(tag_sha)
        and cli.run(
            ["git", "merge-base", "--is-ancestor", tag_name, "HEAD"], cwd=repo_root, check=False
        ).returncode
        == 0
    )
    parent_sha = (
        optional_git_out(cli, repo_root, ["rev-parse", "HEAD^"]) if head_sha != tag_sha else ""
    )
    grandparent_sha = (
        optional_git_out(cli, repo_root, ["rev-parse", "HEAD^^"])
        if tag_sha and parent_sha and parent_sha != tag_sha
        else ""
    )
    parent_message = (
        git_out(cli, repo_root, ["show", "-s", "--format=%B", "HEAD^"]) if parent_sha else ""
    )
    remote_result = cli.run(
        ["git", "ls-remote", "--heads", remote, f"refs/heads/{branch}"],
        cwd=repo_root,
        check=False,
    )
    remote_branch_sha = (
        remote_result.stdout.split(maxsplit=1)[0]
        if remote_result.returncode == 0 and remote_result.stdout.strip()
        else ""
    )
    close_refs = cli.release_content_close_keyword_refs(head_message)
    parent_close_refs = cli.release_content_close_keyword_refs(parent_message)
    phase = "release-content"

    def _prepared(commit: str) -> dict[str, str] | None:
        return _claims_review["prepared_record"](
            repo_root, commit=commit, record_path=record_path, run=cli.run
        )

    prepared_head = _prepared(head_sha)
    prepared = _prepared(parent_sha) if parent_sha else None
    tagged_prepared = _prepared(tag_sha) if tag_sha else None
    claims_evidence_commit = ""
    tagged_claims_evidence = (
        claims_evidence_child(cli, repo_root, prepared_commit=tagged_prepared["commit"])
        if tagged_prepared
        else ""
    )

    # Each claims arm asks the same question of a DIFFERENT commit: "walking back past
    # the release's own generated artifact commits, is this R?" Computed once and named,
    # rather than inline in three conditions -- three spellings of one predicate is how
    # the arms would drift apart, and the boundary walk shells out to git per step.
    def _is_claims_evidence(commit: str) -> bool:
        return (
            bool(tagged_prepared)
            and bool(tagged_claims_evidence)
            and claims_evidence_boundary(
                cli, repo_root, commit, tag_name=tag_name, record_path=record_path
            )
            == tagged_claims_evidence
        )

    def _bind_tagged_claims(name: str) -> tuple[str, dict[str, str] | None, str]:
        """The three fields every claims arm sets together, so one cannot be forgotten."""
        return name, tagged_prepared, tagged_claims_evidence

    if tag_sha and parent_sha == tag_sha and close_refs:
        phase = "post-publication-carrier"
    elif prepared_head and head_subject == commit_message:
        # A marked P is a deliberate pause, never a legacy partial-publish
        # recovery; no claims artifact can be inferred from P alone.
        phase = "prepared-claims-review"
        prepared = prepared_head
    elif _is_claims_evidence(parent_sha) and close_refs:
        phase, prepared, claims_evidence_commit = _bind_tagged_claims(
            "post-publication-claims-carrier"
        )
    elif (
        _is_claims_evidence(grandparent_sha)
        and parent_close_refs
        and head_subject == f"Record release issue closeout for {tag_name}"
    ):
        phase, prepared, claims_evidence_commit = _bind_tagged_claims(
            "post-publication-claims-final"
        )
    elif _is_claims_evidence(head_sha):
        phase, prepared, claims_evidence_commit = _bind_tagged_claims("prepared-claims-review")
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
        and is_claims_evidence_commit(
            cli, repo_root, prepared_commit=prepared["commit"], evidence_commit=head_sha
        )
    ):
        phase = "prepared-claims-review"
        claims_evidence_commit = head_sha
    prepared_parent_sha = (
        optional_git_out(cli, repo_root, ["rev-parse", f"{prepared['commit']}^"])
        if isinstance(prepared, dict)
        else ""
    )
    remote_is_prepared_base = (
        bool(remote_branch_sha and prepared_parent_sha)
        and cli.run(
            ["git", "merge-base", "--is-ancestor", remote_branch_sha, prepared_parent_sha],
            cwd=repo_root,
            check=False,
        ).returncode
        == 0
    )
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
