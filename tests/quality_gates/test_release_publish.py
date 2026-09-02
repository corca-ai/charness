from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

from . import release_publish_fixtures as fixture_support
from .issue_closeout_support import bug_closeout_body
from .release_publish_fixtures import (
    REPO_ROOT,
    _build_release_publish_seed,
    _copy_release_publish_seed,
    _release_env,
    _run_publish,
    _run_publish_patch,
    _run_review_gate,
    _seed_publish_release_repo,
    _write_exec,
    commit_claims_review,
    ensure_fixture_release_base,
    release_publish_seed,
)
from .release_script_loading import load_release_script
from .seeding_support import git, write_release_adapter

CLAIMS_REVIEW = load_release_script("publish_release_claims_review", suffix="direct_parent")
pytestmark = pytest.mark.boundary_contract(
    reason="exercise the exported release publish entrypoint with its real git and GitHub-backed topology"
)


def _tree_snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


@pytest.mark.release_only
def test_release_fixture_seed_is_cached_isolated_and_bootstrap_is_not_repeated(
    tmp_path: Path, monkeypatch
) -> None:
    from tests import seed_cache

    monkeypatch.setenv("CHARNESS_TEST_SEED_CACHE_ROOT", str(tmp_path / "cache"))
    monkeypatch.setattr(seed_cache, "_SOURCE_HASH", "release-fixture-cache-proof")
    git_commands: list[tuple[str, ...]] = []
    real_run = fixture_support.subprocess.run

    def recording_run(args, *run_args, **run_kwargs):
        if args and args[0] == "git":
            git_commands.append(tuple(args))
        return real_run(args, *run_args, **run_kwargs)

    monkeypatch.setattr(fixture_support.subprocess, "run", recording_run)

    uncached_root = tmp_path / "uncached"
    uncached_root.mkdir()
    uncached_seed = uncached_root / "seed"
    uncached_seed.mkdir()
    _build_release_publish_seed(uncached_seed)
    uncached_test_root = tmp_path / "uncached-test"
    uncached_test_root.mkdir()
    _copy_release_publish_seed(uncached_test_root, uncached_seed)
    uncached_second_root = tmp_path / "uncached-second"
    uncached_second_root.mkdir()
    uncached_second_seed = uncached_second_root / "seed"
    uncached_second_seed.mkdir()
    _build_release_publish_seed(uncached_second_seed)
    uncached_second_test_root = tmp_path / "uncached-second-test"
    uncached_second_test_root.mkdir()
    _copy_release_publish_seed(uncached_second_test_root, uncached_second_seed)
    uncached_count = len(git_commands)

    seed = release_publish_seed()
    before_seed = _tree_snapshot(seed)
    cached_root = tmp_path / "cached"
    cached_root.mkdir()
    _copy_release_publish_seed(cached_root, seed)
    cached_second_root = tmp_path / "cached-second"
    cached_second_root.mkdir()
    _copy_release_publish_seed(cached_second_root, seed)
    cached_count = len(git_commands) - uncached_count

    # 12 and 8 until the seed catalog landed. `_setup_git` used to shell out to git
    # per build; it now delegates to `repo_shapes.replace_with_committed_repo`, which
    # COPIES a cached one-commit checkout and runs no git of its own. So these counts
    # fell as a result of the improvement this test exists to protect -- and the
    # release-only lane has been red ever since, invisibly, because the standing lane
    # excludes `release_only` and a skipped gate is not a passed gate.
    assert uncached_count == 6
    assert cached_count == 5

    # The counts above are a proxy: they only see git run from THIS module, which is
    # precisely why they went stale when the work moved to another one. This is the
    # property the test is named for, and it survives the work moving again.
    before_reask = len(git_commands)
    assert release_publish_seed() == seed
    assert len(git_commands) == before_reask, "re-asking for the seed rebuilt it"
    assert git_commands[-2][1:] == (
        "remote",
        "add",
        "origin",
        str(cached_second_root / "remote.git"),
    )
    assert git_commands[-1][1:] == ("push", "-u", "origin", "main")

    first_clone = cached_root / "repo"
    ensure_fixture_release_base(first_clone)
    assert _tree_snapshot(seed) == before_seed


@pytest.mark.release_only
def test_execute_prepares_claims_review_record_without_publication(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    git_log_path = tmp_path / "git-log.json"
    gh_log_path = tmp_path / "gh-log.json"
    prior_git_log = (
        json.loads(git_log_path.read_text(encoding="utf-8")) if git_log_path.exists() else []
    )
    prior_gh_log = (
        json.loads(gh_log_path.read_text(encoding="utf-8")) if gh_log_path.exists() else []
    )
    result = _run_publish(
        repo,
        _release_env(tmp_path, bin_dir),
        "--part",
        "patch",
        "--execute",
        "--critique-blocked",
        "synthetic-test-harness does not spawn real critique subagents",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["release_stage"] == "prepared-awaiting-claims-review"
    assert payload["prepared_release_commit"]
    artifact = (repo / "charness-artifacts" / "release" / "latest.md").read_text(encoding="utf-8")
    assert "<!-- charness-release-state:prepared-awaiting-claims-review -->" in artifact
    assert "branch/tag push: pending independent claims review" in artifact
    git_log = json.loads(git_log_path.read_text(encoding="utf-8"))[len(prior_git_log) :]
    gh_log = json.loads(gh_log_path.read_text(encoding="utf-8"))[len(prior_gh_log) :]
    assert ["push", "origin", "main", "v0.0.1"] not in git_log
    assert ["tag", "v0.0.1"] not in git_log
    assert not any(entry[:2] == ["release", "create"] for entry in gh_log)


@pytest.mark.release_only
def test_resume_refuses_missing_claims_review_before_auth_or_publish(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _release_env(tmp_path, bin_dir)
    prepared = _run_publish(
        repo,
        env,
        "--part",
        "patch",
        "--execute",
        "--critique-blocked",
        "synthetic-test-harness does not spawn real critique subagents",
    )
    assert prepared.returncode == 0, prepared.stderr
    gh_log_path = tmp_path / "gh-log.json"
    git_log_path = tmp_path / "git-log.json"
    prior_gh = json.loads(gh_log_path.read_text(encoding="utf-8"))
    prior_git = json.loads(git_log_path.read_text(encoding="utf-8"))

    refused = _run_publish(
        repo,
        env,
        "--resume",
        "--publish-current",
        "--execute",
        "--critique-blocked",
        "synthetic-test-harness does not spawn real critique subagents",
    )

    assert refused.returncode != 0
    assert "requires --claims-review-artifact" in refused.stderr
    assert ["auth", "status"] not in json.loads(gh_log_path.read_text(encoding="utf-8"))[
        len(prior_gh) :
    ]
    git_log = json.loads(git_log_path.read_text(encoding="utf-8"))[len(prior_git) :]
    assert ["push", "origin", "main", "v0.0.1"] not in git_log
    assert ["tag", "v0.0.1"] not in git_log


@pytest.mark.release_only
def test_exported_plugin_executes_claims_review_topology(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _release_env(tmp_path, bin_dir)
    plugin_publish = (
        REPO_ROOT / "plugins" / "charness" / "skills" / "release" / "scripts" / "publish_release.py"
    )
    prepared = subprocess.run(
        [
            "python3",
            str(plugin_publish),
            "--repo-root",
            str(repo),
            "--part",
            "patch",
            "--execute",
            "--critique-blocked",
            "synthetic-test-harness does not spawn real critique subagents",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert prepared.returncode == 0, prepared.stderr
    payload = yaml.safe_load(prepared.stdout)
    prepared_commit = payload["prepared_release_commit"]
    record = subprocess.run(
        ["git", "show", f"{prepared_commit}:charness-artifacts/release/latest.md"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    review_path = commit_claims_review(
        repo,
        prepared_commit=prepared_commit,
        prepared_record=record,
        target_version=payload["target_version"],
        tag_name=payload["tag_name"],
        stem="plugin-claims",
    )
    evidence_commit = git(repo, "rev-parse", "HEAD")
    # Simulate response loss after P's tag reaches the remote but before R's
    # branch push. Resume must push the evidence branch without retagging P.
    git(repo, "tag", "v0.0.1", prepared_commit)
    git(repo, "push", "origin", "v0.0.1")

    resumed = subprocess.run(
        [
            "python3",
            str(plugin_publish),
            "--repo-root",
            str(repo),
            "--resume",
            "--publish-current",
            "--execute",
            "--claims-review-artifact",
            review_path,
            "--critique-blocked",
            "synthetic-test-harness does not spawn real critique subagents",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert resumed.returncode == 0, resumed.stderr
    tag_commit = git(repo, "rev-list", "-n", "1", "v0.0.1")
    remote_head = git(repo, "ls-remote", "origin", "refs/heads/main").split()[0]
    assert tag_commit == prepared_commit
    assert (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", evidence_commit, remote_head],
            cwd=repo,
            check=False,
            capture_output=True,
            text=True,
        ).returncode
        == 0
    )


@pytest.mark.release_only
def test_publish_release_bumps_pushes_tags_and_creates_release(tmp_path: Path) -> None:
    repo, remote, bin_dir = _seed_publish_release_repo(tmp_path)
    critique_artifact = repo / "charness-artifacts" / "critique" / "demo.md"
    critique_artifact.parent.mkdir(parents=True)
    # Names its release. The publish gate now requires the standalone critique to
    # BIND to the version being published, so a critique that could belong to any
    # release no longer satisfies it -- which is the point, and means this fixture
    # has to look like a real release critique rather than a placeholder.
    critique_artifact.write_text("# Demo critique\n\nRelease: 0.0.1\n", encoding="utf-8")
    git(repo, "add", str(critique_artifact))
    git(repo, "commit", "-m", "Add critique proof")

    env = _release_env(tmp_path, bin_dir)
    result = _run_publish_patch(
        repo, env, "--critique-artifact", "charness-artifacts/critique/demo.md"
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    manifest = json.loads((repo / "packaging" / "demo.json").read_text(encoding="utf-8"))
    assert payload["previous_version"] == "0.0.0"
    assert payload["target_version"] == "0.0.1"
    assert manifest["version"] == "0.0.1"
    assert (repo / ".quality-ran").read_text(encoding="utf-8").strip() == "quality ok"
    assert (repo / "charness-artifacts" / "release" / "latest.md").is_file()
    assert git(repo, "tag", "--list", "v0.0.1") == "v0.0.1"
    remote_tags = subprocess.run(
        ["git", "ls-remote", "--tags", "origin", "refs/tags/v0.0.1"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert "refs/tags/v0.0.1" in remote_tags
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    assert ["auth", "status"] in gh_log
    assert ["release", "view", "v0.0.1"] in gh_log
    assert any(
        entry[:6] == ["release", "create", "v0.0.1", "--verify-tag", "--title", "v0.0.1"]
        for entry in gh_log
    )
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    assert ["push", "origin", "main", "v0.0.1"] in git_log
    assert ["push", "origin", "main"] in git_log
    assert ["push", "origin", "v0.0.1"] not in git_log
    assert payload["release_url"] == "https://github.com/example/demo/releases/tag/v0.0.1"
    assert payload["public_release_verification"] == "verified"
    assert "post_publish_artifact_commit_sha" in payload
    artifact_text = (repo / "charness-artifacts" / "release" / "latest.md").read_text(
        encoding="utf-8"
    )
    assert "## Release State" in artifact_text
    assert (
        "GitHub release record: verified URL `https://github.com/example/demo/releases/tag/v0.0.1`"
        in artifact_text
    )
    assert "public release surface verification: verified" in artifact_text
    assert "## Public Release Verification" in artifact_text
    assert "GitHub release publication: verified by the release backend." in artifact_text
    assert "initial release push carried the release branch update and tag" in artifact_text
    assert "post-publish artifact push recorded the verified public release state" in artifact_text
    assert "## Review Proof" in artifact_text
    assert "Review proof: `charness-artifacts/critique/demo.md`." in artifact_text
    assert "## Requested Review Gate" in artifact_text
    assert "Requested-review gate status: `ok`." in artifact_text
    assert "Configuration status: `not_configured`." in artifact_text
    assert "## Post-Publish Proof" in artifact_text
    assert "Public release check: `gh release view v0.0.1`" in artifact_text
    assert "## Release Runtime" in artifact_text
    assert "`quality_command`:" in artifact_text
    assert "`push_create_verify_release`:" in artifact_text
    assert "Run `demo update`." in artifact_text
    assert "Restart the host if the previous version is still visible." in artifact_text
    assert "(tag `v0.0.1`)" in artifact_text
    assert "audit narrative: durable record written to" in artifact_text


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


def test_requested_review_gate_blocks_unavailable_release_record(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "release").mkdir(parents=True)
    write_release_adapter(repo, language=None)
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(
        "# Release Surface Check\n\n- requested review unavailable: missing executor_variants\n",
        encoding="utf-8",
    )

    result = _run_review_gate(repo)

    assert result.returncode == 1
    assert "requested review unavailable" in result.stdout


def test_requested_review_gate_allows_explicit_waiver(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "release").mkdir(parents=True)
    write_release_adapter(repo, language=None)
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(
        "\n".join(
            [
                "# Release Surface Check",
                "",
                "- requested review unavailable: external provider outage",
                "- review waiver: maintainer accepted this release without that requested gate.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = _run_review_gate(repo, "--detail")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "waived"
    assert payload["unavailable_hits"]
    assert payload["waiver_hits"]


def test_requested_review_gate_warns_when_commands_are_empty(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "release").mkdir(parents=True)
    write_release_adapter(repo, ["requested_review_commands: []"], language=None)
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(
        "# Release Surface Check\n\n- Release proof complete.\n",
        encoding="utf-8",
    )

    result = _run_review_gate(repo, "--detail")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "ok"
    assert payload["configuration_status"] == "not_configured"
    assert "requested_review_commands is empty" in payload["warnings"][0]

    plain = _run_review_gate(repo)
    assert plain.returncode == 0, plain.stderr
    assert "WARNING: requested_review_commands is empty" in plain.stdout
    assert "configuration status: not_configured" in plain.stdout


def test_requested_review_gate_honors_advisory_only_policy(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "release").mkdir(parents=True)
    write_release_adapter(
        repo,
        ["requested_review_commands: []", "requested_review_policy: advisory-only"],
        language=None,
    )
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(
        "# Release Surface Check\n\n- Release proof complete.\n",
        encoding="utf-8",
    )

    result = _run_review_gate(repo, "--detail")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["configuration_status"] == "advisory_only"
    assert payload["warnings"] == []

    plain = _run_review_gate(repo)
    assert plain.returncode == 0, plain.stderr
    assert "configuration status: advisory_only" in plain.stdout


def test_requested_review_gate_blocks_failed_command_under_advisory_only_policy(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "release").mkdir(parents=True)
    write_release_adapter(
        repo,
        [
            "requested_review_policy: advisory-only",
            "requested_review_commands:",
            "- \"bash -c 'echo review failed >&2; exit 1'\"",
        ],
        language=None,
    )
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(
        "# Release Surface Check\n\n- Release proof complete.\n",
        encoding="utf-8",
    )

    result = _run_review_gate(repo, "--detail")

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["configuration_status"] == "configured"
    assert payload["requested_review_policy"] == "advisory-only"
    assert "requested review command failed" in payload["blockers"][0]


@pytest.mark.release_only
def test_publish_release_blocks_failed_requested_review_command(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    adapter_path = repo / ".agents" / "release-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "\nrequested_review_commands:\n- \"bash -c 'echo review unavailable >&2; exit 1'\"\n",
        encoding="utf-8",
    )
    subprocess.run(
        ["git", "add", ".agents/release-adapter.yaml"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Configure requested review gate"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    env = _release_env(tmp_path, bin_dir)
    result = _run_publish_patch(repo, env)

    assert result.returncode == 1
    assert "requested release review gate blocked publish" in result.stderr
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    assert not any(entry[:2] == ["release", "create"] for entry in gh_log)


@pytest.mark.release_only
def test_publish_release_blocks_failed_fresh_checkout_probe_before_tag_push(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    (repo / ".git" / "info" / "exclude").write_text(
        ".fresh-checkout-only-missing\n", encoding="utf-8"
    )
    (repo / ".fresh-checkout-only-missing").write_text("maintainer local only\n", encoding="utf-8")
    adapter_path = repo / ".agents" / "release-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + '\nfresh_checkout_probes:\n- "test ! -f .fresh-checkout-only-missing"\n- "test \\"$(git rev-list --count HEAD)\\" = 1"\n- "bash -c \'echo fresh checkout failed >&2; exit 1\'"\n',
        encoding="utf-8",
    )
    subprocess.run(
        ["git", "add", ".agents/release-adapter.yaml"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Configure fresh checkout probe"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    env = _release_env(tmp_path, bin_dir)
    result = _run_publish_patch(repo, env)

    assert result.returncode == 1
    assert "fresh checkout release probes blocked publish" in result.stderr
    assert "fresh checkout failed" in result.stderr
    assert ".fresh-checkout-only-missing" not in result.stderr
    assert "git rev-list --count HEAD" not in result.stderr
    assert (
        subprocess.run(
            ["git", "tag", "--list", "v0.0.1"], cwd=repo, check=True, capture_output=True, text=True
        ).stdout.strip()
        == ""
    )
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    assert not any(entry and entry[0] == "push" for entry in git_log)
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    assert not any(entry[:2] == ["release", "create"] for entry in gh_log)


@pytest.mark.release_only
def test_publish_release_records_passed_fresh_checkout_probes_before_push(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    (repo / ".git" / "info" / "exclude").write_text(
        ".fresh-checkout-only-missing\n", encoding="utf-8"
    )
    (repo / ".fresh-checkout-only-missing").write_text("maintainer local only\n", encoding="utf-8")
    adapter_path = repo / ".agents" / "release-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + '\nfresh_checkout_probes:\n- "test ! -f .fresh-checkout-only-missing"\n- "test \\"$(git rev-list --count HEAD)\\" = 1"\n',
        encoding="utf-8",
    )
    subprocess.run(
        ["git", "add", ".agents/release-adapter.yaml"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Configure passing fresh checkout probes"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    env = _release_env(tmp_path, bin_dir)
    result = _run_publish_patch(repo, env)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["fresh_checkout_probe_status"] == "passed"
    artifact_text = (repo / "charness-artifacts" / "release" / "latest.md").read_text(
        encoding="utf-8"
    )
    assert "Fresh-checkout probe status: passed." in artifact_text
    assert "`test ! -f .fresh-checkout-only-missing`" in artifact_text
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    clone_entries = [entry for entry in git_log if entry and entry[0] == "clone"]
    assert clone_entries
    assert all("--depth" in entry and "1" in entry for entry in clone_entries)
    assert ["commit", "--amend", "--no-edit"] in git_log
    amend_index = git_log.index(["commit", "--amend", "--no-edit"])
    push_index = next(index for index, entry in enumerate(git_log) if entry and entry[0] == "push")
    assert amend_index < push_index


@pytest.mark.release_only
def test_publish_release_runs_adapter_preflight_before_bump(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    ensure_fixture_release_base(repo)
    resolver_path = repo / "skills" / "public" / "release" / "scripts" / "resolve_adapter.py"
    resolver_path.parent.mkdir(parents=True)
    _write_exec(resolver_path, "#!/usr/bin/env python3\nprint('adapter ok')\n")
    test_path = repo / "tests" / "quality_gates" / "test_release_backend.py"
    test_path.parent.mkdir(parents=True)
    test_path.write_text("def test_ok(): pass\n", encoding="utf-8")
    _write_exec(
        bin_dir / "pytest",
        "#!/usr/bin/env bash\necho focused adapter preflight failed >&2\nexit 7\n",
    )
    adapter_path = repo / ".agents" / "release-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8") + "\nfresh_checkout_probes:\n- test ok\n",
        encoding="utf-8",
    )
    subprocess.run(
        ["git", "add", ".agents/release-adapter.yaml", "skills", "tests"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Change release adapter"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    env = _release_env(tmp_path, bin_dir)
    result = _run_publish_patch(repo, env)

    assert result.returncode == 1
    assert "release adapter focused preflight blocked publish before mutation" in result.stderr
    manifest = json.loads((repo / "packaging" / "demo.json").read_text(encoding="utf-8"))
    assert manifest["version"] == "0.0.0"
    assert not (repo / ".quality-ran").exists()
    assert (
        subprocess.run(
            ["git", "tag", "--list", "v0.0.1"],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        == ""
    )


@pytest.mark.release_only
def test_publish_release_records_adapter_preflight_in_release_artifact(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    ensure_fixture_release_base(repo)
    resolver_path = repo / "skills" / "public" / "release" / "scripts" / "resolve_adapter.py"
    resolver_path.parent.mkdir(parents=True)
    _write_exec(resolver_path, "#!/usr/bin/env python3\nprint('adapter ok')\n")
    test_path = repo / "tests" / "quality_gates" / "test_release_backend.py"
    test_path.parent.mkdir(parents=True)
    test_path.write_text("def test_ok(): pass\n", encoding="utf-8")
    _write_exec(bin_dir / "pytest", "#!/usr/bin/env bash\nexit 0\n")
    adapter_path = repo / ".agents" / "release-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8") + "\nfresh_checkout_probes:\n- test ok\n",
        encoding="utf-8",
    )
    subprocess.run(
        ["git", "add", ".agents/release-adapter.yaml", "skills", "tests"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Change release adapter"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    env = _release_env(tmp_path, bin_dir)
    result = _run_publish_patch(repo, env)

    assert result.returncode == 0, result.stderr
    artifact_text = (repo / "charness-artifacts" / "release" / "latest.md").read_text(
        encoding="utf-8"
    )
    assert "## Release Adapter Preflight" in artifact_text
    assert "Release adapter focused preflight status: `required`." in artifact_text
    assert "`fresh_checkout_probes`" in artifact_text
    assert (
        "`pytest tests/quality_gates/test_release_backend.py::test_release_adapter_preserves_fresh_checkout_probes"
        in artifact_text
    )
