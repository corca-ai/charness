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
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _run_git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def test_the_changed_files_section_marks_deletions_instead_of_listing_them_as_edits(
    tmp_path: Path,
) -> None:
    """A release review reported "no deletion entry or absence marker for any
    removed component" over a range that removed six files, because the listing
    rendered a removal exactly like an edit. A reviewer cannot ask what a deletion
    cost if the packet never says one happened.
    """
    _run_git(tmp_path, "init")
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
    _run_git(tmp_path, "add", ".")
    _run_git(tmp_path, "commit", "-m", "initial")
    (tmp_path / "kept.md").write_text("two\n", encoding="utf-8")
    (tmp_path / "removed.md").unlink()
    _run_git(tmp_path, "add", "-A")
    _run_git(tmp_path, "commit", "-m", "remove one, edit one")

    producer = REPO_ROOT / "scripts/render_critique_section_changed_surfaces.py"
    result = subprocess.run(
        ["python3", str(producer), "--repo-root", str(tmp_path), "--changed-ref", "HEAD^..HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    lines = {line.split()[1]: line for line in result.stdout.splitlines() if line.startswith("- ")}
    assert "DELETED" in lines["removed.md"]
    # The discriminator: an edited path in the SAME listing must stay unmarked, or
    # the marker means nothing.
    assert "DELETED" not in lines["kept.md"]
    assert "1 of 2 changed path(s) were DELETED in the ref `HEAD^..HEAD`" in result.stdout


def test_a_ref_with_no_deletions_gains_no_deletion_prose(tmp_path: Path) -> None:
    """The summary line must not appear when nothing was removed."""
    _run_git(tmp_path, "init")
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
    _run_git(tmp_path, "add", ".")
    _run_git(tmp_path, "commit", "-m", "initial")
    (tmp_path / "kept.md").write_text("two\n", encoding="utf-8")
    _run_git(tmp_path, "commit", "-am", "edit")

    producer = REPO_ROOT / "scripts/render_critique_section_changed_surfaces.py"
    result = subprocess.run(
        ["python3", str(producer), "--repo-root", str(tmp_path), "--changed-ref", "HEAD^..HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "DELETED" not in result.stdout


def _repo_with_surfaces(tmp_path: Path) -> Path:
    _run_git(tmp_path, "init")
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
    _run_git(repo, "add", "-A")
    _run_git(repo, "commit", "-m", "initial")
    (repo / "kept.md").write_text("two\n", encoding="utf-8")
    (repo / "removed.md").unlink()

    producer = REPO_ROOT / "scripts/render_critique_section_changed_surfaces.py"
    result = subprocess.run(
        ["python3", str(producer), "--repo-root", str(repo)],
        capture_output=True,
        text=True,
        check=False,
    )

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
    _run_git(repo, "add", "-A")
    _run_git(repo, "commit", "-m", "initial")
    (repo / "kept.md").write_text("two\n", encoding="utf-8")
    _run_git(repo, "rm", "-q", "staged-removal.md")

    producer = REPO_ROOT / "scripts/render_critique_section_changed_surfaces.py"
    result = subprocess.run(
        ["python3", str(producer), "--repo-root", str(repo)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    lines = {line.split()[1]: line for line in result.stdout.splitlines() if line.startswith("- ")}
    assert "DELETED" in lines["staged-removal.md"]
    assert "DELETED" not in lines["kept.md"]
