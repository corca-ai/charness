"""Final-consumer tests for release-surface revalidation on resume."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from . import test_release_resume_edge_coverage as edge


def test_claims_resume_rechecks_and_binds_the_target_release_surface() -> None:
    clis: list = []

    edge._resume_claims_publication_leg(
        remote_branch_sha="old-branch", tag_remote=True, cli_out=clis,
    )

    assert clis[0].version_surface_checks == [{
        "version": "1.2.3", "stage": "post-claims-review, pre-push",
    }]
    assert clis[0].finalized_payloads[0]["version_drift_check"] == {
        "status": "passed",
        "stage": "post-claims-review, pre-push",
        "checked_version": "1.2.3",
        "surfaces": ["packaging/charness.json", "plugins/charness/.codex-plugin/plugin.json"],
        "drift": [],
    }


def test_claims_resume_refuses_deleted_required_surface_before_publication() -> None:
    commands: list[list[str]] = []
    cli = edge._ClaimsResumeCli(
        commands,
        version_surface_error=(
            "release surface drift: required plugin manifest is missing after claims review"
        ),
    )
    state = {
        "phase": "prepared-claims-review", "tag_local": True, "tag_remote": True,
        "remote_branch_sha": "claims-evidence", "claims_evidence_commit": "claims-evidence",
        "head_sha": "claims-evidence", "prepared": {"commit": "prepared"},
        "release_exists": False, "record_path": edge._RECORD_PATH,
        "claims_review": {
            "path": "charness-artifacts/release-review/edge.json", "verdict": "pass",
            "observer_distinctness": {"kind": "separate-agent-context", "signal": "fixture"},
        },
    }
    plan = {
        "payload": {"commit_message": "Release v1.2.3", "target_version": "1.2.3"},
        "tag_name": "v1.2.3", "branch": "main", "backend": "github",
        "issue_repo": "example/demo", "release_content_paths": [], "title": "v1.2.3",
    }
    args = SimpleNamespace(execute=True, remote="origin", notes_file=None, close_issue=[])

    with pytest.raises(SystemExit, match="required plugin manifest is missing"):
        edge.RESUME_PUBLISH.resume_publish(
            Path("."), args=args, plan=plan, adapter_data=edge._ADAPTER, cli=cli,
            state=state, resumable_state=lambda *_a, **_k: state,
            assert_resumable=lambda *_a, **_k: None, common=edge._ClaimsResumeCommon(),
            resume_closeout=SimpleNamespace(),
            commit_artifact_before_push=lambda *_a, **_k: pytest.fail("artifact commit must not run"),
            release_record_path=edge.CLAIMS.release_record_path,
        )

    assert cli.version_surface_checks == [{
        "version": "1.2.3", "stage": "post-claims-review, pre-push",
    }]
    assert cli.commands == [["gh", "auth", "status"]]
    assert cli.final_artifact_commits == []
