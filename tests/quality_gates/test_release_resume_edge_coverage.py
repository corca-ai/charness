"""Focused edge coverage for release closeout recovery helpers."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "public" / "release" / "scripts"


def _load(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"{name}_edge_coverage", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RESUME_CLOSEOUT = _load("publish_release_resume_closeout")
ISSUE_CLOSEOUT = _load("release_issue_closeout")
ISSUE_CLOSEOUT_ARTIFACT = _load("release_issue_closeout_artifact")
MESSAGE = _load("release_issue_closeout_message")
RESUME_PUBLISH = _load("publish_release_resume_publish")
RESUME = _load("publish_release_resume")
CLAIMS = _load("publish_release_claims_review")


class _ClaimsResumeCli:
    def __init__(self, commands: list[list[str]], *, notes_preflights: list[dict] | None = None,
                 allow_create: bool = False):
        self.commands = commands
        self.notes_preflights = notes_preflights if notes_preflights is not None else []
        self.allow_create = allow_create

    def run(self, command, *, cwd, check=True):
        self.commands.append(command)
        return SimpleNamespace(returncode=0, stdout="https://example.test/v1.2.3")

    def run_notes_file_preflight(self, repo_root, *, target_tag, notes_file, on_resume=False):
        # Recorded, never executed against the real filesystem: the stub passes
        # `repo_root=Path(".")`, so a real preflight here would read the AUTHORING repo's
        # adapter and its drafted-notes directory against a fixture tag.
        self.notes_preflights.append(
            {"target_tag": target_tag, "notes_file": notes_file, "on_resume": on_resume}
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

    @staticmethod
    def safe_real_host_payload(_root, _paths, *, build_payload):
        return build_payload()

    @staticmethod
    def build_real_host_payload():
        return {"required": False}

    @staticmethod
    def build_retro_trigger_evaluation(*_args, **_kwargs):
        return {"required": False}

    @staticmethod
    def verify_release_visible(*_args, **_kwargs):
        return SimpleNamespace(returncode=0)

    @staticmethod
    def finalize_release_payload(*_args, **_kwargs):
        return None

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
        "payload": {"commit_message": "Release v1.2.3"}, "tag_name": "v1.2.3", "branch": "main",
        "backend": "github", "issue_repo": "example/demo", "release_content_paths": [], "title": "v1.2.3",
    }
    args = SimpleNamespace(execute=True, remote="origin", notes_file=notes_file, close_issue=[])
    RESUME_PUBLISH.resume_publish(
        Path("."), args=args, plan=plan, adapter_data=_ADAPTER,
        cli=_ClaimsResumeCli(commands, notes_preflights=notes_preflights, allow_create=not release_exists),
        state=state,
        resumable_state=lambda *_args, **_kwargs: state, assert_resumable=lambda *_args, **_kwargs: None,
        common=_ClaimsResumeCommon(), resume_closeout=SimpleNamespace(),
        commit_artifact_before_push=lambda *_args, **_kwargs: committed.append("artifact"),
        release_record_path=CLAIMS.release_record_path,
    )
    return commands, committed


def test_resume_closeout_requires_original_irreversible_inputs() -> None:
    args = SimpleNamespace(
        close_issue=[], close_issue_classification=None, close_issue_carrier_file=None,
        close_issue_behavior=[],
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
            Path("."), args=args, plan=plan, adapter_data=_ADAPTER, cli=_ClaimsResumeCli(commands),
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
        close_issue_behavior=["Behavior #44: fixture"], remote="origin",
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
    assert '"resume": "dry-run: would reconcile post-publication-carrier against the remote branch"' in capsys.readouterr().out
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
    }
    ISSUE_CLOSEOUT_ARTIFACT.commit_issue_closeout_carrier_artifact(
        Path("."), write_artifact=lambda **kwargs: writes.append(kwargs), payload=carrier,
        fresh_checkout_payload={}, artifact_relpath="charness-artifacts/release/latest.md",
        expected_release_url=None, remote="origin", branch="main", run=run,
    )
    assert commands[0] == ["git", "add", "charness-artifacts/release/latest.md"]
    assert commands[1] == ["git", "commit", "-m", "Release v1.2.3", "-m", "Close #44."]
    assert carrier["issue_closeout"]["status"] == "carrier-pending-state-verification"
    assert carrier["issue_closeout_carrier_commit_sha"] == "commit-sha"
    assert len(writes) == 2


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
            Path("."), args=args, plan=plan, adapter_data=_ADAPTER, cli=_ClaimsResumeCli(commands),
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
