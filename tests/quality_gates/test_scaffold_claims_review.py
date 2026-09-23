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
pytestmark = pytest.mark.boundary_contract(
    reason="observe the claims-review scaffold executable and its real git-backed release record boundary"
)
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


@pytest.mark.release_only
def test_scaffold_and_resume_accept_paperwork_tail_between_prepare_and_claims(
    tmp_path: Path,
) -> None:
    """A record-correction commit between prepare and claims must not strand the release.

    Regression for the v8.11.1 round-1 topology (prepared -> ledger correction
    -> claims): fixed-position boundary checks refused the scaffold ("HEAD is
    not the one-parent commit") and the resume ("no single-parent prepared
    boundary"), and the only documented recovery was abandon-reset -- for a
    state the tool's own routine behavior produced. The boundary walk binds
    the tag-bound introducer through a bounded paperwork tail.
    """
    repo, env, payload = _prepare(tmp_path)
    prepared = payload["prepared_release_commit"]
    correction = repo / "charness-artifacts" / "issue" / "fixture-closeout.md"
    correction.parent.mkdir(parents=True, exist_ok=True)
    correction.write_text("Closes #44\n", encoding="utf-8")
    subprocess.run(["git", "add", str(correction)], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "Correct fixture closeout ledger"], cwd=repo, check=True)
    narrative = _review_narrative(repo, payload)

    result = _run_scaffold(repo, narrative)

    assert result.returncode == 0, result.stderr
    record_path = yaml.safe_load(result.stdout)["output"]
    record = json.loads((repo / record_path).read_text(encoding="utf-8"))
    assert record["prepared_commit"] == prepared
    # The review scope is the release delta ending at the prepared commit;
    # the tail correction must not leak into the reviewed scope.
    assert "charness-artifacts/issue/fixture-closeout.md" not in record["review_scope"][
        "blocking_paths"
    ]
    assert "charness-artifacts/issue/fixture-closeout.md" not in record["review_scope"][
        "advisory_paths"
    ]

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


def _boundary_repo(tmp_path: Path, *, tag: str = "v9.9.9"):
    """A temp repo with no release record; returns repo, record path, run, tag."""
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-b", "main", str(repo)], check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=repo, check=True)
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "seed"], cwd=repo, check=True)

    def run(command: list[str], *, cwd: Path, check: bool = True):
        return subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=check)

    record_path = "charness-artifacts/release/latest.md"
    return repo, record_path, run, tag


def _commit_record(repo: Path, record_path: str, text: str, message: str) -> str:
    target = repo / record_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    subprocess.run(["git", "add", record_path], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=repo, check=True)
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()


def _commit_file(repo: Path, name: str, text: str, message: str) -> str:
    target = repo / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    subprocess.run(["git", "add", name], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=repo, check=True)
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()


def _marked_record(marker: str, tag: str) -> str:
    return f"<!-- {marker} -->\ntag `{tag}`\n"


def test_boundary_walk_finds_introducer_through_paperwork_tail(tmp_path: Path) -> None:
    from .release_script_loading import load_release_script as _load

    claims = _load("publish_release_claims_review", suffix="boundary")
    repo, record_path, run, tag = _boundary_repo(tmp_path)
    prepared = _commit_record(
        repo, record_path, _marked_record(claims.MARKER, tag), "prepare"
    )
    _commit_file(repo, "charness-artifacts/issue/note.md", "correction\n", "correction")

    found = claims.find_prepared_boundary_for_tag(
        repo, head="HEAD", tag_name=tag, record_path=record_path, run=run
    )

    assert found is not None
    assert found["commit"] == prepared
    assert found["path"] == record_path


def test_boundary_walk_refuses_second_prepare_for_same_tag(tmp_path: Path) -> None:
    from .release_script_loading import load_release_script as _load

    claims = _load("publish_release_claims_review", suffix="boundary")
    repo, record_path, run, tag = _boundary_repo(tmp_path)
    _commit_record(repo, record_path, _marked_record(claims.MARKER, tag), "prepare one")
    _commit_record(
        repo,
        record_path,
        _marked_record(claims.MARKER, tag) + "re-prepared\n",
        "prepare two",
    )

    assert (
        claims.find_prepared_boundary_for_tag(
            repo, head="HEAD", tag_name=tag, record_path=record_path, run=run
        )
        is None
    )


def test_boundary_walk_refuses_product_path_in_tail(tmp_path: Path) -> None:
    from .release_script_loading import load_release_script as _load

    claims = _load("publish_release_claims_review", suffix="boundary")
    repo, record_path, run, tag = _boundary_repo(tmp_path)
    _commit_record(repo, record_path, _marked_record(claims.MARKER, tag), "prepare")
    _commit_file(repo, "README.md", "base\nsource edit\n", "source edit")

    assert (
        claims.find_prepared_boundary_for_tag(
            repo, head="HEAD", tag_name=tag, record_path=record_path, run=run
        )
        is None
    )


def test_boundary_walk_ignores_older_tag_introducer(tmp_path: Path) -> None:
    from .release_script_loading import load_release_script as _load

    claims = _load("publish_release_claims_review", suffix="boundary")
    repo, record_path, run, tag = _boundary_repo(tmp_path)
    _commit_record(repo, record_path, _marked_record(claims.MARKER, "v0.0.0"), "old prepare")
    _commit_record(repo, record_path, "published record\n", "publish rewrites record")
    prepared = _commit_record(
        repo, record_path, _marked_record(claims.MARKER, tag), "prepare"
    )

    found = claims.find_prepared_boundary_for_tag(
        repo, head="HEAD", tag_name=tag, record_path=record_path, run=run
    )

    assert found is not None
    assert found["commit"] == prepared


def test_boundary_walk_returns_none_without_marker(tmp_path: Path) -> None:
    from .release_script_loading import load_release_script as _load

    claims = _load("publish_release_claims_review", suffix="boundary")
    repo, record_path, run, tag = _boundary_repo(tmp_path)

    assert (
        claims.find_prepared_boundary_for_tag(
            repo, head="HEAD", tag_name=tag, record_path=record_path, run=run
        )
        is None
    )


def _scaffold_args(repo: Path, narrative: str | None, *, verdict: str = "pass"):
    from argparse import Namespace

    return Namespace(
        repo_root=repo,
        verdict=verdict,
        reviewer_context="fixture separate reviewer inspected the marked commit",
        observer_kind="separate-agent-context" if verdict == "pass" else "unproven",
        observer_signal="fixture records a bounded reviewer in a separate agent context",
        review_artifact=narrative,
        preparer_context="fixture release operator prepared the marked commit",
        advisory_finding=[],
        output="charness-artifacts/release-review/fixture-derived-review.json",
        remote="origin",
        write=False,
    )


def test_prepared_facts_and_build_record_bind_through_a_paperwork_tail(
    tmp_path: Path,
) -> None:
    """The scaffold's tail path, driven in-process where coverage can see it.

    The spawned tail test above proves the operator-visible behaviour end to
    end, but a subprocess is invisible to in-process coverage -- which is why
    the prepared-facts tail read as unproven. Same topology (prepare, ledger
    correction, scaffold), driven through `_prepared_facts`/`build_record`
    directly: the introducer binds the prepared commit below the tail, and the
    tail correction stays out of the reviewed scope.
    """
    from .release_script_loading import load_release_script as _load

    scaffold = _load("scaffold_claims_review", suffix="facts")
    repo, _env, payload = _prepare(tmp_path)
    prepared = payload["prepared_release_commit"]
    correction = repo / "charness-artifacts" / "issue" / "fixture-closeout.md"
    correction.parent.mkdir(parents=True, exist_ok=True)
    correction.write_text("Closes #44\n", encoding="utf-8")
    subprocess.run(["git", "add", str(correction)], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "Correct fixture closeout ledger"], cwd=repo, check=True)
    narrative = _review_narrative(repo, payload)

    facts = scaffold._prepared_facts(_scaffold_args(repo, narrative))

    assert facts["prepared"]["commit"] == prepared
    record, summary = scaffold.build_record(_scaffold_args(repo, narrative))
    assert record["prepared_commit"] == prepared
    assert summary["prepared_commit"] == prepared
    assert "charness-artifacts/issue/fixture-closeout.md" not in record["review_scope"][
        "blocking_paths"
    ]


def test_prepared_facts_refuses_when_head_lost_the_prepared_marker(
    tmp_path: Path,
) -> None:
    """After publication rewrites the record, the scaffold must refuse.

    The marker is gone from HEAD, so no prepared stop is outstanding: binding
    whatever boundary the walk would find below (the previous release's, or
    nothing) would author a review against a release that already shipped.
    """
    from .release_script_loading import load_release_script as _load

    scaffold = _load("scaffold_claims_review", suffix="facts")
    repo, _env, payload = _prepare(tmp_path)
    record_path = "charness-artifacts/release/latest.md"
    published = (repo / record_path).read_text(encoding="utf-8").replace(
        scaffold._evidence.PREPARED_MARKER, "<!-- published -->"
    )
    (repo / record_path).write_text(published, encoding="utf-8")
    subprocess.run(["git", "add", record_path], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "Publish release"], cwd=repo, check=True)
    narrative = _review_narrative(repo, payload)

    with pytest.raises(SystemExit, match="does not carry the prepared claims-review marker"):
        scaffold._prepared_facts(_scaffold_args(repo, narrative))
