from __future__ import annotations

from pathlib import Path

from .support import inspect_setup_repo


def _run_inspect(repo: Path) -> dict[str, object]:
    return inspect_setup_repo(repo)


def _seed_repo(repo: Path, adapter_lines: list[str]) -> None:
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n\nA sentence that is guarded.\n", encoding="utf-8")
    (repo / "docs" / "spec.md").write_text(
        "\n".join(
            [
                "# Spec",
                "",
                "| path | matcher | pattern |",
                "| --- | --- | --- |",
                "| README.md | fixed | A sentence that is guarded. |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / ".agents" / "setup-adapter.yaml").write_text("\n".join(adapter_lines) + "\n", encoding="utf-8")


def _write_extra_guard(repo: Path) -> None:
    (repo / "notes").mkdir()
    (repo / "notes" / "extra.md").write_text(
        "\n".join(
            [
                "# Extra",
                "",
                "| path | matcher | pattern |",
                "| --- | --- | --- |",
                "| README.md | fixed | A sentence that is guarded. |",
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_setup_inspect_source_guard_roots_on_one_tree(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_repo(repo, ["version: 1", "repo: repo", "prose_wrap_policy: semantic"])
    _write_extra_guard(repo)

    default = _run_inspect(repo)
    assert default["prose_wrap"]["source_guard_count"] == 1
    assert default["prose_wrap"]["source_guards"][0]["spec_path"] == "docs/spec.md"

    (repo / ".agents" / "setup-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "prose_wrap_policy: semantic",
                "source_guard_scan_roots:",
                "  - notes",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    overridden = _run_inspect(repo)
    assert overridden["prose_wrap"]["source_guard_count"] == 1
    assert overridden["prose_wrap"]["source_guards"][0]["spec_path"] == "notes/extra.md"
