"""The push-time binding between gate validation evidence and what is pushed.

The resume publish lane validates (quality gates + fresh-checkout probes) and
then MOVES the tree (receipt promotion, the artifact refresh commit) before
`git push`. These cases drive the binding helpers against a real repository:
the seal must record what the gates saw versus what the push carries, and a
HEAD that moves after the seal must refuse the push instead of publishing
state the gates never saw.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from .release_script_loading import load_release_script

_BINDING = load_release_script("publish_release_push_binding")


class _GitCli:
    """Run git for real and record intent, so drift is actual repository drift."""

    def __init__(self) -> None:
        self.commands: list[list[str]] = []

    def run(self, command, *, cwd, check=True):
        self.commands.append([str(part) for part in command])
        result = subprocess.run(
            [str(part) for part in command],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        if check and result.returncode != 0:
            raise SystemExit(f"command failed: {' '.join(command)}\n{result.stderr}")
        return SimpleNamespace(
            returncode=result.returncode, stdout=result.stdout, stderr=result.stderr
        )


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        [
            "git",
            "-c",
            "user.name=Binding Test",
            "-c",
            "user.email=binding@example.com",
            *args,
        ],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main", "-q")
    (repo / "release.md").write_text("release\n", encoding="utf-8")
    _git(repo, "add", "release.md")
    _git(repo, "commit", "-qm", "Release v1.2.3")
    return repo


def test_binding_records_validation_seal_and_push_digests(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    cli = _GitCli()
    payload: dict = {}

    _BINDING._record_validation_binding(cli, repo, payload)
    validated = _git(repo, "rev-parse", "HEAD")
    assert payload["push_binding"]["validated_head"] == validated

    (repo / "release.md").write_text("release refreshed\n", encoding="utf-8")
    _git(repo, "commit", "-qam", "chore(release): commit v1.2.3 artifact before resume push")
    _BINDING._seal_push_binding(cli, repo, payload)

    binding = payload["push_binding"]
    assert binding["push_head"] == _git(repo, "rev-parse", "HEAD")
    assert binding["push_head"] != validated
    assert binding["validated_to_push_changes"] == ["release.md"]

    _git(repo, "tag", "v1.2.3", binding["push_head"])
    checked = _BINDING._verify_push_binding(
        cli, repo, payload, tag_name="v1.2.3", expected_tag_commit=binding["push_head"]
    )
    assert checked["pushed_head"] == binding["push_head"]
    assert checked["pushed_tree"] == binding["push_tree"]
    assert checked["tag_target"] == binding["push_head"]
    assert checked["expected_tag_commit"] == binding["push_head"]
    assert not any(command[:2] == ["git", "push"] for command in cli.commands)


def test_verify_refuses_a_head_that_moved_after_the_seal(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    cli = _GitCli()
    payload: dict = {}

    _BINDING._record_validation_binding(cli, repo, payload)
    _BINDING._seal_push_binding(cli, repo, payload)

    (repo / "intruder.md").write_text("not validated\n", encoding="utf-8")
    _git(repo, "add", "intruder.md")
    _git(repo, "commit", "-qm", "unvalidated drift")

    with pytest.raises(SystemExit, match="moved between the sealed pre-push state"):
        _BINDING._verify_push_binding(
            cli, repo, payload, tag_name="v1.2.3", expected_tag_commit="whatever"
        )
    assert not any(command[:2] == ["git", "push"] for command in cli.commands)


def test_verify_refuses_without_a_seal(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    cli = _GitCli()

    with pytest.raises(SystemExit, match="without a sealed push binding"):
        _BINDING._verify_push_binding(
            cli, repo, {}, tag_name="v1.2.3", expected_tag_commit="whatever"
        )


def test_binding_binds_but_does_not_refuse_a_repointed_tag(tmp_path: Path) -> None:
    """Tag identity is classified upstream; the binding records it as evidence."""
    repo = _repo(tmp_path)
    cli = _GitCli()
    payload: dict = {}

    _BINDING._record_validation_binding(cli, repo, payload)
    validated = payload["push_binding"]["validated_head"]
    _git(repo, "tag", "v1.2.3", validated)

    (repo / "other.md").write_text("other\n", encoding="utf-8")
    _git(repo, "add", "other.md")
    _git(repo, "commit", "-qm", "other")
    other = _git(repo, "rev-parse", "HEAD")
    _BINDING._seal_push_binding(cli, repo, payload)
    _git(repo, "tag", "-f", "v1.2.3", other)

    checked = _BINDING._verify_push_binding(
        cli,
        repo,
        payload,
        tag_name="v1.2.3",
        expected_tag_commit=validated,
    )
    assert checked["tag_target"] == other
    assert checked["expected_tag_commit"] == validated


class _EmptyCli:
    """Answer rev-parse with nothing, so no digest can be bound."""

    def run(self, command, *, cwd, check=True):
        return SimpleNamespace(returncode=0, stdout="\n", stderr="")


def test_git_head_and_tree_refuses_unresolvable_head(tmp_path: Path) -> None:
    repo = _repo(tmp_path)

    with pytest.raises(SystemExit, match="could not resolve HEAD"):
        _BINDING._git_head_and_tree(_EmptyCli(), repo)


def test_push_binding_loader_refuses_a_broken_spec(monkeypatch: pytest.MonkeyPatch) -> None:
    publish = load_release_script("publish_release_resume_publish")
    monkeypatch.setattr(
        publish.importlib.util, "spec_from_file_location", lambda *args, **kwargs: None
    )

    with pytest.raises(ImportError, match="Unable to load"):
        publish._load_push_binding()
