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
    state = {"phase": "post-publication-carrier", "head_message": message, "head_sha": "carrier-sha", "remote_branch_sha": "old-sha"}
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
