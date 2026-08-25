from __future__ import annotations

from pathlib import Path

from .support import inspect_setup_repo


def test_nonstandard_surface_override_is_bound_to_approval_identity(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)
    (repo / "wiki").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "wiki" / "index.md").write_text("AAAA\n", encoding="utf-8")
    (repo / ".agents" / "setup-adapter.yaml").write_text(
        "version: 1\nrepo: repo\nsurfaces:\n  docs_index: wiki/index.md\n", encoding="utf-8"
    )

    first = inspect_setup_repo(repo)
    assert "wiki/index.md" in first["approval_plan"]["input_paths"]
    (repo / "wiki" / "index.md").write_text("BBBB\n", encoding="utf-8")

    second = inspect_setup_repo(repo)

    assert first["approval_plan"]["identity"] != second["approval_plan"]["identity"]


def test_docs_inventory_includes_uppercase_markdown_extensions(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs" / "nested").mkdir(parents=True)
    (repo / "docs" / "nested" / "Topic.MD").write_text("AAAA\n", encoding="utf-8")

    first = inspect_setup_repo(repo)
    assert "docs/nested/Topic.MD" in first["docs_inventory"]["nested_paths"]
    (repo / "docs" / "nested" / "Topic.MD").write_text("BBBB\n", encoding="utf-8")

    second = inspect_setup_repo(repo)

    assert first["approval_plan"]["identity"] != second["approval_plan"]["identity"]
