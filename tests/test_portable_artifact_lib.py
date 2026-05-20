from __future__ import annotations

from pathlib import Path

from scripts.portable_artifact_lib import sanitize_artifact_json


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
