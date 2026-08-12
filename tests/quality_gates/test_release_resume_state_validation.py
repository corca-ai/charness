from __future__ import annotations

import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from .release_script_loading import load_release_script

RESUME = load_release_script("publish_release_resume", suffix="state_validation")
HELPERS = load_release_script("publish_release_helpers", suffix="tag_identity")


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()


def test_remote_annotated_tag_identity_is_peeled_to_release_commit(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    remote = tmp_path / "remote.git"
    repo.mkdir()
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    _git(repo, "init", "-b", "main")
    (repo / "README.md").write_text("release\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "seed")
    release_sha = _git(repo, "rev-parse", "HEAD")
    _git(repo, "tag", "-a", "v1.2.3", "-m", "release")
    _git(repo, "remote", "add", "origin", str(remote))
    _git(repo, "push", "origin", "v1.2.3")

    state = HELPERS.tag_exists(repo, "v1.2.3", remote="origin")

    assert state == {"local": True, "remote": True, "remote_tag_sha": release_sha}


def test_remote_lightweight_tag_identity_uses_direct_commit(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    remote = tmp_path / "remote.git"
    repo.mkdir()
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    _git(repo, "init", "-b", "main")
    (repo / "README.md").write_text("release\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "seed")
    release_sha = _git(repo, "rev-parse", "HEAD")
    _git(repo, "tag", "v1.2.3")
    _git(repo, "remote", "add", "origin", str(remote))
    _git(repo, "push", "origin", "v1.2.3")

    state = HELPERS.tag_exists(repo, "v1.2.3", remote="origin")

    assert state == {"local": True, "remote": True, "remote_tag_sha": release_sha}


@pytest.mark.parametrize(
    ("stdout", "message"),
    [
        ("f" * 40 + "\trefs/tags/other\n", "returned `refs/tags/other`"),
        ("f" * 40 + "\trefs/tags/v1.2.3\n" + "e" * 40 + "\trefs/tags/v1.2.3\n", "ambiguous records"),
        ("not-an-object\trefs/tags/v1.2.3\n", "invalid full object id"),
    ],
)
def test_remote_tag_record_parser_rejects_untrusted_output(stdout: str, message: str) -> None:
    with pytest.raises(SystemExit, match=message):
        HELPERS._single_remote_object_id(stdout, expected_ref="refs/tags/v1.2.3")


def _published_state(phase: str) -> dict[str, object]:
    return {
        "phase": phase,
        "tag_local": True,
        "tag_remote": True,
        "release_exists": True,
        "tag_sha": "release-sha",
        "remote_tag_sha": "release-sha",
        "head_parent_is_tag": True,
        "parent_sha": "carrier-sha",
        "head_grandparent_is_tag": True,
        "remote_branch_sha": "release-sha" if phase == "post-publication-carrier" else "carrier-sha",
        "head_sha": "local-sha",
    }


@pytest.mark.parametrize(
    ("phase", "override", "message"),
    [
        (
            "post-publication-carrier",
            {"tag_remote": False},
            "lacks confirmed tag/release publication state",
        ),
        (
            "post-publication-carrier",
            {"remote_tag_sha": "wrong-release-sha"},
            "remote tag `v1.2.3` does not resolve to the local release commit",
        ),
        (
            "post-publication-carrier",
            {"head_parent_is_tag": False},
            "carrier HEAD is not directly based on its release tag",
        ),
        (
            "post-publication-final",
            {"head_grandparent_is_tag": False},
            "final closeout HEAD is not based on its carrier and release tag",
        ),
        (
            "post-publication-carrier",
            {"remote_branch_sha": "unrelated-sha"},
            "refusing ambiguous closeout recovery",
        ),
    ],
)
def test_assert_resumable_rejects_ambiguous_published_state(
    phase: str, override: dict[str, object], message: str
) -> None:
    state = {**_published_state(phase), **override}

    with pytest.raises(SystemExit, match=message):
        RESUME.assert_resumable(state, tag_name="v1.2.3")


def test_claims_evidence_classifier_rejects_a_non_direct_descendant() -> None:
    class Cli:
        def run(self, command: list[str], *, cwd: Path, check: bool = True):
            if command == ["git", "show", "-s", "--format=%P", "evidence-sha"]:
                return SimpleNamespace(returncode=0, stdout="prepared-sha intermediary-sha\n")
            raise AssertionError(f"unexpected command: {command}")

    assert not RESUME._is_claims_evidence_commit(
        Cli(), Path("."), prepared_commit="prepared-sha", evidence_commit="evidence-sha"
    )
