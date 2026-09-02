"""Post-create verification and issue-close tests for release publication.

This module owns the release boundary after external creation: verifying the
public record, recording distinct-channel outcomes, and closing issues only
through the required evidence path. Those cases are one lifecycle concept
separate from preparation, review policy, and preflight checks.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

from .issue_closeout_support import bug_closeout_body
from .test_release_publish import (
    _release_env,
    _run_publish_patch,
    _seed_publish_release_repo,
)

pytestmark = pytest.mark.boundary_contract(
    reason="exercise the exported release publish entrypoint with its real git and GitHub-backed topology"
)


@pytest.mark.release_only
def test_release_artifact_does_not_claim_post_publish_proof_before_verification(
    tmp_path: Path,
) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)

    env = _release_env(tmp_path, bin_dir)
    result = _run_publish_patch(repo, env)

    assert result.returncode == 0, result.stderr
    tag_artifact = subprocess.run(
        ["git", "show", "v0.0.1:charness-artifacts/release/latest.md"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert "## Post-Publish Proof" not in tag_artifact
    assert "Review proof: not recorded in this helper invocation." in tag_artifact


@pytest.mark.release_only
def test_publish_release_fails_after_post_create_verification_failure(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)

    env = _release_env(tmp_path, bin_dir)
    env["FAKE_GH_RELEASE_CREATE_WITHOUT_VIEW"] = "1"
    result = _run_publish_patch(repo, env)

    assert result.returncode == 1
    assert "release post-create verification failed after external mutation" in result.stderr
    assert "command: gh release view v0.0.1" in result.stderr
    assert "post_publish_artifact_commit_sha:" in result.stderr
    assert "not_committed" not in result.stderr
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    release_create_index = next(
        index for index, entry in enumerate(gh_log) if entry[:2] == ["release", "create"]
    )
    post_create_views = [
        entry
        for entry in gh_log[release_create_index + 1 :]
        if entry == ["release", "view", "v0.0.1"]
    ]
    assert len(post_create_views) >= 3
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    assert ["push", "origin", "main", "v0.0.1"] in git_log
    assert ["push", "origin", "main"] in git_log
    artifact_text = (repo / "charness-artifacts" / "release" / "latest.md").read_text(
        encoding="utf-8"
    )
    assert "public release surface verification: failed" in artifact_text
    assert "create returned `https://github.com/example/demo/releases/tag/v0.0.1`" in artifact_text
    assert "post-create verification failed" in artifact_text
    assert "## Post-Publish Proof" not in artifact_text


@pytest.mark.release_only
def test_publish_release_does_not_close_issues_when_post_create_verification_fails(
    tmp_path: Path,
) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)

    env = _release_env(tmp_path, bin_dir)
    env["FAKE_GH_ISSUE_STATE"] = str(tmp_path / "issue-state.json")
    env["FAKE_GH_RELEASE_CREATE_WITHOUT_VIEW"] = "1"
    Path(env["FAKE_GH_ISSUE_STATE"]).write_text(json.dumps({"44": "OPEN"}) + "\n", encoding="utf-8")
    result = _run_publish_patch(
        repo,
        env,
        "--close-issue",
        "44",
        "--close-issue-behavior",
        "Behavior #44: confirmed via fresh checkout install",
        "--close-issue-probe-record",
        "Probe record #44: local-only-by-contract",
    )

    assert result.returncode == 1
    state = json.loads(Path(env["FAKE_GH_ISSUE_STATE"]).read_text(encoding="utf-8"))
    assert state["44"] == "OPEN"
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    release_create_index = next(
        index for index, entry in enumerate(gh_log) if entry[:2] == ["release", "create"]
    )
    post_create_views = [
        entry
        for entry in gh_log[release_create_index + 1 :]
        if entry == ["release", "view", "v0.0.1"]
    ]
    assert len(post_create_views) >= 3
    assert not any(entry[:2] == ["issue", "close"] for entry in gh_log)
    artifact_text = (repo / "charness-artifacts" / "release" / "latest.md").read_text(
        encoding="utf-8"
    )
    assert "Issue closeout verification: pending or not requested." in artifact_text


@pytest.mark.release_only
def test_publish_release_records_distinct_channel_confirmation_before_issue_close(
    tmp_path: Path,
) -> None:
    # WS-1 rung-2: a channel distinct from `gh release view` confirms the published
    # release, and the verdict is RECORDED before the irreversible issue close.
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _release_env(tmp_path, bin_dir)
    env["FAKE_GH_ISSUE_STATE"] = str(tmp_path / "issue-state.json")
    Path(env["FAKE_GH_ISSUE_STATE"]).write_text(json.dumps({"44": "OPEN"}) + "\n", encoding="utf-8")
    result = _run_publish_patch(
        repo,
        env,
        "--close-issue",
        "44",
        "--close-issue-behavior",
        "Behavior #44: confirmed via fresh checkout install",
        "--close-issue-probe-record",
        "Probe record #44: local-only-by-contract",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["distinct_channel_verification"]["status"] == "confirmed"
    assert payload["distinct_channel_verification"]["channel"] == "adapter-probe"
    # the distinct channel actually ran (a channel separate from `gh release view`)
    distinct_log = json.loads((tmp_path / "distinct-channel-log.json").read_text(encoding="utf-8"))
    assert distinct_log == [["v0.0.1"]]
    state = json.loads(Path(env["FAKE_GH_ISSUE_STATE"]).read_text(encoding="utf-8"))
    assert state["44"] == "CLOSED"
    artifact_text = (repo / "charness-artifacts" / "release" / "latest.md").read_text(
        encoding="utf-8"
    )
    assert "adapter-probe" in artifact_text
    assert "confirmed" in artifact_text


@pytest.mark.release_only
def test_publish_release_records_distinct_channel_disposition_and_still_closes(
    tmp_path: Path,
) -> None:
    # F2a: a typed non-`verified` disposition (the distinct channel could not
    # confirm) passes the rung-1 presence floor EQUALLY — the close advances on
    # record-presence, never on an automated `confirmed ⇒ proceed` gate; the
    # honesty of the `not-confirmed` is the human rung-2 audit.
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _release_env(tmp_path, bin_dir)
    env["FAKE_DISTINCT_CHANNEL_RESULT"] = "fail"
    env["FAKE_GH_ISSUE_STATE"] = str(tmp_path / "issue-state.json")
    Path(env["FAKE_GH_ISSUE_STATE"]).write_text(json.dumps({"44": "OPEN"}) + "\n", encoding="utf-8")
    result = _run_publish_patch(
        repo,
        env,
        "--close-issue",
        "44",
        "--close-issue-behavior",
        "Behavior #44: confirmed via fresh checkout install",
        "--close-issue-probe-record",
        "Probe record #44: local-only-by-contract",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["distinct_channel_verification"]["status"] == "not-confirmed"
    assert payload["public_release_verification"] == "unproven"
    state = json.loads(Path(env["FAKE_GH_ISSUE_STATE"]).read_text(encoding="utf-8"))
    assert state["44"] == "CLOSED"
    artifact_text = (repo / "charness-artifacts" / "release" / "latest.md").read_text(
        encoding="utf-8"
    )
    assert "Rung-2 distinct-channel verdict: `not-confirmed`" in artifact_text


@pytest.mark.release_only
def test_publish_release_verifies_and_falls_back_to_manual_issue_close(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)

    env = _release_env(tmp_path, bin_dir)
    env["FAKE_GH_ISSUE_STATE"] = str(tmp_path / "issue-state.json")
    Path(env["FAKE_GH_ISSUE_STATE"]).write_text(json.dumps({"44": "OPEN"}) + "\n", encoding="utf-8")
    result = _run_publish_patch(
        repo,
        env,
        "--close-issue",
        "44",
        "--close-issue-behavior",
        "Behavior #44: confirmed via fresh checkout install",
        "--close-issue-probe-record",
        "Probe record #44: local-only-by-contract",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["issue_closeout_preflight"]["status"] == "verified"
    assert payload["issue_closeout_preflight"]["issues"][0]["state"] == "OPEN"
    assert payload["issue_closeout_behavioral_verdict"]["ok"] is True
    assert payload["issue_closeout"]["status"] == "state-verified"
    assert payload["issue_closeout"]["issues"][0]["state"] == "CLOSED"
    assert payload["issue_closeout"]["issues"][0]["preflight_state"] == "OPEN"
    assert payload["issue_closeout"]["issues"][0]["carrier"] == "direct_post_publish_commit_body"
    assert payload["issue_closeout"]["issues"][0]["manual_fallback_used"] is True
    assert payload["issue_closeout_commit_sha"]
    artifact_text = (repo / "charness-artifacts" / "release" / "latest.md").read_text(
        encoding="utf-8"
    )
    assert "## Issue Closeout" in artifact_text
    assert "Issue closeout verification: `state-verified`." in artifact_text
    assert "Issue #44: `CLOSED`" in artifact_text
    assert "carrier: `direct_post_publish_commit_body`" in artifact_text
    assert "manual fallback used: `True`" in artifact_text
    commit_body = subprocess.run(
        ["git", "log", "--format=%B", "-2"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert "Close #44." in commit_body
    assert "Behavior #44: confirmed via fresh checkout install" in commit_body
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    assert ["issue", "view", "44", "--repo", "example/demo", "--json", "number,state,url"] in gh_log
    assert any(entry[:5] == ["issue", "close", "44", "--repo", "example/demo"] for entry in gh_log)
    release_create_index = next(
        index for index, entry in enumerate(gh_log) if entry[:2] == ["release", "create"]
    )
    issue_view_indexes = [
        index
        for index, entry in enumerate(gh_log)
        if entry == ["issue", "view", "44", "--repo", "example/demo", "--json", "number,state,url"]
    ]
    assert issue_view_indexes[0] < release_create_index
    assert issue_view_indexes[-1] > release_create_index


@pytest.mark.release_only
def test_publish_release_accepts_full_bug_closeout_carrier(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)

    env = _release_env(tmp_path, bin_dir)
    env["FAKE_GH_ISSUE_STATE"] = str(tmp_path / "issue-state.json")
    Path(env["FAKE_GH_ISSUE_STATE"]).write_text(json.dumps({"44": "OPEN"}) + "\n", encoding="utf-8")
    carrier = tmp_path / "closeout.md"
    carrier.write_text(
        bug_closeout_body(
            close_line="Close #44.",
            behavior_line=None,
        )
        + "\n",
        encoding="utf-8",
    )

    result = _run_publish_patch(
        repo,
        env,
        "--close-issue",
        "44",
        "--close-issue-classification",
        "bug",
        "--close-issue-carrier-file",
        str(carrier),
        "--close-issue-behavior",
        "Behavior #44: confirmed via fresh checkout install",
        "--close-issue-probe-record",
        "Probe record #44: local-only-by-contract",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    draft_validation = payload["issue_closeout_draft_validation"]
    assert draft_validation["ok"] is True
    assert draft_validation["missing_fields"] == []
    assert draft_validation["missing_close_keywords"] == []
    commit_body = subprocess.run(
        ["git", "log", "--format=%B", "-2"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert "Classification: bug" in commit_body
    assert "Root cause: the issue closeout carrier was prose-only." in commit_body
    assert "Debug artifact: charness-artifacts/debug/latest.md." in commit_body
    assert "Behavior #44: confirmed via fresh checkout install" in commit_body
