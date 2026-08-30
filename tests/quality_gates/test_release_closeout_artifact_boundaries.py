"""Irreversible release closeout artifact boundaries."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from .seeding_support import load_module

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "public" / "release" / "scripts"


def _load(name: str):
    return load_module(f"{name}_closeout_artifact_boundaries", SCRIPTS / f"{name}.py")


ISSUE_CLOSEOUT = _load("release_issue_closeout")
ISSUE_CLOSEOUT_ARTIFACT = _load("release_issue_closeout_artifact")
MESSAGE = _load("release_issue_closeout_message")


def test_carrier_artifact_refuses_missing_preflight_paragraphs() -> None:
    with pytest.raises(SystemExit, match="carrier paragraphs are missing"):
        ISSUE_CLOSEOUT_ARTIFACT.commit_issue_closeout_carrier_artifact(
            Path("."),
            write_artifact=lambda **_kwargs: None,
            payload={},
            fresh_checkout_payload={},
            artifact_relpath="charness-artifacts/release/latest.md",
            expected_release_url=None,
            remote="origin",
            branch="main",
            run=lambda *_args, **_kwargs: None,
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
        Path("."),
        write_artifact=lambda **kwargs: writes.append(kwargs),
        payload=common,
        fresh_checkout_payload={"status": "passed"},
        artifact_relpath="charness-artifacts/release/latest.md",
        expected_release_url="https://example.test/v1.2.3",
        remote="origin",
        branch="main",
        run=run,
    )
    assert commands[0] == [
        "git",
        "add",
        "charness-artifacts/release/latest.md",
        "charness-artifacts/probe/observer.json",
    ]
    assert common["issue_closeout_commit_sha"] == "commit-sha"

    commands.clear()
    carrier = {
        "issue_closeout_draft_validation": {"paragraphs": ["Release v1.2.3", "Close #44."]},
        "issue_closeout_preflight": {"repo": "example/demo", "issues": [{"number": 44}]},
        "release_observer": {"path": "charness-artifacts/probe/observer.json"},
    }
    ISSUE_CLOSEOUT_ARTIFACT.commit_issue_closeout_carrier_artifact(
        Path("."),
        write_artifact=lambda **kwargs: writes.append(kwargs),
        payload=carrier,
        fresh_checkout_payload={},
        artifact_relpath="charness-artifacts/release/latest.md",
        expected_release_url=None,
        remote="origin",
        branch="main",
        run=run,
    )
    assert commands[0] == [
        "git",
        "add",
        "charness-artifacts/release/latest.md",
        "charness-artifacts/probe/observer.json",
    ]
    assert commands[1] == ["git", "commit", "-m", "Release v1.2.3", "-m", "Close #44."]
    assert carrier["issue_closeout"]["status"] == "carrier-pending-state-verification"
    assert carrier["issue_closeout_carrier_commit_sha"] == "commit-sha"
    assert len(writes) == 2


def test_the_carrier_refuses_to_close_issues_when_the_observer_capture_failed() -> None:
    commands: list[list[str]] = []
    payload = {
        "tag_name": "v1.2.3",
        "issue_closeout_draft_validation": {"paragraphs": ["Release v1.2.3", "Close #44."]},
        "issue_closeout_preflight": {"repo": "example/demo", "issues": [{"number": 44}]},
        "release_observer": {"status": "capture_error", "path": None},
    }
    with pytest.raises(SystemExit, match="release observer record was not written"):
        ISSUE_CLOSEOUT_ARTIFACT.commit_issue_closeout_carrier_artifact(
            Path("."),
            write_artifact=lambda **kwargs: None,
            payload=payload,
            fresh_checkout_payload={},
            artifact_relpath="charness-artifacts/release/latest.md",
            expected_release_url=None,
            remote="origin",
            branch="main",
            run=lambda command, *, cwd: commands.append(command),
        )
    assert commands == []


def test_release_content_close_refs_refuses_when_issue_verifier_is_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(MESSAGE, "_ISSUE_VERIFY_CLOSEOUT", None)
    monkeypatch.setattr(MESSAGE, "_ISSUE_CLOSEOUT_DRAFT_ERROR", "issue skill missing (forced)")
    with pytest.raises(SystemExit, match="requires the issue skill's closeout helper"):
        MESSAGE.release_content_close_keyword_refs("Release\n\nClose #44.")
