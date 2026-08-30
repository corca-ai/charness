"""Direct contracts for post-publication release closeout recovery.

The resilience suite retains one real resume/closeout path. This module owns the
state matrix so each recovery arm does not rebuild a repository and fake provider.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from .release_resume_edge_support import ResumeCli
from .release_script_loading import load_release_script

RESUME_CLOSEOUT = load_release_script("publish_release_resume_closeout")
RECORD_PATH = "charness-artifacts/release/latest.md"


def test_resume_closeout_requires_original_irreversible_inputs() -> None:
    args = SimpleNamespace(
        close_issue=[],
        close_issue_classification=None,
        close_issue_carrier_file=None,
        close_issue_behavior=[],
        close_issue_probe_record=[],
    )

    with pytest.raises(
        SystemExit, match="Recovery never infers or omits issue-close context"
    ) as error:
        RESUME_CLOSEOUT._require_closeout_resume_inputs(args)

    for flag in (
        "--close-issue",
        "--close-issue-classification",
        "--close-issue-carrier-file",
        "--close-issue-behavior",
    ):
        assert flag in str(error.value)


def test_resume_commit_file_refuses_missing_evidence() -> None:
    cli = ResumeCli(changed=[], files={})

    with pytest.raises(SystemExit, match="does not contain required evidence"):
        RESUME_CLOSEOUT._commit_file(Path("."), commit_ref="HEAD", path="missing.json", cli=cli)


def test_resume_carrier_tree_refuses_missing_wrong_or_unbound_evidence() -> None:
    observer = "charness-artifacts/probe/demo-v1.2.3-release-observer.json"
    missing = ResumeCli(changed=[], files={})
    with pytest.raises(SystemExit, match="carrier evidence tree must change"):
        RESUME_CLOSEOUT._validate_carrier_evidence_tree(
            Path("."),
            commit_ref="HEAD",
            artifact_relpath=RECORD_PATH,
            tag_name="v1.2.3",
            payload={},
            cli=missing,
        )
    assert not any(command[:2] == ["git", "push"] for command in missing.commands)

    cli = ResumeCli(
        changed=[RECORD_PATH, observer],
        files={
            RECORD_PATH: "carrier-pending-state-verification",
            observer: json.dumps({"target": {"tag": "v9.9.9"}}),
        },
    )
    with pytest.raises(SystemExit, match="targets a different release tag"):
        RESUME_CLOSEOUT._validate_carrier_evidence_tree(
            Path("."),
            commit_ref="HEAD",
            artifact_relpath=RECORD_PATH,
            tag_name="v1.2.3",
            payload={"tag_name": "v9.9.9"},
            cli=cli,
        )

    cli.files[observer] = json.dumps({"target": {"tag": "v1.2.3"}})
    with pytest.raises(SystemExit, match="does not bind its observer"):
        RESUME_CLOSEOUT._validate_carrier_evidence_tree(
            Path("."),
            commit_ref="HEAD",
            artifact_relpath=RECORD_PATH,
            tag_name="v1.2.3",
            payload={},
            cli=cli,
        )


def test_resume_carrier_refuses_validation_that_does_not_match_preflight() -> None:
    cli = ResumeCli(changed=[], files={})
    payload = {"issue_closeout_draft_validation": {"commit_message": "expected"}}
    with pytest.raises(SystemExit, match="does not exactly match"):
        RESUME_CLOSEOUT._validated_carrier_message(
            Path("."),
            args=SimpleNamespace(close_issue=[44], close_issue_classification="bug"),
            issue_repo="example/demo",
            payload=payload,
            commit_message="different",
            commit_ref="HEAD",
            artifact_relpath=RECORD_PATH,
            tag_name="v1.2.3",
            cli=cli,
        )
    assert payload["resume_carrier_validation"]["matches_preflight_draft"] is False


def test_resume_final_evidence_validator_is_an_in_process_state_transition() -> None:
    cli = ResumeCli(
        changed=[RECORD_PATH],
        files={RECORD_PATH: "Issue closeout verification: `state-verified`"},
    )
    payload: dict = {}
    RESUME_CLOSEOUT._validate_final_evidence_tree(
        Path("."), commit_ref="HEAD", artifact_relpath=RECORD_PATH, payload=payload, cli=cli
    )
    assert payload["resume_final_evidence"] == {
        "status": "validated",
        "artifact_path": RECORD_PATH,
    }

    cli.files[RECORD_PATH] = "carrier-pending-state-verification"
    with pytest.raises(SystemExit, match="lacks its state-verified release artifact"):
        RESUME_CLOSEOUT._validate_final_evidence_tree(
            Path("."), commit_ref="HEAD", artifact_relpath=RECORD_PATH, payload={}, cli=cli
        )


def test_resume_reconciles_ambiguous_push_after_remote_receipt() -> None:
    cli = ResumeCli(changed=[], files={}, push_error=True, remote_sha="carrier-sha")
    payload: dict = {}
    RESUME_CLOSEOUT._reconcile_push(
        Path("."),
        state={"remote_branch_sha": "old-sha", "head_sha": "carrier-sha"},
        remote="origin",
        branch="main",
        payload=payload,
        cli=cli,
    )
    assert payload["resume_remote_reconcile"] == {
        "status": "push-error-but-shared",
        "sha": "carrier-sha",
    }
    assert ["git", "ls-remote", "--heads", "origin", "refs/heads/main"] in cli.commands


def test_resume_refuses_ambiguous_push_when_remote_identity_differs() -> None:
    cli = ResumeCli(changed=[], files={}, push_error=True, remote_sha="other-sha")

    with pytest.raises(RuntimeError, match="connection lost"):
        RESUME_CLOSEOUT._reconcile_push(
            Path("."),
            state={"remote_branch_sha": "old-sha", "head_sha": "carrier-sha"},
            remote="origin",
            branch="main",
            payload={},
            cli=cli,
        )


def _post_publication_case(*, execute: bool, remote_sha: str):
    observer = "charness-artifacts/probe/demo-v1.2.3-release-observer.json"
    message = "carrier message"
    cli = ResumeCli(
        changed=[RECORD_PATH, observer],
        files={
            RECORD_PATH: f"{observer}\ncarrier-pending-state-verification",
            observer: json.dumps({"target": {"tag": "v1.2.3"}}),
        },
    )
    cli.expected_github_release_url = lambda *_args: "https://example.test/v1.2.3"
    cli.run_fresh_checkout_probes = lambda *_args: {"status": "passed"}
    cli.verify_release_visible = lambda *_args, **_kwargs: SimpleNamespace(returncode=0)
    cli.backend_command = lambda *_args: ["gh"]
    finalized: list[dict] = []
    cli.finalize_release_payload = lambda _root, payload, **_kwargs: finalized.append(dict(payload))
    tail_calls: list[dict] = []
    common = SimpleNamespace(
        preflight_close_issue_carrier=lambda *_args, **_kwargs: None,
        run_release_closeout_tail=lambda *_args, **kwargs: tail_calls.append(kwargs),
    )
    args = SimpleNamespace(
        execute=execute,
        close_issue=[44],
        close_issue_classification="bug",
        close_issue_carrier_file=Path("carrier.md"),
        close_issue_behavior=["Behavior #44: fixture"],
        close_issue_probe_record=["Probe record #44: local-only-by-contract"],
        remote="origin",
    )
    payload = {"issue_closeout_draft_validation": {"commit_message": message}}
    plan = {
        "payload": payload,
        "issue_repo": "example/demo",
        "tag_name": "v1.2.3",
        "branch": "main",
        "backend": {"id": "gh"},
    }
    state = {
        "phase": "post-publication-carrier",
        "head_message": message,
        "head_sha": "carrier-sha",
        "remote_branch_sha": remote_sha,
        "record_path": RECORD_PATH,
    }
    return cli, common, args, payload, plan, state, finalized, tail_calls


def test_resume_dry_run_validates_carrier_without_reconciling(capsys) -> None:
    cli, common, args, _payload, plan, state, _finalized, _tail_calls = _post_publication_case(
        execute=False, remote_sha="old-sha"
    )

    RESUME_CLOSEOUT.resume_post_publication_closeout(
        Path("."),
        args=args,
        plan=plan,
        adapter_data={"output_dir": "charness-artifacts/release"},
        state=state,
        common=common,
        cli=cli,
    )

    assert yaml.safe_load(capsys.readouterr().out)["resume"] == (
        "dry-run: would reconcile post-publication-carrier against the remote branch"
    )
    assert not any(command[:2] == ["git", "push"] for command in cli.commands)


def test_invalid_carrier_refuses_before_top_level_resume_pushes() -> None:
    cli, common, args, _payload, plan, state, _finalized, _tail_calls = _post_publication_case(
        execute=True, remote_sha="old-sha"
    )
    cli.changed = []

    with pytest.raises(SystemExit, match="carrier evidence tree must change"):
        RESUME_CLOSEOUT.resume_post_publication_closeout(
            Path("."),
            args=args,
            plan=plan,
            adapter_data={"output_dir": "charness-artifacts/release"},
            state=state,
            common=common,
            cli=cli,
        )

    assert not any(command[:2] == ["git", "push"] for command in cli.commands)


def test_post_publication_carrier_resume_reconciles_and_runs_the_live_tail() -> None:
    cli, common, args, payload, plan, state, finalized, tail_calls = _post_publication_case(
        execute=True, remote_sha="carrier-sha"
    )

    RESUME_CLOSEOUT.resume_post_publication_closeout(
        Path("."),
        args=args,
        plan=plan,
        adapter_data={"output_dir": "charness-artifacts/release"},
        state=state,
        common=common,
        cli=cli,
    )

    assert payload["resume_remote_reconcile"] == {
        "status": "already-shared",
        "sha": "carrier-sha",
    }
    assert finalized
    assert len(tail_calls) == 1
    assert tail_calls[0]["carrier_already_committed"] is True
    assert tail_calls[0]["carrier_source"] == "release-resume-closeout"
    assert not any(command[:2] == ["git", "push"] for command in cli.commands)
