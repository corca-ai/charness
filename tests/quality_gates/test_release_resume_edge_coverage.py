"""Focused edge coverage for release closeout recovery helpers."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from .seeding_support import load_module

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "public" / "release" / "scripts"


def _load(name: str):
    return load_module(f"{name}_edge_coverage", SCRIPTS / f"{name}.py")


RESUME_CLOSEOUT = _load("publish_release_resume_closeout")
ISSUE_CLOSEOUT = _load("release_issue_closeout")
ISSUE_CLOSEOUT_ARTIFACT = _load("release_issue_closeout_artifact")
MESSAGE = _load("release_issue_closeout_message")
RESUME_PUBLISH = _load("publish_release_resume_publish")
RESUME = _load("publish_release_resume")
CLAIMS = _load("publish_release_claims_review")
RESUME_STATE = _load("publish_release_resume_state")
_ISOLATED_RESUME_REPO = Path(tempfile.mkdtemp(prefix="charness-resume-repo-"))


class _ClaimsResumeCli:
    def __init__(self, commands: list[list[str]], *, notes_preflights: list[dict] | None = None,
                 allow_create: bool = False, verify_returncode: int = 0,
                 version_surface_error: str | None = None):
        self.commands = commands
        self.notes_preflights = notes_preflights if notes_preflights is not None else []
        self.allow_create = allow_create
        self.verify_returncode = verify_returncode
        self.version_surface_error = version_surface_error
        self.version_surface_checks: list[dict] = []
        self.final_artifact_commits: list[dict] = []
        self.finalized_payloads: list[dict] = []

    def run(self, command, *, cwd, check=True):
        self.commands.append(command)
        return SimpleNamespace(returncode=0, stdout="https://example.test/v1.2.3")

    def run_notes_file_preflight(
        self, repo_root, *, target_tag, notes_file, on_resume=False, previous_version=None
    ):
        # Recorded, never executed against the real filesystem: the stub passes
        # an isolated temporary repo root, so a real preflight here would read the AUTHORING repo's
        # adapter and its drafted-notes directory against a fixture tag.
        # `previous_version` is recorded because the resume lane is the reason it exists:
        # the manifest is ALREADY bumped there, so without it the outgoing version is
        # ungrounded on the one lane that publishes, and the note that passed at prepare
        # is refused at the boundary whose only remedy locks the resume out.
        self.notes_preflights.append(
            {
                "target_tag": target_tag,
                "notes_file": notes_file,
                "on_resume": on_resume,
                "previous_version": previous_version,
            }
        )

    @staticmethod
    def backend_command(_backend, _operation, fallback):
        return fallback

    @staticmethod
    def release_content_close_keyword_refs(_text):
        return []

    @staticmethod
    def run_fresh_checkout_probes(_root):
        return {"status": "passed"}

    @staticmethod
    def expected_github_release_url(_root, _backend, _tag):
        return "https://example.test/v1.2.3"

    def ensure_release_surface(self, _repo_root, expected_version, *, stage):
        self.version_surface_checks.append({"version": expected_version, "stage": stage})
        if self.version_surface_error:
            raise SystemExit(self.version_surface_error)
        return {
            "status": "passed",
            "stage": stage,
            "checked_version": expected_version,
            "surfaces": ["packaging/charness.json", "plugins/charness/.codex-plugin/plugin.json"],
            "drift": [],
        }

    def verify_release_visible(self, *_args, **_kwargs):
        return SimpleNamespace(
            returncode=self.verify_returncode, args=["gh", "release", "view", "v1.2.3"],
            stdout="", stderr="release not found",
        )

    def finalize_release_payload(self, _repo_root, payload, **_kwargs):
        self.finalized_payloads.append(dict(payload))

    def commit_final_release_artifact(self, *_args, **kwargs):
        self.final_artifact_commits.append(kwargs)

    @staticmethod
    def fail_after_post_create_verification(_payload, *, verification_result):
        # The real one renders `payload` keys that `finalize_release_payload` fills in;
        # that stub is a no-op here, so the stub asserts only the contract this harness
        # can honestly hold: it raises, and it raises with the verification exit code.
        raise SystemExit(
            "release post-create verification failed after external mutation\n"
            f"exit_code: {verification_result.returncode}"
        )

    def create_release(self, *_args, **_kwargs):
        if not self.allow_create:
            raise AssertionError("existing release should not be created again")
        return SimpleNamespace(returncode=0, stdout="https://example.test/v1.2.3")


class _ClaimsResumeCommon:
    @staticmethod
    def preflight_close_issue_carrier(*_args, **_kwargs):
        return None

    @staticmethod
    def run_pre_push_quality_gates(*_args, **_kwargs):
        return None

    @staticmethod
    def timed(_payload, _label, action):
        return action()

    @staticmethod
    def run_release_closeout_tail(*_args, **_kwargs):
        return None


_ADAPTER = {"output_dir": "charness-artifacts/release"}
_RECORD_PATH = "charness-artifacts/release/latest.md"


def _resume_claims_publication_leg(
    *, remote_branch_sha: str, tag_remote: bool, release_exists: bool = True,
    notes_file=None, notes_preflights: list[dict] | None = None,
    verify_returncode: int = 0, cli_out: list | None = None,
) -> tuple[list[list[str]], list[str]]:
    commands: list[list[str]] = []
    committed: list[str] = []
    state = {
        "phase": "prepared-claims-review", "tag_local": True, "tag_remote": tag_remote,
        "remote_branch_sha": remote_branch_sha, "claims_evidence_commit": "claims-evidence",
        "head_sha": "claims-evidence", "prepared": {"commit": "prepared"},
        "release_exists": release_exists, "record_path": _RECORD_PATH,
        # The real `preflight_resume_state` always sets this for a claims phase, and
        # `resume_publish` now refuses a claims phase without it -- a reconstructed state
        # must not be able to reach tag/push/release create with the floor unrun.
        "claims_review": {
            "path": "charness-artifacts/release-review/edge.json",
            "verdict": "pass",
            "observer_distinctness": {
                "kind": "separate-agent-context", "signal": "edge-coverage fixture",
                "review_artifact": "charness-artifacts/release-review/edge.md",
            },
        },
    }
    plan = {
        # `previous_version` is what the real planner carries and what the notes lint must
        # ground on this lane; the fixture would otherwise pin the defect as intended.
        "payload": {"commit_message": "Release v1.2.3", "previous_version": "1.2.2"},
        "tag_name": "v1.2.3", "branch": "main",
        "backend": "github", "issue_repo": "example/demo", "release_content_paths": [], "title": "v1.2.3",
    }
    args = SimpleNamespace(execute=True, remote="origin", notes_file=notes_file, close_issue=[])
    cli = _ClaimsResumeCli(commands, notes_preflights=notes_preflights, allow_create=not release_exists,
                           verify_returncode=verify_returncode)
    if cli_out is not None:
        cli_out.append(cli)
    RESUME_PUBLISH.resume_publish(
        _ISOLATED_RESUME_REPO, args=args, plan=plan, adapter_data=_ADAPTER,
        cli=cli,
        state=state,
        resumable_state=lambda *_args, **_kwargs: state, assert_resumable=lambda *_args, **_kwargs: None,
        common=_ClaimsResumeCommon(), resume_closeout=SimpleNamespace(),
        commit_artifact_before_push=lambda *_args, **_kwargs: committed.append("artifact"),
        release_record_path=CLAIMS.release_record_path,
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
            remote_branch_sha="claims-evidence", tag_remote=True,
            verify_returncode=1, cli_out=clis,
        )

    assert len(clis[0].final_artifact_commits) == 1, (
        "the failure arm must persist the release artifact before refusing; the tag and "
        "the release already exist by the time verification runs"
    )
    assert clis[0].final_artifact_commits[0]["has_issue_closeout"] is False


def test_resume_closeout_requires_original_irreversible_inputs() -> None:
    args = SimpleNamespace(
        close_issue=[], close_issue_classification=None, close_issue_carrier_file=None,
        close_issue_behavior=[], close_issue_probe_record=[],
    )

    with pytest.raises(SystemExit, match="Recovery never infers or omits issue-close context") as error:
        RESUME_CLOSEOUT._require_closeout_resume_inputs(args)

    for flag in (
        "--close-issue", "--close-issue-classification",
        "--close-issue-carrier-file", "--close-issue-behavior",
    ):
        assert flag in str(error.value)


class _ResumeCli:
    def __init__(self, *, changed: list[str], files: dict[str, str], push_error: bool = False, remote_sha: str = ""):
        self.changed = changed
        self.files = files
        self.push_error = push_error
        self.remote_sha = remote_sha
        self.commands: list[list[str]] = []

    def run(self, command, *, cwd, check=True):
        self.commands.append(command)
        if command[:2] == ["git", "show"]:
            path = command[2].split(":", 1)[1]
            return SimpleNamespace(returncode=0 if path in self.files else 1, stdout=self.files.get(path, ""))
        if command[:3] == ["git", "diff-tree", "--no-commit-id"]:
            return SimpleNamespace(returncode=0, stdout="\n".join(self.changed))
        if command[:2] == ["git", "push"]:
            if self.push_error:
                raise RuntimeError("connection lost after remote receipt")
            return SimpleNamespace(returncode=0, stdout="")
        if command[:2] == ["git", "ls-remote"]:
            return SimpleNamespace(returncode=0, stdout=f"{self.remote_sha}\trefs/heads/main\n")
        raise AssertionError(f"unexpected command: {command}")

    @staticmethod
    def validate_release_observer_record(_record):
        return None

    @staticmethod
    def validate_release_closeout_commit_message(*_args, **_kwargs):
        return {"ok": True}


def test_resume_commit_file_refuses_missing_evidence() -> None:
    cli = _ResumeCli(changed=[], files={})

    with pytest.raises(SystemExit, match="does not contain required evidence"):
        RESUME_CLOSEOUT._commit_file(Path("."), commit_ref="HEAD", path="missing.json", cli=cli)


def test_resume_carrier_tree_refuses_wrong_tag_and_unbound_artifact() -> None:
    observer = "charness-artifacts/probe/demo-v1.2.3-release-observer.json"
    common = {"tag_name": "v9.9.9"}
    cli = _ResumeCli(
        changed=["charness-artifacts/release/latest.md", observer],
        files={
            "charness-artifacts/release/latest.md": "carrier-pending-state-verification",
            observer: json.dumps({"target": {"tag": "v9.9.9"}}),
        },
    )
    with pytest.raises(SystemExit, match="targets a different release tag"):
        RESUME_CLOSEOUT._validate_carrier_evidence_tree(
            Path("."), commit_ref="HEAD", artifact_relpath="charness-artifacts/release/latest.md",
            tag_name="v1.2.3", payload=common, cli=cli,
        )

    cli.files[observer] = json.dumps({"target": {"tag": "v1.2.3"}})
    cli.files["charness-artifacts/release/latest.md"] = "carrier-pending-state-verification"
    with pytest.raises(SystemExit, match="does not bind its observer"):
        RESUME_CLOSEOUT._validate_carrier_evidence_tree(
            Path("."), commit_ref="HEAD", artifact_relpath="charness-artifacts/release/latest.md",
            tag_name="v1.2.3", payload={}, cli=cli,
        )


def test_resume_carrier_refuses_validation_that_does_not_match_preflight() -> None:
    cli = _ResumeCli(changed=[], files={})
    payload = {"issue_closeout_draft_validation": {"commit_message": "expected"}}
    with pytest.raises(SystemExit, match="does not exactly match"):
        RESUME_CLOSEOUT._validated_carrier_message(
            Path("."), args=SimpleNamespace(close_issue=[44], close_issue_classification="bug"),
            issue_repo="example/demo", payload=payload, commit_message="different", commit_ref="HEAD",
            artifact_relpath="charness-artifacts/release/latest.md", tag_name="v1.2.3", cli=cli,
        )
    assert payload["resume_carrier_validation"]["matches_preflight_draft"] is False


def test_resume_reconciles_ambiguous_push_after_remote_receipt() -> None:
    cli = _ResumeCli(changed=[], files={}, push_error=True, remote_sha="carrier-sha")
    payload: dict = {}
    RESUME_CLOSEOUT._reconcile_push(
        Path("."), state={"remote_branch_sha": "old-sha", "head_sha": "carrier-sha"},
        remote="origin", branch="main", payload=payload, cli=cli,
    )
    assert payload["resume_remote_reconcile"] == {"status": "push-error-but-shared", "sha": "carrier-sha"}
    assert ["git", "ls-remote", "--heads", "origin", "refs/heads/main"] in cli.commands


def test_resume_refuses_ambiguous_push_when_remote_identity_differs() -> None:
    cli = _ResumeCli(changed=[], files={}, push_error=True, remote_sha="other-sha")

    with pytest.raises(RuntimeError, match="connection lost"):
        RESUME_CLOSEOUT._reconcile_push(
            Path("."), state={"remote_branch_sha": "old-sha", "head_sha": "carrier-sha"},
            remote="origin", branch="main", payload={}, cli=cli,
        )


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


class _ClassifierCli:
    """Enough git for `resumable_state`, and nothing that can reach a real repo.

    The end-to-end resume tests drive this classifier through `subprocess`, which is the
    honest way to test a CLI and leaves its phase arms invisible to in-process coverage --
    so the changed-line mutation gate reads them as untested, which is what it did.
    """

    MARKER = "charness-release-state:prepared-awaiting-claims-review"

    def __init__(self, *, revs: dict[str, str], subject: str, messages: dict[str, str],
                 tag_local: bool = True, close_refs: list[str] | None = None,
                 marked: tuple[str, ...] = (), parents: dict[str, str] | None = None,
                 children: dict[str, str] | None = None, evidence_changed: list[str] | None = None):
        self.revs = revs
        self.subject = subject
        self.messages = messages
        self.tag_local = tag_local
        self.close_refs = close_refs or []
        # Commits whose release record carries the prepared marker. `prepared_record` also
        # requires a single parent that does NOT carry it, so `parents` drives that arm.
        self.marked = marked
        self.parents = parents or {}
        self.children = children or {}
        self.evidence_changed = evidence_changed or ["charness-artifacts/release-review/r.json"]
        self._helpers = SimpleNamespace(
            tag_exists=lambda *_a, **_k: {"local": tag_local, "remote": True, "remote_tag_sha": revs.get("tag", "")},
            release_exists=lambda *_a, **_k: True,
        )

    def run(self, command, *, cwd, check=True):
        args = command[1:]
        if args[:2] == ["log", "-1"]:
            return SimpleNamespace(returncode=0, stdout=self.subject)
        if args[:1] == ["rev-parse"]:
            return SimpleNamespace(returncode=0, stdout=self.revs.get(args[1], ""))
        if args[:3] == ["show", "-s", "--format=%P"]:
            parent = self.parents.get(args[-1])
            return SimpleNamespace(returncode=0 if parent is not None else 1, stdout=parent or "")
        if args[:2] == ["show", "-s"]:
            return SimpleNamespace(returncode=0, stdout=self.messages.get(args[-1], ""))
        if args[:1] == ["show"]:
            commit = args[1].split(":", 1)[0]
            if commit in self.marked:
                return SimpleNamespace(returncode=0, stdout=f"# Release\n<!-- {self.MARKER} -->\n")
            # An unmarked record still EXISTS; only the marker decides a prepared boundary.
            return SimpleNamespace(returncode=0, stdout="# Release\n")
        if args[:1] == ["rev-list"] and "--all" in args:
            return SimpleNamespace(
                returncode=0,
                stdout="".join(f"{child} {parent}\n" for parent, child in self.children.items()),
            )
        if args[:1] == ["rev-list"]:
            return SimpleNamespace(returncode=0, stdout=self.revs.get("tag", ""))
        if args[:2] == ["diff-tree", "--no-commit-id"]:
            return SimpleNamespace(returncode=0, stdout="\n".join(self.evidence_changed))
        if args[:1] == ["merge-base"]:
            return SimpleNamespace(returncode=0, stdout="")
        if args[:1] == ["ls-remote"]:
            return SimpleNamespace(returncode=0, stdout="remote-sha\trefs/heads/main\n")
        raise AssertionError(f"unexpected command: {command}")

    def release_content_close_keyword_refs(self, text):
        return list(self.close_refs) if "Close #" in text else []


def test_the_post_publication_phase_arms_classify_in_process() -> None:
    """The two closeout arms the subprocess tests reach only through a full publish."""
    carrier = RESUME_STATE.resumable_state(
        Path("."), tag_name="v1.2.3", commit_message="Release demo 1.2.3", remote="origin",
        branch="main", backend={}, record_path=_RECORD_PATH,
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
        Path("."), tag_name="v1.2.3", commit_message="Release demo 1.2.3", remote="origin",
        branch="main", backend={}, record_path=_RECORD_PATH,
        cli=_ClassifierCli(
            revs={"HEAD": "final-sha", "HEAD^": "carrier-sha", "HEAD^^": "tag-sha", "tag": "tag-sha"},
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
        Path("."), tag_name="v1.2.3", commit_message="Release demo 1.2.3", remote="origin",
        branch="main", backend={}, record_path=_RECORD_PATH,
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
        Path("."), tag_name="v1.2.3", commit_message="Release demo 1.2.3", remote="origin",
        branch="main", backend={}, record_path=_RECORD_PATH,
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
        Path("."), tag_name="v1.2.3", commit_message="Release demo 1.2.3", remote="origin",
        branch="main", backend={}, record_path=_RECORD_PATH,
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
        RESUME_STATE.claims_evidence_boundary(cli, Path("."), "c0", tag_name="v1.2.3")
        == RESUME_STATE._BOUNDARY_WALK_EXHAUSTED
    )
    # The sentinel is not a commit id and not the empty string a failed rev-parse yields,
    # so a reader debugging a refused resume can tell the two apart.
    assert RESUME_STATE._BOUNDARY_WALK_EXHAUSTED not in {"", None}


def test_a_forged_artifact_commit_subject_does_not_open_the_boundary() -> None:
    """Subject alone is copyable off `git log`; content is not.

    `git commit --allow-empty -m "chore(release): commit v1.2.3 artifact before resume
    push"` over staged content would otherwise be walked past, and the run would tag,
    push, create the release and close issues over content the reviewed claims record
    does not cover — while binding publication to that record is the boundary's whole
    purpose. Here the commit carries the right subject and touches a path outside the
    generated-artifact tree.
    """
    subject = RESUME_STATE.release_artifact_commit_subject("v1.2.3")
    carrier = RESUME_STATE.resumable_state(
        Path("."), tag_name="v1.2.3", commit_message="Release demo 1.2.3", remote="origin",
        branch="main", backend={}, record_path=_RECORD_PATH,
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
        Path("."), tag_name="v1.2.3", commit_message="Release demo 1.2.3", remote="origin",
        branch="main", backend={}, record_path=_RECORD_PATH,
        cli=_ClassifierCli(
            revs={"HEAD": "carrier-sha", "HEAD^": "x-sha", "x-sha^": "r-sha", "tag": "tag-sha"},
            subject="Record release issue closeout carrier for v1.2.3",
            messages={"HEAD": "carrier\n\nClose #44.", "HEAD^": "docs: a stray operator edit",
                      "x-sha": "docs: a stray operator edit"},
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
        "charness-artifacts-old/release/latest.md": ["charness-artifacts", "charness-artifacts-old/release"],
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
        remote_branch_sha="old-branch", tag_remote=True, release_exists=False,
        notes_file=notes, notes_preflights=preflights,
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
        remote_branch_sha="old-branch", tag_remote=True, release_exists=release_exists,
        notes_file=None, notes_preflights=preflights,
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
        "phase": "prepared-claims-review", "tag_local": True, "tag_remote": False,
        "remote_branch_sha": "old-branch", "claims_evidence_commit": "claims-evidence",
        "head_sha": "claims-evidence", "prepared": {"commit": "prepared"},
        "release_exists": True, "record_path": "artifacts/release/latest.md",
    }
    plan = {
        "payload": {"commit_message": "Release v1.2.3"}, "tag_name": "v1.2.3", "branch": "main",
        "backend": "github", "issue_repo": "example/demo", "release_content_paths": [], "title": "v1.2.3",
    }
    args = SimpleNamespace(execute=True, remote="origin", notes_file=None, close_issue=[])

    with pytest.raises(SystemExit, match="refusing to publish across two record paths"):
        RESUME_PUBLISH.resume_publish(
            _ISOLATED_RESUME_REPO, args=args, plan=plan, adapter_data=_ADAPTER, cli=_ClaimsResumeCli(commands),
            state=state, resumable_state=lambda *_a, **_k: state,
            assert_resumable=lambda *_a, **_k: None, common=_ClaimsResumeCommon(),
            resume_closeout=SimpleNamespace(),
            commit_artifact_before_push=lambda *_a, **_k: None,
            release_record_path=CLAIMS.release_record_path,
        )
    assert commands == []


def test_resume_dry_run_validates_carrier_without_reconciling(capsys) -> None:
    observer = "charness-artifacts/probe/demo-v1.2.3-release-observer.json"
    message = "carrier message"
    cli = _ResumeCli(
        changed=["charness-artifacts/release/latest.md", observer],
        files={
            "charness-artifacts/release/latest.md": f"{observer}\ncarrier-pending-state-verification",
            observer: json.dumps({"target": {"tag": "v1.2.3"}}),
        },
    )
    args = SimpleNamespace(
        execute=False, close_issue=[44], close_issue_classification="bug",
        close_issue_carrier_file=Path("carrier.md"),
        close_issue_behavior=["Behavior #44: fixture"],
        close_issue_probe_record=["Probe record #44: local-only-by-contract"], remote="origin",
    )
    plan = {
        "payload": {"issue_closeout_draft_validation": {"commit_message": message}},
        "issue_repo": "example/demo", "tag_name": "v1.2.3", "branch": "main",
    }
    state = {"phase": "post-publication-carrier", "head_message": message, "head_sha": "carrier-sha",
             "remote_branch_sha": "old-sha", "record_path": _RECORD_PATH}
    common = SimpleNamespace(preflight_close_issue_carrier=lambda *_args, **_kwargs: None)

    RESUME_CLOSEOUT.resume_post_publication_closeout(
        Path("."), args=args, plan=plan, adapter_data={"output_dir": "charness-artifacts/release"},
        state=state, common=common, cli=cli,
    )
    # The payload is YAML now, and `emit_yaml` line-wraps long scalars, so pin
    # the parsed field rather than a raw-stdout substring.
    assert yaml.safe_load(capsys.readouterr().out)["resume"] == (
        "dry-run: would reconcile post-publication-carrier against the remote branch"
    )
    assert not any(command[:2] == ["git", "push"] for command in cli.commands)


def test_carrier_artifact_refuses_missing_preflight_paragraphs() -> None:
    with pytest.raises(SystemExit, match="carrier paragraphs are missing"):
        ISSUE_CLOSEOUT_ARTIFACT.commit_issue_closeout_carrier_artifact(
            Path("."), write_artifact=lambda **_kwargs: None, payload={}, fresh_checkout_payload={},
            artifact_relpath="charness-artifacts/release/latest.md", expected_release_url=None,
            remote="origin", branch="main", run=lambda *_args, **_kwargs: None,
        )


def test_missing_artifact_action_is_typed_on_the_real_module(monkeypatch) -> None:
    monkeypatch.setattr(ISSUE_CLOSEOUT, "_ARTIFACT", None)
    monkeypatch.setattr(ISSUE_CLOSEOUT, "_ARTIFACT_ERROR", "forced missing helper")

    with pytest.raises(SystemExit, match="artifact helper is unavailable in this installation"):
        ISSUE_CLOSEOUT._artifact_action("commit_issue_closeout_artifact")()


def test_closeout_artifact_owner_stages_observer_and_commits_both_phases() -> None:
    commands: list[list[str]] = []
    writes: list[dict] = []

    def run(command, *, cwd):
        commands.append(command)
        return SimpleNamespace(stdout="commit-sha\n")

    common = {
        "tag_name": "v1.2.3",
        "issue_closeout": {"status": "state-verified"},
        "release_observer": {"path": "charness-artifacts/probe/observer.json"},
    }
    ISSUE_CLOSEOUT_ARTIFACT.commit_issue_closeout_artifact(
        Path("."), write_artifact=lambda **kwargs: writes.append(kwargs), payload=common,
        fresh_checkout_payload={"status": "passed"},
        artifact_relpath="charness-artifacts/release/latest.md",
        expected_release_url="https://example.test/v1.2.3", remote="origin", branch="main", run=run,
    )
    assert commands[0] == [
        "git", "add", "charness-artifacts/release/latest.md",
        "charness-artifacts/probe/observer.json",
    ]
    assert common["issue_closeout_commit_sha"] == "commit-sha"

    commands.clear()
    carrier = {
        "issue_closeout_draft_validation": {"paragraphs": ["Release v1.2.3", "Close #44."]},
        "issue_closeout_preflight": {"repo": "example/demo", "issues": [{"number": 44}]},
        # An observer record is now a PRECONDITION of this commit, not decoration: pushing
        # it is what auto-closes the issues. The earlier version of this fixture omitted it
        # and so pinned the defect -- a carrier that closes eleven issues while the evidence
        # for the close was never written.
        "release_observer": {"path": "charness-artifacts/probe/observer.json"},
    }
    ISSUE_CLOSEOUT_ARTIFACT.commit_issue_closeout_carrier_artifact(
        Path("."), write_artifact=lambda **kwargs: writes.append(kwargs), payload=carrier,
        fresh_checkout_payload={}, artifact_relpath="charness-artifacts/release/latest.md",
        expected_release_url=None, remote="origin", branch="main", run=run,
    )
    assert commands[0] == [
        "git", "add", "charness-artifacts/release/latest.md",
        "charness-artifacts/probe/observer.json",
    ]
    assert commands[1] == ["git", "commit", "-m", "Release v1.2.3", "-m", "Close #44."]
    assert carrier["issue_closeout"]["status"] == "carrier-pending-state-verification"
    assert carrier["issue_closeout_carrier_commit_sha"] == "commit-sha"
    assert len(writes) == 2


def test_the_carrier_refuses_to_close_issues_when_the_observer_capture_failed() -> None:
    """`safe_write_release_observer` swallows every exception into `capture_error`.

    Nothing between that and this commit refused, so a failed observer write closed the
    whole issue set with its distinct-channel evidence missing -- and then made recovery
    impossible, because `_validate_carrier_evidence_tree` refuses a carrier tree without
    exactly one observer record. Asserted at the point the NEXT statement is irreversible.
    """
    commands: list[list[str]] = []
    payload = {
        "tag_name": "v1.2.3",
        "issue_closeout_draft_validation": {"paragraphs": ["Release v1.2.3", "Close #44."]},
        "issue_closeout_preflight": {"repo": "example/demo", "issues": [{"number": 44}]},
        "release_observer": {"status": "capture_error", "path": None},
    }
    with pytest.raises(SystemExit, match="release observer record was not written"):
        ISSUE_CLOSEOUT_ARTIFACT.commit_issue_closeout_carrier_artifact(
            Path("."), write_artifact=lambda **kwargs: None, payload=payload,
            fresh_checkout_payload={}, artifact_relpath="charness-artifacts/release/latest.md",
            expected_release_url=None, remote="origin", branch="main",
            run=lambda command, *, cwd: commands.append(command),
        )
    # The refusal lands BEFORE any git call. A refusal after `git add`/`git commit` would
    # leave the carrier staged for the next operator command to push by hand.
    assert commands == []


def test_release_content_close_refs_refuses_when_issue_verifier_is_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(MESSAGE, "_ISSUE_VERIFY_CLOSEOUT", None)
    monkeypatch.setattr(MESSAGE, "_ISSUE_CLOSEOUT_DRAFT_ERROR", "issue skill missing (forced)")
    with pytest.raises(SystemExit, match="requires the issue skill's closeout helper"):
        MESSAGE.release_content_close_keyword_refs("Release\n\nClose #44.")


def test_a_claims_phase_without_a_validated_review_cannot_publish() -> None:
    """The claims floor lives in `preflight_resume_state`, a different function from the
    one that publishes. A reconstructed state can resolve to a claims phase, pass
    `assert_resumable`, carry no `claims_review`, and reach tag/push/release create --
    the exact "publishing path that never calls validate_claims_review" shape this lane
    was repaired for, preserved one caller away."""
    commands: list[list[str]] = []
    state = {
        "phase": "prepared-claims-review", "tag_local": True, "tag_remote": False,
        "remote_branch_sha": "old-branch", "claims_evidence_commit": "claims-evidence",
        "head_sha": "claims-evidence", "prepared": {"commit": "prepared"}, "release_exists": True,
        "record_path": _RECORD_PATH,
    }
    plan = {
        "payload": {"commit_message": "Release v1.2.3"}, "tag_name": "v1.2.3", "branch": "main",
        "backend": "github", "issue_repo": "example/demo", "release_content_paths": [], "title": "v1.2.3",
    }
    args = SimpleNamespace(execute=True, remote="origin", notes_file=None, close_issue=[])

    with pytest.raises(SystemExit, match="requires a validated claims review"):
        RESUME_PUBLISH.resume_publish(
            _ISOLATED_RESUME_REPO, args=args, plan=plan, adapter_data=_ADAPTER, cli=_ClaimsResumeCli(commands),
            state=state, resumable_state=lambda *_a, **_k: state,
            assert_resumable=lambda *_a, **_k: None, common=_ClaimsResumeCommon(),
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
            "marker_at_head": True, "phase": "release-content",
            "head_is_release_commit": True, "tag_local": published,
            "tag_remote": published, "release_exists": published,
            "tag_points_at_head": published, "prepared": None,
            "remote_tag_sha": "tag", "tag_sha": "tag", "head_sha": "head",
            "remote_branch_sha": "", "claims_evidence_commit": "",
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
