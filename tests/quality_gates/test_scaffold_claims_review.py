"""The claims-review authoring capability derives facts instead of asking for copies."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from .release_publish_fixtures import (
    _release_env,
    _run_publish,
    _seed_publish_release_repo,
    claims_review_narrative,
    ensure_fixture_release_base,
)
from .support import ROOT

SCAFFOLD = ROOT / "skills/public/release/scripts/scaffold_claims_review.py"
sys.path.insert(0, str(SCAFFOLD.parent))
from claims_review_scope import changed_paths_sha256, partition  # noqa: E402


def test_scaffold_help_names_the_current_v4_contract() -> None:
    result = subprocess.run(
        ["python3", str(SCAFFOLD), "--help"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    help_text = result.stdout.replace("-\n", "-")
    assert "claims-review v4 record" in help_text
    assert "claims-review v3 record" not in help_text


def _prepare(tmp_path: Path):
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    ensure_fixture_release_base(repo)
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
    return repo, env, yaml.safe_load(prepared.stdout)


def _review_narrative(repo: Path, payload: dict) -> str:
    relative = "charness-artifacts/release-review/reviewer-product.md"
    target = repo / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        claims_review_narrative(payload["prepared_release_commit"], payload["target_version"]),
        encoding="utf-8",
    )
    return relative


def _run_scaffold(repo: Path, narrative: str | None, *, write: bool = True, verdict: str = "pass"):
    args = [
        "python3",
        str(SCAFFOLD),
        "--repo-root",
        str(repo),
        "--verdict",
        verdict,
        "--preparer-context",
        "fixture release operator prepared the marked commit",
        "--reviewer-context",
        "fixture separate reviewer inspected the marked commit",
        "--observer-kind",
        "separate-agent-context" if verdict == "pass" else "unproven",
        "--observer-signal",
        "fixture records a bounded reviewer in a separate agent context",
        "--output",
        "charness-artifacts/release-review/fixture-derived-review.json",
    ]
    if narrative:
        args.extend(["--review-artifact", narrative])
    if write:
        args.append("--write")
    return subprocess.run(args, cwd=ROOT, check=False, capture_output=True, text=True)


@pytest.mark.release_only
def test_scaffold_derives_exact_v4_record_and_resume_accepts_it(tmp_path: Path) -> None:
    repo, env, payload = _prepare(tmp_path)
    narrative = _review_narrative(repo, payload)

    result = _run_scaffold(repo, narrative)

    assert result.returncode == 0, result.stderr
    summary = yaml.safe_load(result.stdout)
    record_path = summary["output"]
    record = json.loads((repo / record_path).read_text(encoding="utf-8"))
    prepared = payload["prepared_release_commit"]
    release_record = subprocess.run(
        ["git", "show", f"{prepared}:charness-artifacts/release/latest.md"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    delta = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", f"v0.0.0..{prepared}"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    split = partition(delta)

    assert record["schema_version"] == "charness.release.claims-review.v4"
    assert record["prepared_commit"] == prepared
    assert record["release_record_sha256"] == hashlib.sha256(release_record.encode()).hexdigest()
    assert record["review_scope"] == {
        "blocking_paths": split["blocking"],
        "advisory_paths": split["advisory"],
    }
    assert record["scope_basis"] == {
        "base_ref": "refs/tags/v0.0.0",
        "changed_paths_sha256": changed_paths_sha256(delta),
        "changed_path_count": len(set(delta)),
    }

    subprocess.run(["git", "add", narrative, record_path], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "Record generated claims review"], cwd=repo, check=True)
    resumed = _run_publish(
        repo,
        env,
        "--resume",
        "--publish-current",
        "--claims-review-artifact",
        record_path,
        "--critique-blocked",
        "synthetic-test-harness does not spawn real critique subagents",
    )
    assert resumed.returncode == 0, resumed.stderr


@pytest.mark.release_only
def test_scaffold_preview_is_read_only_and_unrelated_dirty_state_refuses(tmp_path: Path) -> None:
    repo, _env, payload = _prepare(tmp_path)
    narrative = _review_narrative(repo, payload)

    preview = _run_scaffold(repo, narrative, write=False)

    assert preview.returncode == 0, preview.stderr
    record = yaml.safe_load(preview.stdout)
    assert record["prepared_commit"] == payload["prepared_release_commit"]
    assert not (repo / "charness-artifacts/release-review/fixture-derived-review.json").exists()

    (repo / "README.md").write_text("unrelated operator edit\n", encoding="utf-8")
    refused = _run_scaffold(repo, narrative)
    assert refused.returncode != 0
    assert "unrelated worktree changes" in refused.stderr


@pytest.mark.release_only
def test_scaffold_refuses_a_passing_scope_without_a_release_base(tmp_path: Path) -> None:
    repo, _env, payload = _prepare(tmp_path)
    narrative = _review_narrative(repo, payload)
    subprocess.run(["git", "tag", "-d", "v0.0.0"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "push", "origin", ":refs/tags/v0.0.0"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    result = _run_scaffold(repo, narrative)

    assert result.returncode != 0
    assert "no previous release tag" in result.stderr
