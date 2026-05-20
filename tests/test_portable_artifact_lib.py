from __future__ import annotations

from pathlib import Path

from scripts.portable_artifact_lib import (
    _sanitize_mapping_value,
    portable_path_value,
    sanitize_artifact_json,
    sanitize_diagnostic_text,
)


def test_sanitize_artifact_json_handles_mixed_path_lists(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    inside = repo / "docs" / "handoff.md"
    inside.parent.mkdir()
    inside.write_text("# handoff\n", encoding="utf-8")
    outside = tmp_path / "external.txt"
    outside.write_text("external\n", encoding="utf-8")

    payload = sanitize_artifact_json(
        {
            "source_paths": [
                str(inside),
                {"nested_path": str(outside)},
            ]
        },
        repo_root=repo,
    )

    assert payload == {
        "source_paths": [
            "docs/handoff.md",
            {"nested_path": "external-path:external.txt"},
        ]
    }


def test_portable_artifact_helpers_preserve_keyword_call_contract(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    inside = repo / "docs" / "handoff.md"
    inside.parent.mkdir()
    inside.write_text("# handoff\n", encoding="utf-8")

    assert portable_path_value(repo_root=repo, value=inside) == "docs/handoff.md"
    assert sanitize_artifact_json(value={"path": str(inside)}, repo_root=repo) == {
        "path": "docs/handoff.md"
    }
    assert _sanitize_mapping_value(key="path", value=str(inside), repo_root=repo) == "docs/handoff.md"
    assert sanitize_diagnostic_text(text=f"failed at {inside}", repo_root=repo) == (
        "failed at ./docs/handoff.md"
    )


def test_sanitize_artifact_json_distinguishes_path_keys_from_plain_strings(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    inside = repo / "docs" / "handoff.md"
    inside.parent.mkdir()
    inside.write_text("# handoff\n", encoding="utf-8")

    payload = sanitize_artifact_json(
        {
            "path": str(inside),
            "label": str(inside),
            "path_hint": str(inside),
            "artifact_paths": [str(inside)],
        },
        repo_root=repo,
    )

    assert payload == {
        "path": "docs/handoff.md",
        "label": str(inside),
        "path_hint": "docs/handoff.md",
        "artifact_paths": ["docs/handoff.md"],
    }


def test_sanitize_diagnostic_text_rewrites_repo_and_home_paths(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    inside = repo / "logs" / "trace.txt"
    inside.parent.mkdir()
    inside.write_text("trace\n", encoding="utf-8")

    text = f"repo={inside} home={Path.home() / 'cache' / 'tool.log'}"

    assert sanitize_diagnostic_text(text=text, repo_root=repo) == (
        "repo=./logs/trace.txt home=$HOME/cache/tool.log"
    )
