from __future__ import annotations

from pathlib import Path

from .support import init_git_repo, run_script


def test_check_doc_links_rejects_absolute_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("[bad](/tmp/not-in-repo.md)\n", encoding="utf-8")
    result = run_script("scripts/check-doc-links.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "absolute link" in result.stderr


def test_check_doc_links_rejects_repo_local_absolute_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    docs_dir.mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (docs_dir / "handoff.md").write_text(
        f"[root]({repo / 'README.md'})\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check-doc-links.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "absolute link" in result.stderr


def test_check_doc_links_rejects_bare_internal_markdown_reference(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    docs_dir.mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n\nSee docs/guide.md before editing.\n", encoding="utf-8")
    (docs_dir / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_script("scripts/check-doc-links.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "bare internal markdown reference" in result.stderr


def test_check_doc_links_allows_runnable_commands_and_concept_tokens_in_backticks(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    docs_dir.mkdir(parents=True)
    (repo / "README.md").write_text(
        "\n".join(
            [
                "# Demo",
                "",
                "Use the linked guide: [guide](docs/guide.md).",
                "",
                "Runnable command in inline code: `sed -n '1,20p' docs/guide.md`.",
                "",
                "Concept token without extension: `charness-concept`.",
                "",
                "Version strings: `v1.2.3`, `a.b.c`.",
                "",
                "```bash",
                "sed -n '1,20p' docs/guide.md",
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (docs_dir / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_script("scripts/check-doc-links.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_check_doc_links_rejects_backticked_nested_file_reference(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    docs_dir.mkdir(parents=True)
    (repo / "README.md").write_text(
        "See `docs/guide.md` for the guide.\n",
        encoding="utf-8",
    )
    (docs_dir / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_script("scripts/check-doc-links.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "backticked file reference" in result.stderr
    assert "docs/guide.md" in result.stderr


def test_check_doc_links_rejects_backticked_root_file_with_extension(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "README.md").write_text(
        "See `AGENTS.md` for house rules.\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check-doc-links.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "backticked file reference" in result.stderr
    assert "AGENTS.md" in result.stderr


def test_check_doc_links_rejects_backticked_non_markdown_file_reference(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "run.py").write_text("print('hi')\n", encoding="utf-8")
    (repo / "README.md").write_text(
        "Run `scripts/run.py` for a demo.\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check-doc-links.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "backticked file reference" in result.stderr
    assert "scripts/run.py" in result.stderr


def test_check_doc_links_ignores_gitignored_markdown(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    docs_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("docs/generated-*.md\n", encoding="utf-8")
    (repo / "README.md").write_text("# Demo\n\nUse the linked guide: [guide](docs/guide.md).\n", encoding="utf-8")
    (docs_dir / "guide.md").write_text("# Guide\n", encoding="utf-8")
    (docs_dir / "generated-bad.md").write_text("[bad](/tmp/not-in-repo.md)\n", encoding="utf-8")
    init_git_repo(repo, ".gitignore", "README.md", "docs/guide.md")

    result = run_script("scripts/check-doc-links.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
