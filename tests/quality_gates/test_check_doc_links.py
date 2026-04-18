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


def test_check_doc_links_rejects_relative_link_without_dot_slash_prefix(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    docs_dir.mkdir(parents=True)
    (repo / "README.md").write_text("See [guide](docs/guide.md).\n", encoding="utf-8")
    (docs_dir / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_script("scripts/check-doc-links.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "must start with `./` or `../`" in result.stderr


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
                "Use the linked guide: [guide](./docs/guide.md).",
                "",
                "Runnable command in inline code: `sed -n '1,20p' docs/guide.md`.",
                "",
                "Concept tokens: `charness-concept`, `SKILL.md`, `v1.2.3`, `core.hooksPath`.",
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
    # Two SKILL.md files at different paths → ambiguous basename → allowed as concept.
    (docs_dir / "SKILL.md").write_text("# One\n", encoding="utf-8")
    (repo / "docs2").mkdir()
    (repo / "docs2" / "SKILL.md").write_text("# Two\n", encoding="utf-8")
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


def test_check_doc_links_rejects_dot_slash_backtick_that_resolves_to_repo_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "run-quality.sh").write_text("#!/bin/bash\n", encoding="utf-8")
    (repo / "README.md").write_text(
        "Prefer `./scripts/run-quality.sh` as the local quality gate.\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check-doc-links.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "backticked file reference" in result.stderr
    assert "./scripts/run-quality.sh" in result.stderr


def test_check_doc_links_rejects_unique_bare_basename(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "unique-runner.py").write_text("print('hi')\n", encoding="utf-8")
    (repo / "README.md").write_text(
        "Invoke `unique-runner.py` for the demo.\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check-doc-links.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "backticked file reference" in result.stderr
    assert "unique-runner.py" in result.stderr
    assert "unique-basename" in result.stderr


def test_check_doc_links_accepts_dot_slash_prefix_in_markdown_link(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "run.sh").write_text("#!/bin/bash\n", encoding="utf-8")
    (repo / "README.md").write_text(
        "Run [`./scripts/run.sh`](./scripts/run.sh) to demo.\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check-doc-links.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_check_doc_links_ignores_gitignored_markdown(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    docs_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("docs/generated-*.md\n", encoding="utf-8")
    (repo / "README.md").write_text("# Demo\n\nUse the linked guide: [guide](./docs/guide.md).\n", encoding="utf-8")
    (docs_dir / "guide.md").write_text("# Guide\n", encoding="utf-8")
    (docs_dir / "generated-bad.md").write_text("[bad](/tmp/not-in-repo.md)\n", encoding="utf-8")
    init_git_repo(repo, ".gitignore", "README.md", "docs/guide.md")

    result = run_script("scripts/check-doc-links.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
