"""Fixture git never detaches background maintenance.

git >= 2.46 runs `maintenance run --auto` after every `git commit` and lets it
detach. The daemon takes `.git/objects/maintenance.lock` BEFORE it forks, so the
lock is still on disk for a moment after `commit` has returned. A seed builder
publishes its shape the instant that commit returns, and the next test's
`shutil.copytree` lists the lock and then finds it gone: 82 `shutil.Error`s in
one CI baseline run, on whichever tests asked for a fresh shape first (#764).
git 2.34 never detaches, which is why the race never showed locally.

The session gitconfig turns the knob off. These tests assert the knob git
honours rather than sampling the race, which a fast machine loses only about
one commit in forty.
"""

from __future__ import annotations

from pathlib import Path


def test_session_gitconfig_disables_auto_maintenance(tmp_path: Path) -> None:
    from tests.quality_gates.seeding_support import git

    # Outside any repository, so the only source is the session's global config.
    assert git(tmp_path, "config", "--type=bool", "--get", "maintenance.auto") == "false"


def test_a_commit_in_a_seeded_repo_leaves_no_maintenance_lock(tmp_path: Path) -> None:
    from tests.quality_gates.repo_shapes import install_committed_repo
    from tests.quality_gates.seeding_support import git

    repo = install_committed_repo(tmp_path / "repo", {"a.txt": "a\n"})
    (repo / "a.txt").write_text("b\n", encoding="utf-8")
    git(repo, "commit", "-q", "-a", "-m", "edit")

    assert not (repo / ".git" / "objects" / "maintenance.lock").exists()
    assert (
        git(repo, "config", "--type=bool", "--get", "maintenance.auto") == "false"
    )
