"""Focused edge coverage for release closeout recovery helpers."""

from __future__ import annotations

import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from .release_resume_edge_support import (
    ClaimsResumeCli as _ClaimsResumeCli,
)
from .release_resume_edge_support import (
    ClaimsResumeCommon as _ClaimsResumeCommon,
)
from .release_resume_edge_support import (
    ClassifierCli as _ClassifierCli,
)
from .seeding_support import load_module
from scripts.runtime_scratch import owned_scratch

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "public" / "release" / "scripts"


def _load(name: str):
    return load_module(f"{name}_edge_coverage", SCRIPTS / f"{name}.py")


RESUME_PUBLISH = _load("publish_release_resume_publish")
RESUME = _load("publish_release_resume")
CLAIMS = _load("publish_release_claims_review")
RESUME_STATE = _load("publish_release_resume_state")
_ISOLATED_RESUME_REPO = Path(tempfile.mkdtemp(prefix="charness-resume-repo-"))


_ADAPTER = {"output_dir": "charness-artifacts/release"}
_RECORD_PATH = "charness-artifacts/release/latest.md"


def _resume_claims_publication_leg(
    *,
    remote_branch_sha: str,
    tag_remote: bool,
    release_exists: bool = True,
    notes_file=None,
    notes_preflights: list[dict] | None = None,
    verify_returncode: int = 0,
    cli_out: list | None = None,
) -> tuple[list[list[str]], list[str]]:
    commands: list[list[str]] = []
    committed: list[str] = []
    state = {
        "phase": "prepared-claims-review",
        "tag_local": True,
        "tag_remote": tag_remote,
        "remote_branch_sha": remote_branch_sha,
        "claims_evidence_commit": "claims-evidence",
        "head_sha": "claims-evidence",
        "prepared": {"commit": "prepared"},
        "release_exists": release_exists,
        "record_path": _RECORD_PATH,
        # The real `preflight_resume_state` always sets this for a claims phase, and
        # `resume_publish` now refuses a claims phase without it -- a reconstructed state
        # must not be able to reach tag/push/release create with the floor unrun.
        "claims_review": {
            "path": "charness-artifacts/release-review/edge.json",
            "verdict": "pass",
            "observer_distinctness": {
                "kind": "separate-agent-context",
                "signal": "edge-coverage fixture",
                "review_artifact": "charness-artifacts/release-review/edge.md",
            },
        },
    }
    plan = {
        # `previous_version` is what the real planner carries and what the notes lint must
        # ground on this lane; the fixture would otherwise pin the defect as intended.
        "payload": {"commit_message": "Release v1.2.3", "previous_version": "1.2.2"},
        "tag_name": "v1.2.3",
        "branch": "main",
        "backend": "github",
        "issue_repo": "example/demo",
        "release_content_paths": [],
        "title": "v1.2.3",
    }
    args = SimpleNamespace(execute=True, remote="origin", notes_file=notes_file, close_issue=[])
    cli = _ClaimsResumeCli(
        commands,
        notes_preflights=notes_preflights,
        allow_create=not release_exists,
        verify_returncode=verify_returncode,
    )
    if cli_out is not None:
        cli_out.append(cli)
    RESUME_PUBLISH.resume_publish(
        _ISOLATED_RESUME_REPO,
        args=args,
        plan=plan,
        adapter_data=_ADAPTER,
        cli=cli,
        state=state,
        resumable_state=lambda *_args, **_kwargs: state,
        assert_resumable=lambda *_args, **_kwargs: None,
        common=_ClaimsResumeCommon(),
        resume_closeout=SimpleNamespace(),
        commit_artifact_before_push=lambda *_args, **_kwargs: committed.append("artifact"),
        release_record_path=CLAIMS.release_record_path,
        claims_review_validator=lambda _repo, current_state: current_state["claims_review"],
    )
    return commands, committed


def test_a_failed_post_create_verification_commits_the_artifact_before_it_refuses() -> None:
    """The order is the whole point of the arm, and nothing measured it.

    Verification runs AFTER the tag and the GitHub release exist, so a failure here is
    already past the irreversible boundary. Refusing without first committing the release
    artifact would leave the operator with a published release and no local record of what
    was published -- the one artifact the recovery path reads. So the arm commits, THEN
    raises. Asserting only the raise would pass against an implementation that dropped the
    commit, which is why the commit is asserted first and by count.

    What the `match=` below does NOT prove: `cli` is the harness stub, so that string is
    the STUB's literal, not `publish_release_post_create.fail_after_post_create_verification`'s.
    Changing the real message would not fail here. This test owns the ORDER on the claims
    lane; the real refusal text is the subprocess test's to own -- and that owner
    (`test_release_publish.py`) is `release_only`, so it does NOT run in the standing or
    mutation lanes. "Owned elsewhere" here means owned outside the routine gate.
    """
    clis: list = []

    with pytest.raises(SystemExit, match="post-create verification failed after external mutation"):
        _resume_claims_publication_leg(
            remote_branch_sha="claims-evidence",
            tag_remote=True,
            verify_returncode=1,
            cli_out=clis,
        )

    assert len(clis[0].final_artifact_commits) == 1, (
        "the failure arm must persist the release artifact before refusing; the tag and "
        "the release already exist by the time verification runs"
    )
    assert clis[0].final_artifact_commits[0]["has_issue_closeout"] is False


@pytest.mark.parametrize(
    ("remote_branch_sha", "tag_remote", "expected_push"),
    [
        ("old-branch", True, ["git", "push", "origin", "main"]),
        ("claims-evidence", False, ["git", "push", "origin", "v1.2.3"]),
    ],
)
def test_claims_resume_repairs_exactly_the_missing_publication_leg(
    remote_branch_sha: str, tag_remote: bool, expected_push: list[str]
) -> None:
    """Exercise source-owned branch-only and tag-only recovery, not a copied fixture."""
    commands, committed = _resume_claims_publication_leg(
        remote_branch_sha=remote_branch_sha, tag_remote=tag_remote
    )

    pushes = [command for command in commands if command[:2] == ["git", "push"]]
    assert pushes == [expected_push]
    assert not any(command[:2] == ["git", "tag"] for command in commands)
    assert committed == ["artifact"]


def test_the_post_publication_phase_arms_classify_in_process() -> None:
    """The two closeout arms the subprocess tests reach only through a full publish."""
    carrier = RESUME_STATE.resumable_state(
        Path("."),
        tag_name="v1.2.3",
        commit_message="Release demo 1.2.3",
        remote="origin",
        branch="main",
        backend={},
        record_path=_RECORD_PATH,
        cli=_ClassifierCli(
            revs={"HEAD": "carrier-sha", "HEAD^": "tag-sha", "tag": "tag-sha"},
            subject="Record release issue closeout carrier for v1.2.3",
            messages={"HEAD": "carrier\n\nClose #44.", "HEAD^": "Release demo 1.2.3"},
            close_refs=["#44"],
        ),
    )
    assert carrier["phase"] == "post-publication-carrier"
    assert carrier["head_parent_is_tag"] is True
    assert carrier["record_path"] == _RECORD_PATH

    final = RESUME_STATE.resumable_state(
        Path("."),
        tag_name="v1.2.3",
        commit_message="Release demo 1.2.3",
        remote="origin",
        branch="main",
        backend={},
        record_path=_RECORD_PATH,
        cli=_ClassifierCli(
            revs={
                "HEAD": "final-sha",
                "HEAD^": "carrier-sha",
                "HEAD^^": "tag-sha",
                "tag": "tag-sha",
            },
            subject="Record release issue closeout for v1.2.3",
            messages={"HEAD": "final artifact", "HEAD^": "carrier\n\nClose #44."},
            close_refs=["#44"],
        ),
    )
    assert final["phase"] == "post-publication-final"
    assert final["head_grandparent_is_tag"] is True


def test_the_prepared_claims_review_arms_classify_in_process() -> None:
    """The two arms that select a prepared stop, which remote CI's broad mutation lane
    named as uncovered while the local focused lane called the same range clean.

    Both reach `prepared-claims-review` from different evidence: HEAD is the marked
    prepared record itself, or HEAD is the claims-evidence child of a TAGGED prepared
    record. Which one matched decides what `prepared` and `claims_evidence_commit` bind
    to, so a collapsed arm publishes against the wrong boundary."""
    # HEAD is the marked prepared record P; no tag yet.
    at_prepared = RESUME_STATE.resumable_state(
        Path("."),
        tag_name="v1.2.3",
        commit_message="Release demo 1.2.3",
        remote="origin",
        branch="main",
        backend={},
        record_path=_RECORD_PATH,
        cli=_ClassifierCli(
            revs={"HEAD": "p-sha", "HEAD^": "base-sha"},
            subject="Release demo 1.2.3",
            messages={"HEAD": "Release demo 1.2.3", "HEAD^": "base"},
            tag_local=False,
            marked=("p-sha",),
            parents={"p-sha": "base-sha"},
        ),
    )
    assert at_prepared["phase"] == "prepared-claims-review"
    assert at_prepared["prepared"]["commit"] == "p-sha"
    # No evidence commit can be inferred from P alone.
    assert at_prepared["claims_evidence_commit"] == ""

    # HEAD is R, the claims-evidence child of a TAGGED prepared record.
    at_evidence = RESUME_STATE.resumable_state(
        Path("."),
        tag_name="v1.2.3",
        commit_message="Release demo 1.2.3",
        remote="origin",
        branch="main",
        backend={},
        record_path=_RECORD_PATH,
        cli=_ClassifierCli(
            revs={"HEAD": "r-sha", "HEAD^": "tag-sha", "tag": "tag-sha"},
            subject="Record claims review",
            messages={"HEAD": "Record claims review", "HEAD^": "Release demo 1.2.3"},
            marked=("tag-sha",),
            parents={"tag-sha": "base-sha", "r-sha": "tag-sha"},
            children={"tag-sha": "r-sha"},
        ),
    )
    assert at_evidence["phase"] == "prepared-claims-review"
    assert at_evidence["prepared"]["commit"] == "tag-sha"
    assert at_evidence["claims_evidence_commit"] == "r-sha"


def test_the_claims_carrier_still_classifies_across_the_resumes_own_artifact_commit() -> None:
    """The resume lane creates a commit the classifier could not see, and that made every
    post-push failure on a claims-lane release unrecoverable.

    `resume_publish` re-runs the full quality gate, which regenerates tracked inventory
    under `charness-artifacts/`, and `commit_artifact_before_push` commits that churn so
    the pre-push hook does not observe a dirty worktree. The result is `P -> R -> C ->
    carrier`, while both post-publication claims arms required the carrier's parent (or
    grandparent) to be R EXACTLY. Every arm fell through to `release-content`, and
    `--resume` answered "nothing to resume" -- with the tag already on the remote and an
    arbitrary prefix of the issue set already closed.

    It stayed invisible because the end-to-end tests stub `commit_artifact_before_push`
    to a no-op, so no test ever put the two together.
    """
    subject = RESUME_STATE.release_artifact_commit_subject("v1.2.3")

    carrier = RESUME_STATE.resumable_state(
        Path("."),
        tag_name="v1.2.3",
        commit_message="Release demo 1.2.3",
        remote="origin",
        branch="main",
        backend={},
        record_path=_RECORD_PATH,
        cli=_ClassifierCli(
            revs={"HEAD": "carrier-sha", "HEAD^": "c-sha", "c-sha^": "r-sha", "tag": "tag-sha"},
            subject="Record release issue closeout carrier for v1.2.3",
            messages={"HEAD": "carrier\n\nClose #44.", "HEAD^": subject, "c-sha": subject},
            close_refs=["#44"],
            marked=("tag-sha",),
            parents={"tag-sha": "base-sha", "r-sha": "tag-sha"},
            children={"tag-sha": "r-sha"},
        ),
    )
    assert carrier["phase"] == "post-publication-claims-carrier"
    # The bound boundary is still R, never C: the recovery lane must re-validate against
    # the reviewed claims record, not against a generated inventory commit.
    assert carrier["claims_evidence_commit"] == "r-sha"
    assert carrier["prepared"]["commit"] == "tag-sha"
    for remote_boundary in ("r-sha", "c-sha", "carrier-sha"):
        carrier["remote_branch_sha"] = remote_boundary
        RESUME.assert_resumable(carrier, tag_name="v1.2.3")
    with pytest.raises(SystemExit, match="remote branch"):
        RESUME.assert_resumable({**carrier, "remote_branch_sha": "unrelated"}, tag_name="v1.2.3")
    final = RESUME_STATE.resumable_state(
        Path("."), tag_name="v1.2.3", commit_message="Release demo 1.2.3",
        remote="origin", branch="main", backend={}, record_path=_RECORD_PATH,
        cli=_ClassifierCli(
            revs={"HEAD": "final-sha", "HEAD^": "carrier-sha", "HEAD^^": "c-sha", "c-sha^": "r-sha", "tag": "tag-sha"},
            subject="Record release issue closeout for v1.2.3",
            messages={"HEAD": "final", "HEAD^": "carrier\n\nClose #44.", "c-sha": subject},
            close_refs=["#44"], marked=("tag-sha",),
            parents={"tag-sha": "base-sha", "r-sha": "tag-sha"}, children={"tag-sha": "r-sha"},
        ),
    )
    assert final["phase"] == "post-publication-claims-final"
    final["remote_branch_sha"] = "carrier-sha"
    RESUME.assert_resumable(final, tag_name="v1.2.3")
    with pytest.raises(SystemExit, match="claims final"):
        RESUME.assert_resumable({**final, "claims_grandparent_boundary": "unrelated"}, tag_name="v1.2.3")


def test_the_claims_carrier_classifies_an_adapter_owned_artifact_commit() -> None:
    """The classifier must follow the adapter record, not the author's directory.

    A consumer may configure its release record below ``artifacts/release``. The
    resume writer commits that directory when it refreshes the record, so the
    classifier must walk past it while retaining the claims record's direct
    identity. The companion quality inventory remains in ``charness-artifacts``.
    """
    record_path = "artifacts/release/latest.md"
    subject = RESUME_STATE.release_artifact_commit_subject("v1.2.3")
    carrier = RESUME_STATE.resumable_state(
        Path("."),
        tag_name="v1.2.3",
        commit_message="Release demo 1.2.3",
        remote="origin",
        branch="main",
        backend={},
        record_path=record_path,
        cli=_ClassifierCli(
            revs={"HEAD": "carrier-sha", "HEAD^": "c-sha", "c-sha^": "r-sha", "tag": "tag-sha"},
            subject="Record release issue closeout carrier for v1.2.3",
            messages={"HEAD": "carrier\n\nClose #44.", "HEAD^": subject, "c-sha": subject},
            close_refs=["#44"],
            marked=("tag-sha",),
            parents={"tag-sha": "base-sha", "r-sha": "tag-sha"},
            children={"tag-sha": "r-sha"},
            evidence_changed_by_commit={"c-sha": [record_path]},
        ),
    )
    assert carrier["phase"] == "post-publication-claims-carrier"
    assert carrier["claims_evidence_commit"] == "r-sha"
    assert carrier["prepared"]["commit"] == "tag-sha"


def test_the_boundary_walk_refuses_rather_than_falling_back_to_legacy_content() -> None:
    """Exhausting the walk budget must not resolve to the state it exists to avoid.

    Returning the commit it was standing on made `_is_claims_evidence` False, which
    falls through to `release-content` -- i.e. "HEAD is not the release commit; nothing
    to resume" after a pushed tag, which is the worst state on this path. A guard that
    produces the state it guards against is not a guard. The sentinel cannot equal any
    commit id, so the comparison fails by classification instead of by coincidence.
    """
    subject = RESUME_STATE.release_artifact_commit_subject("v1.2.3")
    cli = _ClassifierCli(
        revs={f"c{n}^": f"c{n + 1}" for n in range(9)},
        subject="unused",
        messages={f"c{n}": subject for n in range(9)},
    )
    # Every commit in the chain carries the generated subject and touches only generated
    # paths, so the walk can never terminate on content -- only on its budget.
    assert (
        RESUME_STATE.claims_evidence_boundary(
            cli, Path("."), "c0", tag_name="v1.2.3", record_path=_RECORD_PATH
        )
        == RESUME_STATE._BOUNDARY_WALK_EXHAUSTED
    )
    # The sentinel is not a commit id and not the empty string a failed rev-parse yields,
    # so a reader debugging a refused resume can tell the two apart.
    assert RESUME_STATE._BOUNDARY_WALK_EXHAUSTED not in {"", None}


def test_a_forged_artifact_commit_subject_does_not_open_the_boundary() -> None:
    """Subject alone is copyable off `git log`; an unrelated path stops the walk.

    `git commit --allow-empty -m "chore(release): commit v1.2.3 artifact before resume
    push"` with unrelated content must not be walked past. The check narrows accidental
    matches; it is not cryptographic proof against an operator who can imitate the
    subject and an allowed generated path. Here the commit carries the right subject
    and touches a path outside the adapter-derived/generated scopes.
    """
    subject = RESUME_STATE.release_artifact_commit_subject("v1.2.3")
    carrier = RESUME_STATE.resumable_state(
        Path("."),
        tag_name="v1.2.3",
        commit_message="Release demo 1.2.3",
        remote="origin",
        branch="main",
        backend={},
        record_path=_RECORD_PATH,
        cli=_ClassifierCli(
            revs={"HEAD": "carrier-sha", "HEAD^": "c-sha", "c-sha^": "r-sha", "tag": "tag-sha"},
            subject="Record release issue closeout carrier for v1.2.3",
            messages={"HEAD": "carrier\n\nClose #44.", "HEAD^": subject, "c-sha": subject},
            close_refs=["#44"],
            marked=("tag-sha",),
            parents={"tag-sha": "base-sha", "r-sha": "tag-sha"},
            children={"tag-sha": "r-sha"},
            evidence_changed=["scripts/some_source_file.py"],
        ),
    )
    assert carrier["phase"] == "release-content"


def test_an_operator_commit_between_the_claims_record_and_the_carrier_is_still_refused() -> None:
    """The widening is exactly the release's OWN generated commit and nothing else.

    A commit an operator authored in that window is the thing the direct-child rule exists
    to catch, so it must still fall through -- otherwise this repair would have traded a
    recoverable release for an unwatched one."""
    carrier = RESUME_STATE.resumable_state(
        Path("."),
        tag_name="v1.2.3",
        commit_message="Release demo 1.2.3",
        remote="origin",
        branch="main",
        backend={},
        record_path=_RECORD_PATH,
        cli=_ClassifierCli(
            revs={"HEAD": "carrier-sha", "HEAD^": "x-sha", "x-sha^": "r-sha", "tag": "tag-sha"},
            subject="Record release issue closeout carrier for v1.2.3",
            messages={
                "HEAD": "carrier\n\nClose #44.",
                "HEAD^": "docs: a stray operator edit",
                "x-sha": "docs: a stray operator edit",
            },
            close_refs=["#44"],
            marked=("tag-sha",),
            parents={"tag-sha": "base-sha", "r-sha": "tag-sha"},
            children={"tag-sha": "r-sha"},
        ),
    )
    assert carrier["phase"] == "release-content"


def test_the_artifact_commit_pathspec_covers_the_adapter_record_without_a_phantom() -> None:
    """`git add` exits 128 on a pathspec matching nothing (`git status` does not), and
    `cli.run` is check=True -- so a candidate list containing an absent path would kill a
    consumer's resume mid-lane. The caller statuses each candidate separately; this pins
    what the candidates ARE, including the repo-root record whose directory is `.` and
    would otherwise sweep the whole worktree or be dropped entirely."""
    cases = {
        "charness-artifacts/release/latest.md": ["charness-artifacts"],
        "charness-artifacts/latest.md": ["charness-artifacts"],
        "artifacts/release/latest.md": ["charness-artifacts", "artifacts/release"],
        # The trailing slash in the prefix test is what keeps this a distinct directory.
        "charness-artifacts-old/release/latest.md": [
            "charness-artifacts",
            "charness-artifacts-old/release",
        ],
        # `output_dir: .` or blank: the record FILE, never `.` as a pathspec.
        "latest.md": ["charness-artifacts", "latest.md"],
    }
    for record_path, expected in cases.items():
        assert RESUME._artifact_commit_candidates(record_path) == expected, record_path


def test_the_claims_resume_lane_runs_the_notes_file_preflight_before_publishing() -> None:
    """A floor that fires at PREPARE time did not fire at the boundary that publishes.
    The prepare always stops at the marked record, so this lane is the only path to
    `create_release`, and it ran no notes preflight at all -- a resume that dropped
    `--notes-file` published `--generate-notes` instead of the notes the prepare
    validated, with nothing refusing it. Twice: once early for a cheap message, once
    immediately before the irreversible step, which is the call that is actually a gate."""
    preflights: list[dict] = []
    notes = Path("charness-artifacts/release/notes-v1.2.3.md")

    _resume_claims_publication_leg(
        remote_branch_sha="old-branch",
        tag_remote=True,
        release_exists=False,
        notes_file=notes,
        notes_preflights=preflights,
    )

    assert [call["target_tag"] for call in preflights] == ["v1.2.3", "v1.2.3"]
    assert all(call["notes_file"] == notes.resolve() for call in preflights)
    # The resume-aware remedy arm: the generic blocker tells the operator to delete the
    # drafted notes AND COMMIT that, which strands a resume behind a third commit.
    assert all(call["on_resume"] is True for call in preflights)
    # The OUTGOING version reaches the lint on this lane. The manifest is already bumped
    # here, so `_known_versions` reads the version being CUT from it -- and without this
    # argument a rollback paragraph naming the outgoing version is grounded at prepare and
    # ungrounded at publish. That refusal lands where the only remedy (edit the notes) puts
    # a commit on top of the claims record and makes the resume unreachable, so the
    # asymmetry had to be closed on the lane, not left to the operator.
    assert all(call["previous_version"] == "1.2.2" for call in preflights)


@pytest.mark.parametrize(("release_exists", "expected_calls"), [(True, 0), (False, 2)])
def test_the_notes_preflight_fires_exactly_when_a_body_can_still_be_attached(
    release_exists: bool, expected_calls: int
) -> None:
    """Both directions in one test, because `preflights == []` alone is satisfied equally
    by "the guard works" and by "both production calls were deleted".

    When the release already exists this resume is repairing a missing branch or tag push
    and cannot attach a body at all, so the blocker's premise ("the published body would be
    auto-generated") is false and refusing on it would be a wrong stop."""
    preflights: list[dict] = []

    commands, committed = _resume_claims_publication_leg(
        remote_branch_sha="old-branch",
        tag_remote=True,
        release_exists=release_exists,
        notes_file=None,
        notes_preflights=preflights,
    )

    assert len(preflights) == expected_calls
    # The gate must not create the state it then refuses: the second call sits ABOVE the
    # artifact commit, so a refusal there leaves no third commit for the next resume to
    # fail to classify.
    if expected_calls:
        assert committed == ["artifact"]
        assert commands, "the preflight must not be the only thing this lane did"


def test_a_state_classified_against_another_record_path_cannot_publish() -> None:
    """The state is classified against ONE release record path; everything after it
    writes, commits, and reports against the path derived from the adapter. Production
    always passes a preflighted state, which is exactly the kind of invariant that holds
    until a second caller appears."""
    commands: list[list[str]] = []
    state = {
        "phase": "prepared-claims-review",
        "tag_local": True,
        "tag_remote": False,
        "remote_branch_sha": "old-branch",
        "claims_evidence_commit": "claims-evidence",
        "head_sha": "claims-evidence",
        "prepared": {"commit": "prepared"},
        "release_exists": True,
        "record_path": "artifacts/release/latest.md",
    }
    plan = {
        "payload": {"commit_message": "Release v1.2.3"},
        "tag_name": "v1.2.3",
        "branch": "main",
        "backend": "github",
        "issue_repo": "example/demo",
        "release_content_paths": [],
        "title": "v1.2.3",
    }
    args = SimpleNamespace(execute=True, remote="origin", notes_file=None, close_issue=[])

    with pytest.raises(SystemExit, match="refusing to publish across two record paths"):
        RESUME_PUBLISH.resume_publish(
            _ISOLATED_RESUME_REPO,
            args=args,
            plan=plan,
            adapter_data=_ADAPTER,
            cli=_ClaimsResumeCli(commands),
            state=state,
            resumable_state=lambda *_a, **_k: state,
            assert_resumable=lambda *_a, **_k: None,
            common=_ClaimsResumeCommon(),
            resume_closeout=SimpleNamespace(),
            commit_artifact_before_push=lambda *_a, **_k: None,
            release_record_path=CLAIMS.release_record_path,
        )
    assert commands == []


def test_a_claims_phase_without_a_validated_review_cannot_publish() -> None:
    """The claims floor lives in `preflight_resume_state`, a different function from the
    one that publishes. A reconstructed state can resolve to a claims phase, pass
    `assert_resumable`, carry no `claims_review`, and reach tag/push/release create --
    the exact "publishing path that never calls validate_claims_review" shape this lane
    was repaired for, preserved one caller away."""
    commands: list[list[str]] = []
    state = {
        "phase": "prepared-claims-review",
        "tag_local": True,
        "tag_remote": False,
        "remote_branch_sha": "old-branch",
        "claims_evidence_commit": "claims-evidence",
        "head_sha": "claims-evidence",
        "prepared": {"commit": "prepared"},
        "release_exists": True,
        "record_path": _RECORD_PATH,
    }
    plan = {
        "payload": {"commit_message": "Release v1.2.3"},
        "tag_name": "v1.2.3",
        "branch": "main",
        "backend": "github",
        "issue_repo": "example/demo",
        "release_content_paths": [],
        "title": "v1.2.3",
    }
    args = SimpleNamespace(execute=True, remote="origin", notes_file=None, close_issue=[])

    with pytest.raises(SystemExit, match="requires a validated claims review"):
        RESUME_PUBLISH.resume_publish(
            _ISOLATED_RESUME_REPO,
            args=args,
            plan=plan,
            adapter_data=_ADAPTER,
            cli=_ClaimsResumeCli(commands),
            state=state,
            resumable_state=lambda *_a, **_k: state,
            assert_resumable=lambda *_a, **_k: None,
            common=_ClaimsResumeCommon(),
            resume_closeout=SimpleNamespace(),
            commit_artifact_before_push=lambda *_a, **_k: None,
            release_record_path=CLAIMS.release_record_path,
        )
    assert commands == [], "refused before any git or gh command"


def test_the_marker_refusal_names_a_safe_recovery_after_publication() -> None:
    """The refusal's recovery text is read at a boundary where the wrong advice is
    destructive. Before publication "reset to one prepared record" is right; AFTER the tag
    is pushed and the release exists it would rewrite history behind a published tag and
    discard the committed claims record, so that state gets its own sentence."""
    for published, expected, forbidden in (
        (False, "reset to one prepared record", "already pushed"),
        (True, "do NOT reset past the claims record", "reset to one prepared record"),
    ):
        state = {
            "marker_at_head": True,
            "phase": "release-content",
            "head_is_release_commit": True,
            "tag_local": published,
            "tag_remote": published,
            "release_exists": published,
            "tag_points_at_head": published,
            "prepared": None,
            "remote_tag_sha": "tag",
            "tag_sha": "tag",
            "head_sha": "head",
            "remote_branch_sha": "",
            "claims_evidence_commit": "",
        }
        with pytest.raises(SystemExit) as excinfo:
            RESUME.assert_resumable(state, tag_name="v1.2.3")
        message = str(excinfo.value)
        assert "no single-parent prepared boundary" in message
        assert expected in message
        assert forbidden not in message


def test_a_claims_artifact_the_phase_will_not_read_is_refused_in_process() -> None:
    """Only reachable through a CLI subprocess otherwise, which in-process coverage
    cannot see — and a refusal nobody exercised is a floor nobody proved."""
    CLAIMS.assert_claims_artifact_is_read("prepared-claims-review", "a/b.json")
    CLAIMS.assert_claims_artifact_is_read("release-content", None)
    for phase in ("release-content", "post-publication-carrier", "post-publication-final"):
        with pytest.raises(SystemExit, match="does not read it"):
            CLAIMS.assert_claims_artifact_is_read(phase, "charness-artifacts/release-review/r.json")


def test_the_unproven_warning_fires_only_for_an_unproven_verdict() -> None:
    """Publication proceeds on `unproven`. The published release record now carries the
    verdict too, but that record is read after the fact by someone outside the session;
    stderr is what puts it in front of the operator standing at the boundary, while there
    is still a decision to make."""
    written: list[str] = []
    CLAIMS.unproven_claims_warning(
        {"verdict": "unproven", "observer_distinctness": {"signal": "host refused the spawn"}},
        write=written.append,
    )
    assert len(written) == 1
    assert "verdict is `unproven`" in written[0]
    assert "host refused the spawn" in written[0]

    for quiet in ({"verdict": "pass", "observer_distinctness": {"signal": "s"}}, {}):
        written.clear()
        CLAIMS.unproven_claims_warning(quiet, write=written.append)
        assert written == []


def test_pre_push_quality_receipt_is_promoted_before_release_scratch_closes(tmp_path: Path) -> None:
    owner = owned_scratch(
        tmp_path,
        "release-prepush-quality",
        run_id="receipt",
        runtime_root_path=tmp_path / ".runtime",
    )
    receipt_path = owner.open() / "receipt.json"
    receipt_path.write_text('{"verified_head":"abc"}\n', encoding="utf-8")
    payload: dict = {}
    destination = tmp_path / "charness-artifacts" / "release" / "1.2.3-prepush-quality.json"
    destination.parent.mkdir(parents=True)
    destination.write_text('{"verified_head":"stale"}\n', encoding="utf-8")
    payload["prepush_quality_receipt"] = str(destination.relative_to(tmp_path))

    RESUME_PUBLISH._promote_quality_receipt(
        tmp_path,
        owner=owner,
        receipt_path=receipt_path,
        record_path="charness-artifacts/release/latest.md",
        tag_name="v1.2.3",
        payload=payload,
    )
    owner.close(state="succeeded")

    durable = destination
    assert durable.read_text(encoding="utf-8") == '{"verified_head":"abc"}\n'
    assert payload["prepush_quality_receipt"] == str(durable.relative_to(tmp_path))
    assert payload["prepush_quality_receipt_sha256"]
    assert not (tmp_path / ".runtime" / "scratch" / "release-prepush-quality" / "receipt").exists()


def _tailed_scripted_run(answers: dict[tuple[str, ...], tuple[int, str]]):
    """A `run` carrying per-command git return codes for the tail-boundary tests.

    The walk and the resume classifier ask only git reads; unanswered commands
    raise so a test cannot pass by silently inventing history.
    """
    def run(command, *, cwd=None, check=False):  # noqa: ARG001 - mirrors the real signature
        key = tuple(str(part) for part in command)
        if key not in answers:
            raise AssertionError(f"unscripted git read: {list(key)}")
        returncode, stdout = answers[key]
        return SimpleNamespace(returncode=returncode, stdout=stdout, stderr="")

    return run


_TAILED_TAG = "v9.9.9"
_TAILED_MARKED = f"<!-- {CLAIMS.MARKER} -->\ntag `{_TAILED_TAG}`\n"
_TAILED_REVIEW_DIFF = "charness-artifacts/release-review/review.json\n"


def _tailed_walk_answers() -> dict[tuple[str, ...], tuple[int, str]]:
    """Scripted history: evidence retaining the marker atop a paperwork gap.

    `w` (the evidence commit) keeps the prepared record byte-identical, so the
    marker is present but introduced below; `p` is a record-correction commit
    without the marker; `g` is older history without it.
    """
    return {
        ("git", "rev-parse", "head"): (0, "w\n"),
        ("git", "show", f"w:{_RECORD_PATH}"): (0, _TAILED_MARKED),
        ("git", "show", "-s", "--format=%P", "w"): (0, "p\n"),
        ("git", "show", f"p:{_RECORD_PATH}"): (0, "record without marker\n"),
        ("git", "show", "-s", "--format=%P", "p"): (0, "g\n"),
        ("git", "show", f"g:{_RECORD_PATH}"): (0, "record without marker\n"),
        ("git", "show", "-s", "--format=%P", "g"): (0, ""),
    }


def test_tailed_boundary_binds_evidence_that_retains_the_marker() -> None:
    """The tail arm's happy path: walk binds, head diff is claims-shaped.

    The evidence commit does not touch the release record, so the marker is
    present at HEAD but introduced at the prepared commit below the paperwork
    gap. The walk binds the tag-bound introducer and the parent-to-head diff
    carries exactly the review record, so the outstanding release resolves.
    """
    answers = _tailed_walk_answers()
    answers[("git", "diff-tree", "--no-commit-id", "--name-only", "-r", "p", "head")] = (
        0, _TAILED_REVIEW_DIFF,
    )
    cli = SimpleNamespace(run=_tailed_scripted_run(answers))

    prepared, evidence = RESUME_STATE._tailed_claims_boundary(
        cli, Path("."), prepared=None, parent_sha="p", head_sha="head",
        tag_name=_TAILED_TAG, record_path=_RECORD_PATH,
    )

    assert evidence == "head"
    assert prepared is not None and prepared["commit"] == "w"


def test_tailed_boundary_refuses_a_head_diff_without_the_review_record() -> None:
    """The walk binding alone is not enough: R's own diff must be claims-shaped.

    A paperwork-only head above the bound introducer is a correction awaiting
    its review, not evidence carrying one -- binding it as evidence would let
    the resume publish a release whose claims were never recorded.
    """
    answers = _tailed_walk_answers()
    answers[("git", "diff-tree", "--no-commit-id", "--name-only", "-r", "p", "head")] = (
        0, "charness-artifacts/issue/note.md\n",
    )
    cli = SimpleNamespace(run=_tailed_scripted_run(answers))

    assert RESUME_STATE._tailed_claims_boundary(
        cli, Path("."), prepared=None, parent_sha="p", head_sha="head",
        tag_name=_TAILED_TAG, record_path=_RECORD_PATH,
    ) == (None, "")


def test_resumable_state_recovers_prepared_through_a_paperwork_tail() -> None:
    """The classifier's `elif tailed_evidence` arm, driven where coverage sees it.

    HEAD is the claims evidence above a record-correction gap: no tag exists
    yet, neither HEAD nor its parent introduces the marker (both inherit it),
    and no earlier arm binds -- so the direct checks decline and only the
    tail walk recognizes the outstanding release. Without this arm the resume
    reports the legacy `release-content` lane and its refusals never run.
    """
    answers = _tailed_walk_answers()
    answers.update({
        ("git", "log", "-1", "--format=%s"): (0, "Record generated claims review\n"),
        ("git", "rev-parse", "HEAD"): (0, "head\n"),
        ("git", "show", "-s", "--format=%B", "HEAD"): (0, "Record generated claims review\n"),
        ("git", "rev-parse", "HEAD^"): (0, "parent\n"),
        ("git", "show", "-s", "--format=%B", "HEAD^"): (0, "Correct fixture closeout ledger\n"),
        ("git", "ls-remote", "--heads", "origin", "refs/heads/main"): (1, ""),
        ("git", "show", f"head:{_RECORD_PATH}"): (0, "record without marker\n"),
        ("git", "show", f"parent:{_RECORD_PATH}"): (0, "record without marker\n"),
        ("git", "diff-tree", "--no-commit-id", "--name-only", "-r", "parent", "head"): (
            0, _TAILED_REVIEW_DIFF,
        ),
        ("git", "rev-parse", "w^"): (0, "parent\n"),
    })
    cli = SimpleNamespace(
        run=_tailed_scripted_run(answers),
        _helpers=SimpleNamespace(
            tag_exists=lambda repo_root, tag_name, remote=None: {
                "local": False, "remote": False, "remote_tag_sha": "",
            },
            release_exists=lambda repo_root, tag_name, backend: False,
        ),
        release_content_close_keyword_refs=lambda message: [],
    )

    state = RESUME_STATE.resumable_state(
        Path("."),
        tag_name=_TAILED_TAG,
        commit_message="Release 9.9.9",
        remote="origin",
        branch="main",
        backend={"kind": "github"},
        record_path=_RECORD_PATH,
        cli=cli,
    )

    assert state["phase"] == "prepared-claims-review"
    assert state["prepared"] is not None and state["prepared"]["commit"] == "w"
    assert state["claims_evidence_commit"] == "head"
