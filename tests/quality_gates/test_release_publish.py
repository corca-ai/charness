from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from .release_publish_fixtures import (
    _release_env,
    _run_publish_patch,
    _run_review_gate,
    _seed_publish_release_repo,
    _write_exec,
)


@pytest.mark.release_only
def test_publish_release_bumps_pushes_tags_and_creates_release(tmp_path: Path) -> None:
    repo, remote, bin_dir = _seed_publish_release_repo(tmp_path)
    critique_artifact = repo / "charness-artifacts" / "critique" / "demo.md"
    critique_artifact.parent.mkdir(parents=True)
    critique_artifact.write_text("# Demo critique\n", encoding="utf-8")
    subprocess.run(["git", "add", str(critique_artifact)], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "Add critique proof"], cwd=repo, check=True, capture_output=True, text=True)

    env = _release_env(tmp_path, bin_dir)
    result = _run_publish_patch(repo, env, "--critique-artifact", "charness-artifacts/critique/demo.md")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    manifest = json.loads((repo / "packaging" / "demo.json").read_text(encoding="utf-8"))
    assert payload["previous_version"] == "0.0.0"
    assert payload["target_version"] == "0.0.1"
    assert manifest["version"] == "0.0.1"
    assert (repo / ".quality-ran").read_text(encoding="utf-8").strip() == "quality ok"
    assert (repo / "charness-artifacts" / "release" / "latest.md").is_file()
    assert subprocess.run(["git", "tag", "--list", "v0.0.1"], cwd=repo, check=True, capture_output=True, text=True).stdout.strip() == "v0.0.1"
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
    artifact_text = (repo / "charness-artifacts" / "release" / "latest.md").read_text(encoding="utf-8")
    assert "## Release State" in artifact_text
    assert "GitHub release record: verified URL `https://github.com/example/demo/releases/tag/v0.0.1`" in artifact_text
    assert "public release surface verification: verified" in artifact_text
    assert "## Public Release Verification" in artifact_text
    assert "GitHub release publication: verified by the release backend." in artifact_text
    assert "initial release push carried the release branch update and tag" in artifact_text
    assert "post-publish artifact push recorded the verified public release state" in artifact_text
    assert "No configured public/real-host verification trigger matched" not in artifact_text
    assert "## Review Proof" in artifact_text
    assert "Review proof: `charness-artifacts/critique/demo.md`." in artifact_text
    assert "## Post-Publish Proof" in artifact_text
    assert "Public release check: `gh release view v0.0.1`" in artifact_text
    assert "Run `demo update`." in artifact_text
    assert "Restart the host if the previous version is still visible." in artifact_text
    assert "(tag `v0.0.1`)" in artifact_text
    assert "audit narrative: durable record written to" in artifact_text


@pytest.mark.release_only
def test_release_artifact_does_not_claim_post_publish_proof_before_verification(tmp_path: Path) -> None:
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
    release_create_index = next(index for index, entry in enumerate(gh_log) if entry[:2] == ["release", "create"])
    post_create_views = [entry for entry in gh_log[release_create_index + 1 :] if entry == ["release", "view", "v0.0.1"]]
    assert len(post_create_views) >= 3
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    assert ["push", "origin", "main", "v0.0.1"] in git_log
    assert ["push", "origin", "main"] in git_log
    artifact_text = (repo / "charness-artifacts" / "release" / "latest.md").read_text(encoding="utf-8")
    assert "public release surface verification: failed" in artifact_text
    assert "create returned `https://github.com/example/demo/releases/tag/v0.0.1`" in artifact_text
    assert "post-create verification failed" in artifact_text
    assert "## Post-Publish Proof" not in artifact_text


@pytest.mark.release_only
def test_publish_release_does_not_close_issues_when_post_create_verification_fails(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)

    env = _release_env(tmp_path, bin_dir)
    env["FAKE_GH_ISSUE_STATE"] = str(tmp_path / "issue-state.json")
    env["FAKE_GH_RELEASE_CREATE_WITHOUT_VIEW"] = "1"
    Path(env["FAKE_GH_ISSUE_STATE"]).write_text(json.dumps({"44": "OPEN"}) + "\n", encoding="utf-8")
    result = _run_publish_patch(repo, env, "--close-issue", "44")

    assert result.returncode == 1
    state = json.loads(Path(env["FAKE_GH_ISSUE_STATE"]).read_text(encoding="utf-8"))
    assert state["44"] == "OPEN"
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    release_create_index = next(index for index, entry in enumerate(gh_log) if entry[:2] == ["release", "create"])
    post_create_views = [entry for entry in gh_log[release_create_index + 1 :] if entry == ["release", "view", "v0.0.1"]]
    assert len(post_create_views) >= 3
    assert not any(entry[:2] == ["issue", "close"] for entry in gh_log)
    artifact_text = (repo / "charness-artifacts" / "release" / "latest.md").read_text(encoding="utf-8")
    assert "Issue closeout verification: pending or not requested." in artifact_text


@pytest.mark.release_only
def test_publish_release_verifies_and_falls_back_to_manual_issue_close(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)

    env = _release_env(tmp_path, bin_dir)
    env["FAKE_GH_ISSUE_STATE"] = str(tmp_path / "issue-state.json")
    Path(env["FAKE_GH_ISSUE_STATE"]).write_text(json.dumps({"44": "OPEN"}) + "\n", encoding="utf-8")
    result = _run_publish_patch(repo, env, "--close-issue", "44")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["issue_closeout_preflight"]["status"] == "verified"
    assert payload["issue_closeout_preflight"]["issues"][0]["state"] == "OPEN"
    assert payload["issue_closeout"]["status"] == "verified"
    assert payload["issue_closeout"]["issues"][0]["state"] == "CLOSED"
    assert payload["issue_closeout"]["issues"][0]["preflight_state"] == "OPEN"
    assert payload["issue_closeout"]["issues"][0]["carrier"] == "direct_release_commit_body"
    assert payload["issue_closeout"]["issues"][0]["manual_fallback_used"] is True
    assert payload["issue_closeout_commit_sha"]
    artifact_text = (repo / "charness-artifacts" / "release" / "latest.md").read_text(encoding="utf-8")
    assert "## Issue Closeout" in artifact_text
    assert "Issue closeout verification: `verified`." in artifact_text
    assert "Issue #44: `CLOSED`" in artifact_text
    assert "carrier: `direct_release_commit_body`" in artifact_text
    assert "manual fallback used: `True`" in artifact_text
    commit_body = subprocess.run(
        ["git", "log", "--format=%B", "-2"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert "Close #44." in commit_body
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    assert ["issue", "view", "44", "--repo", "example/demo", "--json", "number,state,url"] in gh_log
    assert any(entry[:5] == ["issue", "close", "44", "--repo", "example/demo"] for entry in gh_log)
    release_create_index = next(index for index, entry in enumerate(gh_log) if entry[:2] == ["release", "create"])
    issue_view_indexes = [
        index for index, entry in enumerate(gh_log)
        if entry == ["issue", "view", "44", "--repo", "example/demo", "--json", "number,state,url"]
    ]
    assert issue_view_indexes[0] < release_create_index
    assert issue_view_indexes[-1] > release_create_index


@pytest.mark.release_only
def test_publish_release_records_real_host_proof_for_unreleased_content(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    adapter_path = repo / ".agents" / "release-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "\nreal_host_required_path_globs:\n- README.md\nreal_host_checklist:\n- Verify on a clean host.\n",
        encoding="utf-8",
    )
    (repo / ".agents" / "surfaces.json").write_text(
        json.dumps(
            {
                "version": 1,
                "surfaces": [
                    {
                        "surface_id": "operator-docs",
                        "description": "Operator docs.",
                        "source_paths": ["README.md"],
                        "derived_paths": [],
                        "sync_commands": [],
                        "verify_commands": [],
                        "notes": [],
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    readme_path = repo / "README.md"
    readme_path.write_text("# Demo\n\nChanged operator surface.\n", encoding="utf-8")
    subprocess.run(
        ["git", "add", "README.md", ".agents/release-adapter.yaml", ".agents/surfaces.json"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Change operator surface"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    env = _release_env(tmp_path, bin_dir)
    result = _run_publish_patch(repo, env)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    artifact_text = (repo / "charness-artifacts" / "release" / "latest.md").read_text(encoding="utf-8")
    assert payload["real_host_required"] is True
    assert "Release-time real-host proof is required for this slice." in artifact_text
    assert "Verify on a clean host." in artifact_text


def test_requested_review_gate_blocks_unavailable_release_record(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "release").mkdir(parents=True)
    (repo / ".agents" / "release-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "output_dir: charness-artifacts/release",
                "",
            ]
        ),
        encoding="utf-8",
    )
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
    (repo / ".agents" / "release-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "output_dir: charness-artifacts/release",
                "",
            ]
        ),
        encoding="utf-8",
    )
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

    result = _run_review_gate(repo, "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "waived"
    assert payload["unavailable_hits"]
    assert payload["waiver_hits"]


def test_requested_review_gate_warns_when_commands_are_empty(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "release").mkdir(parents=True)
    (repo / ".agents" / "release-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "output_dir: charness-artifacts/release",
                "requested_review_commands: []",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(
        "# Release Surface Check\n\n- Release proof complete.\n",
        encoding="utf-8",
    )

    result = _run_review_gate(repo, "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"
    assert payload["configuration_status"] == "not_configured"
    assert "requested_review_commands is empty" in payload["warnings"][0]

    plain = _run_review_gate(repo)
    assert plain.returncode == 0, plain.stderr
    assert "WARNING: requested_review_commands is empty" in plain.stdout


@pytest.mark.release_only
def test_publish_release_blocks_failed_requested_review_command(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    adapter_path = repo / ".agents" / "release-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "\nrequested_review_commands:\n- \"bash -c 'echo review unavailable >&2; exit 1'\"\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", ".agents/release-adapter.yaml"], cwd=repo, check=True, capture_output=True, text=True)
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
    (repo / ".git" / "info" / "exclude").write_text(".fresh-checkout-only-missing\n", encoding="utf-8")
    (repo / ".fresh-checkout-only-missing").write_text("maintainer local only\n", encoding="utf-8")
    adapter_path = repo / ".agents" / "release-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "\nfresh_checkout_probes:\n- \"test ! -f .fresh-checkout-only-missing\"\n- \"test \\\"$(git rev-list --count HEAD)\\\" = 1\"\n- \"bash -c 'echo fresh checkout failed >&2; exit 1'\"\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", ".agents/release-adapter.yaml"], cwd=repo, check=True, capture_output=True, text=True)
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
    assert subprocess.run(["git", "tag", "--list", "v0.0.1"], cwd=repo, check=True, capture_output=True, text=True).stdout.strip() == ""
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    assert not any(entry and entry[0] == "push" for entry in git_log)
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    assert not any(entry[:2] == ["release", "create"] for entry in gh_log)


@pytest.mark.release_only
def test_publish_release_records_passed_fresh_checkout_probes_before_push(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    (repo / ".git" / "info" / "exclude").write_text(".fresh-checkout-only-missing\n", encoding="utf-8")
    (repo / ".fresh-checkout-only-missing").write_text("maintainer local only\n", encoding="utf-8")
    adapter_path = repo / ".agents" / "release-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "\nfresh_checkout_probes:\n- \"test ! -f .fresh-checkout-only-missing\"\n- \"test \\\"$(git rev-list --count HEAD)\\\" = 1\"\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", ".agents/release-adapter.yaml"], cwd=repo, check=True, capture_output=True, text=True)
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
    payload = json.loads(result.stdout)
    assert payload["fresh_checkout_probe_status"] == "passed"
    artifact_text = (repo / "charness-artifacts" / "release" / "latest.md").read_text(encoding="utf-8")
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
    subprocess.run(["git", "tag", "v0.0.0"], cwd=repo, check=True, capture_output=True, text=True)
    resolver_path = repo / "skills" / "public" / "release" / "scripts" / "resolve_adapter.py"
    resolver_path.parent.mkdir(parents=True)
    _write_exec(resolver_path, "#!/usr/bin/env python3\nprint('adapter ok')\n")
    test_path = repo / "tests" / "quality_gates" / "test_release_real_host.py"
    test_path.parent.mkdir(parents=True)
    test_path.write_text("def test_ok(): pass\n", encoding="utf-8")
    _write_exec(
        bin_dir / "pytest",
        "#!/usr/bin/env bash\n"
        "echo focused adapter preflight failed >&2\n"
        "exit 7\n",
    )
    adapter_path = repo / ".agents" / "release-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "\nreal_host_checklist:\n- Verify tokei on a clean temp-home.\n",
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
    assert subprocess.run(
        ["git", "tag", "--list", "v0.0.1"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip() == ""


@pytest.mark.release_only
def test_publish_release_records_adapter_preflight_in_release_artifact(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    subprocess.run(["git", "tag", "v0.0.0"], cwd=repo, check=True, capture_output=True, text=True)
    resolver_path = repo / "skills" / "public" / "release" / "scripts" / "resolve_adapter.py"
    resolver_path.parent.mkdir(parents=True)
    _write_exec(resolver_path, "#!/usr/bin/env python3\nprint('adapter ok')\n")
    test_path = repo / "tests" / "quality_gates" / "test_release_real_host.py"
    test_path.parent.mkdir(parents=True)
    test_path.write_text("def test_ok(): pass\n", encoding="utf-8")
    _write_exec(bin_dir / "pytest", "#!/usr/bin/env bash\nexit 0\n")
    adapter_path = repo / ".agents" / "release-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "\nreal_host_checklist:\n- Verify tokei on a clean temp-home.\n",
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
    artifact_text = (repo / "charness-artifacts" / "release" / "latest.md").read_text(encoding="utf-8")
    assert "## Release Adapter Preflight" in artifact_text
    assert "Release adapter focused preflight status: `required`." in artifact_text
    assert "`real_host_checklist`" in artifact_text
    assert "`pytest tests/quality_gates/test_release_real_host.py -q`" in artifact_text
