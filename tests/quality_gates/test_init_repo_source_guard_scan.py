from __future__ import annotations

import json
from pathlib import Path

from .support import run_script


def _run_inspect(repo: Path) -> dict[str, object]:
    result = run_script("skills/public/init-repo/scripts/inspect_repo.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


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
    (repo / ".agents" / "init-repo-adapter.yaml").write_text("\n".join(adapter_lines) + "\n", encoding="utf-8")


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


def test_init_repo_inspect_uses_bounded_default_source_guard_roots(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_repo(repo, ["version: 1", "repo: repo", "prose_wrap_policy: semantic"])
    _write_extra_guard(repo)

    payload = _run_inspect(repo)

    assert payload["prose_wrap"]["source_guard_count"] == 1
    assert payload["prose_wrap"]["source_guards"][0]["spec_path"] == "docs/spec.md"


def test_init_repo_inspect_adapter_can_override_source_guard_roots(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_repo(
        repo,
        [
            "version: 1",
            "repo: repo",
            "prose_wrap_policy: semantic",
            "source_guard_scan_roots:",
            "  - notes",
        ],
    )
    _write_extra_guard(repo)

    payload = _run_inspect(repo)

    assert payload["prose_wrap"]["source_guard_count"] == 1
    assert payload["prose_wrap"]["source_guards"][0]["spec_path"] == "notes/extra.md"
