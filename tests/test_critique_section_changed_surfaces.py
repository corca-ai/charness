"""What the default changed-files-and-owning-surfaces producer EMITS.

Split from `test_critique_prepare_packet.py`, which owns adapter loading, section
execution, packet rendering, and the runner CLI that merely configures this
producer. These tests run `render_critique_section_changed_surfaces.py` directly
and own one question: whether the rendered listing tells a reviewer what actually
happened to each path.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts import git_status_snapshot as status
from scripts import render_critique_section_changed_surfaces as producer_module
from tests.quality_gates.repo_shapes import install_two_commit_repo, replace_with_committed_repo
from tests.quality_gates.support import run_script

REPO_ROOT = Path(__file__).resolve().parent.parent
PRODUCER = "scripts/render_critique_section_changed_surfaces.py"


def _run_git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def test_the_changed_files_section_marks_deletions_instead_of_listing_them_as_edits(
    tmp_path: Path,
) -> None:
    """A release review reported "no deletion entry or absence marker for any
    removed component" over a range that removed six files, because the listing
    rendered a removal exactly like an edit. A reviewer cannot ask what a deletion
    cost if the packet never says one happened.
    """
    from tests.quality_gates.repo_shapes import replace_with_committed_repo

    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    (agents_dir / "surfaces.json").write_text(
        json.dumps(
            {
                "version": 1,
                "surfaces": [
                    {
                        "surface_id": "docs",
                        "description": "Markdown",
                        "source_paths": ["*.md"],
                        "derived_paths": [],
                        "sync_commands": [],
                        "verify_commands": ["check docs"],
                        "notes": [],
                        "generated_markdown": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "kept.md").write_text("one\n", encoding="utf-8")
    (tmp_path / "removed.md").write_text("doomed\n", encoding="utf-8")
    replace_with_committed_repo(tmp_path, message="initial")
    (tmp_path / "kept.md").write_text("two\n", encoding="utf-8")
    (tmp_path / "removed.md").unlink()
    _run_git(tmp_path, "add", "-A")
    _run_git(tmp_path, "commit", "-m", "remove one, edit one")

    result = run_script(PRODUCER, "--repo-root", str(tmp_path), "--changed-ref", "HEAD^..HEAD")

    assert result.returncode == 0, result.stderr
    lines = {line.split()[1]: line for line in result.stdout.splitlines() if line.startswith("- ")}
    assert "DELETED" in lines["removed.md"]
    # The discriminator: an edited path in the SAME listing must stay unmarked, or
    # the marker means nothing.
    assert "DELETED" not in lines["kept.md"]
    assert "1 of 2 changed path(s) were DELETED in the ref `HEAD^..HEAD`" in result.stdout


def test_a_ref_with_no_deletions_gains_no_deletion_prose(tmp_path: Path) -> None:
    """The summary line must not appear when nothing was removed."""
    surfaces = json.dumps(
        {
            "version": 1,
            "surfaces": [
                {
                    "surface_id": "docs",
                    "description": "Markdown",
                    "source_paths": ["*.md"],
                    "derived_paths": [],
                    "sync_commands": [],
                    "verify_commands": ["check docs"],
                    "notes": [],
                    "generated_markdown": [],
                }
            ],
        }
    )
    install_two_commit_repo(
        tmp_path,
        {".agents/surfaces.json": surfaces, "kept.md": "one\n"},
        {"kept.md": "two\n"},
        first_message="initial",
        second_message="edit",
    )

    result = run_script(PRODUCER, "--repo-root", str(tmp_path), "--changed-ref", "HEAD^..HEAD")

    assert result.returncode == 0, result.stderr
    assert "DELETED" not in result.stdout


def _repo_with_surfaces(tmp_path: Path) -> Path:
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    (agents_dir / "surfaces.json").write_text(
        json.dumps(
            {
                "version": 1,
                "surfaces": [
                    {
                        "surface_id": "docs",
                        "description": "Markdown",
                        "source_paths": ["*.md"],
                        "derived_paths": [],
                        "sync_commands": [],
                        "verify_commands": ["check docs"],
                        "notes": [],
                        "generated_markdown": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return tmp_path


def test_a_working_tree_deletion_is_marked_too(tmp_path: Path) -> None:
    """The DEFAULT packet is the working-tree one, and it hid removals entirely.

    Scoping the marker to `--changed-ref` fixed the rarer substrate and left the
    common one rendering a removal exactly like an edit.
    """
    repo = _repo_with_surfaces(tmp_path)
    (repo / "kept.md").write_text("one\n", encoding="utf-8")
    (repo / "removed.md").write_text("doomed\n", encoding="utf-8")
    replace_with_committed_repo(repo, message="initial")
    (repo / "kept.md").write_text("two\n", encoding="utf-8")
    (repo / "removed.md").unlink()

    result = run_script(PRODUCER, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    lines = {line.split()[1]: line for line in result.stdout.splitlines() if line.startswith("- ")}
    assert "DELETED" in lines["removed.md"]
    assert "DELETED" not in lines["kept.md"]
    assert "1 of 2 changed path(s) were DELETED in the working tree" in result.stdout


def test_a_staged_deletion_counts_the_same_as_an_unstaged_one(tmp_path: Path) -> None:
    """`git rm` and removing the file on disk are the same fact to a reviewer."""
    repo = _repo_with_surfaces(tmp_path)
    (repo / "kept.md").write_text("one\n", encoding="utf-8")
    (repo / "staged-removal.md").write_text("doomed\n", encoding="utf-8")
    replace_with_committed_repo(repo, message="initial")
    (repo / "kept.md").write_text("two\n", encoding="utf-8")
    _run_git(repo, "rm", "-q", "staged-removal.md")

    result = run_script(PRODUCER, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    lines = {line.split()[1]: line for line in result.stdout.splitlines() if line.startswith("- ")}
    assert "DELETED" in lines["staged-removal.md"]
    assert "DELETED" not in lines["kept.md"]


def test_working_tree_producer_replaces_five_git_processes_with_one_snapshot(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _repo_with_surfaces(tmp_path)
    replace_with_committed_repo(repo, message="initial")
    calls: list[list[str]] = []
    oid = b"a" * 40

    def counting_run(command, *args, **kwargs):
        calls.append(list(command))
        return subprocess.CompletedProcess(
            command,
            0,
            (
                b"1 .M N... 100644 100644 100644 " + oid + b" " + oid + b" kept.md\0"
                b"1 D. N... 100644 000000 000000 " + oid + b" " + (b"0" * 40) + b" removed.md\0"
            ),
            b"",
        )

    monkeypatch.setattr(subprocess, "run", counting_run)
    monkeypatch.setattr(
        sys,
        "argv",
        ["render_critique_section_changed_surfaces.py", "--repo-root", str(repo)],
    )

    assert producer_module.main() == 0
    assert calls == [["git", *status.status_args()]]
    assert "- removed.md  (DELETED" in capsys.readouterr().out


def test_changed_ref_producer_replaces_two_diffs_with_one_name_status_pass(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """`--changed-ref` used to run a `--name-only` diff for the changed paths and a
    second `--name-only --diff-filter=D` diff for the deletions among them, over
    the identical ref. One `--name-status` pass already carries the per-path
    status letter both used to need a separate process to isolate -- the
    `--changed-ref` sibling of `test_working_tree_producer_replaces_five_git_processes_with_one_snapshot`.
    """
    repo = _repo_with_surfaces(tmp_path)
    (repo / "kept.md").write_text("one\n", encoding="utf-8")
    (repo / "removed.md").write_text("doomed\n", encoding="utf-8")
    replace_with_committed_repo(repo, message="initial")
    (repo / "kept.md").write_text("two\n", encoding="utf-8")
    (repo / "removed.md").unlink()
    _run_git(repo, "add", "-A")
    _run_git(repo, "commit", "-m", "remove one, edit one")

    real_run = subprocess.run
    calls: list[list[str]] = []

    def counting_run(command, *args, **kwargs):
        calls.append(list(command))
        return real_run(command, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", counting_run)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "render_critique_section_changed_surfaces.py",
            "--repo-root",
            str(repo),
            "--changed-ref",
            "HEAD^..HEAD",
        ],
    )

    assert producer_module.main() == 0
    git_calls = [call for call in calls if call and call[0] == "git"]
    assert len(git_calls) == 1, git_calls
    assert git_calls[0][:3] == ["git", "diff", "--name-status"]
    lines = {
        line.split()[1]: line
        for line in capsys.readouterr().out.splitlines()
        if line.startswith("- ")
    }
    assert "DELETED" in lines["removed.md"]
    assert "DELETED" not in lines["kept.md"]


def test_a_staged_deletion_that_was_recreated_is_not_marked_deleted(tmp_path: Path) -> None:
    """The marker must mean what the identity binds.

    `git rm` then recreating the file leaves it in the staged-deletion list while
    the file is back on disk, and the identity binds its present bytes. Marking
    it DELETED made the narrative and the binding describe different states of
    the same path — the disagreement this marker exists to end, not create.
    """
    repo = _repo_with_surfaces(tmp_path)
    (repo / "kept.md").write_text("one\n", encoding="utf-8")
    (repo / "revived.md").write_text("original\n", encoding="utf-8")
    replace_with_committed_repo(repo, message="initial")
    _run_git(repo, "rm", "-q", "revived.md")
    (repo / "revived.md").write_text("recreated\n", encoding="utf-8")

    result = run_script(PRODUCER, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    lines = {line.split()[1]: line for line in result.stdout.splitlines() if line.startswith("- ")}
    assert "DELETED" not in lines.get("revived.md", "")
    _run_git(repo, "rm", "-q", "kept.md")
    again = run_script(PRODUCER, "--repo-root", str(repo))
    lines = {line.split()[1]: line for line in again.stdout.splitlines() if line.startswith("- ")}
    assert "DELETED" in lines["kept.md"]
    assert "DELETED" not in lines.get("revived.md", "")


def test_a_retained_but_broken_symlink_is_not_marked_deleted(tmp_path: Path) -> None:
    """`Path.exists()` FOLLOWS a symlink.

    A retained pointer whose target is gone therefore looked absent and rendered
    DELETED, while the link file is still on disk and is the path under review.
    """
    repo = _repo_with_surfaces(tmp_path)
    (repo / "target.md").write_text("target\n", encoding="utf-8")
    (repo / "latest.md").symlink_to("target.md")
    replace_with_committed_repo(repo, message="initial")
    (repo / "target.md").unlink()

    result = run_script(PRODUCER, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    lines = {line.split()[1]: line for line in result.stdout.splitlines() if line.startswith("- ")}
    assert "DELETED" in lines["target.md"], "the removed target IS a deletion"
    assert "latest.md" not in lines or "DELETED" not in lines["latest.md"]
